"""
GovernAI Studio — Hybrid Retrieval Pipeline
Adaptive query routing: simple queries → vector, complex → graph traversal.
"""
import re
from enum import Enum
from typing import Optional

import structlog
from app.corpus.graph_builder import GovernAIGraphBuilder

logger = structlog.get_logger()


class QueryComplexity(Enum):
    SIMPLE = "naive"
    ENTITY = "local"
    THEMATIC = "global"
    COMPLEX = "hybrid"


class QueryRouter:
    """Rule-based query classifier. No LLM call needed — saves rate budget."""

    SECTION_PATTERNS = [
        r"section\s+\d+", r"rule\s+\d+", r"article\s+\d+",
        r"clause\s+\d+", r"para\s+\d+", r"schedule\s+\w+",
    ]

    THEMATIC_KEYWORDS = [
        "principle", "sutra", "framework", "approach", "philosophy",
        "how should", "what is the best", "compare", "relationship between",
        "meaning of", "concept of", "purpose of",
    ]

    CROSS_DOC_INDICATORS = [
        "conflict", "interact", "together", "versus", "both",
        "which acts", "which laws", "multiple", "cross-reference",
        "in conjunction", "read with", "overrides",
    ]

    def classify(self, query: str) -> QueryComplexity:
        q = query.lower()

        for pattern in self.SECTION_PATTERNS:
            if re.search(pattern, q):
                return QueryComplexity.ENTITY

        thematic_count = sum(1 for kw in self.THEMATIC_KEYWORDS if kw in q)
        if thematic_count >= 1:
            return QueryComplexity.THEMATIC

        cross_count = sum(1 for ind in self.CROSS_DOC_INDICATORS if ind in q)
        if cross_count >= 1:
            return QueryComplexity.COMPLEX

        return QueryComplexity.SIMPLE


class GovernAIRetriever:
    """
    The complete retrieval pipeline for the Reference Whisperer.
    
    Flow: query → classify → route → retrieve → structure → return
    """

    def __init__(self, graph: GovernAIGraphBuilder):
        self.graph = graph
        self.router = QueryRouter()

    async def retrieve(
        self,
        scenario_context: str,
        decision_prompt: str,
        whisperer_keywords: Optional[list[str]] = None,
    ) -> dict:
        """
        Main entry point for reference retrieval.

        Args:
            scenario_context: The scenario's narrative (for context)
            decision_prompt: The current decision moment text
            whisperer_keywords: Scenario-authored keywords to boost relevance

        Returns:
            Structured dict with references, mode used, and disclaimer
        """
        # Build enriched query
        parts = []
        if scenario_context:
            # Take first 200 chars of context to avoid token bloat
            parts.append(f"Context: {scenario_context[:200]}")
        parts.append(f"Question: {decision_prompt}")
        if whisperer_keywords:
            parts.append(f"Keywords: {', '.join(whisperer_keywords)}")
        full_query = "\n".join(parts)

        # Classify and route
        complexity = self.router.classify(full_query)
        logger.info("query_classified", mode=complexity.value, query_len=len(full_query))

        # Execute retrieval
        raw_result = await self.graph.query(
            query=full_query,
            mode=complexity.value,
            top_k=5,
        )

        return {
            "query": decision_prompt,
            "mode_used": complexity.value,
            "references": raw_result,
            "keywords_used": whisperer_keywords or [],
            "disclaimer": "Contextual suggestions, not legal advice.",
        }
