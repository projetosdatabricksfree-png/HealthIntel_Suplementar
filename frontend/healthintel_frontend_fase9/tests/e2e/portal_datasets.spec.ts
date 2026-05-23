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

test.describe('Portal — checklist de datasets /app/datasets', () => {
  test('renderiza métricas, tabela e filtros', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/datasets');

    await expect(page.getByRole('heading', { name: 'Checklist de dados entregues' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByText('Tabelas Core')).toBeVisible();
    await expect(page.getByText('Prontas', { exact: true })).toBeVisible();
    await expect(page.getByText('Parciais', { exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Catálogo HealthIntel Core ANS' })).toBeVisible();
    await expect(page.getByPlaceholder('Buscar tabela, domínio, schema ou extração...')).toBeVisible();
  });

  test('filtro de status mantém a tabela renderizada', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/datasets');
    await expect(page.getByRole('heading', { name: 'Catálogo HealthIntel Core ANS' })).toBeVisible({ timeout: 6000 });

    await page.getByRole('button', { name: 'Pronto para consumo', exact: true }).click();
    await expect(page.locator('table').first()).toBeVisible();
    await expect(page.getByText(/itens filtrados/i)).toBeVisible();
  });
});
