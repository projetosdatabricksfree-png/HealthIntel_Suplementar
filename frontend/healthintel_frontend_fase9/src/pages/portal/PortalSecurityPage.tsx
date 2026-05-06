import { useState } from 'react';
import { Card, CardHeader } from '../../components/Card';
import { Button } from '../../components/Button';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, getAuditEvents, getSecuritySettings, saveSecuritySettings } from '../../services/localPortalStore';
import { useAuth } from '../../hooks/useAuth';

function validList(value: string): boolean {
  if (!value.trim()) return true;
  return value.split(',').every((item) => item.trim().length >= 3 && !item.includes(' '));
}

export function PortalSecurityPage() {
  const { user } = useAuth();
  const { success, error, info } = useNotification();
  const initial = getSecuritySettings();
  const [domains, setDomains] = useState(initial.domains);
  const [ips, setIps] = useState(initial.ips);
  const [twoFactorStatus, setTwoFactorStatus] = useState(initial.twoFactorStatus);
  const [audit, setAudit] = useState(getAuditEvents());

  function refreshAudit() {
    setAudit(getAuditEvents());
  }

  function enableTwoFactor() {
    setTwoFactorStatus('pendente');
    saveSecuritySettings({ domains, ips, twoFactorStatus: 'pendente' });
    addAuditEvent({
      tipo: '2fa_pendente',
      usuario: user?.email || 'portal_local',
      detalhe: '2FA marcado como pendente localmente. Producao exige backend real.',
      status: 'aviso'
    });
    refreshAudit();
    info('2FA marcado como pendente. Ativação real depende de backend de autenticação.');
  }

  function saveAllowlist() {
    if (!validList(domains) || !validList(ips)) {
      error('Use domínios/IPs separados por vírgula, sem espaços internos.');
      return;
    }
    saveSecuritySettings({ domains, ips, twoFactorStatus });
    addAuditEvent({
      tipo: 'allowlist_salva',
      usuario: user?.email || 'portal_local',
      detalhe: `Dominios: ${domains || 'nenhum'}; IPs: ${ips || 'nenhum'}.`,
      status: 'sucesso'
    });
    refreshAudit();
    success('Allowlist salva localmente.');
  }

  function clearAllowlist() {
    setDomains('');
    setIps('');
    saveSecuritySettings({ domains: '', ips: '', twoFactorStatus });
    addAuditEvent({
      tipo: 'allowlist_limpa',
      usuario: user?.email || 'portal_local',
      detalhe: 'Allowlist local removida.',
      status: 'sucesso'
    });
    refreshAudit();
    success('Allowlist local removida.');
  }

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
          <Button onClick={enableTwoFactor}>Ativar 2FA</Button>
          <small>Status local: {twoFactorStatus}</small>
        </Card>

        <Card>
          <CardHeader title="Proteção da API key" description="Whitelists reduzem vazamento e uso indevido." />
          <div className="form-grid single">
            <label>Domínios permitidos<input value={domains} onChange={(event) => setDomains(event.target.value)} placeholder="app.empresa.com.br,bi.empresa.com.br" /></label>
            <label>IPs permitidos<input value={ips} onChange={(event) => setIps(event.target.value)} placeholder="200.100.10.20/32" /></label>
            <div className="button-row">
              <Button onClick={saveAllowlist}>Salvar allowlist</Button>
              <Button variant="secondary" onClick={clearAllowlist}>Limpar allowlist</Button>
              <Button variant="ghost" onClick={refreshAudit}>Ver auditoria</Button>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <CardHeader title="Auditoria recente" description="Eventos locais registrados pelo portal." />
        <div className="table-wrap">
          <table>
            <thead><tr><th>Data</th><th>Evento</th><th>Usuário</th><th>Detalhe</th><th>Status</th></tr></thead>
            <tbody>
              {audit.length === 0 && <tr><td colSpan={5}>Sem eventos locais registrados.</td></tr>}
              {audit.map((event) => (
                <tr key={event.id}>
                  <td>{new Date(event.timestamp).toLocaleString('pt-BR')}</td>
                  <td>{event.tipo}</td>
                  <td>{event.usuario}</td>
                  <td>{event.detalhe}</td>
                  <td>{event.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
