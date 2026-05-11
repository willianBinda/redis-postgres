"""
cache_updater.py
Serviço de atualização do cache Redis com os voos em curso.
"""
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Configuração básica de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chaves utilizadas no Redis
REDIS_LIST_KEY = "voos_em_curso"
REDIS_HASH_PREFIX = "voo:"

def obter_conexao_pg():
    """Retorna uma conexão com o banco PostgreSQL."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASS
    )

def obter_cliente_redis():
    """Retorna um cliente Redis com decode de respostas."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )

def buscar_voos_ativos(conn):
    """
    Consulta os voos que estão EM_CURSO e seus dados resumidos.
    Retorna uma lista de dicionários.
    """
    consulta = """
    SELECT
        v.id,
        v.codigo_voo,
        orig.codigo AS origem,
        dest.codigo AS destino,
        v.saida_prevista,
        v.chegada_prevista,
        v.status,
        pv.percentual_concluido,
        pv.chegada_prevista_atualizada,
        pv.latitude,
        pv.longitude
    FROM voos v
    JOIN aeroportos orig ON v.aeroporto_origem_id = orig.id
    JOIN aeroportos dest ON v.aeroporto_destino_id = dest.id
    LEFT JOIN posicao_voo pv ON v.id = pv.voo_id
    WHERE v.status = 'EM_CURSO'
    ORDER BY v.id;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(consulta)
        return cur.fetchall()

def atualizar_cache_redis(dados_voos, cliente_redis):
    """
    Atualiza a lista de voos em curso e os hashes correspondentes no Redis.
    """
    # Limpa a lista existente
    cliente_redis.delete(REDIS_LIST_KEY)

    for voo in dados_voos:
        voo_id = voo["id"]
        # Adiciona o ID do voo à lista de em curso
        cliente_redis.rpush(REDIS_LIST_KEY, voo_id)

        # Cria um hash com os dados resumidos do voo
        chave = f"{REDIS_HASH_PREFIX}{voo_id}"
        mapeamento = {
            "codigo_voo": voo["codigo_voo"],
            "origem": voo["origem"],
            "destino": voo["destino"],
            "saida_prevista": voo["saida_prevista"].isoformat()
                if isinstance(voo["saida_prevista"], datetime)
                else str(voo["saida_prevista"]),
            "chegada_prevista": voo["chegada_prevista"].isoformat()
                if isinstance(voo["chegada_prevista"], datetime)
                else str(voo["chegada_prevista"]),
            "status": voo["status"],
            "percentual_concluido": str(voo["percentual_concluido"])
                if voo["percentual_concluido"] is not None else "",
            "chegada_prevista_atualizada": voo["chegada_prevista_atualizada"].isoformat()
                if isinstance(voo.get("chegada_prevista_atualizada"), datetime)
                else str(voo.get("chegada_prevista_atualizada", "")),
            "latitude": str(voo["latitude"]) if voo["latitude"] is not None else "",
            "longitude": str(voo["longitude"]) if voo["longitude"] is not None else "",
            "ultima_atualizacao": datetime.utcnow().isoformat()
        }
        cliente_redis.hset(chave, mapping=mapeamento)

    # Armazena metadados sobre o cache
    cliente_redis.hset("cache_metadados", mapping={
        "quantidade_voos": len(dados_voos),
        "atualizado_em": datetime.utcnow().isoformat()
    })

    logger.info(f"Cache atualizado com {len(dados_voos)} voos em curso.")

def main():
    """Função principal: conecta ao PostgreSQL, busca voos ativos e atualiza o Redis."""
    try:
        pg_conn = obter_conexao_pg()
        voos_ativos = buscar_voos_ativos(pg_conn)
        pg_conn.close()

        redis_client = obter_cliente_redis()
        atualizar_cache_redis(voos_ativos, redis_client)
    except Exception as erro:
        logger.error(f"Erro na atualização do cache: {erro}", exc_info=True)

if __name__ == "__main__":
    main()