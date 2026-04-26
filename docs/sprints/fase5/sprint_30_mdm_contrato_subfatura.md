# Sprint 30 — MDM de Contrato e Subfatura (módulo privado por tenant)

**Status:** Backlog
**Fase:** Fase 5 — Enriquecimento, Qualidade e MDM sem quebrar o hardgate
**Tag de saída prevista:** `v3.5.0-mdm-privado`
**Objetivo:** validar consistência de contrato/subfatura para dados privados de clientes e cruzamentos com operadora/prestador master.
**Fim esperado:** nenhum dado premium de contrato/subfatura será publicado sem entidade master validada.
**Critério de saída:** modelos `mdm_contrato_master`, `mdm_subfatura_master` e suas tabelas `xref_*` e `*_exception` materializados; regras contratuais formalizadas como testes singulares; `tenant_id` obrigatório em todos os modelos privados.

## Contexto técnico

Contrato e subfatura **não vêm dos dados públicos abertos da ANS**. Devem entrar como módulo privado por tenant/cliente. O caso de uso clássico — Bradesco/operadora com número de contrato divergente em outra tabela — é exatamente um caso de MDM privado: o produto fica muito mais valioso porque consegue reconciliar dados públicos curados com dados internos do cliente.

## Regra-mãe

- [ ] Toda tabela MDM privada vive em schema `mdm_privado` (criar via `infra/postgres/init/028_fase5_mdm_privado_rls.sql`).
- [ ] `tenant_id` é coluna obrigatória, NOT NULL, em todos os modelos.
- [ ] `tenant_id` nasce na entrada física privada (`bruto_cliente.*`) e não pode ser inferido tardiamente no MDM.
- [ ] Row-level security: cliente só lê dados do próprio `tenant_id`.
- [ ] Nenhuma tabela pública pode receber dados de contrato/subfatura.

## Histórias

### HIS-10.0 — Criar entrada física privada por tenant

- [ ] Criar schema `bruto_cliente` em `infra/postgres/init/028_fase5_mdm_privado_rls.sql`.
- [ ] Criar tabela `bruto_cliente.contrato` com `tenant_id` NOT NULL, identificador de carga, hash de arquivo, payload bruto e colunas mínimas de contrato.
- [ ] Criar tabela `bruto_cliente.subfatura` com `tenant_id` NOT NULL, identificador de carga, hash de arquivo, payload bruto e colunas mínimas de subfatura.
- [ ] Definir layout privado por tenant para contrato e subfatura, com fingerprint, versão, score de confiança e fallback para quarentena quando o layout não for reconhecido.
- [ ] Criar processo de carga privada idempotente, com deduplicação por `tenant_id`, fonte, competência e hash de arquivo.
- [ ] Criar `healthintel_dbt/models/staging/cliente/stg_cliente_contrato.sql`.
- [ ] Criar `healthintel_dbt/models/staging/cliente/stg_cliente_subfatura.sql`.
- [ ] Criar documentação `_staging_cliente.yml` com testes `not_null` para `tenant_id`, identificador de origem e chaves mínimas.
- [ ] Garantir que `healthintel_cliente_reader` não tem acesso a `bruto_cliente`, `stg_cliente` nem `mdm_privado`.

### HIS-10.1 — Criar contrato master

- [ ] Criar `healthintel_dbt/models/mdm_privado/mdm_contrato_master.sql`.
- [ ] Criar `healthintel_dbt/models/mdm_privado/xref_contrato_origem.sql`.
- [ ] Usar `stg_cliente_contrato` como fonte obrigatória; não modelar contrato master sem origem física privada.
- [ ] Criar `contrato_master_id` (UUID v5 baseado em tenant + número canônico).
- [ ] Criar `tenant_id` (NOT NULL).
- [ ] Criar `operadora_master_id` (FK lógica para `mdm_operadora_master`).
- [ ] Criar `empresa_contratante_master_id`.
- [ ] Criar `numero_contrato_canonico`.
- [ ] Criar `numero_contrato_normalizado`.
- [ ] Criar `tipo_contrato`.
- [ ] Criar `vigencia_inicio`.
- [ ] Criar `vigencia_fim`.
- [ ] Criar `status_contrato` (ATIVO | SUSPENSO | ENCERRADO | EM_RENEGOCIACAO).
- [ ] Criar `mdm_confidence_score`.
- [ ] Criar `mdm_status`.

### HIS-10.2 — Criar subfatura master

