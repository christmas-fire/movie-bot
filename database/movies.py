import logging
from datetime import datetime

from database.init import get_pool

class Movie:
    def __init__(self,
                 id: int,
                 title: str,
                 added_by: str,
                 added_at: datetime,
                 is_watched: bool = False,
                 watched_at: datetime = None,
                 rating: float = None
                ):
        self.id = id
        self.title = title
        self.added_by = added_by
        self.added_at = added_at
        self.is_watched = is_watched
        self.watched_at = watched_at
        self.rating = rating
        
        
async def create_movies_table():
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS movies (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    added_by TEXT NOT NULL,
                    added_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    is_watched BOOLEAN NOT NULL DEFAULT FALSE,
                    watched_at TIMESTAMPTZ,
                    rating REAL
                );
            """)
            logging.info("create table 'movies'")
        except Exception as e:
            logging.error(f"error create table 'movies': {e}")


async def create_movie(title: str, added_by: str) -> int | None:
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            insert_query = """
            INSERT INTO movies (title, added_by)
            VALUES ($1, $2)
            RETURNING id;
            """
            id = await connection.fetchval(insert_query, title, added_by)
            return id
        except Exception as e:
            logging.error(f"error create movie '{title}': {e}")
            return None


async def get_all_movies() -> list[Movie]:
    pool = get_pool()
    async with pool.acquire() as connection:
        movies = []
        try:
            select_query = "SELECT id, title, added_by, added_at, is_watched, watched_at, rating FROM movies ORDER BY id;"
            records = await connection.fetch(select_query)

            if not records:
                logging.info("any movies not found")
                return []

            for row in records:
                movie = Movie(
                    id=row['id'],
                    title=row['title'],
                    added_by=row['added_by'],
                    added_at=row['added_at'],
                    is_watched=row['is_watched'],
                    watched_at=row['watched_at'],
                    rating=row['rating']
                )
                movies.append(movie)
            return movies
        except Exception as e:
            logging.error(f"error get all coffee: {e}")
            return []


async def get_movies_by_user(added_by: str) -> list[Movie]:
    pool = get_pool()
    async with pool.acquire() as connection:
        movies = []
        try:
            select_query = """
            SELECT id, title, added_by, added_at, is_watched, watched_at, rating
            FROM movies
            WHERE added_by = $1
            ORDER BY id;
            """
            records = await connection.fetch(select_query, added_by)

            if not records:
                logging.info(f"any movies not found by user '{added_by}'")
                return []

            for row in records:
                movie = Movie(
                    id=row['id'],
                    title=row['title'],
                    added_by=row['added_by'],
                    added_at=row['added_at'],
                    is_watched=row['is_watched'],
                    watched_at=row['watched_at'],
                    rating=row['rating']
                )
                movies.append(movie)
            return movies
        except Exception as e:
            logging.error(f"error get all coffee: {e}")
            return []
        
        
async def get_movie_by_title(added_by: str, title: str) -> Movie | None:
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            select_query = """
            SELECT id, title, added_by, added_at, is_watched, watched_at, rating
            FROM movies
            WHERE added_by = $1 AND title = $2
            ORDER BY id;
            """
            record = await connection.fetchrow(select_query, added_by, title)
            if record:
                return Movie(
                    id=record['id'],
                    title=record['title'],
                    added_by=record['added_by'],
                    added_at=record['added_at'],
                    is_watched=record['is_watched'],
                    watched_at=record['watched_at'],
                    rating=record['rating']
                )
            else:
                logging.info(f"movie with title '{title}' not found")
                return None
        
        except Exception as e:
            logging.error(f"error get movie with title '{title}': {e}")
            return None
        
        
async def get_unwatched_movies(added_by: str) -> list[Movie]:
    pool = get_pool()
    async with pool.acquire() as connection:
        movies = []
        try:
            select_query = """
            SELECT id, title, added_by, added_at, is_watched, watched_at, rating
            FROM movies
            WHERE added_by = $1 AND is_watched = False
            ORDER BY id;
            """
            records = await connection.fetch(select_query, added_by)

            if not records:
                logging.info(f"any movies not found by user '{added_by}'")
                return []

            for row in records:
                movie = Movie(
                    id=row['id'],
                    title=row['title'],
                    added_by=row['added_by'],
                    added_at=row['added_at'],
                    is_watched=row['is_watched'],
                    watched_at=row['watched_at'],
                    rating=row['rating']
                )
                movies.append(movie)
            return movies
        except Exception as e:
            logging.error(f"error get all coffee: {e}")
            return []
        
        
async def get_watched_movies(added_by: str) -> list[Movie]:
    pool = get_pool()
    async with pool.acquire() as connection:
        movies = []
        try:
            select_query = """
            SELECT id, title, added_by, added_at, is_watched, watched_at, rating
            FROM movies
            WHERE added_by = $1 AND is_watched = True
            ORDER BY id;
            """
            records = await connection.fetch(select_query, added_by)

            if not records:
                logging.info(f"any movies not found by user '{added_by}'")
                return []

            for row in records:
                movie = Movie(
                    id=row['id'],
                    title=row['title'],
                    added_by=row['added_by'],
                    added_at=row['added_at'],
                    is_watched=row['is_watched'],
                    watched_at=row['watched_at'],
                    rating=row['rating']
                )
                movies.append(movie)
            return movies
        except Exception as e:
            logging.error(f"error get all coffee: {e}")
            return []
        

async def update_movie_as_watched(added_by: str, title: str, rating: float | None) -> bool:
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            update_query = """
            UPDATE movies
            SET 
                is_watched = TRUE,
                watched_at = CURRENT_TIMESTAMP,
                rating = $3
            WHERE 
                added_by = $1 AND title ILIKE $2 AND is_watched = FALSE
            RETURNING id;
            """
            movie_id = await connection.fetchval(update_query, added_by, title, rating)
            
            if movie_id:
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"Error updating movie '{title}' as watched: {e}")
            return False
    
    
async def update_movie_rating(added_by: str, title: str, rating: float) -> bool:
    pool = get_pool()
    async with pool.acquire() as connection:
        try:
            update_query = """
            UPDATE movies
            SET 
                rating = $3
            WHERE 
                added_by = $1 AND title ILIKE $2
            RETURNING id;
            """
            movie_id = await connection.fetchval(update_query, added_by, title, rating)
            
            if movie_id:
                return True
            else:
                return False
                
        except Exception as e:
            logging.error(f"Error updating movie '{title}' rating: {e}")
            return False
        