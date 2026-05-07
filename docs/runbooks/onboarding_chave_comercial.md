# Runbook — Onboarding de Chave Comercial

## Quando usar

Ao assinar contrato com novo cliente. Executado pelo operador responsavel pelo onboarding.

## Pre-requisitos

- Contrato assinado com `cliente_id` definido no sistema
- Plano escolhido (`starter`, `growth`, `enterprise`, `prata`, `gold`)
- Chave admin da API disponivel (`HML_ADMIN_API_KEY` ou chave de producao)
- API da plataforma acessivel (`https://api.healthintel.com.br`)

## Passo a passo

### 1. Criar cliente na plataforma (se ainda nao existir)

```bash
# Via SQL direto na VPS (enquanto POST /admin/clientes nao existe)
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
  INSERT INTO plataforma.cliente
    (nome, email, plano_id, status, criado_em)
  VALUES (
    '<nome_empresa>',
    '<email_contato>',
    (SELECT id FROM plataforma.plano WHERE nome = '<plano_escolhido>' LIMIT 1),
    'ativo',
    now()
  )
  RETURNING id, nome, plano_id;
"
```

Guardar o `id` (UUID) retornado — e o `cliente_id` para os proximos passos.

### 2. Criar chave API via endpoint admin

```bash
CLIENTE_ID="<uuid_do_cliente>"
ADMIN_KEY="<chave_admin>"

curl -s -X POST \
  "https://api.healthintel.com.br/admin/clientes/${CLIENTE_ID}/chaves" \
  -H "X-API-Key: ${ADMIN_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"descricao": "chave principal - onboarding inicial"}' \
  | jq
```

A resposta contem `chave_plain` — **exibida uma unica vez**. Salvar em gerenciador de senhas antes de fechar.

Resposta esperada:

```json
{
  "chave_id": "uuid",
  "prefixo": "hi_abc1234567",
  "chave_plain": "hi_abc1234567_<32_chars_aleatorios>",
  "cliente_id": "uuid",
  "plano": "growth",
  "criado_em": "2026-05-06T10:00:00-03:00"
}
```

### 3. Entregar a chave ao cliente

Enviar por canal seguro (nunca por e-mail plaintext):
- Gerenciador de senhas compartilhado (1Password, Bitwarden)
- Mensagem direta criptografada

Junto com a chave, enviar:
- URL base: `https://api.healthintel.com.br`
- Documentacao: link para Postman Collection
- Limites do plano: RPM, endpoints, camadas

### 4. Validar chave criada

```bash
# Testar com a nova chave
curl -s -H "X-API-Key: <chave_plain>" \
  "https://api.healthintel.com.br/v1/operadoras?pagina=1&por_pagina=1" | jq .meta
```

Esperado: `200 OK` com `plano` correspondente ao plano contratado.

### 5. Registrar no sistema de CRM / auditoria

Verificar que o evento foi registrado em `plataforma.auditoria_cobranca`:

```sql
SELECT evento, cliente_id, criado_em, operador
FROM plataforma.auditoria_cobranca
WHERE evento = 'chave_criada'
  AND cliente_id = '<uuid_do_cliente>'
ORDER BY criado_em DESC
LIMIT 5;
```

## Revogar uma chave

```bash
# Via SQL (endpoint de revogacao a implementar)
docker exec -i healthintel_postgres psql -U healthintel -d healthintel -c "
  UPDATE plataforma.chave_api
  SET status = 'revogada', atualizado_em = now()
  WHERE id = '<chave_id>';

  INSERT INTO plataforma.auditoria_cobranca (evento, cliente_id, chave_id, criado_em, operador)
  VALUES ('chave_revogada', '<cliente_id>', '<chave_id>', now(), current_user);
"
```

Apos revogar, o Redis invalida automaticamente pelo TTL (60s). Para revogacao imediata:

```bash
docker exec healthintel_redis redis-cli del "api_key:<hash_sha256_da_chave>"
```

## Checklist de onboarding

- [ ] Contrato assinado e `cliente_id` criado
- [ ] Plano configurado corretamente em `plataforma.plano`
- [ ] Chave criada via `POST /admin/clientes/{id}/chaves`
- [ ] `chave_plain` entregue por canal seguro ao cliente
- [ ] Teste de `/v1/operadoras` com a nova chave retornou 200
- [ ] Registro em `plataforma.auditoria_cobranca` confirmado
- [ ] Cliente recebeu documentacao e Postman Collection

## Referencias

- `docs/runbooks/runbook_novo_cliente_enterprise.md` — fluxo completo enterprise
- `docs/comercial/` — contratos e planos
- `api/app/routers/admin_billing.py` — endpoint de criacao de chave
