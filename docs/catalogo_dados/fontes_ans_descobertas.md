# Fontes ANS Descobertas

Este documento descreve o catálogo operacional mantido pela ELT universal da ANS.

## Tabelas Operacionais

| Tabela | Propósito |
|---|---|
| `plataforma.fonte_dado_ans` | Catálogo de URLs descobertas no índice público `/FTP/PDA/`. |
| `plataforma.arquivo_fonte_ans` | Manifest operacional dos arquivos baixados, hashes e status. |
| `bruto_ans.ans_arquivo_generico` | Registro Bronze de arquivos ainda sem parser dedicado. |
| `bruto_ans.ans_linha_generica` | Linhas tabulares carregadas em JSONB para auditoria e futura promoção. |

## Famílias Prioritárias

| Família | Exemplos | Status parser inicial |
|---|---|---|
| `cadop` | Operadoras de planos de saúde ativas | Parser dedicado existente e carga genérica disponível. |
| `sib` | Beneficiários por operadora/UF | Parser dedicado existente e carga genérica disponível. |
| `tiss` | Ambulatorial, hospitalar e dicionários | Carga genérica até promoção de parser dedicado. |
| `sip` | Informações periódicas assistenciais | Carga genérica. |
| `igr` | Índice geral de reclamações | Carga genérica ou parser dedicado conforme layout. |
| `idss` | Indicador de desempenho setorial | Carga genérica ou parser dedicado conforme layout. |
| `nip` | Reclamações/NIP | Carga genérica. |
| `diops` | Dados econômico-financeiros | Carga genérica ou parser dedicado conforme layout. |
| `rpc` | Ressarcimento ao SUS | Carga genérica. |
| `caderno_ss` | Caderno de informação da saúde suplementar | Carga genérica. |

## Consulta de Status

```sql
select familia, count(*) as fontes
from plataforma.fonte_dado_ans
group by familia
order by fontes desc;
```

```sql
select status, count(*) as arquivos, sum(tamanho_bytes) as bytes
from plataforma.arquivo_fonte_ans
group by status
order by status;
```

## Critério de Promoção

Um dataset sai de Bronze genérica para parser dedicado quando houver:

- fonte estável;
- layout compreendido e versionado;
- regra de idempotência testada;
- utilidade clara para Prata, Gold ou `consumo_ans`;
- testes de regressão para mudança de layout.
