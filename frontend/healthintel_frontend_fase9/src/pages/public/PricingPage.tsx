import { Section, SectionHeader } from '../../components/marketing/Section';
import { Pricing } from '../../components/marketing/Pricing';
import { FAQ } from '../../components/marketing/FAQ';

export function PricingPage() {
  return (
    <>
      <Section id="planos-top" label="planos">
        <SectionHeader
          eyebrow="Planos"
          title="Sandbox, Piloto Assistido e Core API"
          description="Três níveis sobre a mesma API versionada. Sandbox para validar integração, Piloto para validar caso de uso comercial, Core para produção recorrente."
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
    </>
  );
}
