# Onboarding Enterprise

Fluxo resumido para provisionamento de um cliente enterprise.

## Passos

1. Criar cliente e chave de API.
2. Associar o plano correto em `plataforma.plano`.
3. Garantir `camadas_permitidas` adequadas ao caso de uso.
4. Validar acesso aos endpoints da camada contratada.
5. Registrar consumo e revisar limites de rate limit.

## Checklist técnico

- Confirmar cabeçalhos `X-API-Key`.
- Validar `X-RateLimit-Remaining` e `X-RateLimit-Reset`.
- Testar acesso a Bronze apenas quando o plano permitir.
- Confirmar leitura dos endpoints de Prata e Ouro conforme o tier.

