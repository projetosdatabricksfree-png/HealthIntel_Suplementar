# HealthIntel Core ANS — Fase Inicial de Venda

**Projeto:** HealthIntel Suplementar  
**Produto inicial:** HealthIntel Core ANS  
**Modelo comercial:** DaaS/API de dados tratados da ANS  
**Objetivo da fase:** iniciar venda com um produto menor, estável, validável e compatível com uma VPS de 512 GB.

---

## 1. Visão Executiva

O HealthIntel Core ANS será o primeiro produto comercial do projeto HealthIntel Suplementar.

A proposta é entregar dados públicos da ANS já tratados, modelados, validados e disponibilizados por API/SQL para empresas que precisam analisar o mercado de saúde suplementar sem montar pipelines próprios de ingestão, limpeza, versionamento, governança e atualização dos dados.

Nesta fase inicial, o foco **não** será entregar a base completa da ANS.  
O foco será entregar um produto de inteligência de mercado com escopo controlado, baixa complexidade operacional e valor comercial claro.

---

## 2. Posicionamento Comercial

### 2.1 Descrição Curta

> O HealthIntel Core ANS entrega uma API com dados tratados da ANS para análise de operadoras, beneficiários, mercado, rankings, score, financeiro e risco regulatório.

### 2.2 Descrição Completa

> O HealthIntel Core ANS transforma dados públicos da ANS em tabelas e APIs prontas para consumo por times de BI, analytics, consultorias, corretoras, healthtechs e empresas do setor de saúde. O cliente não precisa manter robôs, parsers, cargas, banco de dados, dbt, atualização de layout ou validações recorrentes. Ele consome dados curados diretamente por API ou views SQL controladas.

### 2.3 O Que Vendemos

Vendemos:

- dados tratados;
- atualização recorrente;
- API pronta para consumo;
- views de consumo para BI;
- indicadores de mercado;
- ranking de operadoras;
- score regulatório/comercial;
- redução de custo técnico para o cliente;
- economia de tempo em engenharia de dados.

### 2.4 O Que Não Vendemos Nesta Fase

Não vender nesta fase:

- base completa da ANS;
- dump bruto;
- exportação integral;
- acesso ao bronze/prata;
- TISS real;
- CNES detalhado completo;
- TUSS comercial;
- histórico infinito;
- ambiente dedicado;
- SLA enterprise.

---

## 3. Problema Que o Produto Resolve

Empresas que usam dados da ANS normalmente enfrentam problemas como:

- dificuldade para localizar arquivos corretos;
- alterações de layout;
- arquivos grandes;
- bases com muitos períodos;
- baixa padronização;
- necessidade de tratar competência, CNPJ, registro ANS, município, UF e indicadores;
- demora para montar pipelines confiáveis;
- custo de engenheiros de dados;
- retrabalho em Power BI, SQL e ETL;
- dificuldade para atualizar bases recorrentemente.

O HealthIntel Core ANS reduz esse custo entregando uma camada pronta para consumo.

---

## 4. Público-Alvo Inicial

### 4.1 Clientes Prioritários

- corretoras de planos de saúde;
- consultorias de benefícios;
- consultorias atuariais;
- healthtechs;
- empresas de BI para saúde;
- pequenas e médias operadoras;
- hospitais e redes de saúde;
- empresas que analisam mercado regional;
- times comerciais que precisam estudar concorrência por município.

### 4.2 Cliente Ideal Para o Primeiro Piloto

O cliente ideal do piloto é uma empresa que:

- já usa Power BI, SQL, Excel ou Python;
- já tentou usar dados da ANS;
- tem dificuldade com coleta/tratamento;
- precisa analisar operadoras e mercado;
- aceita começar com escopo reduzido;
- não exige SLA enterprise no início;
- aceita contrato piloto de 30 a 60 dias.

---

## 5. Produto Inicial

## 5.1 Nome do Produto

# HealthIntel Core ANS

## 5.2 Subtítulo

API de inteligência de operadoras e mercado da saúde suplementar brasileira.

## 5.3 Escopo Funcional

O produto inicial deve responder perguntas como:

- Quais operadoras atuam no mercado?
- Qual o perfil de uma operadora?
- Quais operadoras estão crescendo?
- Quais operadoras estão perdendo beneficiários?
- Qual operadora possui melhor score?
- Qual operadora possui pior risco regulatório?
- Qual município possui oportunidade comercial?
- Qual o comportamento de beneficiários por competência?
- Qual o ranking de operadoras por mercado?
- Qual a visão financeira/regulatória de determinada operadora?

---

## 6. Escopo de Dados do MVP

## 6.1 Datasets Incluídos

| Dataset/Família | Entrar no MVP? | Justificativa |
|---|---:|---|
| CADOP | Sim | Cadastro base das operadoras. |
| SIB | Sim, com janela limitada | Beneficiários e mercado. |
| IDSS | Sim | Indicadores de desempenho/qualidade. |
| IGR | Sim | Indicadores regulatórios. |
| NIP | Sim | Reclamações/atendimento. |
| DIOPS/FIP | Sim, se estável | Financeiro e regulatório. |
| RN/listas regulatórias | Sim, se já materializado | Valor analítico para risco. |
| Score operadora | Sim | Diferencial comercial. |
| Ranking operadora | Sim | Produto de fácil entendimento. |
| Mercado por município | Sim | Valor para vendas e expansão regional. |

## 6.2 Datasets Excluídos da Fase Inicial

| Dataset/Família | Motivo |
|---|---|
| TISS real | Muito grande e ainda não deve ser vendido no MVP. |
| TUSS comercial | Risco de base sintética/não comercial e complexidade de licença/uso. |
| CNES completo | Pode ser pesado; deixar para fase posterior. |
| Histórico completo da ANS | Alto custo operacional e pouco necessário para primeira venda. |
| Bronze/prata | Camadas internas, não produto para cliente. |
| Arquivos brutos | Não devem ser expostos comercialmente. |
| Exportação full | Risco comercial de cliente baixar tudo e cancelar. |

---

## 7. Janela de Dados Recomendada

Para caber em uma VPS de 512 GB:

| Tipo de dado | Retenção inicial recomendada |
|---|---|
| CADOP | Completo ou última versão válida |
| SIB | Últimos 12 meses inicialmente |
| SIB expandido | Até 24 meses se performance e disco permitirem |
| IDSS | Histórico disponível se leve |
| IGR | Histórico disponível se leve |
| NIP | Últimos 24 a 36 meses, se couber |
| Financeiro/DIOPS/FIP | Últimos 8 a 12 trimestres |
| TISS | Fora do MVP |
| CNES completo | Fora do MVP |

Regra prática:

> A VPS deve manter apenas dados necessários para servir API e atualizar o produto Core. Arquivos brutos, históricos longos e backups devem ir para object storage.

---

## 8. Tabelas de Consumo Prioritárias

As tabelas abaixo são a base inicial do produto comercial:

```text
consumo_ans.consumo_operadora_360
consumo_ans.consumo_score_operadora_mes
consumo_ans.consumo_beneficiarios_operadora_mes
consumo_ans.consumo_beneficiarios_municipio_mes
consumo_ans.consumo_financeiro_operadora_trimestre
consumo_ans.consumo_regulatorio_operadora_trimestre
```

Tabelas que podem entrar como diferencial, desde que estejam estáveis:

```text
consumo_ans.consumo_oportunidade_municipio
consumo_ans.consumo_rede_assistencial_municipio
```

---

## 9. API Inicial

## 9.1 Endpoints Públicos do MVP

```text
GET /v1/operadoras
GET /v1/operadoras/{registro_ans}
GET /v1/operadoras/{registro_ans}/score
GET /v1/operadoras/{registro_ans}/beneficiarios
GET /v1/operadoras/{registro_ans}/financeiro
GET /v1/operadoras/{registro_ans}/regulatorio

GET /v1/rankings/operadoras
GET /v1/rankings/score

GET /v1/mercado/municipios
GET /v1/mercado/municipios/{codigo_ibge}

GET /v1/oportunidades/municipios

GET /v1/meta/datasets
GET /v1/meta/atualizacao
GET /v1/meta/qualidade
```

## 9.2 Endpoints Bloqueados no MVP

