from fastapi import APIRouter, UploadFile, File
from schemas.query import queryData
from services.rag_service import RAGService
from prometheus_client import Counter, Histogram
import time



CHUNK_MAX_TOKENS = 500
CHUNK_OVERLAP = 80
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_SIZE = 768
EMBEDDING_NORMALISE = True
CROSS_ENCODER = "BAAI/bge-reranker-large"
RETRIEVAL_TOP_K = 20
RERANK_TOP_K = 5
MIN_RERANK_SCORE = 0.3
LLM_MODEL = "llama3:8b"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 256


# Request counter
rag_requests = Counter(
    "rag_requests_total",
    "Total number of RAG queries"
)

# Errors
rag_errors = Counter(
    "rag_errors_total",
    "Total RAG errors"
)

# Latency
rag_latency = Histogram(
    "rag_pipeline_latency_seconds",
    "RAG pipeline latency"
)

# Quality metrics
# faithfulness_score = Gauge(
#     "rag_faithfulness_score",
#     "Faithfulness score of answers"
# )


rag_service = RAGService()


router = APIRouter(prefix="/rag", tags=["RAG"])



@router.post("/ingest")
async def ingest_and_chunk_document(file: UploadFile = File(...)):

    chunks = rag_service.chunk_store_pipeline(
        file, EMBEDDING_MODEL, EMBEDDING_SIZE, EMBEDDING_NORMALISE
    )

    return {"Parent Chunks Count": len(chunks[0]), "Child Chunks Count": len(chunks[1])}



@router.post("/generate")
async def retrieve_and_generate_llm_answer(data: queryData):

    rag_requests.inc()

    start = time.time()

    try:

        answer = rag_service.retrieve_generate_pipeline(
            data.query, EMBEDDING_MODEL, CROSS_ENCODER, LLM_MODEL
        )

        latency = time.time() - start
        rag_latency.observe(latency)

        return {"answer": answer}
    
    except Exception:
        rag_errors.inc()
        raise



@router.post("/evaluate/chunking")
async def evaluate_chunking(file: UploadFile = File(...)):

    response = rag_service.evaluate_chunking_pipeline(
        file, EMBEDDING_MODEL, EMBEDDING_SIZE, EMBEDDING_NORMALISE
    )

    return response



@router.post("/evaluate/generation")
async def evaluate_retrieval_and_generation():

    answer = rag_service.evaluate_retrieval_generation_pipeline(
        EMBEDDING_MODEL,
        CROSS_ENCODER,
        LLM_MODEL,
        RETRIEVAL_TOP_K,
        RERANK_TOP_K,
        MIN_RERANK_SCORE,
        EMBEDDING_NORMALISE,
        LLM_TEMPERATURE,
        LLM_MAX_TOKENS,
    )

    return answer
