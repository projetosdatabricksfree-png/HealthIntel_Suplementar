# Skill: frontend-performance

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise B2B de dados ANS.
Performance não é apenas experiência do usuário — para produto enterprise com clientes técnicos, LCP lento e bundle pesado comunicam descuido de engenharia. Clientes que avaliam uma API de dados esperam que o próprio site do fornecedor seja rápido.

---

## Quando usar esta skill
- Antes de deploy de qualquer tela nova ou componente pesado
- Ao suspeitar de bundle grande, imagens não otimizadas ou renderização lenta
- Ao implementar carregamento de dados volumosos (tabelas ANS, listas de endpoints)
- Ao analisar métricas de Core Web Vitals em produção
- Ao adicionar dependências novas (avaliar impacto no bundle)

---

## Objetivo
Garantir que o frontend do HealthIntel atinja os targets de Core Web Vitals para produto enterprise: LCP < 2.5s, FID/INP < 200ms, CLS < 0.1 — com bundle otimizado, imagens corretas e estratégia de cache definida.

---

## Targets de performance (produção)

| Métrica | Target | Crítico (falha) |
|---|---|---|
| LCP (Largest Contentful Paint) | < 2.5s | > 4.0s |
| INP (Interaction to Next Paint) | < 200ms | > 500ms |
| CLS (Cumulative Layout Shift) | < 0.1 | > 0.25 |
| FCP (First Contentful Paint) | < 1.8s | > 3.0s |
| TTFB (Time to First Byte) | < 800ms | > 1800ms |
| JS Bundle inicial | < 200KB gzip | > 500KB gzip |
| Total page weight (landing) | < 1MB | > 3MB |

---

## Checklist obrigatório

### Bundle e JavaScript
- [ ] Code splitting por rota configurado (Next.js: automático; Vite: manual se necessário)
- [ ] Dependências pesadas carregadas de forma lazy (charts, editors, PDF viewers)
- [ ] Nenhuma importação de biblioteca inteira quando apenas parte é usada:
  - ❌ `import _ from 'lodash'` → ✅ `import debounce from 'lodash/debounce'`
  - ❌ `import * as icons from 'lucide-react'` → ✅ `import { Search } from 'lucide-react'`
- [ ] `next/dynamic` ou `React.lazy` para componentes pesados não críticos
- [ ] Bundle analyzer rodado após mudanças significativas
- [ ] Tree shaking verificado (sem módulos inteiros incluídos desnecessariamente)

### Imagens
- [ ] Formato WebP/AVIF para imagens rasterizadas (não PNG/JPG puros em produção)
- [ ] `next/image` em projetos Next.js (otimização automática)
- [ ] `width` e `height` explícitos em todas as imagens (evita CLS)
- [ ] `loading="lazy"` em imagens abaixo do fold
- [ ] `priority` apenas na imagem do LCP (hero, logo principal)
- [ ] SVGs otimizados com SVGO antes de comitar
- [ ] Imagens de fundo CSS com srcset para diferentes densidades de pixel

### Carregamento de dados
- [ ] Paginação server-side para listas de dados ANS (nunca carregar 10.000 registros)
- [ ] React Query/SWR com `staleTime` configurado (evitar refetch desnecessário)
- [ ] Dados que não mudam frequentemente com cache agressivo (dados históricos ANS)
- [ ] Dados em tempo real com polling interval razoável (não < 30s sem justificativa)
- [ ] Skeleton screens dimensionados corretamente (evitar CLS quando dados carregam)
- [ ] Virtualização de listas longas (`@tanstack/react-virtual` ou equivalente)

### Renderização
- [ ] Server-side rendering para páginas públicas (landing, pricing, docs) — melhor TTFB e LCP
- [ ] Static generation para conteúdo que não muda com frequência (docs, blog)
- [ ] Client-side rendering apenas para conteúdo dinâmico e autenticado
- [ ] Nenhum `useEffect` disparando em loop (dependências incorretas)
- [ ] Componentes pesados com `React.memo` quando recebem muitos re-renders
- [ ] `useMemo`/`useCallback` usados apenas quando há problema de performance medido (não preventivamente)

