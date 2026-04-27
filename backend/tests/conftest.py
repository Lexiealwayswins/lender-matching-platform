# backend/tests/conftest.py
"""
Pytest fixtures for the Lender Matching Platform tests.
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import SessionLocal


@pytest.fixture(scope="function")
def client():
    """Create a test client for FastAPI."""
    return TestClient(app)


@pytest.fixture(scope="function")
def db():
    """Provide database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()