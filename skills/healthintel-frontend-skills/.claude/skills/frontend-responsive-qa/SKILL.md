# Skill: frontend-responsive-qa

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise B2B.
O buyer primário acessa em desktop/notebook. Mas páginas públicas (landing, pricing, docs) são acessadas em mobile por decisores e compradores em mobilidade. O produto interno (dashboard de API keys, docs) é predominantemente desktop.

---

## Quando usar esta skill
- Antes de qualquer merge de tela pública (landing, pricing, login, docs)
- Ao criar ou alterar layout de componentes com grid/flex
- Ao revisar telas que recebem dados tabulares (tabelas de dados ANS, planos, endpoints)
- Ao suspeitar de regressão visual em breakpoints específicos
- QA de responsividade antes de deploy para produção

---

## Objetivo
Garantir que cada tela seja funcional, legível e sem quebra visual nos 4 breakpoints críticos do produto, com prioridade em desktop/notebook para uso autenticado e mobile para páginas públicas de conversão.

---

## Breakpoints obrigatórios para teste

| Breakpoint | Largura | Dispositivo representativo | Prioridade |
|---|---|---|---|
| mobile-sm | 375px | iPhone SE, Android entry | Páginas públicas |
| mobile | 390px | iPhone 14, Pixel 7 | Páginas públicas |
| tablet | 768px | iPad, tablets | Páginas públicas |
| notebook | 1280px | MacBook 13", notebooks | **Produto principal** |
| desktop | 1440px | Monitor padrão | **Produto principal** |
| wide | 1920px | Monitor wide | Produto principal |

---

## Checklist obrigatório

### Layout e estrutura
- [ ] Nenhum elemento com overflow horizontal em qualquer breakpoint (sem scroll lateral)
- [ ] Nenhum texto truncado incorretamente (usar `truncate` ou `line-clamp` de forma intencional)
- [ ] Grid/flex colapsa corretamente nos breakpoints definidos
- [ ] Sidebar (quando houver) colapsa para menu hamburger ou drawer em mobile
- [ ] Tabelas de dados: responsivas com scroll horizontal explícito OU reformatadas para mobile (não quebram o layout)

### Tipografia responsiva
- [ ] Headings reduzem tamanho em mobile de forma legível (não menor que 20px em mobile)
- [ ] Body text não menor que 14px em nenhum breakpoint
- [ ] Line-height mantém legibilidade em todos os breakpoints
- [ ] Nenhum texto sobreposto a outro em nenhuma resolução

### Imagens e mídia
- [ ] Imagens com `width` e `height` definidos (evita CLS)
- [ ] Imagens decorativas com `role="presentation"` ou `alt=""`
- [ ] SVGs e ícones escalam corretamente (não esticam, não somem)
- [ ] Nenhuma imagem cortada de forma não intencional

### Interação e touch
- [ ] Touch targets mínimos: 44x44px para todos os elementos interativos em mobile
- [ ] Menus dropdown acessíveis por touch (sem dependência de hover)
- [ ] Formulários: inputs com tamanho mínimo 16px de font-size (evita zoom automático no iOS)
- [ ] Scroll de listas longas funcional em touch (sem `overflow: hidden` que bloqueie)

### Componentes críticos
- [ ] Header/Nav: funcional em todos os breakpoints
- [ ] Hero section: legível e CTA visível em 375px
- [ ] Pricing cards: empilham corretamente em mobile, não ficam espremidos
- [ ] Footer: links acessíveis em mobile, colunas colapsam corretamente
- [ ] Modais: ocupam tela inteira ou quase em mobile (não ficam minúsculos)
- [ ] Toasts/notificações: posicionados corretamente em mobile (não cobrem CTA principal)

### Páginas públicas (prioridade mobile)
- [ ] Landing page: CTA visível above the fold em 375px sem scroll
- [ ] Pricing: todos os planos visíveis (scroll vertical aceitável, scroll horizontal não)
- [ ] Login: formulário centralizado, sem overflow, teclado não cobre CTA em mobile
- [ ] Documentação: sidebar de navegação acessível em mobile

---

## Critérios de aprovação
- Zero scroll horizontal em qualquer breakpoint
- Nenhum elemento interativo menor que 44x44px em mobile
- CTA principal visível above the fold em 375px nas páginas de conversão
- Tabelas com scroll horizontal explícito e indicador visual
- Formulários sem zoom automático em iOS

## Critérios de reprovação
- Scroll horizontal inesperado em qualquer resolução
- Texto ilegível (sobreposição, truncamento sem intenção, tamanho < 12px)
- Botão ou link inatingível por touch (muito pequeno ou coberto)
- Layout quebrado entre 768px e 1024px (tablet landscape é um breakpoint difícil)
- Modal que não fecha em mobile ou que fica fora da viewport
- Input com font-size menor que 16px em mobile (causa zoom no iOS)
- Hero section com CTA abaixo do fold em 375px

---

## Instruções para Claude Code

```
ANTES de qualquer alteração de layout:
1. Identifique os breakpoints configurados: cat tailwind.config.* | grep "screens"
2. Identifique o padrão mobile-first ou desktop-first do projeto
3. NÃO altere breakpoints globais sem discussão
4. Para telas novas: desenvolva mobile-first, progressive enhancement para desktop

Ferramentas de debug responsivo:
- Use DevTools > Device Toolbar para simular breakpoints
- Teste 375px (menor alvo) e 1440px (alvo principal)
- Use "Responsive" mode e arraste para encontrar pontos de quebra

Padrão de classes Tailwind responsivas (mobile-first):
- base = mobile (375px+)
- sm: = 640px+
- md: = 768px+
- lg: = 1024px+
- xl: = 1280px+
- 2xl: = 1536px+
```

### Comandos recomendados
```bash
# Ver breakpoints configurados no projeto
grep -A 20 '"screens"' tailwind.config.ts 2>/dev/null || grep -A 20 "screens:" tailwind.config.js 2>/dev/null

# Encontrar possíveis problemas de overflow
grep -r "overflow-hidden\|overflow-x-hidden" src/ --include="*.tsx" | grep -v "node_modules"

# Encontrar font-sizes fixos que podem causar problema em mobile
grep -r "text-\[" src/ --include="*.tsx" | grep -v "node_modules"

# Verificar se inputs têm text-base ou maior (16px = evita zoom iOS)
grep -r "<input\|<Input" src/ --include="*.tsx" | grep -v "node_modules" | head -20
```

### Checklist de teste manual obrigatório (antes do merge)
```
[ ] Abrir DevTools > Device Toolbar
[ ] Testar em iPhone SE (375px)
[ ] Testar em iPad (768px)
[ ] Testar em 1280px (notebook)
[ ] Testar em 1440px (desktop)
[ ] Verificar ausência de scroll horizontal em cada breakpoint
[ ] Verificar que todos os CTAs estão acessíveis
[ ] Verificar formulários com teclado virtual simulado (mobile)
```

---

## Regra anti-atalho
**Proibido:**
- `overflow-x: hidden` no body como solução para scroll horizontal (mascara o problema)
- `zoom: 0.8` ou `transform: scale()` para "caber" conteúdo em mobile
- Ocultar funcionalidade em mobile com `hidden sm:block` sem equivalente acessível
- Hardcode de `width: 400px` em componente que aparece em mobile
- `white-space: nowrap` sem overflow tratado corretamente
