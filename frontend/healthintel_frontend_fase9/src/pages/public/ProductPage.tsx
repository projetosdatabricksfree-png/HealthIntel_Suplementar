import { Section, SectionHeader } from '../../components/marketing/Section';
import { DatasetsGrid } from '../../components/marketing/DatasetsGrid';
import { EndpointBrowser } from '../../components/marketing/EndpointBrowser';
import { CurlExample } from '../../components/marketing/CurlExample';
import { Coverage } from '../../components/marketing/Coverage';

export function ProductPage() {
  return (
    <>
      <Section id="produto-top" label="produto">
        <SectionHeader
          eyebrow="Produto"
          title="HealthIntel Core ANS — dados públicos como produto"
          description="API REST com catálogo de dados versionado, paginação consistente, autenticação por X-API-Key, rate limit por plano e logs auditáveis. O produto separa Core pronto, parcial, premium e entregas pontuais."
        />
      </Section>

      <Section id="datasets" surface="soft" label="datasets">
        <SectionHeader
          eyebrow="Datasets"
          title="26 tabelas Core e 11 tabelas Premium mapeadas"
          description="Cada tabela tem finalidade, janela temporal, status comercial e orientação de extração. O que não está pronto aparece como ressalva ou roadmap."
        />
        <div className="section__body">
          <DatasetsGrid />
        </div>
      </Section>

      <Section id="endpoints" label="endpoints">
        <SectionHeader
          eyebrow="Endpoints Core"
          title="Catálogo REST agrupado por dataset"
          description="Busque e filtre por path, dataset, descrição ou status. Os endpoints públicos não exigem chave; os demais exigem header X-API-Key."
        />
        <div className="section__body">
          <EndpointBrowser />
        </div>
        <CurlExample />
      </Section>

      <Section id="escopo" surface="soft" label="escopo">
        <SectionHeader
          eyebrow="Escopo"
          title="O que cobrimos — e o que ainda não"
          description="Transparência sobre o release atual."
        />
        <div className="section__body">
          <Coverage />
        </div>
      </Section>
    </>
  );
}
