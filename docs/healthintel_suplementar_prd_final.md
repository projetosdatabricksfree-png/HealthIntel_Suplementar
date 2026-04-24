# HealthIntel Suplementar — PRD de Visão

| Campo | Valor |
| --- | --- |
| Versão | 3.0 |
| Status | Em execução ativa |
| Data | 23/04/2026 |
| Domínio | Saúde suplementar / ANS |
| Tipo de produto | Engenharia de dados + API SaaS / DaaS |
| Fases | Fase 1 concluída (Sprints 1–12) · Fase 2 concluída (Sprints 13–14) · Fase 3 concluída (Sprints 15–20) |

---

## 1. Visão Executiva

### O que é o produto

HealthIntel Suplementar é uma plataforma de infraestrutura de dados regulatórios e operacionais da Agência Nacional de Saúde Suplementar. O produto coleta, valida, governa, transforma e expõe dados públicos da ANS por meio de uma API REST autenticada, com múltiplos níveis de garantia de qualidade e contratos semânticos distintos por camada. O objetivo não é produzir análises ou dashboards — é entregar dados prontos para integração por times de dados, engenharia, risco, pricing, regulatório e produto em clientes B2B.

### Por que existe

Dados públicos da ANS existem, mas são inacessíveis na prática. Layouts físicos mudam sem aviso, arquivos chegam em formatos heterogêneos, a semântica entre publicações é inconsistente, não há API oficial estruturada, e o custo de montar e manter um pipeline confiável é alto para qualquer empresa individualmente. O HealthIntel resolve isso operando dados públicos como produto comercial com contrato, versionamento e SLA.

### Para quem

O ICP primário é composto por healthtechs B2B, corretoras e distribuidores com inteligência comercial, operadoras e seguradoras com times de estratégia e risco, consultorias com squads de dados, e fintechs de comparação e regulação. O ICP secundário cobre fundos e M&A com tese em saúde, times de pricing e revenue intelligence, e software houses com produtos para operadoras e prestadores.

### O que o produto não é

O produto não é BI, dashboard, consultoria analítica, data lake genérico sem contrato, nem mecanismo de inferência sem supervisão humana. O cliente recebe endpoints e datasets — nunca análises prontas. Esse limite é um firewall de escopo, não uma limitação técnica.

---

## 2. Proposta de Valor e Tese de Monetização

### O que o cliente recebe

O cliente assina o serviço, recebe credenciais de API e passa a consumir dados públicos da ANS com curadoria técnica, histórico, versionamento e SLA operacional sem precisar construir localmente: robôs de download, tratamento de encoding, reconciliação de schema, normalização de layouts mutáveis, governança de histórico, marts analíticos e contratos de API.

O produto entrega três níveis distintos de dado:

- **Bronze**: dado bruto auditável com metadados estruturais completos — para engenharia e auditoria
- **Prata**: dado padronizado com tipagem garantida e transparência de qualidade — para ciência de dados e BI técnico
- **Ouro**: dado pronto para negócio com scores, rankings e oportunidades — para produto, estratégia e comercial

### Tese de vantagem competitiva

A vantagem não está na posse exclusiva do dado — esses dados são públicos. A vantagem está no pacote operacional: governança formal de layout físico com compatibilidade retroativa, histórico reproduzível e auditável, reprocessamento determinístico sem perda de dados anteriores, e contratos de API estáveis mesmo quando a ANS muda formatos.

Sem essa camada operacional, o custo real do cliente está na engenharia: layouts físicos instáveis, CSVs heterogêneos, ausência de contratos consolidados, quebra metodológica entre anos e falta de padrão operacional entre fontes.

### Dimensões de monetização

O produto monetiza em quatro dimensões independentes e combináveis: camada de acesso (dado bruto, padronizado ou pronto para negócio), volume de requisições por hora, profundidade de famílias de datasets disponíveis por plano, e SLA de latência e disponibilidade garantidos por tier.

---

## 3. Modelo Comercial — Cinco Tiers por Camada

A plataforma opera com cinco tiers comerciais. Cada tier define quais camadas da arquitetura medallion o cliente pode acessar via API, qual o volume de requisições permitido e qual SLA é garantido contratualmente.

