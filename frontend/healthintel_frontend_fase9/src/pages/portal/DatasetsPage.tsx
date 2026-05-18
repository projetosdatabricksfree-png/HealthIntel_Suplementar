import { useMemo, useState } from 'react';
import { datasets, datasetStats, statusLabel, statusTone } from '../../data/datasets';
import { Badge } from '../../components/Badge';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import type { DeliveryStatus } from '../../types/domain';

const statusOptions: Array<'todos' | DeliveryStatus> = ['todos', 'pronto', 'parcial', 'premium', 'sem_dados'];

export function DatasetsPage() {
  const [status, setStatus] = useState<'todos' | DeliveryStatus>('todos');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => datasets.filter((dataset) => {
    const matchesStatus = status === 'todos' || dataset.status === status;
    const normalized = `${dataset.nome} ${dataset.codigo} ${dataset.dominio} ${dataset.schema} ${dataset.tabela} ${dataset.descricao} ${dataset.extracao}`.toLowerCase();
    return matchesStatus && normalized.includes(search.toLowerCase());
  }), [search, status]);

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Datasets</p>
          <h1>Checklist de dados entregues</h1>
          <p>Visão técnica e comercial do que está pronto, parcial, premium ou ainda sem dados publicados.</p>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Tabelas Core" value={String(datasetStats.consumoTables)} detail="schema consumo_ans" />
        <MetricCard label="Prontas" value={String(datasetStats.readyTables)} detail="vendáveis hoje" />
        <MetricCard label="Parciais" value={String(datasetStats.partialTables)} detail="com ressalva/recorte" />
        <MetricCard label="Premium" value={String(datasetStats.premiumTables)} detail="schema consumo_premium_ans" />
      </div>

      <div className="toolbar">
        <input placeholder="Buscar tabela, domínio, schema ou extração..." value={search} onChange={(event) => setSearch(event.target.value)} />
        <div className="filter-row">
          {statusOptions.map((item) => (
            <button type="button" key={item} className={item === status ? 'chip chip-active' : 'chip'} onClick={() => setStatus(item)}>
              {item === 'todos' ? 'Todos' : statusLabel[item]}
            </button>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader title="Catálogo HealthIntel Core ANS" description={`${filtered.length} itens filtrados. Fonte: PostgreSQL local validado em ${datasetStats.evaluatedAt}.`} />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Tabela</th>
                <th>Status</th>
                <th>Domínio</th>
                <th>Dados</th>
                <th>Janela</th>
                <th>Para que serve</th>
                <th>Como extrair</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((dataset) => (
                <tr key={dataset.codigo}>
                  <td>
                    <strong>{dataset.nome}</strong>
                    <br />
                    <small className="mono">{dataset.schema}.{dataset.tabela}</small>
                    <br />
                    <small>{dataset.grao}</small>
                  </td>
                  <td><Badge tone={statusTone[dataset.status]}>{statusLabel[dataset.status]}</Badge></td>
                  <td>{dataset.dominio}</td>
                  <td><strong>{dataset.linhas}</strong><br /><small>{dataset.periodos}</small></td>
                  <td>{dataset.janela}<br /><small>{dataset.atualizacao}</small></td>
                  <td>{dataset.usoComercial}</td>
                  <td><code className="mono">{dataset.extracao}</code></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
