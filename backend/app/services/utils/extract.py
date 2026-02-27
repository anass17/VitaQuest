from llama_parse import LlamaParse
import tempfile



def extract_content_from_uploaded_pdf(uploaded_file):

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

    # Return text
    if len(documents) > 0:
        return list(map(lambda d: d.text, documents))
    else:
        return []