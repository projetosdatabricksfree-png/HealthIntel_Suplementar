# Skill: frontend-api-integration

## Produto
**HealthIntel Suplementar** — SaaS/DaaS API-first de dados ANS.
O frontend consome a própria API do produto. A qualidade da integração é, ela mesma, uma demonstração do produto para clientes técnicos. Integração mal feita comunica: "se o frontend deles não trata erros, a API deles também não é confiável."

---

## Quando usar esta skill
- Ao criar qualquer fetch, chamada de API ou integração com backend
- Ao revisar tratamento de erros, estados de loading e autenticação
- Ao integrar com endpoints documentados no Swagger/OpenAPI
- Ao implementar refresh de token, interceptors e retry logic
- Ao suspeitar de vazamento de estado ou race condition em chamadas assíncronas

---

## Objetivo
Garantir integração robusta, segura e consistente entre frontend e a API FastAPI do HealthIntel — com tratamento correto de autenticação, erros, loading states, tipagem a partir do OpenAPI spec e sem anti-patterns de dados em produção.

---

## Stack de referência
- **Backend**: FastAPI + OpenAPI/Swagger
- **Auth**: Bearer token (JWT) ou API Key (detectar pelo repositório)
- **HTTP client**: detectar no projeto (fetch nativo, axios, ky, wretch)
- **State management**: detectar (React Query/TanStack Query, SWR, Zustand, Context)
- **Tipagem**: OpenAPI → TypeScript types (openapi-typescript ou equivalente)

---

## Checklist obrigatório

### Configuração base
- [ ] URL base da API em variável de ambiente (nunca hardcoded)
- [ ] Variável de ambiente validada em runtime (erro explícito se ausente)
- [ ] HTTP client configurado em instância centralizada (não fetch espalhado pelo código)
- [ ] Timeout configurado (mínimo: 10s para dados, 30s para operações longas)
- [ ] Headers padrão definidos centralmente (Content-Type, Accept)

### Autenticação
- [ ] Token armazenado de forma segura (httpOnly cookie preferível — nunca localStorage para JWT sensível)
- [ ] Token injetado via interceptor/middleware centralizado (não em cada chamada)
- [ ] Refresh de token implementado antes do retry (se aplicável)
- [ ] Fluxo de logout limpa todos os estados de auth e dados do usuário
- [ ] Rota protegida redireciona para login quando token ausente ou expirado
- [ ] API Key do produto (key do cliente) nunca exposta no frontend público

### Tratamento de erros
- [ ] Todos os status HTTP tratados explicitamente:
  - `400` → erro de validação: mostrar mensagem específica do campo
  - `401` → não autenticado: redirecionar para login
  - `403` → sem permissão: mensagem clara, não redireciona para login
  - `404` → recurso não encontrado: estado vazio com contexto
  - `422` → erro de validação FastAPI: parsear `detail` e mostrar por campo
  - `429` → rate limit: mensagem com tempo de espera se disponível no header
  - `500/502/503` → erro de servidor: mensagem genérica + opção de retry
- [ ] Erro de rede (offline, timeout): mensagem específica, diferente de erro de servidor
- [ ] Nenhum `console.error` exposto ao usuário como mensagem de interface
- [ ] Nenhum stack trace exposto na UI

### Loading states
- [ ] Todo fetch tem estado de loading (não apenas "dados ou vazio")
- [ ] Loading state com skeleton ou spinner apropriado ao componente
- [ ] Botão de submit desabilitado durante chamada em andamento (evita duplo envio)
- [ ] Indicador global de loading apenas para operações que afetam toda a UI
- [ ] Skeleton dimensionado aproximadamente igual ao conteúdo esperado (evita CLS)

### Tipagem e contrato de dados
- [ ] Tipos TypeScript gerados ou alinhados com o OpenAPI spec do FastAPI
- [ ] Nenhum `any` em respostas de API (usar tipo correto ou `unknown` + type guard)
- [ ] Validação de resposta antes de usar (Zod, yup, ou type guard explícito)
- [ ] Datas da API (ISO 8601) parseadas corretamente antes de exibição
- [ ] Valores nulos/undefined tratados explicitamente na renderização

