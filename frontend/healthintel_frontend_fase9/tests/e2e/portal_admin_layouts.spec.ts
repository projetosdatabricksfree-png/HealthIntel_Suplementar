import { test, expect, type Page } from '@playwright/test';

async function setupAuth(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('healthintel.auth.access_token', 'mock-access');
    localStorage.setItem('healthintel.auth.refresh_token', 'mock-refresh');
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

test.describe('Portal — layouts admin /app/admin/layouts', () => {
  test('lista layouts e exibe o JSON retornado', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/admin/layouts');
    await expect(page.getByRole('heading', { name: 'Layouts e compatibilidade' })).toBeVisible({ timeout: 6000 });

    // Registrado após o goto para não interceptar a navegação do SPA (/app/admin/layouts).
    await page.route('**/admin/layouts**', async (route) => {
      if (route.request().resourceType() === 'document') {
        await route.fallback();
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          dados: [
            { nome: 'layout_sib_e2e', versao: '3', aliases: 12 },
            { nome: 'layout_cadop_e2e', versao: '2', aliases: 8 },
          ],
          meta: { total: 2 },
        }),
      });
    });

    await page.getByRole('button', { name: 'Listar layouts' }).click();
    await expect(page.getByText(/layout_sib_e2e/).first()).toBeVisible({ timeout: 6000 });
  });
});
