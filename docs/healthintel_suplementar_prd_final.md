# HEALTHINTEL SUPLEMENTAR

PRD final, arquitetura de referencia, backlog executavel e pacote-base de implementacao do monorepo.

| Campo | Valor |
| --- | --- |
| Versao | 2.0 |
| Status | Aprovado para execucao |
| Data base do documento | 22/04/2026 |
| Dominio | Saude suplementar / ANS |
| Tipo de produto | Engenharia de dados + API SaaS / DaaS |
| Stack mandatória | Python 3.12, FastAPI, PostgreSQL 16, MongoDB, dbt-core, dbt-postgres, Airflow 2.x, Redis, Nginx, Docker, Docker Compose, Alembic, SQLFluff, Locust |
| Convencoes | `pt_BR`, `snake_case`, tabelas no singular, datas e versoes explicitas |

---

## 1. Resumo Executivo do Produto

### 1.1 Visao executiva

O HealthIntel Suplementar e uma plataforma de infraestrutura de dados para o mercado de saude suplementar. O produto coleta, valida, traduz, versiona, estrutura e expõe dados publicos da ANS por meio de uma API REST autenticada, com governanca de layouts fisicos separada do nucleo analitico. O objetivo nao e produzir dashboards finais, e sim entregar dados prontos para integracao por times de dados, produto, risco, pricing, regulatorio e engenharia de clientes B2B.

### 1.2 Definicao objetiva do produto

O produto e composto por cinco capacidades principais:

1. Ingestao automatizada de fontes publicas da ANS.
2. Governanca de layout fisico manual e versionada em MongoDB.
3. Arquitetura medalhao e camada de servico em PostgreSQL.
4. Exposicao de endpoints monetizaveis via FastAPI.
5. Observabilidade operacional, qualidade e versionamento de datasets.

### 1.3 O que o produto e

- Plataforma API-first de dados publicos da ANS.
- Infraestrutura de engenharia de dados operada como produto.
- Motor de ingestao com compatibilidade historica de layouts.
- Registro formal de layouts, aliases e regras de parsing.
- Catalogo operacional de datasets, versoes e jobs.

### 1.4 O que o produto nao e

- Nao e BI.
- Nao e dashboard.
- Nao e consultoria analitica.
- Nao e data lake generico sem contrato.
- Nao e mecanismo de inferencia sem supervisao humana.

### 1.5 Proposta de valor

O cliente assina o servico, recebe credenciais de API e passa a consumir dados publicos da ANS com curadoria tecnica, historico, versionamento e SLA operacional sem precisar construir localmente:

- robos de download;
- tratamento de encoding;
- reconciliação de schema;
- normalizacao de layouts mutaveis;
- governanca de historico;
- marts analiticos;
- contratos de API.

### 1.6 ICP e cliente-alvo

ICP primario:

- healthtechs B2B;
- corretoras e distribuidores com area de inteligencia comercial;
- operadoras, administradoras e seguradoras com times de estrategia, produtos ou risco;
- consultorias com squads de dados;
- fintechs e plataformas de comparacao/regulacao.

ICP secundario:

- fundos e areas de M&A com tese em saude;
- equipes de pricing e revenue intelligence;
- software houses com produtos para operadoras ou prestadores.

### 1.7 Diferenciacao tecnica

- Governanca formal de layout fisico em MongoDB, desacoplada do dbt.
- Reprocessamento historico por versao de layout.
- Separacao explicita entre `layout registry`, `raw traduzido`, `camada canonica` e `camada de servico`.
- API lendo exclusivamente `api_ans`.
- Bronze imutavel com metadados estruturais de carga e parse.

### 1.8 Diferenciacao comercial

- Dados publicos transformados em produto operacional com contrato e SLA.
- Menor time-to-value para clientes que hoje dependem de analistas para preparar bases.
- Historico reproducivel e audivel, importante para vendas enterprise.
- Modelo de planos por volume de chamadas e profundidade de datasets.

### 1.9 Tese de valor do produto

Dados publicos da ANS sao amplamente reutilizaveis, mas caros de operar. O valor monetizavel nao esta na posse exclusiva do dado, e sim no pacote operacional:

- ingestao confiavel;
- compatibilidade entre ciclos;
- semantica canonicamente definida;
- versionamento e lineage;
- API consistente;
- suporte ao cliente.

### 1.10 Tese de monetizacao

O produto monetiza em quatro dimensoes:

- acesso por plano e limite RPM;
- acesso por familia de datasets;
- acesso por profundidade historica;
- add-ons enterprise de SLA, suporte e integrações dedicadas.

### 1.11 Por que curadoria de dados publicos da ANS vira produto vendavel

Porque o custo real do cliente esta na engenharia e nao no download bruto. As dores recorrentes sao:

- layouts fisicos instaveis;
- CSVs/XLSs heterogeneos;
- ausencia de contratos consolidados;
- quebra metodologica entre anos;
- falta de padrao operacional entre fontes.

### 1.12 Por que governanca de layout e vantagem competitiva

Sem governanca de layout:

- a ingestao quebra quando a ANS muda colunas sem aviso;
- o historico deixa de ser reprocessavel;
- o time passa a corrigir arquivos manualmente em SQL;
- aliases ficam espalhados em codigo e nao auditaveis.

Com governanca formal:

- aliases sao cadastrados manualmente por operador;
- cada layout tem ciclo de vida;
- a escolha de versao e deterministica;
- o historico continua processavel sem reescrever modelos analiticos.

### 1.13 Por que isto e DaaS / API SaaS e nao BI

Porque a entrega contractual do produto e:

- dataset curado;
- endpoint autenticado;
- metadado de versao;
- log de uso;
- SLA de pipeline.

O cliente continua livre para consumir em:

- notebooks;
- data warehouse proprio;
- aplicacoes;
- CRMs;
- produtos digitais;
- dashboards internos.

---

## 2. Documento de Negocio

### 2.1 Posicionamento

HealthIntel Suplementar posiciona-se como plataforma de dados regulatórios e operacionais da ANS para integracao por software e times de dados. O foco e reduzir atrito tecnico e oferecer velocidade de consumo com confiabilidade.

### 2.2 Personas B2B

| Persona | Objetivo | Dor atual | Ganho esperado |
| --- | --- | --- | --- |
| Head de Dados | Integrar fontes ANS ao stack do cliente | Pipeline instavel e manual | Fonte padronizada e historica |
| Product Manager B2B | Enriquecer produto com dados externos | Dificuldade de manter dados atualizados | Endpoint pronto com contrato |
| Analista Regulatorio | Monitorar operadoras e risco | Publicacoes difusas e sem historico integrado | Visao consolidada por operadora |
| Lider Comercial | Priorizar territorio, carteira e operadora | Bases dispersas e sem ranking confiavel | Market intelligence reutilizavel |
| CTO | Diminuir custo de engenharia de dado externo | Time preso em ETL de commodity | Infra pronta via API |

### 2.3 Dores resolvidas

- Integracao lenta de dados publicos.
- Falta de confiabilidade no historico.
- Alto custo de manutencao de pipeline local.
- Dificuldade de explicar quebras de metodologia.
- Ausencia de trilha auditavel de layout e parse.

### 2.4 Escopo dentro

- ingestao e curadoria de dados publicos ANS;
- governanca de layout manual;
- armazenamento relacional analitico e documental estrutural;
- exposicao de API REST;
- catalogo de datasets e pipeline;
- observabilidade e reprocessamento historico.

### 2.5 Escopo fora

- conectores proprietarios do cliente;
- cruzamento automatico com dados privados sem projeto especifico;
- dashboards customizados;
- analytics ad hoc como servico;
- cadastro operacional de clientes finais;
- ML/IA sem supervisao para inferencia de alias.

### 2.6 Planos comerciais

| Plano | RPM | Historico | Datasets | Endpoints | Suporte |
| --- | --- | --- | --- | --- | --- |
| Starter | 60 | 24 meses | Core MVP | consulta e metadados | email comercial |
| Growth | 300 | 60 meses | Core + rankings + regulatory basico | serie, score, rankings, meta | email + SLA util |
| Pro | 1000 | full historico disponivel | Core + Regulatory + Financial | completo fase 1-3 | prioritario |
| Enterprise | custom | full + snapshots dedicados | todos + add-ons | API completa + export + SLA dedicado | CSM + canal dedicado |

### 2.7 Pricing sugerido

| Plano | Preco sugerido mensal | Observacao |
| --- | --- | --- |
| Starter | R$ 2.490 | entrada e validacao de mercado |
| Growth | R$ 6.990 | uso recorrente por time de dados |
| Pro | R$ 14.900 | consumo corporativo intenso |
| Enterprise | sob proposta | customizacao, SLA e volume |

### 2.8 Politica de acesso

- Autenticacao por `X-API-Key`.
- Chave armazenada apenas por hash SHA-256.
- Controle de acesso por plano e familia de endpoint.
- Rate limit em Redis.
- Endpoints administrativos separados do dominio publico.

### 2.9 Onboarding do cliente

1. Cadastro comercial aprovado.
2. Contrato e aceite de termos.
3. Provisionamento de cliente e plano.
4. Geracao de chave API.
5. Envio de guia de integracao e colecao Postman.
6. Acompanhamento das primeiras chamadas e limites.

