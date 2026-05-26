"""
GovernAI Studio — Simulation API Routes (Production)
=====================================================
Fully wired simulation lifecycle with real DB operations,
LLM Gateway calls, and state machine enforcement.

Endpoints:
  POST /sessions/start              → Start a new simulation
  POST /sessions/{id}/advance       → Advance from SETTING to INTERACTION
  POST /sessions/{id}/interact      → Talk to an NPC
  POST /sessions/{id}/decision      → Submit a decision
  GET  /sessions/{id}/consequences  → Get consequence artifacts
  GET  /sessions/{id}/reflection    → Get Seven Sutras debrief
  GET  /sessions/{id}/status        → Get current session state
  POST /sessions/{id}/draft         → Request drafting assistance
"""
import json
from uuid import uuid4, UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Scenario, SimulationSession, Decision, Reflection
from app.api.deps import get_current_officer
from app.ai.gateway import LLMGateway, LLMBusyError
from app.ai.agents import (
    ScenarioDirectorAgent,
    NPCDialogueAgent,
    ReferenceWhispererAgent,
    ReflectionCoachAgent,
    DraftingPartnerAgent,
    ConsequenceEngine,
)
from app.simulation import SimulationState, SimulationStage

import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/sessions", tags=["simulation"])


# ============================================================
# Request/Response Models
# ============================================================

class StartSessionRequest(BaseModel):
    scenario_slug: str
    officer_tier: Optional[str] = "B"  # Will be set from auth in production

class StartSessionResponse(BaseModel):
    session_id: str
    stage: str
    setting_narrative: str
    npcs: list[dict]
    initial_prompt: str

class AdvanceStageRequest(BaseModel):
    target_stage: str

class NPCInteractRequest(BaseModel):
    npc_id: str
    message: str

class NPCInteractResponse(BaseModel):
    npc_name: str
    npc_role: str
    response: str
    interaction_count: int
    required_met: bool
    can_advance_to_decisions: bool

class SubmitDecisionRequest(BaseModel):
    decision_moment_id: str
    choice_type: str          # OPTION or FREEFORM
    selected_option: Optional[str] = None
    free_text: Optional[str] = None

class SubmitDecisionResponse(BaseModel):
    accepted: bool
    next_stage: str
    decisions_remaining: int
    whisperer_keywords: list[str]

class DraftRequest(BaseModel):
    request_text: str

class SessionStatusResponse(BaseModel):
    session_id: str
    stage: str
    decisions_made: int
    decisions_total: int
    npcs_consulted: list[str]
    is_complete: bool


# ============================================================
# Session cache with DB persistence
# Sessions are kept in-memory for speed, auto-persisted to DB
# on every mutation, and auto-recovered from DB on cache miss.
# ============================================================
_session_cache: dict[str, SimulationState] = {}


def _get_gateway(request: Request) -> LLMGateway:
    """Get the LLM Gateway from app state."""
    return request.app.state.llm_gateway


# ============================================================
# Endpoints
# ============================================================

