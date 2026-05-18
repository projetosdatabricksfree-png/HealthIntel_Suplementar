import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { endpointCatalog } from '../../data/endpoints';
import { EndpointCard } from '../../components/EndpointCard';
import type { EndpointAvailability, EndpointTier } from '../../types/domain';

const tiers: Array<'todos' | EndpointTier> = ['todos', 'core', 'premium', 'admin', 'sob_demanda'];
const statuses: Array<'todos' | EndpointAvailability> = ['todos', 'disponivel', 'parcial', 'premium', 'roadmap', 'sem_dados'];

const tierLabel: Record<'todos' | EndpointTier, string> = {
  todos: 'Todos',
  core: 'Core',
  premium: 'Premium',
  admin: 'Admin',
  interno: 'Interno',
  sob_demanda: 'Sob demanda'
};

const statusLabel = {
  todos: 'Todos',
  disponivel: 'Disponível',
  parcial: 'Parcial',
  premium: 'Premium',
  roadmap: 'Roadmap',
  sem_dados: 'Sem dados'
} as const;

export function EndpointsPage() {
  const navigate = useNavigate();
  const [tier, setTier] = useState<'todos' | EndpointTier>('core');
  const [status, setStatus] = useState<(typeof statuses)[number]>('todos');
  const [search, setSearch] = useState('');

  const endpoints = useMemo(() => endpointCatalog.filter((endpoint) => {
    const matchesTier = tier === 'todos' || endpoint.tier === tier;
    const availability = endpoint.availability || 'disponivel';
    const matchesStatus = status === 'todos' || availability === status;
    const normalized = `${endpoint.path} ${endpoint.title} ${endpoint.description} ${endpoint.group} ${availability}`.toLowerCase();
    return matchesTier && matchesStatus && normalized.includes(search.toLowerCase());
  }), [tier, status, search]);

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Endpoints</p>
          <h1>Catálogo da API</h1>
          <p>Rotas disponíveis, parciais, premium e roadmap, alinhadas ao smoke de 3 anos.</p>
        </div>
      </div>

      <div className="toolbar">
        <input placeholder="Buscar endpoint..." value={search} onChange={(event) => setSearch(event.target.value)} />
        <div className="filter-row">
          {tiers.map((item) => (
            <button type="button" key={item} className={item === tier ? 'chip chip-active' : 'chip'} onClick={() => setTier(item)}>
              {tierLabel[item]}
            </button>
          ))}
        </div>
        <div className="filter-row">
          {statuses.map((item) => (
            <button type="button" key={item} className={item === status ? 'chip chip-active' : 'chip'} onClick={() => setStatus(item)}>
              {statusLabel[item]}
            </button>
          ))}
        </div>
      </div>

      <div className="endpoint-grid">
        {endpoints.map((endpoint) => (
          <EndpointCard
            key={endpoint.id}
            endpoint={endpoint}
            onSelect={(selected) => navigate(`/app/explorer?endpoint=${encodeURIComponent(selected.id)}`)}
          />
        ))}
      </div>
    </div>
  );
}