```text
/bronze
/prata
/tiss
/cnes
/premium-instavel
/admin
/layout
/raw
/export-full
/download-all
```

---

## 10. Arquitetura Inicial

```text
[Cliente]
   |
   v
[Nginx]
   |
   v
[FastAPI]
   |
   +--> [Redis]
   |       - cache
   |       - rate limit
   |
   +--> [PostgreSQL]
   |       - api_ans
   |       - consumo_ans
   |       - schemas internos controlados
   |
   +--> [Logs de consumo por API key]

[Airflow/dbt/Ingestão]
   |
   +--> baixa arquivos ANS controlados
   +--> carrega apenas escopo Core
   +--> transforma com dbt
   +--> valida qualidade
   +--> publica api_ans/consumo_ans
   +--> limpa landing local
   +--> envia bruto/backup para R2

[Cloudflare R2 ou equivalente]
   |
   +--> raw antigo
   +--> backups
   +--> arquivos compactados
   +--> histórico sob demanda
```

---

## 11. Regra de Operação Para VPS de 512 GB

## 11.1 Limites de Segurança

| Item | Limite recomendado |
|---|---:|
| Banco PostgreSQL | até 220 GB |
| Landing local | até 80 GB |
| Backups locais | mínimo possível |
| Uso total de disco | alerta em 75% |
| Uso crítico de disco | parar cargas em 90% |
| SIB | 12 meses inicialmente |
| TISS | fora do MVP |
| Histórico bruto | object storage |

## 11.2 Regras Obrigatórias

- não executar carga `all_ftp` no MVP;
- não carregar TISS real;
- não manter todo bruto local;
- não gerar backup full local pesado sem envio externo;
- limpar landing após carga validada;
- manter logs de tamanho por schema/tabela;
- monitorar crescimento do PostgreSQL;
- rodar `VACUUM/ANALYZE` conforme necessidade;
- particionar tabelas grandes por competência/ano quando aplicável.

---

## 12. Proteção Comercial Contra Download Integral

## 12.1 Regras Técnicas

A API deve implementar:

- autenticação por API key;
- paginação obrigatória;
- limite máximo por página;
- rate limit por plano;
- logs por cliente;
- bloqueio de varredura massiva;
- cache para consultas frequentes;
- endpoints agregados em vez de linha a linha;
- sem exportação full;
- sem endpoint para baixar base completa.

## 12.2 Regras Contratuais

O contrato deve prever:

- proibição de redistribuição;
- proibição de revenda dos dados;
- proibição de scraping;
- proibição de reconstrução integral da base;
- uso restrito à finalidade contratada;
- multa por uso indevido;
- bloqueio de chave em caso de abuso;
- auditoria de consumo;
- confidencialidade sobre estrutura e enriquecimentos.

---

## 13. Planos Comerciais Iniciais

## 13.1 Piloto Pago

**Preço sugerido:** R$ 1.500 a R$ 3.000/mês  
**Duração:** 30 a 60 dias

Inclui:

- 1 API key;
- endpoints Core;
- Swagger/Postman;
- limite controlado de requisições;
- suporte assíncrono;
- 1 reunião de onboarding;
- sem SLA enterprise;
- sem exportação completa.

## 13.2 Core API

**Preço sugerido:** R$ 3.900 a R$ 6.900/mês

Inclui:

- API Core;
- 1 a 3 API keys;
- endpoints de operadora, score, ranking, mercado, financeiro e regulatório;
- documentação técnica;
- atualização recorrente;
- logs básicos de consumo;
- suporte comercial.

## 13.3 BI/Consultoria

**Preço sugerido:** R$ 7.900 a R$ 12.900/mês

Inclui:

- API Core;
- views SQL controladas;
- apoio para Power BI;
- onboarding técnico;
- consultas específicas;
- dashboard exemplo;
- suporte consultivo.

## 13.4 Enterprise

**Preço:** sob contrato

Inclui, conforme negociação:

- histórico maior;
- ambiente dedicado;
- datasets adicionais;
- MDM privado;
- SLA superior;
- integrações específicas;
- endpoints premium;
- suporte prioritário.

---

## 14. Critérios Para Começar a Vender

