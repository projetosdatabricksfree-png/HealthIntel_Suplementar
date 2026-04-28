# Runbook — Reverter versão TUSS / ROL / DE-PARA / Snapshot Vigente

**Categoria:** Operação excepcional. Use apenas em emergência (regressão semântica detectada na nova versão, layout incompatível, dados corrompidos pela ANS).

**Pré-requisitos:**
- Acesso `psql` ao PostgreSQL `healthintel`.
- Sprint 37 aplicada (`infra/postgres/init/032_fase7_versao_dataset.sql`).
- Permissão para escrita em `plataforma.versao_dataset_vigente`.

**Risco:** alto. Ação manual sobre tabela de governança. Documentar incidente que motivou a reversão antes de executar.

---

## 1. Identificar versão vigente atual

```sql
SELECT id, dataset_codigo, versao, hash_arquivo, publicado_em, carregado_em
FROM plataforma.versao_dataset_vigente
WHERE dataset_codigo = '<DATASET_CODIGO>'
ORDER BY carregado_em DESC;
```

Ex.: `<DATASET_CODIGO>` = `tuss_procedimento`.

A linha `vigente=true` é a versão atual em uso. As demais são histórico.

## 2. Identificar a versão anterior estável

Listar as versões anteriores com data de carga:

```sql
SELECT id, versao, publicado_em, carregado_em, hash_arquivo, vigente
FROM plataforma.versao_dataset_vigente
WHERE dataset_codigo = '<DATASET_CODIGO>'
ORDER BY carregado_em DESC
LIMIT 10;
```

Confirme com o time de Produto qual `id` deve voltar a vigente. Anote os dois `id`s:

- `id_atual_problema` (a que será desativada).
- `id_anterior_estavel` (a que voltará a vigente).

## 3. Reverter atomicamente em uma transação

**ATENÇÃO:** o índice único parcial `ux_versao_dataset_vigente_dataset` exige que apenas uma linha tenha `vigente=true` por dataset. A reversão precisa desativar a atual ANTES de reativar a anterior, dentro da mesma transação.

```sql
BEGIN;

-- Desativar a versão problemática
UPDATE plataforma.versao_dataset_vigente
   SET vigente = false
 WHERE id = <id_atual_problema>
   AND dataset_codigo = '<DATASET_CODIGO>';

-- Reativar a versão anterior estável
UPDATE plataforma.versao_dataset_vigente
   SET vigente = true
 WHERE id = <id_anterior_estavel>
   AND dataset_codigo = '<DATASET_CODIGO>';

-- Validar invariante (deve retornar 1)
SELECT count(*) AS vigentes_apos_reversao
  FROM plataforma.versao_dataset_vigente
 WHERE dataset_codigo = '<DATASET_CODIGO>'
   AND vigente = true;

COMMIT;
```

Se o `SELECT count(*)` retornar diferente de 1, **NÃO commitar** — investigar antes.

## 4. Repropagar para a tabela bruta (se aplicável)

Se a tabela bruta tiver coluna `versao_dataset` e linhas da versão problemática:

```sql
-- Inspecionar
SELECT versao_dataset, count(*) FROM "<schema>"."<tabela>"
WHERE versao_dataset IS NOT NULL
GROUP BY 1 ORDER BY 1;

-- Remover linhas da versão problemática (se confirmado pelo Produto)
DELETE FROM "<schema>"."<tabela>"
WHERE versao_dataset = '<versao_problematica>';
```

Em seguida, recarregar a versão anterior usando o pipeline normal de ingestão (a próxima execução da DAG real, quando existir, irá recarregar com `registrar_nova_versao`).

## 5. Validar com o helper Python

```python
import asyncio
from ingestao.app.versao_vigente import obter_versao_vigente, garantir_unica_versao_vigente

async def main():
    await garantir_unica_versao_vigente("<DATASET_CODIGO>")
    vigente = await obter_versao_vigente("<DATASET_CODIGO>")
    print("Vigente:", vigente.versao if vigente else "NENHUMA")

asyncio.run(main())
```

## 6. Rodar os testes da Sprint 37

```bash
.venv/bin/pytest ingestao/tests/test_versao_vigente.py -v
```

Todos devem passar (22/22).

## 7. Registrar o incidente

- Abrir entrada em `docs/operacao/incidentes/` com data, dataset, versão problemática, versão revertida, motivo, evidências (queries acima copiadas).
- Notificar Produto e Engenharia.
- Avaliar se a versão problemática deve ser deletada do manifesto ou mantida como histórico.

## 8. Quando NÃO usar este runbook

- **Não usar** para "limpar" o manifesto. As linhas com `vigente=false` são histórico de auditoria; mantenha.
- **Não usar** para excluir o registro vigente sem ter outro para reativar — isso deixa o dataset sem vigente, quebrando idempotência da próxima ingestão.
- **Não usar** durante carga ativa da DAG real (quando existir) — aguarde o fim do job ou pause a DAG.

---

**Owner do runbook:** Engenharia de dados HealthIntel.
**Última revisão:** Sprint 37 (Fase 7) — 2026-04-28.
