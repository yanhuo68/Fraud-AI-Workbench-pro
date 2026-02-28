# rag_sql/knowledge_base.py

from pathlib import Path
from typing import List, Dict, Any, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings

from agents.llm_router import init_llm

DOCS_DIR = Path("docs")
INDEX_DIR = Path("data/kb")
INDEX_DIR.mkdir(parents=True, exist_ok=True)


def load_documents() -> List:
    docs = []
    if not DOCS_DIR.exists():
        return docs

    for path in DOCS_DIR.glob("*.md"):
        docs.append(TextLoader(str(path), encoding="utf-8").load()[0])
    for path in DOCS_DIR.glob("*.txt"):
        docs.append(TextLoader(str(path), encoding="utf-8").load()[0])
    return docs


def build_vectorstore():
    docs = load_documents()
    if not docs:
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    chunks = splitter.split_documents(docs)

    # Local embeddings for better performance and privacy
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(str(INDEX_DIR / "faiss_index"))
    return vs


def load_vectorstore():
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        return FAISS.load_local(
            str(INDEX_DIR / "faiss_index"),
            embeddings,
            allow_dangerous_deserialization=True,
        )
    except Exception:
        return None


def get_or_create_vectorstore():
    vs = load_vectorstore()
    if vs is not None:
        return vs
    return build_vectorstore()


def retrieve_with_scores(question: str, k: int = 4) -> List[Tuple[Any, float]]:
    """
    Return (Document, score) pairs for RAG inspector.
    Lower scores usually mean closer / more similar, depending on FAISS config.
    """
    vs = get_or_create_vectorstore()
    if vs is None:
        return []
    return vs.similarity_search_with_score(question, k=k)


def answer_kb_question(
    question: str,
    llm_id: str,
    return_context: bool = False,
    k: int = 4,
) -> Any:
    """
    Main entry point:
    - If return_context=False: returns only answer string (backward compatible).
    - If return_context=True: returns dict {answer, contexts[]} for RAG inspector.
    """
    pairs = retrieve_with_scores(question, k=k)
    if not pairs:
        answer = "No knowledge-base documents found in ./docs; please add .md or .txt files and rebuild the index."
        if return_context:
            return {"answer": answer, "contexts": []}
        return answer

    docs = [d for d, _ in pairs]

    context_text = "\n\n".join(
        f"Source {i+1} ({d.metadata.get('source','unknown')}):\n{d.page_content}"
        for i, d in enumerate(docs)
    )

    llm = init_llm(llm_id)
    prompt = (
        "You are a fraud analytics expert. Use ONLY the following context to answer the question.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        "Answer clearly and concisely. If the context is insufficient, say so explicitly."
    )
    resp = llm.invoke(prompt)
    answer = resp.content

    if not return_context:
        return answer

    # Build debug-friendly context list
    context_items: List[Dict[str, Any]] = []
    for doc, score in pairs:
        context_items.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
        )

    return {
        "answer": answer,
        "contexts": context_items,
    }

def compare_rag_vs_no_rag(
    question: str,
    llm_id: str,
    k: int = 4,
) -> Dict[str, Any]:
    """
    Runs both:
    - RAG-enhanced answer (using context)
    - No-RAG answer (LLM alone)

    Returns structured result:
    {
        "rag_answer": str,
        "no_rag_answer": str,
        "contexts": [...]
    }
    """
    # 1. RAG answer (with context)
    rag_result = answer_kb_question(
        question,
        llm_id=llm_id,
        return_context=True,
        k=k,
    )

    rag_answer = rag_result["answer"]
    contexts = rag_result["contexts"]

    # Build RAG context text for debugging
    context_text = "\n\n".join(
        f"[Source: {ctx['metadata'].get('source','unknown')}] {ctx['content']}"
        for ctx in contexts
    )

    # 2. No-RAG answer
    llm = init_llm(llm_id)
    no_rag_prompt = f"""
You are a fraud analytics expert.

Answer the following question *without* using any external documents or context.

Question: {question}

Answer as best as you can using only your internal knowledge.
"""

    no_rag_response = llm.invoke(no_rag_prompt)

    return {
        "rag_answer": rag_answer,
        "no_rag_answer": no_rag_response.content,
        "contexts": contexts,
        "rag_context_text": context_text,
    }
