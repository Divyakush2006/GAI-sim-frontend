"""
GovernAI Studio — Reference Whisperer API Route (Production)
=============================================================
Graph-powered reference surfacing at decision moments.
Pulls real session data and formats via the Whisperer agent.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.retrieval.pipeline import GovernAIRetriever
from app.corpus.graph_builder import GovernAIGraphBuilder
from app.ai.agents import ReferenceWhispererAgent
from app.ai.gateway import LLMGateway, LLMBusyError

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/sessions", tags=["whisperer"])


class ReferenceResponse(BaseModel):
    references: dict | str
    mode_used: str
    keywords_used: list[str]
    disclaimer: str
    formatted: bool


def get_retriever(request: Request) -> GovernAIRetriever:
    """Dependency: returns the retriever instance."""
    graph = request.app.state.graph_rag
    return GovernAIRetriever(graph)


def get_gateway(request: Request) -> LLMGateway:
    """Dependency: returns the LLM Gateway."""
    return request.app.state.llm_gateway


@router.get("/{session_id}/reference", response_model=ReferenceResponse)
async def get_references(
    session_id: str,
    decision_moment_id: str,
    request: Request,
    retriever: GovernAIRetriever = Depends(get_retriever),
):
    """
    Reference Whisperer endpoint.

    Surfaces relevant legal/governance references for the current
    decision moment using GraphRAG hybrid retrieval, then formats
    them via the Whisperer agent for officer readability.

    Flow:
    1. Load session state → get scenario context + decision prompt
    2. Query GraphRAG with scenario keywords
    3. Format results via Whisperer agent
    4. Track which references were shown (for Reflection Coach)
    """
    # Get session state
    from app.api.routes.simulation import _session_cache
    state = _session_cache.get(session_id)

    if state:
        # Real session — use actual data
        scenario = state.scenario
        decision_moment = None
        for dm in scenario.get("decision_moments", []):
            if dm["id"] == decision_moment_id:
                decision_moment = dm
                break

        if not decision_moment:
            raise HTTPException(404, {"error": "DECISION_MOMENT_NOT_FOUND"})

        scenario_context = scenario.get("description", "")
        decision_prompt = decision_moment.get("prompt", "")
        whisperer_keywords_map = scenario.get("whisperer_keywords", {})
        keywords = whisperer_keywords_map.get(decision_moment_id, [])
    else:
        # Fallback for testing without active session
        scenario_context = "AI governance decision in Indian government"
        decision_prompt = "General governance query"
        keywords = ["AI governance", "India"]

    # Step 1: Retrieve from GraphRAG
    retrieval_result = await retriever.retrieve(
        scenario_context=scenario_context,
        decision_prompt=decision_prompt,
        whisperer_keywords=keywords,
    )

    raw_references = retrieval_result.get("references", "")
    mode_used = retrieval_result.get("mode_used", "hybrid")

    # Step 2: Format via Whisperer agent (if graph has content)
    formatted = False
    if raw_references and raw_references != "Reference retrieval error: " and len(str(raw_references)) > 50:
        try:
            gateway = get_gateway(request)
            whisperer_prompt = ReferenceWhispererAgent.build_prompt(
                raw_references=str(raw_references),
                decision_prompt=decision_prompt,
                scenario_context=scenario_context,
                whisperer_keywords=keywords,
            )
            formatted_response = await gateway.generate(
                system_prompt=whisperer_prompt["system_prompt"],
                user_prompt=whisperer_prompt["user_prompt"],
                role="whisperer",
            )
            # Parse JSON from response
            from app.api.routes.simulation import _parse_json_response
            references_data = _parse_json_response(formatted_response)
            formatted = True
        except Exception as e:
            logger.warning("whisperer_format_failed", error=str(e)[:80])
            references_data = raw_references
    else:
        references_data = {
            "primary_references": [],
            "contextual_note": "The knowledge graph has not been populated yet. References will be available after the legal corpus is ingested.",
            "gaps": ["Full legal corpus not yet indexed"],
            "caution": "No references available at this time.",
        }
        formatted = True

    # Track references shown (for Reflection Coach)
    if state:
        state.references_shown.extend(keywords)

    return ReferenceResponse(
        references=references_data,
        mode_used=mode_used,
        keywords_used=keywords,
        disclaimer="These are contextual suggestions for reference, not legal advice.",
        formatted=formatted,
    )
