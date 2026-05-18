import { ArrowUpRight } from 'lucide-react';
import { Hero } from '../../components/marketing/Hero';
import { StatsStrip } from '../../components/marketing/StatsStrip';
import { Section, SectionHeader } from '../../components/marketing/Section';
import { ProductSection } from '../../components/marketing/ProductSection';
import { CustomerJourney } from '../../components/marketing/CustomerJourney';
import { DatasetsGrid } from '../../components/marketing/DatasetsGrid';
import { SecurityStrip } from '../../components/marketing/SecurityStrip';
import { Pricing } from '../../components/marketing/Pricing';
import { Coverage } from '../../components/marketing/Coverage';
import { FAQ } from '../../components/marketing/FAQ';
import { CTA } from '../../components/marketing/CTA';

export function HomePage() {
  return (
    <>
      <Hero variant="split" showWidget />

      <StatsStrip />

      <Section id="produto" surface="default" label="produto">
        <SectionHeader
          eyebrow="Por que HealthIntel"
          title="O time da ANS terceirizado. Você só chama a API."
          description="Quatro motivos pelos quais healthtechs, operadoras e consultorias preferem comprar pipeline da ANS pronto a montar e manter o seu próprio."
        />
        <div className="section__body">
          <ProductSection />
        </div>
      </Section>

      <Section id="como-funciona" surface="soft" label="como-funciona">
        <SectionHeader
          eyebrow="Como funciona"
          title="Do checkout à sua primeira requisição em 3 passos"
          description="Self-service total. Pague no Stripe, entre com Google e a API key aparece na sua área do cliente, pronta pra uso. Sem ticket, sem onboarding obrigatório."
        />
        <div className="section__body">
          <CustomerJourney />
        </div>
      </Section>

      <Section id="datasets" surface="default" label="datasets">
        <SectionHeader
          eyebrow="Datasets"
          title="Cobrimos todas as tabelas publicadas pela ANS"
          description="CADOP, SIB, CNES, DIOPS, IDSS, NIP, Reajustes, Rol/TUSS, Garantias Financeiras, Mercado e Score — todos versionados e datados por competência. TISS e SIB nível beneficiário individual são liberados sob solicitação."
          action={
            <a href="/documentacao" className="btn btn--ghost btn--sm">
              Catálogo completo
              <ArrowUpRight size={14} />
            </a>
          }
        />
        <div className="section__body">
          <DatasetsGrid />
        </div>
      </Section>

      <Section id="seguranca" surface="soft" label="seguranca">
        <SectionHeader
          eyebrow="Segurança e governança"
          title="API key, rate limit, logs e versionamento"
          description="Operação previsível, com chave por cliente, limites por plano, trilha auditável e contratos versionados."
        />
        <div className="section__body">
          <SecurityStrip />
        </div>
      </Section>

      <Section id="planos" surface="default" label="planos">
        <SectionHeader
          eyebrow="Planos"
          title="Comece grátis. Suba quando o uso crescer."
          description="Quatro planos self-service via Stripe — do FREE com 100 req/dia ao MAX com 500 mil/dia. Volume além disso, Enterprise sob contrato."
          align="center"
        />
        <div className="section__body">
          <Pricing />
        </div>
      </Section>

      <Section id="escopo" surface="soft" label="escopo">
        <SectionHeader
          eyebrow="Cobertura"
          title="Todas as tabelas ANS — com escopo controlado para dados sensíveis"
          description="Cobertura honesta: o release atual já inclui as famílias completas. TISS e SIB nível beneficiário individual passam por análise comercial antes da liberação."
        />
        <div className="section__body">
          <Coverage />
        </div>
      </Section>

      <Section id="faq" surface="default" label="faq">
        <SectionHeader
          eyebrow="FAQ"
          title="Perguntas frequentes"
          description="Respostas diretas para times técnicos e comerciais avaliando a API."
          align="center"
        />
        <div className="section__body section__body--narrow">
          <FAQ />
        </div>
      </Section>

      <CTA />
    </>
  );
}
