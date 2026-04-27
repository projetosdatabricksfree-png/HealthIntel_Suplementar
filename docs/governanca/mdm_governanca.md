# MDM — Master Data Management

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir a governança de Master Data Management (MDM) para entidades públicas e privadas na plataforma HealthIntel Suplementar.

---

## Golden Record

### Definição

Golden record é o registro canônico de uma entidade, resultante da aplicação de survivorship rules sobre múltiplas fontes.

### Survivorship Rule

1. **Operadora**: CADOP é fonte primária. DIOPS, SIB e TISS complementam atributos.
2. **Estabelecimento**: CNES ST é fonte primária. SIB complementa.
3. **Prestador**: CNES ST + TISS.
4. **Contrato**: dados do tenant são fonte única (sem dedup entre tenants).
5. **Subfatura**: dados do tenant, consistência com contrato.

---

## Crosswalk

### Definição

Crosswalk (`xref_*`) é a tabela de mapeamento entre identificadores de origem e o master ID.

### Regras

1. Todo crosswalk é versionado — inclui competência.
2. Crosswalk nunca remove registros, apenas marca `mdm_status = EXCLUIDO`.
3. Aprovação manual de crosswalk é permitida para registros ambíguos.
4. Trilha de auditoria registra quem aprovou, quando e por quê.

---

## Entidades MDM

### Operadora

| Propriedade | Valor |
|-------------|-------|
| **Master table** | `mdm_ans.mdm_operadora_master` |
| **Surrogate key** | `operadora_master_id varchar(32)` |
| **Chave natural** | `registro_ans` |
| **Fonte primária** | CADOP |
| **Fontes complementares** | DIOPS, SIB, TISS |
| **Score** | `mdm_confidence_score` |

### Estabelecimento

| Propriedade | Valor |
|-------------|-------|
| **Master table** | `mdm_ans.mdm_estabelecimento_master` |
| **Surrogate key** | `estabelecimento_master_id varchar(32)` |
| **Chave natural** | `cnes` |
| **Fonte primária** | CNES ST |
| **Score** | `mdm_confidence_score` |

### Prestador

| Propriedade | Valor |
|-------------|-------|
| **Master table** | `mdm_ans.mdm_prestador_master` |
| **Surrogate key** | `prestador_master_id varchar(32)` |
| **Chave natural** | `cnes + tipo_prestador` |
| **Fontes** | CNES ST, TISS |
| **Score** | `mdm_confidence_score` |

### Contrato (Privado)

| Propriedade | Valor |
|-------------|-------|
| **Master table** | `mdm_privado.mdm_contrato_master` |
| **Surrogate key** | `contrato_master_id varchar(32)` |
| **Chave natural** | `tenant_id + numero_contrato_normalizado` |
| **Fonte** | `bruto_cliente` / `stg_cliente` |
| **RLS** | Obrigatório — `tenant_id` |
| **Score** | `mdm_confidence_score` |

### Subfatura (Privada)

| Propriedade | Valor |
|-------------|-------|
| **Master table** | `mdm_privado.mdm_subfatura_master` |
| **Surrogate key** | `subfatura_master_id varchar(32)` |
| **Chave natural** | `tenant_id + contrato_master_id + competencia` |
| **Fonte** | `bruto_cliente` / `stg_cliente` |
| **RLS** | Obrigatório — `tenant_id` |
| **Score** | `mdm_confidence_score` |

---

## Score de Confiança

### `mdm_confidence_score`

| Faixa | Significado |
|-------|-------------|
| 0.90–1.00 | Alta confiança — múltiplas fontes concordam |
| 0.70–0.89 | Média confiança — fonte única ou divergência menor |
| 0.50–0.69 | Baixa confiança — divergência significativa |
| 0.00–0.49 | Muito baixa — dados insuficientes ou conflitantes |

---

## Regras de Bloqueio

1. Registro com `mdm_confidence_score < 0.50` não publica em produto premium.
2. Registro com `mdm_status = EXCLUIDO` não publica em nenhum produto.
3. Registro com `mdm_status = PENDENTE` publica com warning.
4. Crosswalk sem aprovação manual (quando exigida) bloqueia o master.

---

## MDM Público vs Privado

| Aspecto | MDM Público (`mdm_ans`) | MDM Privado (`mdm_privado`) |
|---------|--------------------------|------------------------------|
| **Dados** | ANS — domínio público | Dados do tenant |
| **Schema** | `mdm_ans` | `mdm_privado` |
| **RLS** | Não | Sim (`tenant_id`) |
| **Exposição** | API pública (ouro/prata) | Apenas API privada do tenant |
| **Cross-tenant** | Não aplicável — dados públicos | **Proibido** — nunca misturar tenants |
| **Surrogate key** | Hash do registro_ans / cnes | Hash do tenant_id + chave natural |

### Regra de Separação

**Dados públicos e privados nunca se misturam no mesmo registro.** Um master público pode ser referenciado por um registro privado via FK lógica, mas o registro privado contém apenas dados do tenant.

---

## Exceções MDM

### Tipos

| Tipo | Descrição |
|------|-----------|
| `MDM_DUPLICATA` | Duas fontes produzem registros distintos para a mesma entidade |
| `MDM_CONFLITO` | Fontes divergem em atributo crítico |
| `MDM_ORFAO` | Registro sem master resolvido |
| `MDM_CROSSWALK_NAO_APROVADO` | Crosswalk pendente de revisão manual |

### Regras

1. Exceções MDM são armazenadas em `quality_ans.mdm_exception` ou `mdm_privado.mdm_exception`.
2. Exceção bloqueante impede publicação do master.
3. Exceção warning reduz `mdm_confidence_score`.

---

## Trilha de Auditoria

1. `mdm_created_at` — quando o master foi criado.
2. `mdm_updated_at` — última atualização do master.
3. Crosswalk approval log — quem aprovou, quando.
4. Log de alteração de survivorship rule.