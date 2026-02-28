from app.services.utils.prompt import llm_prompt

def test_llm_prompt():
    prompt = llm_prompt("query", "context")

    assert type(prompt) == str