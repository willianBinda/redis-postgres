from db.base import pg_conn

def buscarDadosTodosCliente():
    with pg_conn.cursor() as cursor:
        cursor.execute("SELECT * FROM clientes")
        dados = cursor.fetchall()
    return dados