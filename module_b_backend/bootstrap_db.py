from app.core.database import ensure_database_ready, DB_PATH


if __name__ == "__main__":
    ensure_database_ready()
    print(f"Database ready at: {DB_PATH}")
