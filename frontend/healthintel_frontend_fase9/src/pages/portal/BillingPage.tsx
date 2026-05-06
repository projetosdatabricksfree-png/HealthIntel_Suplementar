import { useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { plans } from '../../data/plans';
import { PlanCard } from '../../components/PlanCard';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, addUpgradeRequest, getUpgradeRequests } from '../../services/localPortalStore';
import { useAuth } from '../../hooks/useAuth';

export function BillingPage() {
  const { user } = useAuth();
  const { success, info, error } = useNotification();
  const [showModal, setShowModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('Core API');
  const [justificativa, setJustificativa] = useState('');
  const [requests, setRequests] = useState(getUpgradeRequests());

  function submitUpgrade() {
    if (!selectedPlan.trim() || !justificativa.trim()) {
      error('Informe plano e justificativa para registrar a solicitação.');
      return;
    }
    const request = addUpgradeRequest({ plano: selectedPlan, justificativa });
    setRequests((current) => [request, ...current]);
    addAuditEvent({
      tipo: 'upgrade_solicitado',
      usuario: user?.email || 'portal_local',
      detalhe: `Solicitacao local registrada para o plano ${selectedPlan}.`,
      status: 'sucesso'
    });
    setShowModal(false);
    setJustificativa('');
    success('Solicitação registrada localmente. Nenhum upgrade foi aplicado automaticamente.');
  }

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Billing</p>
          <h1>Plano e faturamento</h1>
          <p>Base visual para cobrança por plano, limite e consumo.</p>
        </div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Plano" value="Core API" detail="ativo" />
        <MetricCard label="Valor base" value="R$ 4.900" detail="mensal" />
        <MetricCard label="Consumo" value="6.430" detail="requisições" />
        <MetricCard label="Próximo ciclo" value="30/05" detail="demonstração" />
      </div>

      <Card>
        <div className="button-row">
          <Button onClick={() => setShowModal(true)}>Solicitar upgrade</Button>
          <Button variant="secondary" onClick={() => info('Plano atual: Core API. Limites contratuais controlados por API key.')}>Ver plano atual</Button>
          <Button variant="secondary" onClick={() => info('Limites locais: rate limit por plano, paginação obrigatória e sem exportação integral.')}>Ver limites</Button>
          <Button variant="ghost" onClick={() => setShowModal(true)}>Registrar solicitação</Button>
        </div>
      </Card>

      {showModal && (
        <Card className="modal-card">
          <CardHeader title="Solicitar upgrade" description="Fluxo local de homologação. Backend real de billing ainda é pendência de produção." />
          <div className="form-grid single">
            <label>
              Plano desejado
              <select value={selectedPlan} onChange={(event) => setSelectedPlan(event.target.value)}>
                {plans.map((plan) => <option key={plan.nome}>{plan.nome}</option>)}
              </select>
            </label>
            <label>
              Justificativa
              <textarea rows={4} value={justificativa} onChange={(event) => setJustificativa(event.target.value)} />
            </label>
            <div className="button-row">
              <Button onClick={submitUpgrade}>Confirmar solicitação</Button>
              <Button variant="secondary" onClick={() => setShowModal(false)}>Cancelar</Button>
            </div>
          </div>
        </Card>
      )}

      {requests.length > 0 && (
        <Card>
          <CardHeader title="Solicitações registradas" description="Registros locais para homologação." />
          <div className="table-wrap">
            <table>
              <thead><tr><th>Data</th><th>Plano</th><th>Status</th><th>Justificativa</th></tr></thead>
              <tbody>
                {requests.map((request) => (
                  <tr key={request.id}>
                    <td>{new Date(request.timestamp).toLocaleString('pt-BR')}</td>
                    <td>{request.plano}</td>
                    <td>{request.status}</td>
                    <td>{request.justificativa}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Card>
        <CardHeader title="Planos disponíveis" description="O upgrade deve acionar `/admin/billing/upgrade` em fluxo administrativo." />
        <div className="plans-grid plans-grid-five">
          {plans.map((plan) => <PlanCard key={plan.nome} plan={plan} />)}
        </div>
      </Card>
    </div>
  );
}
