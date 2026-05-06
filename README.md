# HealthIntel Suplementar

**Plataforma DaaS (Data as a Service) para dados regulatórios da saúde suplementar brasileira.**

HealthIntel Suplementar é uma plataforma de engenharia de dados que transforma dados públicos e regulatórios da ANS (Agência Nacional de Saúde Suplementar) em data products confiáveis, modelados, documentados e prontos para consumo empresarial.

---

## Frontend Comercial / Portal do Cliente

O frontend da Fase 9 está em `frontend/healthintel_frontend_fase9` e implementa o site público e portal do cliente do HealthIntel Core ANS.

Comandos:

```bash
cd frontend/healthintel_frontend_fase9
cp .env.example .env
npm install
npm run dev
```

Documentação: `docs/produto/fase_9_frontend_portal_cliente.md`

---

## 1. Visão do Produto

HealthIntel Suplementar é uma **plataforma DaaS** que encapsula todo o ciclo de vida de dados regulatórios da saúde suplementar:

- **Coleta**: Extração automatizada de dados públicos da ANS.
- **Tratamento**: Validação de layouts, normalização de formatos, resolução de inconsistências.
- **Modelagem**: Arquitetura medalhão com camadas Bronze, Prata, Ouro e Premium.
- **Qualidade**: Testes automáticos, monitoramento de freshness, rastreamento de origem.
- **Exposição**: API autenticada, SQL controlado, tabelas desnormalizadas para BI.
- **Governança**: Versionamento de dados, controle de acesso por plano, auditoria de consumo.

O produto não é um simples repositório de scripts ou um dashboard de BI. É uma **plataforma comercial** que permite que empresas, times de dados e produtos digitais consumam dados regulatórios de alta qualidade sem construir internamente toda a infraestrutura de ingestão, validação, transformação e documentação.

---

## 2. Proposta de Valor

Clientes pagam para **não precisar construir internamente**:

| Atividade | Custo Interno | HealthIntel Suplementar |
|-----------|---------------|------------------------|
| Montar ingestão automática da ANS | ⚠️ Manutenção contínua, parsing de layouts inconsistentes | ✅ Automático, layouts versionados, atualizações mensais |
| Normalizar e validar dados | ⚠️ Engenheiros de dados, testes manuais | ✅ Regras de qualidade codificadas, testes contínuos |
| Modelar dados para BI/Analytics | ⚠️ Arquitetos, documentação dispersa | ✅ Tabelas analíticas prontas, contratos de dados, dicionário completo |
| Garantir conformidade | ⚠️ Rastreabilidade manual, auditorias offline | ✅ Logs automáticos, linhagem de dados, compliance built-in |
| Escalar acesso seguro | ⚠️ Gerenciar acesso, rate limiting, billing manual | ✅ API multi-tenant, rate limit automático, billing por uso |

**Resultado**: Clientes entram em produção em semanas, não meses. Reduzem custo operacional. Foco no negócio, não em plumbing de dados.

---

## 3. O que o Produto Entrega

### Camadas de Dados

| Camada | Schema | Descrição | Acesso Cliente |
|--------|--------|-----------|---|
| **Bronze** | `bruto_ans` | Dados brutos ingeridos com metadados de lote, preservando origem | Interna; eventual produto derivado deve sair via `api_ans` |
| **Prata** | `stg_ans`, `int_ans` (internas) | Normalização, tipagem, limpeza, validação, preparação para análise | Interna (nunca exposta diretamente) |
| **Ouro** | `nucleo_ans` (interna) | Fatos, dimensões, marts agregados orientados a tópicos | Interna (nunca exposta diretamente) |
| **API Serving** | `api_ans` (única superfície) | Tabelas/views otimizadas para endpoints FastAPI com paginação, índices, cache, rate limit | Standard+ (via API REST) |
| **Consumo BI Standard** | `consumo_ans` | Desnormalizadas, linguagem cliente, acesso via role `healthintel_cliente_reader` | Standard+ (SQL direto ou BI tools) |
| **Consumo Premium** | `consumo_premium_ans` | SLA garantido, enriquecimento adicional, acesso via role `healthintel_premium_reader` | Premium (SQL direto) |

