from fastapi import FastAPI, UploadFile, File
from services.rag_service import RAGService
from schemas.query import queryData
import json

app = FastAPI()

rag_service = RAGService()


EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_SIZE = 768
EMBEDDING_NORMALISE = True
CROSS_ENCODER = "BAAI/bge-reranker-large"
LLM_MODEL = "llama3:8b"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 256


@app.get('/')
def hello():
    return {
        "message": "Hello !"
    }

@app.post("/ingest")
async def upload_pdf(
    file: UploadFile = File(...)
):

    docs = rag_service.extract_content_from_uploaded_pdf(file)

    with open("file_test.json", "w") as json_file:
        json.dump(
            {
                "content": docs,
            },
            json_file
        )

    return {
        'message': docs
    }



@app.post("/chunk")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # docs = rag_service.extract_content_from_uploaded_pdf(file)

    with open("file_test.json", "r") as json_file:
        docs = json.load(json_file)['content'][0]

    chunks = rag_service.chunk_markdown_documents(docs, file.filename)

    rag_service.store_parent_chunks(chunks[0])

    rag_service.store_chunks(chunks[1], EMBEDDING_MODEL, EMBEDDING_SIZE, EMBEDDING_NORMALISE)


    return {
        'message': chunks
    }



@app.post("/answer/generate")
async def upload_pdf(
    data: queryData
):

    answer = rag_service.retrieve_generate_pipeline(data.query, EMBEDDING_MODEL, CROSS_ENCODER, LLM_MODEL)

    return {
        "result": answer
    }