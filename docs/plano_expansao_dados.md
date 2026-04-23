# Plano de Expansão de Dados - HealthIntel Suplementar

Este documento detalha a estratégia para expansão do catálogo de dados da plataforma, visando transformar o projeto de uma ferramenta regulatória em uma plataforma completa de Inteligência em Saúde (DaaS/SaaS).

## Datasets Identificados para Composição

| Dataset | Fonte | Categoria | Proposta de Valor |
| :--- | :--- | :--- | :--- |
| **TISS (Microdados)** | ANS | Utilização | Análise granular de procedimentos, exames e internações. Permite o cálculo do VCMH real e predição de sinistralidade. |
| **SIP & RPC** | ANS | Produtos | Detalhamento técnico dos planos (cobertura, coparticipação, regionalidade). Essencial para segmentação de mercado. |
| **GPS (Guia de Planos)** | ANS | Mercado | Preços comerciais praticados. Permite benchmark de preço vs. custo assistencial. |
| **Ressarcimento ao SUS** | ANS | Eficiência | Monitoramento de uso de rede pública por beneficiários privados. Indicador de falha na rede credenciada. |
| **CNES** | DATASUS | Infraestrutura | Mapeamento completo de prestadores de serviço de saúde no Brasil. |

## Status da Implementação (Sprint Atual)

Atualmente, o projeto já apresenta componentes em estágio inicial para:
- [ ] **CNES**: Inicialização de scripts de layout e DAG de ingestão.
- [ ] **TISS**: Estrutura inicial de banco de dados e DAG de processamento.

## Próximos Passos

1. Finalizar a integração dos layouts TISS no `mongo_layout_service`.
2. Implementar modelos dbt para normalização dos microdados TISS (Bronze -> Silver).
3. Desenvolver indicadores de "Fuga de Rede" baseados nos dados de Ressarcimento ao SUS.
