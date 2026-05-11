-- seed.sql
-- Dados de exemplo para teste

INSERT INTO aeroportos (codigo, nome, cidade, pais, fuso_horario) VALUES
('GRU', 'Aeroporto Internacional de Guarulhos', 'São Paulo', 'Brasil', 'America/Sao_Paulo'),
('GIG', 'Aeroporto Internacional do Galeão', 'Rio de Janeiro', 'Brasil', 'America/Sao_Paulo'),
('BSB', 'Aeroporto Internacional de Brasília', 'Brasília', 'Brasil', 'America/Sao_Paulo'),
('SSA', 'Aeroporto Internacional de Salvador', 'Salvador', 'Brasil', 'America/Bahia'),
('CGH', 'Aeroporto de Congonhas', 'São Paulo', 'Brasil', 'America/Sao_Paulo');

INSERT INTO aeronaves (matricula, modelo, capacidade, ano_fabricacao, status) VALUES
('PR-GUA', 'Boeing 737-800', 186, 2015, 'ATIVO'),
('PR-XMA', 'Airbus A320neo', 174, 2019, 'ATIVO'),
('PS-ABC', 'Embraer E195-E2', 132, 2021, 'ATIVO'),
('PT-MNB', 'ATR 72-600', 70, 2018, 'ATIVO');

INSERT INTO voos (codigo_voo, aeronave_id, aeroporto_origem_id, aeroporto_destino_id, saida_prevista, chegada_prevista, status) VALUES
('LA3450', 1, 1, 2, '2026-05-11 08:00:00', '2026-05-11 09:00:00', 'EM_CURSO'),
('G31201', 2, 3, 4, '2026-05-11 07:30:00', '2026-05-11 10:00:00', 'EM_CURSO'),
('AD4788', 3, 5, 3, '2026-05-11 09:15:00', '2026-05-11 10:45:00', 'EMBARQUE'),
('LA3550', 4, 2, 1, '2026-05-11 06:45:00', '2026-05-11 07:45:00', 'POUSADO'),
('G31234', 1, 4, 5, '2026-05-11 11:00:00', '2026-05-11 13:00:00', 'CANCELADO');

INSERT INTO historico_status_voo (voo_id, status, atualizado_em, observacao) VALUES
(1, 'EM_CURSO', '2026-05-11 08:05:00', 'Partida realizada'),
(2, 'EM_CURSO', '2026-05-11 07:32:00', 'Voo em rota'),
(3, 'EMBARQUE', '2026-05-11 08:50:00', 'Embarque iniciado'),
(4, 'POUSADO', '2026-05-11 08:00:00', 'Pouso confirmado'),
(5, 'CANCELADO', '2026-05-11 09:00:00', 'Problemas técnicos');

INSERT INTO posicao_voo (voo_id, latitude, longitude, altitude, velocidade_solo, proa, percentual_concluido, chegada_prevista_atualizada, registrado_em) VALUES
(1, -23.4356, -46.4731, 10000, 850, 45, 32.5, '2026-05-11 09:10:00', '2026-05-11 08:30:00'),
(2, -15.7801, -47.9292, 11000, 900, 70, 60.0, '2026-05-11 09:55:00', '2026-05-11 08:40:00');