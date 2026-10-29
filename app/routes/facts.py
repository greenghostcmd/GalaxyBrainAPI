from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import random

from app.database import get_db
from app.models import Fact
from app.schemas import FactCreate, FactResponse, FactListResponse

router = APIRouter(prefix="/facts", tags=["facts"])


@router.get("", response_model=FactListResponse)
def get_facts(
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of facts.
    Optionally filter by category.
    """
    query = db.query(Fact)

    if category:
        query = query.filter(Fact.category == category.lower())

    total = query.count()
    facts = query.offset((page - 1) * limit).limit(limit).all()

    return FactListResponse(
        facts=facts,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/random", response_model=FactResponse)
def get_random_fact(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get a random fact.
    Optionally filter by category.
    """
    query = db.query(Fact)

    if category:
        query = query.filter(Fact.category == category.lower())

    facts = query.all()

    if not facts:
        raise HTTPException(status_code=404, detail="No facts found")

    random_fact = random.choice(facts)
    return random_fact


@router.get("/{fact_id}", response_model=FactResponse)
def get_fact(fact_id: int, db: Session = Depends(get_db)):
    """
    Get a specific fact by ID.
    """
    fact = db.query(Fact).filter(Fact.id == fact_id).first()

    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")

    return fact


@router.post("", response_model=FactResponse, status_code=201)
def create_fact(fact: FactCreate, db: Session = Depends(get_db)):
    """
    Submit a new fact.
    """

    fact.category = fact.category.lower()

    new_fact = Fact(
        content=fact.content,
        category=fact.category,
        source=fact.source
    )

    db.add(new_fact)
    db.commit()
    db.refresh(new_fact)

    return new_fact
