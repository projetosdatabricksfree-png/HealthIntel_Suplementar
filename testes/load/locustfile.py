import os
import random

from locust import HttpUser, between, task

# Registro ANS de amostra para testes de detalhe (substitui por valor real da VPS)
_REGISTRO_ANS_AMOSTRA = os.getenv("LOCUST_REGISTRO_ANS", "123456")

# UF de amostra para filtros de mercado
_UF_AMOSTRA = os.getenv("LOCUST_UF", "SP")


class ApiUser(HttpUser):
    """Plano growth_local: mix realista dos 6 endpoints Core MVP."""

    wait_time = between(0.5, 1.5)

    def on_start(self) -> None:
        api_key = os.getenv("LOCUST_API_KEY", "hi_local_dev_2026_api_key")
        self.cache_mode = os.getenv("LOCUST_CACHE_MODE", "mixed")
        self.headers = {"X-API-Key": api_key}

    def _params(self) -> dict[str, str]:
        if self.cache_mode == "cold":
            return {"busca": f"operadora-{random.randint(1, 99999)}"}
        if self.cache_mode == "hot":
            return {"busca": "Operadora"}
        if random.random() > 0.5:
            return {"busca": "Operadora"}
        return {"busca": f"operadora-{random.randint(1, 99999)}"}

    @task(3)
    def listar_operadoras(self) -> None:
        self.client.get(
            "/v1/operadoras",
            headers=self.headers,
            params=self._params(),
            name="/v1/operadoras",
        )

    @task(2)
    def detalhar_operadora(self) -> None:
        self.client.get(
            f"/v1/operadoras/{_REGISTRO_ANS_AMOSTRA}",
            headers=self.headers,
            name="/v1/operadoras/{registro_ans}",
        )

    @task(2)
    def consultar_score(self) -> None:
        self.client.get(
            f"/v1/operadoras/{_REGISTRO_ANS_AMOSTRA}/score",
            headers=self.headers,
            name="/v1/operadoras/{registro_ans}/score",
        )

    @task(2)
    def ranking_score(self) -> None:
        self.client.get(
            "/v1/rankings/operadora/score",
            headers=self.headers,
            params={"pagina": 1, "tamanho": 20},
            name="/v1/rankings/operadora/score",
        )

    @task(1)
    def mercado_municipio(self) -> None:
        self.client.get(
            "/v1/mercado/municipio",
            headers=self.headers,
            params={"uf": _UF_AMOSTRA},
            name="/v1/mercado/municipio",
        )

    @task(1)
    def listar_meta(self) -> None:
        self.client.get("/v1/meta/dataset", name="/v1/meta/dataset")
