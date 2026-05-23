import { test, expect, type Page } from '@playwright/test';

async function setupBilling(
  page: Page,
  plano: 'free' | 'pro',
  resumo: unknown,
  faturas: unknown[],
) {
  await page.addInitScript(() => {
    localStorage.setItem('healthintel.auth.access_token', 'mock-access');
    localStorage.setItem('healthintel.auth.refresh_token', 'mock-refresh');
  });
  await page.route('**/v1/me/perfil', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'u1', email: 'tester@empresa.com', nome: 'Tester', avatar_url: null,
        status: 'ativo', email_verificado: true, ultimo_login_em: null,
        criado_em: new Date().toISOString(),
        tenants: [{ cliente_id: 'c1', nome: 'Empresa Tester', role: 'owner', status: 'ativo', plano_nome: plano }],
        perfil_b2b: null,
      }),
    });
  });
  await page.route('**/v1/portal/billing/resumo', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ dados: resumo }) });
  });
  await page.route('**/v1/portal/billing/faturas', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ dados: faturas }) });
  });
}

test.describe('Portal — billing /app/billing', () => {
  test('plano free mostra alerta gratuito e tabela de faturas vazia', async ({ page }) => {
    await setupBilling(page, 'free', {
      plano: { nome: 'Free', limite_api_keys: 1 },
      uso_hoje: 12,
      chaves_ativas: 1,
      assinatura: null,
    }, []);
    await page.goto('/app/billing');

    await expect(page.getByRole('heading', { name: 'Plano e faturamento' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByText('Você está no plano gratuito')).toBeVisible();
    await expect(page.getByText('Plano Free não possui faturas.')).toBeVisible();
  });

  test('plano pro mostra faturas pagas na tabela', async ({ page }) => {
    await setupBilling(page, 'pro', {
      plano: { nome: 'Pro', limite_api_keys: 5 },
      uso_hoje: 40,
      chaves_ativas: 2,
      assinatura: { stripe_subscription_id: 'sub_1', status: 'active', current_period_end: '2026-06-15' },
    }, [
      {
        id: 'f1', numero: 'INV-2026-001', data: 1746057600, descricao: 'Plano Pro mensal',
        valor_centavos: 9900, moeda: 'brl', status: 'paid', pdf_url: 'https://stripe.test/inv.pdf',
      },
    ]);
    await page.goto('/app/billing');

    await expect(page.getByRole('heading', { name: 'Plano e faturamento' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByRole('heading', { name: 'Histórico de faturas' })).toBeVisible();
    await expect(page.getByText('INV-2026-001')).toBeVisible({ timeout: 6000 });
    await expect(page.getByText('Plano Pro mensal')).toBeVisible();
  });
});
