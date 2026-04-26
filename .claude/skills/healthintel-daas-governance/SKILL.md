---
name: healthintel-daas-governance
description: Identidade do produto HealthIntel Suplementar como plataforma DaaS para dados ANS — guia de propósito e escopo.
---

# HealthIntel DaaS — Governança de Identidade do Produto

## Quando usar esta skill

- Antes de propor qualquer feature, endpoint, modelo dbt, mart, dashboard ou integração.
- Ao receber pedido genérico que cheira a “BI”, “relatório bonito”, “dump”, “export massivo” ou “tela”.
- Ao avaliar se uma sprint, story ou PR contribui para o produto comercial.
- Sempre que houver dúvida sobre o que o HealthIntel Suplementar é e o que ele NÃO é.

## Regras obrigatórias

1. HealthIntel Suplementar é uma **plataforma DaaS comercial** sobre dados regulatórios da ANS (saúde suplementar brasileira).
2. O produto entrega **tabelas ANS confiáveis, governadas e consumíveis** — via API autenticada e via SQL controlado em schemas curados.
3. Toda entrega precisa responder objetivamente:
   - **“Esta entrega aproxima o produto de disponibilizar tabelas confiáveis, governadas e consumíveis pelo cliente?”**
   - Se a resposta for **não**, a entrega é secundária ou está fora de escopo.
4. O valor não está nos dados brutos (que são públicos), e sim na **engenharia, curadoria, contrato, governança e exposição controlada**.
5. Toda decisão técnica deve preservar: rastreabilidade, idempotência, contrato de saída, auditoria de uso e proteção comercial.
6. Diferenciar sempre **estado atual** (o que já está implementado, com tag/baseline) de **visão-alvo** (roadmap declarado em `docs/sprints/fase{N}/`).

## Anti-padrões

- Tratar o produto como **BI final** (dashboards interativos, telas executivas como entrega principal).
- Tratar o produto como **dump de base** (exportar `bruto_ans`/`stg_ans` direto para o cliente).
- Tratar o produto como **revenda de CSV público da ANS** sem agregar curadoria, qualidade e contrato.
- Construir telas/relatórios antes de existir tabela curada, contrato e governança que sustentem aquela informação.
- Confundir “o que o agente acha bonito entregar” com “o que o cliente paga para consumir”.
- Marcar uma entrega como concluída só porque o código compilou — sem teste, sem contrato, sem documentação.

## Checklist antes de concluir

- [ ] A entrega resulta em (ou suporta diretamente) uma tabela confiável, governada e consumível pelo cliente?
- [ ] A entrega respeita a separação medalhão? (bruto/stg/int internos; api_ans/consumo_ans/consumo_premium_ans expostos)
- [ ] Existe contrato mínimo (schema, descrição, teste) para o que vai ser consumido?
- [ ] Foi distinguido claramente o que é estado atual vs. visão-alvo?
- [ ] A entrega não introduziu rota direta de cliente para schema interno?
- [ ] A entrega não foi descrita como “BI/dashboard” quando deveria ser “tabela/contrato”?

## Exemplo de prompt de uso

> “Estou avaliando criar um endpoint que devolva todos os campos brutos do CADOP por operadora.
> Aplique a skill `healthintel-daas-governance` e me diga se isso aproxima o produto de entregar tabelas confiáveis, governadas e consumíveis, ou se quebra a regra de exposição controlada e o posicionamento DaaS.”