@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    req: StartSessionRequest,
    request: Request,
    db=Depends(get_db),
    current_officer: Optional["Officer"] = Depends(get_current_officer),
):
    """
    Start a new simulation session.

    1. Load scenario from DB by slug
    2. Create session record (linked to authenticated officer or guest)
    3. Invoke Scenario Director to adapt narrative
    4. Return immersive opening scene
    """
    gateway = _get_gateway(request)

    # Load scenario from DB
    result = await db.execute(
        select(Scenario).where(Scenario.slug == req.scenario_slug, Scenario.is_active == True)
    )
    scenario_record = result.scalar_one_or_none()
    if not scenario_record:
        raise HTTPException(status_code=404, detail={"error": "SCENARIO_NOT_FOUND"})

    # Build scenario dict from ORM
    scenario_data = {
        "id": str(scenario_record.id),
        "slug": scenario_record.slug,
        "title": scenario_record.title,
        "domain": scenario_record.domain,
        "description": scenario_record.description,
        "estimated_minutes": scenario_record.estimated_minutes,
        "tier_scope": scenario_record.tier_scope,
        "setting_narrative": scenario_record.setting_narrative,
        "npcs": scenario_record.npcs,
        "decision_moments": scenario_record.decision_moments,
        "consequence_branches": scenario_record.consequence_branches,
        "whisperer_keywords": scenario_record.whisperer_keywords,
        "sutras": scenario_record.sutras,
    }

    # Create session record in DB
    session_id = uuid4()

    # Use authenticated officer if available, else create guest
    if current_officer:
        officer_id = current_officer.id
        officer_tier = current_officer.tier or req.officer_tier or "B"
    else:
        from app.db.models import Officer
        officer_id = uuid4()
        guest_email = f"guest_{str(officer_id)[:8]}@governai.dev"
        guest_officer = Officer(
            id=officer_id,
            email=guest_email,
            tier=req.officer_tier or "B",
            onboarding_complete=True,
        )
        db.add(guest_officer)
        await db.flush()
        officer_tier = req.officer_tier or "B"

    session_record = SimulationSession(
        id=session_id,
        officer_id=officer_id,
        scenario_id=scenario_record.id,
        current_stage="SETTING",
        is_complete=False,
        conversation_history={},
        started_at=datetime.now(timezone.utc),
    )
    db.add(session_record)

    # Initialize state machine
    state = SimulationState(
        session_id=str(session_id),
        scenario=scenario_data,
        officer_tier=officer_tier,
        officer_id=str(officer_id),
    )

    # Invoke Scenario Director to adapt narrative
    director_prompt = ScenarioDirectorAgent.build_prompt(
        scenario=scenario_data,
        officer_tier=state.officer_tier,
    )

    try:
        raw_response = await gateway.generate(
            system_prompt=director_prompt["system_prompt"],
            user_prompt=director_prompt["user_prompt"],
            role="director",
        )
        # Try to parse JSON from the Director's response
        narrative_data = _parse_json_response(raw_response)
        narrative_text = narrative_data.get("narrative", raw_response)
        initial_prompt = narrative_data.get(
            "initial_prompt",
            "What would you like to do first?"
        )
    except (LLMBusyError, Exception) as e:
        # Fallback to base narrative if LLM is unavailable
        logger.warning("director_fallback", error=str(e)[:80])
        tier_key = f"tier_{state.officer_tier.lower()}"
        setting = scenario_data.get("setting_narrative", {})
        narrative_text = setting.get(tier_key, setting.get("tier_b", ""))
        initial_prompt = "What would you like to do first?"

    state.adapted_narrative = narrative_text

    # Update DB with adapted narrative
    session_record.adapted_narrative = narrative_text
    await db.flush()

    # Cache state
    _session_cache[str(session_id)] = state

    # Build NPC list for frontend (without hidden agendas)
    safe_npcs = []
    for npc in scenario_data.get("npcs", []):
        safe_npcs.append({
            "id": npc["id"],
            "name": npc["name"],
            "role": npc["role"],
            "required_interactions": npc.get("required_interactions", 0),
        })

    logger.info(
        "session_started",
        session_id=str(session_id),
        scenario=scenario_data["slug"],
        tier=state.officer_tier,
    )

    return StartSessionResponse(
        session_id=str(session_id),
        stage=state.current_stage.value,
        setting_narrative=narrative_text,
        npcs=safe_npcs,
        initial_prompt=initial_prompt,
    )


@router.post("/{session_id}/advance")
async def advance_stage(session_id: str, req: AdvanceStageRequest, db=Depends(get_db)):
    """Advance the simulation to the next stage."""
    state = await _get_or_recover_session(session_id, db)

    try:
        target = SimulationStage(req.target_stage)
    except ValueError:
        raise HTTPException(400, {"error": "INVALID_STAGE", "valid": [s.value for s in SimulationStage]})

    # Validate transition
    if target == SimulationStage.DECISION_MOMENTS and not state.required_interactions_met:
        raise HTTPException(400, {
            "error": "REQUIRED_INTERACTIONS_NOT_MET",
            "message": "You must consult the required NPCs before proceeding to decisions.",
        })

    if not state.advance_stage(target):
        raise HTTPException(400, {
            "error": "INVALID_TRANSITION",
            "current": state.current_stage.value,
            "target": target.value,
        })

    # Persist to DB
    await _persist_state(session_id, state, db)

    return {"stage": state.current_stage.value, "session_id": session_id}


