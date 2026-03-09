"""
Memory Store — Persist interactions, feedback, and semantic search over past solutions.

Stores every interaction as JSON in memory/memory.json and embeds problem texts
into a ChromaDB collection (past_solutions) for similarity retrieval.
"""

import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path

import chromadb
import openai

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config


class MemoryStore:
    """Handles all memory operations: storage, feedback, stats, and vector search."""

    def __init__(self, memory_file: str = config.MEMORY_FILE) -> None:
        self._memory_file = memory_file
        self._lock = threading.Lock()
        self._data: list[dict] = self._load()

        # Lazy-init for ChromaDB / OpenAI (only when vector methods are called)
        self._chroma_client: chromadb.PersistentClient | None = None
        self._collection: chromadb.Collection | None = None
        self._openai_client: openai.OpenAI | None = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> list[dict]:
        """Read memory.json; return [] on corruption or missing file."""
        try:
            path = Path(self._memory_file)
            if not path.exists():
                return []
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self) -> None:
        """Write self._data to disk atomically."""
        with self._lock:
            path = Path(self._memory_file)
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, default=str)

    def _ensure_vector_store(self) -> None:
        """Lazy-init ChromaDB client and past_solutions collection."""
        if self._collection is not None:
            return
        try:
            os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
            try:
                self._collection = self._chroma_client.get_collection(
                    config.CHROMA_MEMORY_COLLECTION
                )
            except Exception:
                self._collection = self._chroma_client.create_collection(
                    name=config.CHROMA_MEMORY_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
        except Exception as e:
            print(f"[Memory] ChromaDB init failed: {e}")
            self._collection = None

    def _get_openai(self) -> openai.OpenAI:
        if self._openai_client is None:
            self._openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        return self._openai_client

    def _embed(self, text: str) -> list[float]:
        """Embed a single string using the configured embedding model."""
        client = self._get_openai()
        response = client.embeddings.create(
            model=config.EMBEDDING_MODEL,
            input=[text],
        )
        return response.data[0].embedding

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save_interaction(self, interaction: dict) -> str:
        """Append interaction to memory and save to disk. Returns the interaction ID."""
        self._data.append(interaction)
        self._save()
        return interaction["id"]

    def update_feedback(self, interaction_id: str, rating: str, comment: str = "") -> bool:
        """Update feedback for an existing interaction. Returns True if found."""
        for item in self._data:
            if item.get("id") == interaction_id:
                item["user_feedback"] = {
                    "rating": rating,
                    "comment": comment,
                    "timestamp": datetime.now().isoformat(),
                }
                self._save()
                return True
        return False

    def get_all(self) -> list[dict]:
        """Return all stored interactions."""
        return list(self._data)

    def get_by_id(self, interaction_id: str) -> dict | None:
        """Get a specific interaction by ID."""
        for item in self._data:
            if item.get("id") == interaction_id:
                return item
        return None

    def get_successful_solutions(self) -> list[dict]:
        """Return interactions where user_feedback.rating == 'correct'."""
        return [
            item for item in self._data
            if item.get("user_feedback", {}).get("rating") == "correct"
        ]

    def get_stats(self) -> dict:
        """Return summary stats: total, correct, incorrect, no_feedback, by_topic."""
        total = len(self._data)
        correct = 0
        incorrect = 0
        no_feedback = 0
        by_topic: dict[str, int] = {}

        for item in self._data:
            rating = item.get("user_feedback", {}).get("rating")
            if rating == "correct":
                correct += 1
            elif rating == "incorrect":
                incorrect += 1
            else:
                no_feedback += 1

            topic = item.get("topic", "unknown")
            by_topic[topic] = by_topic.get(topic, 0) + 1

        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "no_feedback": no_feedback,
            "by_topic": by_topic,
        }

    def clear(self) -> None:
        """Reset memory.json to [] and clear the ChromaDB past_solutions collection."""
        self._data = []
        self._save()
        try:
            self._ensure_vector_store()
            if self._chroma_client is not None:
                try:
                    self._chroma_client.delete_collection(config.CHROMA_MEMORY_COLLECTION)
                except Exception:
                    pass
                self._collection = self._chroma_client.create_collection(
                    name=config.CHROMA_MEMORY_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
        except Exception as e:
            print(f"[Memory] Failed to clear vector store: {e}")

    # ------------------------------------------------------------------
    # Vector store — embed & search
    # ------------------------------------------------------------------

    def add_to_vector_store(self, interaction_id: str, problem_text: str) -> None:
        """Embed the problem text and store in ChromaDB for similarity search."""
        try:
            self._ensure_vector_store()
            if self._collection is None:
                return
            embedding = self._embed(problem_text)
            self._collection.upsert(
                ids=[interaction_id],
                embeddings=[embedding],
                documents=[problem_text],
                metadatas=[{"interaction_id": interaction_id}],
            )
        except Exception as e:
            print(f"[Memory] add_to_vector_store failed: {e}")

    def find_similar(
        self,
        query: str,
        threshold: float = config.MEMORY_SIMILARITY_THRESHOLD,
    ) -> list[dict]:
        """
        Search past_solutions for similar problems.

        Returns list of full interaction dicts (from memory.json) enriched
        with a 'similarity_score' field, sorted by similarity descending.
        Only includes matches with similarity >= threshold.
        """
        try:
            self._ensure_vector_store()
            if self._collection is None or self._collection.count() == 0:
                return []

            embedding = self._embed(query)
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=min(5, self._collection.count()),
                include=["metadatas", "distances"],
            )

            matches: list[dict] = []
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]
                similarity = 1.0 - distance
                if similarity < threshold:
                    continue

                interaction_id = results["metadatas"][0][i].get("interaction_id")
                interaction = self.get_by_id(interaction_id)
                if interaction is None:
                    continue

                enriched = dict(interaction)
                enriched["similarity_score"] = round(similarity, 4)
                matches.append(enriched)

            matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            return matches

        except Exception as e:
            print(f"[Memory] find_similar failed: {e}")
            return []
