# ELT ANS Completa

## Objetivo

A ELT universal da ANS descobre, cataloga, baixa e carrega arquivos públicos de
`https://dadosabertos.ans.gov.br/FTP/PDA/` sem substituir as ingestões dedicadas já existentes.

O fluxo dedicado CADOP/SIB continua válido para parsers homologados. A ELT universal atende ao
passo anterior da plataforma: manter catálogo operacional, landing zone, hash, idempotência e
Bronze genérica para datasets ainda sem parser específico.

## Escopos

- `sector_core`: recorte prioritário do produto, incluindo CADOP, SIB, TISS, SIP, IGR, IDSS,
  NIP/reclamações, DIOPS/econômico-financeiro, RPC, Caderno_SS, dados de planos e dicionários.
- `all_ftp`: varredura ampla de `/FTP/PDA/`. Deve ser executado sob limite operacional explícito.

## Comandos

```bash
make elt-discover
make elt-status
make elt-all ELT_FAMILIAS=cadop ELT_LIMITE=10
make elt-all ELT_FAMILIAS=sib ELT_LIMITE=5
make elt-all ELT_FAMILIAS=tiss ELT_LIMITE=10
make elt-all ELT_ESCOPO=all_ftp ELT_LIMITE=100
```

## Fluxo Operacional

1. Discovery lê índices HTML do FTP/PDA, classifica links e grava `plataforma.fonte_dado_ans`.
2. Extract baixa arquivos por streaming para `/tmp/healthintel/landing/ans/.../raw/`.
3. Cada arquivo baixado registra URL, hash, tamanho, origem e status em `plataforma.arquivo_fonte_ans`.
4. Hash já carregado ou baixado vira `ignorado_duplicata`.
5. Load envia arquivos tabulares para `bruto_ans.ans_linha_generica`.
6. Arquivos sem parser ficam registrados em `bruto_ans.ans_arquivo_generico`.
7. dbt expõe `stg_ans_arquivo_generico` e `stg_ans_linha_generica` para auditoria.

## Arquivos Sem Parser

PDF, XLS, XLSX, JSON e XML são baixados e catalogados, mas não são transformados automaticamente.
O status esperado é `baixado_sem_parser`. Para promover um dataset:

1. Confirmar valor de produto e estabilidade mínima da fonte.
2. Criar parser dedicado com leitura streaming quando aplicável.
3. Registrar layout versionado no serviço de layout.
4. Adicionar staging, intermediate e, somente quando fizer sentido, Prata/Gold/Consumo.

## Estratégia de Escala

- Nunca executar `all_ftp` sem `ELT_LIMITE`.
- Priorizar famílias por valor comercial.
- Usar carga genérica como auditoria e retenção Bronze, não como contrato final de API.
- Manter idempotência por `hash_arquivo` em todas as etapas.
- Tratar arquivos grandes por streaming/chunks.

## Airflow

A DAG `dag_elt_ans_catalogo` é manual e aceita parâmetros:

- `escopo`
- `familias`
- `limite`
- `max_depth`

Ela executa discovery, extract, load, dbt staging genérico e resumo operacional.
