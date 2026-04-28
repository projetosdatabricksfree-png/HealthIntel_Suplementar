# Histórico Sob Demanda por Cliente — Sprint 38

## Objetivo

O histórico sob demanda é o mecanismo premium para liberar competências antigas por cliente, dataset e faixa contratada, sem duplicar bases por cliente e sem alterar a carga hot padrão.

## Princípios

- A base hot continua compartilhada e enxuta.
- O histórico não é liberado por flag global.
- O acesso histórico depende de `plataforma.cliente_dataset_acesso`.
- A carga histórica depende de `plataforma.solicitacao_historico` aprovada.
- A FastAPI não lê `bruto_ans`, `nucleo_ans`, `consumo_premium_ans`, `mdm_ans` ou `mdm_privado` para servir dados.
- Rotas de dados premium continuam restritas a camadas de serviço/API (`api_ans`/`api_premium` quando houver rota histórica).
- Exportação completa permanece bloqueada no MVP.

## Modelo Operacional

### Entitlement

`plataforma.cliente_dataset_acesso` registra:

- `cliente_id`;
- `dataset_codigo`;
- `acesso_historico`;
- `competencia_inicio`;
- `competencia_fim`;
- `permite_exportacao`;
- `ativo`.

Somente registros `ativo=true` são considerados. A faixa é inclusiva: `competencia_inicio <= competencia <= competencia_fim`.

### Solicitação

`plataforma.solicitacao_historico` registra o workflow:

`pendente -> aprovada -> em_execucao -> concluida`

Falhas controladas usam `erro`. Solicitações canceladas, rejeitadas ou concluídas não são reprocessadas pela DAG.

### Backfill

`dag_historico_sob_demanda` roda a cada 15 minutos e processa uma solicitação aprovada por vez. O fluxo:

1. Seleciona uma solicitação `aprovada`.
2. Marca como `em_execucao`.
3. Valida política em `plataforma.politica_dataset`.
4. Cria partições anuais históricas com `plataforma.criar_particao_anual_competencia`.
5. Registra decisão em `plataforma.ingestao_janela_decisao`.
6. Em local/smoke, conclui em `HISTORICO_SOB_DEMANDA_DRY_RUN=true`.
7. Em produção sem extractor real configurado, falha de forma controlada.

O dry-run é apenas para teste local e valida workflow, entitlement, partição e auditoria sem baixar dados da ANS.

## Regras de Acesso

- Competência dentro da janela hot passa sem entitlement histórico.
- Competência fora da janela hot exige entitlement ativo.
- Entitlement ativo sem `acesso_historico=true` não libera histórico.
- Competência fora da faixa contratada é bloqueada.
- Limite máximo do MVP para rotas históricas: `limite <= 1000`.
- `csv_completo` e equivalentes são pós-MVP e permanecem bloqueados.

## Expiração

Histórico não é estendido automaticamente. Se a faixa contratada caducar ou o cliente precisar de novo ano, uma nova solicitação e novo entitlement são necessários.

## Pós-MVP

Ficam fora da Sprint 38 MVP:

- endpoints admin públicos;
- billing detalhado por rubrica histórica;
- rate limit avançado dedicado;
- UI/admin;
- exportação completa controlada.