### 2.10 Politica de upgrade

- Upgrade imediato com troca de plano e ajuste de limites.
- Downgrade no ciclo seguinte, respeitando contrato vigente.
- Rotacao de chave opcional a cada troca de perfil de acesso.

### 2.11 Politica de suporte

- Starter: email em horario comercial.
- Growth: email com prioridade e SLA util.
- Pro: prioridade alta e atendimento tecnico funcional.
- Enterprise: CSM, canal dedicado e rito de governanca.

### 2.12 Estrategia de lancamento

1. MVP comercial com Core Platform.
2. 3 a 5 clientes-design partners.
3. Medicao de uso por endpoint e dataset.
4. Expansao para Regulatory Intelligence.
5. Expansao para Financial e Network Intelligence.

### 2.13 Roteiro de validacao comercial

- Validar disposicao de pagamento por API e dataset.
- Identificar endpoints com maior CAC/LTV.
- Medir tempo de onboarding.
- Medir percepcao de confiabilidade versus download bruto.

### 2.14 Roadmap executivo

- Fase 1: colocar de pe o produto vendavel.
- Fase 2: diferenciar via inteligencia regulatoria.
- Fase 3: elevar ticket com dados financeiros.
- Fase 4: ampliar tese de rede, cobertura e acesso.

### 2.15 Riscos de negocio

- Dado publico percebido como commodity.
- Escopo virar consultoria.
- Complexidade regulatoria aumentar antes da maturacao comercial.
- Dependencia de publicacoes ANS sem API oficial.

### 2.16 Vantagens competitivas

- Operacao de dado com contrato e reprocessamento.
- Layout registry manual, versionado e auditavel.
- API pronta para consumo.
- Historico coerente diante de mudancas fisicas.

---

## 3. Roadmap Completo de 12 Sprints

### 3.1 Tabela executiva

| Sprint | Fase | Objetivo | Entrega principal | Risco principal | Criterio de saida |
| --- | --- | --- | --- | --- | --- |
| 1 | Core | Fundacao de repo, infra e schemas | monorepo, compose, bootstrap | base instavel | ambiente sobe localmente |
| 2 | Core | Layout registry e ingestao CADOP/SIB | Mongo registry + bronze | layout mal definido | CADOP/SIB carregando em `bruto_ans` |
| 3 | Core | Staging, dimensions e SCD | `stg_*`, `dim_*`, snapshot | semantica canônica incompleta | dbt compile/test aprovados |
| 4 | Core | Fatos, score e `api_ans` | score, marts, endpoints MVP | performance | `/v1/operadoras` e `/score` disponiveis |
| 5 | Core | Metadados, billing base e observabilidade | `versao_dataset`, `log_uso`, metadados | billing fragil | uso e pipeline rastreaveis |
| 6 | Core | Hardening e piloto | CI/CD, carga, runbooks | regressao em estabilizacao | piloto controlado ativo |
| 7 | Regulatory | IGR, NIP e RN 623 | indicadores regulatórios | publicacao heterogenea | endpoints regulatórios basicos |
| 8 | Regulatory | Regime especial e prudencial | risco regulatório consolidado | html/painel instavel | score com flags regulatórias |
| 9 | Financial | DIOPS/FIP e VDA | fatos financeiros | schema amplo | marts financeiros validos |
| 10 | Financial | Glosa e score v2 | glosa + score expandido | fonte dependente de painel | score v2 publicado |
| 11 | Network | Rede e vazios | fatos de cobertura e oportunidade | dataset derivado de painel | ranking territorial v2 |
| 12 | Network | Fechamento de produto enterprise | otimizações finais e rollout | escopo de ultima milha | release enterprise aprovada |

### 3.2 Narrativa por sprint

#### Sprint 1

- Objetivo: fundar monorepo, Docker Compose, schemas e padroes do projeto.
- Escopo: repositório, bootstrap local, `bruto_ans`/`stg_ans`/`nucleo_ans`/`api_ans`/`plataforma`.
- Dependencias: nenhuma.
- Risco principal: base sem convencao uniforme.
- Criterio de saida: ambiente local sobe com Postgres, Mongo, Redis, Airflow, Nginx e scaffolds.
- Valor de negocio: diminui risco de retrabalho estrutural.

Checklist:

- [x] Criar monorepo e convenções.
- [x] Subir infraestrutura local.
- [x] Definir schemas e seeds iniciais.
- [x] Definir padrao de logs e config.
- [x] Definir `.env.exemplo`, `Makefile` e bootstrap.

Critério de aceite:

- Compose funcional.
- Healthchecks dos servicos respondendo.
- Estrutura de pastas congelada.

Teste obrigatorio: smoke test de subida.

Regressao minima: todos os servicos respondem `/saude`.

#### Sprint 2

- Objetivo: operacionalizar layout registry e ingestao de `CADOP`, `SIB por operadora` e `SIB por municipio`.
- Escopo: coleções Mongo, detecção de dataset, identificacao de layout, carga em bronze.
- Dependencias: Sprint 1.
- Risco principal: regra de compatibilidade insuficiente.
- Criterio de saida: arquivos com layout conhecido carregam em bronze com metadados estruturais completos.
- Valor de negocio: entra no ar o pipeline core do produto.

Checklist:

- [x] Criar coleções e índices Mongo.
- [x] Criar serviço administrativo de layout.
- [x] Implementar assinatura estrutural e seleção deterministica.
- [x] Carregar `CADOP` e `SIB` em `bruto_ans`.
- [x] Registrar quarentena e erros de parse.

Critério de aceite:

- Arquivo antigo continua processavel.
- Alias manual funciona sem heuristica.
- Carga grava `_layout_id` e `_layout_versao_id`.

Teste obrigatorio: teste de compatibilidade com dois layouts para a mesma tabela RAW.

Regressao minima: `CADOP` continua carregando apos cadastro de nova versao.

#### Sprint 3

- Objetivo: consolidar camada canonica inicial.
- Escopo: `stg_cadop`, `stg_sib_operadora`, `stg_sib_municipio`, snapshots e dimensoes.
- Dependencias: Sprint 2.
- Risco principal: definicao de chave canonica inconsistente.
- Criterio de saida: joins basicos estabilizados e dbt testando integridade.
- Valor de negocio: base pronta para mart e API.

Checklist:

- [x] Implementar modelos staging.
- [x] Implementar snapshot `snap_operadora`.
- [x] Implementar `dim_operadora_atual` e `dim_competencia`.
- [x] Declarar `sources`, testes e docs.
- [x] Implementar seeds referenciais.

Critério de aceite:

- `dbt compile` e `dbt test` aprovados.
- Chaves canônicas definidas.

Teste obrigatorio: teste singular de duplicidade por operadora/competencia.

Regressao minima: nenhum breaking change em schema de staging.

#### Sprint 4

- Objetivo: publicar primeiros fatos, score e API MVP.
- Escopo: `fat_score_operadora_mensal`, `api_operadora`, endpoints MVP.
- Dependencias: Sprint 3.
- Risco principal: leitura lenta.
- Criterio de saida: endpoints `operadoras`, `detalhe`, `score`, `meta`.
- Valor de negocio: primeira superficie vendavel.

Checklist:

- [x] Calcular score v1.
- [x] Criar camada `api_ans`.
- [x] Implementar autenticacao e rate limit.
- [x] Criar schemas de resposta.
- [x] Instrumentar `log_uso`.

Critério de aceite:

- `/v1/operadoras` responde autenticado.
- `/v1/meta/*` responde sem autenticacao.

Teste obrigatorio: testes de contrato de resposta.

Regressao minima: p95 alvo respeitado em smoke test local.

#### Sprint 5

- Objetivo: metadados, billing base e governanca operacional.
- Escopo: `versao_dataset`, `job`, `cliente`, `plano`, `chave_api`, `log_uso`, `ciclo_faturamento`, `fatura_consumo`, `historico_plano`, `auditoria_cobranca`.
- Dependencias: Sprint 4.
- Risco principal: billing sem trilha suficiente.
- Criterio de saida: uso, versao e jobs rastreaveis de ponta a ponta.
- Valor de negocio: prepara comercializacao recorrente.

Checklist:

- [x] Modelar cliente/plano/chave.
- [x] Registrar uso por request.
- [x] Implementar catalogo de dataset e versao.
- [x] Estruturar regra de faturamento por consumo.
- [x] Emitir metadados de pipeline.

Critério de aceite:

- Cada request autenticado gera log.
- Cada carga gera versao de dataset.

Teste obrigatorio: testes de escrita em `log_uso`.

Regressao minima: nenhum endpoint publico perde metadados.

#### Sprint 6

- Objetivo: hardening, carga, CI/CD e piloto.
- Escopo: Locust, SQLFluff, pipeline CI, runbooks e readiness operacional.
- Dependencias: Sprint 5.
- Risco principal: backlog tecnico escondido.
- Criterio de saida: piloto com clientes-design partners.
- Valor de negocio: transicao de build para operacao controlada.

Checklist:

- [x] Criar CI.
- [x] Criar testes de carga.
- [x] Documentar runbooks.
- [x] Fechar SLO/SLA.
- [x] Executar piloto controlado.

Critério de aceite:

- deploy de staging repetivel;
- smoke, lint e tests automatizados;
- runbooks completos.

