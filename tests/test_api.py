import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import Fact

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "GalaxyBrainAPI"
    assert data["version"] == "1.0.0"


def test_health(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_fact(client):
    """Test creating a new fact."""
    response = client.post(
        "/facts",
        json={
            "content": "Test fact for testing purposes.",
            "category": "test",
            "source": "Test source"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Test fact for testing purposes."
    assert data["category"] == "test"
    assert data["source"] == "Test source"
    assert "id" in data
    assert "created_at" in data


def test_create_fact_validation(client):
    """Test fact creation validation."""
    # Test missing content
    response = client.post(
        "/facts",
        json={
            "category": "test"
        }
    )
    assert response.status_code == 422

    # Test missing category
    response = client.post(
        "/facts",
        json={
            "content": "Test fact"
        }
    )
    assert response.status_code == 422


def test_get_facts(client, db):
    """Test getting all facts with pagination."""
    # Add test facts
    for i in range(5):
        fact = Fact(
            content=f"Test fact {i}",
            category="test",
            source=f"Source {i}"
        )
        db.add(fact)
    db.commit()

    response = client.get("/facts")
    assert response.status_code == 200
    data = response.json()
    assert "facts" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert data["page"] == 1
    assert data["limit"] == 20


def test_get_facts_with_category_filter(client, db):
    """Test getting facts filtered by category."""
    # Add test facts
    fact1 = Fact(content="Space fact", category="space", source="NASA")
    fact2 = Fact(content="Science fact", category="science", source="Nature")
    db.add(fact1)
    db.add(fact2)
    db.commit()

    response = client.get("/facts?category=space")
    assert response.status_code == 200
    data = response.json()
    assert len(data["facts"]) == 1
    assert data["facts"][0]["category"] == "space"


def test_get_facts_pagination(client, db):
    """Test pagination of facts."""
    # Add test facts
    for i in range(25):
        fact = Fact(
            content=f"Test fact {i}",
            category="test",
            source=f"Source {i}"
        )
        db.add(fact)
    db.commit()

    response = client.get("/facts?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["facts"]) == 10
    assert data["page"] == 1
    assert data["limit"] == 10

    response = client.get("/facts?page=2&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["facts"]) == 10
    assert data["page"] == 2


def test_get_fact_by_id(client, db):
    """Test getting a specific fact by ID."""
    fact = Fact(
        content="Specific test fact",
        category="test",
        source="Test source"
    )
    db.add(fact)
    db.commit()
    db.refresh(fact)

    response = client.get(f"/facts/{fact.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fact.id
    assert data["content"] == "Specific test fact"


def test_get_fact_not_found(client):
    """Test getting a non-existent fact."""
    response = client.get("/facts/99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_random_fact(client, db):
    """Test getting a random fact."""
    fact = Fact(
        content="Random test fact",
        category="test",
        source="Test source"
    )
    db.add(fact)
    db.commit()

    response = client.get("/facts/random")
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "category" in data


def test_get_random_fact_with_category(client, db):
    """Test getting a random fact filtered by category."""
    fact1 = Fact(content="Space fact", category="space", source="NASA")
    fact2 = Fact(content="Science fact", category="science", source="Nature")
    db.add(fact1)
    db.add(fact2)
    db.commit()

    response = client.get("/facts/random?category=space")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "space"


def test_get_random_fact_no_facts(client):
    """Test getting random fact when no facts exist."""
    response = client.get("/facts/random")
    assert response.status_code == 404


def test_search_facts(client, db):
    """Test searching facts."""
    fact1 = Fact(content="The Sun is a star", category="space", source="NASA")
    fact2 = Fact(content="Water is essential for life",
                 category="science", source="Nature")
    db.add(fact1)
    db.add(fact2)
    db.commit()

    response = client.get("/search?q=star")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "star" in data[0]["content"].lower()


def test_search_facts_no_results(client):
    """Test search with no results."""
    response = client.get("/search?q=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_get_categories(client, db):
    """Test getting all categories."""
    fact1 = Fact(content="Space fact", category="space", source="NASA")
    fact2 = Fact(content="Science fact", category="science", source="Nature")
    fact3 = Fact(content="Another space fact", category="space", source="ESA")
    db.add(fact1)
    db.add(fact2)
    db.add(fact3)
    db.commit()

    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    categories = {cat["category"] for cat in data}
    assert "space" in categories
    assert "science" in categories


def test_get_stats(client, db):
    """Test getting API statistics."""
    fact1 = Fact(content="Space fact", category="space", source="NASA")
    fact2 = Fact(content="Science fact", category="science", source="Nature")
    fact3 = Fact(content="Another space fact", category="space", source="ESA")
    db.add(fact1)
    db.add(fact2)
    db.add(fact3)
    db.commit()

    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_facts"] == 3
    assert data["total_categories"] == 2
    assert len(data["facts_per_category"]) == 2