### Contratos e Documentação

- ✅ **Contrato de dados**: Estrutura, semântica, SLA, lineage, owner.
- ✅ **Dicionário técnico e de negócio**: Campos, tipos, transformações, origem.
- ✅ **Testes de qualidade**: Cobertura mínima por tabela de consumo.
- ✅ **Rastreabilidade**: Origem, versão, histórico de mudanças por campo.
- ✅ **Versionamento**: Tabelas versionadas, mudanças breaking comunicadas, rolling deployment.

### Exposição Controlada

- ✅ **API REST paginada**: Endpoints via `api_ans`, filtrados, estruturados por domínio (operadora, mercado, regulatório). Sem acesso direto a schemas internos.
- ✅ **SQL Controlado**:
  - **Standard**: Acesso via role `healthintel_cliente_reader` a `consumo_ans` (tabelas desnormalizadas).
  - **Premium**: Acesso via role `healthintel_premium_reader` a `consumo_premium_ans` (SLA garantido, enriquecimento).
- 🚧 **Rate Limiting**: Por plano e cliente (em implementação/roadmap).
- 🚧 **Autenticação**: X-API-Key (implementado); OAuth (roadmap).
- ✅ **Autorização**: Planos com `camadas_permitidas` controla acesso a camadas e datasets.
- ✅ **Logs de Consumo**: Rastreamento em `plataforma.log_uso` (queries, endpoints, volume, origem).

---

## 4. O que o Produto NÃO É

❌ **Não é um dashboard final**: HealthIntel entrega dados prontos. O cliente monta seu próprio BI, Metabase, Power BI, ou integração customizada.

❌ **Não é uma ferramenta genérica de BI**: Não competimos com Tableau, Looker ou Power BI. Somos a camada de dados que alimenta essas ferramentas.

❌ **Não é entrega completa irrestrita da base**: Nunca permitiremos download integral ou bypass de autenticação. Dados são consumidos por paginação, filtros e limits.

❌ **Não é revenda simples de arquivo público**: Apenas reempacotar CSV da ANS não é produto. Adicionamos valor via qualidade, modelagem, validação e exposição controlada.

❌ **Não é uma API sem curadoria**: Toda tabela, endpoint e coluna expostos têm proprietário, contrato, testes, e SLA.

❌ **Não é um projeto acadêmico**: Este é um produto comercial com ciclo de vida real, escalabilidade, observabilidade, segurança, billing e suporte.

❌ **Não é um repositório de scripts soltos**: Código está organizado, versionado, testado e deployado via CI/CD. Sem drift entre produção e repositório.

---

## 5. Regra Central de Desenvolvimento

### **Única pergunta que importa:**
> Essa entrega aproxima o produto de disponibilizar **tabelas confiáveis, governadas e consumíveis pelo cliente**?

Se a resposta for **não**, a entrega é secundária, dívida técnica ou fora de escopo.

Exemplos:

- ✅ **Sim**: Adicionar campo novo ao mart de operadora com teste + contrato + documentação.
- ✅ **Sim**: Reduzir latência de API em 50% via índice + query rewrite.
- ✅ **Sim**: Implementar rate limit por plano para proteger SLA.
- ❌ **Não**: Refatoração pura em utilitários sem mover entrega.
- ❌ **Não**: Dashboard interno bonito (sem cliente pedindo).
- ❌ **Não**: Suporte a 10 formatos de export sem cliente pedindo.

---

## 6. Modelo de Consumo

### Canais de Acesso

