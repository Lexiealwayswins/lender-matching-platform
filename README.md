# Lender Matching Platform

A robust loan underwriting and intelligent lender matching system that evaluates business equipment finance applications against multiple lenders' credit policies. The system parses real lender guidelines from 5 PDF documents and provides transparent, detailed matching results with clear rejection reasons.

## Features

- **Extensible Policy Engine**: Rules are stored in a flexible `LenderProgramRule` table, making it easy to add, edit, or extend criteria without changing code.
- **Detailed Matching Results**: Shows exactly which rules passed or failed with human-readable explanations (e.g. "Minimum FICO required is 725, applicant has 680").
- **Fit Score Ranking**: Lenders are ranked by match quality (0-100).
- **Workflow Orchestration**: Uses Hatchet to demonstrate validation, feature derivation, parallel matching, and retry logic.
- **Modern UI**: Clean React + TypeScript frontend with detailed rule result tables.

## Tech Stack

**Backend:**
- Python 3.12 + FastAPI
- SQLAlchemy 2.0 + Alembic (migrations)
- PostgreSQL (Docker)
- Hatchet (workflow orchestration with parallelization and retries)

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- React Router

**Testing:**
- pytest + FastAPI TestClient
- Manual API testing with curl

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <your-repo>
cd lender-matching-platform
```

### 2. Backend Setup

```bash
cd backend

# Start PostgreSQL
docker compose up -d

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed lender policies from the 5 PDFs
python scripts/seed_lenders.py
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Start Services

```bash
# From project root
./start.sh
```

Backend will run on: **http://localhost:8000**  
Frontend will run on: **http://localhost:5173**

### 5. Run Tests

```bash
cd backend
pytest -v
```

## API Documentation

- Interactive Swagger UI: http://localhost:8000/docs
- Key Endpoints:

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| POST   | `/loans/`                       | Create new loan application              |
| POST   | `/loans/{id}/underwrite`        | Run traditional matching engine          |
| POST   | `/loans/{id}/underwrite-hatchet`| Run matching via Hatchet workflow        |
| GET    | `/loans/{id}/matches`           | Get detailed matching results            |
| GET    | `/policies/lenders`             | View all lender policies and rules       |

## Architecture Overview

- **`app/models/`** — SQLAlchemy models with extensible rule-based design (`LenderProgramRule`)
- **`app/services/`** — `RuleEvaluator` and `MatchingService` (core matching logic)
- **`app/workflows/`** — Hatchet workflow with validation, feature derivation, parallel matching and retry logic
- **`app/api/endpoints/`** — RESTful routers for loans and policies
- **Frontend** — Clean component-based UI with detailed rule result tables

The system is designed for high extensibility — new lender PDFs can be supported by simply adding rules to the database.

## Testing

See detailed testing commands in the **Testing** section of this README (included below).

**Manual Testing (curl):**
```bash
# Create application
curl -X POST http://localhost:8000/loans/ -H "Content-Type: application/json" -d '{"business_name":"Demo Corp","industry":"Manufacturing","state":"TX","years_in_business":6,"fico_score":750,"requested_amount":85000,"equipment_type":"Excavator"}'

# Run underwriting
curl -X POST http://localhost:8000/loans/1/underwrite

# Run with Hatchet (demonstrates parallelization + retry)
curl -X POST http://localhost:8000/loans/1/underwrite-hatchet
```

**Automated Testing:**
```bash
pytest tests/test_api.py -v
pytest tests/test_matching.py -v
pytest tests/test_matching.py -v
```
