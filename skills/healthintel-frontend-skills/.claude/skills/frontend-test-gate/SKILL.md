# Skill: frontend-test-gate

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise B2B de dados ANS.
Hard gates impedem que código quebrado chegue em produção. Para produto enterprise vendido como infraestrutura confiável, deploy com erro de build, tipo quebrado ou teste falhando é incompatível com o posicionamento do produto.

---

## Quando usar esta skill
- Ao configurar ou revisar o pipeline de CI/CD do frontend
- Ao definir quais checks são obrigatórios antes do merge (branch protection)
- Ao adicionar novo tipo de teste ao projeto
- Ao investigar falha silenciosa em produção que deveria ter sido detectada antes
- Ao onboarding de novo desenvolvedor (definir o que precisa passar antes do merge)

---

## Objetivo
Definir e garantir um conjunto de hard gates que impeçam regressões, erros de tipo, violações de lint, builds quebrados e falhas críticas de smoke test de chegarem à branch principal e ao ambiente de produção.

---

## Hierarquia de gates (ordem de execução)

```
GATE 1 — Lint (< 30s)
  └─ ESLint + regras específicas do projeto
  └─ Prettier (verificação de formatação)
  └─ Resultado: PASS ou FAIL com linha exata do erro

GATE 2 — Typecheck (< 60s)
  └─ tsc --noEmit
  └─ Zero erros de tipo permitidos
  └─ Resultado: PASS ou FAIL com arquivo e linha

GATE 3 — Unit + Integration Tests (< 3min)
  └─ Vitest ou Jest
  └─ Cobertura mínima em paths críticos
  └─ Resultado: PASS ou FAIL com test name

GATE 4 — Build (< 5min)
  └─ next build ou vite build
  └─ Zero warnings tratados como erro (se configurado)
  └─ Bundle size check (se configurado)
  └─ Resultado: PASS ou FAIL

GATE 5 — Smoke Tests E2E (< 5min, em staging)
  └─ Playwright ou Cypress
  └─ Fluxos críticos: login, acesso à API key, docs
  └─ Resultado: PASS ou FAIL com screenshot

GATE 6 — Visual Regression (opcional, paralelo ao GATE 5)
  └─ Chromatic ou Percy
  └─ Aprovação manual se houver diff visual
```

---

## Checklist obrigatório

### Gate 1 — Lint
- [ ] ESLint configurado com regras do projeto (`.eslintrc.*` ou `eslint.config.*`)
- [ ] Regras obrigatórias habilitadas:
  - `no-unused-vars` (erro, não warning)
  - `no-console` (warning em dev, erro em CI)
  - `react-hooks/rules-of-hooks` (erro)
  - `react-hooks/exhaustive-deps` (warning)
  - `@typescript-eslint/no-explicit-any` (erro)
  - `@typescript-eslint/no-non-null-assertion` (warning)
- [ ] Prettier configurado e consistente com ESLint (sem conflito)
- [ ] `lint-staged` configurado para lint no pre-commit (feedback antes do push)
- [ ] CI bloqueia merge se lint falhar

### Gate 2 — Typecheck
- [ ] `tsconfig.json` com `"strict": true`
- [ ] `tsc --noEmit` passa sem erros
- [ ] Nenhum `@ts-ignore` sem comentário explicativo de prazo para remoção
- [ ] Nenhum `@ts-expect-error` em código de produção (permitido apenas em testes)
- [ ] Tipos de resposta de API alinhados com OpenAPI spec (não `any`)

### Gate 3 — Testes unitários e de integração
- [ ] Framework de testes configurado: Vitest (preferível com Vite/Next.js moderno) ou Jest
- [ ] Testes para lógica crítica de negócio:
  - Parsers de dados ANS (formatação de datas, valores, códigos ANS)
  - Validações de schema Zod dos formulários
  - Helpers de autenticação e tratamento de token
  - Formatadores de resposta de API
- [ ] Testes para componentes críticos (mínimo):
  - Formulário de login: submit, erro, loading
  - Formulário de cadastro: validação por campo
  - Componente de API key: mascaramento, reveal, cópia
- [ ] Coverage mínimo nos paths críticos: 80% (não coverage global — coverage direcionado)
- [ ] Nenhum teste com `setTimeout` arbitrário ou `sleep` como solução de timing

### Gate 4 — Build
- [ ] `next build` ou `vite build` passa sem erros
- [ ] Sem variáveis de ambiente obrigatórias ausentes no build
- [ ] Bundle size verificado: alerta se exceder threshold configurado
- [ ] Nenhum `console.error` no output do build (sinal de problema de configuração)
- [ ] Build reproducível (mesmo output para mesmo input)