@router.post("/{session_id}/interact", response_model=NPCInteractResponse)
async def npc_interact(
    session_id: str,
    req: NPCInteractRequest,
    request: Request,
    db=Depends(get_db),
):
    """
    Send a message to an NPC and receive an in-character response.

    The NPC agent uses the character's personality, hidden agenda,
    and conversation history to generate contextual dialogue.
    """
    state = await _get_or_recover_session(session_id, db)
    gateway = _get_gateway(request)

    # Auto-advance from SETTING to INTERACTION on first interaction
    if state.current_stage == SimulationStage.SETTING:
        state.advance_stage(SimulationStage.INTERACTION)

    if state.current_stage not in (SimulationStage.INTERACTION, SimulationStage.DECISION_MOMENTS):
        raise HTTPException(400, {"error": "WRONG_STAGE", "current": state.current_stage.value})

    # Find NPC
    npc = state.get_npc_by_id(req.npc_id)
    if not npc:
        raise HTTPException(404, {"error": "NPC_NOT_FOUND", "npc_id": req.npc_id})

    # Get conversation history for this NPC
    history = state.conversation_histories.get(req.npc_id, [])

    # Build NPC prompt
    npc_prompt = NPCDialogueAgent.build_prompt(
        npc=npc,
        scenario=state.scenario,
        conversation_history=history,
        officer_message=req.message,
        decisions_made=state.decisions_made,
    )

    # Generate NPC response via Gateway
    try:
        npc_response = await gateway.generate(
            system_prompt=npc_prompt["system_prompt"],
            user_prompt=npc_prompt["user_prompt"],
            role="npc_dialogue",
        )
    except LLMBusyError:
        raise HTTPException(503, {
            "error": "LLM_CAPACITY_EXHAUSTED",
            "message": "All AI providers are busy. Please wait a moment.",
            "retry_after": 60,
        })

    # Record interaction
    state.record_npc_interaction(req.npc_id, req.message, npc_response)

    # Persist to DB
    await _persist_state(session_id, state, db)

    interaction_count = state.npc_interactions.get(req.npc_id, 0)
    can_advance = state.required_interactions_met

    return NPCInteractResponse(
        npc_name=npc["name"],
        npc_role=npc["role"],
        response=npc_response,
        interaction_count=interaction_count,
        required_met=can_advance,
        can_advance_to_decisions=can_advance,
    )


