"""
RAG Embedder — Chunk & Embed Knowledge Base into ChromaDB.

Reads all .md files from config.KNOWLEDGE_DIR, splits them into
header-based chunks with size limits, embeds via OpenAI, and persists
to ChromaDB at config.CHROMA_PERSIST_DIR.
"""

import os
import re
import sys
from pathlib import Path

import openai
import chromadb

# ---------------------------------------------------------------------------
# Root-relative import support
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _topic_from_filename(filename: str) -> str:
    """
    Extract broad topic from filename via keyword lookup.
    e.g. 'quadratic_equations.md' -> 'algebra'
    """
    stem = Path(filename).stem.lower()
    calculus_stems = {
        "limits", "derivatives", "applications_of_derivatives",
        "integration_basics", "definite_integrals",
    }
    probability_stems = {
        "probability_basics", "bayes_theorem", "combinatorics", "distributions",
    }
    linear_algebra_stems = {
        "matrices", "determinants", "linear_systems",
    }
    algebra_stems = {
        "algebra_identities", "quadratic_equations", "sequences_series",
        "binomial_theorem", "inequalities",
    }

    if stem in calculus_stems:
        return "calculus"
    if stem in probability_stems:
        return "probability"
    if stem in linear_algebra_stems:
        return "linear_algebra"
    if stem in algebra_stems:
        return "algebra"

    # Fallback: first segment before underscore
    return stem.split("_")[0]


def _split_by_headers(text: str) -> list[tuple[str, str]]:
    """
    Split markdown text by ## and ### headers.
    Returns list of (header_text, content) tuples.
    """
    header_pattern = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(header_pattern.finditer(text))

    if not matches:
        return [("Introduction", text.strip())]

    sections: list[tuple[str, str]] = []

    # Content before the first header
    if matches[0].start() > 0:
        pre = text[: matches[0].start()].strip()
        if pre:
            sections.append(("Introduction", pre))

    for i, match in enumerate(matches):
        header = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            sections.append((header, content))

    return sections


def _sub_chunk(header: str, content: str, chunk_size: int, overlap: int) -> list[str]:
    """
    If a section exceeds chunk_size characters, split further.
    Maintains overlap characters of context between sub-chunks.
    """
    section_text = f"## {header}\n{content}"

    if len(section_text) <= chunk_size:
        return [section_text]

    # Split content at paragraph boundaries
    paragraphs = re.split(r"\n{2,}", content)
    chunks: list[str] = []
    current = f"## {header}\n"

    for para in paragraphs:
        candidate = current + para + "\n\n"
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            # Save current chunk if it has real content
            stripped = current.strip()
            if stripped and stripped != f"## {header}":
                chunks.append(stripped)

            # Start new chunk with overlap tail from previous
            if chunks:
                tail = chunks[-1][-overlap:]
                newline_pos = tail.rfind("\n")
                tail = tail[newline_pos + 1:] if newline_pos > 0 else tail
                current = f"## {header} (cont.)\n{tail}\n{para}\n\n"
            else:
                current = f"## {header}\n{para}\n\n"

    # Flush remaining content
    stripped = current.strip()
    if stripped and stripped != f"## {header}":
        chunks.append(stripped)

    # Fallback: brute-force split if nothing was produced
    if not chunks:
        text = section_text
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                newline = text.rfind("\n", start, end)
                if newline > start:
                    end = newline
            chunks.append(text[start:end].strip())
            start = end - overlap

    return [c for c in chunks if c.strip()]


def chunk_document(filepath: str) -> list[dict]:
    """
    Read a markdown file and return a list of chunk dicts:
    {"text": str, "source": str, "topic": str, "chunk_index": int}
    """
    path = Path(filepath)
    filename = path.name
    topic = _topic_from_filename(filename)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    sections = _split_by_headers(text)
    chunks: list[dict] = []

    for chunk_index, (header, content) in enumerate(
        (h, c) for section in sections for h, c in [section]
    ):
        sub_chunks = _sub_chunk(header, content, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        for i, chunk_text in enumerate(sub_chunks):
            chunks.append({
                "text": chunk_text,
                "source": filename,
                "topic": topic,
                "chunk_index": len(chunks),
            })

    return chunks


def chunk_all_documents(knowledge_dir: str) -> list[dict]:
    """Read and chunk all .md files from knowledge_dir."""
    knowledge_path = Path(knowledge_dir)
    if not knowledge_path.exists():
        print(f"[ERROR] Knowledge directory not found: {knowledge_dir}")
        return []

    md_files = sorted(knowledge_path.glob("*.md"))
    if not md_files:
        print(f"[WARN] No .md files found in {knowledge_dir}")
        return []

    all_chunks: list[dict] = []
    for md_file in md_files:
        try:
            doc_chunks = chunk_document(str(md_file))
            all_chunks.extend(doc_chunks)
            print(f"  Chunked {md_file.name}: {len(doc_chunks)} chunks")
        except Exception as e:
            print(f"  [ERROR] Failed to chunk {md_file.name}: {e}")

    return all_chunks


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str], client: openai.OpenAI, batch_size: int = 100) -> list[list[float]]:
    """Embed a list of strings in batches using the OpenAI embedding API."""
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=batch,
        )
        # Sort by index to preserve order
        batch_embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
        all_embeddings.extend(batch_embeddings)
        total_batches = (len(texts) - 1) // batch_size + 1
        print(f"  Embedded batch {i // batch_size + 1}/{total_batches} ({len(batch)} texts)")

    return all_embeddings


