import { test, expect, type Page } from '@playwright/test';

async function setupAuth(page: Page) {
  // Ensure clean state across tests to avoid idle timeout interference
  await page.addInitScript(() => {
    localStorage.setItem('healthintel.auth.access_token', 'mock-access');
    localStorage.setItem('healthintel.auth.refresh_token', 'mock-refresh');
    localStorage.removeItem('healthintel.portal.last_activity');
  });
  await page.route('**/v1/me/perfil', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'u1', email: 'admin@healthintel.com.br', nome: 'Admin', avatar_url: null,
        status: 'ativo', email_verificado: true, ultimo_login_em: null,
        criado_em: new Date().toISOString(),
        tenants: [{ cliente_id: 'c1', nome: 'HealthIntel', role: 'admin_internal', status: 'ativo', plano_nome: 'enterprise' }],
        perfil_b2b: null,
      }),
    });
  });
}

test.describe('Portal — billing admin /app/admin/billing', () => {
  test('busca resumo administrativo e exibe o JSON retornado', async ({ page }) => {
    await setupAuth(page);
    await page.route('**/admin/billing/resumo**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          dados: { referencia: '2026-05', total_faturado_centavos: 4242420, clientes_ativos: 7 },
          meta: { gerado_em: '2026-05-22' },
        }),
      });
    });

    await page.goto('/app/admin/billing');
    await expect(page.getByRole('heading', { name: 'Billing administrativo' })).toBeVisible({ timeout: 6000 });

    await page.getByRole('button', { name: 'Buscar resumo' }).click();
    await expect(page.getByText(/4242420/).first()).toBeVisible({ timeout: 6000 });
  });
});