@router.post("/{session_id}/decision", response_model=SubmitDecisionResponse)
async def submit_decision(session_id: str, req: SubmitDecisionRequest, db=Depends(get_db)):
    """
    Submit a decision for the current decision moment.

    Validates against the state machine, records the decision,
    and returns the next stage + whisperer keywords for the next moment.
    """
    state = await _get_or_recover_session(session_id, db)

    # Auto-advance to DECISION_MOMENTS if still in INTERACTION
    if state.current_stage == SimulationStage.INTERACTION:
        if not state.required_interactions_met:
            raise HTTPException(400, {
                "error": "REQUIRED_INTERACTIONS_NOT_MET",
                "message": "Consult required NPCs before making decisions.",
            })
        state.advance_stage(SimulationStage.DECISION_MOMENTS)

    if state.current_stage != SimulationStage.DECISION_MOMENTS:
        raise HTTPException(400, {"error": "WRONG_STAGE", "current": state.current_stage.value})

    # Validate decision moment
    current_moment = state.current_decision_moment
    if not current_moment:
        raise HTTPException(400, {"error": "NO_MORE_DECISIONS"})

    if req.decision_moment_id != current_moment["id"]:
        raise HTTPException(400, {
            "error": "WRONG_DECISION_MOMENT",
            "expected": current_moment["id"],
            "received": req.decision_moment_id,
        })

    # Validate choice
    if req.choice_type == "OPTION":
        valid_options = [o["id"] for o in current_moment.get("options", [])]
        if req.selected_option not in valid_options:
            raise HTTPException(400, {
                "error": "INVALID_OPTION",
                "valid_options": valid_options,
            })
    elif req.choice_type == "FREEFORM":
        if not current_moment.get("allows_freeform", False):
            raise HTTPException(400, {"error": "FREEFORM_NOT_ALLOWED"})
        if not req.free_text or len(req.free_text.strip()) < 10:
            raise HTTPException(400, {"error": "FREEFORM_TOO_SHORT"})

    # Record decision
    state.record_decision(
        decision_moment_id=req.decision_moment_id,
        choice_type=req.choice_type,
        selected_option=req.selected_option,
        free_text=req.free_text,
    )

    # Save decision to DB
    decision_record = Decision(
        id=uuid4(),
        session_id=session_id,
        decision_moment_id=req.decision_moment_id,
        choice_type=req.choice_type,
        selected_option=req.selected_option,
        free_text=req.free_text,
        whisperer_references_shown=state.references_shown,
        npcs_consulted=state.npcs_consulted,
    )
    db.add(decision_record)

    # Determine next stage
    if state.decisions_remaining == 0:
        state.advance_stage(SimulationStage.CONSEQUENCES)
        next_stage = "CONSEQUENCES"
        whisperer_kw = []
    else:
        next_stage = "DECISION_MOMENTS"
        next_moment = state.current_decision_moment
        whisperer_keywords = state.scenario.get("whisperer_keywords", {})
        whisperer_kw = whisperer_keywords.get(
            next_moment["id"] if next_moment else "", []
        )

    # Persist state
    await _persist_state(session_id, state, db)

    return SubmitDecisionResponse(
        accepted=True,
        next_stage=next_stage,
        decisions_remaining=state.decisions_remaining,
        whisperer_keywords=whisperer_kw,
    )


@router.get("/{session_id}/consequences")
async def get_consequences(session_id: str, db=Depends(get_db)):
    """
    Get consequence artifacts based on the officer's decisions.

    Uses the rule-based ConsequenceEngine to determine which branch
    triggers, then returns the consequence artifacts (news headlines,
    RTI filings, internal notes).
    """
    state = await _get_or_recover_session(session_id, db)

    if state.current_stage not in (SimulationStage.CONSEQUENCES, SimulationStage.REFLECTION):
        raise HTTPException(400, {"error": "WRONG_STAGE", "message": "Complete all decisions first."})

    # Determine consequence branch
    branch_name, artifacts = ConsequenceEngine.determine_branch(
        decisions=state.decisions_made,
        consequence_branches=state.scenario.get("consequence_branches", {}),
    )

    state.consequence_branch = branch_name
    state.consequence_artifacts = artifacts

    # Persist
    await _persist_state(session_id, state, db)

    return {
        "branch": branch_name,
        "consequences": artifacts,
        "decisions_summary": [
            {"moment": d["decision_moment_id"], "choice": d.get("selected_option") or (d.get("free_text") or "")[:50]}
            for d in state.decisions_made
        ],
    }


