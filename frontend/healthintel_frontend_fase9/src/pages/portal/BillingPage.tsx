import { useCallback, useEffect, useState } from 'react';
import { Button } from '../../components/Button';
import { Card, CardHeader, MetricCard } from '../../components/Card';
import { plans } from '../../data/plans';
import { PlanCard } from '../../components/PlanCard';
import { useNotification } from '../../components/NotificationProvider';
import { useAuth } from '../../hooks/useAuth';
import { getCurrentPlan, hasPlanAtLeast } from '../../data/planRules';
import { buildUrl } from '../../services/apiClient';
import { getAccessToken } from '../../services/storage';
import { criarSessaoCustomerPortal } from '../../services/checkoutApi';
import type { BillingResumo, Fatura } from '../../types/domain';

async function fetchJson<T>(path: string): Promise<T> {
  const at = getAccessToken();
  const res = await fetch(buildUrl(path), {
    headers: { ...(at ? { Authorization: `Bearer ${at}` } : {}) },
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = (json as { detail?: { mensagem?: string } }).detail?.mensagem || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return (json as { dados: T }).dados;
}

export function BillingPage() {
  const { user } = useAuth();
  const { success, error } = useNotification();
  const [resumo, setResumo] = useState<BillingResumo | null>(null);
  const [faturas, setFaturas] = useState<Fatura[]>([]);
  const [loadingPortal, setLoadingPortal] = useState(false);
  const currentPlan = getCurrentPlan(user?.tenant_ativo?.plano_nome);
  const isFree = currentPlan.slug === 'free';
  const hasSubscription = !!(resumo?.assinatura?.stripe_subscription_id);

  const load = useCallback(async () => {
    try {
      const [r, f] = await Promise.all([
        fetchJson<BillingResumo>('/v1/portal/billing/resumo').catch(() => null),
        fetchJson<Fatura[]>('/v1/portal/billing/faturas').catch(() => []),
      ]);
      if (r) setResumo(r);
      setFaturas(f as Fatura[]);
    } catch {
      // non-fatal: show stale data
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function openCustomerPortal() {
    setLoadingPortal(true);
    try {
      const url = await criarSessaoCustomerPortal();
      window.location.href = url;
    } catch (err) {
      error(err instanceof Error ? err.message : 'Erro ao abrir portal de billing.');
    } finally {
      setLoadingPortal(false);
    }
  }

  const proximaCobranca = resumo?.assinatura?.current_period_end
    ? new Date(resumo.assinatura.current_period_end).toLocaleDateString('pt-BR')
    : hasSubscription ? 'Via Stripe' : '—';

  return (
    <div className="portal-page">
      <div className="portal-title">
        <div>
          <p className="eyebrow">Billing</p>
          <h1>Plano e faturamento</h1>
          <p>Gerencie sua assinatura, faturas e upgrade de plano.</p>
        </div>
      </div>

      {isFree && (
        <Card>
          <CardHeader title="Você está no plano gratuito" description="Free é um SKU real para avaliação técnica com 100 requisições por dia." />
          <div className="button-row">
            <Button onClick={() => document.getElementById('planos-disponiveis')?.scrollIntoView({ behavior: 'smooth' })}>
              Fazer upgrade
            </Button>
          </div>
        </Card>
      )}

      {isFree && resumo && resumo.uso_hoje >= 80 && (
        <Card>
          <CardHeader
            title={resumo.uso_hoje >= 100 ? 'Limite diário atingido' : 'Próximo do limite diário'}
            description={
              resumo.uso_hoje >= 100
                ? '100/100 requisições usadas hoje. Novas chamadas retornam HTTP 429 até amanhã. Faça upgrade para continuar sem interrupção.'
                : `${resumo.uso_hoje}/100 requisições usadas hoje. Faça upgrade para não ser bloqueado.`
            }
          />
          <div className="button-row">
            <Button onClick={() => document.getElementById('planos-disponiveis')?.scrollIntoView({ behavior: 'smooth' })}>
              Ver planos
            </Button>
          </div>
        </Card>
      )}

      <div className="metrics-grid">
        <MetricCard label="Plano atual" value={resumo?.plano.nome || currentPlan.nome} detail={currentPlan.preco} />
        <MetricCard label="Requisições hoje" value={resumo ? String(resumo.uso_hoje) : '—'} detail={isFree ? 'de 100 req/dia (plano free)' : 'chamadas à API'} />
        <MetricCard label="Chaves ativas" value={resumo ? String(resumo.chaves_ativas) : '—'} detail={`limite: ${resumo?.plano.limite_api_keys === -1 ? 'ilimitado' : (resumo?.plano.limite_api_keys ?? currentPlan.keyLimit)}`} />
        <MetricCard label="Próxima cobrança" value={proximaCobranca} detail={resumo?.assinatura?.cancel_at_period_end ? 'cancelamento no fim do período' : hasSubscription ? 'via Customer Portal' : 'sem assinatura ativa'} />
      </div>

      <Card>
        <CardHeader
          title="Assinatura"
          description={
            hasSubscription
              ? `Status: ${resumo?.assinatura?.status || 'ativo'}. Gerencie cartão, Pix, invoices e cancelamento no Stripe.`
              : isFree
              ? 'Plano Free sem assinatura. Faça upgrade para acesso a dados completos.'
              : 'Assinatura não encontrada. Contate o suporte se sua assinatura já foi ativada.'
          }
        />
        <div className="button-row">
          <Button onClick={() => void openCustomerPortal()} disabled={!hasSubscription || loadingPortal}>
            {loadingPortal ? 'Abrindo…' : 'Gerenciar assinatura'}
          </Button>
          <Button variant="secondary" onClick={() => void load()}>Atualizar</Button>
        </div>
      </Card>

      <Card>
        <CardHeader title="Histórico de faturas" description="Faturas pagas via Stripe." />
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Número</th><th>Data</th><th>Descrição</th><th>Valor</th><th>Status</th><th>PDF</th></tr>
            </thead>
            <tbody>
              {faturas.length === 0 ? (
                <tr><td colSpan={6}>{isFree ? 'Plano Free não possui faturas.' : 'Nenhuma fatura encontrada.'}</td></tr>
              ) : faturas.map((f) => (
                <tr key={f.id}>
                  <td>{f.numero || '—'}</td>
                  <td>{new Date(f.data * 1000).toLocaleDateString('pt-BR')}</td>
                  <td>{f.descricao || '—'}</td>
                  <td>{(f.valor_centavos / 100).toLocaleString('pt-BR', { style: 'currency', currency: f.moeda.toUpperCase() })}</td>
                  <td>{f.status}</td>
                  <td>{f.pdf_url ? <a href={f.pdf_url} target="_blank" rel="noreferrer">PDF</a> : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <div id="planos-disponiveis">
        <Card>
          <CardHeader title="Planos disponíveis" description="Mesmos planos da landing: FREE, STARTER, PRO, MAX e ENTERPRISE." />
          <div className="plans-grid plans-grid-five">
            {plans.map((plan) => (
              <PlanCard
                key={plan.slug}
                plan={plan}
                isCurrent={plan.slug === currentPlan.slug}
              />
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
