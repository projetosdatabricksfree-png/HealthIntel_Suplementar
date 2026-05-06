import { datasets } from '../../data/datasets';
import { Badge } from '../../components/Badge';
import { Card, CardHeader } from '../../components/Card';

const tone = {
  ativo: 'green',
  em_validacao: 'yellow',
  sob_demanda: 'blue'
} as const;

const statusLabel = {
  ativo: 'Publicado',
  em_validacao: 'Em validação',
  sob_demanda: 'Sob demanda'
} as const;

const camadaLabel = {
  api: 'API',
  consumo: 'Consumo',
  interno: 'Módulo avançado'
} as const;

export function DatasetsPage() {
  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Datasets</p>
          <h1>Escopo de dados do produto</h1>
          <p>Controle visual do que está publicado, em validação ou disponível como módulo adicional.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Catálogo HealthIntel Core ANS" description="Dados publicados, produtos derivados e expansões comerciais." />
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Dataset</th>
                <th>Status</th>
                <th>Camada</th>
                <th>Atualização</th>
                <th>Retenção</th>
                <th>Descrição</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr key={dataset.codigo}>
                  <td><strong>{dataset.nome}</strong><br /><small>{dataset.codigo}</small></td>
                  <td><Badge tone={tone[dataset.status]}>{statusLabel[dataset.status]}</Badge></td>
                  <td>{camadaLabel[dataset.camada]}</td>
                  <td>{dataset.atualizacao}</td>
                  <td>{dataset.retencao}</td>
                  <td>{dataset.descricao}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
