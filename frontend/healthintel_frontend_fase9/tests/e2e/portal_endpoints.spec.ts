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
        id: 'u1', email: 'tester@empresa.com', nome: 'Tester', avatar_url: null,
        status: 'ativo', email_verificado: true, ultimo_login_em: null,
        criado_em: new Date().toISOString(),
        tenants: [{ cliente_id: 'c1', nome: 'Empresa Tester', role: 'owner', status: 'ativo', plano_nome: 'free' }],
        perfil_b2b: null,
      }),
    });
  });
}

test.describe('Portal — catálogo de endpoints /app/endpoints', () => {
  test('renderiza catálogo, filtros e grid de endpoints', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/endpoints');

    await expect(page.getByRole('heading', { name: 'Catálogo da API' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByPlaceholder('Buscar endpoint...')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Core', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Premium', exact: true }).first()).toBeVisible();

    const cards = page.locator('.endpoint-grid > *');
    await expect(cards.first()).toBeVisible({ timeout: 6000 });
  });

  test('busca inexistente esvazia o grid', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/endpoints');
    await expect(page.locator('.endpoint-grid > *').first()).toBeVisible({ timeout: 6000 });

    await page.getByPlaceholder('Buscar endpoint...').fill('zzz-nao-existe-zzz');
    await expect(page.locator('.endpoint-grid > *')).toHaveCount(0);
  });
});