1. **API REST Paginada** (Standard+)
   - Endpoints via `api_ans`: estruturados por domínio (operadora, mercado, regulatório, etc).
   - Resposta em envelope: `{dados: [...], meta: {total, pagina, competencia_referencia, ...}}`.
   - Autenticação: X-API-Key.
   - Rate limit: Diferenciado por plano (limites menores em Starter, maiores em Enterprise/Premium). Detalhe em roadmap.
   - Paginação obrigatória: máximo de registros por request varia por plano, impede dump integral.

2. **SQL BI Standard** (Standard+)
   - Schema: `consumo_ans` (tabelas desnormalizadas, linguagem cliente).
   - Role: `healthintel_cliente_reader` (sem acesso a schemas internos ou sensíveis).
   - Atualização: automática via `dag_dbt_consumo_refresh.py`.
   - Use case: BI tools (Power BI, Metabase), SQL direto, integrações.

3. **SQL Premium** (Premium)
   - Schema: `consumo_premium_ans` (SLA garantido, enriquecimento adicional).
   - Role: `healthintel_premium_reader` (restrito ao tier Premium).
   - Auditoria: queries rastreadas em `plataforma.log_uso`.
   - SLA: uptime, latência, retenção de dados.

### Modelo de Faturamento (Roadmap)

- **Por plano**: Starter (API, exploração), Standard (BI, consumo limitado), Enterprise (volume alto, SLA), Premium (SQL Premium, enriquecimento).
- **Por uso**: requisições/mês (API), queries/mês (SQL), volume em GB, concurrent connections.
- **Por volume**: rate limits, retention, concurrent connections variam por tier.
- **Modelos**: pay-as-you-go, volume commitment, contratos anuais.

---

## 7. Regra de Proteção Comercial

**Objetivo**: Evitar que cliente faça uma extração integral e substitua o serviço.

### Controles Obrigatórios

| Controle | Implementação | Justificativa |
|----------|--------------|---------------|
| **Paginação** | Máximo 10k registros/request, cursor stateless | Impede dump integral |
| **Filtros** | Alguns filtros obrigatórios (ex: competência) | Força uso de API, não query raw |
| **Rate Limit** | Por cliente, diferenciado por plano | Impede scraping paralelo |
| **Autenticação** | X-API-Key, OAuth (roadmap) | Impede acesso anônimo |
| **Autorização** | Plano controla camadas e datasets | Cliente Premium ≠ cliente Starter |
| **Logs** | Toda query/request em `plataforma.log_uso` | Detecta padrão abusivo |
| **Contrato** | T&Cs explícitas sobre uso permitido | Fundamento legal |
| **SLA Comercial** | Downtime compensado, overages cobrados | Skin in the game |

### Sinais de Abuso

- Query com 1M+ registros em minutos → Throttle imediato, alerta operacional.
- Download completo de tabela com múltiplos workers → Bloqueio temporário, revisão contratual.
- Tentativa de reversa de schema → Revoke role, auditoria.
- Compartilhamento ou venda de dados para terceiro → Cancelamento de conta, ação legal.

---

## 8. Arquitetura-Alvo

