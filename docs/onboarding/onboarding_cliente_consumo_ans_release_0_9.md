# Onboarding Cliente — `consumo_ans` Release 0.9

**Tag**: `v0.9.0-core-ans`
**Schema**: `consumo_ans` (acesso somente leitura)
**Role**: `healthintel_cliente_reader`
**Catálogo**: [`catalogo_consumo_ans.yml`](../catalogo_dados/consumo_ans/catalogo_consumo_ans.yml)

---

## 1. Como conectar

### 1.1 Receba credenciais

A HealthIntel provisiona um **usuário PostgreSQL dedicado por cliente**, sempre
membro da role `healthintel_cliente_reader`. Senha é entregue via canal seguro
(não-email, não-Slack público).

Exemplo do que você recebe:

```
host: <ip-vps-healthintel>
porta: 5432
database: healthintel
usuário: healthintel_cliente_<seu-nome>
senha: <gerada-via-secret-manager>
schema único permitido: consumo_ans
```

### 1.2 Conexão via psql

```bash
psql "host=<ip> port=5432 dbname=healthintel user=healthintel_cliente_<seu-nome>" \
    -W
# Cole a senha quando solicitado
```

### 1.3 Conexão via DBeaver / TablePlus / outros BIs

- **JDBC URL**: `jdbc:postgresql://<ip>:5432/healthintel`
- **Schema padrão**: `consumo_ans`
- **SSL**: recomendado (`sslmode=require`)

### 1.4 Verifique seu acesso

```sql
-- Lista tabelas que você consegue ver (deve mostrar 12)
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'consumo_ans'
ORDER BY table_name;

-- Tente acessar schema interno (DEVE FALHAR com permission denied)
SELECT 1 FROM bruto_ans.cadop LIMIT 1;
```

Se a tentativa de acessar `bruto_ans` retornar resultado, contate suporte
imediatamente — isso é um vazamento.

---

## 2. Schemas disponíveis

| Schema | Acesso | Conteúdo |
|---|---|---|
| `consumo_ans` | ✅ SELECT | 12 tabelas comerciais — único schema disponível |
| `bruto_ans` | ❌ negado | dados brutos ANS (interno) |
| `stg_ans` | ❌ negado | staging (interno) |
| `int_ans` | ❌ negado | intermediate (interno) |
| `nucleo_ans` | ❌ negado | fatos e dimensões (interno) |
| `api_ans` | ❌ negado | projeções API (interno) |
| `plataforma` | ❌ negado | metadados operacionais (interno) |
| `mdm_*` | ❌ negado | master data (interno) |
| `quality_ans` | ❌ negado | validações (interno) |
| `consumo_premium_ans` | ❌ negado | datasets premium (acesso separado) |

---

## 3. Exemplos SQL

Veja [`queries_exemplo.sql`](../catalogo_dados/consumo_ans/queries_exemplo.sql)
para exemplos prontos. Resumo:

```sql
-- Produtos e planos por operadora em determinada competência
SELECT registro_ans, codigo_produto, nome_produto, segmentacao, modalidade
FROM consumo_ans.consumo_produto_plano
WHERE competencia = '202412'
LIMIT 100;

-- Indicadores regulatórios trimestrais
SELECT registro_ans, trimestre, ind_nip, ind_igr, ind_resolutividade
FROM consumo_ans.consumo_regulatorio_operadora_trimestre
WHERE trimestre = '202403'
ORDER BY registro_ans
LIMIT 100;

-- IDSS anual
SELECT registro_ans, ano_base, idss_geral, idss_atencao_saude
FROM consumo_ans.consumo_idss
WHERE ano_base = 2023
LIMIT 50;

-- TUSS vigente (referência)
SELECT codigo_tuss, descricao, especialidade
FROM consumo_ans.consumo_tuss_procedimento_vigente
WHERE descricao ILIKE '%consulta%'
LIMIT 50;
```

---

## 4. Boas práticas

### 4.1 Sempre use `LIMIT` em queries exploratórias

```sql
-- ✅ BOM
SELECT * FROM consumo_ans.consumo_produto_plano LIMIT 100;

-- ❌ EVITE (full table scan)
SELECT * FROM consumo_ans.consumo_produto_plano;
```

### 4.2 Filtre por `competencia` ou `trimestre`

As tabelas têm índice em `competencia`/`trimestre`. Sempre filtre.

```sql
-- ✅ BOM (usa índice)
WHERE competencia = '202412'

-- ❌ EVITE (table scan)
WHERE competencia LIKE '2024%'
```

### 4.3 Faça JOINs em chaves de negócio

```sql
-- Cruzar produto + regulatório
SELECT p.registro_ans, p.codigo_produto, r.ind_nip
FROM consumo_ans.consumo_produto_plano p
LEFT JOIN consumo_ans.consumo_regulatorio_operadora_trimestre r
       ON p.registro_ans = r.registro_ans
      AND r.trimestre = '202403'
WHERE p.competencia = '202412'
LIMIT 100;
```

### 4.4 Documente competência da extração

Cada extração que você fizer deve registrar:
- `competencia` ou `trimestre` consultado.
- Data/hora da extração.
- Versão do catálogo (`v0.9.0-core-ans`).

---

## 5. Limites de uso

| Limite | Valor | Observação |
|---|---|---|
| Conexões simultâneas | 5 por cliente | requisição → suporte |
| Query timeout | 60s | queries longas → suporte |
| Tamanho de retorno | 1M linhas | acima → paginação |

Excedentes contínuos disparam alerta para o time de plataforma.

---

## 6. O que NÃO está incluso (importante)

- ❌ TISS (fora do escopo).
- ❌ SIB histórico completo (apenas parciais — não publicado).
- ❌ CNES rede assistencial detalhada.
- ❌ NTRP / precificação detalhada.
- ❌ Ressarcimento SUS detalhado.
- ❌ Dados sensíveis pessoais (LGPD).
- ❌ Acesso aos schemas internos (`bruto_*`, `stg_*`, `nucleo_*`).

Para cobertura completa, ver [`cobertura_atual_release_0_9.md`](../catalogo_dados/consumo_ans/cobertura_atual_release_0_9.md).

---

## 7. Suporte e SLA

- **Canal**: suporte técnico via canal dedicado entregue na contratação.
- **SLA de resposta**: 1 dia útil para dúvidas, 4h para incidentes críticos.
- **Janela de manutenção**: domingos 02:00–04:00 BRT (avisada com 48h).

---

## 8. FAQ

**P: Onde está a tabela TISS?**
R: TISS está **fora do escopo** da Release 0.9. Não foi disponibilizada porque os
dados não atendem critério de qualidade comercial. Aguarda decisão de roadmap.

**P: Posso ler `bruto_ans`?**
R: Não. Tentativas retornam `42501 permission denied for schema`. Esse é o
comportamento correto.

**P: Como reportar dado faltando?**
R: Use o canal de suporte e cite tabela + competência + chave de negócio.

**P: Versão do catálogo é congelada?**
R: Sim. A tag `v0.9.0-core-ans` congela o catálogo. Mudanças entram em
release nova com versão maior.
