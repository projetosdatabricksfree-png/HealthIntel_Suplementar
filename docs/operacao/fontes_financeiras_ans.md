# Fontes financeiras ANS

## DIOPS financeiro

- Página oficial: `https://www.gov.br/ans/pt-br/assuntos/operadoras/aplicativos-ans-2/aplicativos-diops/diops-financeiro`
- A ANS informa envio trimestral das informações financeiras das operadoras.
- A página oficial também divulga versões históricas do cliente `DIOPS-XML`, incluindo a linha a partir de `2026`.

## FIP histórico

- Referência operacional: `https://www.gov.br/ans/pt-br/assuntos/operadoras/aplicativos-ans-2/aplicativos-diops/diops-financeiro`
- O projeto trata `FIP` como série histórica compatível e separada no `bronze`, com harmonização posterior no `dbt`.
- A modelagem preserva compatibilidade com o legado contábil e com o uso do DIOPS como canal vigente.

## Premissas de ingestão

- Cadência trimestral para `diops` e `fip`.
- Versionamento manual de layout no `MongoDB`.
- Bronze imutável e reprocessamento histórico via novo lote.
- Publicação de versões de dataset em `plataforma.versao_dataset` e `plataforma.publicacao_financeira`.
