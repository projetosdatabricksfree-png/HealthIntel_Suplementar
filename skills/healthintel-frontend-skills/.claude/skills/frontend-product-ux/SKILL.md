# Skill: frontend-product-ux

## Produto
**HealthIntel Suplementar** — SaaS/DaaS API-first de dados públicos da ANS.
Público-alvo: times internos de BI, dados e tecnologia de operadoras, seguradoras e consultorias de saúde suplementar.
Posicionamento: dados ANS curados, versionados, governados e expostos via API REST/GraphQL com SLA e documentação enterprise.

---

## Quando usar esta skill
- Criar ou revisar páginas públicas: home, pricing, docs, login, cadastro, trial
- Avaliar clareza de proposta de valor e CTAs para buyer B2B técnico
- Auditar fluxo de onboarding: cadastro → validação → primeira chamada de API
- Revisar estrutura de informação de qualquer tela pré-autenticação
- Qualquer tela que precise comunicar confiança, maturidade e valor antes do contrato

---

## Objetivo
Garantir que cada tela comunique: **"dados ANS confiáveis, prontos para produção, com governança e suporte enterprise"** — sem ambiguidade, sem jargão desnecessário, sem fricção na jornada de avaliação e compra.

---

## Contexto do produto (não altere sem validação)
- NÃO é dashboard interno, NÃO é BI embutido, NÃO é consultoria analítica
- O valor entregue é: API + dados curados + documentação + versionamento + SLA
- O comprador avalia: confiabilidade dos dados, cobertura da ANS, latência da API, governança, suporte
- A dor real: times gastando semanas coletando, normalizando e atualizando dados públicos da ANS manualmente
- A solução: dados prontos via API, com histórico, versões, changelog e suporte dedicado

---

## Checklist obrigatório

### Above the fold (home/landing)
- [ ] Headline resolve uma dor específica do buyer técnico B2B de saúde suplementar
- [ ] Subheadline especifica o mecanismo: "dados ANS via API REST, atualizados, com histórico desde XXXX"
- [ ] 1 CTA primário visível sem scroll ("Solicitar acesso" / "Ver documentação" / "Testar API")
- [ ] Sem jargões vagos: "plataforma inteligente", "solução completa", "ecossistema"
- [ ] Nenhuma imagem decorativa sem propósito informativo

### Proposta de valor
- [ ] 3 pilares comunicados visualmente: Dados, API, Governança
- [ ] Cobertura da ANS explicitada: quais datasets, qual período, frequência de atualização
- [ ] Comparação implícita ou explícita com a alternativa (coletar dados brutos da ANS manualmente)

### Pricing
- [ ] Planos nomeados por perfil de uso, não por tamanho genérico (Starter/Pro/Enterprise)
- [ ] Métricas claras: chamadas/mês, endpoints disponíveis, SLA, suporte
- [ ] Plano recomendado destacado visualmente
- [ ] CTA diferenciado por plano: trial self-service vs. contato comercial para enterprise
- [ ] Âncora de credibilidade: clientes, volume de dados, uptime histórico

### Login / Acesso
- [ ] Labels visíveis em todos os campos (nunca apenas placeholder)
- [ ] CTA do botão: "Entrar" (não "Submit", não "Login")
- [ ] Recuperação de senha acessível e visível
- [ ] Mensagem de erro específica, nunca genérica ("E-mail não encontrado" vs "Credenciais inválidas")
- [ ] Nenhum redirecionamento pós-login para tela em branco ou 404

### Onboarding pós-cadastro
- [ ] Primeira tela logada mostra próximo passo concreto (não dashboard vazio)
- [ ] API key gerada ou acessível na primeira sessão
- [ ] Link direto para documentação de quickstart
- [ ] Indicador de progresso se onboarding tem múltiplas etapas

### Navegação global
- [ ] Itens de menu refletem jornada do buyer: Produto → Docs → Pricing → Login
- [ ] Mobile menu funcional e acessível
- [ ] Sem links quebrados em nenhum estado de navegação

---

## Critérios de aprovação
- Regra dos 5 segundos: usuário técnico B2B entende o produto sem scrollar
- Fluxo cadastro → API key em menos de 3 cliques
- Nenhuma tela sem CTA ou próximo passo claro
- Copy sem ambiguidade sobre o que é entregue (dados, não análise; API, não dashboard)
- Pricing com métricas objetivas, sem "entre em contato para saber mais" como única opção

## Critérios de reprovação
- Headline genérica que serve para qualquer produto de dados
- CTAs com verbos fracos: "Saiba mais", "Clique aqui", "Acesse"
- Tela de login sem recuperação de senha visível
- Onboarding que não entrega a API key na primeira sessão
- Pricing sem métricas concretas de uso
- Qualquer menção a "dashboard", "BI" ou "relatórios" como proposta de valor principal
- Copy que posiciona o produto como consultoria ou serviço gerenciado

---

## Instruções para Claude Code

```
ANTES de qualquer alteração:
1. Identifique o framework: Next.js, React, Vite — leia package.json e next.config.*
2. Mapeie as rotas públicas existentes: pages/, app/, src/pages/, src/app/
3. Identifique o sistema de componentes: shadcn/ui, Radix, custom — leia components/
4. NÃO crie componentes novos sem verificar se já existem equivalentes
5. NÃO altere copy sem aprovação explícita do responsável pelo produto

Padrão de intervenção:
- Prefira refatoração cirúrgica sobre reescrita completa
- Mantenha consistência com o padrão de nomenclatura existente
- Preserve hierarquia de componentes existente
- Documente no PR o que mudou e por quê (UX rationale)
```

### Comandos recomendados
```bash
# Mapear estrutura de rotas públicas
find . -path ./node_modules -prune -o -name "*.tsx" -print | grep -E "(page|layout|index)" | head -40

# Verificar componentes existentes
ls src/components/ || ls components/

# Checar se há testes de integração para fluxos de auth
find . -name "*.test.*" -o -name "*.spec.*" | xargs grep -l "login\|auth\|signup" 2>/dev/null
```

---

## Regra anti-atalho
**Proibido:**
- Criar mocks de autenticação permanentes
- Simular fluxo de onboarding com dados fake hardcoded
- Deixar CTAs com href="#" ou onClick vazio
- Criar telas de placeholder com "Em breve" sem data ou funcionalidade real
- Qualquer solução que faça o produto "parecer" funcionar sem funcionar de fato
