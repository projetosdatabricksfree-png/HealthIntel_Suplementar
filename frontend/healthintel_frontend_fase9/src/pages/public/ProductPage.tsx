import { Database, LockKeyhole, ServerCog, ShieldCheck } from 'lucide-react';
import { Card, CardHeader } from '../../components/Card';
import { endpointCatalog } from '../../data/endpoints';
import { EndpointCard } from '../../components/EndpointCard';

export function ProductPage() {
  return (
    <section className="page section">
      <div className="section-heading align-left">
        <p className="eyebrow">Produto</p>
        <h1>HealthIntel Core ANS</h1>
        <p>
          API de inteligência para saúde suplementar, desenhada para vender valor com escopo controlado:
          operadoras, mercado, beneficiários, rankings, score, financeiro e regulatório.
        </p>
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Escopo vendido no MVP" description="Camadas de consumo e API com dados Core." />
          <ul className="check-list">
            <li>CADOP, SIB hot, IDSS, IGR, NIP e financeiro validado.</li>
            <li>Operadora 360, score, ranking e mercado por município.</li>
            <li>Paginação, rate limit e API key obrigatória.</li>
            <li>Sem bronze/prata/dump bruto para cliente.</li>
          </ul>
        </Card>
        <Card>
          <CardHeader title="Fora do MVP" description="Itens bloqueados para não quebrar a operação em VPS." />
          <ul className="danger-list">
            <li>TISS real.</li>
            <li>CNES completo.</li>
            <li>Histórico completo da ANS.</li>
            <li>Exportação integral da base.</li>
          </ul>
        </Card>
      </div>

      <div className="feature-grid">
        {[
          { icon: Database, title: 'Data product', desc: 'O produto final são tabelas e endpoints prontos para consumo.' },
          { icon: ServerCog, title: 'Operação VPS', desc: 'Retenção hot, limpeza de landing e object storage para bruto/histórico.' },
          { icon: LockKeyhole, title: 'Controle de acesso', desc: 'API key, plano, endpoint permitido e camada permitida.' },
          { icon: ShieldCheck, title: 'Segurança comercial', desc: 'Sem download full, com logs de consumo e limite de plano.' }
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
        {endpointCatalog.filter((endpoint) => endpoint.tier === 'core').slice(6, 14).map((endpoint) => (
          <EndpointCard key={endpoint.id} endpoint={endpoint} />
        ))}
      </div>
    </section>
  );
}