**Piloto**: acesso exclusivo à camada Ouro. Limite baixo de requisições, SLA básico de latência e disponibilidade. Usado para validação de produto, provas de conceito e entrada de mercado.

**Essencial**: acesso exclusivo à camada Ouro com volume maior. Produto padrão para times de dados que consomem scores, rankings e séries históricas de operadoras. SLA básico.

**Plus**: acesso às camadas Ouro e Prata. Volume médio, SLA intermediário. Para times que precisam de dado padronizado com visibilidade de qualidade, taxa de aprovação por lote e acesso a registros em quarentena. Inclui dados enriquecidos de operadora, métricas por município e financeiro consolidado por período.

**Enterprise**: acesso completo às três camadas — Ouro, Prata e Bronze. Volume alto, SLA forte de latência p95 e disponibilidade mensal. Para integrações de engenharia que precisam de dado bruto auditável com metadados de ingestão completos.

**Enterprise Técnico**: acesso completo sem limite de requisições. SLA máximo. Dado bruto com todos os metadados de lote, arquivo de origem, hash e versão de layout. Para clientes que operam o dado como infraestrutura própria, com pipeline de ingestão próprio que precisa de rastreabilidade total.

O rate limiting reflete o custo diferencial de cada camada: uma requisição à Bronze API consome três vezes mais do bucket do que uma requisição à Ouro API. Isso incentiva o uso da camada adequada ao caso de uso e protege a infraestrutura em tiers inferiores.

---

## 4. Arquitetura Medallion com Exposição Multi-tier

A plataforma é organizada em arquitetura medallion de cinco camadas lógicas. Três delas têm exposição comercial via API, com contratos e garantias distintos.

### Bronze — Dado Bruto Auditável

Schema bruto_ans no PostgreSQL. Espelho imutável dos dados da ANS após tradução física pelo motor de layout. Cada registro é identificado por hash de arquivo e de linha, associado ao lote de ingestão, ao layout físico que foi aplicado e ao arquivo de origem. Nenhuma transformação semântica ocorre aqui — nomes de campos podem ainda ter variações de encoding ou capitalização resolvidas apenas no staging.

O contrato da camada Bronze é estrutural: o dado chegou, foi parseado corretamente pelo layout aprovado, e está disponível com metadados completos de auditoria. A aviso de ausência de garantia semântica está explicitamente presente no envelope de resposta da Bronze API.

Acesso via API restrito ao tier Enterprise Técnico.

### Prata Entrada — Dado Padronizado

Schema stg_ans via views dbt. Staging normalizado: tipagem garantida, registro ANS padronizado a seis dígitos, datas em formato canônico, domínios validados, campos derivados de normalização. Registros inválidos são segregados em tabelas de quarentena específicas por dataset, com motivo de rejeição, regra que falhou e lote preservado. Esses registros nunca aparecem nos dados servidos — mas são acessíveis via endpoint dedicado para clientes com plano adequado.

O contrato da camada Prata é de tipagem e domínio: todos os campos têm tipo definido, domínio validado e a taxa de aprovação do lote está sempre visível no envelope de resposta.

Acesso via API nos tiers Plus, Enterprise e Enterprise Técnico.

### Prata Saída — Dado Enriquecido

Schema int_ans como modelos efêmeros dbt (não materializados como tabela independente). Enriquecimento via joins entre fontes, derivações de métricas compostas por operadora e por município, reconciliação de dados de múltiplos datasets no mesmo período. Alimenta tanto os marts de Ouro quanto modelos enriquecidos servidos via Prata API.

### Ouro Analítico — Modelo Dimensional

Schema nucleo_ans. Modelo dimensional completo: fatos incrementais com chave única garantida por testes dbt, dimensões SCD Type 2, derivados de score, ranking e oportunidade territorial. Não exposto diretamente — serve de base para a camada de serviço.

### Ouro Serviço — API Pronta para Negócio

Schema api_ans. Tabelas desnormalizadas, indexadas e otimizadas para resposta da FastAPI. Leitura exclusiva pela API pública. SLA de latência p95 garantido. Todos os cinco tiers têm acesso à camada Ouro — é o produto comercial principal.

