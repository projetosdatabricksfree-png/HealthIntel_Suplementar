# HealthIntel — Core ANS v0.9 (Release Comercial)

**Tag**: `v0.9.0-core-ans`
**Data**: 2026-05-16
**Status**: ✅ pronto para piloto comercial controlado

---

> **A HealthIntel entrega um Core ANS curado para BI/API com tabelas comerciais
> governadas, acesso controlado, documentação, testes, catálogo de cobertura
> e bloqueio automático contra exposição de dados vazios ou incompletos.**

---

## O que é HealthIntel Core ANS

Plataforma **DaaS** (Data-as-a-Service) de dados públicos da ANS (Agência
Nacional de Saúde Suplementar) prontos para consumo corporativo. Você compra
**dados curados e governados**, não dashboards prontos, não BI embutido, não
consultoria.

A entrega é via:
- **SQL direto** sobre schema `consumo_ans` (BI corporativo, DBeaver, TablePlus, etc).
- **API REST** com `X-API-Key` (envelope `{dados, meta}`, paginação, rate limit).

---

## Cobertura comercial — 12 tabelas disponíveis

| Domínio | Tabela `consumo_ans.*` | Periodicidade |
|---|---|---|
| Produtos e planos | `consumo_produto_plano` | mensal |
| Histórico de planos | `consumo_historico_plano` | mensal |
| Regulatório agregado | `consumo_regulatorio_operadora_trimestre` | trimestral |
| IGR | `consumo_igr` | trimestral |
| NIP | `consumo_nip` | trimestral |
| IDSS | `consumo_idss` | anual |
| Taxa resolutividade | `consumo_taxa_resolutividade_operadora_trimestral` | trimestral |
| Prudencial | `consumo_prudencial_operadora_trimestral` | trimestral |
| Financeiro (DIOPS/FIP) | `consumo_financeiro_operadora_trimestre` | trimestral |
| Glosa | `consumo_glosa_operadora_mensal` | mensal |
| TUSS oficial vigente | `consumo_tuss_procedimento_vigente` | versão vigente |
| Regime especial | `consumo_regime_especial_operadora_trimestral` | trimestral |

Cobertura completa em [`cobertura_atual_release_0_9.md`](../catalogo_dados/consumo_ans/cobertura_atual_release_0_9.md).

---

## O que **não** está incluso nesta release

- **TISS** (todas as subfamílias) — fora do escopo. Não prometido.
- **SIB histórico completo** — parciais não publicados como produto.
- **CNES rede assistencial** — fonte bloqueada.
- **NTRP / precificação** — carga em roadmap.
- **Ressarcimento SUS** — em roadmap.

Diferentemente de fornecedores que **vendem ANS completa** sem entregar,
nós explicitamos cada limitação no catálogo.

---

## Diferenciais técnicos

### 1. Hard gate comercial automático

Script `validar_consumo_ans_comercial.py` verifica em CI e antes de cada
release que:
- nenhuma tabela publicada como `disponivel` está vazia;
- toda tabela publicada tem fonte ANS declarada, granularidade, chave;
- toda tabela publicada tem teste dbt mínimo;
- nenhuma tabela TISS é marcada como `disponivel`.

Se falhar, release é bloqueada. **Sem exceção.**

### 2. Dicionário versionado por release

Cada tabela tem entrada obrigatória no [`dicionario_consumo_ans.md`](../catalogo_dados/consumo_ans/dicionario_consumo_ans.md)
com descrição, granularidade, chave, colunas, limitações conhecidas e
exemplo SQL.

### 3. Role isolada (`healthintel_cliente_reader`)

Cliente acessa **apenas** `consumo_ans`. Tentativas de SELECT em schemas
internos (`bruto_ans`, `stg_ans`, `nucleo_ans`, `api_ans`, `plataforma`,
`mdm_*`, `quality_ans`, `consumo_premium_ans`) retornam HTTP 403 / SQL 42501.

Validação empírica em [`evidencia_grants_cliente_reader_release_0_9.md`](../evidencias/release_0_9/evidencia_grants_cliente_reader_release_0_9.md).

### 4. API com auth, rate limit e log de uso

- `X-API-Key` obrigatório em todos os endpoints autenticados.
- Rate limit por plano (peso bronze=3, prata=2, premium=2, ouro=1).
- Log de uso em `plataforma.log_uso` por requisição (sem vazar chave).
- Endpoints sem dado real ficam ocultos do Swagger (`include_in_schema=False`).

### 5. Catálogo de cobertura público

Cliente sabe exatamente o que está comprando. Não há promessa de cobertura
que não existe.

---

## Modelos de consumo

### Modelo 1 — SQL direto (DaaS)

Cliente recebe usuário PostgreSQL e conecta com BI (DBeaver, PowerBI, Looker, etc).

**Para quem**: BI corporativo, analytics ad-hoc, exportação batch.

### Modelo 2 — API REST (em curva de maturidade)

Cliente recebe `X-API-Key` e consome via HTTP. Envelope `{dados, meta}`,
paginação, autenticação, rate limit.

**Para quem**: integrações com produtos próprios, dashboards web,
aplicações que consomem dado em runtime.

---

## SLA Release 0.9

| Item | Valor |
|---|---|
| Disponibilidade da plataforma | 99% mensal |
| Janela de manutenção | dom 02:00–04:00 BRT (com aviso de 48h) |
| Atualização dos dados | conforme periodicidade da fonte ANS (mensal/trimestral/anual) |
| SLA suporte técnico | 1 dia útil (dúvidas) / 4h (incidentes críticos) |
| Janela de carga | até D+5 do período da competência |

---

## Como contratar

1. Reunião comercial → catálogo de cobertura compartilhado.
2. Assinatura de contrato com escopo congelado em tag de release.
3. Provisionamento de usuário PostgreSQL + opcional chave de API.
4. Onboarding técnico (1h) — ver [`onboarding_cliente_consumo_ans_release_0_9.md`](../onboarding/onboarding_cliente_consumo_ans_release_0_9.md).
5. Piloto controlado de 30 dias com 12 tabelas disponíveis.

---

## Veredito da release (auditoria interna)

| Dimensão | Nota | Justificativa |
|---|---:|---|
| `consumo_ans` como DaaS | **9/10** | 12 tabelas com dado real + dicionário + queries + role + hard gate. -1 por SIB ainda parcial. |
| API como produto | **8/10** | Auth+rate+log reais; endpoints sem dado ocultos. -2 por TISS/SIB ainda em roadmap. |
| VPS para piloto controlado | **9/10** | Tag, backup, smoke verde, 12 tabelas prontas. -1 por ainda não ter HA. |
| VPS para consumo amplo | **6/10** | OK para piloto; consumo amplo requer SIB completo. |

Pendências não maquiadas em [`evidencia_release_0_9_resumo.md`](../evidencias/release_0_9/evidencia_release_0_9_resumo.md).

---

## Frase final

> "Esta release não é o catálogo ANS completo. É o **core ANS curado**: o
> subconjunto que conseguimos entregar com qualidade, governança e bloqueio
> automático contra exposição de dado vazio. O resto está no roadmap, com
> data e responsável claros."
