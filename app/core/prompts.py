"""
Prompt templates.

Kept in their own file on purpose: prompt wording is something you'll tune
repeatedly while testing answer quality, and it shouldn't be buried inside
business logic. This is the file to edit if answers are too verbose, not
citing properly, or answering from general knowledge instead of the docs.
"""


def build_answer_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    """Build the final prompt sent to the LLM, grounding it in retrieved chunks.

    The instructions explicitly forbid answering outside the provided
    context and require inline [Source] tags - this is the prompt-level
    half of the citation strategy (the other half is programmatic: the
    API always returns the real retrieved sources regardless of what the
    model writes, see query_service.py).
    """
    context_blocks = []
    for chunk in retrieved_chunks:
        context_blocks.append(
            f"[Source: {chunk['source_filename']}, page {chunk['page_number']}]\n"
            f"{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    return f"""You are a technical assistant answering questions about internal company documents (supplier datasheets, technical PDFs, etc.).

Rules:
1. Answer ONLY using the information in the CONTEXT below. Do not use outside knowledge.
2. If the context does not contain the answer, say clearly: "I could not find this information in the provided documents." Do not guess.
3. After every factual claim, cite it like this: [Source: filename, page X], using the exact filename and page number from the context block it came from.
4. Answer in the same language the question was asked in (German or English).
5. Be concise and precise - this is for verifying technical/supplier information, not casual conversation.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""