```
┌─────────────────────────────────────────────────────────┐
│                    Fontes Oficiais (ANS)                │
│         (Público, FTP, CADOP, IGR, NIP, TISS, CNES)    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │   Ingestão Automatizada     │
        │   (Airflow + Scripts)       │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  Bronze (bruto_ans)         │
        │  Preserva origem, metadados │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  Prata (stg_ans, int_ans)   │
        │  Valida, normaliza, limpa   │
        │  Quarentena automática      │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  Ouro (nucleo_ans)          │
        │  Fatos, dimensões, marts    │
        │  Regras de negócio, SCD2    │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    ┌───▼────────┐          ┌────────▼──────────┐
    │ api_ans    │          │  consumo_*        │
    │ (única     │          │  (SQL direto)     │
    │ superfície)│          │  - consumo_ans    │
    │ Índices    │          │  - consumo_premium│
    │ Cache      │          │  _ans             │
    └───┬────────┘          └────────┬──────────┘
        │                           │
    ┌───▼──────────────────────────▼──┐
    │    FastAPI (Port 8000)           │
    │    - Endpoints REST paginados    │
    │    - Auth (X-API-Key)            │
    │    - Rate limit (por plano)      │
    │    - Logs: plataforma.log_uso    │
    │    - Cache: Redis                │
    └────────────────────────────────┘
        │
        ├─► PostgreSQL (relacional)
        │   └─ Nunca expõe bruto_ans, stg_ans, int_ans, nucleo_ans diretamente
        ├─► MongoDB (metadados de layouts)
        ├─► Redis (cache de API)
        └─► Arquivos (raw, processados)

┌────────────────────────────────────┐
│  Observabilidade & Governança      │
│  - Logs estruturados               │
│  - Métricas via Prometheus         │
│  - Linhagem via dbt docs           │
│  - Auditoria de dados              │
└────────────────────────────────────┘
```

### Separação de Responsabilidades

| Camada | Propósito | Schema | Acesso Cliente |
|--------|-----------|--------|---|
| Bronze | Preservação integral, auditoria | `bruto_ans` | (Interna; acesso futuro via `api_ans` se necessário) |
| Prata | Qualidade, normalização | `stg_ans`, `int_ans` | ❌ **NUNCA exposta** (interna) |
| Ouro | Análise, marts, KPIs | `nucleo_ans` | ❌ **NUNCA exposta** (interna) |
| API Serving | Endpoint REST controlado | `api_ans` (única superfície) | ✅ Standard+ via `/v1/*` (paginado, autenticado, rate limit) |
| BI Standard | SQL BI, desnormalizadas | `consumo_ans` | ✅ Standard+ via role `healthintel_cliente_reader` |
| SQL Premium | SLA, enriquecimento | `consumo_premium_ans` | ✅ Premium via role `healthintel_premium_reader` |

**Regra de Ouro**:
- API nunca lê `bruto_ans`, `stg_ans`, `int_ans` ou `nucleo_ans` diretamente.
- Toda exposição cliente passa por `api_ans` (API) ou `consumo_*` (SQL).
- Schemas internos são **blindados** contra acesso cliente.

---

## 9. Princípios Não Negociáveis

1. **Baseline Estável**: Baseline aprovado não é quebrado. Mudanças breaking requerem nova versão, novo endpoint, deprecation warning.

2. **Fases Completas não Reabrem**: Sprint concluída = implementada, testada, documentada, validada. Reabrir requer justificativa executiva.

3. **Evolução Aditiva**: Novas fases agregam, não derrubam. v1.0 + Fase2 = v2.0 com v1.0 intacto.

4. **Contrato por Tabela**: Toda tabela de consumo tem: owner, SLA, testes mínimos, documentação, changelog.

5. **Testes Obrigatórios**: Cobertura mínima por modelo de consumo. Teste quebrado = bloqueio de merge.

6. **Autorização por Endpoint**: Cada endpoint tem regra de plano e camada. Sem acesso anônimo.

7. **Semântica Previsível**: `fat_*` = fato, `dim_*` = dimensão, `stg_*` = staging, `int_*` = intermediário, `api_*` = serving, `consumo_*` = cliente. Sem exceções.

8. **Documentação Sincronizada**: Modelo muda → Contrato muda → Documentação muda → Testes adaptam. Tudo junto.

9. **Checkbox [x] = Pronto**: Tarefa marcada como concluída **apenas** quando implementada, testada, mergida e validada em produção. Não é "feito em 90%".

10. **Auditoria Completa**: `plataforma.job`, `plataforma.log_uso`, `plataforma.dataset_versao` rastreiam tudo. Sem black holes.

---

## 10. Roadmap Macro

