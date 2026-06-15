from base import mongodb_client;
def popular_mongodb():

    db = mongodb_client["recomendacoes"]

    db.drop_collection("interesses_clientes")

    collection = db["interesses_clientes"]

    collection.insert_many([
        {
            "_id": 1,
            "cpf": "11111111111",
            "nome": "João Silva",
            "interesses": ["Futebol", "Corrida", "Tecnologia"]
        },
        {
            "_id": 2,
            "cpf": "22222222222",
            "nome": "Maria Souza",
            "interesses": ["Cinema", "Séries", "Música"]
        },
        {
            "_id": 3,
            "cpf": "33333333333",
            "nome": "Pedro Santos",
            "interesses": ["Tecnologia", "Games", "Programação"]
        },
        {
            "_id": 4,
            "cpf": "44444444444",
            "nome": "Ana Costa",
            "interesses": ["Livros", "Educação", "Filmes"]
        },
        {
            "_id": 5,
            "cpf": "55555555555",
            "nome": "Carlos Lima",
            "interesses": ["Futebol", "Música", "Viagens"]
        }
    ])

    print("MongoDB populado.")

popular_mongodb()