### Por que esta separação existe

O dbt governa transformação semântica, não layout físico instável. Mudança de cabeçalho, alias, ordem de coluna, assinatura de arquivo e regra de compatibilidade pertencem ao domínio estrutural do motor de ingestão com MongoDB. Essa separação é o que torna o histórico reproduzível: qualquer arquivo antigo pode ser reprocessado com o layout que estava ativo na época, sem reescrever nenhum modelo dbt.

---

## 5. Governança de Layout Físico

O problema central do pipeline ANS é que layouts físicos mudam sem aviso: colunas são renomeadas, acrescentadas, removidas, reordenadas ou têm encoding alterado entre publicações. Sem governança formal, o pipeline quebra a cada mudança e o histórico deixa de ser reprocessável.

O MongoDB resolve este problema armazenando datasets, versões de layout, aliases de coluna, regras de transformação, compatibilidades, histórico de mapeamento e trilha de aprovação humana. Cada arquivo recebido passa por um fluxo determinístico: identificação de dataset, snapshot estrutural, resolução de layout por compatibilidade e prioridade, aplicação de aliases e regras de parse, e só então carga em bronze.

Os princípios fundamentais da governança de layout são:

Todo alias é cadastrado manualmente por operador, sem inferência automática. Toda versão de layout exige aprovação humana antes de entrar em produção. A seleção de layout é determinística com regra de compatibilidade, prioridade declarada e fallback explícito. Bronze é imutável: reprocessamento gera novo lote sem sobrescrever o anterior. O histórico é reproduzível: qualquer arquivo antigo pode ser reprocessado com o layout que estava ativo na época.

O ciclo de vida de um layout passa pelos estados rascunho, em validação, ativo, depreciado, inativo e rejeitado. Nenhuma versão avança para ativo sem evento de aprovação registrado. Arquivo sem layout aprovado vai para quarentena — nunca é ignorado silenciosamente.

---

## 6. Universo de Datasets — 22 Fontes Mapeadas

A plataforma cobre 22 datasets organizados em quatro famílias com status operacional distinto.

### Core Platform — Dados de Mercado e Beneficiários

CADOP (Cadastro de Operadoras) é a base mestre de operadoras com atualização contínua. SIB por Operadora e SIB por Município cobrem beneficiários com granularidade por registro ANS, competência e localidade, com publicação mensal. IDSS (Índice de Desempenho) traz pontuação anual de qualidade por operadora. VDA (Variação das Despesas Assistenciais) e Portabilidade são mensais e operacionais. Regime Especial e Prudencial são trimestrais e cobrem risco regulatório de solvência. Valores Comerciais não tem publicação ANS estruturada e está como placeholder para Fase 4. Reajustes Coletivos tem publicação em PDF ou tabela no site ANS e será avaliado na Sprint 18.

### Regulatory Intelligence

IGR (Índice Geral de Reclamações), NIP (Notificações de Intermediação Preliminar) e RN 623 (Lista de Excelência e Redução) são trimesrais e cobrem o panorama regulatório de atendimento ao beneficiário. Taxa de Resolutividade complementa a análise regulatória. QUALISS e IEPRS (Índice de Desempenho da Atenção Primária) terão viabilidade de publicação avaliada na Sprint 18.

### Financial Intelligence

DIOPS (Demonstrações Contábeis) e FIP (Ficha de Informações Padronizadas) são trimestrais e cobrem resultado econômico-financeiro. Glosa cobre valores glosados por operadora com granularidade mensal.

### Network and Coverage Intelligence

Rede Assistencial cobre prestadores por operadora e município com publicação mensal. CNES (Cadastro Nacional de Estabelecimentos de Saúde do DATASUS) está em integração na Sprint 13. TISS (Troca de Informações em Saúde Suplementar) está planejado para a Sprint 14.

---

## 7. Estado Atual — Fase 1 Concluída (Sprints 1–12)

A Fase 1 entregou o produto comercial inicial completo com todas as camadas da arquitetura medallion operacionais e o primeiro conjunto de datasets integrados.

### Fundação e Pipeline Core (Sprints 1–6)