| Fase | Sprints | Estado | Descrição |
|------|---------|--------|-----------|
| **1. Fundação** | 01–12 | ✅ CONCLUÍDA (v1.0.0) | Ingestão, Bronze, Prata, Ouro básico, API Gold, dbt, scoring |
| **2. Datasets** | 13–14 | ✅ CONCLUÍDA (v1.1.0) | CNES, TISS, Prata estendida |
| **3. Qualidade** | 15–20 | ✅ CONCLUÍDA (v2.0.0) | Bronze API, Prata API, governança, freshness SLO, Score v3 |
| **4. Comercial** | 21–25 | ✅ CONCLUÍDA (v3.0.0) | Ingestão real SIB/CADOP, Gold marts BI, consumo_ans, billing |
| **5. Piloto** | 26–30 | 🚧 EM ANDAMENTO | Piloto comercial, observabilidade, hardening, escalabilidade |
| **6. Premium** | 31–35 | 📋 ROADMAP | MDM, enriquecimento, consultas complexas, SLA 99.9% |
| **7. Portal** | 36–40 | 📋 ROADMAP | Onboarding de clientes, auto-provisioning, documentação cliente |
| **8. Observabilidade** | 41–45 | 📋 ROADMAP | Dashboards operacionais, alertas, SLI/SLO públicas, status page |

---

## 11. Instruções para Agentes de IA

Qualquer IA (Claude, ou outra) que atuar neste repositório deve seguir estas regras:

### Identidade do Projeto

- Este é um **produto DaaS comercial**, não um pipeline técnico genérico.
- O norte é sempre: **"Isso aproxima o projeto de entregar tabelas confiáveis, governadas e consumíveis?"**
- Não há espaço para BI final, dashboard bonito, ou dump irrestrito da base.

### Obrigações

- ✅ Preservar posicionamento DaaS. Nunca simplificar a uma ferramenta genérica.
- ✅ Respeitar arquitetura medallion: Bronze → Prata → Ouro → Premium.
- ✅ Respeitar schemas e roles definidos. Sem acesso anômalo.
- ✅ Toda tabela de consumo precisa de contrato, testes, documentação.
- ✅ Toda mudança breaking precisa de deprecation + nova versão.
- ✅ Rate limit, autenticação, autorização são não-negociáveis.
- ✅ Logs de consumo devem rastrear toda atividade.

### Procedimentos

1. **Antes de mudanças grandes** (novos endpoints, novos models, refactor em camadas): Gere um **plano explícito** com:
   - Objetivo alinhado com "tabelas consumíveis".
   - Impacto em baseline, versioning, testes, documentação.
   - Riscos, bloqueadores, hardgates.
   - Arquivos alterados.

2. **Ao escrever código**:
   - Prefira editar existente a criar novo.
   - Respeite convenções (`fat_*`, `dim_*`, `stg_*`, etc).
   - Toda tabela = contrato de dados explícito.
   - Teste mínimo obrigatório.
   - Documentação mínima obrigatória (comentário, YAML, PR description).

3. **Ao completar tarefa**:
   - **Não marque como concluída** sem evidência: teste passou, merge aconteceu, validação em staging/prod.
   - Sempre liste **arquivos alterados**.
   - Sempre aponte **riscos, pendências, hardgates**.
   - Se houver hardgate não resolvido, sinalize explicitamente.

4. **Operação**:
   - Nunca altere baseline aprovado sem autorização.
   - Nunca reabra sprint concluída sem justificativa executiva.
   - Sempre prefira aditivo a destrutivo.

### Anti-Padrões

❌ Marcar sprint como "90% completa".  
❌ Fazer refatoração "enquanto estou aqui" (scope creep).  
❌ Adicionar feature "para o futuro" sem cliente pedindo.  
❌ Deixar comentários `TODO: remove later` no código.  
❌ Quebrar baseline e consertar depois (sem deprecation).  
❌ Propor download irrestrito de dados ou bypass de paginação.  

