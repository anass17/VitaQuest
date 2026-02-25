from fastapi import FastAPI, UploadFile, File
from services.rag_service import RAGService
import json

app = FastAPI()

rag_service = RAGService()


EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
EMBEDDING_SIZE = 768
EMBEDDING_NORMALISE = True


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

    rag_service.store_chunks(chunks[1], EMBEDDING_MODEL, EMBEDDING_SIZE, EMBEDDING_NORMALISE)

    return {
        'message': chunks
    }



@app.get("/vectors")
async def upload_pdf():

    d = rag_service.get_count()

    return {
        "result": d
    }