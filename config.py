
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Load .env for local development.
# On Vercel, configure these values in Project Settings > Environment Variables.
load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Configure it locally in .env "
        "or in Vercel Environment Variables."
    )

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dbname": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "sslmode": os.getenv("DB_SSLMODE", "require"),
}

# Validate required database environment variables.
required_db_vars = ["host", "user", "password", "dbname"]

missing_db_vars = [
    key for key in required_db_vars if not DB_CONFIG[key]
]

if missing_db_vars:
    raise RuntimeError(
        "Missing database configuration: "
        + ", ".join(missing_db_vars)
    )


def get_db_connection():
    """Create a PostgreSQL connection using dictionary-style rows."""
    print("DEBUG - App file:", __file__)
    print("DEBUG - DB username:", DB_CONFIG.get("user"))
    print("DEBUG - Password configured:", bool(DB_CONFIG.get("password")))
    print("DEBUG - DB host:", DB_CONFIG.get("host"))
    print("DEBUG - DB name:", DB_CONFIG.get("dbname"))

    return psycopg.connect(
        **DB_CONFIG,
        row_factory=dict_row
    )
