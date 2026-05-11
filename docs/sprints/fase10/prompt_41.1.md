Você está trabalhando no projeto HealthIntel Suplementar.

Objetivo:
Fechar a Sprint 41 Delta ANS 100% trabalhando somente nos itens [ ] ainda abertos do checklist.

Arquivo principal:
docs/sprints/fase10/sprint_41_delta_ans_100_faltantes.md

Regras obrigatórias:
- Não alterar lógica comercial.
- Não alterar billing.
- Não alterar autenticação.
- Não alterar middleware.
- Não alterar deploy.yml.
- Não alterar ci.yml sem necessidade.
- Não refatorar APIs antigas.
- Não recriar catálogo.
- Não recriar bronze genérico.
- Não recriar Mongo Layout Registry.
- Não remover modelos existentes.
- Não renomear tabelas existentes.
- Não criar mock permanente.
- Não marcar [x] sem evidência real.

Tarefa 1 — Validar itens de não refatoração
Revisar a seção "Fora do escopo desta sprint".
Para cada item:
- Não refatorar CADOP ativo
- Não refatorar SIB
- Não refatorar CNES
- Não refatorar DIOPS/FIP
- Não refatorar IDSS/IGR/NIP
- Não refatorar Portabilidade
- Não refatorar Prudencial
- Não refatorar Regime Especial
- Não refatorar RN623
- Não refatorar Taxa Resolutividade
- Não refatorar TISS procedimento já existente
- Não refatorar APIs atuais
- Não alterar bronze genérico

Verificar no git diff se esses pontos foram preservados.
Se foram preservados, reescrever como:
[x] Confirmado que <item> não foi refatorado.
Não marcar como [x] se houver alteração real.

Tarefa 2 — Criar APIs finais faltantes
Criar, se ainda não existirem:
- healthintel_dbt/models/api/api_plano_servico_opcional.sql
- healthintel_dbt/models/api/api_quadro_auxiliar_corresponsabilidade.sql

Requisitos:
- Usar stg_ans.stg_plano_servico_opcional.
- Usar stg_ans.stg_quadro_auxiliar_corresponsabilidade.
- Adicionar YAML.
- Adicionar tag delta_ans_100.
- Adicionar teste mínimo.
- Garantir grant.
- Criar smoke SQL.

Tarefa 3 — Criar modelos consumo_ans faltantes
Criar, se ainda não existirem:
- healthintel_dbt/models/consumo/consumo_historico_plano.sql
- healthintel_dbt/models/consumo/consumo_plano_servico_opcional.sql
- healthintel_dbt/models/consumo/consumo_tuss_procedimento_vigente.sql
- healthintel_dbt/models/consumo/consumo_tiss_utilizacao_operadora_mes.sql
- healthintel_dbt/models/consumo/consumo_sip_assistencial_operadora.sql
- healthintel_dbt/models/consumo/consumo_ressarcimento_sus_operadora.sql

Requisitos:
- Não consultar bruto_ans diretamente.
- Preferir api_ans ou staging validado conforme padrão atual.
- Adicionar YAML.
- Adicionar tags delta_ans_100.
- Adicionar testes mínimos.
- Aplicar grant para healthintel_cliente_reader.
- Criar smoke SQL.

Tarefa 4 — Fechar TUSS oficial
Garantir:
- api_ans.api_tuss_procedimento_vigente usa somente TUSS oficial.
- Nenhum modelo final de produção usa crosswalk sintético como fonte principal.
- consumo_ans.consumo_tuss_procedimento_vigente existe.
- Teste dbt codigo_tuss not null existe.
- Teste dbt descricao not null existe.
- Teste dbt de duplicidade codigo_tuss + versao_tuss existe.
- Teste dbt de vigencia_inicio <= vigencia_fim existe.
- Smoke SQL por codigo_tuss existe.
- Smoke SQL por descricao existe.

Tarefa 5 — Fechar TISS
Garantir:
- api_tiss_ambulatorial_operadora_mes mantém janela de 24 meses.
- api_tiss_hospitalar_operadora_mes mantém janela de 24 meses.
- api_tiss_plano_mes mantém janela de 24 meses.
- consumo_tiss_utilizacao_operadora_mes mantém janela de 24 meses.
- Bruto TISS pesado não é exposto para cliente.
- Consultas grandes possuem filtros obrigatórios ou documentação de uso.

