# HealthIntel Core ANS

**API de inteligência de operadoras e mercado da saúde suplementar brasileira.**

---

## O que é

O HealthIntel Core ANS transforma dados públicos da ANS em uma API pronta para consumo por times de BI, analytics, consultorias, corretoras e healthtechs.

O cliente não precisa manter robôs de coleta, parsers de layout, banco de dados próprio, pipelines dbt ou atualização recorrente. Consome dados curados diretamente por API ou views SQL controladas.

---

## O que entregamos

| | |
|---|---|
| Dados tratados da ANS | CADOP, SIB, IDSS, IGR, NIP, DIOPS/FIP |
| Atualização recorrente | Carga automática conforme publicação ANS |
| API autenticada | Endpoints REST com paginação e rate limit |
| Score de operadora | Indicador composto v3 (regulatório, financeiro, rede, estrutural) |
| Ranking de operadoras | Por score, crescimento, oportunidade |
| Mercado por município | Market share, oportunidade territorial |
| Metadados de qualidade | Última atualização, status de cada dataset |

---

## Principais endpoints

```
GET /v1/operadoras
GET /v1/operadoras/{registro_ans}
GET /v1/operadoras/{registro_ans}/score
GET /v1/operadoras/{registro_ans}/beneficiarios
GET /v1/operadoras/{registro_ans}/financeiro
GET /v1/operadoras/{registro_ans}/regulatorio
GET /v1/rankings/operadoras
GET /v1/mercado/municipios
GET /v1/oportunidades/municipios
GET /v1/meta/datasets
```

---

## Planos

| Plano | Preço/mês | Inclui |
|---|---|---|
| Piloto | R$ 2.500 | 30 dias, 1 API key, onboarding, endpoints Core |
| Core API | R$ 3.900–6.900 | 1–3 API keys, endpoints Core, docs, suporte |
| BI/Consultoria | R$ 7.900–12.900 | Core + views SQL, apoio Power BI, onboarding técnico |
| Enterprise | Sob contrato | Histórico ampliado, datasets adicionais, SLA, MDM privado |

---

## Para quem

Corretoras · Consultorias atuariais · Healthtechs · Times de BI para saúde · Operadoras médias · Hospitais e redes · Times comerciais que analisam concorrência regional.

---

**Contato:** projetosdatabricksfree@gmail.com  
**Swagger:** `/docs` — autenticação por API key (`X-API-Key`)
