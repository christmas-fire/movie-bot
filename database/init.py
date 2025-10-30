import os
import logging
import asyncpg
from dotenv import load_dotenv

load_dotenv()

pool = None

async def create_pool():
    global pool
    if pool is not None:
        return

    try:
        pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        logging.info("Пул соединений с PostgreSQL успешно создан.")
        
    except Exception as e:
        logging.critical(f"error create postgres connection pool: {e}")
        
        
def get_pool():
    if pool is None:
        raise RuntimeError("connection pool not created yet")
    return pool