---

## 12. Status Atual do Projeto

**HealthIntel Suplementar v3.0.0** — Fase 4 concluída. Fundação técnica estabelecida.

O projeto evoluiu de um **pipeline técnico de ingestão e modelagem** (Fases 1–4) para uma **plataforma DaaS comercial em evolução** (Fases 5+).

### ✅ Implementado

- Ingestão automática de 6+ datasets ANS (Público, FTP, CADOP, IGR, NIP, TISS, CNES).
- Validação de qualidade com quarentena automática.
- Arquitetura medalhão (Bronze → Prata → Ouro) com testes genéricos e singulares.
- API REST com endpoints via `api_ans` (autenticação X-API-Key implementada).
- Ingestão real SIB e CADOP com idempotência.
- Consumo BI via `consumo_ans` com role de segurança `healthintel_cliente_reader`.
- Documentação técnica, runbooks operacionais básicos.
- Orquestração dbt com testes de qualidade integrados.

### 🚧 Em Desenvolvimento / Roadmap

- **Rate Limit por Plano**: Estrutura preparada, implementação em progresso.
- **Billing**: Estrutura preparada em `plataforma.*`; cálculo e faturamento em roadmap.
- **SQL Premium via `consumo_premium_ans`**: Schema e role `healthintel_premium_reader` preparados; client pilot planejado.
- **Observabilidade**: Logs estruturados; dashboards e alertas em roadmap.
- **Documentação Comercial**: PRD fundacional; documentação cliente e SLA formais em roadmap.

### 📋 Roadmap (Fase 5+)

- **Fase 5 (Piloto Comercial)**: Validação com clientes reais, hardening de segurança, rate limit ativo, billing inicial.
- **Fase 6 (Premium)**: Enriquecimento de dados, MDM, produtos de maior valor agregado.
- **Fase 7 (Portal)**: Onboarding self-service, documentação cliente, analytics de uso.
- **Fase 8+ (Escalabilidade)**: Multi-region, disaster recovery, SLA garantido (99.9% target).

---

## 🏗️ Estrutura do Monorepo

O repositório é organizado como um monorepo contendo todos os componentes da plataforma:

-   **`api/`**: API principal em FastAPI. Endpoints públicos e autenticados expostos a partir de projeções controladas em `api_ans`, além de rotas administrativas como billing, layout e admin.
-   **`mongo_layout_service/`**: Microserviço de governança de layouts em MongoDB. Versionamento e validação de estrutura de arquivos ANS.
-   **`ingestao/`**: Camada de ingestão: DAGs Airflow, scripts Python, extração de ANS, validação de layout, carga em Bronze.
-   **`healthintel_dbt/`**: Transformação de dados via dbt. Modelos de todas as camadas, testes de qualidade, dbt docs.
-   **`infra/`**: Docker Compose local (PostgreSQL, MongoDB, Redis, Airflow, Nginx).
-   **`docs/`**: Documentação completa (PRD, runbooks, sprints, releases).
-   **`scripts/`**: Utilitários (seeding, ingestão real, smoke tests, load tests).
-   **`testes/`**: Testes de integração, regressão e carga.

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

### Serviços Disponíveis

| Serviço | URL | Descrição |
|---------|-----|-----------|
| API | `http://localhost:8000` | FastAPI principal (port 8000) |
| Layout Service | `http://localhost:8001` | Microserviço de layouts MongoDB |
| Airflow UI | `http://localhost:8088` | Orquestração de DAGs |
| PostgreSQL | `localhost:5432` | Banco relacional (schemas: bruto_ans, stg_ans, int_ans, nucleo_ans, api_ans, consumo_ans, consumo_premium_ans, plataforma) |
| MongoDB | `localhost:27017` | Metadados de layouts (DB: healthintel_layout) |
| Redis | `localhost:6379` | Cache de API |

---

