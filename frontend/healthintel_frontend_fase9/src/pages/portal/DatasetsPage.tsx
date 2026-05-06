import { datasets } from '../../data/datasets';
import { Badge } from '../../components/Badge';
import { Card, CardHeader } from '../../components/Card';

const tone = {
  ativo: 'green',
  em_validacao: 'yellow',
  bloqueado_mvp: 'red'
} as const;

export function DatasetsPage() {
  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Datasets</p>
          <h1>Escopo de dados do produto</h1>
          <p>Controle visual do que está publicado, em validação ou bloqueado no MVP.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Catálogo Core ANS" description="Camadas de dados e retenção inicial." />
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
                  <td><Badge tone={tone[dataset.status]}>{dataset.status}</Badge></td>
                  <td>{dataset.camada}</td>
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
