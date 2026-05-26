"""
GovernAI Studio — Onboarding & Scenarios API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db

# === Onboarding ===

onboarding_router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class OnboardingSubmission(BaseModel):
    work_location: str    # central_hq | state_secretariat | district_field | psu_regulatory
    work_shape: str       # drafting_reviewing | running_programmes | field_implementation | other
    domains: Optional[list[str]] = None


class OnboardingResponse(BaseModel):
    onboarding_complete: bool


class TierRouter:
    """
    Determines officer tier based on onboarding answers.
    
    Tier A (Policy/HQ): Drafting, reviewing, approving at central/state level.
    Tier B (Field/Implementation): Ground operations, citizen-facing work.
    
    CRITICAL: Tier labels are NEVER exposed to the officer.
    """

    @staticmethod
    def determine_tier(location: str, shape: str) -> str:
        # Tier A: HQ-based policy work
        if location in ("central_hq", "state_secretariat") and \
           shape in ("drafting_reviewing", "running_programmes"):
            return "A"
        
        # Tier B: Field implementation
        if location == "district_field" or shape == "field_implementation":
            return "B"
        
        # Edge cases for PSU/regulatory
        if location == "psu_regulatory":
            return "A" if shape == "drafting_reviewing" else "B"
        
        # Default to B (more inclusive)
        return "B"


@onboarding_router.get("/questions")
async def get_questions():
    """Return onboarding question structure. Static, cached."""
    return {
        "questions": [
            {
                "id": "work_location",
                "text": "Where do you primarily work?",
                "required": True,
                "options": [
                    {"value": "central_hq", "label": "Central Headquarters",
                     "description": "Ministry, department, or attached office"},
                    {"value": "state_secretariat", "label": "State Secretariat",
                     "description": "State government headquarters"},
                    {"value": "district_field", "label": "District or Field",
                     "description": "District, block, or frontline posting"},
                    {"value": "psu_regulatory", "label": "PSU or Regulatory Authority",
                     "description": "Public sector or regulator"},
                ],
            },
            {
                "id": "work_shape",
                "text": "What is the main shape of your work?",
                "required": True,
                "options": [
                    {"value": "drafting_reviewing", "label": "Drafting, reviewing, or approving",
                     "description": "Policy, schemes, regulations, files"},
                    {"value": "running_programmes", "label": "Running programmes or pilots",
                     "description": "Mission-mode, project management"},
                    {"value": "field_implementation", "label": "Field implementation",
                     "description": "Citizen interface, ground operations"},
                    {"value": "other", "label": "Other",
                     "description": "Doesn't fit the above"},
                ],
            },
            {
                "id": "domains",
                "text": "Which domains are most relevant?",
                "required": False,
                "options": [
                    {"value": "procurement", "label": "Procurement"},
                    {"value": "citizen_services", "label": "Citizen services"},
                    {"value": "sectoral_regulation", "label": "Sectoral regulation"},
                    {"value": "cross_sectoral", "label": "Cross-sectoral policy"},
                    {"value": "data_digital", "label": "Data & digital infrastructure"},
                    {"value": "international", "label": "International & diplomatic"},
                ],
            },
        ],
    }

from app.api.deps import get_current_officer, require_officer
from app.db.models import Officer


@onboarding_router.post("/submit", response_model=OnboardingResponse)
async def submit_onboarding(
    submission: OnboardingSubmission,
    db=Depends(get_db),
    officer: Officer = Depends(require_officer),
):
    """Submit onboarding answers. Tier is determined server-side and never exposed."""
    tier = TierRouter.determine_tier(submission.work_location, submission.work_shape)

    # Update officer record
    from sqlalchemy import select
    result = await db.execute(select(Officer).where(Officer.id == officer.id))
    record = result.scalar_one_or_none()
    if record:
        record.tier = tier
        record.work_location = submission.work_location
        record.work_shape = submission.work_shape
        record.domains = submission.domains or []
        record.onboarding_complete = True
        await db.flush()

    return OnboardingResponse(onboarding_complete=True)