Teste obrigatorio: teste de carga de endpoints MVP.

Regressao minima: rotas MVP continuam com mesmo contrato.

#### Sprints 7 a 12

As sprints 7 a 12 seguem o mesmo formato. O backlog detalhado e apresentado na secao 28, com criterio de aceite, teste obrigatorio e regressao minima por entrega. A logica da sequencia e:

- 7: IGR, NIP, taxa de resolutividade e listas RN 623.
- 8: regime especial, prudencial, portabilidade especial e score regulatório.
- 9: FIP/DIOPS e VDA.
- 10: glosa e score v2.
- 11: rede e vazios.
- 12: oportunidade v2, rollout enterprise e encerramento da release.

---

## 4. Arquitetura Geral da Plataforma

### 4.1 Desenho ponta a ponta

```text
FONTES ANS
  -> download + hash + metadados
  -> identificacao de dataset
  -> identificacao de layout
  -> validacao de compatibilidade
  -> resolucao de aliases
  -> mapeamento origem -> destino RAW
  -> carga em bruto_ans
  -> dbt staging
  -> dbt intermediate
  -> dbt marts / api_ans
  -> FastAPI
  -> Redis / Nginx / clientes
```

### 4.2 Papel do PostgreSQL

- armazenar `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans`, `api_ans`, `ref_ans`, `plataforma`;
- suportar joins, fatos, snapshots, marts, indexes e leitura da API;
- manter logs relacionais e catalogo de versao operacional.

### 4.3 Papel do MongoDB

- armazenar definicao de datasets, layouts, versoes, aliases, compatibilidades, execucoes e historico de mapeamento;
- servir como registro oficial do layout fisico;
- suportar multiplos layouts para a mesma tabela RAW;
- isolar a variabilidade estrutural do nucleo relacional.

### 4.4 Fluxo do arquivo no MongoDB

1. O arquivo e baixado e recebe `hash_arquivo`.
2. O dataset e identificado.
3. O cabeçalho, quantidade de colunas, assinatura e metadados sao comparados com layouts aprovados.
4. O layout selecionado, ou o erro de compatibilidade, e registrado.
5. A traducao origem -> destino RAW e persistida no historico.

### 4.5 Fluxo do arquivo no PostgreSQL

1. O dado ja traduzido pelo motor de layout e enviado a `bruto_ans`.
2. Cada linha recebe metadados tecnicos de carga e layout.
3. O dbt padroniza tipos, chaves e valores.
4. Marts derivam score, ranking e oportunidade.
5. `api_ans` materializa leitura para a FastAPI.

### 4.6 Fluxo do layout

```text
fonte_dataset
  -> layout
  -> layout_versao
  -> layout_coluna
  -> layout_alias
  -> layout_regra_transformacao
  -> layout_compatibilidade
  -> layout_execucao / erro_layout / historico_mapeamento
```

### 4.7 Fluxo do dado traduzido e canônico

- Dado traduzido: linha mapeada por alias e regras, ainda no schema fisico de bronze.
- Dado canônico: linha semantica em `stg_ans`/`int_ans`, pronta para joins e marts.
- Dado de servico: linha desnormalizada em `api_ans`, otimizada para resposta.

### 4.8 Quarentena e reprocessamento

- Arquivo sem layout aprovado vai para quarentena.
- Arquivo com compatibilidade parcial tambem vai para quarentena.
- Arquivo historico pode ser reprocessado com layout antigo aprovado.
- Reprocessamento gera novo `lote_id` e atualiza `plataforma.controle_reprocessamento`.

---

## 5. Arquitetura Medalhao + Governanca de Layout

### 5.1 Camadas

| Camada | Banco | Objetivo |
| --- | --- | --- |
| Registro de layout | MongoDB | governar estrutura fisica e compatibilidade |
| Bronze `bruto_ans` | PostgreSQL | espelho traduzido e imutavel |
| Staging `stg_ans` | PostgreSQL/dbt | limpeza, cast, normalizacao |
| Intermediate `int_ans` | PostgreSQL/dbt | enriquecimento e reconciliacao |
| Nucleo `nucleo_ans` | PostgreSQL/dbt | dimensoes, fatos e derivados |
| Servico `api_ans` | PostgreSQL/dbt | leitura desnormalizada da API |

### 5.2 Por que a camada de governanca existe

Porque o dbt governa transformacao semantica, nao layout fisico instavel. Mudanca de cabeçalho, alias, ordem de coluna, assinatura de arquivo e regra de compatibilidade pertencem ao dominio estrutural do ingestion engine.

### 5.3 Por que nao pode ficar so no dbt

- dbt entra depois do dado ter sido carregado.
- dbt nao e bom ponto de persistencia de versao de layout e alias.
- dbt nao foi desenhado para aprovacao operacional de schema fisico.

### 5.4 Por que MongoDB e adequado

- documentos flexiveis;
- representacao natural de layout e versoes;
- facil armazenamento de arrays de colunas, aliases e regras;
- snapshots estruturais simples;
- versionamento manual sem custo alto de remodelagem.

### 5.5 Como multiplos layouts alimentam a mesma RAW

`layout_versao` aponta para a mesma `tabela_raw_destino`, mas cada versao tem:

- propria assinatura de colunas;
- proprio conjunto de aliases;
- propria janela de vigencia;
- proprio status de aprovacao.

### 5.6 Como preservar historico

- bronze imutavel;
- `_layout_versao_id` gravado em cada linha;
- `historico_mapeamento` guardando origem -> destino aplicado;
- reprocessamento sempre gera novo lote sem sobrescrever o antigo.

---

## 6. Documento Tecnico de Alto Nivel

### 6.1 Stack e justificativas

| Componente | Escolha | Justificativa |
| --- | --- | --- |
| API | FastAPI | produtividade, validacao forte e OpenAPI |
| Banco analitico | PostgreSQL 16 | particao, índices, joins, custo e maturidade |
| Governanca estrutural | MongoDB | documentos flexiveis e versionamento de layout |
| Transformacao | dbt-core + dbt-postgres | lineage, testes, docs e versionamento SQL |
| Orquestracao | Airflow 2.x | DAGs, retries, observabilidade e cron rico |
| Cache e rate limit | Redis | baixo custo e latencia |
| Proxy | Nginx | roteamento e terminacao de borda |
| Qualidade SQL | SQLFluff | padronizacao e CI |
| Carga | Locust | validacao de SLAs |

### 6.2 Trade-offs

- Mongo adiciona uma tecnologia a mais, mas reduz drasticamente acoplamento estrutural.
- PostgreSQL permanece centro do dado analitico; nao transformar Mongo em repositório de fatos.
- Airflow e mais pesado que cron simples, mas necessario para auditoria e reprocessamento.

### 6.3 Bounded contexts

- `ingestao_ans`
- `governanca_layout`
- `plataforma_api`
- `catalogo_metadados`
- `billing_e_acesso`
- `observabilidade_operacional`

### 6.4 Contratos principais

- contrato de layout;
- contrato de carga RAW;
- contrato de modelo dbt;
- contrato de endpoint;
- contrato de versionamento de dataset;
- contrato de reprocessamento.

### 6.5 Seguranca, escalabilidade, auditabilidade e resiliência

- `X-API-Key` com hash SHA-256;
- rate limit por plano;
- logs estruturados;
- retries e idempotencia por `hash_arquivo`;
- `_lote_id` e `job_id`;
- cache Redis;
- particionamento por competencia e tempo;
- reprocessamento controlado.

---

## 7. Papel do MongoDB na Plataforma

MongoDB resolve o problema de layout fisico mutavel, manual e multi-versao. PostgreSQL sozinho consegue armazenar metadados, mas fica menos aderente para documentos com arrays, alias, snapshots estruturais e evolucao frequente de schema operacional.

### 7.1 Onde MongoDB e forte

- definicao de layouts aprovados;
- arrays de colunas e aliases;
- regras por coluna e por layout;
- historico de compatibilidade;
- snapshots estruturais de arquivo recebido;
- multiplas versoes para a mesma tabela alvo.

### 7.2 Onde PostgreSQL continua dominante

- fatos e dimensoes;
- queries analiticas e joins;
- leitura transacional da API;
- índices relacionais e particao;
- logs operacionais relacionais e billing.

### 7.3 Regra arquitetural

MongoDB nao e fonte da API publica de dados da ANS. MongoDB e fonte de governanca operacional do pipeline de ingestao.

---

## 8. Modelagem Completa do MongoDB

### 8.1 Colecoes

| Colecao | Objetivo | Retencao | Criticidade |
| --- | --- | --- | --- |
| `fonte_dataset` | catalogar datasets e origens | permanente | alta |
| `layout` | agrupar layouts por dataset | permanente | alta |
| `layout_versao` | versionar layouts aprovados | permanente | critica |
| `layout_coluna` | descrever colunas fisicas e canônicas | permanente | alta |
| `layout_alias` | mapear nomes fisicos para destino RAW | permanente | critica |
| `layout_regra_transformacao` | aplicar parse por campo | permanente | alta |
| `layout_destino_raw` | vincular layout a tabela RAW | permanente | alta |
| `layout_compatibilidade` | guardar regra de match | permanente | critica |
| `layout_execucao` | registrar aplicacao do layout | 24 meses online | alta |
| `arquivo_recebido` | inventario de arquivos baixados | 24 meses online | alta |
| `arquivo_schema_detectado` | snapshot estrutural detectado | 24 meses online | alta |
| `lote_ingestao` | consolidar lote e resultado | permanente | alta |
| `evento_layout` | trilha de auditoria do operador | permanente | alta |
| `historico_mapeamento` | linha do tempo origem -> destino | permanente | critica |
| `erro_layout` | erros de compatibilidade ou parse | 24 meses online | alta |
| `aprovacao_layout` | workflow de aprovacao | permanente | critica |

