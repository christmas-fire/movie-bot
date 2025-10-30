import logging
from datetime import datetime

from database.init import get_pool

class User:
    def __init__(self, id: int, user_id: int, username: str, first_name: str, created_at: datetime):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.created_at = created_at


async def create_users_table():
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logging.info("Таблица 'users' успешно проверена/создана.")
        except Exception as e:
            logging.error(f"Ошибка при создании таблицы 'users': {e}")


async def create_user(user_id: int, username: str = None, first_name: str = None):
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            insert_query = """
            INSERT INTO users (user_id, username, first_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING;
            """
            await connection.execute(insert_query, user_id, username, first_name)
        except Exception as e:
            logging.error(f"Ошибка при создании пользователя {user_id}: {e}")


async def get_all_users() -> list[User]:
    pool = get_pool()
    async with pool.acquire() as connection:
        users_list = []
        try:
            select_query = "SELECT id, user_id, username, first_name, created_at FROM users ORDER BY id;"
            records = await connection.fetch(select_query)

            if not records:
                logging.info("Пользователи не найдены.")
                return []

            for row in records:
                users_list.append(User(
                    id=row['id'],
                    user_id=row['user_id'],
                    username=row['username'],
                    first_name=row['first_name'],
                    created_at=row['created_at']
                ))
            return users_list
        except Exception as e:
            logging.error(f"Ошибка при получении всех пользователей: {e}")
            return []


async def get_user_by_user_id(user_id: int) -> User | None:
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            select_query = "SELECT id, user_id, username, first_name, created_at FROM users WHERE user_id = $1;"
            record = await connection.fetchrow(select_query, user_id)

            if record:
                return User(
                    id=record['id'],
                    user_id=record['user_id'],
                    username=record['username'],
                    first_name=record['first_name'],
                    created_at=record['created_at']
                )
            else:
                logging.info(f"Пользователь с user_id {user_id} не найден.")
                return None
        except Exception as e:
            logging.error(f"Ошибка при получении пользователя '{user_id}': {e}")
            return None
        