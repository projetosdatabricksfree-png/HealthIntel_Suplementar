# HealthIntel Suplementar — Frontend Skills

> Skills de Claude Code para o frontend do HealthIntel Suplementar.
> SaaS/DaaS API-first de dados públicos da ANS para times B2B de dados, BI e tecnologia.

---

## Índice de Skills

| # | Skill | Arquivo | Invocar com |
|---|-------|---------|-------------|
| 1 | frontend-product-ux | `.claude/skills/frontend-product-ux/SKILL.md` | `/frontend-product-ux` |
| 2 | frontend-design-system | `.claude/skills/frontend-design-system/SKILL.md` | `/frontend-design-system` |
| 3 | frontend-responsive-qa | `.claude/skills/frontend-responsive-qa/SKILL.md` | `/frontend-responsive-qa` |
| 4 | frontend-accessibility | `.claude/skills/frontend-accessibility/SKILL.md` | `/frontend-accessibility` |
| 5 | frontend-api-integration | `.claude/skills/frontend-api-integration/SKILL.md` | `/frontend-api-integration` |
| 6 | frontend-security-review | `.claude/skills/frontend-security-review/SKILL.md` | `/frontend-security-review` |
| 7 | frontend-performance | `.claude/skills/frontend-performance/SKILL.md` | `/frontend-performance` |
| 8 | frontend-forms-validation | `.claude/skills/frontend-forms-validation/SKILL.md` | `/frontend-forms-validation` |
| 9 | frontend-conversion-copy | `.claude/skills/frontend-conversion-copy/SKILL.md` | `/frontend-conversion-copy` |
| 10 | frontend-test-gate | `.claude/skills/frontend-test-gate/SKILL.md` | `/frontend-test-gate` |

---

## Resumo de cada skill

### 1. `frontend-product-ux`
Garante que páginas públicas (landing, pricing, login, onboarding) comuniquem com clareza o posicionamento de dados ANS via API. Foca em hierarquia de informação, CTAs corretos e jornada de conversão B2B técnico.

### 2. `frontend-design-system`
Padroniza tokens de design, componentes base (botões, inputs, cards, tabelas, badges) e garante consistência visual sem hardcode de cores, fonts ou spacing. Referência para qualquer novo componente.

### 3. `frontend-responsive-qa`
QA de responsividade em 6 breakpoints (375px → 1920px). Foco em: zero scroll horizontal, touch targets corretos, tabelas responsivas e formulários sem zoom automático em iOS.

### 4. `frontend-accessibility`
Conformidade WCAG 2.1 AA: contraste, navegação por teclado, semântica HTML, labels, ARIA e focus management. Cobre checklist completo de componentes interativos e formulários.

### 5. `frontend-api-integration`
Integração robusta com FastAPI: HTTP client centralizado, tratamento de todos os status HTTP, loading states, tipagem a partir do OpenAPI spec e autenticação segura. Zero mocks permanentes.

### 6. `frontend-security-review`
Revisão de segurança: storage de tokens, headers HTTP, rotas protegidas, exposição de API keys, XSS, CSRF, supply chain e conformidade LGPD. Hard stop em credenciais expostas.

### 7. `frontend-performance`
Targets de Core Web Vitals (LCP < 2.5s, CLS < 0.1), otimização de bundle, imagens, lazy loading, cache e renderização server/client. Baseado em medição, não intuição.

### 8. `frontend-forms-validation`
Padronização de formulários críticos (login, cadastro, contato, API key): validação com React Hook Form + Zod, mensagens de erro específicas, tratamento de erros 422 do FastAPI e UX sem duplo envio.

### 9. `frontend-conversion-copy`
Copy SaaS B2B para buyer técnico de saúde suplementar: posicionamento correto (dados ANS via API, não dashboard), headlines específicas, CTAs com verbos de ação, pricing com métricas e conformidade LGPD.

### 10. `frontend-test-gate`
Hard gates de CI/CD: lint (ESLint + Prettier), typecheck (tsc --strict), testes unitários/integração, build verificado, smoke tests E2E com Playwright/Cypress e configuração de branch protection.

---

## Próximo passo recomendado — Auditoria do frontend atual

Execute na ordem abaixo para diagnóstico rápido do estado atual:

```bash
# 1. Estado do lint
npm run lint 2>&1 | tail -20

# 2. Estado do typecheck  
npx tsc --noEmit 2>&1 | head -30

# 3. Estado dos testes
npm test -- --run 2>&1 | tail -20

# 4. Estado do build
npm run build 2>&1 | tail -20

# 5. Vulnerabilidades de dependências
npm audit --audit-level=high

# 6. URLs hardcoded (segurança)
grep -r "https://\|http://localhost" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | grep -v ".test."

# 7. Tokens em localStorage
grep -r "localStorage" src/ --include="*.ts" --include="*.tsx" | grep -i "token\|auth" | grep -v "node_modules"

# 8. Imagens sem dimensões (CLS)
grep -r "<img\|<Image" src/ --include="*.tsx" | grep -v "width=" | grep -v "node_modules"
```

Resultado esperado de cada diagnóstico deve ser documentado e tratado como backlog prioritário antes do próximo deploy para produção.

---

## Regras globais (aplicam a todas as skills)

1. **Detectar antes de criar** — sempre inspecionar o repositório antes de qualquer implementação
2. **Preservar arquitetura existente** — não alterar estrutura de pastas ou padrões estabelecidos
3. **Zero mocks permanentes** — nenhuma solução fake que mascare falha real
4. **Zero segredos no código** — nenhum token, API key ou URL sensível hardcoded
5. **Zero dependências sem justificativa** — cada nova dependência deve ser justificada
6. **Medição antes de otimização** — performance só com evidência medida
7. **Gate antes de merge** — nenhum código sem passar pelos gates configurados