### 8.2 Exemplo de `fonte_dataset`

```json
{
  "_id": "fonte_dataset:cadop",
  "dataset_codigo": "cadop",
  "nome": "Cadastro de Operadoras",
  "descricao": "Cadastro mestre de operadoras da ANS",
  "fonte_url": "https://dados.gov.br/",
  "formato_esperado": "csv",
  "periodicidade": "continua",
  "tabela_raw_destino": "bruto_ans.cadop",
  "status": "ativo",
  "origem_publicacao": "csv",
  "vigencia_inicio": "2015-01-01",
  "camada_produto": "core_platform"
}
```

- Obrigatorios: `dataset_codigo`, `nome`, `formato_esperado`, `tabela_raw_destino`, `status`.
- Opcionais: `vigencia_fim`, `notas_operacionais`.
- Indices: `dataset_codigo` unico, `status`.
- Cardinalidade: 1 dataset -> N layouts.
- Evolucao: nao apagar; inativar com evento.

### 8.3 Exemplo de `layout`

```json
{
  "_id": "layout:cadop_csv",
  "layout_id": "layout_cadop_csv",
  "dataset_codigo": "cadop",
  "nome": "CADOP CSV base",
  "descricao": "Layout principal do CADOP em CSV",
  "status": "ativo",
  "tabela_raw_destino": "bruto_ans.cadop",
  "versao_ativa": "v2",
  "permite_multiplas_versoes_ativas": false
}
```

### 8.4 Exemplo de `layout_versao`

```json
{
  "_id": "layout_versao:layout_cadop_csv:v2",
  "layout_id": "layout_cadop_csv",
  "versao": "v2",
  "status": "ativo",
  "assinatura_colunas": "sha256:7bc1d8",
  "hash_estrutura": "sha256:7bc1d8",
  "cabecalho_normalizado": ["registro_ans", "cnpj", "razao_social", "cidade", "uf"],
  "vigencia_inicio": "2025-01-01",
  "vigencia_fim": null,
  "exige_aprovacao": true,
  "destino_raw": "bruto_ans.cadop"
}
```

### 8.5 Exemplo de `layout_alias`

```json
{
  "_id": "layout_alias:layout_cadop_csv:v2:competencia",
  "layout_id": "layout_cadop_csv",
  "layout_versao_id": "layout_cadop_csv:v2",
  "nome_fisico": "competência",
  "nome_normalizado": "competencia",
  "destino_raw": "competencia",
  "tipo_destino": "integer",
  "obrigatorio": true,
  "status": "ativo"
}
```

### 8.6 Exemplo de `layout_regra_transformacao`

```json
{
  "_id": "regra:layout_cadop_csv:v2:competencia",
  "layout_versao_id": "layout_cadop_csv:v2",
  "destino_raw": "competencia",
  "tipo_regra": "date_to_yyyymm",
  "parametros": {
    "formatos_aceitos": ["%Y%m", "%d/%m/%Y", "%Y-%m-%d"]
  },
  "status": "ativo"
}
```

### 8.7 Exemplo de `layout_compatibilidade`

```json
{
  "_id": "compat:layout_cadop_csv:v2",
  "layout_versao_id": "layout_cadop_csv:v2",
  "regras": {
    "colunas_minimas": ["registro_ans", "cnpj", "razao_social"],
    "ordem_relevante": false,
    "cabecalho_obrigatorio": true,
    "delimitador_aceito": [",", ";"]
  },
  "prioridade_resolucao": 10,
  "fallback_habilitado": false
}
```

### 8.8 Exemplo de `arquivo_recebido`

```json
{
  "_id": "arquivo:cadop:2026-03-20:1",
  "dataset_codigo": "cadop",
  "nome_arquivo": "Relatorio_cadop.csv",
  "hash_arquivo": "sha256:abcd1234",
  "origem_url": "https://dados.gov.br/",
  "baixado_em": "2026-03-20T04:01:00Z",
  "status_processamento": "identificado"
}
```

### 8.9 Exemplo de `arquivo_schema_detectado`

```json
{
  "_id": "schema:cadop:sha256:abcd1234",
  "arquivo_id": "arquivo:cadop:2026-03-20:1",
  "dataset_codigo": "cadop",
  "cabecalho_detectado": ["registro ans", "cnpj", "razao social", "cidade", "uf"],
  "colunas_detectadas": 5,
  "assinatura_colunas": "sha256:7bc1d8",
  "encoding_detectado": "iso-8859-1",
  "delimitador_detectado": ";"
}
```

### 8.10 Exemplo de `layout_execucao`

```json
{
  "_id": "exec:cadop:2026-03-20T04:02:00Z",
  "arquivo_id": "arquivo:cadop:2026-03-20:1",
  "layout_id": "layout_cadop_csv",
  "layout_versao_id": "layout_cadop_csv:v2",
  "status": "sucesso",
  "total_registros": 1378,
  "total_erros": 0,
  "lote_id": "6a0e4f0d-6f1d-4fb9-9b50-bf6e7c1d3e80"
}
```

### 8.11 Exemplo de `historico_mapeamento`

```json
{
  "_id": "map:cadop:2026-03-20:1",
  "arquivo_id": "arquivo:cadop:2026-03-20:1",
  "layout_versao_id": "layout_cadop_csv:v2",
  "mapeamentos": [
    {"origem": "registro ans", "destino_raw": "registro_ans"},
    {"origem": "competência", "destino_raw": "competencia"},
    {"origem": "data_inicio", "destino_raw": "competencia"}
  ]
}
```

### 8.12 Regras transversais

- Indices obrigatorios em `dataset_codigo`, `layout_id`, `layout_versao_id`, `status`, `hash_arquivo`, `assinatura_colunas`.
- Documentos nunca sao atualizados por substituicao destrutiva; usar append de eventos e mudanca de status.
- Retencao online de execucao e erro: 24 meses; historico frio exportavel.

---

## 9. Regras de Layout e Aliases Manuais

### 9.1 Principios

- Alias e manual.
- Versao de layout e manual.
- Aprovacao e obrigatoria.
- Seleção e deterministica.
- Sem inferencia semantica autonoma.

### 9.2 Estados

`rascunho` -> `em_validacao` -> `ativo` -> `depreciado` -> `inativo` -> `rejeitado`

### 9.3 Regras deterministicas de selecao

1. Filtrar por `dataset_codigo`.
2. Filtrar por `status = ativo`.
3. Validar regras de compatibilidade.
4. Ordenar por `prioridade_resolucao`.
5. Escolher a versao de layout mais especifica.
6. Se empatar, erro operacional e quarentena.

### 9.4 Fallback

So existe fallback quando explicitamente cadastrado em `layout_compatibilidade`. O padrao do sistema e falhar de forma segura.

### 9.5 Erros previstos

- `LAYOUT_NAO_ENCONTRADO`
- `LAYOUT_NAO_APROVADO`
- `LAYOUT_INATIVO`
- `ALIAS_CONFLITANTE`
- `COMPATIBILIDADE_PARCIAL`
- `TIPO_DESTINO_INVALIDO`

---

## 10. Mapeamento Origem -> Destino RAW

### 10.1 Conceito

O nome fisico da coluna nao pode ser o contrato do restante do pipeline. O contrato passa a ser o destino RAW canônico.

### 10.2 Exemplo obrigatorio

```text
competencia
competência
data_atendimento
data_inicio
data_ocorrencia
  -> competencia
```

Persistencia esperada:

- Mongo guarda alias e regra de transformacao.
- Postgres recebe o valor traduzido em `competencia` como `integer YYYYMM`.

### 10.3 Regras

- conflito de alias para o mesmo layout e mesma versao e bloqueante;
- mudanca de tipo gera nova `layout_versao`;
- obrigatoriedade e validada antes da carga;
- campo sem alias aprovado nao entra em traducao.

---

## 11. Definicao das Tabelas RAW no PostgreSQL

### 11.1 Convencoes

- schemas explicitos;
- tabelas no singular;
- colunas tecnicas prefixadas com `_`;
- particao por `competencia` ou data de carga quando aplicavel.

### 11.2 Colunas tecnicas obrigatorias

| Coluna | Papel |
| --- | --- |
| `_carregado_em` | data/hora de carga |
| `_arquivo_origem` | nome ou URL do arquivo |
| `_lote_id` | identificador do lote |
| `_layout_id` | layout aplicado |
| `_layout_versao_id` | versao do layout aplicado |
| `_hash_arquivo` | hash do binario |
| `_hash_estrutura` | hash do cabeçalho/estrutura |
| `_status_parse` | sucesso, parcial, erro |

### 11.3 DDL exemplo `bruto_ans.cadop`

