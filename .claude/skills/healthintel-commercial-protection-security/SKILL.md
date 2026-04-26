---
name: healthintel-commercial-protection-security
description: Proteção comercial, segurança e controle de acesso — impedir cópia integral do produto e garantir uso governado.
---

# HealthIntel — Proteção Comercial e Segurança

## Quando usar esta skill

- Ao desenhar/alterar autenticação, autorização, rate limit, paginação, hardening ou logging.
- Ao provisionar cliente em `scripts/admin/provisionar_cliente_postgres.py`.
- Ao mexer em roles PostgreSQL (`healthintel_cliente_reader`, `healthintel_premium_reader`).
- Ao avaliar feature que possa, direta ou indiretamente, viabilizar download integral do produto.

## Regras obrigatórias

1. **O cliente nunca deve conseguir baixar a base inteira de forma irrestrita.** Esse é o invariante comercial. Toda decisão técnica passa por esse filtro.
2. Mecanismos obrigatórios em camada de exposição:
   - **autenticação** (X-API-Key na API; user/password PostgreSQL com role limitada no SQL),
   - **autorização por plano e por camada** (`verificar_plano`, `verificar_camada`),
   - **paginação** com teto máximo por página,
   - **filtros** (preferencialmente obrigatórios em endpoints de granularidade fina),
   - **rate limit** (com multiplicadores por camada: Bronze 3×, Prata 2×, Gold 1×),
   - **logging auditável** em `plataforma.log_uso`.
3. Topologia de roles SQL:
   - `healthintel_cliente_reader` → **somente** `consumo_ans`.
   - `healthintel_premium_reader` → **somente** `consumo_premium_ans` (e o que estiver explicitamente liberado).
   - **Nenhum cliente** acessa `bruto_ans`, `stg_ans`, `int_ans`, `nucleo_ans`, `api_ans` (interna do FastAPI) ou `plataforma`.
   - Roles `NOLOGIN` quando são apenas “grupo de permissões”; usuário individual `LOGIN` por cliente herda a role.
4. Toda query/request relevante deve ser **auditável** em `plataforma.log_uso` quando aplicável (cliente, endpoint, timestamp, volume, latência, plano).
5. Sinais de abuso (rajadas anômalas, varreduras sequenciais, paginação exaustiva, padrão de scraping) devem disparar:
   - **throttle**,
   - **bloqueio temporário** automático ou manual,
   - **alerta operacional**,
   - **revisão contratual** com o cliente.
6. **Não propor feature** que facilite cópia integral do produto: export massivo livre, endpoint “dump tudo”, role com `SELECT` em schema interno, link público sem auth, dataset baixável inteiro por um único request.
7. Segredos e credenciais ficam fora do código. Mudança em hardening/CORS/headers passa por revisão consciente — não por “colocar `*` que destrava o frontend”.

## Anti-padrões

- Liberar `GRANT SELECT ON ALL TABLES IN SCHEMA nucleo_ans TO healthintel_cliente_reader`.
- Endpoint sem paginação “porque o volume é pequeno” (volume cresce; produto fica exposto).
- CORS aberto em `*` em produção para “simplificar integração”.
- Compartilhar X-API-Key entre clientes ou logar a key em texto claro.
- Tratar abuso como problema de UX (“o cliente está pedindo muito”) em vez de problema comercial/de proteção.
- Criar “endpoint admin” sem autorização forte porque “é interno”.
- Dar acesso direto a `consumo_premium_ans` para cliente que comprou plano standard “só para ele ver”.
- Aceitar pedido de cliente do tipo “me manda o CSV completo da base” — isso quebra o produto.

## Checklist antes de concluir

- [ ] A feature respeita o invariante: cliente não consegue baixar a base inteira de forma irrestrita?
- [ ] Auth, autorização por plano/camada, paginação, filtros, rate limit e logging estão todos presentes onde se aplicam?
- [ ] Roles SQL apontam **apenas** para o schema correto da camada de consumo do cliente?
- [ ] Nenhum cliente recebeu acesso a schema interno?
- [ ] `plataforma.log_uso` está sendo alimentado com o necessário para auditoria e billing?
- [ ] Sinais de abuso disparam throttle/bloqueio/alerta — não apenas log silencioso?
- [ ] Nenhum endpoint/role/script novo é uma porta de saída do produto inteiro?
- [ ] Mudanças em hardening/CORS são justificadas e mínimas?

## Exemplo de prompt de uso

> “Cliente pediu acesso SQL direto para o time de dados dele rodar análises.
> Aplique a skill `healthintel-commercial-protection-security` e me oriente:
> (1) qual role usar (`healthintel_cliente_reader` vs `healthintel_premium_reader`) conforme o plano,
> (2) como provisionar o usuário com `scripts/admin/provisionar_cliente_postgres.py`,
> (3) que controles (rate, log, alerta) precisam estar ativos,
> (4) o que **não** dar acesso (schemas internos, `api_ans`, `plataforma`).”
