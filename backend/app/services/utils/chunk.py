import re
import uuid
import mlflow

# Get categorie name if exist


def get_categorie(doc):
    search = re.search(r"\n# (.+)\n$", doc)
    if search:
        chapter = search.group(1)
        return chapter

    return None


# Get chapter name if exist


def get_chapter(doc):

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


# Cleaning: Delete duplicated text


def delete_duplicated_text(doc):
    text = re.sub(r"[\n]+Guide des Protocoles - 2025\s*\d*\s*[\n]*", "", doc)

    splits = re.split(r"(.+|\n)Date :[*]* 2025( [|]|[*]+|\n)", text)

    text = splits[-1]

    return text.strip()


# Chunk documents


@mlflow.trace
def chunk_markdown_documents(
    documents: list, source: str, max_tokens: int = 500, overlap: int = 80
):

    documents = documents[1:]

    parent_store = {}
    child_chunks = []

    categorie_name = None
    chapter_name = None

    for page_num, doc in enumerate(documents, 1):

        # If categorie name is detected, move to next page
        categorie = get_categorie(doc)
        if categorie:
            categorie_name = categorie
            continue

        # Get chapter name if exists
        chapter = get_chapter(doc)
        if chapter:
            chapter_name = chapter

        clean_doc = delete_duplicated_text(doc)
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

                title = lines[0].strip("# ")  # Heading
                content = "\n".join(lines[1:])  # Body

                parent_id = str(uuid.uuid4())
                full_parent_text = f"{title}\n{content}"

                # Save to Parent Store
                parent_store[parent_id] = {
                    "content": full_parent_text,
                    "metadata": {
                        "chapter": chapter_name,
                        "section": title,
                        "categorie": categorie_name,
                        "page": page_num,
                    },
                }

                # Create Children manually
                paragraphs = content.split("\n\n")
                for para in paragraphs:
                    if len(para) > 10:
                        child_chunks.append(
                            {
                                "text": para.strip(),
                                "metadata": {
                                    "parent_id": parent_id,
                                    "header": title,
                                    "chapter": chapter_name,
                                    "categorie": categorie_name,
                                    "page": page_num,
                                    "source": source,
                                },
                            }
                        )

    return parent_store, child_chunks
