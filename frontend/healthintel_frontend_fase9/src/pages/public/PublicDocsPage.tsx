import { Section, SectionHeader } from '../../components/marketing/Section';
import { EndpointBrowser } from '../../components/marketing/EndpointBrowser';
import { CurlExample } from '../../components/marketing/CurlExample';
import { datasets, datasetStats, statusLabel } from '../../data/datasets';
import { endpointCatalog } from '../../data/endpoints';

const docsDatasets = datasets.filter((dataset) => dataset.status !== 'sem_dados').slice(0, 18);
const roadmapDatasets = datasets.filter((dataset) => dataset.status === 'sem_dados');

export function PublicDocsPage() {
  return (
    <>
      <Section id="docs-top" label="docs">
        <SectionHeader
          eyebrow="Documentação"
          title="Catálogo técnico e comercial do Core ANS"
          description={`Base validada em ${datasetStats.evaluatedAt}: ${datasetStats.consumoTables} tabelas Core, ${datasetStats.premiumTables} tabelas Premium e ${endpointCatalog.length} endpoints catalogados. Cada item abaixo informa finalidade, status e caminho de extração.`}
        />
      </Section>

      <Section id="dataset-guide" surface="soft" label="tabelas">
        <SectionHeader
          eyebrow="Tabelas"
          title="O que existe, para que serve e como extrair"
          description="Use esta visão para alinhar times técnicos e vendas. Pronto para consumo significa que pode entrar no escopo Core; parcial exige ressalva ou recorte; premium depende de contratação específica."
        />
        <div className="section__body">
          <div className="docs-table-wrap">
            <table className="docs-table">
              <thead>
                <tr>
                  <th>Tabela</th>
                  <th>Status</th>
                  <th>Dados disponíveis</th>
                  <th>Para que serve</th>
                  <th>Como extrair</th>
                </tr>
              </thead>
              <tbody>
                {docsDatasets.map((dataset) => (
                  <tr key={dataset.codigo}>
                    <td>
                      <strong>{dataset.nome}</strong>
                      <small className="mono">{dataset.schema}.{dataset.tabela}</small>
                      <small>{dataset.grao}</small>
                    </td>
                    <td>
                      <span className={`status-pill status-pill--${dataset.status}`}>
                        {statusLabel[dataset.status]}
                      </span>
                    </td>
                    <td>
                      <strong>{dataset.linhas}</strong>
                      <small>{dataset.periodos}</small>
                      <small>{dataset.janela}</small>
                    </td>
                    <td>{dataset.usoComercial}</td>
                    <td><code className="mono">{dataset.extracao}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Section>

      <Section id="roadmap" label="roadmap">
        <SectionHeader
          eyebrow="Ressalvas"
          title="Criado no banco, mas não entregue como produto recorrente"
          description="Essas tabelas existem como estrutura ou dependem de carga privada, fonte externa ou contratação pontual. Elas não devem ser vendidas como entrega Core pronta."
        />
        <div className="section__body">
          <div className="roadmap-grid">
            {roadmapDatasets.map((dataset) => (
              <article key={dataset.codigo} className="roadmap-card">
                <span className={`status-pill status-pill--${dataset.status}`}>{statusLabel[dataset.status]}</span>
                <h3>{dataset.nome}</h3>
                <code className="mono">{dataset.schema}.{dataset.tabela}</code>
                <p>{dataset.descricao}</p>
                <small>{dataset.extracao}</small>
              </article>
            ))}
          </div>
        </div>
      </Section>

      <Section id="endpoints" surface="soft" label="endpoints">
        <SectionHeader
          eyebrow="Catálogo"
          title="Endpoints disponíveis, parciais, premium e roadmap"
          description="Use a busca para filtrar por path, dataset, status ou descrição. Endpoints públicos não exigem chave; os demais exigem X-API-Key."
        />
        <div className="section__body">
          <EndpointBrowser />
        </div>
        <CurlExample />
      </Section>
    </>
  );
}
