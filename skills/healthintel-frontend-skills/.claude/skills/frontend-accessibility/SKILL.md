# Skill: frontend-accessibility

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise B2B.
Acessibilidade não é apenas compliance: para produto enterprise vendido a grandes operadoras e seguradoras, é requisito contratual. Violações de a11y bloqueiam licitações e contratos com empresas com políticas de inclusão digital.

---

## Quando usar esta skill
- Antes de qualquer merge de componente novo ou alterado
- Ao criar formulários, modais, dropdowns, tabelas e componentes interativos
- Ao revisar telas de login, cadastro, documentação e pricing
- Quando houver dúvida sobre contraste, navegação por teclado ou semântica HTML
- Antes de deploy para produção de qualquer tela pública

---

## Objetivo
Garantir conformidade mínima com WCAG 2.1 nível AA em todas as telas do produto, com ênfase em: contraste, navegação por teclado, semântica HTML, labels de formulário e ARIA correto.

---

## Referência normativa
- WCAG 2.1 AA (padrão mínimo exigido)
- WAI-ARIA 1.2 para componentes customizados
- Lei Brasileira de Inclusão (LBI 13.146/2015) — art. 63: acessibilidade em TIC
- eMAG 3.1 (modelo de acessibilidade do governo brasileiro) — referência para contratos públicos

---

## Checklist obrigatório

### Contraste de cores
- [ ] Texto normal (< 18px): contraste mínimo 4.5:1 contra o fundo
- [ ] Texto grande (≥ 18px ou ≥ 14px bold): contraste mínimo 3:1
- [ ] Elementos de UI interativos (bordas de inputs, ícones funcionais): contraste mínimo 3:1
- [ ] Texto sobre imagem/gradiente: contraste verificado em toda a área do texto
- [ ] Estados de foco visíveis: contraste do anel de foco mínimo 3:1

### Navegação por teclado
- [ ] Todos os elementos interativos alcançáveis por Tab
- [ ] Ordem de foco lógica e sequencial (segue fluxo visual)
- [ ] Nenhum elemento com `tabindex > 0` (quebra ordem natural)
- [ ] `tabindex="-1"` usado apenas para foco programático (modais, alerts)
- [ ] Skip link "Pular para conteúdo principal" na primeira posição do tab
- [ ] Dropdowns: abrem com Enter/Space, navegam com setas, fecham com Esc
- [ ] Modais: foco vai para o modal ao abrir, retorna ao trigger ao fechar
- [ ] Focus trap em modais e drawers obrigatório

### Semântica HTML
- [ ] `<h1>` único por página, hierarquia H1→H2→H3 sem pular níveis
- [ ] Botões de ação: `<button>` (não `<div onClick>`, não `<a>` sem href)
- [ ] Links de navegação: `<a href>` (não `<button>` para navegação)
- [ ] Listas de itens: `<ul>/<ol>/<li>` (não divs com bullets CSS)
- [ ] Tabelas com `<thead>`, `<tbody>`, `<th scope>` correto
- [ ] `<main>`, `<nav>`, `<header>`, `<footer>`, `<section>`, `<aside>` usados corretamente
- [ ] Formulários com `<form>` e associação correta label→input

### Labels e ARIA
- [ ] Todo input com `<label>` associado via `htmlFor` ou `aria-label`
- [ ] Placeholder NÃO substitui label (placeholder desaparece ao digitar)
- [ ] Ícones funcionais com `aria-label` (ex: botão de fechar modal)
- [ ] Ícones decorativos com `aria-hidden="true"`
- [ ] Imagens informativas com `alt` descritivo
- [ ] Imagens decorativas com `alt=""` e/ou `role="presentation"`
- [ ] Erros de formulário com `aria-describedby` apontando para a mensagem de erro
- [ ] Campos obrigatórios com `aria-required="true"` ou `required`
- [ ] Estados de loading: `aria-busy="true"` no contêiner em carregamento
- [ ] Alertas dinâmicos com `role="alert"` ou `aria-live="polite"`

