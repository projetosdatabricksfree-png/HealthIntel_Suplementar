import { Button } from '../../components/Button';
import { Card, CardHeader } from '../../components/Card';

export function TeamPage() {
  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Equipe</p>
          <h1>Usuários e permissões</h1>
          <p>Tela preparada para multiusuário por cliente.</p>
        </div>
      </div>

      <Card>
        <CardHeader title="Membros" description="Em produção, cada usuário deve ter papel e trilha de auditoria." />
        <div className="table-wrap">
          <table>
            <thead><tr><th>Nome</th><th>E-mail</th><th>Papel</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td>Diego Costa</td><td>cliente@healthintel.local</td><td>Owner</td><td>Ativo</td></tr>
              <tr><td>Analista BI</td><td>bi@empresa.com.br</td><td>Leitor</td><td>Convite pendente</td></tr>
            </tbody>
          </table>
        </div>
        <div className="button-row">
          <Button>Convidar membro</Button>
          <Button variant="secondary">Configurar papéis</Button>
        </div>
      </Card>
    </div>
  );
}
