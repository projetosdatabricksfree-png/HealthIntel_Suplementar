import { useMemo, useState } from 'react';
import { Search, ArrowUpRight } from 'lucide-react';
import { endpointCatalog, endpointStatusLabel, publicDocumentationEndpoints } from '../../data/endpoints';
import type { ApiEndpoint } from '../../types/domain';

function MethodBadge({ method }: { method: string }) {
  return <span className={`method-badge method-badge--${method.toLowerCase()}`}>{method}</span>;
}

export function EndpointBrowser() {
  const [query, setQuery] = useState('');
  const filtered = useMemo(
    () =>
      publicDocumentationEndpoints.filter((e) =>
        `${e.path} ${e.title} ${e.description} ${e.group} ${e.availability}`.toLowerCase().includes(query.toLowerCase())
      ),
    [query]
  );
  const groups = useMemo(() => {
    const acc: Record<string, ApiEndpoint[]> = {};
    filtered.forEach((e) => {
      acc[e.group] = acc[e.group] || [];
      acc[e.group].push(e);
    });
    return acc;
  }, [filtered]);

  return (
    <div className="endpoint-browser">
      <div className="endpoint-browser__chrome">
        <div className="endpoint-browser__search">
          <Search size={14} />
          <input
            type="text"
            placeholder="Buscar endpoint, path, dataset…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <kbd className="mono">⌘K</kbd>
        </div>
        <span className="endpoint-browser__count mono">
          {filtered.length} / {publicDocumentationEndpoints.length} endpoints
        </span>
      </div>
      <div className="endpoint-browser__body">
        {Object.keys(groups).map((g) => (
          <div key={g} className="endpoint-group">
            <div className="endpoint-group__label">{g}</div>
            <ul>
              {groups[g].map((e) => (
                <li key={e.path}>
                  <a href="/documentacao" className="endpoint-row">
                    <MethodBadge method={e.method} />
                    <code className="mono endpoint-row__path">{e.path}</code>
                    <span className="endpoint-row__desc">{e.description}</span>
                    <span className={`status-pill status-pill--${e.availability || 'disponivel'}`}>
                      {endpointStatusLabel[e.availability || 'disponivel']}
                    </span>
                    <span className={`auth-pill auth-pill--${e.authRequired ? 'key' : 'public'}`}>
                      {e.authRequired ? 'API key' : 'publico'}
                    </span>
                    <ArrowUpRight size={14} className="endpoint-row__arrow" />
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="endpoint-browser__empty">
            Nenhum endpoint para <code className="mono">{query}</code>.
          </div>
        )}
      </div>
    </div>
  );
}

export const documentedEndpointCount = endpointCatalog.length;
