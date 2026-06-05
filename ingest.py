import os
import json
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

PARSED_DIR = os.path.join("data", "parsed")
DB_DIR = "db"
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def _format_section_label(section_name: str) -> str:
    """Convert snake_case section name to a Title Case label for chunk prefix."""
    return section_name.replace("_", " ").title()


def ingest_data():
    if not os.path.exists(PARSED_DIR):
        error_msg = f"Error: Parsed data directory '{PARSED_DIR}' does not exist. Run parse.py first."
        print(error_msg)
        raise FileNotFoundError(error_msg)

    parsed_files = [f for f in os.listdir(PARSED_DIR) if f.endswith(".json")]
    if not parsed_files:
        error_msg = f"No parsed JSON files found in '{PARSED_DIR}'"
        print(error_msg)
        raise FileNotFoundError(error_msg)

    print(f"Found {len(parsed_files)} parsed files. Preparing documents...")

    # Phase 3.2 — Section-aware chunking
    # chunk_size=350, overlap=50 as per implementation plan.
    # Most sections fit in 1 chunk; fund_management may produce 2.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,
        chunk_overlap=50,
        length_function=len
    )

    documents = []

    for file_name in sorted(parsed_files):
        file_path = os.path.join(PARSED_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scheme_name = data.get("scheme_name", "")
        source_url  = data.get("source_url", "")
        last_updated = data.get("last_updated", "")
        sections    = data.get("sections", {})

        print(f"\nProcessing: {scheme_name}")
        print(f"  Source URL  : {source_url}")
        print(f"  Last Updated: {last_updated}")

        for section_name, section_text in sections.items():
            # 3.1 — Skip empty sections (statements file has several)
            if not section_text or not section_text.strip():
                print(f"  [SKIP] Empty section: {section_name}")
                continue

            # 3.2 — Split section text into chunks
            raw_chunks = splitter.split_text(section_text)

            for idx, chunk_content in enumerate(raw_chunks):
                # 3.3 — Section-prefix embedding strategy:
                # Prepend "[Section Label] " so BGE Small encodes both the
                # section topic and the factual content in a single vector.
                # This significantly improves cosine-similarity precision for
                # short keyword queries (e.g. "expense ratio?").
                section_label = _format_section_label(section_name)
                prefixed_content = f"[{section_label}] {chunk_content}"

                doc = Document(
                    page_content=prefixed_content,
                    metadata={
                        "scheme_name":  scheme_name,
                        "source_url":   source_url,
                        "last_updated": last_updated,
                        "source_file":  file_name,
                        "section":      section_name,
                        "chunk_index":  idx,
                    }
                )
                documents.append(doc)
                print(f"  [chunk {idx}] [{section_label}] -> {len(prefixed_content)} chars")

    print(f"\nTotal document chunks generated: {len(documents)}")

    # Wipe and recreate DB for a clean build
    if os.path.exists(DB_DIR):
        print(f"Removing existing database at '{DB_DIR}' for clean rebuild...")
        shutil.rmtree(DB_DIR)

    # 3.4 — Embedding generation
    print(f"Loading embedding model: {MODEL_NAME} (CPU)")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},  # cosine-ready unit vectors
    )

    # 3.5 — Persist to ChromaDB
    print(f"Writing embeddings to ChromaDB at '{DB_DIR}'...")
    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_DIR,
    )
    db.persist()
    print("ChromaDB index built and persisted successfully.")
    print(f"Index contains {db._collection.count()} vectors.")

    return {
        "status": "success",
        "urls_fetched": len(parsed_files),
        "chunks_generated": len(documents)
    }


if __name__ == "__main__":
    ingest_data()