@router.get("/{session_id}/reflection")
async def get_reflection(session_id: str, request: Request, db=Depends(get_db)):
    """
    Get the Seven Sutras reflective debrief.

    Invokes the Reflection Coach agent with full session context
    to generate a structured, non-evaluative debrief.
    """
    state = await _get_or_recover_session(session_id, db)
    gateway = _get_gateway(request)

    # Auto-advance to REFLECTION if in CONSEQUENCES
    if state.current_stage == SimulationStage.CONSEQUENCES:
        state.advance_stage(SimulationStage.REFLECTION)

    if state.current_stage != SimulationStage.REFLECTION:
        raise HTTPException(400, {"error": "WRONG_STAGE", "message": "View consequences first."})

    # Check if reflection already exists in DB
    existing = await db.execute(
        select(Reflection).where(Reflection.session_id == session_id)
    )
    existing_reflection = existing.scalar_one_or_none()
    if existing_reflection:
        return {
            "preamble": existing_reflection.preamble,
            "sutra_observations": existing_reflection.sutra_observations,
            "alternative_approaches": existing_reflection.alternative_approaches,
            "further_reading": existing_reflection.further_reading,
            "cached": True,
        }

    # Build Coach prompt
    coach_prompt = ReflectionCoachAgent.build_prompt(
        scenario=state.scenario,
        decisions_made=state.decisions_made,
        npcs_consulted=state.npcs_consulted,
        references_shown=state.references_shown,
        consequence_branch=state.consequence_branch,
    )

    try:
        raw_response = await gateway.generate(
            system_prompt=coach_prompt["system_prompt"],
            user_prompt=coach_prompt["user_prompt"],
            role="coach",
        )
        reflection_data = _parse_json_response(raw_response)
    except (LLMBusyError, Exception) as e:
        logger.error("reflection_generation_failed", error=str(e)[:80])
        reflection_data = {
            "preamble": "You navigated a complex governance scenario involving multiple stakeholders and competing priorities.",
            "sutra_observations": [],
            "alternative_approaches": [],
            "further_reading": [],
        }

    # Save reflection to DB
    reflection_record = Reflection(
        id=uuid4(),
        session_id=session_id,
        preamble=reflection_data.get("preamble", ""),
        sutra_observations=reflection_data.get("sutra_observations", []),
        alternative_approaches=reflection_data.get("alternative_approaches", []),
        further_reading=reflection_data.get("further_reading", []),
    )
    db.add(reflection_record)

    # Mark session complete
    await _mark_session_complete(session_id, db)
    await _persist_state(session_id, state, db)

    return {
        **reflection_data,
        "cached": False,
    }


@router.post("/{session_id}/draft")
async def request_draft(session_id: str, req: DraftRequest, request: Request, db=Depends(get_db)):
    """
    Request drafting assistance from the Drafting Partner agent.
    Available during DECISION_MOMENTS stage.
    """
    state = await _get_or_recover_session(session_id, db)
    gateway = _get_gateway(request)

    if state.current_stage not in (SimulationStage.DECISION_MOMENTS, SimulationStage.INTERACTION):
        raise HTTPException(400, {"error": "WRONG_STAGE", "message": "Drafting is available during the scenario."})

    draft_prompt = DraftingPartnerAgent.build_prompt(
        scenario=state.scenario,
        decisions_made=state.decisions_made,
        draft_request=req.request_text,
        references_available=state.references_shown,
    )

    try:
        raw_response = await gateway.generate(
            system_prompt=draft_prompt["system_prompt"],
            user_prompt=draft_prompt["user_prompt"],
            role="drafting_partner",
        )
        draft_data = _parse_json_response(raw_response)
    except LLMBusyError:
        raise HTTPException(503, {"error": "LLM_CAPACITY_EXHAUSTED", "retry_after": 60})

    return draft_data


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str, db=Depends(get_db)):
    """Get the current state of a simulation session."""
    state = await _get_or_recover_session(session_id, db)

    return SessionStatusResponse(
        session_id=session_id,
        stage=state.current_stage.value,
        decisions_made=len(state.decisions_made),
        decisions_total=state.total_decision_moments,
        npcs_consulted=state.npcs_consulted,
        is_complete=state.current_stage == SimulationStage.REFLECTION,
    )


@router.get("/{session_id}/decision-moment")
async def get_current_decision_moment(session_id: str, db=Depends(get_db)):
    """Get the current decision moment details."""
    state = await _get_or_recover_session(session_id, db)

    moment = state.current_decision_moment
    if not moment:
        return {"complete": True, "message": "All decisions have been made."}

    # Get whisperer keywords for this moment
    whisperer_keywords = state.scenario.get("whisperer_keywords", {})
    keywords = whisperer_keywords.get(moment["id"], [])

    return {
        "complete": False,
        "decision_moment": moment,
        "whisperer_keywords": keywords,
        "decisions_remaining": state.decisions_remaining,
        "index": state.current_decision_index + 1,
        "total": state.total_decision_moments,
    }


