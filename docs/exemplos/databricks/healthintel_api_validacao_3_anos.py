# Databricks notebook source
# MAGIC %md
# MAGIC # HealthIntel Core ANS - validacao de cobertura 3 anos

# COMMAND ----------

import os
import re
from datetime import datetime, timezone

import requests
from pyspark.sql import Row

BASE_URL = os.getenv("HEALTHINTEL_API_BASE_URL", "https://api.healthintel.local").rstrip("/")
API_KEY = dbutils.secrets.get("healthintel", "api_key")
HEADERS = {"X-API-Key": API_KEY}
DESTINO = "healthintel_ans_smoke.smoke_api_3_anos"


def get_json(path, params=None):
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params or {}, timeout=60)
    resp.raise_for_status()
    return resp.json()


def ano_de_valor(valor):
    if valor is None:
        return None
    texto = str(valor).strip().upper()
    if re.fullmatch(r"\d{6}", texto):
        return int(texto[:4])
    if re.fullmatch(r"\d{4}", texto):
        return int(texto)
    match = re.fullmatch(r"[1-4]T(\d{4})", texto)
    if match:
        return int(match.group(1))
    match = re.fullmatch(r"(\d{4})Q[1-4]", texto)
    if match:
        return int(match.group(1))
    return None


def campo_temporal(item):
    tipo = item.get("tipo_granularidade_temporal")
    if tipo == "mensal":
        return "competencia"
    if tipo == "trimestral":
        return "trimestre"
    if tipo == "anual":
        return "ano_base"
    return None


def materializar_path(path):
    return (
        path.replace("{registro_ans}", os.getenv("HEALTHINTEL_SMOKE_REGISTRO_ANS", "000001"))
        .replace("{cd_municipio}", os.getenv("HEALTHINTEL_SMOKE_CD_MUNICIPIO", "3550308"))
        .replace("{sg_uf}", os.getenv("HEALTHINTEL_SMOKE_SG_UF", "SP"))
    )


# COMMAND ----------

endpoints = get_json("/v1/meta/endpoints")["dados"]
linhas = []

for item in endpoints:
    path = item.get("path") or item.get("rota")
    if not path or not item.get("aparece_catalogo_publico"):
        continue

    url_path = materializar_path(path)
    payload = get_json(url_path, {"page": 1, "per_page": 100, "pagina": 1, "por_pagina": 100})
    dados = payload.get("dados", [])
    meta = payload.get("meta", {})
    janela = meta.get("janela_temporal") or {}
    campo = campo_temporal(item)

    anos = set()
    if campo:
        for row in dados:
            ano = ano_de_valor(row.get(campo) or row.get("competencia_id"))
            if ano:
                anos.add(ano)
    if not anos and janela.get("anos_cobertos"):
        anos = set(int(ano) for ano in janela["anos_cobertos"])

    status = janela.get("status_cobertura") or item.get("status_cobertura_3_anos")
    resultado = "ok" if status in {"ok_3_anos", "snapshot_vigente", "nao_temporal"} else "falha"
    linhas.append(
        Row(
            endpoint=path,
            total_meta=int(meta.get("total") or 0),
            anos_detectados_dados=sorted(anos),
            qtd_anos_detectados=len(anos),
            status_cobertura_3_anos=status,
            resultado=resultado,
            validado_em=datetime.now(timezone.utc).isoformat(),
        )
    )


# COMMAND ----------

df = spark.createDataFrame(linhas)
spark.sql("create database if not exists healthintel_ans_smoke")
(
    df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(DESTINO)
)
display(df.orderBy("endpoint"))
