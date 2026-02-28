import numpy as np
from unittest.mock import patch, MagicMock
from app.services.utils.store import store_chunks, store_parent_chunks


@patch("app.services.utils.store.SentenceTransformer")
def test_store_chunks(mock_sentence_transformer):

    # Mock embedding model
    mock_embedder = MagicMock()
    mock_sentence_transformer.return_value = mock_embedder
    mock_embedder.encode.return_value = np.array([0.1, 0.2, 0.3])

    # Mock Qdrant client
    mock_client = MagicMock()

    chunks = [
        {
            "text": "chunk 1 text",
            "metadata": {"parent_id": 1, "chapter": "A"},
        },
        {
            "text": "chunk 2 text",
            "metadata": {"parent_id": 2, "chapter": "B"},
        },
    ]

    store_chunks(
        client=mock_client,
        chunks=chunks,
        emb_model="fake-model",
        emb_size=3,
        normalise=True,
    )

    # Check collection creation
    mock_client.recreate_collection.assert_called_once()

    # Check upsert called
    mock_client.upsert.assert_called_once()

    # Verify points were generated
    args, kwargs = mock_client.upsert.call_args
    points = kwargs["points"]

    assert len(points) == 2
    assert points[0].payload["content"] == "chunk 1 text"
    assert points[1].payload["content"] == "chunk 2 text"


def test_store_parent_chunks():

    mock_cursor = MagicMock()
    mock_conn = MagicMock()

    parent_docs = {
        1: {
            "content": "Parent text 1",
            "metadata": {
                "chapter": "Chap1",
                "section": "Sec1",
                "categorie": "Cat1",
                "page": 5,
            },
        },
        2: {
            "content": "Parent text 2",
            "metadata": {
                "chapter": "Chap2",
                "section": "Sec2",
                "categorie": "Cat2",
                "page": 8,
            },
        },
    }

    result = store_parent_chunks(mock_cursor, mock_conn, parent_docs)

    # DELETE executed
    mock_cursor.execute.assert_any_call("""
            DELETE FROM parents
        """)

    # INSERT executed twice
    assert mock_cursor.execute.call_count == 3

    # commit called
    assert mock_conn.commit.call_count == 2

    assert result is True