Monorepo com quatro serviços isolados: FastAPI pública, MongoDB Layout Service, Airflow e dbt. Infraestrutura local via Docker Compose com PostgreSQL 16, MongoDB 7, Redis 7, Airflow e Nginx. Schemas completos no PostgreSQL: bruto_ans, stg_ans, nucleo_ans, api_ans e plataforma. Layout registry operacional em MongoDB com collections de governança, versionamento, aliases e aprovação humana. Ingestão operacional de CADOP, SIB por Operadora e SIB por Município. Staging dbt com normalização, snapshot SCD2 de operadora, dimensões de operadora, competência e localidade. Score v1 parametrizado por seed com fatos incrementais e camada api_ans indexada. FastAPI com autenticação por X-API-Key, rate limit em Redis, log de uso por requisição e cache com TTL de 60 segundos. Billing base com ciclo de faturamento, fatura de consumo por cliente, histórico de plano e trilha de auditoria. CI automatizado com Ruff, pytest, SQLFluff, dbt compile e validação de configuração Docker. Hardening com TrustedHost, limite de payload, headers de segurança e token de serviço interno. Smoke tests fim a fim, baseline de carga com Locust e runbooks operacionais.

### Regulatory Intelligence (Sprints 7–8)

IGR, NIP e RN 623 com layouts bootstrapados em MongoDB, bronze particionado no PostgreSQL e staging dbt. Regime especial, prudencial e portabilidade integrados. Score regulatório calculado a partir das dimensões IGR, NIP, RN 623 e situação prudencial. Endpoints de score regulatório por operadora, regime especial e portabilidade disponíveis na API.

### Financial Intelligence (Sprints 9–10)

DIOPS e FIP com fatos financeiros trimestrais. VDA e Glosa com granularidade mensal. Score v2 incorporando dimensões financeiras sobre o score regulatório. Endpoints financeiros e de score v2 operacionais.

### Network and Coverage Intelligence (Sprints 11–12)

Rede assistencial com cobertura por município e por operadora. Vazios assistenciais calculados por cruzamento entre demanda e oferta territorial. Oportunidade v2 por município com score composto de mercado. Rankings territoriais com filtros por UF e modalidade. Catálogos de dataset, runbooks de produção e baseline v1.0.0 taggeado no git.

---

## 8. Concluída — Fase 2 (Sprints 13–14)

### Sprint 13 — CNES (concluída)

Integração do Cadastro Nacional de Estabelecimentos de Saúde do DATASUS. Bronze particionado mensalmente com metadados de auditoria. Staging dbt normalizando código de estabelecimento, tipo de serviço, município e situação. Intermediário de estabelecimentos por operadora para alimentar o componente estrutural do Score v3.

### Sprint 14 — TISS (concluída)

Integração de procedimentos TISS trimestral da ANS. Cruzamentos entre glosa e procedimentos realizados, enriquecimento da análise financeira e contribuição ao componente estrutural do Score v3.

---

## 9. Concluída — Fase 3 (Sprints 15–20)

A Fase 3 formaliza o escopo comercial completo da plataforma: governança rigorosa de todas as camadas, exposição da Bronze API e Prata API como produtos comerciais distintos, Score v3 composto com todas as dimensões disponíveis, e lançamento dos cinco tiers enterprise com SLAs formalizados por camada.

### Sprint 15 — Governança de Camadas

Hardening do bronze com hash SHA-256 por arquivo e por linha, idempotência determinística por hash e rejeição de duplicatas com status auditável. Quarentena real por dataset: tabelas de quarentena com motivo de rejeição, regra que falhou e lote preservado — substituindo a quarentena de arquivo atual por uma quarentena semântica de registro. Gates de qualidade entre camadas com thresholds declarados em variáveis dbt: taxa mínima de aprovação no staging, integridade referencial obrigatória nos intermediários, e pelo menos um registro válido por período para materialização de fatos. Freshness SLO documentado para todos os 22 datasets. Documento formal de contratos por camada com garantias, transformações, validações, saída esperada e nível de risco.

### Sprint 16 — Bronze API Técnica

