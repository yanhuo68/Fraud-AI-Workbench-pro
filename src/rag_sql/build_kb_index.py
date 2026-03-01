# rag_sql/build_kb_index.py

"""
Build a FAISS vector store over all markdown / text documents in ./docs
and save it under ./data/kb/faiss_index.

Usage (from project root):

    python -m rag_sql.build_kb_index

or:

    python rag_sql/build_kb_index.py --docs-dir docs --out-dir data/kb

This uses local HuggingFace embeddings (sentence-transformers) by default.
"""

import argparse
import logging
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from rag_sql.erd_generator import build_mermaid_erd
import streamlit as st

logger = logging.getLogger(__name__)

def find_docs(docs_dir: Path) -> list[Path]:
    """Return all .md and .txt files under docs_dir."""
    patterns = ["**/*.md", "**/*.txt"]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(docs_dir.glob(pattern))
    # Deduplicate and sort
    files = sorted(set(files))
    return files


def load_documents(docs_dir: Path) -> list[Document]:
    files = find_docs(docs_dir)
    if not files:
        logger.warning("No .md or .txt files found in %s", docs_dir)
        return []

    docs: list[Document] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(errors="ignore")
        docs.append(
            Document(
                page_content=text,
                metadata={"source": str(path.relative_to(docs_dir))}
            )
        )
    logger.info("Loaded %d documents from %s", len(docs), docs_dir)
    return docs


def build_vectorstore(
    docs_dir: Path = Path("docs"),
    out_dir: Path = Path("data/kb"),
    chunk_size: int = 800,
    chunk_overlap: int = 150,
):
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Building vector store from %s -> %s", docs_dir, out_dir)
    
    # -----------------------------------------------------
    # 1. Generate ERD diagram markdown automatically
    # -----------------------------------------------------
    if (
        "table_dataframes" in st.session_state
        and "table_pkfk" in st.session_state
        and st.session_state.table_dataframes
    ):
        tables = st.session_state.table_dataframes
        pkfk_map = st.session_state.table_pkfk

        erd_text = build_mermaid_erd(tables, pkfk_map)

        erd_path = docs_dir / "erd_diagram.md"
        erd_path.write_text(erd_text, encoding="utf-8")

    # -----------------------------------------------------
    # 2. Load all .md and .txt documents
    # -----------------------------------------------------
    docs = []
    
    for path in docs_dir.glob("*.md"):
        docs.extend(TextLoader(str(path), encoding="utf-8").load())

    for path in docs_dir.glob("*.txt"):
        docs.extend(TextLoader(str(path), encoding="utf-8").load())
    if not docs:
        logger.error("No documents to index. Aborting.")
        return
        
    # -----------------------------------------------------
    # 3. Chunk documents
    # -----------------------------------------------------
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    
    #docs = load_documents(docs_dir)
    #splitter = RecursiveCharacterTextSplitter(
    #    chunk_size=chunk_size,
    #    chunk_overlap=chunk_overlap,
    #)
    #chunks = splitter.split_documents(docs)
    logger.info("Split into %d chunks (chunk_size=%d, overlap=%d)",
                len(chunks), chunk_size, chunk_overlap)

    # -----------------------------------------------------
    # 4. Save FAISS index
    # -----------------------------------------------------
    # Embeddings: Local HuggingFace model (fast, private, zero-cost)
    logger.info("Loading local HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vs = FAISS.from_documents(chunks, embeddings)
    index_path = out_dir / "faiss_index"
    vs.save_local(str(index_path))
    logger.info("Saved FAISS index to %s", index_path)
    return vs

def main():
    parser = argparse.ArgumentParser(
        description="Build FAISS KB index from docs/"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="docs",
        help="Directory containing .md / .txt knowledge-base files",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="data/kb",
        help="Output directory to save FAISS index",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Text chunk size for splitting documents",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=150,
        help="Overlap between chunks",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    docs_dir = Path(args.docs_dir)
    out_dir = Path(args.out_dir)

    if not docs_dir.exists():
        logger.error("Docs directory %s does not exist.", docs_dir)
        raise SystemExit(1)

    build_vectorstore(
        docs_dir=docs_dir,
        out_dir=out_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )


if __name__ == "__main__":
    main()