## 🛠️ Desenvolvimento e Qualidade

### Linting e Verificação

| Comando | Descrição |
|---------|-----------|
| `make lint` | Linting Python (Ruff) |
| `make sql-lint` | Linting SQL (SQLFluff) |
| `make test` | Testes unitários e integração (Pytest) |

### Smoke Tests (Validação E2E)

| Comando | Descrição |
|---------|-----------|
| `make smoke` | Smoke test Piloto (datasets base) |
| `make smoke-prata` | Smoke test Prata (17 modelos de API Prata) |
| `make smoke-sib` | Smoke test SIB (ingestão real SIB) |
| `make smoke-cadop` | Smoke test CADOP (ingestão real CADOP) |
| `make smoke-cnes` | Smoke test CNES |
| `make smoke-tiss` | Smoke test TISS |
| `make smoke-consumo` | Smoke test consumo_ans (BI) |
| `make smoke-ingestao-real` | Smoke test pós-ingestão real (idempotência) |

### DAGs e Ingestão

| Comando | Descrição |
|---------|-----------|
| `make dag-parse DAG=nome` | Validar que DAG parseia sem erro |
| `make dag-run-real-sib UFS=AC COMPETENCIA=202501` | Ingestão real SIB (streaming por UF) |
| `make dag-run-real-cadop COMPETENCIA=202501` | Ingestão real CADOP |

### Performance

| Comando | Descrição |
|---------|-----------|
| `make load-test` | Teste de carga via Locust (simula clientes, mede latência/throughput) |

---

## 📄 Documentação Operacional

### Runbooks e Procedimentos

Para operação da plataforma, consulte:

- **`docs/runbooks/`**: Procedimentos operacionais (aprovação de layout, reprocessamento, troubleshooting).
- **`docs/runbooks/ingestao_real_ans.md`**: Runbook de ingestão real ANS (SIB/CADOP).
- **`docs/operacao/slo_sla.md`**: Metas operacionais, SLA de dados, indicadores.
- **`docs/operacao/baseline_capacidade.md`**: Limites de carga, escalabilidade, particionamento.
- **`docs/releases/v3.0.0.md`**: Relatório de entrega Fase 4.

### Documentação de Sprints

Cada fase tem documentação detalhada em `docs/sprints/`:

- **Fase 1–4**: Implementação de fundação, qualidade, ingestão real, marts BI, consumo.
- **Fase 5+**: Roadmap comercial, piloto, Premium, escalabilidade.

### Dicionário Técnico

Documentação de modelos dbt gerada via `dbt docs generate`. Consulte `healthintel_dbt/target/index.html` após `make dbt-build`.

---

## 📋 Checklist de Antes de Mergear

Antes de abrir PR ou mergear em main:

- [ ] Linting passou (`make lint`, `make sql-lint`).
- [ ] Testes passaram (`make test`, `make smoke`).
- [ ] Modelos dbt compila sem erro (`make dbt-compile`).
- [ ] Documentação atualizada (YAML em modelos, contrato de dados, changelog).
- [ ] Tabelas de consumo têm testes (`tests/assert_*.sql` ou generic tests).
- [ ] Se quebra baseline: nova versão + deprecation warning planejado.
- [ ] Changelog atualizado em `docs/releases/`.

---

## 🔗 Referências Rápidas

- **CLAUDE.md**: Instruções para Claude Code (arquitetura, convenções, workflows).
- **dbt docs**: `dbt docs generate` e abra `target/index.html`.
- **Logs estruturados**: `plataforma.job`, `plataforma.log_uso`.
- **Versionamento de dados**: `plataforma.dataset_versao`.
- **Contratos de dados**: Modelo em `YAML` nos arquivos `_*.yml` de dbt.

---

*HealthIntel Suplementar v3.0.0 — Fase 4 concluída. Evoluindo de pipeline técnico para plataforma DaaS comercial.*
