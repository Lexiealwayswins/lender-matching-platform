# Lender Matching Platform

A robust loan underwriting and intelligent lender matching system that evaluates business equipment finance applications against multiple lenders' credit policies. The system provides a complete administrative suite for managing lenders and their complex credit rules alongside the core matching engine.

## Features

- **Extensible Policy Engine**: Comprehensive CRUD operations for Lenders, Programs, and Rules, allowing administrators to update credit policies in real-time.
- **Asynchronous CRUD via Hatchet**: Heavy deletion operations (Lenders/Programs/Applications) are handled asynchronously through Hatchet workflows to ensure system responsiveness.
- **Extensible Rule Engine**: Supports diverse criteria (FICO, Industry, State, etc.) using a flexible rule_type + operator + value design.
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

## Project Structure

```bash
lender-matching-platform/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/endpoints/            # API Routers (loans.py, policies.py)
│   │   ├── core/                     # Configuration (config.py)
│   │   ├── database.py               # Database session management
│   │   ├── models/                   # SQLAlchemy Models
│   │   │   ├── base.py               # Base class + RuleType Enum
│   │   │   ├── lender.py             # Lender, LenderProgram, LenderProgramRule
│   │   │   ├── application.py        # LoanApplication
│   │   │   └── match.py              # ApplicationMatch + MatchRuleResult
│   │   ├── schemas/                  # Pydantic models for API
│   │   ├── services/                 # Business Logic
│   │   │   ├── rule_evaluator.py     # Single rule evaluation
│   │   │   └── matching_service.py   # Main matching engine
│   │   └── workflows/                # Hatchet Workflow
│   ├── migrations/                   # Alembic database migrations
│   ├── scripts/
│   │   └── seed_lenders.py           # Seed data from 5 PDFs
│   ├── tests/                        # pytest test files
│   ├── .env.example
│   ├── alembic.ini
│   ├── main.py
│   └── requirements.txt
│
├── frontend/                         # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── RuleResultTable.tsx   # Detailed rule matching table
│   │   ├── pages/
│   │   │   ├── LoanApplicationForm.tsx
│   │   │   ├── ApplicationResults.tsx # Matching results with detailed reasons
│   │   │   └── LenderPolicies.tsx    # View and manage lender rules
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript interfaces
│   │   ├── utils/
│   │   │   └── api.ts                # API client
│   │   ├── App.tsx                   # Routing configuration
│   │   └── main.tsx
│   ├── .env
│   ├── index.html
│   ├── package.json
│   └── tailwind.config.js
│
├── docker-compose.yml                # PostgreSQL container
├── start.sh                          # Start both frontend and backend
├── README.md
├── DECISIONS.md
└── .gitignore
```


## Local Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/Lexiealwayswins/lender-matching-platform.git
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

# run hatchet workflow
python run_worker.py

# run backend services
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install

# run frontend services
npm run dev
```

### 4. or Skip 2 & 3 and Just Run Start Services

```bash
# From project root
./start.sh
```

Backend will run on: **http://localhost:8000**  
Frontend will run on: **http://localhost:5173**


## 🚀 API Documentation & Testing (Swagger UI)

- Interactive Swagger UI: http://localhost:8000/docs
- Key Endpoints:

### 1. Loan Applications
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/application/` | Submit a new loan application. |
| **GET** | `/application/` | List all submitted applications. |
| **PUT** | `/application/{id}` | Update application details. |
| **DELETE** | `/application/{id}` | Async deletion of application and matches via Hatchet. |

### 2. Policy Management (Lenders, Programs, & Rules)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/lenders/` | Retrieve all lenders with nested programs and rules. |
| **POST** | `/lenders/` | Create a new lending institution. |
| **POST** | `/programs/` | Create a specific lending program (e.g., "Tier 1"). |
| **PUT** | `/rules/{rule_id}` | Update specific credit criteria (e.g., change Min FICO). |
| **DELETE** | `/lenders/{id}` | Cascade delete lender, programs, and rules via Hatchet. |

### 3. Underwriting & Matching
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/match/{id}/underwrite` | Trigger the Hatchet asynchronous matching pipeline. |
| **GET** | `/match/{id}/matches` | Retrieve final results with injected Lender/Program names. |


## Architecture Overview

- **`app/models/`** — SQLAlchemy models with extensible rule-based design (`LenderProgramRule`)
- **`app/services/`** — `RuleEvaluator` and `MatchingService` (core matching logic)
- **`app/workflows/`** — Hatchet workflow with validation, feature derivation, parallel matching and retry logic
- **`app/api/endpoints/`** — RESTful routers for loans and policies
- **Frontend** — Clean component-based UI with detailed rule result tables

The system is designed for high extensibility — new lender PDFs can be supported by simply adding rules to the database.
