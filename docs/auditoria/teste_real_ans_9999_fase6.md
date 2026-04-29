# Teste Real ANS — Carga Controlada (Fase 6 pré-requisito)

**Data**: 2026-04-27  
**Branch**: `teste-real-ans-9999`  
**Executor**: Diego  

---

## Objetivo

Validar ingestão real ANS com volume controlado (sem truncar Docker volumes), rodando os gates completos após a carga.

---

## Contexto

O banco continha 278 GB / 281.368.495 linhas em `bruto_ans.ans_linha_generica` de uma sessão anterior. Em vez de resetar Docker (`down -v`), foi feito TRUNCATE seletivo das tabelas SIB + restore do controle de arquivos.

---

## Fase 1 — Limpeza Seletiva

| Ação | Resultado |
|------|-----------|
| TRUNCATE `ans_linha_generica` | 278 GB → 32 kB |
| TRUNCATE 14 tabelas SIB adicionais | `sib_beneficiario_*`, `fat_beneficiario_*`, `consumo_beneficiarios_*`, `api_prata_sib_*` |
| Disco pré-limpeza | 96% (22 GB livres) |
| Disco pós-TRUNCATE | **33% (299 GB livres)** |

Tabelas truncadas:
- `bruto_ans.ans_linha_generica`
- `bruto_ans.sib_beneficiario_municipio` + partições
- `bruto_ans.sib_beneficiario_operadora` + partições
- `bruto_ans.sib_municipio_quarentena`
- `bruto_ans.sib_operadora_quarentena`
- `nucleo_ans.fat_beneficiario_localidade`
- `nucleo_ans.fat_beneficiario_operadora`
- `api_ans.api_prata_sib_municipio`
- `api_ans.api_prata_sib_operadora`
- `consumo_ans.consumo_beneficiarios_municipio_mes`
- `consumo_ans.consumo_beneficiarios_operadora_mes`

---

## Fase 2 — Reset de Controle de Arquivos

| Ação | Resultado |
|------|-----------|
| Deletar 13 lotes SIB demo de `plataforma.lote_ingestao` | OK |
| Reset 2 arquivos CADOP `carregado` → `baixado` | `Relatorio_cadop.csv`, `Relatorio_cadop_canceladas.csv` |
| Mover 9 arquivos SIB grandes para `pendente` | PR/RJ/RS/SC/SE/RN/RO/SP/benef_regiao_geog |
| Manter 2 arquivos SIB menores como `baixado` | `sib_inativo_RR.zip` (3.3 MB), `sib_inativo_TO.zip` (14 MB — arquivo ausente) |

**Observação**: `sib_inativo_TO.zip` estava marcado como `baixado` no DB mas o arquivo físico não existia em `/tmp/healthintel/landing/`. Bug identificado: quando `_zip_tem_csv()` falha por `FileNotFoundError`, a exceção escapa do try/except interno e o status não é atualizado para `erro_carga`. Corrigido manualmente via UPDATE.

---

## Fase 3 — ELT Carga

### CADOP (1ª run)

```
make elt-load ELT_ESCOPO=sector_core ELT_FAMILIAS=cadop ELT_LIMITE=9999
```

| Métrica | Valor |
|---------|-------|
| Arquivos processados | 2 |
| Arquivos carregados | 2 |
| Linhas carregadas | **4.162** |
| Erros | 0 |

Datasets: `Relatorio_cadop.csv` (1.106 linhas) + `Relatorio_cadop_canceladas.csv` (3.056 linhas).

### CADOP (idempotência — 2ª run)

| Métrica | Valor |
|---------|-------|
| Arquivos processados | **0** |
| Linhas carregadas | **0** |

Resultado: **IDEMPOTENTE** ✓

### SIB (1ª run)

```
make elt-load ELT_ESCOPO=sector_core ELT_FAMILIAS=sib ELT_LIMITE=9999
```

| Métrica | Valor |
|---------|-------|
| Arquivos processados | 3 |
| Arquivos carregados | 1 |
| Linhas carregadas | **222.770** |
| Sem parser | 1 (PDF — esperado) |
| Erros | 1 (`sib_inativo_TO.zip` — arquivo físico ausente) |

Dataset: `sib_inativo_RR.zip` — Roraima inativos.

### SIB (idempotência — 2ª run)

| Métrica | Valor |
|---------|-------|
| Arquivos carregados | 0 |
| Linhas carregadas | **0** |
| Erros | 1 (TO.zip ainda `baixado` — bug confirmado, corrigido via UPDATE) |

Resultado: RR.zip **IDEMPOTENTE** ✓

---

## Fase 4 — Bronze Final

| Dataset | Família | Linhas | Arquivos |
|---------|---------|--------|----------|
| `cadop_operadoras_ativas` | cadop | 4.162 | 2 |
| `sib_ativo_uf` | sib | 222.770 | 1 |
| **TOTAL** | | **226.932** | **3** |

> **Nota de nomenclatura**: o arquivo carregado foi `sib_inativo_RR.zip` mas o `dataset_codigo` registrado é `sib_ativo_uf`. Trata-se do nome canônico legado do loader SIB para a família `sib`, não há erro de roteamento. Verificar se faz sentido renomear para `sib_beneficiario_uf` (ou similar) no catálogo, fora do escopo deste teste.

---

## Fase 5 — Gates

### dbt build

```
make dbt-build
```

| Resultado | Contagem |
|-----------|----------|
| PASS | **557** |
| WARN | 1 |
| ERROR | 0 |
| SKIP | 0 |
| Tempo | 31.16s |

O WARN é `assert_cnpj_digito_invalido_em_modelos` com 28.775 CNPJs inválidos nos dados reais ANS — hardgate configurado intencionalmente como `warn` (dado real tem qualidade inferior ao demo).

