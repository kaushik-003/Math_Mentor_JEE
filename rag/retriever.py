"""
RAG Retriever — Query the ChromaDB vector store.

Provides a Retriever class with search() and get_formatted_context()
methods for injecting relevant knowledge into solver prompts.
"""

import sys
from pathlib import Path

import openai
import chromadb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


class Retriever:
    """
    Connects to the persisted ChromaDB knowledge base and provides
    semantic search over embedded math reference chunks.
    """

    def __init__(self) -> None:
        self._openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self._chroma_client: chromadb.PersistentClient | None = None
        self._collection: chromadb.Collection | None = None
        self._ready = False
        self._init_chroma()

    def _init_chroma(self) -> None:
        """Connect to persisted ChromaDB; sets _ready = False if unavailable."""
        try:
            self._chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
            self._collection = self._chroma_client.get_collection(
                config.CHROMA_KNOWLEDGE_COLLECTION
            )
            count = self._collection.count()
            if count == 0:
                print(
                    f"[RAG] Collection '{config.CHROMA_KNOWLEDGE_COLLECTION}' is empty. "
                    "Run rag/embedder.py first."
                )
                self._ready = False
            else:
                self._ready = True
        except Exception as e:
            print(
                f"[RAG] ChromaDB not available ({e}). "
                "RAG will return empty context. Run rag/embedder.py to set up."
            )
            self._ready = False

    def _embed_query(self, query: str) -> list[float]:
        """Embed a single query string using the configured embedding model."""
        response = self._openai_client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=[query],
        )
        return response.data[0].embedding

    def search(
        self,
        query: str,
        topic: str | None = None,
        top_k: int = config.RAG_TOP_K,
    ) -> list[dict]:
        """
        Search for relevant chunks in the knowledge base.

        Args:
            query: The natural language query string.
            topic: Optional topic filter (e.g. "algebra", "calculus").
                   If provided, only chunks with matching metadata topic are returned.
            top_k: Number of results to return.

        Returns:
            List of dicts: {"text", "source", "topic", "score"}
            Empty list if collection unavailable or no results found.
        """
        if not self._ready or self._collection is None:
            return []

        try:
            query_embedding = self._embed_query(query)

            # Build optional metadata filter
            where_filter = None
            if topic and topic in config.SUPPORTED_TOPICS:
                where_filter = {"topic": {"$eq": topic}}

            query_kwargs: dict = {
                "query_embeddings": [query_embedding],
                "n_results": min(top_k, self._collection.count()),
                "include": ["documents", "metadatas", "distances"],
            }
            if where_filter:
                query_kwargs["where"] = where_filter

            results = self._collection.query(**query_kwargs)

            output: list[dict] = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                # ChromaDB cosine space returns distance = 1 - similarity
                score = 1.0 - distance
                output.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i].get("source", "unknown"),
                    "topic": results["metadatas"][0][i].get("topic", "unknown"),
                    "score": round(score, 4),
                })

            return output

        except Exception as e:
            print(f"[RAG] Search error: {e}")
            return []

    def get_formatted_context(
        self,
        query: str,
        topic: str | None = None,
    ) -> str:
        """
        Search and format results as a clean string for LLM prompt injection.

        Format:
            Source: [filename] | Topic: [topic]
            [chunk text]
            ---

        Returns empty string if no results found.
        """
        results = self.search(query, topic=topic)
        if not results:
            return ""

        parts: list[str] = []
        for r in results:
            parts.append(
                f"Source: {r['source']} | Topic: {r['topic']}\n"
                f"{r['text']}\n"
                f"---"
            )

        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Entry Point — Manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Math Mentor — RAG Retriever Test")
    print("=" * 60)

    retriever = Retriever()

    test_queries = [
        ("quadratic formula discriminant", "algebra"),
        ("probability of two events", "probability"),
        ("L'Hopital rule limit", "calculus"),
        ("matrix determinant properties", "linear_algebra"),
    ]

    for query, topic in test_queries:
        print(f"\nQuery : '{query}' (topic filter: {topic})")
        print("-" * 50)
        results = retriever.search(query, topic=topic, top_k=2)
        if not results:
            print("  No results.")
        for i, r in enumerate(results, 1):
            preview = r["text"][:150].replace("\n", " ")
            print(f"  [{i}] score={r['score']:.4f} | {r['source']}")
            print(f"       {preview}...")

    print(f"\n{'=' * 60}")
    print("Formatted Context Sample:")
    print("=" * 60)
    ctx = retriever.get_formatted_context("chain rule derivative", topic="calculus")
    print(ctx[:600] if ctx else "(empty — run embedder first)")
