# HealthIntel Suplementar

Plataforma SaaS/DaaS de engenharia de dados para consumo e análise de dados públicos da ANS (Agência Nacional de Saúde Suplementar). Utiliza arquitetura medalhão (Bronze, Silver, Gold), governança de layouts em MongoDB e exposição via FastAPI.

## 🏗️ Arquitetura do Projeto

O repositório está organizado como um monorepo contendo todos os componentes da plataforma:

-   **`api/`**: API principal desenvolvida em FastAPI. Contém endpoints públicos para consulta de operadoras, scores e dados regulatórios, além de endpoints administrativos para billing e gerenciamento.
-   **`mongo_layout_service/`**: Microserviço dedicado à governança de layouts de arquivos da ANS, utilizando MongoDB para armazenamento flexível de metadados.
-   **`ingestao/`**: Camada de ingestão contendo DAGs do Airflow e scripts Python para extração de dados (IGR, NIP, RN623) e carga na camada Bronze.
-   **`healthintel_dbt/`**: Coração da transformação de dados. Implementa a arquitetura medalhão, testes de qualidade de dados e geração de marts para consumo da API.
-   **`infra/`**: Configuração de infraestrutura local via Docker Compose (PostgreSQL, MongoDB, Redis, Airflow, Nginx).
-   **`docs/`**: Documentação completa do projeto, incluindo PRD mestre, runbooks operacionais e detalhamento de todas as 12 sprints de desenvolvimento.
-   **`scripts/`**: Utilitários para seeding de banco de dados, testes de carga e inicialização de ambiente.

## 🚀 Como Subir o Ambiente Local

Como o projeto lida com dados sensíveis e configurações de infraestrutura, siga os passos abaixo:

1.  **Configuração de Ambiente**: Crie um arquivo `.env` na raiz do projeto seguindo as definições necessárias (PostgreSQL, MongoDB, tokens de serviço).
2.  **Inicialização da Stack**: Execute o comando para subir todos os containers:
    ```bash
    make up
    ```
    Se a porta `27017` já estiver ocupada no seu ambiente, o Mongo expõe `27018` por padrão no host.
3.  **Bootstrap de Layouts**: Inicialize o registro de layouts no MongoDB:
    ```bash
    python scripts/bootstrap_layout_registry_regulatorio.py
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

O projeto utiliza ferramentas modernas para garantir a qualidade do código e dos dados:

-   **Linting**: `make lint` (Ruff)
-   **SQL Linting**: `make sql-lint` (SQLFluff)
-   **Testes**: `make test` (Pytest)
-   **Smoke Test**: `make smoke` (Validação fim-a-fim do piloto)
-   **Carga**: `make load-test` (Testes de performance via Locust)

## 📄 Documentação Operacional

Para detalhes sobre a operação da plataforma e runbooks, consulte:
-   `docs/runbooks/`: Procedimentos de aprovação de layout e reprocessamento.
-   `docs/operacao/slo_sla.md`: Metas operacionais e indicadores de performance.
-   `docs/operacao/baseline_capacidade.md`: Limites de carga e escalabilidade.

---
*Este projeto está em baseline funcional (Sprint 12 concluída).*