### CSS e fontes
- [ ] CSS crítico inline ou no `<head>` para above-the-fold
- [ ] Fontes com `font-display: swap` (não bloqueia renderização)
- [ ] Preload de fonte principal: `<link rel="preload" as="font">`
- [ ] Nenhuma fonte carregada de origem externa não necessária
- [ ] Tailwind com PurgeCSS ativo em produção (zero CSS não utilizado)
- [ ] Animações com `transform` e `opacity` (evitar `top`, `left`, `width` em animações)

### Cache e infra
- [ ] Assets estáticos com cache imutável (hashed filenames + `Cache-Control: immutable`)
- [ ] API responses cacheadas no cliente com estratégia definida (stale-while-revalidate)
- [ ] Prefetch de rotas prováveis (`<Link prefetch>` no Next.js)
- [ ] CDN configurado para assets estáticos em produção

---

## Critérios de aprovação
- Lighthouse Performance ≥ 85 nas páginas públicas
- LCP < 2.5s medido em conexão 4G simulada
- Bundle JS inicial < 200KB gzip
- Zero imagens PNG/JPG sem otimização em produção
- CLS < 0.1 (skeletons dimensionados corretamente)

## Critérios de reprovação
- Bundle JS inicial > 500KB gzip
- Imagens sem `width`/`height` explícitos (CLS)
- `import lodash from 'lodash'` ou `import * from` biblioteca grande
- Lista de dados sem paginação (carregando tudo de uma vez)
- LCP > 4.0s em Lighthouse
- Fonte sem `font-display: swap`
- `useEffect` rodando em loop (dependências incorretas)
- Componente de chart/editor carregado no bundle inicial quando só aparece após interação

---

## Instruções para Claude Code

```
ANTES de otimizar:
1. MEDIR primeiro — não otimize por intuição
2. Rode Lighthouse antes e depois de qualquer mudança de performance
3. Use bundle analyzer para identificar o maior problema: next-bundle-analyzer ou rollup-plugin-visualizer
4. Priorize: (1) bundle size, (2) imagens, (3) dados, (4) renderização

Para Next.js:
- next build && next start → Lighthouse no localhost:3000
- Bundle analyzer: ANALYZE=true next build

Para Vite:
- vite build --report → verifica rollup output
- vite-bundle-visualizer para análise visual

NÃO aplique micro-otimizações (useMemo, useCallback) sem evidência de problema medido.
Estas adicionam complexidade e muitas vezes não melhoram performance real.
```

### Comandos recomendados
```bash
# Analisar bundle Next.js
ANALYZE=true npm run build

# Verificar tamanho do bundle atual
npm run build 2>&1 | grep -E "First Load JS|chunks|kB|MB"

# Encontrar importações de bibliotecas inteiras (candidatos a tree shaking)
grep -r "^import \* as\|^import [a-zA-Z]* from 'lodash'\|^import [a-zA-Z]* from 'moment'" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules"

# Verificar imagens sem dimensões
grep -r "<img\|<Image" src/ --include="*.tsx" | grep -v "width=\|height=" | grep -v "node_modules"

# Verificar uso de next/image vs img nativo (Next.js)
grep -rn "<img " src/ --include="*.tsx" | grep -v "node_modules" | grep -v "// "

# Verificar listas sem paginação ou virtualização
grep -r "\.map(" src/ --include="*.tsx" | grep -v "node_modules" | grep -v "test\|spec" | head -20
```

### Lighthouse via CLI
```bash
# Instalar se necessário
npm install -g lighthouse

# Rodar em produção local
lighthouse http://localhost:3000 --output=html --output-path=./lighthouse-report.html --only-categories=performance

# Checar Core Web Vitals
lighthouse http://localhost:3000 --output=json | python3 -c "
import json, sys
data = json.load(sys.stdin)
cats = data['categories']['performance']
audits = data['audits']
print(f'Score: {cats[\"score\"]*100:.0f}')
for key in ['largest-contentful-paint','cumulative-layout-shift','total-blocking-time']:
    print(f'{key}: {audits[key][\"displayValue\"]}')
"
```

---

## Regra anti-atalho
**Proibido:**
- Remover lazy loading para "simplificar" o código
- Adicionar `loading="eager"` em imagens abaixo do fold para "garantir que carrega"
- Carregar todos os dados da API sem paginação para "evitar complexidade"
- `React.memo` em todo componente como "otimização preventiva"
- Desabilitar SSR para contornar erro de hidratação (resolve o sintoma, não a causa)
- Bundle analyzer apontando problema e merge aprovado sem resolução documentada
