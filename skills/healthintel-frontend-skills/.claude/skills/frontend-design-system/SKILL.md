# Skill: frontend-design-system

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise de dados ANS.
O design system deve transmitir: precisão, confiança, maturidade técnica. Estética enterprise, não startup colorida. Clareza informacional acima de decoração.

---

## Quando usar esta skill
- Criar ou revisar componentes de UI: botões, cards, inputs, badges, tabelas, modais
- Auditar inconsistências visuais entre telas (spacing, cores, tipografia)
- Implementar ou validar tokens de design (CSS variables, Tailwind theme)
- Garantir que novos componentes sigam o padrão existente antes do merge
- Qualquer tarefa de padronização visual ou de componentes

---

## Objetivo
Garantir um sistema de componentes coeso, documentado e escalável que suporte crescimento do produto sem regressão visual ou inconsistência entre telas.

---

## Checklist obrigatório

### Tokens de design
- [ ] Cores definidas como variáveis/tokens — nunca hardcoded no componente
- [ ] Paleta de cor semântica definida: primary, secondary, destructive, muted, accent, border, background, foreground
- [ ] Escala tipográfica definida: font-size, font-weight, line-height, letter-spacing
- [ ] Escala de spacing consistente (base 4px ou 8px — não misturar)
- [ ] Escala de border-radius consistente
- [ ] Tokens de sombra/elevation definidos
- [ ] Tokens de z-index documentados e centralizados

### Componentes base

#### Botões
- [ ] Variantes obrigatórias: primary, secondary, ghost, destructive, outline
- [ ] Estados: default, hover, active, disabled, loading
- [ ] Tamanhos: sm, md, lg
- [ ] Estado loading com spinner interno (não troca texto por "...")
- [ ] Estado disabled não usa opacity como único indicador
- [ ] Nenhum botão sem aria-label quando não tem texto visível

#### Inputs / Form fields
- [ ] Label sempre visível (nunca apenas placeholder)
- [ ] Estados: default, focus, error, disabled, readonly
- [ ] Mensagem de erro inline, abaixo do campo, com ícone
- [ ] Mensagem de sucesso/hint opcional abaixo do campo
- [ ] Tamanho de clique mínimo: 44x44px (touch target)

#### Cards
- [ ] Variantes: default, interactive (hover state), selected, disabled
- [ ] Padding interno consistente com a escala de spacing
- [ ] Nunca card sem estrutura semântica interna (heading, content, footer quando aplicável)

#### Tabelas de dados
- [ ] Coluna com sorting indica estado ativo visualmente
- [ ] Linha com hover state
- [ ] Estado vazio: mensagem + ação sugerida (não tela em branco)
- [ ] Estado loading: skeleton, não spinner global sobreposto
- [ ] Paginação consistente com o restante do sistema
- [ ] Colunas numéricas alinhadas à direita

#### Badges / Tags
- [ ] Semântica de cor consistente: verde=ativo/sucesso, vermelho=erro/inativo, amarelo=pendente/alerta, cinza=neutro
- [ ] Nunca usar cor como único diferenciador (adicionar ícone ou texto)

#### Modais / Dialogs
- [ ] Sempre com foco preso dentro do modal (focus trap)
- [ ] Fechar com Esc obrigatório
- [ ] CTA destrutivo: botão vermelho + confirmação explícita ("Excluir" não "OK")
- [ ] Overlay com opacity, nunca bloquear scroll sem feedback

### Consistência global
- [ ] Nenhum valor de cor fora da paleta definida (verificar com grep/lint)
- [ ] Nenhum font-size fora da escala definida
- [ ] Nenhum margin/padding fora da escala de spacing
- [ ] Ícones de uma única biblioteca (Lucide, Heroicons, Phosphor — não misturar)
- [ ] Animações/transições com duração e easing consistentes (150ms/200ms ease-out como base)

---

## Critérios de aprovação
- Componente novo segue todos os tokens existentes sem hardcode
- Todas as variantes e estados implementados antes do merge
- Componente testável de forma isolada (Storybook ou equivalente se existir)
- Nenhuma cor, font-size ou spacing hardcoded no componente
- Documentação inline mínima: prop types, descrição de variantes

## Critérios de reprovação
- Cor hardcoded (`#1A2B3C`, `blue`, `rgb(...)`) fora dos tokens
- Componente sem estado de loading quando envolve operação assíncrona
- Componente sem estado de erro quando envolve dados externos
- Mistura de bibliotecas de ícones sem justificativa
- Spacing inventado fora da escala (ex: `margin: 13px`)
- Componente que quebra em dark mode se o sistema suportar dark mode
- Variantes nomeadas diferente do padrão existente (ex: `type="big"` em vez de `size="lg"`)

---

## Instruções para Claude Code

```
ANTES de criar qualquer componente:
1. Leia o tailwind.config.* para entender a escala de cores, spacing e tipografia
2. Verifique se o projeto usa shadcn/ui: ls components/ui/
3. Se usa shadcn/ui: NUNCA recriar Button, Input, Card, Dialog, Badge do zero
4. Verifique a biblioteca de ícones: grep -r "from 'lucide\|from '@heroicons\|from 'phosphor" src/ | head -5
5. Leia um componente existente similar antes de criar um novo (padrão de props, naming, estrutura)

Padrão de nomenclatura:
- Componentes: PascalCase (ApiKeyCard, PlanBadge)
- Props: camelCase, descritivas
- Variantes: string literal union ("sm" | "md" | "lg"), não enum
- Arquivos: kebab-case (api-key-card.tsx)

Estrutura de componente (quando não há padrão definido):
- Props interface no topo
- Variantes com cva() se Tailwind + shadcn
- Export nomeado + default opcional
- Nenhuma lógica de negócio dentro de componente de UI puro
```

### Comandos recomendados
```bash
# Verificar paleta de cores definida
cat tailwind.config.ts | grep -A 50 "colors"

# Listar componentes existentes
ls src/components/ui/ 2>/dev/null || ls components/ui/ 2>/dev/null

# Detectar hardcode de cores
grep -r "#[0-9a-fA-F]\{3,6\}" src/ --include="*.tsx" --include="*.ts" --include="*.css" | grep -v "node_modules"

# Detectar mistura de bibliotecas de ícones
grep -r "from 'lucide\|from '@heroicons\|from 'phosphor\|from 'react-icons" src/ --include="*.tsx" | awk -F"'" '{print $2}' | sort | uniq
```

---

## Regra anti-atalho
**Proibido:**
- Criar componente "temporário" com estilo inline para resolver urgência
- Copiar e colar componente existente com nome diferente sem refatorar para reutilização
- Usar `!important` para corrigir conflito de estilo
- Deixar `TODO: add dark mode later` sem issue rastreada
- Criar variante de botão com cor inventada que não existe no design system
