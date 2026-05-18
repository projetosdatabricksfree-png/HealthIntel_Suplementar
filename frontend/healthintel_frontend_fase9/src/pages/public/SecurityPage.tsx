import { Section, SectionHeader } from '../../components/marketing/Section';
import { SecurityStrip } from '../../components/marketing/SecurityStrip';
import { CurlExample } from '../../components/marketing/CurlExample';
import { Coverage } from '../../components/marketing/Coverage';

export function SecurityPage() {
  return (
    <>
      <Section id="seguranca-top" label="seguranca">
        <SectionHeader
          eyebrow="Segurança e governança"
          title="API key, rate limit, logs e versionamento"
          description="Operação previsível, com chave por cliente, limites por plano, trilha auditável e contratos versionados. Dados públicos da ANS tratados conforme LGPD."
        />
        <div className="section__body">
          <SecurityStrip />
        </div>
      </Section>

      <Section id="exemplo" surface="soft" label="exemplo">
        <SectionHeader
          eyebrow="Chamada autenticada"
          title="Exemplo de requisição com X-API-Key"
          description="Toda chamada autenticada inclui o header X-API-Key. O rate limit é aplicado por chave e por plano."
        />
        <div className="section__body">
          <CurlExample />
        </div>
      </Section>

      <Section id="protecao" label="protecao">
        <SectionHeader
          eyebrow="Proteção comercial"
          title="Sem extração integral, sem redistribuição"
          description="Paginação obrigatória, limite máximo por página, detecção de consumo anômalo e contrato proibindo redistribuição/scraping."
        />
        <div className="section__body">
          <Coverage />
        </div>
      </Section>
    </>
  );
}
