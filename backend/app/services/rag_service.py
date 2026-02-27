import sqlite3
from qdrant_client import QdrantClient

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.models import OllamaModel

from .utils.extract import extract_content_from_uploaded_pdf
from .utils.chunk import chunk_markdown_documents
from .utils.store import store_chunks, store_parent_chunks

from .utils.retrieve import hierarchical_retriever
from .utils.rerank import chunks_reranker
from .utils.generate import llm_generate_answer

from utils.mlflow_evaluation import setup_mlflow, start_run, log_params, log_dict, log_text
from .utils.prompt import llm_prompt


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

        setup_mlflow("vitaquest_experiment")
        



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
    



    def chunk_store_pipeline(self, uploaded_file, emb_model, emb_size, normalize = True, mlflow_log = False):
        
        documents = extract_content_from_uploaded_pdf(uploaded_file, mlflow_log)
        
        chunks = chunk_markdown_documents(documents, uploaded_file.filename)

        store_parent_chunks(self.cursor, self.conn, chunks[0])
        
        store_chunks(self.client, chunks[1], emb_model, emb_size, normalize)

        return chunks

    


    def retrieve_generate_pipeline(self, query, emb_model, cross_model, llm_model, retrieval_top_k = 20, rerank_top_k = 5, rerank_min_score = 0.3, normalise = True, temperature = 0.2, max_tokens = 256, mlflow_log = False):
        
        chunks = hierarchical_retriever(self.client, self.cursor, query, emb_model, retrieval_top_k, normalise, mlflow_log)
        
        reranked_chunks = chunks_reranker(query, chunks, cross_model, rerank_top_k, rerank_min_score, mlflow_log)
        
        answer = llm_generate_answer(query, self.ollama_url, llm_model, reranked_chunks, temperature, max_tokens)

        return answer
    



    def evaluate_chunking_pipeline(self, uploaded_file, emb_model, emb_size, normalize = True):
        
        with start_run("RAG-Chunking"):

            log_params({
                "Uploaded file name": uploaded_file.filename,
                "Embedding Model": emb_model,
                "Embedding Size": emb_size,
                "Embedding Normalize": normalize
            })
            
            documents = extract_content_from_uploaded_pdf(uploaded_file)
        
            chunks = chunk_markdown_documents(documents, uploaded_file.filename)

            log_params({
                "Parser": "LlamaParse",
                "Parsing Format": "Markdown",
                "Pages Parsed": len(documents),
                "Chunking Type": "hierarchical chunking",
                "Parent Chunks Count": len(chunks[0]),
                "Child Chunks Count": len(chunks[1]),
                "Vector DB": "Qdrant"
            })

            return {
                "chunks": chunks
            }


    

    def evaluate_retrieval_generation_pipeline(self, query, emb_model, cross_model, llm_model, retrieval_top_k = 20, rerank_top_k = 5, rerank_min_score = 0.3, normalise = True, temperature = 0.2, max_tokens = 256):
        
        with start_run("RAG-Generation"):

            log_params({
                "Embedding Model": emb_model,
                "Retrieval Top K": retrieval_top_k,
                "Cross Encoder": cross_model,
                "Rerank Top K": rerank_top_k,
                "Min Rerank Score": rerank_min_score,
                "LLM Model": llm_model,
                "LLM Temperature": temperature,
                "LLM Max Tokens": max_tokens
            })
            
            chunks = hierarchical_retriever(self.client, self.cursor, query, emb_model, retrieval_top_k, normalise)

            reranked_chunks = chunks_reranker(query, chunks, cross_model, rerank_top_k, rerank_min_score)
            
            answer = llm_generate_answer(query, self.ollama_url, llm_model, reranked_chunks, temperature, max_tokens)

            log_params({
                "Number of retrived chunks": len(chunks),
                "Number of reranked chunks": len(reranked_chunks)
            })

            log_text(llm_prompt("[Query]", "[Context]"), "prompt_template.txt")

            log_dict({
                "Query": query,
                "Answer": answer,
                "Chunks": reranked_chunks
            }, "generation_details.json")

            return {
                "query": query,
                "answer": answer
            }