Antes de vender para o primeiro cliente pagante, estes itens devem estar concluídos.

## 14.1 Critérios Técnicos Obrigatórios

- [ ] Ambiente limpo de homologação no ar.
- [ ] PostgreSQL funcionando com escopo Core.
- [ ] FastAPI funcionando atrás do Nginx.
- [ ] Redis ativo para cache/rate limit.
- [ ] API key obrigatória.
- [ ] Rotas não MVP bloqueadas.
- [ ] Tabelas `api_ans` e/ou `consumo_ans` do Core materializadas.
- [ ] dbt build do Core aprovado.
- [ ] smoke test dos endpoints Core aprovado.
- [ ] documentação Swagger validada.
- [ ] limpeza de landing funcionando.
- [ ] backup off-host configurado.
- [ ] restore mínimo testado.
- [ ] monitoramento de disco ativo.
- [ ] alerta de uso de disco configurado.
- [ ] limite de paginação ativo.
- [ ] rate limit ativo por API key.

## 14.2 Critérios Comerciais Obrigatórios

- [ ] One-page comercial do produto.
- [ ] Tabela de planos.
- [ ] Contrato de piloto.
- [ ] Termos anti redistribuição.
- [ ] Política de uso aceitável da API.
- [ ] Proposta comercial padrão.
- [ ] Roteiro de demo.
- [ ] Lista de 20 clientes potenciais.
- [ ] E-mail/WhatsApp de abordagem.
- [ ] Dashboard exemplo ou prints de API.
- [ ] Postman collection pronta.
- [ ] Swagger com autenticação demonstrável.

---

## 15. Sprints da Fase Inicial

## Sprint 1 — Corte Oficial de Escopo

### Objetivo

Definir oficialmente o que será vendido e o que fica fora do MVP.

### Entregas

- [ ] Documento de escopo do HealthIntel Core ANS.
- [ ] Lista de datasets incluídos.
- [ ] Lista de datasets excluídos.
- [ ] Decisão formal: TISS fora do MVP.
- [ ] Decisão formal: CNES completo fora do MVP.
- [ ] Decisão formal: sem exportação full.
- [ ] Decisão formal: cliente só consome API/views controladas.

### Critério de aceite

O projeto deve ter uma documentação clara dizendo que a fase inicial vende apenas o Core ANS.

---

## Sprint 2 — Carga Core Controlada

### Objetivo

Executar uma carga reduzida, estável e compatível com VPS de 512 GB.

### Entregas

- [ ] Comando de carga apenas para Core.
- [ ] Limite de janela para SIB.
- [ ] Exclusão de TISS da carga MVP.
- [ ] Exclusão de `all_ftp` da carga MVP.
- [ ] Métricas de tamanho por schema/tabela.
- [ ] Limpeza de landing após validação.
- [ ] Evidência de uso de disco antes/depois.

### Critério de aceite

A carga Core deve rodar sem ultrapassar limites de disco e sem carregar datasets fora do escopo.

---

## Sprint 3 — dbt Build Core

### Objetivo

Criar um hard gate apenas para os modelos do produto inicial.

### Entregas

- [ ] Selector/tag dbt para `core_ans`.
- [ ] `dbt build` apenas do escopo Core.
- [ ] Testes de integridade mínimos.
- [ ] Testes de chave de negócio.
- [ ] Testes de não duplicidade.
- [ ] Testes de competência.
- [ ] Testes de campos obrigatórios.
- [ ] Documentação das tabelas Core.

### Critério de aceite

O Core deve passar no dbt sem depender de tabelas gigantes fora do MVP.

---

## Sprint 4 — API Core

### Objetivo

Publicar somente endpoints vendáveis.

### Entregas

- [ ] Endpoint de operadoras.
- [ ] Endpoint de score.
- [ ] Endpoint de ranking.
- [ ] Endpoint de beneficiários.
- [ ] Endpoint de mercado por município.
- [ ] Endpoint financeiro.
- [ ] Endpoint regulatório.
- [ ] Endpoint de metadados.
- [ ] Paginação obrigatória.
- [ ] Limite por página.
- [ ] API key obrigatória.
- [ ] Rate limit.
- [ ] Logs por cliente.

