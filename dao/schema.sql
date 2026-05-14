-- =====================================================================
-- Esquema do banco de dados db_lpoo_locadora_veiculos
-- Banco: PostgreSQL
-- Para criar o banco antes:
--   CREATE DATABASE db_lpoo_locadora_veiculos;
-- Depois conecte-se nele e execute este script.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabela de veículos (já utilizada pelo projeto base)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_veiculos (
    vei_placa         VARCHAR(7)    PRIMARY KEY,
    vei_categoria     VARCHAR(20)   NOT NULL,
    vei_taxa_diaria   NUMERIC(10,2) NOT NULL CHECK (vei_taxa_diaria >= 0),
    vei_estado_atual  VARCHAR(50),
    vei_tipo          VARCHAR(20)   NOT NULL
);

-- ---------------------------------------------------------------------
-- Tabela de locações (nova - implementada nesta atividade)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tb_locacoes (
    loc_id            SERIAL        PRIMARY KEY,
    vei_placa         VARCHAR(7)    NOT NULL,
    loc_data_inicio   DATE          NOT NULL,
    loc_data_fim      DATE,
    loc_status        VARCHAR(20)   NOT NULL DEFAULT 'reservado'
                                   CHECK (loc_status IN ('reservado', 'locado', 'devolvido', 'cancelado')),
    loc_valor_total   NUMERIC(10,2),

    CONSTRAINT fk_locacao_veiculo
        FOREIGN KEY (vei_placa)
        REFERENCES tb_veiculos(vei_placa)
        ON DELETE RESTRICT,

    CONSTRAINT chk_datas_locacao
        CHECK (loc_data_fim IS NULL OR loc_data_fim >= loc_data_inicio)
);

-- Índice útil para a busca de veículos disponíveis em um intervalo
CREATE INDEX IF NOT EXISTS idx_locacoes_periodo
    ON tb_locacoes (vei_placa, loc_data_inicio, loc_data_fim, loc_status);
