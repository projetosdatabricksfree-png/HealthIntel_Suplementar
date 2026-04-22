# Fontes regulatórias ANS — Sprint 07

## Objetivo

Consolidar o contrato operacional das fontes oficiais usadas na Sprint 07 para IGR, NIP/TIR e listas da RN 623/2024.

## Fontes oficiais

| Dataset | URL oficial | Atualização oficial usada | Cadência operacional | Formato de publicação | Observação |
| --- | --- | --- | --- | --- | --- |
| `igr` | `https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/indice-de-reclamacoes-2` | `24/09/2025` | trimestral | página + painel Power BI | seção oficial informa IGR e histórico desde 2020 |
| `nip` | `https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/indice-de-reclamacoes-2` | `24/09/2025` | trimestral | página + painel Power BI | mesma página oficial traz Demandas NIP, TR e TIR |
| `tir` | `https://www.gov.br/ans/pt-br/assuntos/noticias/sobre-ans/ans-lanca-painel-sobre-taxa-de-intermediacao-resolvida` | `05/03/2025` | trimestral | notícia + painel | notícia oficial marca o lançamento da TIR |
| `rn623_lista` | `https://www.gov.br/ans/pt-br/assuntos/informacoes-e-avaliacoes-de-operadoras/lista-excelencia-e-reducao-das-reclamacoes-das-operadoras` | `13/03/2026` | trimestral | página HTML + PDFs + painel | listas de Excelência e Redução por trimestre |

## Regras de coleta adotadas

- `igr`: capturar trimestre, registro ANS, modalidade, porte, total de reclamações, beneficiários, IGR e meta.
- `nip`: capturar trimestre, registro ANS, modalidade, demandas NIP, demandas resolvidas, beneficiários, TIR e TR quando disponíveis.
- `rn623_lista`: capturar trimestre, tipo de lista, registro ANS, modalidade, IGR, meta, beneficiários e total de NIP.
- Cada publicação gera hash próprio em `plataforma.publicacao_regulatoria`.
- Cada carga gera nova versão em `plataforma.versao_dataset`.
- O pipeline aceita ingestão manual assistida enquanto o extrator definitivo de painel Power BI não for promovido para produção.

## Limites conhecidos

- As publicações oficiais são heterogêneas e misturam HTML, PDF e painel.
- Nesta sprint, a plataforma fecha o contrato de dados, o bronze, o staging e a API básica; a automação completa de scraping/export do Power BI fica preparada para sprint operacional posterior.
