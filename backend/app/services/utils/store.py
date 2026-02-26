import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance
)


# Store as vectors in Qdrant

def store_chunks(client, chunks, emb_model, emb_size, normalise):
    points = []

    client.recreate_collection(
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

    client.upsert(
        collection_name="manual_chunks",
        points=points
    )



# Store in a table in SQLite

def store_parent_chunks(cursor, conn, parent_docs: dict):
        cursor.execute('''
            DELETE FROM parents
        ''')
        conn.commit()

        for id, doc in parent_docs.items():

            parent_id = id
            content = doc["content"]
            chapter = doc["metadata"].get('chapter', 'Unknown')
            section = doc["metadata"].get('section', 'Unknown')
            categorie = doc["metadata"].get('categorie', 'Unknown')
            page = doc["metadata"].get('page', 'Unknown')
            
            # Save Parent to SQLite
            cursor.execute(
                "INSERT INTO parents (id, text, chapter, section, categorie, page) VALUES (?, ?, ?, ?, ?, ?)",
                (parent_id, content, chapter, section, categorie, page)
            )
        
        conn.commit()

        return True