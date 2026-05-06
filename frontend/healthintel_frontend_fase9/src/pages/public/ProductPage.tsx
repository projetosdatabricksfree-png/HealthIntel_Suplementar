import { Database, LockKeyhole, ShieldCheck, Sparkles } from 'lucide-react';
import { Card, CardHeader } from '../../components/Card';
import { endpointCatalog } from '../../data/endpoints';
import { EndpointCard } from '../../components/EndpointCard';

const featuredEndpointIds = [
  'operadoras',
  'operadora-score-v3',
  'mercado-municipio',
  'rede-municipio',
  'cnes-municipio',
  'cnes-uf',
  'ranking-score',
  'financeiro'
];

export function ProductPage() {
  const featuredEndpoints = endpointCatalog.filter((endpoint) => featuredEndpointIds.includes(endpoint.id));

  return (
    <section className="page section">
      <div className="section-heading align-left">
        <p className="eyebrow">Produto</p>
        <h1>HealthIntel Core ANS</h1>
        <p>
          API de inteligência para saúde suplementar, desenhada para entregar valor rápido com confiabilidade:
          operadoras, mercado, beneficiários, rede CNES, rankings, score, financeiro e regulatório.
        </p>
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Incluído no plano Core" description="Dados tratados e endpoints prontos para operação comercial." />
          <ul className="check-list">
            <li>CADOP, SIB hot, CNES agregado, IDSS, IGR, NIP e financeiro validado.</li>
            <li>Operadora 360, score, ranking e mercado por município.</li>
            <li>Rede assistencial e estabelecimentos CNES por município e UF.</li>
            <li>Paginação, rate limit e API key obrigatória.</li>
            <li>Consumo seguro por API, com acesso controlado por contrato.</li>
          </ul>
        </Card>
        <Card>
          <CardHeader title="Expansões comerciais sob demanda" description="O Core já inclui CNES agregado. Estes pacotes entram quando o cliente precisa de profundidade analítica, histórico maior ou integração dedicada." />
          <ul className="check-list">
            <li>TISS analítico para estudos de utilização, procedimentos e sinistralidade.</li>
            <li>Análises avançadas de rede e cobertura para cruzamentos dedicados e recortes regionais específicos.</li>
            <li>Histórico regulatório estendido para comparação temporal e leitura de tendência.</li>
            <li>Projetos dedicados, integrações específicas e entregas customizadas sob contrato.</li>
          </ul>
        </Card>
      </div>

      <div className="feature-grid">
        {[
          { icon: Database, title: 'Inteligência pronta', desc: 'Indicadores de operadoras, mercado e risco organizados para consumo imediato.' },
          { icon: Sparkles, title: 'Produto de alto impacto', desc: 'Entrega clara para times comerciais, dados, BI, consultorias e healthtechs.' },
          { icon: LockKeyhole, title: 'Controle de acesso', desc: 'API key, plano, endpoint permitido e camada permitida.' },
          { icon: ShieldCheck, title: 'Segurança comercial', desc: 'Consumo paginado, logs de uso e limites definidos por plano.' }
        ].map((item) => {
          const Icon = item.icon;
          return (
            <Card className="feature-card" key={item.title}>
              <Icon size={30} />
              <h3>{item.title}</h3>
              <p>{item.desc}</p>
            </Card>
          );
        })}
      </div>

      <div className="section-heading align-left">
        <h2>Endpoints Core em destaque</h2>
      </div>
      <div className="endpoint-grid">
        {featuredEndpoints.map((endpoint) => (
          <EndpointCard key={endpoint.id} endpoint={endpoint} />
        ))}
      </div>
    </section>
  );
}