### Critério de aceite

Todos os endpoints públicos devem consultar apenas tabelas do Core e passar smoke test.

---

## Sprint 5 — Segurança Comercial e Antiextração

### Objetivo

Reduzir risco de cliente baixar a base inteira e cancelar.

### Entregas

- [ ] Rate limit por plano.
- [ ] Limite máximo de registros por resposta.
- [ ] Bloqueio de exportação full.
- [ ] Logs por API key.
- [ ] Detecção de varredura massiva.
- [ ] Política de uso aceitável.
- [ ] Termos anti scraping.
- [ ] Cláusula contratual de multa.
- [ ] Bloqueio/revogação de chave.

### Critério de aceite

Não deve existir rota pública que permita exportar a base inteira.

---

## Sprint 6 — Operação VPS

### Objetivo

Garantir que o produto rode com estabilidade em VPS de 512 GB.

### Entregas

- [ ] Monitor de disco.
- [ ] Monitor de banco.
- [ ] Monitor de landing.
- [ ] Rotina de backup externo.
- [ ] Rotina de limpeza.
- [ ] Stop automático de carga em disco crítico.
- [ ] Documentação de restore.
- [ ] VACUUM/ANALYZE planejado.
- [ ] Política de retenção.

### Critério de aceite

A VPS deve operar o Core sem risco de encher disco por carga ou backup local.

---

## Sprint 7 — Kit Comercial

### Objetivo

Preparar material para vender.

### Entregas

- [ ] Landing page simples.
- [ ] One-page PDF/MD.
- [ ] Proposta comercial padrão.
- [ ] Contrato de piloto.
- [ ] Termos de uso.
- [ ] Swagger.
- [ ] Postman collection.
- [ ] Roteiro de demo.
- [ ] Lista de prospects.
- [ ] Script de abordagem.

### Critério de aceite

Deve ser possível enviar uma proposta para um cliente real sem improvisar.

---

## 16. Roteiro de Demo

## 16.1 Estrutura da Apresentação

1. Problema: dados da ANS são públicos, mas difíceis de consumir.
2. Custo: empresas gastam tempo com engenharia de dados antes de gerar valor.
3. Solução: API pronta com dados tratados.
4. Demonstração:
   - buscar operadora;
   - ver score;
   - ver beneficiários;
   - comparar ranking;
   - analisar município;
   - consultar metadados de atualização.
5. Valor: cliente consome no BI sem montar pipeline.
6. Oferta: piloto pago de 30 dias.

## 16.2 Frase de Demonstração

> Em vez da sua equipe baixar arquivos da ANS, tratar layout, criar banco, montar dbt e atualizar carga, vocês consomem uma API pronta e já modelada para análise de mercado.

---

## 17. Abordagem Comercial Inicial

## 17.1 Mensagem Curta Para WhatsApp/LinkedIn

```text
Olá, tudo bem?

Estou lançando o HealthIntel Core ANS, uma API com dados tratados da ANS para análise de operadoras, beneficiários, mercado, rankings, score e risco regulatório.

A ideia é ajudar empresas que usam dados da saúde suplementar a consumir essas informações direto no BI/API, sem precisar montar pipeline próprio de coleta e tratamento.

Estou abrindo alguns pilotos pagos com escopo reduzido para empresas do setor. Faz sentido eu te mostrar uma demo rápida?
```

## 17.2 E-mail de Prospecção

```text
Assunto: API com dados tratados da ANS para BI e análise de mercado

Olá,

Estou lançando o HealthIntel Core ANS, uma API/DaaS com dados públicos da ANS já tratados, modelados e prontos para consumo por times de BI, analytics e áreas comerciais.

O produto inicial entrega informações de operadoras, beneficiários, mercado por município, rankings, score, financeiro e risco regulatório.

A proposta é reduzir o esforço de manter robôs, cargas, layouts, banco de dados e transformações recorrentes sobre os arquivos da ANS.

Estou abrindo uma fase de pilotos pagos com escopo controlado para validar o produto com empresas do setor.

Posso te apresentar uma demonstração rápida?
```

---

## 18. Proposta de Piloto

## 18.1 Piloto HealthIntel Core ANS

