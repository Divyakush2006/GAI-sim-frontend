"""
GovernAI Studio — GraphRAG Knowledge Graph Builder
Uses LightRAG for graph-enhanced retrieval over the Indian legal/governance corpus.
"""
import os
import asyncio
from pathlib import Path
from typing import Optional

import numpy as np
import structlog

logger = structlog.get_logger()


class GovernAIGraphBuilder:
    """
    Manages the LightRAG knowledge graph for the Reference Whisperer.

    The graph stores entities (statutes, sections, institutions, concepts)
    and relationships (references, defines, governs) extracted from the
    53-document Indian AI governance corpus.
    """

    def __init__(self, working_dir: str = "./graph_data"):
        self.working_dir = working_dir
        os.makedirs(working_dir, exist_ok=True)
        self._rag = None  # Lazy initialization

    @property
    def rag(self):
        """Lazy-load LightRAG to avoid slowing down cold starts."""
        if self._rag is None:
            self._initialize_rag()
        return self._rag

    def _initialize_rag(self):
        """Initialize LightRAG with Gemini free tier."""
        try:
            from lightrag import LightRAG, QueryParam
            from lightrag.utils import EmbeddingFunc

            self._rag = LightRAG(
                working_dir=self.working_dir,
                llm_model_func=self._llm_complete,
                llm_model_max_async=2,       # Stay under 15 RPM
                embedding_func=EmbeddingFunc(
                    embedding_dim=3072,      # gemini-embedding-2 outputs 3072-dim
                    max_token_size=8192,
                    func=self._embed,
                ),
                chunk_token_size=300,
                chunk_overlap_token_size=100,
                entity_extract_max_gleaning=2,
                graph_storage="NetworkXStorage",
                vector_storage="NanoVectorDBStorage",
                kv_storage="JsonKVStorage",
            )
            logger.info("lightrag_initialized", working_dir=self.working_dir)
        except Exception as e:
            logger.error("lightrag_init_failed", error=str(e))
            raise

    async def ensure_initialized(self):
        """Ensure LightRAG storages are initialized (required in v1.4.9+)."""
        _ = self.rag  # trigger lazy init
        await self._rag.initialize_storages()
        from lightrag.kg.shared_storage import initialize_pipeline_status
        await initialize_pipeline_status()
        logger.info("lightrag_storages_ready")

    async def _llm_complete(self, prompt: str, **kwargs) -> str:
        """LLM function for LightRAG entity extraction.
        Uses Gemini with key rotation, falls back to Groq via LiteLLM."""
        from app.ai.key_rotator import get_rotator
        rotator = get_rotator()

        # Try up to 3 rotated Gemini keys
        last_error = None
        for attempt in range(min(3, max(rotator.key_count, 1))):
            api_key = rotator.get_key()
            if not api_key:
                break
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"temperature": 0.1, "max_output_tokens": 2000},
                )
                rotator.mark_success(api_key)
                return response.text
            except Exception as e:
                last_error = e
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    rotator.mark_exhausted(api_key)
                    continue
                break

        # Fallback to Groq
        logger.warning("gemini_fallback_to_groq", error=str(last_error)[:80] if last_error else "no keys")
        import litellm
        response = await litellm.acompletion(
            model="groq/llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=2000, timeout=30,
        )
        return response.choices[0].message.content

    async def _embed(self, texts: list[str]) -> np.ndarray:
        """Embedding function using Gemini with key rotation."""
        from app.ai.key_rotator import get_rotator
        rotator = get_rotator()

        for attempt in range(min(3, max(rotator.key_count, 1))):
            api_key = rotator.get_key()
            if not api_key:
                break
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                result = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=texts if isinstance(texts, list) else [texts],
                )
                rotator.mark_success(api_key)
                embeddings = [e.values for e in result.embeddings]
                return np.array(embeddings)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    rotator.mark_exhausted(api_key)
                    continue
                raise

        raise RuntimeError("All Gemini keys exhausted for embeddings")

    async def ingest_document(self, text: str):
        """Ingest a single document into the knowledge graph."""
        await self.ensure_initialized()
        await self.rag.ainsert(text)
        logger.info("document_ingested", chars=len(text))

    async def ingest_batch(self, documents: list[str], batch_size: int = 10):
        """
        Batch ingest documents with rate limit pauses.
        Designed for the one-time corpus construction.
        """
        total = len(documents)
        for i in range(0, total, batch_size):
            batch = documents[i : i + batch_size]
            combined = "\n\n---\n\n".join(batch)

            await self.rag.ainsert(combined)

            progress = min(i + batch_size, total)
            logger.info("batch_progress", done=progress, total=total)

            # Rate limit pause (Gemini free: 15 RPM)
            if (i // batch_size) % 5 == 0 and i > 0:
                await asyncio.sleep(10)

        logger.info("ingestion_complete", total_documents=total)

    async def query(
        self,
        query: str,
        mode: str = "hybrid",
        top_k: int = 5,
    ) -> str:
        """
        Query the knowledge graph.

        Modes:
          - naive:  Pure vector search (fastest, simple queries)
          - local:  Entity-focused graph traversal (specific clauses)
          - global: Community-level thematic search (principles, themes)
          - hybrid: Both local + global (best quality, default)
        """
        from lightrag import QueryParam

        try:
            result = await self.rag.aquery(
                query, param=QueryParam(mode=mode, top_k=top_k)
            )
            logger.info("graph_query", mode=mode, query_len=len(query))
            return result
        except Exception as e:
            logger.error("graph_query_failed", error=str(e), mode=mode)
            return f"Reference retrieval error: {str(e)}"

    def get_stats(self) -> dict:
        """Get graph statistics."""
        try:
            import networkx as nx

            graph_file = Path(self.working_dir) / "graph_chunk_entity_relation.graphml"
            if not graph_file.exists():
                return {"status": "empty", "entities": 0, "relationships": 0}

            G = nx.read_graphml(str(graph_file))
            return {
                "status": "ready",
                "entities": G.number_of_nodes(),
                "relationships": G.number_of_edges(),
            }
        except Exception:
            return {"status": "unknown"}
