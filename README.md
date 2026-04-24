# HealthIntel Suplementar

Plataforma SaaS/DaaS de engenharia de dados para consumo e análise de dados públicos da ANS (Agência Nacional de Saúde Suplementar). Utiliza arquitetura medalhão (Bronze, Silver, Gold), governança de layouts em MongoDB e exposição via FastAPI.

## 🏗️ Arquitetura do Projeto

O repositório está organizado como um monorepo contendo todos os componentes da plataforma:

-   **`api/`**: API principal desenvolvida em FastAPI. Contém endpoints públicos para consulta de operadoras, scores e dados regulatórios, além de endpoints administrativos para billing e gerenciamento.
-   **`mongo_layout_service/`**: Microserviço dedicado à governança de layouts de arquivos da ANS, utilizando MongoDB para armazenamento flexível de metadados.
-   **`ingestao/`**: Camada de ingestão contendo DAGs do Airflow e scripts Python para extração de dados (IGR, NIP, RN623, SIB, CADOP) e carga na camada Bronze. Inclui fluxo streaming para arquivos grandes (SIB).
-   **`healthintel_dbt/`**: Coração da transformação de dados. Implementa a arquitetura medalhão, testes de qualidade de dados e geração de marts para consumo da API.
-   **`infra/`**: Configuração de infraestrutura local via Docker Compose (PostgreSQL, MongoDB, Redis, Airflow, Nginx).
-   **`docs/`**: Documentação completa do projeto, incluindo PRD mestre, runbooks operacionais e detalhamento de todas as sprints de desenvolvimento.
-   **`scripts/`**: Utilitários para seeding de banco de dados, testes de carga, ingestão real e inicialização de ambiente.

### Camadas de Dados

| Camada | Schema | Descrição |
|--------|--------|-----------|
| **Bronze** | `bruto_ans` | Dados brutos ingeridos da ANS com metadados de lote |
| **Staging** | `stg_ans` | Tipagem, limpeza, normalização e preparação técnica |
| **Intermediate** | `int_ans` | Joins, enriquecimentos e modelos intermediários |
| **Gold Analítico** | `nucleo_ans` | Fatos, dimensões, marts e métricas curadas |
| **Serving API** | `api_ans` | Modelos otimizados para os endpoints FastAPI |
| **Consumo** | `consumo_ans` | Data products para clientes com grants de segurança |

## 🚀 Como Subir o Ambiente Local

1.  **Configuração de Ambiente**: Crie um arquivo `.env` na raiz do projeto a partir de `.env.exemplo`.
2.  **Inicialização da Stack**:
    ```bash
    make up
    ```
3.  **Bootstrap de Layouts**: Inicialize o registro de layouts no MongoDB:
    ```bash
    make bootstrap-regulatorio-layouts
    make bootstrap-rede-layouts
    make bootstrap-cnes-layouts
    make bootstrap-tiss-layouts
    make bootstrap-sib-layouts
    make bootstrap-cadop-layouts
    ```
4.  **Carga de Dados Demo**: Popule o banco de dados com dados de demonstração:
    ```bash
    make demo-data
    ```
5.  **Build do dbt**: Compile e execute as transformações do dbt:
    ```bash
    make dbt-build
    ```

### Serviços Disponíveis:
-   **API Pública**: `http://localhost:8080`
-   **Layout Service**: `http://localhost:8081`
-   **Airflow UI**: `http://localhost:8088`

## 🛠️ Desenvolvimento e Qualidade

| Comando | Descrição |
|---------|-----------|
| `make lint` | Linting Python (Ruff) |
| `make sql-lint` | Linting SQL (SQLFluff) |
| `make test` | Testes unitários e integração (Pytest) |
| `make smoke` | Smoke test piloto |
| `make smoke-prata` | Smoke test camada Prata (17 endpoints) |
| `make smoke-sib` | Smoke test SIB |
| `make smoke-cadop` | Smoke test CADOP |
| `make smoke-consumo` | Smoke test camada Consumo |
| `make smoke-ingestao-real` | Smoke test pós-ingestão real (idempotência) |
| `make dag-parse DAG=nome` | Validar DAG parseia sem erro |
| `make dag-run-real-sib UFS=AC COMPETENCIA=202501` | Ingestão real SIB streaming |
| `make dag-run-real-cadop COMPETENCIA=202501` | Ingestão real CADOP |
| `make load-test` | Testes de performance via Locust |

## 📄 Documentação Operacional

Para detalhes sobre a operação da plataforma e runbooks, consulte:
-   `docs/runbooks/`: Procedimentos de aprovação de layout e reprocessamento.
-   `docs/runbooks/ingestao_real_ans.md`: Runbook de ingestão real ANS (SIB/CADOP).
-   `docs/operacao/slo_sla.md`: Metas operacionais e indicadores de performance.
-   `docs/operacao/baseline_capacidade.md`: Limites de carga e escalabilidade.
-   `docs/releases/v3.0.0.md`: Relatório de preparação / Release Candidate da versão 3.0.0.

---
*Status corrente: Release Candidate Fase 4 — v3.0.0 pending. A tag final será criada somente após aprovação dos hard gates completos.*
