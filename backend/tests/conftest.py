# backend/tests/conftest.py
"""
Pytest fixtures for the Lender Matching Platform.

This file ensures Python can find both 'main.py' (in root) and the 'app' package.
"""

import sys
from pathlib import Path

# Add backend root to Python path so 'main' and 'app' can be imported
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

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
    """Provide a database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()