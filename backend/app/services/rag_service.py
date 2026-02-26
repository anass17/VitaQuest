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
from qdrant_client.models import FieldCondition, Filter, MatchValue
import sqlite3
from sentence_transformers import CrossEncoder
from utils.llm_prompt import llm_prompt
import requests
# from rag.reranker import chunks_reranker
# from rag.mlflow_utils import log_metrics


class RAGService:

    def __init__(self):
        self.client = QdrantClient(url="http://qdrant:6333")
        self.conn = sqlite3.connect('../rag_chunks.db')
        self.ollama_url = "http://host.docker.internal:11434/api/generate"
        self.cursor = self.conn.cursor()

        # Setup SQLite Table
        # self.cursor.execute('''
        #     DROP TABLE parents
        # ''')
        # self.conn.commit()

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

    
    def chunks_reranker(self, query, chunks, model, top_k=5, min=0.3):
        reranker = CrossEncoder(model)

        pairs = [(query, chunk["text"]) for chunk in chunks]

        scores = reranker.predict(pairs)

        reranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )

        top_chunks = [chunk for chunk, score in reranked[:top_k] if float(score) >= min]

        return top_chunks
    


    def hierarchical_retriever(self, query: str, emb_model: str, cross_encoder: str, retrieval_top_k: int = 20, rerank_top_k: int = 5, min_score: int = 0.3, normalise: bool = True, mlflow_log: bool = False) -> List[Dict]:

        embedder = SentenceTransformer(emb_model)

        # Embed the query
        query_vector = embedder.encode(query, normalize_embeddings=normalise).tolist()

        # Retrieve top_k chunks from Qdrant
        response = self.client.query_points(
            collection_name="manual_chunks",
            query=query_vector,
            limit=retrieval_top_k,
            with_payload=True
        )

        final_context = []
        seen_parents = set()
        
        for hit in response.points:
            p_id = hit.payload['parent_id']
            
            if p_id not in seen_parents:
                # Fetch Parent from SQLite
                self.cursor.execute("SELECT text, chapter, section, categorie, page FROM parents WHERE id = ?", (p_id,))
                parent_data = self.cursor.fetchone()

                if parent_data:
                    text, chapter, section, categorie, page = parent_data
                    final_context.append({
                        "text": text,
                        "categorie": categorie,
                        "chapter": chapter,
                        "section": section,
                        "page": page,
                        "score": hit.score
                    })
                    seen_parents.add(p_id)
                    
        # return final_context

        # if mlflow_log:
        #     log_metrics({
        #         "Number of retrived chunks": len(retrieved_chunks)
        #     })
        

        # if mlflow_log:
        #     log_metrics({
        #         "Number of reranked chunks": len(top_chunks)
        #     })

        return final_context


        
    def ollama_generate(self, prompt: str, model: str, temperature: int = 0.2, max_tokens: int = 256) -> str:
        response = requests.post(
            self.ollama_url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["response"]



    # def store_answer(db: Session, user_query: str, answer: str):
    #     query = Query(
    #         query=user_query,
    #         reponse=answer
    #     )

    #     db.add(query)
    #     db.commit()



    def llm_generate_answer(self, query: str, model: str, chunks: List[Dict], temperature: int = 0.2, max_tokens: int = 256) -> str:

        # Build context from chunks
        context = "\n\n".join([f"{c['chapter']} | {c['section']}\n{c['text']}" 
                            for c in chunks])


        # log_text(llm_prompt("[Query]", "[Context]"), "prompt_template.txt")

        # Construct prompt
        prompt = llm_prompt(query, context)
        answer = self.ollama_generate(prompt, model, temperature, max_tokens)  # returns string

        return answer

