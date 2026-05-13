"""Sprint 43 — testes unitários do auto-detector de layout.

Não toca o Layout Service real; mocka httpx via respx.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

import httpx
import pytest

from ingestao.app.layout_autodetect import (
    assinar_colunas,
    detectar_cabecalho,
    detectar_cabecalho_de_bytes,
    detectar_e_resolver_layout,
    solicitar_rascunho,
)


def test_assinar_colunas_normaliza_e_e_estavel():
    a = assinar_colunas(["A", " b ", "C "])
    b = assinar_colunas(["a", "B", "c"])
    assert a == b
    assert isinstance(a, str)
    assert len(a) == 64  # sha256 hex


def test_assinar_colunas_ordem_importa():
    a = assinar_colunas(["a", "b", "c"])
    b = assinar_colunas(["c", "b", "a"])
    assert a != b


def test_detectar_cabecalho_utf8(tmp_path: Path):
    arq = tmp_path / "x.csv"
    arq.write_text("col1;col2;col3\n10;20;30\n", encoding="utf-8")
    colunas = detectar_cabecalho(arq)
    assert colunas == ["col1", "col2", "col3"]


def test_detectar_cabecalho_com_bom(tmp_path: Path):
    arq = tmp_path / "x_bom.csv"
    arq.write_bytes("﻿col1;col2\n10;20\n".encode("utf-8"))
    colunas = detectar_cabecalho(arq)
    assert colunas == ["col1", "col2"]


def test_detectar_cabecalho_latin1_fallback(tmp_path: Path):
    arq = tmp_path / "x_latin.csv"
    arq.write_bytes("descrição;valor\n".encode("latin-1"))
    colunas = detectar_cabecalho(arq)
    assert "descrição" in colunas
    assert "valor" in colunas


def test_detectar_cabecalho_de_bytes():
    conteudo = "A;B;C\n1;2;3\n".encode("utf-8")
    colunas = detectar_cabecalho_de_bytes(conteudo)
    assert colunas == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_detectar_e_resolver_layout_quando_compativel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    arq = tmp_path / "tiss.csv"
    arq.write_text("competencia;registro_ans;codigo_plano\n", encoding="utf-8")

    async def fake_validar(*, dataset_codigo, colunas_detectadas, nome_arquivo):
        return {
            "compativel": True,
            "layout_id": "layout_x",
            "layout_versao_id": "v_x",
            "motivos": [],
        }

    monkeypatch.setattr(
        "ingestao.app.layout_autodetect.validar_arquivo_layout", fake_validar
    )
    chamou_rascunho = False

    async def fake_rascunho(**kwargs):
        nonlocal chamou_rascunho
        chamou_rascunho = True
        return {}

    monkeypatch.setattr(
        "ingestao.app.layout_autodetect.solicitar_rascunho", fake_rascunho
    )

    resultado = await detectar_e_resolver_layout(
        dataset_codigo="tiss_ambulatorial", caminho_arquivo=arq
    )

    assert resultado.compativel is True
    assert resultado.layout_id == "layout_x"
    assert resultado.rascunho_criado is False
    assert chamou_rascunho is False


@pytest.mark.asyncio
async def test_detectar_e_resolver_layout_quando_incompativel_cria_rascunho(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    arq = tmp_path / "novo_layout.csv"
    arq.write_text("col_nova_1;col_nova_2;col_nova_3\n", encoding="utf-8")

    async def fake_validar(*, dataset_codigo, colunas_detectadas, nome_arquivo):
        return {
            "compativel": False,
            "layout_id": None,
            "layout_versao_id": None,
            "motivos": ["Assinatura não bate com nenhum layout ativo."],
        }

    monkeypatch.setattr(
        "ingestao.app.layout_autodetect.validar_arquivo_layout", fake_validar
    )

    chamadas_rascunho: list[dict] = []

    async def fake_rascunho(**kwargs):
        chamadas_rascunho.append(kwargs)
        return {
            "layout_id": "novo_layout_id",
            "layout_versao_id": "rascunho_v1",
            "status": "rascunho",
            "assinatura_colunas": kwargs.get("colunas") and "abc" or "",
            "reaproveitado": False,
        }

    monkeypatch.setattr(
        "ingestao.app.layout_autodetect.solicitar_rascunho", fake_rascunho
    )

    resultado = await detectar_e_resolver_layout(
        dataset_codigo="dataset_desconhecido", caminho_arquivo=arq
    )

    assert resultado.compativel is False
    assert resultado.rascunho_criado is True
    assert resultado.layout_id == "novo_layout_id"
    assert resultado.layout_versao_id == "rascunho_v1"
    assert len(chamadas_rascunho) == 1
    assert chamadas_rascunho[0]["dataset_codigo"] == "dataset_desconhecido"
    assert chamadas_rascunho[0]["colunas"] == ["col_nova_1", "col_nova_2", "col_nova_3"]