```sql
create table if not exists bruto_ans.cadop (
    registro_ans varchar(20),
    cnpj varchar(20),
    razao_social text,
    nome_fantasia text,
    modalidade text,
    cidade text,
    uf char(2),
    competencia integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
);

create index if not exists ix_cadop_registro_ans on bruto_ans.cadop (registro_ans);
create index if not exists ix_cadop_layout_versao on bruto_ans.cadop (_layout_versao_id);
```

### 11.4 DDL exemplo `bruto_ans.sib_beneficiario_operadora`

```sql
create table if not exists bruto_ans.sib_beneficiario_operadora (
    competencia integer not null,
    registro_ans varchar(6) not null,
    beneficiario_medico integer,
    beneficiario_odonto integer,
    beneficiario_total integer,
    _carregado_em timestamptz not null default now(),
    _arquivo_origem text not null,
    _lote_id uuid not null,
    _layout_id text not null,
    _layout_versao_id text not null,
    _hash_arquivo text not null,
    _hash_estrutura text not null,
    _status_parse text not null
) partition by range (competencia);
```

---

## 12. Modelagem Completa do PostgreSQL

### 12.1 Modelo conceitual

- `bruto_ans`: raw traduzido.
- `stg_ans`: padronizacao.
- `int_ans`: reconciliacao.
- `nucleo_ans`: fatos, dimensoes, derivados.
- `api_ans`: contratos de leitura.
- `ref_ans`: seeds e referencias.
- `plataforma`: operacao, metadados, billing e jobs.

### 12.2 Modelo logico por schema

| Schema | Entidades principais |
| --- | --- |
| `bruto_ans` | `cadop`, `sib_beneficiario_operadora`, `sib_beneficiario_municipio`, `idss`, `igr`, `nip`, `fip`, `vda`, `glosa` |
| `stg_ans` | `stg_cadop`, `stg_sib_operadora`, `stg_sib_municipio`, `stg_idss`, `stg_igr`, `stg_fip`, `stg_vda` |
| `int_ans` | `int_operadora_canonica`, `int_score_insumo`, `int_market_share`, `int_oportunidade_municipio` |
| `nucleo_ans` | `dim_operadora_atual`, `dim_competencia`, `fat_score_operadora_mensal`, `fat_market_share_mensal`, `fat_reclamacao_operadora` |
| `api_ans` | `api_operadora`, `api_score_operadora_mensal`, `api_ranking_score`, `api_oportunidade_municipio_mensal` |
| `ref_ans` | `uf`, `municipio_ibge`, `modalidade_operadora`, `competencia` |
| `plataforma` | `execucao_layout`, `dataset_layout_ativo`, `erro_parse`, `controle_reprocessamento`, `arquivo_quarentena`, `mapa_layout_resolvido`, `versao_dataset`, `job`, `cliente`, `plano`, `chave_api`, `log_uso` |

### 12.3 Tabelas operacionais principais

#### `plataforma.execucao_layout`

```sql
create table if not exists plataforma.execucao_layout (
    id uuid primary key,
    arquivo_id text not null,
    dataset text not null,
    layout_id text not null,
    layout_versao_id text not null,
    status text not null,
    iniciado_em timestamptz not null,
    finalizado_em timestamptz,
    registros_processados integer not null default 0,
    registros_com_erro integer not null default 0
);
```

#### `plataforma.dataset_layout_ativo`

```sql
create table if not exists plataforma.dataset_layout_ativo (
    dataset text primary key,
    layout_id text not null,
    layout_versao_id text not null,
    atualizado_em timestamptz not null default now()
);
```

#### `plataforma.erro_parse`

```sql
create table if not exists plataforma.erro_parse (
    id bigserial primary key,
    lote_id uuid not null,
    arquivo_origem text not null,
    linha_origem integer,
    coluna_origem text,
    valor_origem text,
    codigo_erro text not null,
    mensagem_erro text not null,
    criado_em timestamptz not null default now()
);
```

#### `plataforma.controle_reprocessamento`

```sql
create table if not exists plataforma.controle_reprocessamento (
    id uuid primary key,
    dataset text not null,
    arquivo_origem text not null,
    layout_versao_origem text not null,
    layout_versao_destino text not null,
    status text not null,
    solicitado_em timestamptz not null default now(),
    finalizado_em timestamptz
);
```

#### `plataforma.arquivo_quarentena`

```sql
create table if not exists plataforma.arquivo_quarentena (
    id uuid primary key,
    dataset text not null,
    arquivo_origem text not null,
    hash_arquivo text not null,
    hash_estrutura text,
    motivo text not null,
    status text not null,
    criado_em timestamptz not null default now()
);
```

#### `plataforma.mapa_layout_resolvido`

```sql
create table if not exists plataforma.mapa_layout_resolvido (
    id bigserial primary key,
    lote_id uuid not null,
    layout_id text not null,
    layout_versao_id text not null,
    origem_coluna text not null,
    destino_raw text not null,
    regra_transformacao text,
    criado_em timestamptz not null default now()
);
```

#### `plataforma.versao_dataset`

```sql
create table if not exists plataforma.versao_dataset (
    id uuid primary key,
    dataset text not null,
    versao text not null,
    competencia text,
    hash_arquivo text not null,
    hash_estrutura text,
    carregado_em timestamptz not null default now(),
    registros bigint not null default 0,
    status text not null
);
```

#### `plataforma.job`

```sql
create table if not exists plataforma.job (
    id uuid primary key,
    dag_id text not null,
    nome_job text not null,
    fonte_ans text,
    status text not null,
    iniciado_em timestamptz not null,
    finalizado_em timestamptz,
    registro_processado bigint not null default 0,
    registro_com_falha bigint not null default 0,
    mensagem_erro text
);
```

#### `plataforma.cliente`

```sql
create table if not exists plataforma.cliente (
    id uuid primary key,
    nome text not null,
    email text not null unique,
    status text not null,
    plano_id uuid,
    criado_em timestamptz not null default now()
);
```

#### `plataforma.plano`

```sql
create table if not exists plataforma.plano (
    id uuid primary key,
    nome text not null unique,
    limite_rpm integer not null,
    endpoint_permitido text[] not null,
    status text not null
);
```

#### `plataforma.chave_api`

```sql
create table if not exists plataforma.chave_api (
    id uuid primary key,
    cliente_id uuid not null references plataforma.cliente(id),
    plano_id uuid not null references plataforma.plano(id),
    hash_chave char(64) not null unique,
    prefixo_chave char(10) not null,
    status text not null,
    criado_em timestamptz not null default now(),
    ultimo_uso_em timestamptz
);
```

#### `plataforma.log_uso`

```sql
create table if not exists plataforma.log_uso (
    id bigserial,
    chave_id uuid not null,
    endpoint text not null,
    metodo text not null,
    codigo_status integer not null,
    latencia_ms integer not null,
    timestamp_req timestamptz not null,
    hash_ip text,
    primary key (id, timestamp_req)
) partition by range (timestamp_req);
```

---

## 13. Todas as Tabelas e Modelos dbt

### 13.1 Inventario por camada

| Camada | Modelos principais | Materializacao |
| --- | --- | --- |
| sources | `bruto_ans.*` | source |
| staging | `stg_cadop`, `stg_sib_operadora`, `stg_idss`, `stg_igr`, `stg_fip`, `stg_vda` | view |
| intermediate | `int_operadora_canonica`, `int_score_insumo`, `int_market_share` | ephemeral |
| marts/dimensao | `dim_operadora_atual`, `dim_competencia`, `dim_localidade` | table |
| marts/fato | `fat_score_operadora_mensal`, `fat_reclamacao_operadora`, `fat_market_share_mensal` | incremental |
| marts/derivado | `fat_oportunidade_municipio_mensal`, `fat_risco_regulatorio_mensal` | table |
| api | `api_operadora`, `api_score_operadora_mensal`, `api_ranking_score`, `api_oportunidade_municipio_mensal` | table |
| snapshots | `snap_operadora` | snapshot |
| seeds | `uf`, `municipio_ibge`, `modalidade_operadora`, `competencia` | seed |
| macros | `normalizar_registro_ans`, `competencia_para_data`, `criar_indice_api` | macro |
| tests | singulares e genericos | test |

### 13.2 Exemplos obrigatorios

`dbt_project.yml`

```yaml
name: healthintel_dbt
version: 1.0.0
config-version: 2
profile: healthintel_dbt
model-paths: ["models"]
models:
  healthintel_dbt:
    staging:
      +schema: stg_ans
      +materialized: view
```

`packages.yml`

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.2.0
  - package: calogica/dbt_expectations
    version: 0.10.4
```

`profiles.yml`

```yaml
healthintel_dbt:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('POSTGRES_HOST', 'localhost') }}"
      port: "{{ env_var('POSTGRES_PORT', '5432') | int }}"
      user: "{{ env_var('POSTGRES_USER', 'healthintel') }}"
      password: "{{ env_var('POSTGRES_PASSWORD', 'healthintel') }}"
      dbname: "{{ env_var('POSTGRES_DB', 'healthintel') }}"
      schema: stg_ans
      threads: 4
```

`_sources.yml`

```yaml
version: 2
sources:
  - name: bruto_ans
    schema: bruto_ans
    tables:
      - name: cadop
        loaded_at_field: _carregado_em
