import subprocess
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ("docker", "compose", "-f", "infra/docker-compose.yml")
PSQL = (
    *COMPOSE,
    "exec",
    "-T",
    "postgres",
    "psql",
    "-v",
    "ON_ERROR_STOP=1",
    "-U",
    "healthintel",
    "-d",
    "healthintel",
)


def _psql(sql: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        (*PSQL, "-X", "-q", "-t", "-A", "-c", sql),
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


@pytest.fixture(scope="module", autouse=True)
def aplicar_bootstrap_particionamento() -> None:
    subprocess.run(
        PSQL,
        cwd=ROOT,
        check=True,
        text=True,
        input=(ROOT / "infra/postgres/init/030_fase7_particionamento_anual.sql").read_text(),
        capture_output=True,
    )


@pytest.fixture()
def tabela_teste() -> tuple[str, str]:
    schema = "teste_particionamento_anual"
    tabela = f"sib_teste_{uuid.uuid4().hex[:10]}"
    _psql(f"create schema if not exists {schema};")
    _psql(
        f"create table {schema}.{tabela} "
        "(competencia integer not null) partition by range (competencia);"
    )
    yield schema, tabela
    _psql(f"drop table if exists {schema}.{tabela} cascade;")
    _psql(f"drop table if exists {schema}.{tabela}_2032 cascade;")


def test_calcular_janela_2026_04_28() -> None:
    resultado = _psql(
        "select ano_inicial, ano_final, ano_preparado, "
        "competencia_minima, competencia_maxima_exclusiva "
        "from plataforma.calcular_janela_carga_anual(2, date '2026-04-28');"
    )

    assert resultado.stdout.strip() == "2025|2026|2027|202501|202701"


def test_calcular_janela_2027_01_02() -> None:
    resultado = _psql(
        "select competencia_minima, competencia_maxima_exclusiva "
        "from plataforma.calcular_janela_carga_anual(2, date '2027-01-02');"
    )

    assert resultado.stdout.strip() == "202601|202801"


def test_calcular_janela_anos_carga_3() -> None:
    resultado = _psql(
        "select ano_inicial, ano_final, ano_preparado, "
        "competencia_minima, competencia_maxima_exclusiva "
        "from plataforma.calcular_janela_carga_anual(3, date '2026-04-28');"
    )

    assert resultado.stdout.strip() == "2024|2026|2027|202401|202701"


def test_calcular_janela_anos_carga_invalido() -> None:
    resultado = _psql(
        "select * from plataforma.calcular_janela_carga_anual(0, date '2026-04-28');",
        check=False,
    )

    assert resultado.returncode != 0
    assert "p_anos_carga deve ser maior ou igual a 1" in resultado.stderr


def test_criar_particao_idempotente(tabela_teste: tuple[str, str]) -> None:
    schema, tabela = tabela_teste

    _psql(f"select plataforma.criar_particao_anual_competencia('{schema}', '{tabela}', 2031);")
    _psql(f"select plataforma.criar_particao_anual_competencia('{schema}', '{tabela}', 2031);")
    particoes = _psql(
        "select count(*) "
        "from pg_inherits "
        f"where inhparent = '{schema}.{tabela}'::regclass "
        f"and inhrelid = '{schema}.{tabela}_2031'::regclass;"
    )
    log_reaproveitada = _psql(
        "select count(*) "
        "from plataforma.retencao_particao_log "
        f"where schema_alvo = '{schema}' "
        f"and tabela_alvo = '{tabela}' "
        "and acao = 'reaproveitada';"
    )

    assert particoes.stdout.strip() == "1"
    assert int(log_reaproveitada.stdout.strip()) >= 1


def test_particao_existente_nao_anexada_aborta(tabela_teste: tuple[str, str]) -> None:
    schema, tabela = tabela_teste
    _psql(f"create table {schema}.{tabela}_2032 (competencia integer not null);")

    resultado = _psql(
        f"select plataforma.criar_particao_anual_competencia('{schema}', '{tabela}', 2032);",
        check=False,
    )

    assert resultado.returncode != 0
    assert "ja existe mas nao esta anexada" in resultado.stderr


def test_preparar_particoes_idempotente(tabela_teste: tuple[str, str]) -> None:
    schema, tabela = tabela_teste

    _psql(f"select plataforma.preparar_particoes_janela_atual('{schema}', '{tabela}', 2);")
    _psql(f"select plataforma.preparar_particoes_janela_atual('{schema}', '{tabela}', 2);")
    resultado = _psql(
        "select count(*) "
        "from pg_inherits "
        f"where inhparent = '{schema}.{tabela}'::regclass;"
    )

    assert resultado.stdout.strip() == "3"


def test_retencao_particao_log_criada(tabela_teste: tuple[str, str]) -> None:
    schema, tabela = tabela_teste

    _psql(f"select plataforma.criar_particao_anual_competencia('{schema}', '{tabela}', 2033);")
    resultado = _psql(
        "select count(*) "
        "from plataforma.retencao_particao_log "
        f"where schema_alvo = '{schema}' "
        f"and tabela_alvo = '{tabela}' "
        "and acao = 'criada';"
    )

    assert int(resultado.stdout.strip()) >= 1


def test_retencao_particao_log_reaproveitada(tabela_teste: tuple[str, str]) -> None:
    schema, tabela = tabela_teste

    _psql(f"select plataforma.criar_particao_anual_competencia('{schema}', '{tabela}', 2034);")
    _psql(f"select plataforma.criar_particao_anual_competencia('{schema}', '{tabela}', 2034);")
    resultado = _psql(
        "select count(*) "
        "from plataforma.retencao_particao_log "
        f"where schema_alvo = '{schema}' "
        f"and tabela_alvo = '{tabela}' "
        "and acao = 'reaproveitada';"
    )

    assert int(resultado.stdout.strip()) >= 1


def test_default_recebeu_linha() -> None:
    resultado = _psql(
        "begin; "
        "insert into bruto_ans.sib_beneficiario_operadora ("
        "competencia, registro_ans, beneficiario_medico, beneficiario_odonto, "
        "beneficiario_total, _arquivo_origem, _lote_id, _layout_id, "
        "_layout_versao_id, _hash_arquivo, _hash_estrutura, _status_parse"
        ") values (203801, '999999', 1, 0, 1, 'teste.csv', "
        "'00000000-0000-0000-0000-000000000001', 'layout_teste', "
        "'layout_teste:v1', 'sha256:arquivo', 'sha256:estrutura', 'ok'); "
        "select count(*) "
        "from plataforma.retencao_particao_log "
        "where acao = 'default_recebeu_linha' "
        "and competencia_inicio = 203801; "
        "rollback;"
    )

    assert resultado.stdout.strip() == "1"


def test_partition_pruning_2026() -> None:
    resultado = _psql(
        "explain (analyze, verbose, buffers) "
        "select count(*) "
        "from bruto_ans.sib_beneficiario_operadora "
        "where competencia between 202601 and 202612;"
    )
    plano = resultado.stdout

    assert "sib_beneficiario_operadora_2026" in plano
    assert "sib_beneficiario_operadora_2025" not in plano
    assert "sib_beneficiario_operadora_2027" not in plano
    assert "sib_beneficiario_operadora_default" not in plano


def test_default_vazia() -> None:
    resultado = _psql("select count(*) from bruto_ans.sib_beneficiario_operadora_default;")

    assert resultado.stdout.strip() == "0"
