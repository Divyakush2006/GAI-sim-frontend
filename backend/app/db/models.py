"""
GovernAI Studio — SQLAlchemy ORM Models
Complete schema for officers, sessions, scenarios, decisions, and reflections.
All tables enforce data isolation — no cross-officer data access.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    DateTime, ForeignKey, Enum as SAEnum, JSON, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


# === Officers ===

class Officer(Base):
    """
    Civil servant user account.
    Privacy-first: no names stored, only email domain for auth.
    Tier is determined server-side and never exposed to the officer.
    """
    __tablename__ = "officers"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    tier = Column(String(1), nullable=True)  # 'A' or 'B', NEVER exposed
    work_location = Column(String(50), nullable=True)
    work_shape = Column(String(50), nullable=True)
    domains = Column(JSON, nullable=True)  # list[str]
    onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sessions = relationship("SimulationSession", back_populates="officer", lazy="selectin")


# === Magic Links ===

class MagicLink(Base):
    """Stores hashed magic link tokens for passwordless auth."""
    __tablename__ = "magic_links"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        Index("ix_magic_links_token_hash", "token_hash"),
    )


# === Scenarios ===

class Scenario(Base):
    """
    Pre-authored governance scenario.
    Contains the complete scenario structure: NPCs, decision moments,
    consequence branches, and Whisperer keywords.
    """
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    domain = Column(String(50), nullable=False)  # cross_cutting, sectoral, etc.
    description = Column(Text, nullable=True)
    estimated_minutes = Column(Integer, default=35)
    tier_scope = Column(String(10), default="AB")  # 'A', 'B', or 'AB'

    # Structured content (JSON)
    setting_narrative = Column(JSON, nullable=False)  # {tier_a: "...", tier_b: "..."}
    npcs = Column(JSON, nullable=False)               # list of NPC definitions
    decision_moments = Column(JSON, nullable=False)    # list of decision structures
    consequence_branches = Column(JSON, nullable=False) # branching logic
    whisperer_keywords = Column(JSON, nullable=True)   # per-decision keywords
    sutras = Column(JSON, nullable=True)               # relevant Seven Sutras

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


# === Simulation Sessions ===

class SimulationSession(Base):
    """
    A single simulation playthrough by an officer.
    Tracks state machine position, conversation history, and decisions.
    """
    __tablename__ = "simulation_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    officer_id = Column(UUID(as_uuid=False), ForeignKey("officers.id"), nullable=False, index=True)
    scenario_id = Column(UUID(as_uuid=False), ForeignKey("scenarios.id"), nullable=False)

    # State machine
    current_stage = Column(
        SAEnum("SETTING", "INTERACTION", "DECISION_MOMENTS", "CONSEQUENCES", "REFLECTION",
               name="simulation_stage"),
        default="SETTING",
    )
    is_complete = Column(Boolean, default=False)

    # Conversation context (for NPC memory)
    conversation_history = Column(JSON, default=list)

    # Adapted narrative (personalized by Director for officer's tier)
    adapted_narrative = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    officer = relationship("Officer", back_populates="sessions")
    decisions = relationship("Decision", back_populates="session", lazy="selectin")
    reflection = relationship("Reflection", back_populates="session", uselist=False, lazy="selectin")

    __table_args__ = (
        Index("ix_sessions_officer_scenario", "officer_id", "scenario_id"),
    )


# === Decisions ===

class Decision(Base):
    """
    A single decision made by the officer at a decision moment.
    Records the choice, reasoning (if freeform), and which references were shown.
    """
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("simulation_sessions.id"), nullable=False, index=True)
    decision_moment_id = Column(String(50), nullable=False)  # e.g., "dm_vendor_choice"

    # What the officer chose
    choice_type = Column(String(10), nullable=False)  # OPTION or FREEFORM
    selected_option = Column(String(50), nullable=True)  # Option ID if OPTION
    free_text = Column(Text, nullable=True)  # Officer's written response if FREEFORM

    # Context at time of decision
    whisperer_references_shown = Column(JSON, nullable=True)
    npcs_consulted = Column(JSON, nullable=True)  # list of NPC IDs consulted before deciding

    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    session = relationship("SimulationSession", back_populates="decisions")


# === Reflections ===

class Reflection(Base):
    """
    The Seven Sutras reflective debrief generated by the Coach.
    One per completed session.
    """
    __tablename__ = "reflections"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("simulation_sessions.id"), unique=True, nullable=False)

    # Coach-generated content
    preamble = Column(Text, nullable=True)
    sutra_observations = Column(JSON, nullable=True)  # list of {sutra, engagement, observation, question}
    alternative_approaches = Column(JSON, nullable=True)
    further_reading = Column(JSON, nullable=True)

    generated_at = Column(DateTime(timezone=True), default=utcnow)

    # Relationships
    session = relationship("SimulationSession", back_populates="reflection")
