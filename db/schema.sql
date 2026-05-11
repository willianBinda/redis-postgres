-- schema.sql
-- Criação das tabelas para o sistema de status de voos

CREATE TABLE aeroportos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(100),
    pais VARCHAR(100),
    fuso_horario VARCHAR(50)
);

CREATE TABLE aeronaves (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    modelo VARCHAR(50) NOT NULL,
    capacidade INTEGER,
    ano_fabricacao INTEGER,
    status VARCHAR(20) DEFAULT 'ATIVO'
);

CREATE TABLE voos (
    id SERIAL PRIMARY KEY,
    codigo_voo VARCHAR(10) NOT NULL,
    aeronave_id INTEGER NOT NULL REFERENCES aeronaves(id),
    aeroporto_origem_id INTEGER NOT NULL REFERENCES aeroportos(id),
    aeroporto_destino_id INTEGER NOT NULL REFERENCES aeroportos(id),
    saida_prevista TIMESTAMP NOT NULL,
    chegada_prevista TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'EMBARQUE'
);

CREATE TABLE historico_status_voo (
    id SERIAL PRIMARY KEY,
    voo_id INTEGER NOT NULL REFERENCES voos(id),
    status VARCHAR(20) NOT NULL,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observacao TEXT
);

CREATE TABLE posicao_voo (
    id SERIAL PRIMARY KEY,
    voo_id INTEGER NOT NULL REFERENCES voos(id),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    velocidade_solo DOUBLE PRECISION,
    proa DOUBLE PRECISION,
    percentual_concluido DOUBLE PRECISION DEFAULT 0,
    chegada_prevista_atualizada TIMESTAMP,
    registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);