### Gate 5 — Smoke tests E2E
- [ ] Playwright ou Cypress configurado apontando para ambiente de staging
- [ ] Smoke tests obrigatórios (mínimo):
  ```
  [ ] Landing page carrega sem erro de JS
  [ ] Formulário de login: submit com credenciais válidas → redireciona para dashboard
  [ ] Formulário de login: submit com credenciais inválidas → mensagem de erro
  [ ] Área autenticada: API key visível (mascarada) após login
  [ ] Documentação pública: navegação entre seções funciona
  [ ] Pricing: todos os CTAs têm href funcional (não #)
  ```
- [ ] Smoke tests rodam em branch de staging antes de promover para produção
- [ ] Screenshots em falha salvos como artefato do CI

### Configuração de CI/CD
- [ ] GitHub Actions (ou equivalente) com jobs paralelos onde possível:
  - `lint-typecheck` (paralelo)
  - `test` (paralelo)
  - `build` (após lint-typecheck)
  - `smoke` (após deploy em staging)
- [ ] Branch protection na `main`: todos os gates obrigatórios
- [ ] Pull request não mergeável com gate falhando
- [ ] Notificação de falha no canal de desenvolvimento (Slack, Discord, email)

### Pre-commit hooks (local)
- [ ] Husky configurado com:
  - Pre-commit: lint-staged (lint + format nos arquivos alterados)
  - Pre-push: typecheck + testes relacionados aos arquivos alterados
- [ ] `lint-staged` só processa arquivos do commit (não o projeto inteiro)

---

## Critérios de aprovação
- Todos os 5 gates configurados e obrigatórios no CI
- Branch protection na main com todos os gates como required checks
- Typecheck com `strict: true` sem erros
- Smoke tests cobrindo os 6 fluxos críticos
- Pre-commit hooks funcionando localmente

## Critérios de reprovação
- CI com step de lint/typecheck como `continue-on-error: true`
- Merge feito com gate falhando via force push ou override
- `@ts-ignore` sem prazo ou issue rastreada
- Testes com `describe.skip` ou `it.skip` em código comitado para main
- Smoke tests apontando para localhost (não staging)
- `any` como tipo de retorno em funções críticas
- Build de produção com `console.log` de dados de usuário

---

## Instruções para Claude Code

```
ANTES de configurar qualquer gate:
1. Identifique o framework de build: cat package.json | grep -E '"build"|"dev"|"start"'
2. Identifique o framework de testes: cat package.json | grep -E '"test"|vitest|jest|playwright|cypress"'
3. Verifique se há CI configurado: ls .github/workflows/ 2>/dev/null
4. NÃO substitua o sistema de CI existente — adicione gates ao pipeline existente
5. NÃO configure gates que não podem passar no estado atual do código sem plano de resolução

Para adicionar gate sem quebrar CI existente:
1. Adicione como warning primeiro (--max-warnings)
2. Corrija as violações
3. Converta para erro (gate real)
Esta progressão é obrigatória — não ative gate em erro antes de ter o código passando.
```

### Comandos recomendados
```bash
# Verificar estado atual de lint
npm run lint 2>&1 | tail -20

# Verificar typecheck
npx tsc --noEmit 2>&1 | head -30

# Rodar testes
npm test -- --run 2>&1 | tail -30

# Rodar build
npm run build 2>&1 | tail -30

# Verificar configuração de husky
cat .husky/pre-commit 2>/dev/null
cat .husky/pre-push 2>/dev/null

# Verificar lint-staged config
cat .lintstagedrc.* 2>/dev/null || cat package.json | grep -A 20 '"lint-staged"'

# Listar workflows de CI existentes
ls -la .github/workflows/ 2>/dev/null

# Checar cobertura de testes (vitest)
npx vitest run --coverage 2>&1 | grep -E "All files|Stmts|Branch|Funcs|Lines"
```

### Template de workflow GitHub Actions
```yaml
# Referência — adaptar ao projeto real
name: Frontend CI

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --run

  build:
    needs: [lint-typecheck, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      env:
        # Variáveis de ambiente necessárias para o build
        NEXT_PUBLIC_API_URL: ${{ secrets.STAGING_API_URL }}
```

---

## Regra anti-atalho
**Proibido:**
- `continue-on-error: true` em qualquer gate crítico de CI
- `git push --force` para bypassar gate com falha
- Adicionar `@ts-ignore` para fazer typecheck passar sem resolver o problema
- Desabilitar regra de ESLint globalmente (`// eslint-disable`) sem issue rastreada
- Merge de PR com testes em `skip` ou `todo`
- Smoke tests que passam porque a asserção está errada (false positive)
- Gate de build que depende de segredo não configurado no CI (build quebra para novos contribuidores)
- `npm audit fix --force` sem revisar o que foi alterado (pode quebrar dependências)
