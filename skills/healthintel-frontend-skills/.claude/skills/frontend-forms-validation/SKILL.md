# Skill: frontend-forms-validation

## Produto
**HealthIntel Suplementar** — SaaS/DaaS enterprise B2B de dados ANS.
Formulários são pontos de conversão críticos: login, cadastro, solicitação de acesso enterprise, contato comercial. Um formulário mal validado ou com UX ruim aumenta a taxa de abandono e transmite falta de cuidado com o produto.

---

## Quando usar esta skill
- Ao criar ou revisar qualquer formulário do produto
- Ao implementar validação client-side e tratamento de erros de API
- Ao revisar fluxo de login, cadastro, recuperação de senha, contato comercial
- Ao suspeitar de UX ruim em formulários (erros confusos, re-submit, perda de dados)
- Antes de qualquer formulário entrar em produção

---

## Objetivo
Garantir que todos os formulários do HealthIntel sejam funcionais, acessíveis, seguros e com feedback claro — eliminando abandono por frustração, duplo envio e mensagens de erro genéricas.

---

## Stack de referência
Detectar no repositório antes de implementar:
- **Validação**: React Hook Form + Zod (padrão recomendado), Formik + Yup, ou nativo
- **UI**: shadcn/ui Form components, Radix UI, ou componentes próprios
- **Feedback de erro**: inline por campo + toast para erros globais

---

## Formulários críticos do produto

### 1. Login
- Email + senha
- Recuperação de senha (link "Esqueceu sua senha?")
- Opcional: SSO/OAuth empresarial

### 2. Cadastro / Solicitar acesso
- Nome completo, e-mail corporativo, empresa, cargo
- Aceite de termos e LGPD
- Opcional: CNPJ da empresa para clientes enterprise

### 3. Contato comercial / Falar com vendas
- Nome, e-mail, empresa, mensagem
- Segmentação por interesse (plano, integração, suporte)

### 4. Recuperação de senha
- E-mail para envio do link
- Nova senha + confirmação de senha

### 5. Configuração de API key (área autenticada)
- Nome da key, permissões, expiração, IP allowlist

---

## Checklist obrigatório

### Estrutura e semântica
- [ ] `<form>` com `onSubmit` (não `onClick` no botão)
- [ ] Botão de submit com `type="submit"` (não `type="button"`)
- [ ] Todos os campos com `<label>` visível e `htmlFor` correto
- [ ] `autocomplete` apropriado: `email`, `current-password`, `new-password`, `name`, `organization`
- [ ] `inputmode` correto em mobile: `email`, `tel`, `numeric`
- [ ] `type` correto: `email`, `password`, `tel`, `text`

### Validação client-side
- [ ] Validação ocorre no `onBlur` (não apenas no submit) para feedback imediato
- [ ] Validação no submit valida todos os campos novamente antes de enviar
- [ ] Mensagens de erro específicas por campo (não "Campo inválido")
- [ ] Mensagens de erro em português, sem jargão técnico
- [ ] E-mail: formato válido + domínio presente
- [ ] Senha: requisitos explícitos visíveis ANTES do erro (não apenas depois de falhar)
- [ ] Confirmação de senha: valida em tempo real quando o segundo campo perde foco
- [ ] CNPJ (se aplicável): formato e dígitos verificadores
- [ ] Campos obrigatórios marcados com `*` e legenda explicativa

### Mensagens de erro
- [ ] Erro aparece ABAIXO do campo, nunca acima ou em tooltip
- [ ] Ícone de erro (vermelho) acompanha a mensagem
- [ ] Mensagem desaparece quando o campo é corrigido (não persiste após correção)
- [ ] Erro global (ex: "E-mail já cadastrado") em banner no topo do form ou toast
- [ ] Erro de API mapeado para campo específico quando possível (422 do FastAPI)

### Padrões de UX
- [ ] Placeholder com exemplo de valor (`exemplo@empresa.com.br`, não apenas "E-mail")
- [ ] Campos de senha com toggle show/hide
- [ ] Força da senha visual em formulários de criação de conta
- [ ] Loading state no botão de submit durante chamada de API
- [ ] Botão desabilitado durante loading (evita duplo envio)
- [ ] Scroll automático para o primeiro campo com erro após tentativa de submit
- [ ] Dados preenchidos preservados após erro de API (não limpar o form)
- [ ] Mensagem de sucesso clara após submit bem-sucedido

