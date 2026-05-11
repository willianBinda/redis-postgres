# from fastapi import FastAPI
from db.redis import redis_client
from db.postgres import pg_conn

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message": "API rodando"}

# @app.get("/teste")
# def teste():
#     redis_client.set("hello", "world", ex=60)
#     value = redis_client.get("hello")

#     cursor = pg_conn.cursor()
#     cursor.execute("SELECT NOW()")
#     now = cursor.fetchone()

#     return {
#         "redis": value,
#         "postgres_time": now
#     }