### Padrões de data fetching
- [ ] GET: React Query/SWR com cache, stale time e invalidation definidos
- [ ] Mutations (POST/PUT/PATCH/DELETE): loading, success e error states
- [ ] Invalidação de cache após mutation bem-sucedida
- [ ] Não fazer fetch de dados sensíveis em componentes que podem ser desmontados sem cancelamento
- [ ] AbortController ou equivalente para cancelar fetches em unmount

### Paginação e dados volumosos
- [ ] Paginação server-side para listas de dados ANS (nunca carregar tudo)
- [ ] Parâmetros de paginação via URL (page, limit ou cursor) para compartilhamento de estado
- [ ] Infinite scroll ou paginação clássica com loading state por página
- [ ] Total de resultados exibido ao usuário

---

## Critérios de aprovação
- Zero URLs de API hardcoded no código (apenas variáveis de ambiente)
- Todos os status HTTP de erro com tratamento explícito e mensagem ao usuário
- Nenhum fetch sem loading state e error state
- Tipos TypeScript alinhados com o OpenAPI spec
- Botões de submit sem duplo envio
- Token/API key nunca em localStorage para dados sensíveis

## Critérios de reprovação
- URL de API hardcoded (`https://api.healthintel.com.br/v1` diretamente no código)
- `catch(err) => console.log(err)` sem mensagem ao usuário
- Fetch sem loading state (UI trava ou fica em branco silenciosamente)
- `any` como tipo de resposta de API
- Token em localStorage quando deveria ser httpOnly cookie
- Dados de usuário que persistem após logout
- Chamada de API duplicada por falta de cache (React Query/SWR não configurado)
- Erro 422 do FastAPI não parseado (mostrar objeto `{detail: [...]}` bruto ao usuário)

---

## Instruções para Claude Code

```
ANTES de implementar qualquer integração:
1. Leia o OpenAPI spec: GET /openapi.json ou /docs no backend local
2. Identifique o HTTP client do projeto: grep -r "axios\|import ky\|from 'wretch'\|useSWR\|useQuery" src/ | head -10
3. Identifique onde a instância centralizada está: src/lib/api.ts, src/services/, src/api/
4. NÃO crie nova instância de HTTP client — use a existente
5. NÃO altere a estrutura de autenticação existente sem revisão de segurança

Para erros do FastAPI (422 Unprocessable Entity):
O body de resposta tem formato:
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
Parsear e mapear para os campos do formulário correspondentes.

Para autenticação Bearer:
Authorization: Bearer <token>
Implementar via interceptor, não inline em cada chamada.
```

### Comandos recomendados
```bash
# Verificar HTTP client em uso
grep -r "axios\|import ky\|from 'wretch'\|createClient\|useQuery\|useSWR" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | head -10

# Encontrar URLs hardcoded de API
grep -r "https://\|http://localhost" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | grep -v "\.test\." | head -20

# Verificar uso de any em respostas de API
grep -rn ": any\|as any" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | grep -v "\.test\."

# Verificar se variáveis de ambiente estão sendo validadas
cat src/env.ts 2>/dev/null || cat src/env.mjs 2>/dev/null || cat src/lib/env.ts 2>/dev/null

# Ver schema OpenAPI do backend (se rodando localmente)
curl -s http://localhost:8000/openapi.json | python3 -m json.tool | head -100
```

### Geração de tipos a partir do OpenAPI
```bash
# Com openapi-typescript
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts

# Verificar se já existe script no package.json
cat package.json | grep -A 2 "openapi\|codegen\|generate"
```

---

## Regra anti-atalho
**Proibido:**
- Mock de API permanente em produção (`return Promise.resolve(fakeData)`)
- `try { ... } catch {}` silencioso (swallow de erro)
- Dados de teste hardcoded em componentes de produção
- `localStorage.setItem('token', token)` para JWT de autenticação principal
- `setTimeout(() => setLoading(false), 2000)` para simular loading
- Ignorar erros 4xx com `if (response.ok)` sem tratar o else
- Expor API keys do produto nas DevTools do browser (log, variável global, window object)
