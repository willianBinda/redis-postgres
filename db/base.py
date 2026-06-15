import redis
import psycopg2
from pymongo import MongoClient
from neo4j import GraphDatabase


# Redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=1,
    decode_responses=True
)

# PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="postgres",
    port=5432
)

# MongoDB
mongodb_client = MongoClient(
    "mongodb://root:root@localhost:27017/"
)

mongo_db = mongodb_client["recomendacoes"]
mongo_collection = mongo_db["interesses_clientes"]

# Neo4j
neo4j_driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "senha123")
)

# print("Conexão com Redis OK")
# print("Conexão com PostgreSQL OK")
# print("Conexão com MongoDB OK")
# print("Conexão com Neo4j OK")