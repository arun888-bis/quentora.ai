
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env for local development.
# Vercel environment variables should be configured in Vercel settings.
load_dotenv(Path(__file__).resolve().parent / ".env", override=False)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is missing. Configure it in your .env file "
        "locally or in Vercel Environment Variables."
    )

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dbname": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "sslmode": os.getenv("DB_SSLMODE", "require"),
}

required_db_vars = ["host", "user", "password", "dbname"]

missing_db_vars = [
    key for key in required_db_vars if not DB_CONFIG[key]
]

if missing_db_vars:
    raise RuntimeError(
        "Missing database configuration: "
        + ", ".join(missing_db_vars)
    )
