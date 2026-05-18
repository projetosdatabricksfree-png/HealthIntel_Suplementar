import { Section, SectionHeader } from '../../components/marketing/Section';
import { SecurityStrip } from '../../components/marketing/SecurityStrip';
import { Coverage } from '../../components/marketing/Coverage';
import { CTA } from '../../components/marketing/CTA';

export function SecurityPage() {
  return (
    <>
      <Section id="seguranca-top" surface="default" label="seguranca">
        <SectionHeader
          eyebrow="Segurança e governança"
          title="API key, rate limit, logs e versionamento"
          description="Operação previsível, com chave por cliente, limites por plano, trilha auditável e contratos versionados. Dados públicos da ANS tratados conforme LGPD."
        />
        <div className="section__body">
          <SecurityStrip />
        </div>
      </Section>

      <Section id="protecao" surface="soft" label="protecao">
        <SectionHeader
          eyebrow="Proteção comercial"
          title="Sem extração integral, sem redistribuição"
          description="Paginação obrigatória, limite máximo por página, detecção de consumo anômalo e contrato proibindo redistribuição/scraping."
        />
        <div className="section__body">
          <Coverage />
        </div>
      </Section>

      <CTA />
    </>
  );
}
