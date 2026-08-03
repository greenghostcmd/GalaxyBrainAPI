from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import facts, stats
from data.seed_data import SEED_FACTS
from app.models import Fact
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GalaxyBrainAPI",
    description="A public knowledge/facts API for the Hack Club RaspAPI YSWS. Discover interesting facts across various categories!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(facts.router)
app.include_router(stats.router)


@app.on_event("startup")
def startup_event():
    """Seed the database with initial facts if empty."""
    from app.database import SessionLocal
    db = SessionLocal()

    try:

        if db.query(Fact).count() == 0:
            print("Seeding database with initial facts...")
            for fact_data in SEED_FACTS:
                fact = Fact(**fact_data)
                db.add(fact)
            db.commit()
            print(f"Seeded {len(SEED_FACTS)} facts into the database.")
        else:
            print("Database already contains facts.")
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "GalaxyBrainAPI",
        "version": "1.0.0",
        "description": "A public knowledge/facts API",
        "docs": "/docs",
        "health": "/health"
    }