Criar smokes:
- min/max competencia
- count por família
- filtro por competencia
- filtro por registro_ans quando existir

Tarefa 6 — Fechar SIP
Garantir:
- consumo_ans.consumo_sip_assistencial_operadora existe.
- relacionamento com operadora quando aplicável.
- teste de período não nulo.
- teste de volume mínimo.
- smoke por operadora/período.

Tarefa 7 — Fechar Ressarcimento SUS
Garantir:
- consumo_ans.consumo_ressarcimento_sus_operadora existe.
- datas estão tipadas.
- valores financeiros estão como decimal(18,2) quando aplicável.
- chaves de operadora/plano são validadas quando existirem.
- smoke por operadora existe.

Tarefa 8 — Fechar testes Python
Criar testes para:
- parser de produtos/planos
- parser de TUSS oficial
- parser de TISS ambulatorial
- parser de TISS hospitalar
- parser de TISS dados de planos
- parser de SIP
- parser de ressarcimento SUS
- parser de NTRP/precificação
- parser de rede/prestadores
- parser de regulatórios complementares
- parser de beneficiários/cobertura
- arquivo grande sem carregar tudo em memória
- encoding latin1, utf-8, utf-8-sig
- delimitadores ; , | tab

Tarefa 9 — Fechar testes dbt
Criar ou validar:
- not_null nas chaves principais.
- unique em dimensões vigentes.
- relationships com api_operadora/dim_operadora quando aplicável.
- accepted_values para UF.
- competencia no formato YYYYMM.
- registro_ans com 6 caracteres.
- vigência TUSS.
- retenção 24 meses para TISS.
- retenção 24 meses para RPC.
- volume mínimo por dataset.
- YAML para todo modelo novo.

Tarefa 10 — Rodar hard gates
Executar e registrar:
- docker compose ps
- ruff check api ingestao scripts testes
- pytest ingestao/tests/ -v
- pytest api/tests/ -v
- dbt debug
- dbt deps
- dbt parse
- dbt compile
- dbt build --select tag:delta_ans_100
- dbt test --select tag:delta_ans_100
- dbt docs generate
- smoke SQL
- smoke API
- validação de grants

Tarefa 11 — Criar evidências
Criar:
- docs/evidencias/ans_100_delta/README.md
- docs/evidencias/ans_100_delta/dbt_build.md
- docs/evidencias/ans_100_delta/dbt_test.md
- docs/evidencias/ans_100_delta/smoke_sql.md
- docs/evidencias/ans_100_delta/smoke_api.md
- docs/evidencias/ans_100_delta/grants.md
- docs/evidencias/ans_100_delta/tuss_oficial.md
- docs/evidencias/ans_100_delta/tiss_24_meses.md
- release notes da Sprint 41

Tarefa 12 — Atualizar checklist
Atualizar:
docs/sprints/fase10/sprint_41_delta_ans_100_faltantes.md

Regras:
- Marcar [x] somente o que foi implementado/testado.
- Não deixar [ ] sem justificativa.
- Para itens não obrigatórios de fechamento, registrar decisão formal no próprio arquivo.
- Registrar comandos executados e resultados.
- Registrar CI e deploy VPS.

Critérios finais:
- APIs finais faltantes criadas.
- consumo_ans final criado.
- TUSS oficial segura.
- TISS com retenção validada.
- SIP consumo validado.
- Ressarcimento consumo validado.
- Testes Python passaram.
- dbt build/test passou.
- Smokes SQL passaram.
- Smokes API passaram.
- Grants validados.
- Evidências salvas.
- Release notes criadas.
- Checklist atualizado.
- CI verde.
- Deploy VPS verde.

Não finalizar se:
- TUSS sintética/crosswalk sintético ainda for usado em produção.
- Alguma tabela final nova não tiver YAML.
- Alguma tabela final nova não tiver teste mínimo.
- Alguma tabela final nova não tiver grant.
- API consultar schema interno.
- TISS/RPC ignorarem retenção de 24 meses.
- Hard gates não forem executados.