### smoke-premium

```
make smoke-premium
```

| Resultado |
|-----------|
| `endpoints_publicos`: 6 ✓ |
| `endpoints_privados`: 2 ✓ |
| `status`: **ok** ✓ |

### pytest

```
make test
```

| Resultado | Contagem |
|-----------|----------|
| Passed | **105** |
| Failed | 0 |
| Warnings | 0 |
| Tempo | 1.37s |

> Antes da correção do BUG-ELT-001, a suíte tinha 104 testes. Após adicionar `test_arquivo_ausente_na_landing_vira_erro_carga`, a suíte passou para 105 testes.

### Ruff

```
make lint
```

| Resultado |
|-----------|
| **All checks passed!** ✓ |

---

## Resumo dos Gates

| Gate | Status |
|------|--------|
| dbt build | ✅ PASS (557/557, 1 WARN esperado) |
| dbt test | ✅ incluído no build |
| smoke-premium | ✅ OK |
| pytest (105 testes) | ✅ 105 passed |
| ruff lint | ✅ All checks passed |

---

## Observação sobre limite

O parâmetro `ELT_LIMITE=9999` foi usado na execução, porém na família SIB a carga efetiva resultou em 222.770 linhas. Isso indica que o limite não atua como limite global de linhas carregadas para todos os loaders/famílias. O teste deve ser interpretado como carga real controlada por família/arquivo, não como limite estrito de 9.999 linhas para SIB.

| BUG-ELT-002 | `ELT_LIMITE=9999` não limitou a SIB a 9.999 linhas | P2 | Investigar sem bloquear homologação técnica |
|-------------|------------------------------------------------------|-----|----------------------------------------------|

---

## Bugs Identificados e Corrigidos

### BUG-ELT-001: Status não atualizado quando arquivo está ausente na landing ✅ CORRIGIDO

**Localização**: `ingestao/app/elt/loaders.py:carregar_arquivo_ans()` (linha 186)

**Descrição original**: Quando `_zip_tem_csv(path)` lançava `FileNotFoundError` (arquivo ausente em landing), a exceção escapava sem atualizar o status do arquivo. O arquivo permanecia como `baixado` e era reprocessado em toda execução seguinte.

**Correção aplicada** (2026-04-27):
- Adicionada verificação explícita de existência do arquivo no início de `carregar_arquivo_ans()`.
- Se o arquivo não existe, chama `_marcar_status_arquivo(id, "erro_carga", msg)` e retorna sem propagar exceção.
- Arquivo alterado: `ingestao/app/elt/loaders.py`
- Teste criado: `ingestao/tests/test_elt_loaders.py::test_arquivo_ausente_na_landing_vira_erro_carga`
- Teste pré-existente corrigido: `test_pdf_vai_para_arquivo_generico` (usava `/tmp/arquivo.pdf` hardcoded; migrado para `tmp_path`)

**Resultado dos testes pós-correção**:
- `ingestao/tests/test_elt_loaders.py`: 6/6 passed ✅
- `make test`: 105 passed, 0 failed (nos testes de ingestão) ✅
- `make lint`: All checks passed ✅

**Validação em ambiente real (pós-correção, 2026-04-27)**:

Para confirmar que o fix opera de ponta a ponta (sem precisar de UPDATE manual no DB), foi simulado o cenário do bug em ambiente real:

1. `sib_inativo_TO.zip` (arquivo físico ausente em `/tmp/healthintel/landing/ans/`) foi resetado de `erro_carga` para `baixado` via UPDATE.
2. Executado `make elt-load ELT_ESCOPO=sector_core ELT_FAMILIAS=sib ELT_LIMITE=9999`.

**1ª run (2 arquivos ausentes na landing)**:

```json
{
  "status": "ok",
  "arquivos_processados": 2,
  "arquivos_carregados": 0,
  "erros": 0,
  "resultados": [
    {
      "status": "erro_carga",
      "erro": "arquivo físico ausente na landing: .../sib_inativo_TO.zip"
    },
    {
      "status": "erro_carga",
      "erro": "arquivo físico ausente na landing: .../dicionario_de_dados_beneficiarios_por_regiao_geografica.pdf"
    }
  ]
}
```

Status no DB após a 1ª run:

| arquivo | status DB | erro_mensagem |
|---------|-----------|---------------|
| `sib_inativo_TO.zip` | `erro_carga` ✅ | `arquivo físico ausente na landing: .../sib_inativo_TO.zip` |
| `dicionario_de_dados...regiao_geografica.pdf` | `erro_carga` ✅ | `arquivo físico ausente na landing: .../dicionario...pdf` |

**2ª run (idempotência)**:

```json
{
  "status": "ok",
  "arquivos_processados": 0,
  "arquivos_carregados": 0,
  "erros": 0,
  "resultados": []
}
```

Resultado: nenhum arquivo reaparece na fila — o status `erro_carga` é terminal e o loop infinito foi eliminado em ambiente real, sem nenhuma intervenção manual.

**Critério de aceite atendido**:
1. Arquivo ausente na landing não fica com status `baixado` ✅
2. Status muda para `erro_carga` com mensagem rastreável ✅
3. Execução seguinte não tenta reprocessar o arquivo ausente infinitamente ✅ (validado em ambiente real, 2 runs consecutivas)
4. Teste unitário passa ✅

---

## Arquivos de Referência

- Landing zone: `/tmp/healthintel/landing/ans/`
- Controle: `plataforma.arquivo_fonte_ans`, `plataforma.lote_ingestao`
- Bronze: `bruto_ans.ans_linha_generica`
- Branch: `teste-real-ans-9999`
