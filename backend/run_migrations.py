import os
import sys
import logging
from dotenv import load_dotenv

# Ensure we can import from backend dir
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrations_runner")

def main():
    load_dotenv()
    db_path = os.getenv("DB_PATH", "prescriptions.db")
    # Resolve relative path to backend directory
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
    
    logger.info(f"Running migration for DB at {db_path}...")
    init_db(db_path)
    logger.info("Migrations completed successfully.")

if __name__ == "__main__":
    main()
