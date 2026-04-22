# Fontes regulatórias ANS — Sprint 08

## Objetivo

Registrar o contrato operacional das fontes oficiais usadas na Sprint 08 para regime especial, capital regulatório/prudencial, portabilidade e taxa de resolutividade.

## Fontes oficiais

| Dataset | URL oficial | Cadência operacional | Formato de publicação | Observação |
| --- | --- | --- | --- | --- |
| `regime_especial` | `https://www.gov.br/pt-br/servicos/obter-certidao-de-regime-especial-de-direcao-tecnica` | trimestral | certidão + página institucional | trata direção técnica/fiscal como evento temporal auditável |
| `prudencial` | `https://www.gov.br/ans/pt-br/assuntos/operadoras/regulacao-prudencial-acompanhamento-assistencial-e-economico-financeiro/regulacao-prudencial-1/capital-regulatorio` | trimestral | página institucional + dados de apoio | usado como contrato de capital regulatório e liquidez |
| `portabilidade` | `https://www.gov.br/ans/pt-br/assuntos/contratacao-e-troca-de-plano/portabilidade-de-carencias` | mensal | página institucional + guia | tratado como movimentação operacional por competência |
| `taxa_resolutividade` | `https://www.gov.br/ans/pt-br/assuntos/noticias/numeros-do-setor/ans-amplia-transparencia-sobre-indices-de-reclamacoes` | trimestral | notícia + painel | a taxa de resolutividade é o componente de reclamação resolvida no painel da ANS |

## Regras de coleta adotadas

- `regime_especial`: registrar tipo de regime, vigência temporal, descrição e situação atual.
- `prudencial`: registrar margem de solvência, capital mínimo, capital disponível e índice de liquidez.
- `portabilidade`: registrar competência, modalidade, tipo de contratação e fluxos de entrada/saída.
- `taxa_resolutividade`: registrar taxa, reclamações resolvidas e total de reclamações.
- Cada publicação gera hash próprio em `plataforma.publicacao_regulatoria`.
- Cada carga gera nova versão em `plataforma.versao_dataset`.

## Limites conhecidos

- O contrato de `regime_especial` não depende de um CSV único; ele consolida páginas institucionais e certidões.
- O contrato de `prudencial` pode depender de publicações tabulares auxiliares e é tratado como artefato operacional versionado pela plataforma.
- O pipeline da sprint fecha o contrato, o bronze, o staging, o score e a API; o scraping automatizado definitivo pode ser refinado em sprints futuras sem quebrar o contrato.