Exposição da camada bruto_ans via REST com onze endpoints — um por dataset core. O envelope Bronze inclui dado bruto com metadados completos de auditoria: fonte, lote, arquivo de origem, hash de arquivo, versão do dataset e aviso explícito de ausência de garantia semântica. Modelos dbt thin em api_ans como views sobre bruto_ans, sem nenhuma transformação de conteúdo. Dependência verificar_camada bloqueando acesso por plano antes de qualquer consulta. Cache Redis desabilitado para Bronze por ser dado mutável até fechamento do lote. Plano enterprise_tecnico como plano mínimo para qualquer endpoint da Bronze API.

### Sprint 17 — Prata API Analítica

Exposição da camada prata via REST com quatorze endpoints: onze datasets padronizados a partir do staging e três modelos enriquecidos a partir dos intermediários (operadora com crescimento histórico e canônico, métricas por município e financeiro consolidado por período). O envelope Prata inclui sempre taxa de aprovação do lote e contagem de registros em quarentena. Dois endpoints de visibilidade de quarentena: resumo por dataset acessível ao plano analítico, e detalhe de registros rejeitados restrito ao enterprise_tecnico. Cache Redis com TTL de 300 segundos habilitado para Prata. Plano analítico como plano mínimo para a Prata API.

### Sprint 18 — Datasets Complementares

Avaliação de viabilidade de publicação ANS para QUALISS, IEPRS e Reajustes Coletivos. Se publicação viável: DDL de bronze, layout registry em MongoDB, DAG de ingestão e staging dbt. Se inviável: decisão documentada com motivo e data de reavaliação. Placeholder formal para Valores Comerciais sem DAG nem layout (dataset não operacional). Catálogo de datasets completo e atualizado cobrindo todos os 22 datasets com status de publicação ANS, freshness SLO, DAG responsável e modelo dbt de staging.

### Sprint 19 — Score v3 e Índice Composto

Score v3 composto com cinco dimensões ponderadas. A dimensão core (SIB) tem peso de 25% e cobre crescimento de beneficiários e presença geográfica. A dimensão regulatória tem peso de 25% e agrega IGR, NIP, RN 623, prudencial, QUALISS e IEPRS quando disponíveis. A dimensão financeira tem peso de 20% e combina DIOPS, FIP, VDA e glosa. A dimensão de rede tem peso de 20% e usa cobertura assistencial e vazios. A dimensão estrutural tem peso de 10% e incorpora CNES quando a Sprint 13 estiver concluída. Fallback automático por componente não disponível com flag componente_estimado e coalesce para o score v2 normalizado. Versão de metodologia v3.0 registrada em plataforma.versao_dataset. Ranking composto com posição geral, posição por modalidade e variação de posição nos últimos três meses. Endpoints de score v3 por operadora e ranking composto com filtros por competência, modalidade e UF.

### Sprint 20 — Comercialização Enterprise Final

Formalização dos cinco tiers com SLAs declarados por camada: latência p95 em milissegundos, disponibilidade mensal em porcentagem, rate limit por hora e camadas_permitidas como campo em plataforma.plano. Rate limiting atualizado com multiplicadores por prefixo de rota: requisição à Bronze API consome três vezes o bucket, Prata consome duas vezes, Ouro consome uma vez. Headers de resposta X-RateLimit-Remaining e X-RateLimit-Reset em todas as respostas. Billing desagregado por camada com coluna camada em plataforma.log_uso inferida pelo prefixo da rota, view de consumo por cliente e camada, e script de fechamento mensal atualizado para fatura desagregada. Catálogo comercial com matriz de planos e guia de onboarding enterprise. Suite de regressão cobrindo todos os endpoints das três camadas, incluindo validação de bloqueio por plano e verificação de registro de camada no billing. Baseline v2.0.0 com documentação CHANGELOG completa e tag git.

---

## 10. Qualidade, Contratos por Camada e Observabilidade

### Contratos por camada

O contrato Bronze garante que o dado chegou, foi parseado pelo layout aprovado e está disponível com metadados de auditoria. Nada além disso. O campo de aviso de qualidade no envelope deixa explícita a ausência de garantia semântica.

