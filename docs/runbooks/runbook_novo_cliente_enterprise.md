# Runbook — Novo cliente Enterprise

## Objetivo

Provisionar cliente, chave API e plano com validação mínima de contrato.

## Passos

1. Cadastrar cliente em `plataforma.cliente`.
2. Criar plano com `endpoint_permitido` e `limite_rpm` adequados.
3. Gerar chave API via endpoint HTTP — ver procedimento completo em `docs/runbooks/onboarding_chave_comercial.md`.
4. Executar smoke de integração:

```bash
curl -H "X-API-Key: <chave>" http://localhost:8080/v1/meta/endpoints
```

5. Validar acesso a endpoints do plano.

## Critério de encerramento

- chave ativa;
- cliente ativo;
- smoke aprovado;
- logs gravando em `plataforma.log_uso`.

## Ver também

- `docs/runbooks/onboarding_chave_comercial.md` — criação e revogação de chave via `POST /admin/clientes/{id}/chaves`
- `docs/infra/acesso_vps.md` — como acessar a VPS para confirmar provisionamento