- [ ] Criar `healthintel_dbt/models/mdm_privado/mdm_subfatura_master.sql`.
- [ ] Criar `healthintel_dbt/models/mdm_privado/xref_subfatura_origem.sql`.
- [ ] Usar `stg_cliente_subfatura` como fonte obrigatória; não modelar subfatura master sem origem física privada.
- [ ] Criar `subfatura_master_id`.
- [ ] Criar `contrato_master_id` (FK lógica obrigatória).
- [ ] Criar `tenant_id` (NOT NULL).
- [ ] Criar `codigo_subfatura_canonico`.
- [ ] Criar `codigo_subfatura_normalizado`.
- [ ] Criar `centro_custo`.
- [ ] Criar `unidade_negocio`.
- [ ] Criar `vigencia_inicio`.
- [ ] Criar `vigencia_fim`.
- [ ] Criar `status_subfatura`.
- [ ] Criar `mdm_confidence_score`.

### HIS-10.3 — Criar regras de validação contratual

- [ ] Criar regra (teste singular): subfatura não pode existir sem `contrato_master_id` válido.
- [ ] Criar regra: subfatura não pode migrar de contrato sem evento de migração registrado.
- [ ] Criar regra: contrato não pode apontar para duas `operadora_master_id` ativas no mesmo período.
- [ ] Criar regra: o mesmo número de contrato não pode representar contratos diferentes no mesmo `tenant_id` sem crosswalk aprovado.
- [ ] Criar regra: contrato com CNPJ de operadora divergente da validação Serpro deve ir para exceção bloqueante.
- [ ] Criar regra: contrato com operadora sem `operadora_master_id` deve ir para quarentena.
- [ ] Criar regra: subfatura duplicada por contrato + competência deve ir para exceção.
- [ ] Materializar cada regra como `assert_*.sql` em `healthintel_dbt/tests/`.

### HIS-10.4 — Criar tabelas de exceção MDM

- [ ] Criar `healthintel_dbt/models/mdm_privado/mdm_contrato_exception.sql`.
- [ ] Criar `healthintel_dbt/models/mdm_privado/mdm_subfatura_exception.sql`.
- [ ] Criar `healthintel_dbt/models/mdm_privado/mdm_operadora_contrato_exception.sql`.
- [ ] Criar `healthintel_dbt/models/mdm_privado/mdm_prestador_contrato_exception.sql`.
- [ ] Criar campo `exception_type`.
- [ ] Criar campo `exception_severity` (INFO | WARNING | BLOCKING).
- [ ] Criar campo `exception_message`.
- [ ] Criar campo `is_blocking` (bit).
- [ ] Criar campo `resolved_at`.
- [ ] Criar campo `resolved_by`.
- [ ] Criar campo `resolution_comment`.

## Entregas esperadas

- [ ] Bootstrap privado em `infra/postgres/init/028_fase5_mdm_privado_rls.sql` (`bruto_cliente`, `mdm_privado`, grants, revokes e RLS)
- [ ] Tabelas `bruto_cliente.contrato` e `bruto_cliente.subfatura`
- [ ] Modelos `stg_cliente_contrato` e `stg_cliente_subfatura`
- [ ] 2 modelos master (`mdm_contrato_master`, `mdm_subfatura_master`)
- [ ] 2 modelos `xref_*_origem`
- [ ] 4 modelos `*_exception`
- [ ] 7 testes singulares de regra contratual
- [ ] `_mdm_privado.yml` documentando todos os modelos
- [ ] `docs/fase5/mdm_contrato_subfatura.md` explicando o módulo privado

## Validação esperada (hard gates)

- [ ] `dbt build --select tag:mdm_privado` zero erros.
- [ ] `dbt test --select tag:mdm_privado` zero falhas.
- [ ] Toda linha de `mdm_contrato_master` e `mdm_subfatura_master` tem `tenant_id IS NOT NULL`.
- [ ] Toda linha em `bruto_cliente.contrato`, `bruto_cliente.subfatura`, `stg_cliente_contrato` e `stg_cliente_subfatura` tem `tenant_id IS NOT NULL`.
- [ ] Nenhuma exceção bloqueante pode existir em produto premium da Sprint 31 (validação cruzada).
- [ ] Schema `mdm_privado` não é acessível pela role `healthintel_cliente_reader` em consultas cruzadas de tenant.

## Resultado Esperado

Sprint 30 fecha a camada MDM com o módulo privado de contrato e subfatura. O produto premium ganha a capacidade rara de reconciliar dados públicos da ANS com dados internos do cliente — o diferencial competitivo central da plataforma. Nenhum modelo público é tocado.
