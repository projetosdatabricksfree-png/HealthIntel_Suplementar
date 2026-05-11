# Skill: frontend-security-review

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise B2B com dados regulatórios da ANS.
Clientes são operadoras de saúde, seguradoras e empresas de tecnologia do setor. Uma vulnerabilidade de segurança no frontend não é apenas técnica — é um risco contratual, regulatório (LGPD) e de reputação que pode encerrar negociações enterprise.

---

## Quando usar esta skill
- Antes de qualquer deploy para produção
- Ao implementar autenticação, sessão, cookies ou armazenamento de tokens
- Ao adicionar dependências novas ao projeto
- Ao revisar qualquer tela que exiba dados de cliente ou API keys
- Ao configurar headers HTTP, CSP, CORS ou políticas de segurança
- Ao suspeitar de vazamento de dados sensíveis em logs, requests ou UI

---

## Objetivo
Garantir que o frontend do HealthIntel não exponha dados sensíveis, tokens, API keys ou vulnerabilidades exploráveis — protegendo clientes, a empresa e os dados regulatórios da ANS sob responsabilidade do produto.

---

## Checklist obrigatório

### Armazenamento de tokens e segredos
- [ ] JWT de autenticação em httpOnly cookie (não localStorage, não sessionStorage)
- [ ] API keys do cliente visíveis apenas na área autenticada, mascaradas por padrão (ex: `sk-••••••••••••••••3f9a`)
- [ ] API keys com botão de reveal explícito (não exibidas por padrão)
- [ ] API keys com botão de cópia (não selecionar com duplo clique na tela)
- [ ] Nenhum secret, token ou key em variáveis de ambiente com prefixo público (`NEXT_PUBLIC_`, `VITE_`)
- [ ] `.env.local` e `.env.production` no `.gitignore`
- [ ] Nenhuma credencial em comentários de código ou mensagens de commit

### Headers de segurança HTTP
- [ ] `Content-Security-Policy` configurado (bloquear inline scripts não autorizados)
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY` ou `SAMEORIGIN`
- [ ] `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] `Permissions-Policy` configurado (restringir câmera, mic, geolocalização)
- [ ] HTTPS obrigatório em produção (HSTS configurado)
- [ ] Cookies com `Secure`, `HttpOnly`, `SameSite=Strict` ou `Lax`

### Rotas protegidas
- [ ] Middleware de autenticação no nível do servidor (não apenas no cliente)
- [ ] Verificação de autenticação acontece server-side antes de renderizar dados sensíveis
- [ ] Rotas autenticadas retornam 401/redirect antes de enviar HTML com dados
- [ ] Nenhum dado sensível no HTML inicial de páginas públicas (SSR/SSG sem dados de usuário)
- [ ] Refresh de página em rota autenticada não expõe estado transitório de loading com dados visíveis

### Exposição de dados na UI
- [ ] Dados pessoais mascarados onde não necessários (email parcial, CPF mascarado)
- [ ] API keys sempre mascaradas por padrão
- [ ] Nenhum dado sensível em URL (query params ou path params expostos no histórico do browser)
- [ ] Dados não persistem em localStorage após logout
- [ ] sessionStorage limpa ao fechar aba (não usar para dados sensíveis entre sessões)

### Proteção contra ataques comuns
- [ ] Nenhum `dangerouslySetInnerHTML` com dados de usuário não sanitizados (XSS)
- [ ] Nenhum `eval()` no código da aplicação
- [ ] Links externos com `rel="noopener noreferrer"` (target="_blank")
- [ ] Formulários com proteção CSRF (cookie SameSite ou token explícito)
- [ ] Inputs de busca e filtros não refletem conteúdo não sanitizado na UI
- [ ] Redirecionamentos pós-login validam que a URL é interna (open redirect prevention)

### Dependências e supply chain
- [ ] `npm audit` sem vulnerabilidades críticas ou altas
- [ ] Dependências atualizadas (sem versões com CVEs conhecidos)
- [ ] Nenhuma dependência que acessa `document.cookie` ou `localStorage` desnecessariamente
- [ ] Scripts de terceiros (analytics, chat) carregados com integridade verificada quando possível

