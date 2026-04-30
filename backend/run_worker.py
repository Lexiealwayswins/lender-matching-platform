# run_worker.py
import os
from dotenv import load_dotenv
from hatchet_sdk import Hatchet

load_dotenv()

from app.workers.hatchet_worker import crud_workflow
from app.workflows.underwriting_workflow import underwriting_workflow

def main():
    print("\n" + "="*50)
    print("🔧 Initializing Hatchet Worker...")
    
    # initialize client
    hatchet = Hatchet(debug=True)
    
    worker = hatchet.worker("lender-match-worker")
    
    # register workflow
    print("📦 Registering decoupled workflows...")
    worker.register_workflow(crud_workflow)
    worker.register_workflow(underwriting_workflow)
    
    # start listen
    print("✅ All workflows registered successfully.")
    print("👷 Hatchet Worker is now RUNNING and listening for background tasks!")
    print("Press Ctrl+C to stop.")
    print("="*50 + "\n")
    
    worker.start()

if __name__ == "__main__":
    main()