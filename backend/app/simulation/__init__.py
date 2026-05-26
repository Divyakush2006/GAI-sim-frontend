"""
GovernAI Studio — Simulation State Machine
============================================
Enforces the simulation lifecycle and tracks progress.

Stages:
  SETTING → INTERACTION → DECISION_MOMENTS → CONSEQUENCES → REFLECTION

Rules:
  - SETTING: Read-only. Officer absorbs the narrative.
  - INTERACTION: Officer talks to NPCs. Must meet minimum required interactions.
  - DECISION_MOMENTS: Officer makes choices at each decision point.
  - CONSEQUENCES: System shows consequences based on decisions.
  - REFLECTION: Coach generates Seven Sutras debrief.
"""
from enum import Enum
from typing import Optional
import structlog

logger = structlog.get_logger()


class SimulationStage(str, Enum):
    SETTING = "SETTING"
    INTERACTION = "INTERACTION"
    DECISION_MOMENTS = "DECISION_MOMENTS"
    CONSEQUENCES = "CONSEQUENCES"
    REFLECTION = "REFLECTION"


# Valid transitions
STAGE_TRANSITIONS = {
    SimulationStage.SETTING: [SimulationStage.INTERACTION],
    SimulationStage.INTERACTION: [
        SimulationStage.INTERACTION,      # Stay (more NPC chats)
        SimulationStage.DECISION_MOMENTS,  # Advance
    ],
    SimulationStage.DECISION_MOMENTS: [
        SimulationStage.DECISION_MOMENTS,  # More decisions
        SimulationStage.CONSEQUENCES,      # All decisions done
    ],
    SimulationStage.CONSEQUENCES: [SimulationStage.REFLECTION],
    SimulationStage.REFLECTION: [],  # Terminal
}


class SimulationState:
    """
    Tracks the full state of a simulation session.
    Used in-memory during the session, persisted to DB at checkpoints.
    """

    def __init__(
        self,
        session_id: str,
        scenario: dict,
        officer_tier: str,
        officer_id: str,
    ):
        self.session_id = session_id
        self.scenario = scenario
        self.officer_tier = officer_tier
        self.officer_id = officer_id
        self.current_stage = SimulationStage.SETTING
        self.adapted_narrative: Optional[str] = None

        # NPC tracking
        self.npc_interactions: dict[str, int] = {}  # npc_id → interaction count
        self.conversation_histories: dict[str, list[dict]] = {}  # npc_id → messages

        # Decision tracking
        self.decisions_made: list[dict] = []
        self.current_decision_index: int = 0

        # Consequence tracking
        self.consequence_branch: Optional[str] = None
        self.consequence_artifacts: list[dict] = []

        # Whisperer tracking
        self.references_shown: list[str] = []

    @property
    def total_decision_moments(self) -> int:
        return len(self.scenario.get("decision_moments", []))

    @property
    def decisions_remaining(self) -> int:
        return self.total_decision_moments - len(self.decisions_made)

    @property
    def current_decision_moment(self) -> Optional[dict]:
        moments = self.scenario.get("decision_moments", [])
        if self.current_decision_index < len(moments):
            return moments[self.current_decision_index]
        return None

    @property
    def required_interactions_met(self) -> bool:
        """Check if all required NPC interactions have been met."""
        for npc in self.scenario.get("npcs", []):
            required = npc.get("required_interactions", 0)
            actual = self.npc_interactions.get(npc["id"], 0)
            if actual < required:
                return False
        return True

    @property
    def npcs_consulted(self) -> list[str]:
        """List of NPC names that were consulted."""
        npc_map = {n["id"]: n["name"] for n in self.scenario.get("npcs", [])}
        return [npc_map[nid] for nid in self.npc_interactions if nid in npc_map]

    def can_transition(self, target: SimulationStage) -> bool:
        """Check if a transition to the target stage is valid."""
        allowed = STAGE_TRANSITIONS.get(self.current_stage, [])
        return target in allowed

    def advance_stage(self, target: SimulationStage) -> bool:
        """Attempt to advance to the target stage."""
        if not self.can_transition(target):
            logger.warning(
                "invalid_stage_transition",
                current=self.current_stage,
                target=target,
                session_id=self.session_id,
            )
            return False
        self.current_stage = target
        logger.info(
            "stage_transition",
            new_stage=target,
            session_id=self.session_id,
        )
        return True

    def record_npc_interaction(self, npc_id: str, officer_msg: str, npc_response: str):
        """Record an NPC interaction."""
        self.npc_interactions[npc_id] = self.npc_interactions.get(npc_id, 0) + 1

        if npc_id not in self.conversation_histories:
            self.conversation_histories[npc_id] = []

        self.conversation_histories[npc_id].append(
            {"role": "user", "content": officer_msg}
        )
        self.conversation_histories[npc_id].append(
            {"role": "assistant", "content": npc_response}
        )

    def record_decision(self, decision_moment_id: str, choice_type: str,
                        selected_option: str = None, free_text: str = None):
        """Record a decision and advance the decision index."""
        self.decisions_made.append({
            "decision_moment_id": decision_moment_id,
            "choice_type": choice_type,
            "selected_option": selected_option,
            "free_text": free_text,
        })
        self.current_decision_index += 1

    def get_npc_by_id(self, npc_id: str) -> Optional[dict]:
        """Look up an NPC by ID."""
        for npc in self.scenario.get("npcs", []):
            if npc["id"] == npc_id:
                return npc
        return None

    def to_db_dict(self) -> dict:
        """Serialize state for DB persistence."""
        return {
            "current_stage": self.current_stage.value,
            "conversation_history": {
                "npc_interactions": self.npc_interactions,
                "conversations": self.conversation_histories,
                "decisions": self.decisions_made,
                "references_shown": self.references_shown,
            },
            "adapted_narrative": self.adapted_narrative,
        }

    @classmethod
    def from_db(cls, session_record, scenario_data: dict) -> "SimulationState":
        """Reconstruct state from DB record."""
        state = cls(
            session_id=str(session_record.id),
            scenario=scenario_data,
            officer_tier=session_record.officer_tier if hasattr(session_record, "officer_tier") else "B",
            officer_id=str(session_record.officer_id),
        )
        state.current_stage = SimulationStage(session_record.current_stage or "SETTING")
        state.adapted_narrative = session_record.adapted_narrative

        history = session_record.conversation_history or {}
        state.npc_interactions = history.get("npc_interactions", {})
        state.conversation_histories = history.get("conversations", {})
        state.decisions_made = history.get("decisions", [])
        state.references_shown = history.get("references_shown", [])
        state.current_decision_index = len(state.decisions_made)

        return state
