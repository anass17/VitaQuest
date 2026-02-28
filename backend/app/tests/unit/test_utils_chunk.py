from app.services.utils.chunk import (
    get_categorie,
    get_chapter,
    delete_duplicated_text,
    chunk_markdown_documents,
)


def test_get_categorie():

    page_content = "\n\n\nGuide des Protocoles - 2025    7\n\n# PÉDIATRIE\n"

    categorie_name = get_categorie(page_content)

    assert categorie_name == "PÉDIATRIE"


def test_categorie_not_found():

    page_content = "\n\nDIRECTION\nDE LA SANTÉ\n\n# GUIDE DES PROTOCOLES\n\n**A l'usage des Professionnels de Santé\nexerçant en Poste Isolé\nen Polynésie Française**\n\nCOLLÈGE MÉDICAL\nDIRECTION\nDE LA SANTÉ\n"

    categorie_name = get_categorie(page_content)

    assert categorie_name is None


def test_get_chapter():

    page_content = "\n\n\n| | PÉDIATRIE | Version : 2 |\n|---|---|---|\n| | **Diarrhée** | Validation : COTEPRO |\n| | | Date : 2025 |\n\n"

    assert get_chapter(page_content) == "Diarrhée"


def test_delete_duplicated_text():

    page_content = "\n\n\n| | PÉDIATRIE | Version : 2 |\n|---|---|---|\n| | **Diarrhée** | Validation : COTEPRO |\n| | | Date : 2025 |\n\n## CE QU'IL FAUT SAVOIR\n\nGuide des Protocoles - 2025\n"

    assert delete_duplicated_text(page_content) == "## CE QU'IL FAUT SAVOIR"


def test_chunk_markdown_documents():

    documents = [
        "Page 1",
        "\n\n\nGuide des Protocoles - 2025    7\n\n# PÉDIATRIE\n",
        "\n\n\n| | PÉDIATRIE | Version : 2 |\n|---|---|---|\n| | **Diarrhée** | Validation : COTEPRO |\n| | | Date : 2025 |\n\n## CE QU'IL FAUT SAVOIR\n\n• List Item 1\n\n• List Item 2\n\nGuide des Protocoles - 2025     8\n\n",
    ]

    expected_parent_chunk = {
        "content": "CE QU'IL FAUT SAVOIR\n\n• List Item 1\n\n• List Item 2",
        "metadata": {
            "chapter": "Diarrhée",
            "section": "CE QU'IL FAUT SAVOIR",
            "categorie": "PÉDIATRIE",
            "page": 2,
        },
    }

    parent_chunks, child_chunks = chunk_markdown_documents(documents, "file_name")

    assert list(parent_chunks.items())[0][1] == expected_parent_chunk

    parent_id = list(parent_chunks.items())[0][0]

    expected_child_chunks_1 = {
        "text": "• List Item 1",
        "metadata": {
            "parent_id": parent_id,
            "header": "CE QU'IL FAUT SAVOIR",
            "chapter": "Diarrhée",
            "categorie": "PÉDIATRIE",
            "page": 2,
            "source": "file_name",
        },
    }

    expected_child_chunks_2 = {
        "text": "• List Item 2",
        "metadata": {
            "parent_id": parent_id,
            "header": "CE QU'IL FAUT SAVOIR",
            "chapter": "Diarrhée",
            "categorie": "PÉDIATRIE",
            "page": 2,
            "source": "file_name",
        },
    }

    assert len(child_chunks) == 2
    assert child_chunks[0] == expected_child_chunks_1
    assert child_chunks[1] == expected_child_chunks_2
