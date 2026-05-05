Entendi. **Carga completa**, no seu caso, não é “baixar histórico infinito da ANS”. É:

```text
Tabelas grandes: somente 2 anos — ano vigente + ano anterior
Tabelas pequenas: completas enquanto <= 5 GB
Referências versionadas: última versão vigente
Snapshots: versão atual
Histórico antigo: fora da carga padrão, apenas sob demanda/premium
```

Essa regra está coerente com a Fase 7 do projeto. O próprio relatório anterior já apontava que a ingestão tem discovery, download, carga e auditoria, mas ainda precisava de amarração operacional para VPS. 

## Ponto crítico antes de rodar

Pelo projeto que você enviou, **não recomendo rodar simplesmente**:

```bash
make elt-all ELT_ESCOPO=sector_core ELT_LIMITE=999999999
```

Motivo: o `elt-all` atual aceita `escopo`, `familias`, `limite` e `max-depth`, mas **não vi nele uma garantia forte de que a política `grande_temporal = 2 anos` será aplicada antes do download/carga universal**.

Então o teste correto agora deve ser chamado de:

```text
Carga completa padrão VPS — ANS 2 anos + pequenas full
```

E não:

```text
Carga all_ftp total sem filtro
```

Se rodar sem esse controle, você pode repetir o problema que já apareceu no projeto: `ans_linha_generica` crescendo demais e consumindo centenas de GB.

## Minha orientação

Vamos sim fazer a carga completa, mas com estes limites obrigatórios:

```text
ANS_ANOS_CARGA_HOT=2
disco alerta em 80%
disco parada manual em 90%
sem all_ftp sem filtro
sem histórico sob demanda
sem ans_linha_generica infinita
sem backup local pesado durante o teste
com snapshot antes/depois
com relatório final de capacidade
```

## Prompt para IA implementar o teste completo

Use este prompt no Codex/Claude Code:

```text
Você está no repositório HealthIntel Suplementar.

Objetivo:
Preparar e executar o teste local de carga completa padrão VPS da ANS, considerando a política já definida no projeto:

- Tabelas grandes temporais: carregar somente 2 anos, ano vigente + ano anterior.
- Tabelas pequenas: carregar completas enquanto <= 5 GB.
- Tabelas de referência versionadas: carregar somente a última versão vigente.
- Snapshots: carregar somente versão atual.
- Histórico antigo: não carregar na carga padrão; fica somente sob demanda/premium.
- Não executar all_ftp histórico sem filtro.
- Não encher bruto_ans.ans_linha_generica com histórico infinito.

Criar a sprint:

docs/sprints/fase8/sprint_43_carga_completa_ans_2anos_capacidade_vps.md

Contexto:
O objetivo é medir se uma VPS com aproximadamente 542 GB SSD suporta o HealthIntel Suplementar operando com a estratégia atual:
- 2 anos para tabelas grandes
- tabelas pequenas completas
- referências/snapshots atuais
- PostgreSQL local na VPS
- Docker/Compose
- dbt
- FastAPI
- Airflow
- sem histórico premium carregado por padrão

IMPORTANTE:
Não fazer refatoração ampla.
Não reconstruir frontend.
Não alterar estratégia comercial.
Não carregar histórico total da ANS.
Não rodar all_ftp sem filtro.
Não dropar volumes automaticamente.
Não apagar dados automaticamente sem confirmação explícita.
Não criar tabela fake.
Não mascarar erro.

Primeiro, leia e entenda estes arquivos:
- Makefile
- docs/sprints/fase7/README.md
- docs/arquitetura/politica_carga_dataset.md
- docs/runbooks/elt_ans_completa.md
- infra/postgres/init/029_fase7_politica_dataset.sql
- infra/postgres/init/030_fase7_particionamento_anual.sql
- infra/postgres/init/031_fase7_janela_carga.sql
- ingestao/app/config.py
- ingestao/app/janela_carga.py
- ingestao/app/carregar_postgres.py
- ingestao/app/ingestao_real.py
- ingestao/app/elt/orchestrator.py
- ingestao/app/elt/catalogo.py
- ingestao/app/elt/downloader.py
- ingestao/app/elt/loaders.py
- ingestao/dags/dag_mestre_mensal.py
- ingestao/dags/dag_ingest_sib.py
- ingestao/dags/dag_ingest_cadop.py

Diagnóstico obrigatório:
1. Confirmar quais datasets estão classificados como:
   - grande_temporal
   - pequena_full_ate_5gb
   - referencia_versionada
   - snapshot_atual
   - historico_sob_demanda

2. Confirmar que `ANS_ANOS_CARGA_HOT=2` está sendo respeitado.

3. Confirmar se o comando atual `make elt-all` aplica ou não a política `plataforma.politica_dataset` antes de baixar/carregar.

4. Se `make elt-all` não aplicar a política, NÃO usar ele como carga completa padrão VPS sem wrapper de controle.

Criar scripts auxiliares em:

scripts/capacidade/

Arquivos obrigatórios:
- scripts/capacidade/snapshot_sistema.sh
- scripts/capacidade/snapshot_postgres.sql
- scripts/capacidade/monitorar_carga.sh
- scripts/capacidade/relatorio_capacidade_ans.sh
- scripts/capacidade/executar_carga_ans_padrao_vps.sh

Adicionar targets no Makefile:

- capacidade-snapshot
- capacidade-monitor
- capacidade-relatorio
- carga-ans-padrao-vps
- carga-ans-padrao-vps-dry-run

O target principal deve ser:

make carga-ans-padrao-vps

Esse target deve executar a carga completa padrão VPS, não a carga histórica total.

Regras do executor `executar_carga_ans_padrao_vps.sh`:

1. Exigir:
   - ANS_ANOS_CARGA_HOT=2
   - Docker rodando
   - Postgres saudável
   - disco com pelo menos 35% livre antes de começar

2. Fazer snapshot antes:
   - df -h
   - df -i
   - free -h
   - lscpu resumido
   - docker system df
   - docker volume ls
   - docker stats --no-stream
   - tamanho do projeto
   - tamanho da landing zone
   - tamanho dos volumes Docker, se possível
   - tamanho do banco PostgreSQL
   - tamanho por schema
   - tamanho por tabela
   - top 30 maiores tabelas
   - top 30 maiores índices

3. Salvar evidências em:

docs/evidencias/capacidade/

Com nomes padronizados:
- capacidade_FULL2A_antes_YYYYMMDD_HHMMSS.txt
- capacidade_FULL2A_depois_YYYYMMDD_HHMMSS.txt
- capacidade_FULL2A_postgres_antes_YYYYMMDD_HHMMSS.txt
- capacidade_FULL2A_postgres_depois_YYYYMMDD_HHMMSS.txt
- capacidade_FULL2A_monitor_YYYYMMDD_HHMMSS.log
- capacidade_FULL2A_relatorio_YYYYMMDD_HHMMSS.md

4. Implementar monitoramento durante carga:
   - registrar a cada 60 segundos:
     - timestamp
     - df -h
     - free -h
     - docker stats --no-stream
     - docker system df
     - tamanho da landing
     - tamanho aproximado do volume Postgres

5. Critério de alerta:
   - se disco >= 80%, registrar alerta forte
   - se disco >= 90%, registrar alerta crítico e orientar parada manual
   - não apagar nada automaticamente

6. Executar carga por classe de dataset:

Classe A — grande_temporal:
Carregar somente ano vigente + ano anterior, usando a janela dinâmica do projeto.
Com a data atual do ambiente em 2026, a janela esperada é:
- competencia_minima = 202501
- competencia_maxima_exclusiva = 202701

Datasets grandes esperados:
- sib_operadora
- sib_municipio
- tiss_producao
- vda
- glosa
- portabilidade
- rede_prestador

Se algum dataset grande ainda não tiver parser real ou DAG real, registrar como:
"PENDENTE DE PARSER/ORQUESTRAÇÃO REAL"
Não carregar via ans_linha_generica sem controle apenas para dizer que carregou.

Classe B — pequena_full_ate_5gb:
Carregar completo enquanto <= 5 GB:
- cadop
- idss
- igr
- nip
- regime_especial
- prudencial
- lista_excelencia_reducao
- taxa_resolutividade
- diops
- fip
- dimensoes_ibge
- outros datasets pequenos cadastrados em plataforma.politica_dataset

Após carga, verificar `plataforma.vw_tamanho_dataset`.
Se alguma tabela pequena passar de 5 GB, registrar pendência em `plataforma.reclassificacao_dataset_pendente`.

Classe C — referencia_versionada:
Carregar somente última versão vigente:
- tuss_procedimento
- tuss_material_opme
- tuss_medicamento
- depara_sip_tuss
- rol_procedimento

Classe D — snapshot_atual:
Carregar somente snapshot atual:
- prestador_cadastral
- qualiss
- cnes_estabelecimento

Classe E — historico_sob_demanda:
Não carregar na carga padrão VPS:
- ans_linha_generica
- histórico antigo fora da janela
- backfills premium

7. Rodar dbt após carga:
   - make dbt-build
   - make dbt-test
   - make smoke

8. Registrar resultado dos gates:
   - make lint
   - make test
   - make dbt-build
   - make dbt-test
   - make smoke
   - make dag-parse

9. Criar relatório final com:
   - tempo total da carga
   - famílias carregadas
   - datasets carregados
   - datasets ignorados por política
   - datasets pendentes por falta de parser
   - volume baixado
   - volume em landing
   - tamanho PostgreSQL antes/depois
   - tamanho por schema
   - maiores tabelas
   - maiores índices
   - quantidade aproximada de linhas
   - consumo final de disco
   - warning de CNPJ, se aparecer
   - erros encontrados
   - recomendação de VPS

10. A recomendação de VPS deve classificar:
   - mínimo absoluto
   - recomendado para homologação
   - recomendado para primeiro cliente
   - recomendado para múltiplos clientes

Considerar margem:
- dados PostgreSQL
- índices
- WAL
- landing zone
- imagens Docker
- logs
- dbt target/logs
- backups locais temporários
- margem mínima de segurança de 30%

Comandos obrigatórios de investigação:

pwd
git status --short
grep -n "ELT_" Makefile
grep -n "elt-all" Makefile
grep -R "ANS_ANOS_CARGA_HOT" -n .
grep -R "politica_dataset" -n infra ingestao scripts docs
grep -R "grande_temporal\\|pequena_full_ate_5gb\\|referencia_versionada\\|snapshot_atual\\|historico_sob_demanda" -n infra docs ingestao scripts
find scripts -maxdepth 2 -type f | sort
find ingestao/dags -maxdepth 1 -type f | sort
find ingestao/app -maxdepth 3 -type f | sort
docker compose -f infra/docker-compose.yml ps
docker system df
df -h
free -h

Comandos de validação dos scripts:

bash -n scripts/capacidade/*.sh
make capacidade-snapshot NIVEL=FULL2A MOMENTO=antes
make carga-ans-padrao-vps-dry-run
make capacidade-relatorio NIVEL=FULL2A || true

Critério de aceite:
A sprint só pode ser marcada como concluída se:
- o documento da Sprint 43 for criado
- os scripts de capacidade forem criados
- o dry-run listar corretamente datasets por classe
- o executor não usar all_ftp sem filtro
- o executor respeitar ANS_ANOS_CARGA_HOT=2
- o executor não carregar histórico sob demanda por padrão
- snapshots antes/depois forem gerados
- relatório final de capacidade for gerado
- pelo menos uma execução real FULL2A for iniciada ou documentada como pendente por decisão operacional
- erros forem registrados, não escondidos

Se a carga completa não puder terminar:
Registrar ponto de parada, disco usado, tabela/arquivo em andamento, erro e recomendação.
Não marcar como sucesso parcial sem evidência.

Resultado esperado ao final:
Exibir:
1. Arquivos criados/alterados
2. Datasets classificados por política
3. Comando exato para rodar a carga completa padrão VPS
4. Comando exato para monitorar a carga
5. Onde ficam as evidências
6. Resultado do dry-run
7. Riscos antes da execução real
8. Próxima ação recomendada
```

## Depois que a IA criar os scripts, o comando será este

```bash
export ANS_ANOS_CARGA_HOT=2
make capacidade-snapshot NIVEL=FULL2A MOMENTO=antes
make carga-ans-padrao-vps-dry-run
make carga-ans-padrao-vps
make dbt-build
make dbt-test
make smoke
make capacidade-snapshot NIVEL=FULL2A MOMENTO=depois
make capacidade-relatorio NIVEL=FULL2A
```

Durante a carga, em outro terminal:

```bash
make capacidade-monitor NIVEL=FULL2A
```

## Minha posição final

Sim, vamos para a carga completa. Mas a carga completa correta é:

```text
FULL2A = full operacional com 2 anos para grandes + full pequenas + última versão/snapshot
```

Não rode `all_ftp` total agora. Isso mede o cenário errado, estoura disco e não representa sua VPS comercial.