O contrato Prata garante tipagem correta, domínio validado e segregação de registros inválidos com transparência. A taxa de aprovação do lote está sempre no envelope. Registros em quarentena são acessíveis com metadados completos de rejeição.

O contrato Ouro garante semântica de negócio: scores calculados com metodologia versionada, rankings reproduzíveis, fatos com chave única garantida por testes dbt, índices físicos para performance e SLA de latência garantido contratualmente.

### Gates de qualidade entre camadas

Entre Bronze e Prata: taxa mínima de 95% de aprovação por lote. Se o lote cair abaixo do threshold, alerta é emitido e os dados são expostos na Prata API com a taxa real no envelope — nunca silenciados ou bloqueados.

Entre Prata e Ouro: integridade referencial 100% nos joins do intermediário. Fatos só materializam se ao menos um registro válido existir para o período.

### Freshness SLO

Cada dataset tem SLO de freshness declarado: warn após N dias sem atualização e error após M dias. Publicações mensais têm SLO de 45 dias de warn e 90 de error. Publicações trimestrais têm 95 dias de warn e 120 de error. Publicações anuais têm 365 dias de warn e 400 de error. Alertas automáticos via dbt source freshness.

### Rastreabilidade fim a fim

A plataforma mantém rastreabilidade completa de arquivo até cliente. Cada arquivo recebido é identificado por hash SHA-256 em MongoDB. Cada lote é rastreado em plataforma.job com timestamps, contagens e status. Cada requisição de API gera log em plataforma.log_uso com endpoint, latência, cliente, camada e código de resposta. Cada execução de layout é registrada no MongoDB com versão aplicada e resultado por linha. Cada versão de dataset é catalogada em plataforma.versao_dataset. O dbt docs mantém lineage completo de todas as dependências entre modelos.

---

## 11. Decisões Arquiteturais Fundamentais

**MongoDB para governança de layout**: MongoDB resolve o problema de layout físico mutável, manual e multi-versão. PostgreSQL poderia armazenar metadados, mas documentos com arrays de aliases, versões paralelas e snapshot estrutural de arquivo recebido são naturais em MongoDB. O MongoDB é exclusivamente fonte de governança de pipeline — nunca fonte de dados da API pública.

**Layout manual com aprovação obrigatória**: alias e versão de layout são cadastrados e aprovados manualmente por operador. Rastreabilidade e previsibilidade superam qualquer ganho marginal de inferência automática. O erro humano é detectável e auditável; inferência silenciosa não é.

**dbt começa no staging, nunca no arquivo**: o dbt governa transformação semântica, não layout físico. Mudança de cabeçalho, encoding, alias e compatibilidade são domínio do motor de ingestão com MongoDB. Essa separação é o que torna o histórico reprocessável sem reescrever modelos dbt.

**Bronze imutável**: nenhum lote histórico é sobrescrito. Reprocessamento gera novo lote com referência cruzada ao anterior. Reprodutibilidade total e auditoria de impacto de qualquer mudança de layout.

**API lê exclusivamente api_ans**: a FastAPI nunca acessa nucleo_ans ou stg_ans diretamente. Essa separação garante SLA de leitura independente do ciclo de transformação dbt e elimina dependência acidental de marts internos em estado intermediário.

**Aprovação de layout como gate bloqueante**: arquivo sem layout aprovado vai para quarentena — nunca é ignorado silenciosamente ou processado com heurística. Falha segura é o padrão do sistema.

**Multi-tier API com camadas_permitidas**: os cinco tiers controlam acesso por camada via campo camadas_permitidas em plataforma.plano. A dependência verificar_camada em FastAPI bloqueia acesso antes de qualquer consulta ao banco. Rate limit com multiplicadores por prefixo de rota reflete o custo diferencial de cada camada e protege a infraestrutura.

**Quarentena semântica de registro, não só de arquivo**: a partir da Fase 3, registros individuais com dados inválidos vão para tabelas de quarentena por dataset — não apenas arquivos inteiros. Isso permite que um lote parcialmente válido contribua para a Prata API com a taxa de aprovação real registrada no envelope.

---

## 12. Roadmap Estratégico por Fase