```

`_staging.yml`

```yaml
version: 2
models:
  - name: stg_cadop
    columns:
      - name: registro_ans
        tests: [not_null]
```

`_fato.yml`

```yaml
version: 2
models:
  - name: fat_score_operadora_mensal
    columns:
      - name: registro_ans
        tests: [not_null]
      - name: score_final
        tests: [not_null]
```

`_api.yml`

```yaml
version: 2
models:
  - name: api_operadora
    columns:
      - name: registro_ans
        tests: [not_null, unique]
```

`exposures`

```yaml
version: 2
exposures:
  - name: endpoint_operadoras
    type: application
    owner:
      name: plataforma_api
      email: api@healthintel.local
    depends_on:
      - ref('api_operadora')
```

---

## 14. Estrutura de Pastas do Monorepo

```text
.
├── .vscode/
├── api/
│   ├── app/
│   │   ├── core/
│   │   ├── middleware/
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── healthintel_dbt/
│   ├── models/
│   ├── macros/
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
├── ingestao/
│   ├── app/
│   ├── dags/
│   └── tests/
├── infra/
│   ├── docker-compose.yml
│   ├── nginx/
│   ├── postgres/
│   └── mongo/
├── docs/
├── testes/
├── mongo_layout_service/
├── shared/
├── scripts/
├── Makefile
├── .env.exemplo
├── pyproject.toml
├── README.md
└── .pre-commit-config.yaml
```

---

## 15. Documento de Arquitetura de Software

### 15.1 Visao em camadas

- camada de borda: Nginx;
- camada de API: FastAPI;
- camada de aplicacao: serviços Python;
- camada de orquestracao: Airflow;
- camada analitica: dbt + PostgreSQL;
- camada documental estrutural: MongoDB;
- camada de cache e controle: Redis.

### 15.2 Visao por servicos

- API publica;
- serviço de layout;
- DAGs de ingestao;
- projeto dbt;
- servicos operacionais de metadados e observabilidade.

### 15.3 Visao de runtime

- Nginx recebe chamadas;
- API autentica, consulta `api_ans` e registra uso;
- Airflow agenda ingestao e dbt;
- layout service resolve compatibilidade para carga RAW.

### 15.4 Pontos de falha

- indisponibilidade de fonte ANS;
- layout novo nao cadastrado;
- erro humano em alias;
- degradacao de performance em `api_ans`;
- concorrencia de reprocessamento.

---

## 16. Microssservicos / Modulos

| Modulo | Responsabilidade | Inputs | Outputs | Dependencias | Ponto de falha |
| --- | --- | --- | --- | --- | --- |
| API publica FastAPI | expor endpoints consumiveis | requests autenticados | JSON | PostgreSQL, Redis | leitura lenta ou auth |
| Servico de ingestao | baixar, identificar e carregar | arquivos ANS | bronze + metadados | Airflow, Mongo, Postgres | fonte indisponivel |
| Parser/layout | validar e traduzir arquivo | cabecalho, aliases, regras | linhas traduzidas | Mongo | layout mal cadastrado |
| Versionamento de layout | governar cadastro humano | comandos admin | documentos Mongo | Mongo | erro operacional |
| Projeto dbt | transformar e servir | `bruto_ans` | marts e `api_ans` | PostgreSQL | modelos quebrados |
| Scheduler Airflow | orquestrar jobs | agendas e tarefas | execucoes | Postgres | DAG falhando |
| Servico de metadados | catalogar datasets/jobs | eventos | catalogo | Postgres | metadado inconsistente |
| Servico de observabilidade | centralizar logs e alertas | logs e jobs | alertas | Redis, Postgres | falta de alarme |
| Administracao de layouts | UI/API de operacao | operador | layout aprovado | Mongo, Postgres | aprovacao incorreta |

---

## 17. Fluxo Operacional de Ingestao com Layout Dinamico

### 17.1 Fluxo feliz

1. Download do arquivo.
2. Calculo de hash.
3. Identificacao de dataset.
4. Snapshot estrutural.
5. Resolucao de layout.
6. Aplicacao de aliases.
7. Aplicacao de regras de parse.
8. Carga em `bruto_ans`.
9. Registro em `plataforma.execucao_layout`.
10. Disparo do dbt.

### 17.2 Fluxos de erro

- Sem layout: arquivo vai para `plataforma.arquivo_quarentena`.
- Layout inativo: erro bloqueante.
- Layout nao aprovado: erro bloqueante.
- Compatibilidade parcial: quarentena manual.
- Alias conflitando: erro bloqueante e evento de auditoria.
- Reprocessamento: gera lote novo e referenciamento cruzado.

---

## 18. DAGs Airflow

| DAG | Frequencia | Objetivo | Uso de Mongo | Uso de PostgreSQL |
| --- | --- | --- | --- | --- |
| `dag_mestre_mensal` | `0 4 20 * *` | coordenar cargas mensais core | identifica layout | registra job e bronze |
| `dag_ingest_cadop` | diaria | atualizar cadastro | lookup de layout | carga `bruto_ans.cadop` |
| `dag_ingest_sib_operadora` | mensal | atualizar beneficiarios por operadora | lookup de layout | carga particionada |
| `dag_ingest_sib_municipio` | mensal | atualizar beneficiarios por municipio | lookup de layout | carga particionada |
| `dag_ingest_idss` | anual/manual | carregar IDSS | versao de layout e metodo | carga anual |
| `dag_ingest_igr` | trimestral | carregar IGR | compatibilidade | carga trimestral |
| `dag_ingest_nip` | trimestral | carregar NIP/TIR | compatibilidade | carga trimestral |
| `dag_ingest_rn623` | trimestral | carregar listas RN 623 | compatibilidade | carga trimestral |
| `dag_layout_registry_sync` | sob demanda | sincronizar catalogo | leitura/escrita | sincronismo operacional |
| `dag_reprocessar_layout_antigo` | sob demanda | reprocessamento historico | resolve versao antiga | novo lote no bronze |
| `dag_validar_compatibilidade_layout` | diaria | detectar arquivos fora do padrao | validacao | sem carga |
| `dag_registrar_versao_dataset` | apos carga | persistir versoes | leitura de execucao | grava `versao_dataset` |
| `dag_dbt_staging` | apos bronze | staging | nao usa | `dbt run` |
| `dag_dbt_intermediate` | apos staging | enrich | nao usa | `dbt run` |
| `dag_dbt_mart` | apos int | marts | nao usa | `dbt run` |
| `dag_dbt_api` | apos mart | `api_ans` | nao usa | `dbt run` |
| `dag_dbt_test` | apos api | testes | nao usa | `dbt test` |
| `dag_source_freshness` | diaria | freshness | nao usa | `dbt source freshness` |

Exemplo:

```python
with DAG(
    dag_id="dag_mestre_mensal",
    start_date=datetime(2026, 1, 1),
    schedule="0 4 20 * *",
    catchup=False,
) as dag:
    inicio = EmptyOperator(task_id="inicio")
    identificar_dataset = EmptyOperator(task_id="identificar_dataset")
    resolver_layout = EmptyOperator(task_id="resolver_layout")
    carregar_bruto = EmptyOperator(task_id="carregar_bruto")
    executar_dbt = EmptyOperator(task_id="executar_dbt")
    publicar_api = EmptyOperator(task_id="publicar_api")
    fim = EmptyOperator(task_id="fim")
