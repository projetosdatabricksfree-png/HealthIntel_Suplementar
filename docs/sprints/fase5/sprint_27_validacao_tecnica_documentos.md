# Sprint 27 — Validação Técnica de CPF, CNPJ, CNES e Registro ANS

**Status:** Implementada em código — pendente validação em ambiente (hardgates `[ ]`).
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate.
**Tag de saída prevista:** `v3.2.0-dq-documental` (somente após hardgates verdes).
**Commit de implementação:** `f0cecc1` — `feat: implement data quality layer with dbt macros, tests and shared python utils`.
**Baseline congelado:** `v3.0.0` (commit `fe7b839`). Não alterado por esta sprint.
**Schema novo:** `quality_ans` (já configurado em `healthintel_dbt/dbt_project.yml`, bloco `models.healthintel_dbt.quality`, `+materialized: table`, `+tags: ["quality"]`).
**Objetivo:** adicionar validação técnica de documentos (CPF/CNPJ/CNES/registro_ans) sem alterar staging, marts, API, consumo, macros ou seeds aprovados na Fase 4.
**Critério de saída técnico:** biblioteca Python `healthintel_quality.validators.documentos` com testes; 7 macros dbt novas em `healthintel_dbt/macros/`; 4 modelos `dq_*` em `healthintel_dbt/models/quality/` com `_quality.yml`; 6 testes singulares `assert_*.sql`; nenhum byte de modelo do baseline `v3.0.0` modificado.
**Critério de saída operacional:** `pytest testes/unit/test_documentos.py -v` zero falhas; `dbt compile` zero erros; `dbt build --select tag:quality` sucesso; `dbt test --select tag:quality` zero falhas; diff contra `v3.0.0` mostra zero alteração em `stg_*`, `int_*`, `fat_*`, `mart_*`, `api_*`, `consumo_*` e `normalizar_registro_ans.sql`.

## Regra-mãe (não negociável)

- [x] Não alterar `stg_cadop`, `stg_cnes_estabelecimento`, `stg_*` existentes nem a macro `normalizar_registro_ans.sql` (mantida íntegra; novas macros entraram como arquivos novos).
- [x] Toda lógica nova entra em arquivos novos (macros, modelos `quality/`, biblioteca Python e testes singulares — todos criados como novos artefatos no commit `f0cecc1`).
- [x] Diretório `healthintel_dbt/models/quality/` configurado em `dbt_project.yml` com `+schema: quality_ans`, `+materialized: table` e `+tags: ["quality"]`, conforme `governanca_minima_fase5.md`.
- [x] Validação de CPF é técnica e reutilizável, mas CPF não entra em produto público derivado da ANS (a biblioteca Python expõe `validar_cpf_digito`/`classificar_documento`; nenhuma tabela `dq_*` ou `consumo_premium_*` materializa CPF).

## Contrato Arquitetural da Sprint

| Item | Valor |
|------|-------|
| Camada criada | Qualidade técnica documental. |
| Schema físico | `quality_ans` (interno; não publicado em FastAPI nem em SQL direto cliente). |
| Tag dbt | `quality` (e tags secundárias por domínio: `documento`, `cadop`, `cnes`, `operadora`, `prestador`). |
| Materialização | `table`. |
| Upstream permitido | `stg_cadop`, `stg_cnes_estabelecimento`, `stg_rede_assistencial`, `dim_operadora_atual`. |
| Downstream esperado | Sprint 28 (filtragem prévia de CNPJ válido para Serpro), Sprints 29–31 (MDM e premium consumindo `documento_quality_status`). |
| Owner técnico | Engenharia de dados HealthIntel. |
| Owner de negócio | Produto HealthIntel. |
| Classificação LGPD | Pública ANS/DATASUS (CNPJ, CNES, registro_ans) + Interna operacional (status/motivo). |
| Regra de publicação | Interna apenas. Nenhum `dq_*` é exposto pela FastAPI ou por `consumo_ans`/`consumo_premium_ans`. Exposição futura, se houver, ocorre via `api_ans.api_premium_*` numa sprint posterior. |
| Regra de rollback | `drop schema quality_ans cascade` + remoção dos arquivos `quality/`, das 7 macros novas, dos 6 `assert_*` novos e da biblioteca Python. Baseline `v3.0.0` permanece intacto. |

## Os Quatro Estados Documentais (obrigatório nas tabelas `dq_*`)

A coluna `documento_quality_status` separa explicitamente — nunca colapsa em `NULL` opaco — os quatro estados exigidos pela skill `healthintel-data-quality-contracts`:

