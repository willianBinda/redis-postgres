"""
test_cache_updater.py
Testes automatizados para o módulo de sincronização de cache com PostgreSQL e Redis.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import cache_updater

# Dados de exemplo retornados pela consulta de voos ativos
voos_ativos_exemplo = [
    {
        "id": 1,
        "codigo_voo": "LA3450",
        "origem": "GRU",
        "destino": "GIG",
        "saida_prevista": datetime(2026, 5, 11, 8, 0, 0),
        "chegada_prevista": datetime(2026, 5, 11, 9, 0, 0),
        "status": "EM_CURSO",
        "percentual_concluido": 32.5,
        "chegada_prevista_atualizada": datetime(2026, 5, 11, 9, 10, 0),
        "latitude": -23.4356,
        "longitude": -46.4731
    },
    {
        "id": 2,
        "codigo_voo": "G31201",
        "origem": "BSB",
        "destino": "SSA",
        "saida_prevista": datetime(2026, 5, 11, 7, 30, 0),
        "chegada_prevista": datetime(2026, 5, 11, 10, 0, 0),
        "status": "EM_CURSO",
        "percentual_concluido": 60.0,
        "chegada_prevista_atualizada": datetime(2026, 5, 11, 9, 55, 0),
        "latitude": -15.7801,
        "longitude": -47.9292
    }
]

@pytest.fixture
def cliente_redis_mock():
    """Retorna um mock do cliente Redis."""
    return MagicMock()

class TestbuscarVoosAtivos:
    """Testes para a função buscar_voos_ativos."""

    @patch("cache_updater.psycopg2.connect")
    def test_consulta_retorna_lista(self, mock_connect):
        """Deve retornar uma lista com os voos ativos."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchall.return_value = voos_ativos_exemplo
        conn.cursor.return_value = cursor
        mock_connect.return_value = conn

        resultado = cache_updater.buscar_voos_ativos(conn)
        assert len(resultado) == 2
        assert resultado[0]["codigo_voo"] == "LA3450"
        assert resultado[1]["percentual_concluido"] == 60.0

    @patch("cache_updater.psycopg2.connect")
    def test_consulta_sem_voos_ativos(self, mock_connect):
        """Deve retornar uma lista vazia quando não houver voos em curso."""
        conn = MagicMock()
        cursor = MagicMock()
        cursor.__enter__.return_value = cursor
        cursor.fetchall.return_value = []
        conn.cursor.return_value = cursor
        mock_connect.return_value = conn

        resultado = cache_updater.buscar_voos_ativos(conn)
        assert resultado == []

class TestatualizarCacheRedis:
    """Testes para a função atualizar_cache_redis."""

    def test_atualiza_lista_e_adiciona_voos(self, cliente_redis_mock):
        """Deve limpar a lista existente e adicionar os IDs dos voos."""
        cache_updater.atualizar_cache_redis(voos_ativos_exemplo, cliente_redis_mock)

        cliente_redis_mock.delete.assert_called_once_with("voos_em_curso")
        assert cliente_redis_mock.rpush.call_count == 2
        cliente_redis_mock.rpush.assert_any_call("voos_em_curso", 1)
        cliente_redis_mock.rpush.assert_any_call("voos_em_curso", 2)

    def test_cria_hash_para_cada_voo(self, cliente_redis_mock):
        """Deve criar um hash Redis para cada voo ativo."""
        cache_updater.atualizar_cache_redis(voos_ativos_exemplo, cliente_redis_mock)

        chaves_esperadas = [
            f"{cache_updater.REDIS_HASH_PREFIX}1",
            f"{cache_updater.REDIS_HASH_PREFIX}2"
        ]
        for chave in chaves_esperadas:
            cliente_redis_mock.hset.assert_any_call(chave, mapping=...)

    def test_conteudo_do_hash(self, cliente_redis_mock):
        """O hash do primeiro voo deve conter os campos corretos."""
        cache_updater.atualizar_cache_redis(voos_ativos_exemplo, cliente_redis_mock)

        # Acessa os argumentos da primeira chamada ao hset
        chamada = cliente_redis_mock.hset.call_args_list[0]
        chave = chamada[0][0]
        mapeamento = chamada[1]["mapping"]
        assert chave == "voo:1"
        assert mapeamento["codigo_voo"] == "LA3450"
        assert mapeamento["origem"] == "GRU"
        assert mapeamento["percentual_concluido"] == "32.5"
        assert mapeamento["latitude"] == "-23.4356"
        assert "ultima_atualizacao" in mapeamento

    def test_armazena_metadados(self, cliente_redis_mock):
        """Deve gravar os metadados do cache."""
        cache_updater.atualizar_cache_redis(voos_ativos_exemplo, cliente_redis_mock)
        cliente_redis_mock.hset.assert_any_call("cache_metadados", mapping={
            "quantidade_voos": 2,
            "atualizado_em": ...  # aceita qualquer valor de string
        })

    def test_metadados_lista_vazia(self, cliente_redis_mock):
        """Quando não há voos ativos, os metadados devem indicar zero."""
        cache_updater.atualizar_cache_redis([], cliente_redis_mock)
        cliente_redis_mock.hset.assert_any_call("cache_metadados", mapping={
            "quantidade_voos": 0,
            "atualizado_em": ...
        })