**Fase 1 — Produto comercial inicial** (Concluída, Sprint 12, baseline v1.0.0)

Fundação técnica completa, governança de layout operacional, pipeline core com doze datasets integrados, score v1 e v2, endpoints MVP de operadoras, regulatório, financeiro e rede, billing base, CI/CD, hardening e rollout enterprise inicial.

**Fase 2 — Expansão de datasets estruturais** (Em andamento)

CNES com estabelecimentos de saúde e TISS com procedimentos. Cruzamentos entre estabelecimentos, procedimentos, glosa e rede assistencial. Componente estrutural preparado para o Score v3.

**Fase 3 — Arquitetura completa e cinco tiers enterprise** (Planejada)

Governança rigorosa com hardening de bronze e quarentena semântica. Bronze API e Prata API como produtos comerciais distintos. Datasets complementares QUALISS, IEPRS e reajustes. Score v3 composto com cinco dimensões. Cinco tiers formalizados com SLAs por camada, billing desagregado e baseline v2.0.0.

**Fase 4 — Expansão enterprise e datasets proprietários** (Futura)

Valores comerciais de planos quando publicação ANS estruturada disponível. Conectores dedicados por segmento de cliente. Add-ons de exportação e SLA dedicado. Possíveis extensões para TISS analítico e integrações com sistemas de operadoras.

---

## 13. Riscos e Mitigações

**Mudança de layout sem aviso pela ANS**: layout registry com quarentena imediata e alerta operacional. Nenhum arquivo sem layout aprovado entra em produção.

**Dataset com publicação instável ou descontinuada**: freshness SLO com alerta automático e catálogo com status de cada dataset e data de reavaliação. SIP já foi depreciado (ANS comunicou fim da obrigatoriedade em 2026) e o catálogo reflete isso.

**Dado público percebido como commodity**: a vantagem competitiva está na operação — governança, histórico, versionamento e contrato — não na exclusividade do dado. O cliente paga pelo custo operacional evitado, não pelo dado em si.

**Escopo derivar para consultoria analítica**: o produto entrega endpoints e datasets, nunca análises ou dashboards. O CLAUDE.md e este PRD são firewalls de escopo operacionais que se aplicam a cada decisão de sprint.

**Latência acima do SLA por tier**: camada api_ans isolada da transformação dbt, cache Redis configurável por tier, índices físicos por endpoint e monitoramento de p95 em tempo real. O rate limit com multiplicadores por camada protege a infraestrutura de sobrecarga por uso excessivo de Bronze.

**Complexidade operacional de três camadas de API**: dependência verificar_camada centralizada em FastAPI, testes de regressão obrigatórios por tier e endpoint, e gate hard de zero falhas na suite de regressão da Fase 3 antes de qualquer release.

**Taxa de quarentena alta por dataset**: alerta automático quando a taxa ultrapassa 5%. Dado ainda é exposto na Prata API com a taxa real — nunca silenciado. O operador é notificado para revisar o layout ou investigar a fonte ANS.

---

## 14. Definição de Pronto por Domínio

**Ingestão**: arquivo identificado por hash, layout resolvido e aprovado, carga em bronze com todos os metadados de auditoria, job registrado em plataforma.job com status e contagens.

**Layout**: versão cadastrada, aliases revisados e aprovados por operador, compatibilidade validada com arquivo de amostra, aprovação registrada com evento auditável.

**dbt**: modelo compilado sem erros, testes genéricos e singulares passando, documentação atualizada no YAML correspondente, lineage verificado.

**API**: schema Pydantic definido, contrato de resposta documentado, teste de integração aprovado, controle de acesso por plano e camada validado, log de uso emitido.

**Qualidade**: gate de taxa de aprovação configurado, freshness SLO declarado em _sources.yml, alerta de quarentena testado.

**Release**: smoke test passando, suite de regressão sem falhas, catálogo de datasets atualizado, CHANGELOG com entradas da release, baseline taggeado no git.

---

Referência operacional de sprints: `docs/sprints/README.md`

Referência de governança de camadas: `docs/sprints/fase3/README.md`

Referência de contratos por camada: `docs/arquitetura/contratos_por_camada.md` (a criar na Sprint 15)
