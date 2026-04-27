# Padrões de Qualidade e Validação

**Versão:** v3.8.0-gov
**Data:** 2026-04-27

---

## Objetivo

Definir regras de validação, scores de qualidade e exceções na plataforma HealthIntel Suplementar. Toda validação é determinística e offline — sem dependência externa em runtime.

---

## Regras de Validação

### CNPJ

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `varchar(14)` |
| **Validação** | Determinística offline |
| **Regra** | `validar_cnpj_completo(cnpj)` — tamanho 14, todos dígitos, dígito verificador |
| **Warning** | Dígito verificador inválido emite `quality_score_documental` reduzido |
| **Bloqueio** | CNPJ com formato inválido (tamanho != 14, caracteres não dígitos) é `INVALIDO` |
| **Dependência externa** | **NENHUMA** — sem Serpro, sem Receita online, sem BrasilAPI |

### CPF

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `varchar(11)` |
| **Fluxo** | Apenas em dados privados de tenant |
| **Justificativa** | LGPD — dado pessoal |
| **Validação** | Apenas em fluxo privado com consentimento documentado |

### CNES

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `varchar(7)` |
| **Validação** | Formato 7 dígitos; referência contra CNES ST when available |
| **Warning** | CNES não encontrado na referência emite `quality_score_cnes` reduzido |

### Registro ANS

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `varchar(6)` |
| **Validação** | Formato 6 dígitos; consistência com CADOP/MDM |
| **Warning** | Registro não encontrado no CADOP da competência emite warning |

### Competência

| Propriedade | Valor |
|-------------|-------|
| **Tipo** | `int` YYYYMM |
| **Validação** | `200001 <= competencia <= competencia_atual + 1`, mês 01-12 |

### TISS/TUSS

| Propriedade | Valor |
|-------------|-------|
| **TISS** | Referenciado contra tabela TUSS versionada ou modo sintético documentado |
| **TUSS** | Dados de referência mantidos como seeds (`ref_tuss.csv`). Dados sintéticos são aceitos desde que explicitamente marcados como `NAO_COMERCIAL` |
| **Validação** | `cd_procedimento_tuss` válido contra referência; trimestre em formato `YYYYTN` |

### Contrato / Subfatura

| Propriedade | Valor |
|-------------|-------|
| **Fluxo** | Apenas em dados privados de tenant |
| **Validação** | `tenant_id` obrigatório; contrato com operadora resolvida via MDM |
| **Exceção bloqueante** | Contrato sem `operadora_master_id` resolvida não publica em premium |
| **Warning** | Subfatura sem contrato correspondente emite warning |

---

## Scores de Qualidade

| Score | Descrição | Faixa | Aplica a |
|-------|-----------|-------|----------|
| `quality_score_documental` | Qualidade do documento (CNPJ/CPF/CNES) | 0.0–100.0 | Operadora, Estabelecimento, Prestador |
| `quality_score_mdm` | Confiança do golden record | 0.0–100.0 | Todo master MDM |
| `quality_score_publicacao` | Prontidão para publicação em produto | 0.0–100.0 | Todo data product |
| `quality_score_cnes` | Qualidade do código CNES | 0.0–100.0 | Estabelecimento |
| `quality_score_tuss` | Qualidade da referência TUSS | 0.0–100.0 | Procedimento TUSS |
| `quality_score_contrato` | Qualidade do contrato | 0.0–100.0 | Contrato (privado) |
| `quality_score_subfatura` | Qualidade da subfatura | 0.0–100.0 | Subfatura (privada) |

### Regras de Score

1. Score = 100.0 significa dado completamente validado.
2. Score = 0.0 significa dado não verificado ou totalmente inválido.
3. Scores são `double precision`.
4. Score < 50.0 é considerado "baixa qualidade".
5. Produto premium exige score mínimo definido no contrato do data product.

---

## Exceções

### Estrutura

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `tipo_excecao` | Categoria da exceção | `CNPJ_DIGITO_INVALIDO` |
| `severidade` | `BLOQUEANTE` ou `WARNING` | `WARNING` |
| `mensagem` | Descrição legível | "CNPJ 11222333000182 possui dígito verificador inválido" |
| `bloqueio` | Impede publicação em produto principal | `false` |
| `data_deteccao` | Quando a exceção foi detectada | `2025-03-15` |
| `owner_correcao` | Responsável pela correção | `Engenharia de Dados` |

### Regras

1. **Exceção bloqueante** (`severidade = BLOQUEANTE`) impede a publicação do registro em produto principal.
2. **Warning** (`severidade = WARNING`) reduz score mas não bloqueia publicação.
3. Toda exceção deve ter `owner_correcao`.
4. Exceções são rastreadas na tabela `quality_ans.*_exception`.
5. Exceções não resolvidas por mais de 3 competências devem escalar.

---

## Validação em Pipeline

### Ordem

1. **Staging**: validação de formato (tipo, tamanho).
2. **Intermediate**: validação de consistência (dígito, referência).
3. **Quality**: validação completa, scores, exceções.
4. **MDM**: survivorship, dedup, crosswalk.
5. **API**: projeção apenas de dados validados.

### Ferramentas

- **dbt tests** para validações declarativas.
- **Macros** para validações reusáveis (`validar_cnpj_completo`, `validar_cnes_formato`).
- **Check constraints** para regras baratas e invioláveis.
- **Tabelas de exceção** em `quality_ans` para registros problemáticos.

---

## Anti-Escopo

1. **Nenhuma validação depende de API externa em runtime.**
2. **Nenhuma validação usa Serpro.**
3. **Nenhuma validação usa Receita online.**
4. **Nenhuma validação usa BrasilAPI.**
5. **Nenhum comando `enrich-cnpj` está ativo.**

Qualquer futura integração externa para validação exige:
- ADR em `docs/arquitetura/`;
- Hard gate próprio;
- Fallback determinístico para quando a API externa estiver indisponível.