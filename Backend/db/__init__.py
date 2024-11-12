import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    DbName = os.getenv("DATABASE_NAME")
    DbUser = os.getenv("DATABASE_USER")
    DbPassword = os.getenv("DATABASE_PASSWORD")

    return psycopg.connect(f"dbname={DbName} user={DbUser} password={DbPassword} host=localhost")