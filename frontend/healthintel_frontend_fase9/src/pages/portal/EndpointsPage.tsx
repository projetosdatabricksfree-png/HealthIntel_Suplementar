import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { endpointCatalog } from '../../data/endpoints';
import { EndpointCard } from '../../components/EndpointCard';
import type { EndpointTier } from '../../types/domain';

const tiers: Array<'todos' | EndpointTier> = ['todos', 'core', 'premium', 'admin', 'sob_demanda'];

const tierLabel: Record<'todos' | EndpointTier, string> = {
  todos: 'Todos',
  core: 'Core',
  premium: 'Premium',
  admin: 'Admin',
  interno: 'Interno',
  sob_demanda: 'Sob demanda'
};

export function EndpointsPage() {
  const navigate = useNavigate();
  const [tier, setTier] = useState<'todos' | EndpointTier>('core');
  const [search, setSearch] = useState('');

  const endpoints = useMemo(() => endpointCatalog.filter((endpoint) => {
    const matchesTier = tier === 'todos' || endpoint.tier === tier;
    const normalized = `${endpoint.path} ${endpoint.title} ${endpoint.description} ${endpoint.group}`.toLowerCase();
    return matchesTier && normalized.includes(search.toLowerCase());
  }), [tier, search]);

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Endpoints</p>
          <h1>Catálogo da API</h1>
          <p>Rotas disponíveis no plano Core e módulos adicionais disponíveis por contratação específica.</p>
        </div>
      </div>

      <div className="toolbar">
        <input placeholder="Buscar endpoint..." value={search} onChange={(event) => setSearch(event.target.value)} />
        <div className="filter-row">
          {tiers.map((item) => (
            <button key={item} className={item === tier ? 'chip chip-active' : 'chip'} onClick={() => setTier(item)}>
              {tierLabel[item]}
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