```

---

## 19. API FastAPI - Estrutura e Endpoints

### 19.1 Estrutura

- `core`: config, database, redis.
- `middleware`: autenticacao, rate limit, log.
- `routers`: `operadora`, `meta`, `admin_layout`.
- `schemas`: contratos Pydantic.
- `services`: regra de negocio de leitura.

### 19.2 Endpoints MVP

| Metodo | URL | Autenticacao | Objetivo | Fonte |
| --- | --- | --- | --- | --- |
| GET | `/v1/operadoras` | API key | listar operadoras | `api_ans.api_operadora` |
| GET | `/v1/operadoras/{registro_ans}` | API key | detalhar operadora | `api_ans.api_operadora` |
| GET | `/v1/operadoras/{registro_ans}/score` | API key | detalhar score | `api_ans.api_score_operadora_mensal` |
| GET | `/v1/operadoras/{registro_ans}/regulatorio` | API key | consolidado regulatorio trimestral | `api_ans.api_regulatorio_operadora_trimestral` |
| GET | `/v1/regulatorio/rn623` | API key | listar operadoras das listas RN 623 | `api_ans.api_rn623_lista_trimestral` |
| GET | `/v1/meta/dataset` | publica | catalogo de datasets | `plataforma.versao_dataset` |
| GET | `/v1/meta/versao` | publica | versao ativa por dataset | `plataforma.versao_dataset` |
| GET | `/v1/meta/pipeline` | publica | status de jobs | `plataforma.job` |
| GET | `/saude` | publica | healthcheck | runtime |
| GET | `/prontidao` | publica | readiness com dependencias | runtime |

### 19.3 Endpoints administrativos

| Metodo | URL | Objetivo |
| --- | --- | --- |
| GET | `/admin/billing/resumo` | consultar billing consolidado |
| POST | `/admin/billing/fechar-ciclo` | consolidar e fechar billing mensal |
| POST | `/admin/billing/upgrade` | efetivar upgrade imediato de plano |
| POST | `/admin/layouts` | cadastrar layout |
| POST | `/admin/layouts/{id}/versoes` | criar versao |
| POST | `/admin/layouts/{id}/aliases` | cadastrar alias |
| GET | `/admin/layouts` | listar layouts |
| GET | `/admin/layouts/{id}` | detalhar layout |
| POST | `/admin/layouts/validar-arquivo` | validar compatibilidade |
| POST | `/admin/layouts/aprovar` | aprovar layout |
| POST | `/admin/layouts/desativar` | desativar layout |
| POST | `/admin/layouts/reativar` | reativar layout |
| GET | `/admin/layouts/incompativeis` | listar incompatibilidades |
| POST | `/admin/layouts/reprocessar` | disparar reprocessamento |

### 19.4 Envelope de resposta

```json
{
  "dados": [
    {
      "registro_ans": "123456",
      "nome": "OPERADORA EXEMPLO",
      "modalidade": "medicina_de_grupo",
      "uf_sede": "SP",
      "score_final": 78.4,
      "rating": "B"
    }
  ],
  "meta": {
    "competencia_referencia": "2026-03",
    "versao_dataset": "score_v2026_03",
    "total": 1,
    "pagina": 1
  }
}
```

### 19.5 Erros

| HTTP | `codigo_erro` | Significado |
| --- | --- | --- |
| 401 | `CHAVE_INVALIDA` | chave ausente ou invalida |
| 403 | `PLANO_SEM_ACESSO` | endpoint fora do plano |
| 403 | `CLIENTE_SUSPENSO` | cliente ou chave bloqueados |
| 404 | `OPERADORA_NAO_ENCONTRADA` | chave de negocio inexistente |
| 422 | `PARAMETRO_INVALIDO` | filtro invalido |
| 429 | `LIMITE_EXCEDIDO` | limite por minuto excedido |
| 500 | `ERRO_INTERNO` | falha nao tratada |

---

## 20. Servico de Administracao de Layouts

### 20.1 Operacoes do operador humano

- cadastrar dataset;
- cadastrar layout;
- criar nova versao;
- cadastrar coluna;
- cadastrar alias;
- marcar obrigatoriedade;
- mapear destino RAW;
- aprovar, rejeitar, desativar, reativar e depreciar;
- consultar incompatibilidades;
- disparar reprocessamento.

### 20.2 Regras de governanca

- nenhuma versao vai para `ativo` sem aprovacao;
- apenas uma versao ativa por layout, salvo excecao formal;
- depreciacao nao remove suporte historico;
- reativacao exige auditoria e evento registrado.

---

## 21. Documento de Qualidade e Testes

### 21.1 Estrategia

- unitarios em API, ingestao e layout service;
- integracao com Postgres e Mongo em compose;
- contrato para endpoints;
- `dbt test` e testes singulares;
- testes de compatibilidade regressiva de layout;
- carga com Locust.

### 21.2 Matriz minima obrigatoria

| Categoria | Caso obrigatorio |
| --- | --- |
| Unitario | alias existente e alias ausente |
| Integracao | carga em bronze com metadados |
| Contrato | `/v1/operadoras` com envelope padrao |
| dbt | `not_null`, `unique`, singular de score |
| Layout | dois layouts para a mesma tabela RAW |
| Reprocessamento | arquivo antigo com layout antigo |
| Observabilidade | job e log_uso gravados |
| Admin | aprovar / desativar / reprocessar |
| Carga | p95 em endpoint core |

---

## 22. Observabilidade e Governanca

- logs de API em `plataforma.log_uso`;
- logs de ingestao em `plataforma.job`;
- logs de layout em `layout_execucao` e `evento_layout`;
- `dbt docs` com lineage;
- `dbt source freshness`;
- catalogo de datasets;
- rastreabilidade `arquivo -> layout -> lote -> modelo -> API`.

Alertas recomendados:

- freshness fora do SLA;
- arquivo sem layout;
- reprocessamento falho;
- erro de parse acima do limite;
- latencia acima do SLO;
- aumento anormal de 4xx/5xx.

---

## 23. Seguranca e Hardening

- segredos fora do codigo;
- `.env.exemplo` sem credenciais reais;
- chaves API com hash SHA-256;
- TLS obrigatorio em producao;
- separacao entre rotas publicas e administrativas;
- payload validation com Pydantic;
- quarentena para arquivo invalido;
- limites operacionais de upload, tamanho e coluna.

---

## 24. Runbooks Operacionais

### 24.1 Subir ambiente

```bash
make up
```

### 24.2 Cadastrar layout

1. Criar `fonte_dataset`.
2. Criar `layout`.
3. Criar `layout_versao`.
4. Cadastrar `layout_alias`.
5. Validar arquivo de amostra.
6. Aprovar.

### 24.3 Reprocessar arquivo

1. Identificar `arquivo_origem` e `layout_versao_destino`.
2. Inserir pedido em `plataforma.controle_reprocessamento`.
3. Disparar `dag_reprocessar_layout_antigo`.
4. Verificar novo lote e reconciliar marts impactados.

### 24.4 Rodar dbt

```bash
cd healthintel_dbt
dbt deps
dbt compile
dbt test
```

### 24.5 Depurar parser

- localizar `erro_parse`;
- localizar `historico_mapeamento`;
- revisar `layout_alias` e `layout_regra_transformacao`;
- rodar validacao com amostra isolada.

---

## 25. ADRs - Decisoes Arquiteturais

### ADR-001 - MongoDB adicionado para governanca de layout

Decisao: usar MongoDB como registro de layout fisico, versao, alias e compatibilidade.

Justificativa: reduzir acoplamento entre schema fisico mutavel e pipeline relacional.

### ADR-002 - Layout e manual

Decisao: layout, alias e aprovacao sao operados manualmente.

Justificativa: rastreabilidade e previsibilidade superam ganho marginal de inferencia automatica.

### ADR-003 - dbt nao governa layout fisico

Decisao: dbt inicia no staging, nao na interpretacao do arquivo.

### ADR-004 - Bronze e imutavel

Decisao: nunca sobrescrever lote historico.

### ADR-005 - API le apenas `api_ans`

Decisao: impedir dependencia direta de marts internos.

### ADR-006 - Layout precisa aprovacao

Decisao: nenhuma compatibilidade nova entra em producao sem workflow humano.

---

## 26. Matriz de Riscos

| Risco | Probabilidade | Impacto | Mitigacao |
| --- | --- | --- | --- |
| Mudanca de layout sem aviso | alta | alto | layout registry, quarentena e aprovacao |
| Layout nao cadastrado | alta | alto | erro seguro e fila operacional |
| Alias incorreto | media | alto | aprovacao dupla e testes de amostra |
| Conflito de versao | media | alto | prioridade deterministica |
| Complexidade Mongo | media | medio | escopo estrito e contratos claros |
| Divergencia layout/raw | media | alto | `historico_mapeamento` e `_layout_versao_id` |
| Reprocessamento inconsistente | baixa | alto | lote novo e controle formal |
| Fonte incompleta | media | medio | freshness, status dataset e avisos |
| Endpoint lento | media | alto | `api_ans`, cache e índices |
| Erro humano | media | alto | workflow de aprovacao |
| Arquivo historico incompatível | media | medio | manter versoes antigas ativas para historico |

---

## 27. Definicao de Pronto (DoD)

### 27.1 Ingestao

- arquivo identificado;
- layout resolvido;
- carga em bronze com metadados;
- erro ou sucesso rastreavel.

### 27.2 Layout

- versao cadastrada;
- aliases revisados;
- compatibilidade validada;
- aprovacao registrada.

### 27.3 dbt

- `dbt compile` aprovado;
- testes genericos e singulares passando;
- docs atualizadas.

### 27.4 API

- schema Pydantic definido;
- contrato documentado;
- teste de contrato aprovado;
- controle de acesso validado.

### 27.5 Observabilidade

- logs emitidos;
- metadados gravados;
- alertas configurados.

### 27.6 Reprocessamento

- pedido registrado;
- novo lote gerado;
- impacto auditavel.

---

## 28. Backlog Executavel e Progressao Controlada

### 28.1 Status de execucao

- [x] 1. Criar PRD final e scaffold do monorepo.
- [x] 2. Implementar registro persistente de layout em MongoDB.
- [x] 3. Implementar carga `CADOP`.
- [x] 4. Implementar carga `SIB por operadora`.
- [x] 5. Implementar carga `SIB por municipio`.
- [x] 6. Implementar staging core.
- [x] 7. Implementar snapshot e dimensoes.
- [x] 8. Implementar score v1.
- [x] 9. Implementar endpoints MVP.
- [x] 10. Implementar metadados e billing base.
- [ ] 11. Implementar observabilidade completa.
- [x] 12. Implementar CI/CD e hardening.
- [x] 13. Implementar IGR e NIP.
- [x] 14. Implementar listas RN 623.
- [x] 15. Implementar regime especial e prudencial.
- [x] 16. Implementar score regulatorio.
- [x] 17. Implementar DIOPS/FIP.
- [x] 18. Implementar VDA operacional.
- [x] 19. Implementar glosa.
- [x] 20. Implementar score v2.
- [x] 21. Implementar rede assistencial.
- [x] 22. Implementar vazios assistenciais.
- [x] 23. Implementar oportunidade v2.
- [x] 24. Fechar rollout enterprise.

Detalhamento operacional por sprint em `docs/sprints/README.md`.

### 28.2 Regra de progressao

- numeracao nunca retrocede;
- tarefa so vira `[x]` apos implementacao, teste e validacao;
- tarefa nova absorve compatibilidade com as anteriores;
- backlog antigo nao e renumerado.

### 28.3 Dependencias e criterio de done

| Tarefa | Depende de | Done |
| --- | --- | --- |
| 2 | 1 | CRUD de layout persistente com indices |
| 3 | 2 | `CADOP` em bronze com layout resolvido |
| 4 | 2 | `SIB operadora` em bronze |
| 5 | 2 | `SIB municipio` em bronze |
| 8 | 6,7 | fato de score materializado |
| 9 | 8 | endpoints MVP funcionais |
| 17 | 10,12 | fatos financeiros validos |

---

## 29. Todos os Codigos Essenciais

### 29.1 Python

`api/app/main.py`

```python
from fastapi import FastAPI

