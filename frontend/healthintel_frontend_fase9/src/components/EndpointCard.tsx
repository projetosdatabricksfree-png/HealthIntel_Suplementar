import type { ApiEndpoint } from '../types/domain';
import { Badge } from './Badge';
import { endpointStatusLabel } from '../data/endpoints';

const tierTone = {
  core: 'green',
  premium: 'blue',
  admin: 'yellow',
  interno: 'gray',
  sob_demanda: 'blue'
} as const;

const tierLabel = {
  core: 'Core',
  premium: 'Premium',
  admin: 'Admin',
  interno: 'Interno',
  sob_demanda: 'Sob demanda'
} as const;

const availabilityTone = {
  disponivel: 'green',
  parcial: 'yellow',
  roadmap: 'blue',
  sem_dados: 'gray',
  premium: 'blue'
} as const;

function renderInlineCode(text: string) {
  const parts = text.split(/`([^`]+)`/);
  return parts.map((part, i) =>
    i % 2 === 1 ? <code key={i}>{part}</code> : part
  );
}

export function EndpointCard({ endpoint, onSelect }: { endpoint: ApiEndpoint; onSelect?: (endpoint: ApiEndpoint) => void }) {
  const availability = endpoint.availability || 'disponivel';
  return (
    <article className="endpoint-card">
      <div className="endpoint-card-top">
        <span className={`method method-${endpoint.method.toLowerCase()}`}>{endpoint.method}</span>
        <Badge tone={tierTone[endpoint.tier]}>{tierLabel[endpoint.tier]}</Badge>
        <Badge tone={availabilityTone[availability]}>{endpointStatusLabel[availability]}</Badge>
      </div>
      <h3>{endpoint.title}</h3>
      <code>{endpoint.path}</code>
      <p>{renderInlineCode(endpoint.description)}</p>
      {onSelect && (
        <button className="text-button" onClick={() => onSelect(endpoint)}>
          Testar endpoint
        </button>
      )}
    </article>
  );
}
