# Modelagem MDM Público

Esta documentação detalha a implementação do Master Data Management (MDM) público para o HealthIntel_Suplementar, focado exclusivamente em dados de domínio público e regulatório, isolado de dados premium ou multi-tenant.

## Geração de Surrogate Keys MDM

O sistema exige identificadores globais determinísticos que não dependam da base de dados (PostgreSQL/Databricks) ou de extensões externas (como `uuid-ossp`).

Por isso, utilizamos hashing MD5 sobre uma string concatenada com pipe (`|`) de forma isolada por domínio:

```sql
md5(concat_ws('|', 'operadora', registro_ans_canonico, coalesce(cnpj_canonico, '')))
```

Isso garante que:
1. Em qualquer banco de dados `md5(string)` gere o mesmo hex de `text`.
2. A recarga total de tabelas preserve o mesmo ID exato.
3. Não colide entre diferentes entidades (devido ao prefixo).

## Tabelas Constituintes

### Master (`mdm_entidade_master`)
A tabela master contém a versão "dourada" e purgada de cada entidade, agregando regras de qualidade (do schema `quality_ans`), definindo:
- `confidence_score` [0-100]
- `status_mdm` [ATIVO, QUARANTENA, REPROVADO]

### Xref (`xref_entidade_origem`)
Cross-referencing map ligando `entidade_master_id` às chaves dos sistemas origens (como CADOP, CNES).

### Exception (`mdm_entidade_exception`)
Registros que não atingiram a nota de corte aceitável no `confidence_score` e demandam análise humana ou purga automática.