### Logs e debugging
- [ ] `console.log` com dados de usuário removidos antes do build de produção
- [ ] Dados de resposta da API não logados em produção
- [ ] Error boundaries não expõem stack traces para o usuário
- [ ] Source maps desabilitados em produção (ou hospedados em endpoint privado)

---

## Critérios de aprovação
- Zero segredos em variáveis de ambiente públicas
- JWT/token em httpOnly cookie
- Headers de segurança configurados e verificados
- API keys mascaradas na UI com reveal explícito
- `npm audit` limpo de críticos e altos
- Rotas protegidas verificadas server-side

## Critérios de reprovação
- JWT em localStorage
- Qualquer `NEXT_PUBLIC_SECRET_*` ou `VITE_API_SECRET_*` em uso
- `dangerouslySetInnerHTML` com dados não sanitizados
- API keys exibidas em texto plano na UI
- Headers de segurança ausentes em produção
- `console.log(userData)` em código de produção
- Source maps públicos expondo código fonte em produção
- Link externo sem `rel="noopener noreferrer"`
- Credencial hardcoded no código (mesmo que "temporária")

---

## Instruções para Claude Code

```
ANTES de qualquer implementação de autenticação:
1. Identifique o mecanismo atual: grep -r "localStorage\|sessionStorage\|cookie" src/ | grep -i "token\|auth\|session"
2. NÃO migre o mecanismo de auth sem planejamento completo — mudanças parciais criam vulnerabilidades
3. NÃO crie endpoints de auth "temporários" para facilitar desenvolvimento

Para verificar variáveis de ambiente expostas:
1. cat .env.local | grep -v "^#" | grep -v "^$"
2. Qualquer variável que NÃO deva ser pública: NÃO deve ter prefixo NEXT_PUBLIC_ ou VITE_

Para verificar headers de segurança:
- Next.js: next.config.js > headers()
- Vite: servidor de produção (nginx, caddy, vercel.json)
- Verificar em produção: curl -I https://seu-dominio.com | grep -i "x-content\|x-frame\|content-security"
```

### Comandos recomendados
```bash
# Auditar dependências
npm audit --audit-level=high

# Encontrar uso de localStorage/sessionStorage para tokens
grep -r "localStorage\|sessionStorage" src/ --include="*.ts" --include="*.tsx" | grep -i "token\|auth\|key\|secret" | grep -v "node_modules"

# Encontrar dangerouslySetInnerHTML
grep -r "dangerouslySetInnerHTML" src/ --include="*.tsx" | grep -v "node_modules"

# Encontrar links externos sem noopener
grep -r 'target="_blank"' src/ --include="*.tsx" | grep -v 'noopener\|noreferrer' | grep -v "node_modules"

# Encontrar console.log com dados potencialmente sensíveis
grep -rn "console\.\(log\|error\|warn\)" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | grep -v "\.test\."

# Verificar variáveis de ambiente públicas no projeto Next.js/Vite
grep -r "NEXT_PUBLIC_\|VITE_" src/ --include="*.ts" --include="*.tsx" | grep -iv "url\|api_url\|base_url\|public" | grep -v "node_modules"

# Verificar headers de segurança configurados
cat next.config.ts | grep -A 50 "headers" 2>/dev/null || cat next.config.js | grep -A 50 "headers" 2>/dev/null
```

### Verificação de headers em produção
```bash
# Verificar headers de segurança em produção
curl -I https://seu-dominio.com 2>/dev/null | grep -iE "x-content-type|x-frame|content-security|referrer|permissions|strict-transport"

# Verificar cookies com flags de segurança
# No browser: DevTools > Application > Cookies > verificar HttpOnly, Secure, SameSite
```

---

## Regra anti-atalho
**Proibido:**
- `localStorage.setItem('access_token', token)` — nunca para JWT de produção
- `NEXT_PUBLIC_API_SECRET=xyz` — variáveis públicas são visíveis no browser
- Comentar código de segurança "temporariamente" para facilitar debug
- `// TODO: add auth check later` em rota que expõe dados de cliente
- Mock de autenticação que permanece ativo em build de produção
- Hardcode de API key em qualquer arquivo que vai para o repositório
- Desabilitar CSP porque "está quebrando o iframe de terceiro" sem investigar
- `dangerouslySetInnerHTML={{ __html: userInput }}` sem sanitização com DOMPurify
