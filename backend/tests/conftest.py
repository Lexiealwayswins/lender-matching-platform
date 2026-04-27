# backend/tests/conftest.py
"""
Pytest fixtures for the Lender Matching Platform.
"""

import sys
from pathlib import Path

# Add backend root to Python path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

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
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()