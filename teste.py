from db.redis import redis_client
from db.postgres import pg_conn

pessoa1 = {"nome":"Antonio","datanasc":{"dia":10, "mes":10, "ano":2000},"cidade": "Chapeco"}
pessoa2 = {"nome":"Pedro","idade":24,"cidade": "Chapeco"}
pessoa3 = {"nome":"Maria","idade":31,"cidade": "Nonoai"}

r = redis_client
r.json().set("pessoa1", "$", pessoa1)
r.json().set("pessoa2", "$", pessoa2)
r.json().set("pessoa3", "$", pessoa3)

p1 = r.json().get("pessoa1", "$")
pd1 = r.json().get("pessoa1", "$.datanasc")
ano = r.json().get("pessoa1", "$..ano")

print(p1)
print(pd1)
print(ano)


cursor = pg_conn.cursor()

cursor.execute("SELECT version();")
version = cursor.fetchone()

cursor.execute("SELECT NOW();")
now = cursor.fetchone()

print("Conexão OK")
print("Versão:", version)
print("Horário servidor:", now)

cursor.close()
