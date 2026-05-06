import type { ApiEndpoint } from '../types/domain';
import { Badge } from './Badge';

const tierTone = {
  core: 'green',
  premium: 'blue',
  admin: 'yellow',
  interno: 'gray',
  bloqueado_mvp: 'red'
} as const;

export function EndpointCard({ endpoint, onSelect }: { endpoint: ApiEndpoint; onSelect?: (endpoint: ApiEndpoint) => void }) {
  return (
    <article className="endpoint-card">
      <div className="endpoint-card-top">
        <span className={`method method-${endpoint.method.toLowerCase()}`}>{endpoint.method}</span>
        <Badge tone={tierTone[endpoint.tier]}>{endpoint.tier}</Badge>
      </div>
      <h3>{endpoint.title}</h3>
      <code>{endpoint.path}</code>
      <p>{endpoint.description}</p>
      {onSelect && (
        <button className="text-button" onClick={() => onSelect(endpoint)}>
          Testar endpoint
        </button>
      )}
    </article>
  );
}
