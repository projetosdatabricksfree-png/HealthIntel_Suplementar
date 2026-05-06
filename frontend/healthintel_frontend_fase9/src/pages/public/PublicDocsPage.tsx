import { useMemo, useState } from 'react';
import { publicDocumentationEndpoints } from '../../data/endpoints';
import { EndpointCard } from '../../components/EndpointCard';
import { CodeBlock } from '../../components/CodeBlock';

export function PublicDocsPage() {
  const [group, setGroup] = useState('Todos');
  const groups = useMemo(() => ['Todos', ...Array.from(new Set(publicDocumentationEndpoints.map((item) => item.group)))], []);
  const endpoints = group === 'Todos'
    ? publicDocumentationEndpoints
    : publicDocumentationEndpoints.filter((item) => item.group === group);

  return (
    <section className="page section">
      <div className="section-heading align-left">
        <p className="eyebrow">Documentação</p>
        <h1>Catálogo de endpoints</h1>
        <p>
          O portal segue o modelo API-first: documentação simples, exemplos por endpoint,
          autenticação por `X-API-Key` e live tester no dashboard. O catálogo público mostra
          apenas endpoints do produto inicial Core ANS.
        </p>
      </div>

      <div className="docs-auth-box">
        <h2>Autenticação</h2>
        <p>Envie sua chave no header de toda chamada protegida.</p>
        <CodeBlock code={`X-API-Key: sua_chave_de_api`} />
      </div>

      <div className="filter-row">
        {groups.map((item) => (
          <button key={item} className={item === group ? 'chip chip-active' : 'chip'} onClick={() => setGroup(item)}>
            {item}
          </button>
        ))}
      </div>

      <div className="endpoint-grid">
        {endpoints.map((endpoint) => <EndpointCard key={endpoint.id} endpoint={endpoint} />)}
      </div>
    </section>
  );
}
