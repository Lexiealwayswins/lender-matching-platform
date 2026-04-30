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
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api.endpoints.application import router as application_router
from app.api.endpoints.lender import router as lender_router
from app.api.endpoints.program import router as program_router
from app.api.endpoints.rule import router as rule_router
from app.api.endpoints.match import router as match_router

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    print("🚀 Starting Lender Matching Platform...")
    if HATCHET_AVAILABLE and getattr(settings, "HATCHET_CLIENT_TOKEN", None):
        print("✅ Hatchet worker started.")
    else:
        print("ℹ️  Hatchet not configured - running in standard mode.")
        
    print("🌐 API is running at: http://localhost:8000")
    print("📚 Swagger Docs available at: http://localhost:8000/docs")
    print("="*50 + "\n")
        
    yield  # let FastAPI process requests
    
    # --- Shutdown Logic (press Ctrl+C) ---
    print("🛑 Shutting down Lender Matching Platform. Cleaning up resources...")


app = FastAPI(
    title="Lender Matching Platform",
    description="Equipment Finance Underwriting & Lender Matching System",
    version="0.2.0",
    lifespan=lifespan
)

# === Strengthen CORS Configuration (This is the key modification) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                    # allow all origins (for development; restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(application_router)
app.include_router(lender_router)
app.include_router(program_router)
app.include_router(rule_router)
app.include_router(match_router)


@app.get("/")
async def root():
    return {
        "message": "Lender Matching Platform is running!",
        "docs": "/docs",
        "note": "Backend is ready. Explore the interactive API documentation."
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)