### Segurança em formulários
- [ ] Campo senha com `autocomplete="current-password"` ou `"new-password"` (não `"off"`)
- [ ] Nenhum dado sensível em query params após submit (usar POST, não GET)
- [ ] CNPJ/dados sensíveis sem formatação persistida em log
- [ ] Honeypot ou outro mecanismo anti-spam em formulários públicos (contato, cadastro)

### Acessibilidade (a11y)
- [ ] Erros associados ao campo via `aria-describedby`
- [ ] Campo inválido com `aria-invalid="true"`
- [ ] Campos obrigatórios com `aria-required="true"`
- [ ] Foco vai para o primeiro campo com erro após submit inválido
- [ ] Screen reader anuncia erros (role="alert" ou aria-live)

---

## Critérios de aprovação
- Zero campo sem label visível
- Mensagens de erro específicas por campo, em português
- Botão de submit desabilitado durante loading
- Dados preservados após erro de API
- Validação funciona com Tab + Enter (navegação por teclado)
- Schema de validação alinhado com as regras de negócio do backend

## Critérios de reprovação
- "Campo inválido" como mensagem de erro genérica
- Formulário limpa todos os dados após erro de API
- Duplo envio possível (botão não desabilitado durante loading)
- Campo de senha sem toggle show/hide
- `<div onClick>` como botão de submit
- Placeholder substituindo label
- Scroll para topo após erro sem indicar qual campo está errado
- Validação apenas no submit (sem feedback no onBlur)
- Formato de e-mail aceito sem validação de domínio (aceitar "a@b")

---

## Instruções para Claude Code

```
ANTES de criar qualquer formulário:
1. Verifique se há sistema de formulários instalado: 
   grep "react-hook-form\|formik\|zod\|yup" package.json
2. Verifique componentes de Form existentes:
   ls src/components/ui/ | grep -i "form\|input\|label\|error"
3. Se usa shadcn/ui: use Form, FormField, FormItem, FormLabel, FormMessage do shadcn
4. NÃO crie sistema de validação próprio se react-hook-form + zod já está no projeto
5. Schema Zod deve espelhar as regras do backend (verificar no OpenAPI spec)

Padrão React Hook Form + Zod + shadcn/ui:
- Schema Zod define as regras
- useForm<z.infer<typeof schema>> para tipagem
- FormField + FormMessage para feedback de erro
- resolver: zodResolver(schema)

Para erros de API (422 FastAPI):
- Parsear detail[] e usar setError() do react-hook-form por campo
- Ex: setError("email", { message: "E-mail já cadastrado" })
```

### Comandos recomendados
```bash
# Verificar biblioteca de formulários instalada
cat package.json | grep -E "react-hook-form|formik|zod|yup|valibot"

# Listar componentes de formulário existentes
ls src/components/ui/ 2>/dev/null | grep -iE "form|input|label|field|error"

# Verificar formulários existentes no projeto
grep -r "useForm\|<Formik\|<form" src/ --include="*.tsx" | grep -v "node_modules" | grep -v "test" | head -20

# Verificar se todos os inputs têm labels associados
grep -rn "<Input\|<input" src/ --include="*.tsx" | grep -v "node_modules" | head -20

# Verificar se há honeypot em formulários públicos
grep -r "honeypot\|_honey\|bot_field" src/ --include="*.tsx" | grep -v "node_modules"
```

### Schema Zod de referência para formulário de cadastro
```typescript
// Referência — adaptar ao schema real do backend
const cadastroSchema = z.object({
  nome: z.string().min(2, "Nome deve ter pelo menos 2 caracteres"),
  email: z.string().email("Informe um e-mail válido").refine(
    (email) => email.includes("."), "Informe um domínio válido"
  ),
  empresa: z.string().min(2, "Informe o nome da empresa"),
  cargo: z.string().min(2, "Informe seu cargo"),
  termos: z.literal(true, {
    errorMap: () => ({ message: "Você deve aceitar os termos para continuar" })
  }),
})
```

---

## Regra anti-atalho
**Proibido:**
- `alert()` para mostrar erros de validação
- Validação apenas no backend (sem feedback client-side)
- Limpar o formulário após erro de servidor
- `disabled={isLoading}` sem indicador visual de loading no botão
- Mensagem de erro genérica mapeando todos os erros 400/422 para "Erro ao processar"
- Schema Zod diferente das regras reais do backend (falso senso de validação)
- `setTimeout(() => clearErrors(), 3000)` para sumir com erros sem o usuário corrigir
