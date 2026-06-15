from base import pg_conn;

def popular_postgres():
    cursor = pg_conn.cursor()

    cursor.execute("""
        DROP TABLE IF EXISTS Compras;
        DROP TABLE IF EXISTS Produtos;
        DROP TABLE IF EXISTS Clientes;
    """)

    cursor.execute("""
        CREATE TABLE Clientes (
            id INT PRIMARY KEY,
            cpf CHAR(11) UNIQUE,
            nome VARCHAR(100),
            endereco VARCHAR(200),
            cidade VARCHAR(100),
            uf CHAR(2),
            email VARCHAR(100)
        );
    """)

    cursor.execute("""
        CREATE TABLE Produtos (
            id INT PRIMARY KEY,
            produto VARCHAR(100),
            valor DECIMAL(10,2),
            quantidade INT,
            tipo VARCHAR(50)
        );
    """)

    cursor.execute("""
        CREATE TABLE Compras (
            id INT PRIMARY KEY,
            id_produto INT,
            data DATE,
            id_cliente INT,
            FOREIGN KEY (id_produto) REFERENCES Produtos(id),
            FOREIGN KEY (id_cliente) REFERENCES Clientes(id)
        );
    """)

    clientes = [
        (1,'11111111111','João Silva','Rua A, 100','Chapecó','SC','joao@gmail.com'),
        (2,'22222222222','Maria Souza','Rua B, 200','Xaxim','SC','maria@gmail.com'),
        (3,'33333333333','Pedro Santos','Rua C, 300','Concórdia','SC','pedro@gmail.com'),
        (4,'44444444444','Ana Costa','Rua D, 400','Chapecó','SC','ana@gmail.com'),
        (5,'55555555555','Carlos Lima','Rua E, 500','Xanxerê','SC','carlos@gmail.com')
    ]

    cursor.executemany(
        "INSERT INTO Clientes VALUES (%s,%s,%s,%s,%s,%s,%s)",
        clientes
    )

    produtos = [
        (1,'Bola de Futebol',120.00,50,'Esportes'),
        (2,'Notebook Gamer',5500.00,10,'Tecnologia'),
        (3,'Violão',850.00,15,'Música'),
        (4,'Livro Python',90.00,100,'Livros'),
        (5,'Smart TV 50"',2800.00,20,'Eletrônicos')
    ]

    cursor.executemany(
        "INSERT INTO Produtos VALUES (%s,%s,%s,%s,%s)",
        produtos
    )

    compras = [
        (1,1,'2025-06-01',1),
        (2,2,'2025-06-02',2),
        (3,3,'2025-06-03',3),
        (4,4,'2025-06-04',1),
        (5,5,'2025-06-05',4),
        (6,1,'2025-06-06',5),
        (7,3,'2025-06-07',2)
    ]

    cursor.executemany(
        "INSERT INTO Compras VALUES (%s,%s,%s,%s)",
        compras
    )

    pg_conn.commit()
    cursor.close()

    print("PostgreSQL populado.")

popular_postgres()