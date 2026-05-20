"""Testes unitários do schema CadastroInput (validações Pydantic)."""

import pytest
from pydantic import ValidationError

from api.app.routers.auth import CadastroInput


def _payload_valido(**overrides) -> dict:
    base = {
        "email": "ana@empresa.com.br",
        "nome": "Ana Silva",
        "senha": "senha-forte-123",
        "empresa": "Empresa LTDA",
        "cnpj": "53.936.542/0001-37",
        "telefone": "(11) 98765-4321",
        "cargo": "Analista de Dados",
        "segmento": "healthtech",
        "objetivo_uso": "testar_api",
        "aceite_termos": True,
        "aceite_lgpd": True,
    }
    base.update(overrides)
    return base


def test_cadastro_b2b_valido_normaliza_cnpj_telefone():
    body = CadastroInput.model_validate(_payload_valido())
    assert body.cnpj == "53936542000137"
    assert body.telefone == "11987654321"
    assert body.segmento == "healthtech"


def test_cadastro_b2b_sem_aceite_termos_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(aceite_termos=False))


def test_cadastro_b2b_sem_aceite_lgpd_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(aceite_lgpd=False))


def test_cadastro_b2b_cnpj_invalido_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(cnpj="11111111111111"))


def test_cadastro_b2b_segmento_invalido_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(segmento="setor_inventado"))


def test_cadastro_b2b_objetivo_invalido_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(objetivo_uso="quero_dados"))


def test_cadastro_b2b_telefone_invalido_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(telefone="123"))


def test_cadastro_b2b_senha_curta_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(senha="curta"))


def test_cadastro_b2b_email_invalido_falha():
    with pytest.raises(ValidationError):
        CadastroInput.model_validate(_payload_valido(email="nao-eh-email"))


def test_cadastro_b2b_campos_opcionais_aceita_omissao():
    body = CadastroInput.model_validate(_payload_valido())
    assert body.site_empresa is None
    assert body.tamanho_empresa is None
    assert body.mensagem is None


def test_cadastro_b2b_aceita_opcionais_quando_fornecidos():
    body = CadastroInput.model_validate(_payload_valido(
        site_empresa="https://empresa.com.br",
        tamanho_empresa="11-50",
        mensagem="Avaliando para integração de BI.",
    ))
    assert body.site_empresa == "https://empresa.com.br"
    assert body.tamanho_empresa == "11-50"
    assert body.mensagem == "Avaliando para integração de BI."
