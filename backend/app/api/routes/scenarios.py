"""
GovernAI Studio — Scenarios API Route (Production)
====================================================
Real DB-backed scenario CRUD operations.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Scenario

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("")
async def list_scenarios(
    domain: Optional[str] = None,
    page: int = 1,
    limit: int = 12,
    db=Depends(get_db),
):
    """
    List available scenarios from the database.
    Supports filtering by domain and pagination.
    """
    query = select(Scenario).where(Scenario.is_active == True)

    if domain:
        query = query.where(Scenario.domain == domain)

    # Get total count
    count_query = select(func.count()).select_from(Scenario).where(Scenario.is_active == True)
    if domain:
        count_query = count_query.where(Scenario.domain == domain)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Scenario.created_at.desc())

    result = await db.execute(query)
    scenarios = result.scalars().all()

    return {
        "scenarios": [
            {
                "id": str(s.id),
                "slug": s.slug,
                "title": s.title,
                "domain": s.domain,
                "description": s.description,
                "estimated_minutes": s.estimated_minutes,
                "tier_scope": s.tier_scope,
                "tags": {"sutras": s.sutras or []},
                "npc_count": len(s.npcs) if s.npcs else 0,
                "decision_count": len(s.decision_moments) if s.decision_moments else 0,
            }
            for s in scenarios
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit if total else 1,
    }


@router.get("/{scenario_slug}")
async def get_scenario(scenario_slug: str, db=Depends(get_db)):
    """Get scenario metadata by slug. No full content until session starts."""
    result = await db.execute(
        select(Scenario).where(Scenario.slug == scenario_slug, Scenario.is_active == True)
    )
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail={"error": "SCENARIO_NOT_FOUND"})

    return {
        "id": str(scenario.id),
        "slug": scenario.slug,
        "title": scenario.title,
        "domain": scenario.domain,
        "description": scenario.description,
        "estimated_minutes": scenario.estimated_minutes,
        "tier_scope": scenario.tier_scope,
        "npcs": [
            {"id": n["id"], "name": n["name"], "role": n["role"]}
            for n in (scenario.npcs or [])
        ],
        "decision_moment_count": len(scenario.decision_moments or []),
        "sutras": scenario.sutras or [],
    }
