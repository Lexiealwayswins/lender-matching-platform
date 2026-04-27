# main.py
"""
Main FastAPI application for the Lender Matching Platform.

This file handles:
- FastAPI app initialization
- CORS middleware
- Router registration
- Graceful Hatchet integration (with fallback if no token is provided)
"""

# main.py
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from app.core.config import settings
from app.database import get_db
from app.api.endpoints.loans import router as loans_router
from app.api.endpoints.policies import router as policies_router

# Hatchet graceful import
HATCHET_AVAILABLE = False
hatchet = None
underwriting_workflow = None

try:
    from app.workflows.underwriting_workflow import underwriting_workflow as wf, hatchet as h
    hatchet = h
    underwriting_workflow = wf
    HATCHET_AVAILABLE = True
except Exception:
    pass

app = FastAPI(
    title="Lender Matching Platform",
    description="Equipment Finance Underwriting & Lender Matching System",
    version="0.2.0",
)

# === Strengthen CORS Configuration (This is the key modification) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # allow all origins (for development; restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loans_router)
app.include_router(policies_router)


@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Lender Matching Platform...")
    if HATCHET_AVAILABLE and settings.HATCHET_CLIENT_TOKEN:
        print("✅ Hatchet worker started.")
    else:
        print("ℹ️  Hatchet not configured - running in standard mode.")


@app.get("/")
async def root():
    return {
        "message": "Lender Matching Platform is running!",
        "docs": "/docs",
        "note": "Backend is ready. Try visiting /policies/lenders"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)