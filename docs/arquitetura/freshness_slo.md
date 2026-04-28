# Freshness SLO

Baseline de monitoramento de frescor para os datasets fonte da plataforma. A data exata da última carga deve ser consultada em `plataforma.versao_dataset.carregado_em` para logs per-carga legados e em `plataforma.versao_dataset_vigente.carregado_em` para datasets de versão vigente; o SLO abaixo é o compromisso operacional usado para `warn_after` e `error_after`.

| Dataset | Publicação ANS / fonte | Frequência | `warn_after` | `error_after` | Observação |
| --- | --- | --- | --- | --- | --- |
| `cadop` | Cadastro de operadoras | Contínua | 24h | 48h | Fonte mestre de operadoras |
| `sib_operadora` | SIB / operadora | Mensal | 45d | 90d | Base de beneficiários por operadora |
| `sib_municipio` | SIB / município | Mensal | 45d | 90d | Beneficiários por localidade |
| `igr` | ANS / IGR | Trimestral | 95d | 120d | Indicador regulatório |
| `nip` | ANS / NIP | Trimestral | 95d | 120d | Demandas de intermediação |
| `rn623_lista` | ANS / RN 623 | Trimestral | 95d | 120d | Listas de excelência e redução |
| `idss` | ANS / IDSS | Anual | 365d | 400d | Índice anual de desempenho |
| `regime_especial` | ANS / regime especial | Trimestral | 95d | 120d | Históricos regulatórios |
| `prudencial` | ANS / prudencial | Trimestral | 95d | 120d | Indicadores de solvência |
| `portabilidade` | ANS / portabilidade | Mensal | 45d | 90d | Movimentação de portabilidade |
| `taxa_resolutividade` | ANS / resolutividade | Trimestral | 95d | 120d | Resolução de reclamações |
| `diops` | ANS / DIOPS | Trimestral | 95d | 120d | Demonstrações contábeis |
| `fip` | ANS / FIP | Trimestral | 95d | 120d | Ficha padronizada |
| `vda` | ANS / VDA | Mensal | 45d | 90d | Variação de despesas assistenciais |
| `glosa` | ANS / glosa | Mensal | 45d | 90d | Glosa assistencial |
| `rede_assistencial` | ANS / rede assistencial | Mensal | 45d | 90d | Prestadores e cobertura |
| `cnes_estabelecimento` | DATASUS / CNES | Mensal | 60d | 90d | Base estrutural de rede |
| `tiss_procedimento` | ANS / TISS | Trimestral | 95d | 120d | Procedimentos e sinistralidade |
