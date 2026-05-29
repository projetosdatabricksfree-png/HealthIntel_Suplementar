import { Section, SectionHeader } from '../../components/marketing/Section';
import { ProductSection } from '../../components/marketing/ProductSection';
import { CustomerJourney } from '../../components/marketing/CustomerJourney';
import { DataCatalog } from '../../components/marketing/DataCatalog';
import { Coverage } from '../../components/marketing/Coverage';
import { CTA } from '../../components/marketing/CTA';

export function ProductPage() {
  return (
    <>
      <Section id="produto-top" surface="default" label="produto">
        <SectionHeader
          eyebrow="Por que DaaS"
          title="Um contrato de dados — não mais um projeto de engenharia"
          description="Quatro garantias pelas quais healthtechs, operadoras e consultorias preferem assinar o dado pronto a montar e manter o próprio pipeline da ANS."
          align="center"
        />
        <div className="section__body">
          <ProductSection />
        </div>
      </Section>

      <Section id="como-funciona" surface="soft" label="como-funciona">
        <SectionHeader
          eyebrow="Como você consome"
          title="Do request ao envelope { dados, meta } em 3 passos"
          description="Sem baixar ZIP, sem decifrar layout fixo, sem descobrir o que mudou no PDF de Resolução. Autentique, chame o endpoint e receba JSON versionado — datado por competência."
        />
        <div className="section__body">
          <CustomerJourney />
        </div>
      </Section>

      <Section id="datasets" surface="default" label="datasets">
        <SectionHeader
          eyebrow="Catálogo"
          title="O produto é o catálogo. Cada dataset, versionado e datado."
          description="Lido do catálogo de produção com grão, janela de competência e contagem real de registros. Status por dataset em /status/cobertura."
        />
        <div className="section__body">
          <DataCatalog />
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
