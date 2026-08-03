from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Fact
from app.schemas import StatsResponse, CategoryResponse, HealthResponse, FactResponse

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Get API statistics including total facts, categories, and facts per category.
    """
    total_facts = db.query(Fact).count()

    category_counts = db.query(
        Fact.category,
        func.count(Fact.id).label('count')
    ).group_by(Fact.category).all()

    facts_per_category = [
        CategoryResponse(category=cat, count=count)
        for cat, count in category_counts
    ]

    return StatsResponse(
        total_facts=total_facts,
        total_categories=len(facts_per_category),
        facts_per_category=facts_per_category
    )


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """
    Get all available fact categories with their counts.
    """
    category_counts = db.query(
        Fact.category,
        func.count(Fact.id).label('count')
    ).group_by(Fact.category).all()

    return [
        CategoryResponse(category=cat, count=count)
        for cat, count in category_counts
    ]


@router.get("/search", response_model=list[FactResponse])
def search_facts(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """
    Search facts by their content.
    """
    facts = db.query(Fact).filter(
        Fact.content.ilike(f"%{q}%")
    ).all()

    return facts


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Check API health status.
    """
    return HealthResponse(
        status="healthy",
        message="GalaxyBrainAPI is running smoothly"
    )
