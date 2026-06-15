from base import neo4j_driver;
def popular_neo4j():

    with neo4j_driver.session() as session:

        session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

        session.run("""
            CREATE
            (joao:Pessoa {id:1, cpf:'11111111111', nome:'João Silva'}),
            (maria:Pessoa {id:2, cpf:'22222222222', nome:'Maria Souza'}),
            (pedro:Pessoa {id:3, cpf:'33333333333', nome:'Pedro Santos'}),
            (ana:Pessoa {id:4, cpf:'44444444444', nome:'Ana Costa'}),
            (carlos:Pessoa {id:5, cpf:'55555555555', nome:'Carlos Lima'}),
            (bruno:Pessoa {id:6, cpf:'66666666666', nome:'Bruno Alves'}),
            (julia:Pessoa {id:7, cpf:'77777777777', nome:'Julia Martins'})
        """)

        session.run("""
            MATCH (joao:Pessoa {id:1}),
                  (maria:Pessoa {id:2}),
                  (pedro:Pessoa {id:3}),
                  (ana:Pessoa {id:4}),
                  (carlos:Pessoa {id:5}),
                  (bruno:Pessoa {id:6}),
                  (julia:Pessoa {id:7})

            CREATE
            (joao)-[:AMIGO_DE]->(maria),
            (maria)-[:AMIGO_DE]->(joao),

            (joao)-[:AMIGO_DE]->(pedro),
            (pedro)-[:AMIGO_DE]->(joao),

            (maria)-[:AMIGO_DE]->(ana),
            (ana)-[:AMIGO_DE]->(maria),

            (carlos)-[:AMIGO_DE]->(joao),
            (joao)-[:AMIGO_DE]->(carlos),

            (bruno)-[:AMIGO_DE]->(joao),
            (joao)-[:AMIGO_DE]->(bruno),

            (julia)-[:AMIGO_DE]->(maria),
            (maria)-[:AMIGO_DE]->(julia)
        """)

    print("Neo4j populado.")

popular_neo4j()