| Status | Significado | Causa típica |
|--------|-------------|--------------|
| `VALIDO` | Documento normalizado, com tamanho e dígito verificador corretos. | Caso esperado. |
| `INVALIDO_FORMATO` | Documento presente mas tamanho diferente do esperado (CNPJ ≠ 14, CNES ≠ 7, registro_ans ≠ 6). | Erro de digitação na fonte ANS/DATASUS. |
| `INVALIDO_DIGITO` | Tamanho ok mas dígito verificador falha. | Documento corrompido/forjado/transcrito errado. |
| `SEQUENCIA_INVALIDA` | Documento composto por dígito repetido (`00000…`, `11111…`). | Preenchimento defensivo da fonte. |
| `NULO` | Documento ausente no contrato atual da fonte (ex.: `stg_rede_assistencial` é agregado e não traz CNPJ/CNES individual). | Limitação contratual da fonte — não é erro técnico. |

A coluna `motivo_invalidade_documento` traz texto humano apenas quando o status difere de `VALIDO`.

## Histórias

### HIS-07.1 — Biblioteca Python de documentos

Local: `shared/python/healthintel_quality/validators/documentos.py` (123 linhas, commit `f0cecc1`).

- [x] `shared/python/healthintel_quality/validators/documentos.py` criado.
- [x] `normalizar_cpf` — remove não-dígitos, sem completar zeros artificiais.
- [x] `normalizar_cnpj` — remove não-dígitos, sem completar zeros artificiais.
- [x] `validar_cpf_digito` — valida tamanho 11, sequência repetida e dígitos verificadores.
- [x] `validar_cnpj_digito` — valida tamanho 14, sequência repetida e dígitos verificadores.
- [x] `classificar_documento` — retorna `Literal["CPF", "CNPJ", "INVALIDO"]`.
- [x] `gerar_hash_documento` — SHA-256 com salt configurável via `HEALTHINTEL_DOCUMENTO_HASH_SALT`; nunca usa salt hardcoded; retorna `None` para inválido.
- [x] Bloqueio para sequências repetidas (`_is_sequencia_invalida`) cobre CPF e CNPJ.
- [x] Testes unitários em `testes/unit/test_documentos.py` (66 linhas).
- [x] Nenhuma chamada HTTP externa; biblioteca puramente local (sem dependência de `requests`/`httpx`).

### HIS-07.2 — Macros dbt novas (sem alterar as existentes)

Locais em `healthintel_dbt/macros/`, todos commit `f0cecc1`:

- [x] `normalizar_cnpj.sql` — `regexp_replace` + cast textual; preserva `null`.
- [x] `normalizar_cpf.sql` — idem para CPF (uso interno; não consumida por modelos `dq_*` públicos).
- [x] `validar_cnpj_digito.sql` — calcula DV1 e DV2 em SQL puro; sequência repetida bloqueada.
- [x] `validar_cpf_digito.sql` — idem para CPF; uso restrito a fluxos privados/tenant futuros.
- [x] `normalizar_cnes.sql` — pad-left zero até 7 dígitos quando aplicável.
- [x] `validar_cnes_formato.sql` — valida exatamente 7 dígitos numéricos.
- [x] `validar_registro_ans_formato.sql` — valida 6 dígitos numéricos sem alterar `normalizar_registro_ans.sql`.
- [x] `normalizar_registro_ans.sql` permanece **byte-idêntica** ao baseline `v3.0.0` (verificável por `git diff v3.0.0 -- healthintel_dbt/macros/normalizar_registro_ans.sql`).

### HIS-07.3 — Tabelas novas de qualidade documental

Locais em `healthintel_dbt/models/quality/`, todos commit `f0cecc1`:

- [x] `dq_cadop_documento.sql` — granularidade `registro_ans`; upstream `stg_cadop`. Tags `quality, documento, cadop`.
- [x] `dq_cnes_documento.sql` — granularidade `competencia, cnes`; upstream `stg_cnes_estabelecimento`. Tags `quality, documento, cnes`.
- [x] `dq_operadora_documento.sql` — granularidade `operadora_id`; upstream `dim_operadora_atual`. Tags `quality, documento, operadora`.
- [x] `dq_prestador_documento.sql` — granularidade `competencia, registro_ans, cd_municipio, segmento, tipo_prestador`; upstream `stg_rede_assistencial`. Status `NULO` explícito porque o contrato agregado não traz CNPJ/CNES individual; nenhum mock criado. Tags `quality, documento, prestador`.
- [x] Coluna `cnpj_normalizado` presente em CADOP, CNES, operadora e prestador.
- [x] Coluna `cnpj_tamanho_valido` presente nas quatro tabelas.
- [x] Coluna `cnpj_digito_valido` presente nas quatro tabelas.
- [x] Coluna `cnpj_is_sequencia_invalida` presente nas quatro tabelas.
- [x] Coluna `documento_quality_status` ∈ {`VALIDO`, `INVALIDO_FORMATO`, `INVALIDO_DIGITO`, `SEQUENCIA_INVALIDA`, `NULO`} em todas.
- [x] Coluna `motivo_invalidade_documento` (texto humano) presente nas quatro tabelas.
- [x] `_quality.yml` (245 linhas) com descrição por tabela contendo responsabilidade, granularidade, upstream, downstream, owner técnico, owner de negócio, classificação LGPD, regra de publicação e regra de rollback.
- [x] `_quality.yml` com testes `not_null` em chaves de negócio e `accepted_values` em `documento_quality_status` para todas as quatro tabelas.

### HIS-07.4 — Testes de qualidade técnica

Locais em `healthintel_dbt/tests/`, todos commit `f0cecc1`:

- [x] `assert_cnpj_14_digitos_quando_preenchido.sql`.
- [x] `assert_cnpj_digito_valido_cadop.sql`.
- [x] `assert_cnpj_digito_valido_cnes.sql`.
- [x] `assert_cnes_7_digitos.sql`.
- [x] `assert_registro_ans_6_digitos_em_mdm.sql`.
- [x] `assert_sem_documento_invalido_em_consumo_premium.sql` (já preparado para Sprint 31; falha somente quando `consumo_premium_ans` existir e contiver documento inválido).

## Entregas materializadas (commit `f0cecc1`)

| Entrega | Caminho | Status físico |
|---------|---------|---------------|
| Biblioteca Python | `shared/python/healthintel_quality/validators/documentos.py` | Presente (123 linhas). |
| Testes unitários | `testes/unit/test_documentos.py` | Presente (66 linhas). |
| Macros novas | `healthintel_dbt/macros/{normalizar_cnpj,normalizar_cpf,validar_cnpj_digito,validar_cpf_digito,normalizar_cnes,validar_cnes_formato,validar_registro_ans_formato}.sql` | 7 arquivos presentes. |
| Modelos dbt | `healthintel_dbt/models/quality/{dq_cadop_documento,dq_cnes_documento,dq_operadora_documento,dq_prestador_documento}.sql` | 4 arquivos presentes. |
| Documentação dbt | `healthintel_dbt/models/quality/_quality.yml` | Presente (245 linhas, contrato completo). |
| Testes singulares | `healthintel_dbt/tests/assert_{cnpj_14_digitos_quando_preenchido,cnpj_digito_valido_cadop,cnpj_digito_valido_cnes,cnes_7_digitos,registro_ans_6_digitos_em_mdm,sem_documento_invalido_em_consumo_premium}.sql` | 6 arquivos presentes. |
| Configuração dbt | `healthintel_dbt/dbt_project.yml` (bloco `models.healthintel_dbt.quality`) | Presente. |

## Validação esperada (hard gates)

Cada item abaixo precisa de evidência objetiva (saída de comando) antes de ser marcado `[x]`. A skill `healthintel-sprint-release-hardgates` proíbe marcar antes da execução real.

- [ ] `pytest testes/unit/test_documentos.py -v` — zero falhas, cobertura ≥ 95%.
- [ ] `dbt deps && dbt compile` — zero erros.
- [ ] `dbt build --select tag:quality` — sucesso (4 modelos, materialização `table` em `quality_ans`).
- [ ] `dbt test --select tag:quality` — zero falhas (testes genéricos do `_quality.yml` + testes singulares aplicáveis).
- [ ] `git diff --stat v3.0.0 -- healthintel_dbt/models/staging healthintel_dbt/models/intermediate healthintel_dbt/models/marts healthintel_dbt/models/api healthintel_dbt/models/consumo healthintel_dbt/macros/normalizar_registro_ans.sql` — saída vazia.
- [ ] `git ls-tree v3.0.0 -- healthintel_dbt/macros/normalizar_registro_ans.sql` versus `git ls-tree HEAD -- healthintel_dbt/macros/normalizar_registro_ans.sql` retornam o mesmo blob hash.
- [ ] `psql -d healthintel -c "\dt quality_ans.*"` lista exatamente as 4 tabelas `dq_*`.
- [ ] Inspeção: nenhum modelo `dq_*` faz chamada HTTP, importa Python externo ou consulta schema interno fora do upstream declarado.