# ---------------------------------------------------------------------------
# ChromaDB Storage
# ---------------------------------------------------------------------------

def get_chroma_client() -> chromadb.PersistentClient:
    """Create or connect to the persisted ChromaDB instance."""
    os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)


def store_chunks(
    chunks: list[dict],
    embeddings: list[list[float]],
    chroma_client: chromadb.PersistentClient,
) -> chromadb.Collection:
    """
    Store chunks and embeddings in ChromaDB.
    Deletes and recreates collection for idempotent re-embedding.
    """
    try:
        chroma_client.delete_collection(config.CHROMA_KNOWLEDGE_COLLECTION)
        print(f"  Deleted existing collection '{config.CHROMA_KNOWLEDGE_COLLECTION}'")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=config.CHROMA_KNOWLEDGE_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {"source": c["source"], "topic": c["topic"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]

    batch_size = 500
    for i in range(0, len(chunks), batch_size):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )
        batch_num = i // batch_size + 1
        n_in_batch = min(batch_size, len(chunks) - i)
        print(f"  Stored batch {batch_num} ({n_in_batch} chunks)")

    return collection


def ensure_memory_collection(chroma_client: chromadb.PersistentClient) -> None:
    """Create the past_solutions memory collection if it doesn't exist (Phase 5)."""
    try:
        chroma_client.get_collection(config.CHROMA_MEMORY_COLLECTION)
        print(f"  Memory collection '{config.CHROMA_MEMORY_COLLECTION}' already exists.")
    except Exception:
        chroma_client.create_collection(
            name=config.CHROMA_MEMORY_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"  Created empty memory collection '{config.CHROMA_MEMORY_COLLECTION}'.")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def build_knowledge_base() -> dict:
    """
    Build the knowledge base if the ChromaDB collection is empty.
    Safe to call on every app startup — skips if already populated.
    Returns stats dict.
    """
    chroma_client = get_chroma_client()
    try:
        collection = chroma_client.get_collection(config.CHROMA_KNOWLEDGE_COLLECTION)
        count = collection.count()
        if count > 0:
            print(f"[KnowledgeBase] Already populated ({count} chunks). Skipping embed.")
            # Ensure memory collection exists even when skipping
            ensure_memory_collection(chroma_client)
            return {"files": 0, "chunks": count, "stored": count, "skipped": True}
    except Exception:
        pass  # Collection doesn't exist yet — proceed with full embed

    print("[KnowledgeBase] Collection empty or missing. Building knowledge base...")
    result = run_embedding_pipeline()
    print(f"[KnowledgeBase] Done. {result.get('chunks', 0)} chunks created.")
    return result


def run_embedding_pipeline() -> dict:
    """
    Full pipeline: chunk → embed → store.
    Returns stats dict with files, chunks, stored counts.
    """
    openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    chroma_client = get_chroma_client()

    print("\n[1/4] Chunking knowledge base documents...")
    chunks = chunk_all_documents(config.KNOWLEDGE_DIR)
    if not chunks:
        return {"files": 0, "chunks": 0, "error": "No chunks generated"}

    unique_files = len(set(c["source"] for c in chunks))
    print(f"\n  Total: {unique_files} files, {len(chunks)} chunks")

    print("\n[2/4] Embedding chunks with OpenAI...")
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts, openai_client)

    print("\n[3/4] Storing in ChromaDB...")
    collection = store_chunks(chunks, embeddings, chroma_client)

    print("\n[4/4] Ensuring memory collection exists...")
    ensure_memory_collection(chroma_client)

    return {"files": unique_files, "chunks": len(chunks), "stored": collection.count()}


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Math Mentor — Knowledge Base Embedder")
    print("=" * 60)

    result = run_embedding_pipeline()

    print(f"\n{'=' * 60}")
    print("Pipeline Complete")
    print(f"  Files processed : {result.get('files', 0)}")
    print(f"  Chunks created  : {result.get('chunks', 0)}")
    print(f"  Chunks stored   : {result.get('stored', 0)}")

    if result.get("error"):
        print(f"  Error: {result['error']}")
        sys.exit(1)

    # Test query
    print(f"\n{'=' * 60}")
    print("Test Query: 'quadratic formula roots'")
    print("=" * 60)

    try:
        openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        chroma_client = get_chroma_client()
        collection = chroma_client.get_collection(config.CHROMA_KNOWLEDGE_COLLECTION)

        query_response = openai_client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=["quadratic formula roots"],
        )
        query_embedding = query_response.data[0].embedding

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "metadatas", "distances"],
        )

        for i in range(len(results["ids"][0])):
            score = 1 - results["distances"][0][i]
            preview = results["documents"][0][i][:200].replace("\n", " ")
            print(f"\nResult {i + 1}:")
            print(f"  Source : {results['metadatas'][0][i]['source']}")
            print(f"  Topic  : {results['metadatas'][0][i]['topic']}")
            print(f"  Score  : {score:.4f}")
            print(f"  Text   : {preview}...")

    except Exception as e:
        print(f"[ERROR] Test query failed: {e}")
        sys.exit(1)
