# Runbook — Novo cliente Enterprise

## Objetivo

Provisionar cliente, chave API e plano com validação mínima de contrato.

## Passos

1. Cadastrar cliente em `plataforma.cliente`.
2. Criar plano com `endpoint_permitido` e `limite_rpm` adequados.
3. Gerar chave API com hash SHA-256 armazenado em `plataforma.chave_api`.
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