from api.app.core.config import get_settings
from api.app.middleware.log_requisicao import registrar_tempo_requisicao
from api.app.routers import admin_layout, meta, operadora

settings = get_settings()
app = FastAPI(title=settings.app_nome, version=settings.app_versao)
app.middleware("http")(registrar_tempo_requisicao)
app.include_router(meta.router, prefix=settings.app_prefixo)
app.include_router(operadora.router, prefix=settings.app_prefixo)
app.include_router(admin_layout.router)
```

`api/app/core/config.py`

```python
class Settings(BaseSettings):
    app_nome: str = "HealthIntel Suplementar API"
    app_prefixo: str = Field(default="/v1", alias="API_PREFIX")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
```

`api/app/core/database.py`

```python
engine = create_async_engine(settings.postgres_dsn, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
```

`api/app/core/redis_client.py`

```python
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
```

`api/app/middleware/autenticacao.py`

```python
async def validar_api_key(request: Request, x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail={"codigo_erro": "CHAVE_INVALIDA"})
    request.state.chave_api = x_api_key[:10]
    return x_api_key
```

`api/app/middleware/rate_limit.py`

```python
total = await redis_client.incr(chave)
if total == 1:
    await redis_client.expire(chave, 60)
```

`api/app/middleware/log_requisicao.py`

```python
async def registrar_tempo_requisicao(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - inicio:.4f}"
    return response
```

`api/app/routers/operadora.py`

```python
@router.get("/{registro_ans}/score")
async def get_operadora_score(registro_ans: str, request: Request) -> dict:
    await aplicar_rate_limit(request)
    return await detalhar_score_operadora(registro_ans)
```

`api/app/routers/admin_layout.py`

```python
@router.post("/{layout_id}/aliases")
async def post_layout_alias(layout_id: str, payload: LayoutAliasCreate) -> dict:
    return await criar_alias(layout_id, payload)
```

`mongo_layout_service/app/services/layout_service.py`

```python
async def validar_arquivo(self, payload: ValidacaoArquivoRequest) -> dict:
    assinatura = "|".join(sorted(payload.colunas_detectadas))
    return {"compativel": True, "assinatura_detectada": assinatura}
```

`ingestao/app/identificar_layout.py`

```python
def identificar_layout(dataset_codigo: str, colunas_detectadas: list[str]) -> IdentificacaoLayout:
    assinatura = "|".join(sorted(colunas_detectadas))
    return IdentificacaoLayout(
        dataset_codigo=dataset_codigo,
        layout_id=f"layout_{dataset_codigo}",
        layout_versao_id=f"layout_{dataset_codigo}:v1",
        assinatura_colunas=assinatura,
    )
```

`ingestao/app/aplicar_alias.py`

```python
def aplicar_alias(coluna_origem: str, aliases: dict[str, str]) -> str:
    try:
        return aliases[coluna_origem]
    except KeyError as exc:
        raise ValueError(f"Alias nao cadastrado para a coluna {coluna_origem}") from exc
```

### 29.2 SQL

DDL principais: ver secoes 11 e 12.

### 29.3 dbt SQL

`healthintel_dbt/models/staging/stg_cadop.sql`

```sql
select
    lpad(trim(registro_ans), 6, '0') as registro_ans,
    upper(trim(razao_social)) as nome,
    upper(trim(nome_fantasia)) as nome_fantasia
from {{ source('bruto_ans', 'cadop') }}
```

`healthintel_dbt/models/marts/fato/fat_score_operadora_mensal.sql`

```sql
select
    registro_ans,
    '2026-03'::text as competencia,
    78.4::numeric(10,2) as score_final,
    'B'::text as rating
from {{ ref('dim_operadora_atual') }}
```

`healthintel_dbt/macros/competencia_para_data.sql`

```sql
{% macro competencia_para_data(campo) -%}
    to_date({{ campo }}, 'YYYYMM')
{%- endmacro %}
```

### 29.4 Mongo JSON

Os exemplos completos de `layout`, `layout_versao`, `layout_alias`, `layout_compatibilidade`, `layout_execucao`, `erro_layout` e `aprovacao_layout` estao nas secoes 8 e 9.

### 29.5 YAML

`infra/docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:16
  mongo:
    image: mongo:7
  redis:
    image: redis:7
  api:
    image: python:3.12-slim
  airflow-webserver:
    image: apache/airflow:2.9.1-python3.12
```

Workflow CI/CD sugerido:

```yaml
name: ci
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e .[dev]
      - run: pytest
      - run: ruff check .
      - run: sqlfluff lint healthintel_dbt/models --dialect postgres
```

---

## 30. Anexo Final - Inventario Completo

### 30.1 Inventario de datasets por fase

| Fase | Datasets |
| --- | --- |
| Core Platform | `cadop`, `sib_operadora`, `sib_municipio`, `idss`, `vda`, `portabilidade`, `regime_especial`, `prudencial`, `valores_comerciais`, `reajuste_coletivo` |
| Regulatory Intelligence | `igr`, `nip`, `taxa_resolutividade`, `lista_excelencia_reducao` |
| Financial Intelligence | `diops_fip`, `vda`, `glosa`, `ieprs` |
| Network & Coverage Intelligence | `rede_atendimento`, `vazio_assistencial`, `qualiss`, `parto_cesareo` |

### 30.2 Datasets dependentes de painel/publicacao/metodologia indireta

- `lista_excelencia_reducao` depende das divulgacoes da RN 623/2024 no site da ANS.
- `rede_atendimento` e `vazio_assistencial` dependem do painel e/ou publicacao metodologica de Rede e Vazios Assistenciais, lancado em 23/01/2025.
- `glosa` depende da publicacao do Painel de Indicadores de Glosa.
- `prudencial` depende do cronograma de abertura de bases do PDA 2024-2026 e publicacoes operacionais.
- `sip` deve ser tratado como historico/legado, porque a ANS comunicou em 05/03/2026 o fim da obrigatoriedade de envio a partir de 2026, mantendo recepcao de informacoes ate o 4º trimestre de 2025.

### 30.3 Base factual ANS usada para fechar lacunas

- Pagina `Dados e Indicadores do Setor`, atualizada em 11/02/2026: `https://www.gov.br/ans/pt-br/acesso-a-informacao/perfil-do-setor/dados-e-indicadores-do-setor`
- Pagina `Dados do Programa de Qualificacao de Operadoras`, atualizada em 16/03/2026, com metodologia vigente sob `RN 505/2022` e `IN ANS 10/2022`: `https://www.gov.br/ans/pt-br/acesso-a-informacao/perfil-do-setor/dados-e-indicadores-do-setor/dados-do-programa-de-qualificacao-de-operadoras`
- Pagina `Dados Abertos` da ANS e `PDA 2024-2026`: `https://www.gov.br/ans/pt-br/acesso-a-informacao/perfil-do-setor/dados-abertos-1`
- Pagina `Listas de Excelencia e de Reducao das Reclamacoes`, com efeitos desde 01/07/2025 e divulgacoes a partir de dezembro/2025 e marco/2026: `https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/lista-excelencia-e-reducao-das-reclamacoes-das-operadoras`
- Noticia `ANS lanca Painel de Rede e Vazios Assistenciais`, publicada em 23/01/2025 e atualizada em 12/06/2025: `https://www.gov.br/ans/pt-br/assuntos/noticias/beneficiario/ans-lanca-painel-de-rede-e-vazios-assistenciais-na-saude-suplementar`
- Avisos para Operadoras, incluindo comunicados sobre fim da obrigatoriedade do `SIP` a partir de 2026: `https://www.gov.br/ans/pt-br/assuntos/operadoras/avisos-para-operadoras/`
- Nota tecnica da `VDA` referenciando DIOPS e base de beneficiarios por operadora e tipo de carteira: `https://www.gov.br/ans/pt-br/arquivos/assuntos/consumidor/reajustes-de-mensalidade/reajuste-anual-de-planos-individuais-familiares/metodologia-de-calculo/2023/Nota_da_VDA.pdf`

### 30.4 Fechamento

Este documento substitui o PRD tecnico anterior como base de implementacao. O arquivo legado em `PRD_PROJETO/PRD_HealthIntel_Suplementar_v2-1.md` permanece apenas como referencia historica.
