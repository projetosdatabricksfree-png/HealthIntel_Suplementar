import { Section, SectionHeader } from '../../components/marketing/Section';
import { Pricing } from '../../components/marketing/Pricing';
import { FAQ } from '../../components/marketing/FAQ';
import { CTA } from '../../components/marketing/CTA';

export function PricingPage() {
  return (
    <>
      <Section id="planos-top" surface="default" label="planos">
        <SectionHeader
          eyebrow="Planos"
          title="14 dias grátis no PRO. Suba quando o uso crescer."
          description="Quatro planos self-service via Stripe — do FREE (100 req/mês após trial PRO de 14 dias) ao MAX (25 mil req/dia). Volume além disso, Enterprise pay-as-you-go."
          align="center"
        />
        <div className="section__body">
          <Pricing />
        </div>
      </Section>

      <Section id="faq" surface="soft" label="faq">
        <SectionHeader
          eyebrow="FAQ"
          title="Perguntas frequentes"
          description="Sobre cobrança, SLA, limites e governança."
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
