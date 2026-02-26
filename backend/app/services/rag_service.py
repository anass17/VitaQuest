from llama_parse import LlamaParse
import tempfile
import re
from typing import List, Dict
import uuid
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct
from qdrant_client.models import (
    VectorParams,
    Distance
)
import sqlite3

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel
# from rag.reranker import chunks_reranker
# from rag.mlflow_utils import log_metrics

from .utils.retriever import hierarchical_retriever
from .utils.reranker import chunks_reranker
from .utils.generation import llm_generate_answer


class RAGService:

    def __init__(self):
        self.client = QdrantClient(url="http://qdrant:6333")
        self.conn = sqlite3.connect('../rag_chunks.db')
        self.ollama_url = "http://host.docker.internal:11434/api/generate"
        self.cursor = self.conn.cursor()
        self.ollama_model = OllamaModel(model="llama3:8b", base_url="http://host.docker.internal:11434")
        

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parents (
                id TEXT PRIMARY KEY,
                text TEXT,
                chapter TEXT,
                section TEXT,
                categorie TEXT,
                page INTEGER
            )
        ''')
        self.conn.commit()



    ### Extraction

    def extract_content_from_uploaded_pdf(self, uploaded_file):

        parser = LlamaParse(
            result_type="markdown",
            language="fr",
            verbose=True,
            premium_mode=True,
        )

        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.file.read())
            tmp_path = tmp.name

        # Parse with LlamaParse
        documents = parser.load_data(
            tmp_path,
            extra_info={"invalidate_cache": True}
        )

        print(f"Pages parsed: {len(documents)}")

        # log_metrics({
        #     "Pages Parsed": len(documents)
        # })

        # Return text
        if len(documents) > 0:
            return list(map(lambda d: d.text, documents))
        else:
            return []
        

    
    ##### Chunking

    # Get categorie name if exist
    def get_categorie(self, doc):
        search = re.search(r"\n# (.+)\n$", doc)
        if search:
            chapter = search.group(1)
            return chapter
        
        return None


    # Get chapter name if exist
    def get_chapter(self, doc):

        search = re.search(r"[*]{2}(.+?)[*]{2}[| ]*[*]*Validation[* :]*COTEPRO", doc)
        if not search: 

            search = re.search(r"\n\n\n# .+\n# (.+)\n", doc)
            if not search:

                search = re.search(r"[*]{2}(.+?)[*]{2}[| \n]*[*]*Version : 2", doc)
                if not search:

                    search = re.search(r"# (.+?)\n\nValidation : COTEPRO", doc)

        if search:
            title = search.group(1)
            return title.replace("<br>", "")
        
        return None



    def delete_duplicated_text(self, doc):
        text = re.sub(r"[\n]+Guide des Protocoles - 2025\s*\d*\s*[\n]*", "", doc)
        
        splits = re.split(r"(.+|\n)Date :[*]* 2025( [|]|[*]+|\n)", text)

        text = splits[-1]

        return text.strip()
    


    def estimate_tokens(self, text: str) -> int:
        return len(text.split())



    def split_by_paragraph(self, text: str, max_tokens: int = 500, overlap: int = 80):
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""

        for p in paragraphs:
            candidate = current + ("\n\n" + p if current else p)
            if self.estimate_tokens(candidate) <= max_tokens:
                current = candidate
            else:
                chunks.append(current.strip())
                tail = " ".join(current.split()[-overlap:])
                current = tail + "\n\n" + p

        if current.strip():
            chunks.append(current.strip())

        return chunks



    # ------------------ main chunker ------------------

    def chunk_markdown_documents(
        self,
        documents: list,
        source: str,
        max_tokens: int = 500,
        overlap: int = 80
    ) -> List[Dict]:

        documents = documents[1:]

        parent_store = {}
        child_chunks = []

        categorie_name = None
        chapter_name = None

        for page_num, doc in enumerate(documents, 1):

            # If categorie name is detected, move to next page

            categorie = self.get_categorie(doc)
            if categorie:
                categorie_name = categorie
                continue

            # Get chapter name if exists

            chapter = self.get_chapter(doc)
            if chapter:
                chapter_name = chapter

            clean_doc = self.delete_duplicated_text(doc)
            if clean_doc:

                # Regex to capture sections
                section_pattern_1 = r"(## .*?)(?=\n## |\Z)"
                section_pattern_2 = r"(# .*?)(?=\n# |\Z)"

                # Detect Sections
                sections = re.findall(section_pattern_1, clean_doc, re.DOTALL)

                if len(sections) == 0:
                    sections = re.findall(section_pattern_2, clean_doc, re.DOTALL)

                    if len(sections) == 0:
                        sections = [clean_doc]

                
                for section in sections:
                    lines = section.strip().split("\n")
                    
                    title = lines[0].strip("# ")                # Heading
                    content = "\n".join(lines[1:])              # Body

                    parent_id = str(uuid.uuid4())
                    full_parent_text = f"{title}\n{content}"
                    
                    # Save to Parent Store
                    parent_store[parent_id] = {
                        "content": full_parent_text,
                        "metadata": {
                            "chapter": chapter_name,
                            "section": title,
                            "categorie": categorie_name,
                            "page": page_num
                        }
                    }
                    
                    # Create Children manually
                    paragraphs = content.split('\n\n')
                    for para in paragraphs:
                        if len(para) > 10:
                            child_chunks.append({
                                "text": para.strip(),
                                "metadata": {
                                    "parent_id": parent_id, 
                                    "header": title,
                                    "chapter": chapter_name,
                                    "categorie": categorie_name,
                                    "page": page_num,
                                    "source": source
                                }
                            })

        return parent_store, child_chunks

    

    def store_chunks(self, chunks, emb_model, emb_size, normalise):
        points = []

        self.client.recreate_collection(
            collection_name="manual_chunks",
            vectors_config=VectorParams(
                size=emb_size,
                distance=Distance.COSINE
            ),
        )

        embedder = SentenceTransformer(emb_model)

        for chunk in chunks:
            vector = embedder.encode(chunk["text"], normalize_embeddings=normalise)

            payload = chunk["metadata"].copy()
            payload['content'] = chunk["text"]

            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload=payload
                )
            )
        
        print("-- Vector generation complete")

        self.client.upsert(
            collection_name="manual_chunks",
            points=points
        )

        print("-- Storage complete")



    def store_parent_chunks(self, parent_docs: dict):
        self.cursor.execute('''
            DELETE FROM parents
        ''')
        self.conn.commit()

        for id, doc in parent_docs.items():

            parent_id = id
            content = doc["content"]
            chapter = doc["metadata"].get('chapter', 'Unknown')
            section = doc["metadata"].get('section', 'Unknown')
            categorie = doc["metadata"].get('categorie', 'Unknown')
            page = doc["metadata"].get('page', 'Unknown')
            
            # Save Parent to SQLite
            self.cursor.execute(
                "INSERT INTO parents (id, text, chapter, section, categorie, page) VALUES (?, ?, ?, ?, ?, ?)",
                (parent_id, content, chapter, section, categorie, page)
            )
        
        self.conn.commit()

        return True


    ### Retriever

    
    

        
    


    def evaluate_rag(self, query, context_chunks, answer, expected_answer):

        context_text = [c["text"] for c in context_chunks]

        test_case = LLMTestCase(
            input=query,
            actual_output=answer,
            expected_output=expected_answer,
            retrieval_context=context_text
        )

        # Metrics
        answer_relevancy = AnswerRelevancyMetric(model=self.ollama_model)
        faithfulness = FaithfulnessMetric(model=self.ollama_model)
        precision = ContextualPrecisionMetric(model=self.ollama_model)
        recall = ContextualRecallMetric(model=self.ollama_model)

        # Measure
        answer_relevancy.measure(test_case)
        faithfulness.measure(test_case)
        precision.measure(test_case)
        recall.measure(test_case)

        return {
            "answer_relevancy": answer_relevancy.score,
            "faithfulness": faithfulness.score,
            "precision_at_k": precision.score,
            "recall_at_k": recall.score
        }
    

    def retrieve_generate_pipeline(self, query, emb_model, cross_model, llm_model, retrieval_top_k = 20, rerank_top_k = 5, rerank_min_score = 0.3, normalise = True, temperature = 0.2, max_tokens = 256, mlflow_log = False):
        chunks = hierarchical_retriever(self.client, self.cursor, query, emb_model, retrieval_top_k, normalise, mlflow_log)
        reranked_chunks = chunks_reranker(query, chunks, cross_model, rerank_top_k, rerank_min_score, mlflow_log)
        answer = llm_generate_answer(query, self.ollama_url, llm_model, reranked_chunks, temperature, max_tokens)

        return answer