
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        database=os.getenv("DB_NAME", "week4_orders"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )
    return connection