**Duração:** 30 dias  
**Valor sugerido:** R$ 2.500  
**Formato:** API key + documentação + onboarding

Inclui:

- acesso à API Core;
- endpoints de operadoras, score, ranking, beneficiários, mercado, financeiro e regulatório;
- Swagger/Postman;
- 1 reunião de onboarding;
- suporte assíncrono;
- limite de requisições;
- sem exportação completa;
- sem SLA enterprise.

Não inclui:

- TISS;
- CNES completo;
- histórico completo;
- download bruto;
- desenvolvimento de dashboard sob medida;
- ambiente dedicado;
- acesso irrestrito ao banco.

---

## 19. Métricas de Sucesso da Fase Inicial

A fase inicial será considerada bem-sucedida se atingir:

- [ ] 1 cliente piloto pagante.
- [ ] 3 demonstrações realizadas.
- [ ] 20 prospects abordados.
- [ ] API Core estável em VPS.
- [ ] Nenhum incidente de disco.
- [ ] Nenhuma rota de exportação full exposta.
- [ ] Carga Core repetível.
- [ ] dbt Core aprovado.
- [ ] Smoke API aprovado.
- [ ] Primeiro feedback real de cliente registrado.

---

## 20. Decisões Arquiteturais da Fase

## 20.1 Decisões Confirmadas

- O MVP será menor que a plataforma completa.
- A primeira venda será sobre dados tratados e indicadores.
- O cliente consumirá API/views controladas.
- A VPS de 512 GB será usada com escopo reduzido.
- Object storage será usado para bruto, backup e histórico.
- TISS fica fora do MVP.
- Exportação full fica fora do MVP.
- Bronze/prata ficam internos.
- Produto inicial foca em operadoras e mercado.

## 20.2 Dívidas Para Fases Futuras

- TISS real.
- CNES detalhado.
- Portal do cliente.
- Billing automatizado completo.
- Ambientes dedicados.
- Histórico ampliado.
- Premium API.
- Contratos enterprise.
- Integração direta com Power BI.
- Marketplace de datasets.

---

## 21. Próximas Ações Imediatas

## 21.1 Técnica

- [ ] Criar tag/selector dbt `core_ans`.
- [ ] Criar comando `make dbt-build-core`.
- [ ] Criar comando `make smoke-core`.
- [ ] Criar comando de carga `core` sem TISS.
- [ ] Criar rotina de limpeza da landing.
- [ ] Bloquear rotas fora do MVP.
- [ ] Validar API key e rate limit.
- [ ] Medir tamanho final do banco Core.
- [ ] Gerar evidência de carga em VPS.

## 21.2 Comercial

- [ ] Criar one-page do produto.
- [ ] Criar proposta de piloto.
- [ ] Criar contrato simples.
- [ ] Criar lista de 20 prospects.
- [ ] Criar roteiro de demo.
- [ ] Criar Postman collection.
- [ ] Criar landing page simples.
- [ ] Definir preço inicial do piloto.
- [ ] Abordar primeiros contatos.

---

## 22. Definição de Pronto da Fase Inicial

A fase inicial estará pronta para venda quando:

```text
1. O escopo Core estiver documentado.
2. A carga Core rodar sem estourar disco.
3. O dbt build Core passar.
4. Os endpoints Core responderem corretamente.
5. API key e rate limit estiverem ativos.
6. A documentação Swagger/Postman estiver pronta.
7. Rotas não MVP estiverem bloqueadas.
8. O contrato de piloto estiver pronto.
9. A proposta comercial estiver pronta.
10. O produto puder ser demonstrado para um cliente real.
```

---

## 23. Resumo Final

O HealthIntel Core ANS deve começar pequeno, confiável e vendável.

A prioridade agora não é carregar toda a ANS.  
A prioridade é transformar o que já está maduro em um produto comercial.

O primeiro produto deve vender inteligência sobre:

- operadoras;
- beneficiários;
- mercado;
- ranking;
- score;
- financeiro;
- regulatório.

Com isso, o projeto pode começar a gerar receita sem depender de uma infraestrutura grande, sem prometer escopo excessivo e sem travar no custo das tabelas gigantes.

