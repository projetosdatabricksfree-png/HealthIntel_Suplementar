import { Section, SectionHeader } from '../../components/marketing/Section';
import { ProductSection } from '../../components/marketing/ProductSection';
import { CustomerJourney } from '../../components/marketing/CustomerJourney';
import { DatasetsGrid } from '../../components/marketing/DatasetsGrid';
import { Coverage } from '../../components/marketing/Coverage';
import { CTA } from '../../components/marketing/CTA';

export function ProductPage() {
  return (
    <>
      <Section id="produto-top" surface="default" label="produto">
        <SectionHeader
          eyebrow="Produto"
          title="O time da ANS terceirizado. Você só chama a API."
          description="Quatro motivos pelos quais healthtechs, operadoras e consultorias preferem comprar pipeline da ANS pronto a montar e manter o seu próprio."
          align="center"
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
          description="CADOP, SIB, CNES, DIOPS, IDSS, NIP, Reajustes, Rol/TUSS, Garantias Financeiras, Mercado e Score — todos versionados e datados por competência."
        />
        <div className="section__body">
          <DatasetsGrid />
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

      <CTA />
    </>
  );
}
