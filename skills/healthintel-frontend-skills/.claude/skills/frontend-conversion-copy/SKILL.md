# Skill: frontend-conversion-copy

## Produto
**HealthIntel Suplementar** — SaaS/DaaS API-first de dados públicos da ANS.
O comprador é técnico-decisor: CTO, Head de Dados, Arquiteto de Soluções, Gerente de TI em operadoras de saúde, seguradoras e healthtechs. Ele avalia: confiabilidade dos dados, maturidade da API, cobertura da ANS e capacidade de integração com seu stack interno.

---

## Quando usar esta skill
- Ao escrever ou revisar copy de landing page, pricing, hero, CTAs
- Ao criar descrições de funcionalidades, benefícios e planos
- Ao revisar textos de onboarding, emails transacionais e mensagens de erro
- Ao criar copy para páginas de documentação pública e changelog
- Quando o copy atual é genérico, vago ou posiciona o produto errado

---

## Objetivo
Garantir que todo texto do produto comunique com precisão: o que é entregue, para quem, qual o valor concreto e por que confiar — eliminando jargão vago, posicionamento errado e perda de conversão por falta de clareza.

---

## Posicionamento correto do produto

### O que o HealthIntel É:
- **Infraestrutura de dados ANS** pronta para consumo via API
- **Dados curados, versionados, governados** da Agência Nacional de Saúde Suplementar
- **API REST** com SLA, autenticação, documentação e suporte enterprise
- **Produto técnico B2B** para times que constroem soluções, não para analistas clicando em dashboards

### O que o HealthIntel NÃO É:
- ❌ Dashboard de BI ou analytics
- ❌ Consultoria de dados ou saúde
- ❌ Ferramenta self-service para gestores sem perfil técnico
- ❌ "Plataforma completa de inteligência de saúde" (vago)
- ❌ Substituto do time de dados do cliente

### A dor que resolve (em linguagem do buyer):
> "Nosso time gasta semanas toda vez que precisa atualizar os dados da ANS. Baixamos manualmente do FTP, normalizamos em Python, versionamos no S3 e ainda assim temos inconsistências. Precisamos disso via API, com histórico, changelog e SLA."

### A proposta de valor (em linguagem do buyer):
> "Dados ANS prontos para produção via API REST. Histórico desde [ano], atualizações automáticas, versionamento semântico e SLA de disponibilidade. Seu time consome em horas, não semanas."

---

## Checklist obrigatório

### Headline principal (hero)
- [ ] Resolve uma dor específica OU descreve o mecanismo com clareza
- [ ] Sem palavras vagas: "inteligente", "completo", "revolucionário", "ecossistema", "solução"
- [ ] Sem metáforas abstratas: "desbloqueie o potencial", "transforme seus dados"
- [ ] Menciona o contexto (ANS / saúde suplementar / dados regulatórios)
- [ ] Especificidade aumenta credibilidade: prefira "dados de 1.200 operadoras" a "dados abrangentes"

### Subheadline
- [ ] Complementa a headline com o mecanismo ou a prova
- [ ] Especifica o que é entregue: API REST, datasets, frequência de atualização
- [ ] Especifica para quem: "para times de dados, BI e engenharia"
- [ ] Máximo 2 linhas

### CTAs
- [ ] Verbo de ação + resultado esperado: "Testar a API" (não "Começar"), "Ver documentação" (não "Saiba mais")
- [ ] CTA primário em destaque visual claro
- [ ] CTA secundário sem competir com o primário
- [ ] Fricção adequada ao estágio: trial → "Criar conta grátis"; enterprise → "Falar com especialista"
- [ ] Nenhum CTA com "Clique aqui", "Saiba mais" ou "Acesse"

### Benefícios e features
- [ ] Benefício primeiro, feature como suporte: "Sem processar dados brutos — API normalizada e pronta"
- [ ] Cada item com especificidade: "ANS Dataset v3.2 — cobertura desde 2019"
- [ ] Sem lista de features sem contexto de valor (para que serve aquele feature?)
- [ ] Máximo 6 benefícios principais (priorize, não liste tudo)

### Pricing
- [ ] Nomes de planos por perfil de uso, não por tamanho: "Starter API", "Data Team", "Enterprise"
- [ ] Métricas claras: chamadas/mês, datasets disponíveis, SLA, suporte
- [ ] Destaque no plano com melhor custo-benefício (badge "Mais popular")
- [ ] CTA por plano diferenciado
- [ ] Sem "Entre em contato para saber o preço" como única opção (bloqueia avaliação)
- [ ] FAQ de objeções: "Os dados são os mesmos do site da ANS?", "Com qual frequência atualizam?", "Tem histórico?"

