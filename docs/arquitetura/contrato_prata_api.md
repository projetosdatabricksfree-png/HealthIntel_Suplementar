# Contrato Prata API

A Prata API expõe dados tipados e padronizados, incluindo visibilidade de qualidade e quarentena. Ela representa o ponto de consumo para integrações que já precisam de consistência estrutural e domínio validado.

## Garantias

- Cada resposta contém `dados` e `meta`.
- `meta.qualidade` informa `taxa_aprovacao`, `registros_quarentena` e `motivos_rejeicao`.
- Os registros inválidos são segregados em tabelas de quarentena e não entram no payload principal.
- O acesso é permitido a partir do plano `analitico`.

## Quarentena

- `/v1/prata/quarentena/resumo` mostra o agregado por dataset, arquivo e competência.
- `/v1/prata/quarentena/{dataset}` mostra os registros rejeitados.
- O endpoint de detalhe de quarentena exige camada Bronze, porque expõe dado técnico de rejeição.

## O que a Prata API entrega

- Tipagem garantida.
- Chaves normalizadas.
- Padronização de competência e códigos.
- Metadados de qualidade para rastrear lote e reprovação.