## Distinção Estado Atual vs Estado-Alvo

| Eixo | Estado atual (HEAD `a311443`) | Estado-alvo da Sprint 27 |
|------|-------------------------------|--------------------------|
| Arquivos | Todos os artefatos das HIS-07.1 a 07.4 presentes em disco. | Idem. |
| Testes Python | Existem (`test_documentos.py`); execução não verificada nesta sessão. | `pytest -v` aprovado com cobertura ≥ 95%. |
| Build dbt | Não verificado nesta sessão. | `dbt build --select tag:quality` aprovado. |
| Testes dbt | Não verificados nesta sessão. | `dbt test --select tag:quality` aprovado. |
| Schema físico `quality_ans` | Não confirmado em PostgreSQL local. | Schema criado e populado pelos 4 `dq_*`. |
| Não regressão `v3.0.0` | Esperada por construção (arquivos novos), pendente verificação por `git diff`. | Verificada por diff explícito. |
| Tag `v3.2.0-dq-documental` | Não criada. | Criada **somente** após todos os hardgates verdes. |

## Comandos de validação local

```bash
# Python
PYTHONPATH=shared/python pytest testes/unit/test_documentos.py -v --cov=healthintel_quality.validators.documentos --cov-report=term-missing

# dbt
cd healthintel_dbt
dbt deps
dbt compile
dbt build --select tag:quality
dbt test --select tag:quality
cd -

# Não regressão contra v3.0.0
git diff --stat v3.0.0 -- \
  healthintel_dbt/models/staging \
  healthintel_dbt/models/intermediate \
  healthintel_dbt/models/marts \
  healthintel_dbt/models/api \
  healthintel_dbt/models/consumo \
  healthintel_dbt/macros/normalizar_registro_ans.sql

# Schema físico
psql "$DATABASE_URL" -c "\dt quality_ans.*"
psql "$DATABASE_URL" -c "select documento_quality_status, count(*) from quality_ans.dq_cadop_documento group by 1 order by 1;"
```

## Anti-padrões explicitamente rejeitados nesta sprint

- Alterar `stg_*`, marts ou `consumo_*` para “embutir” validação de documento (proibido pela regra-mãe da Fase 5).
- Materializar CPF em `quality_ans`, `consumo_ans` ou `consumo_premium_ans`.
- Tratar ausência contratual (rede assistencial agregada sem CNPJ/CNES) como “erro de pipeline”; o status correto é `NULO` com motivo explícito.
- Relaxar `accepted_values` ou `not_null` para “fazer o build passar”.
- Criar nome `validar_cnpj_digito` colidindo com macro existente — neste sprint a macro é nova, sem colisão verificada por `git ls-tree v3.0.0 -- healthintel_dbt/macros/`.
- Marcar hardgates `[x]` antes de executar os comandos correspondentes (proibido pela skill `healthintel-sprint-release-hardgates`).

## Pendências e riscos conhecidos

- Hardgates de execução (pytest, dbt build, dbt test) ainda não foram registrados nesta sprint; até lá a sprint permanece em **Implementada — pendente validação**, nunca **Concluída**.
- Cobertura ≥ 95% exigida em `testes/unit/test_documentos.py` precisa ser confirmada por `--cov-report` real.
- `assert_sem_documento_invalido_em_consumo_premium.sql` só fica efetivamente exercitado quando a Sprint 31 publicar `consumo_premium_ans`; até lá ele é `pass-through` por construção.
- A coluna `_layout_id`/`_layout_versao_id`/`_hash_arquivo`/`_hash_estrutura` em `dq_cnes_documento` depende da presença desses campos em `stg_cnes_estabelecimento` aprovado em `v3.0.0`; verificar antes do `dbt build`.
- Tag `v3.2.0-dq-documental` **não** deve ser criada até que todos os hardgates fiquem verdes em CI ou ambiente reproduzível.

## Resultado Esperado

Sprint 27 entrega a primeira camada de qualidade técnica documental da Fase 5. CPF, CNPJ, CNES e registro_ans passam a ter validação digital verdadeira em tabelas `dq_*` paralelas, no schema `quality_ans`, sem que nenhum modelo aprovado em `v3.0.0` seja tocado. As macros e a biblioteca Python ficam disponíveis como insumo direto das Sprints 28 (Serpro/CNPJ), 29 (MDM público), 30 (MDM privado) e 31 (produtos premium). A coluna `documento_quality_status` materializa o contrato dos quatro estados (válido, formato, dígito, sequência, nulo) e impede que “ausência” e “erro” sejam confundidos a jusante.