### Prova social e confiança
- [ ] Logos de clientes ou parceiros (se disponível)
- [ ] Métricas concretas: uptime, volume de dados, clientes ativos, datasets
- [ ] Depoimentos com cargo e empresa (não apenas nome)
- [ ] Certificações relevantes: ISO, SOC 2, conformidade LGPD
- [ ] Data de fundação / tempo no mercado (demonstra estabilidade)

### LGPD e privacidade
- [ ] Menção explícita à conformidade LGPD na landing e no formulário de cadastro
- [ ] Política de privacidade linkada (não apenas no rodapé escondido)
- [ ] Nos formulários: "Seus dados são usados apenas para [finalidade específica]"
- [ ] Opt-in de marketing explícito e separado dos termos de uso
- [ ] Dados da ANS são públicos — comunicar claramente: "dados públicos regulatórios, não dados de pacientes"

### Microcopy
- [ ] Mensagens de erro em linguagem humana (não "Error 422")
- [ ] Tooltips e hints com informação útil, não redundante
- [ ] Labels de formulário descritivos: "E-mail corporativo" (não "E-mail")
- [ ] Placeholders como exemplos: `joao.silva@operadora.com.br`
- [ ] Confirmações de ação com consequência explícita: "Revogar acesso — esta ação não pode ser desfeita"

---

## Critérios de aprovação
- Regra dos 5 segundos: buyer técnico entende o produto sem scrollar
- Nenhuma palavra vaga: "inteligente", "completo", "revolucionário", "plataforma", "ecossistema"
- CTAs com verbos de ação específicos
- Pricing com métricas concretas de uso
- Menção a conformidade LGPD em páginas de captura
- Copy não menciona "dashboard", "BI", "relatórios" como valor principal

## Critérios de reprovação
- Headline que serve para qualquer produto SaaS de dados
- "Transforme seus dados com inteligência artificial" ou equivalente
- CTA "Saiba mais" como único CTA da página
- Pricing sem volume de chamadas ou datasets disponíveis
- Depoimento sem empresa e cargo
- Nenhuma menção à ANS above the fold
- Copy que posiciona produto como ferramenta de análise self-service

---

## Instruções para Claude Code

```
ANTES de reescrever qualquer copy:
1. Confirme o posicionamento com o responsável pelo produto
2. NÃO mude posicionamento unilateralmente — copy é decisão de produto/marketing
3. Apresente 2-3 variantes quando a direção não está clara
4. Preserve termos técnicos que o buyer reconhece: "ANS", "operadora", "TISS", "RPS", "SIP"

Vocabulário do buyer (usar):
- Dados ANS, dados regulatórios, dados públicos curados
- API REST, endpoint, autenticação, rate limit, SLA
- Operadora, seguradora, healthtech, plano de saúde
- Dataset, schema, versão, changelog, histórico
- Time de dados, time de BI, engenharia de dados, arquitetura

Vocabulário a evitar (genérico ou errado):
- "Plataforma inteligente", "solução completa", "ecossistema"
- "Dashboard", "relatórios", "insights" como proposta de valor
- "Transformação digital", "inovação", "disruptivo"
- "Saúde para todos", linguagem de impacto social (produto é B2B técnico)
```

### Template de headline para teste A/B
```
Fórmula 1 — Dor + solução:
"Pare de normalizar dados brutos da ANS. Use a API."

Fórmula 2 — Mecanismo específico:
"Dados ANS versionados e prontos para produção via API REST"

Fórmula 3 — Benefício + especificidade:
"De semanas para horas: dados de 1.200 operadoras via API com SLA"

Fórmula 4 — Para quem + o quê:
"Para times de dados que precisam de dados ANS prontos — sem ETL manual"
```

---

## Regra anti-atalho
**Proibido:**
- Copiar copy genérico de concorrentes ou templates SaaS americanos sem adaptação
- Usar ChatGPT/IA para gerar copy sem revisão contra o posicionamento do produto
- "Em breve" como CTA para feature que não tem data
- Métricas inventadas: "99,9% de uptime" sem evidência real
- Depoimento fictício ou atribuído a pessoa que não autorizou
- Copy que promete o que o produto não entrega ("dados em tempo real" se não for real-time)