### Componentes ARIA complexos
- [ ] Dropdown menu: `role="menu"`, `role="menuitem"`, `aria-expanded`
- [ ] Tabs: `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`
- [ ] Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- [ ] Tooltip: `role="tooltip"`, acionado por foco E hover
- [ ] Accordion: `aria-expanded`, `aria-controls`, `aria-labelledby`

### Texto e conteúdo
- [ ] Nenhuma informação transmitida APENAS por cor (adicionar ícone ou texto)
- [ ] Links com texto descritivo ("Ver documentação da API v2" — não "Clique aqui")
- [ ] Idioma da página declarado: `<html lang="pt-BR">`
- [ ] Títulos de página únicos e descritivos (`<title>`)

---

## Critérios de aprovação
- Zero erros críticos no axe-core ou equivalente
- Fluxo completo navegável apenas por teclado (cadastro, login, API keys)
- Contraste AA em todos os textos e elementos interativos
- Todos os inputs com labels visíveis e associados
- Modais com focus trap e retorno de foco ao fechar

## Critérios de reprovação
- Qualquer elemento interativo não alcançável por teclado
- Input sem label (placeholder não conta)
- Contraste abaixo de 4.5:1 em texto normal
- `<div>` ou `<span>` com `onClick` sem `role` e `tabindex`
- Modal sem focus trap
- Ícone funcional sem aria-label
- Erro de formulário não associado ao campo via aria-describedby
- Tabela de dados sem `<th>` e `scope`
- Informação transmitida apenas por cor

---

## Instruções para Claude Code

```
ANTES de criar componente interativo:
1. Pergunte: qual é o padrão ARIA correto para este widget? (consulte WAI-ARIA Authoring Practices)
2. Verifique se o shadcn/ui já implementa o componente com a11y (Button, Dialog, Select, etc.)
3. Se usa Radix UI, a maioria dos padrões ARIA já está implementada — não sobrescreva
4. NÃO use aria-* sem entender o que faz — ARIA incorreto é pior que ausente

Ferramentas de verificação:
- axe DevTools (extensão de browser) — rodar antes do merge
- Lighthouse > Accessibility — score mínimo 90
- keyboard-only navigation test — testar manualmente
- Colour Contrast Analyser (ferramenta desktop) ou coolors.co/contrast-checker

Padrões obrigatórios no código:
- Nunca: <div onClick={handler}>
- Sempre: <button onClick={handler}> ou <a href={url}>
- Nunca: <img src={x}> sem alt
- Sempre: <img src={x} alt="descrição" /> ou alt="" para decorativas
```

### Comandos recomendados
```bash
# Detectar divs/spans com onClick (candidatos a violação semântica)
grep -r "onClick" src/ --include="*.tsx" | grep -E "<div|<span" | grep -v "node_modules"

# Verificar imagens sem alt
grep -r "<img" src/ --include="*.tsx" | grep -v "alt=" | grep -v "node_modules"

# Verificar inputs sem label associado
grep -rn "<input\|<Input" src/ --include="*.tsx" | grep -v "node_modules" | grep -v "aria-label\|htmlFor\|id=" | head -20

# Verificar se html tem lang definido
grep -r 'lang=' src/ --include="*.tsx" | grep "<html" | head -5
```

### Ferramentas de auditoria automatizada
```bash
# Se axe-core estiver disponível como dev dependency
npx axe http://localhost:3000 --exit

# Com pa11y
npx pa11y http://localhost:3000 --standard WCAG2AA

# Lighthouse via CLI
npx lighthouse http://localhost:3000 --only-categories=accessibility --output=json
```

---

## Regra anti-atalho
**Proibido:**
- `aria-hidden="true"` em elemento interativo para "esconder do screen reader"
- Remover outline de foco sem substituição visível (`outline: none` sem `focus-visible`)
- `tabindex="9999"` para forçar foco em elemento específico
- Placeholder como substituto de label
- `role="presentation"` em elemento que tem função semântica real
- Fechar issue de a11y adicionando `aria-label="button"` sem descrever a ação
