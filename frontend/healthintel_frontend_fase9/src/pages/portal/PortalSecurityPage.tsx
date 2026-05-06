import { Card, CardHeader } from '../../components/Card';
import { Button } from '../../components/Button';

export function PortalSecurityPage() {
  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Segurança</p>
          <h1>Configurações de segurança</h1>
          <p>Base visual para 2FA, domínios permitidos, IP allowlist e auditoria.</p>
        </div>
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Acesso" description="Proteções recomendadas para produção." />
          <ul className="check-list">
            <li>2FA para usuários do portal.</li>
            <li>Sessão HttpOnly/Secure.</li>
            <li>Política de senha.</li>
            <li>Bloqueio por tentativas.</li>
          </ul>
          <Button>Ativar 2FA</Button>
        </Card>

        <Card>
          <CardHeader title="Proteção da API key" description="Whitelists reduzem vazamento e uso indevido." />
          <div className="form-grid single">
            <label>Domínios permitidos<input placeholder="app.empresa.com.br, bi.empresa.com.br" /></label>
            <label>IPs permitidos<input placeholder="200.100.10.20/32" /></label>
            <Button>Salvar allowlist</Button>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Auditoria recente" description="Eventos demonstrativos." />
        <div className="table-wrap">
          <table>
            <thead><tr><th>Data</th><th>Evento</th><th>Origem</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td>05/05/2026 09:12</td><td>Login no portal</td><td>São Paulo/SP</td><td>OK</td></tr>
              <tr><td>05/05/2026 09:15</td><td>Teste endpoint rankings</td><td>API key demo</td><td>OK</td></tr>
              <tr><td>05/05/2026 09:18</td><td>Tentativa de endpoint bloqueado</td><td>API key demo</td><td>Bloqueado</td></tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