# ============================================================
# Helper Functions
# ============================================================

def _get_session_state(session_id: str) -> SimulationState:
    """Retrieve session state from memory cache (sync, no DB recovery)."""
    state = _session_cache.get(session_id)
    if not state:
        raise HTTPException(404, {
            "error": "SESSION_NOT_FOUND",
            "message": "Session not found or expired. Start a new session.",
        })
    return state


async def _get_or_recover_session(session_id: str, db) -> SimulationState:
    """Get session from cache, or recover from DB on cache miss."""
    state = _session_cache.get(session_id)
    if state:
        return state

    # Try DB recovery (survives server restarts)
    try:
        result = await db.execute(
            select(SimulationSession).where(SimulationSession.id == session_id)
        )
        session_record = result.scalar_one_or_none()
        if not session_record:
            raise HTTPException(404, {
                "error": "SESSION_NOT_FOUND",
                "message": "Session not found or expired. Start a new session.",
            })

        scenario_result = await db.execute(
            select(Scenario).where(Scenario.id == session_record.scenario_id)
        )
        scenario_record = scenario_result.scalar_one_or_none()
        if not scenario_record:
            raise HTTPException(404, {"error": "SCENARIO_NOT_FOUND"})

        scenario_data = {
            "id": str(scenario_record.id),
            "slug": scenario_record.slug,
            "title": scenario_record.title,
            "domain": scenario_record.domain,
            "description": scenario_record.description,
            "estimated_minutes": scenario_record.estimated_minutes,
            "tier_scope": scenario_record.tier_scope,
            "setting_narrative": scenario_record.setting_narrative,
            "npcs": scenario_record.npcs,
            "decision_moments": scenario_record.decision_moments,
            "consequence_branches": scenario_record.consequence_branches,
            "whisperer_keywords": scenario_record.whisperer_keywords,
            "sutras": scenario_record.sutras,
        }

        state = SimulationState.from_db(session_record, scenario_data)
        _session_cache[session_id] = state
        logger.info("session_recovered_from_db", session_id=session_id,
                     stage=state.current_stage.value)
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("session_recovery_failed", error=str(e)[:80])
        raise HTTPException(404, {
            "error": "SESSION_NOT_FOUND",
            "message": "Session not found or expired. Start a new session.",
        })


async def _persist_state(session_id: str, state: SimulationState, db):
    """Persist simulation state to database."""
    try:
        state_dict = state.to_db_dict()
        result = await db.execute(
            select(SimulationSession).where(SimulationSession.id == session_id)
        )
        session_record = result.scalar_one_or_none()
        if session_record:
            session_record.current_stage = state_dict["current_stage"]
            session_record.conversation_history = state_dict["conversation_history"]
            session_record.adapted_narrative = state_dict["adapted_narrative"]
            await db.flush()
    except Exception as e:
        logger.warning("persist_state_failed", error=str(e)[:100], session_id=session_id)


async def _mark_session_complete(session_id: str, db):
    """Mark a session as complete in the database."""
    try:
        result = await db.execute(
            select(SimulationSession).where(SimulationSession.id == session_id)
        )
        session_record = result.scalar_one_or_none()
        if session_record:
            session_record.is_complete = True
            session_record.completed_at = datetime.now(timezone.utc)
            await db.flush()
    except Exception as e:
        logger.warning("mark_complete_failed", error=str(e)[:100])


def _parse_json_response(raw: str) -> dict:
    """
    Attempt to parse JSON from an LLM response.
    Handles markdown code blocks and malformed JSON gracefully.
    """
    text = raw.strip()

    # Strip markdown code blocks
    if "```json" in text:
        text = text.split("```json", 1)[1]
        text = text.rsplit("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1]
        text = text.rsplit("```", 1)[0]

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        # Return raw text as fallback
        logger.warning("json_parse_failed", raw_length=len(raw))
        return {"raw_response": raw}
