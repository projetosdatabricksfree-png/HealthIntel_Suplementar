import { test, expect, type Page } from '@playwright/test';

async function setupAuth(page: Page, plano: 'free' | 'starter' | 'pro') {
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
}

test.describe('Portal — segurança /app/seguranca', () => {
  test('plano free vê o gate de upgrade', async ({ page }) => {
    await setupAuth(page, 'free');
    await page.goto('/app/seguranca');
    await expect(page.getByRole('heading', { name: 'Disponível a partir do plano Starter' })).toBeVisible({ timeout: 6000 });
  });

  test('plano pro acessa cards de segurança e auditoria', async ({ page }) => {
    await setupAuth(page, 'pro');
    await page.goto('/app/seguranca');

    await expect(page.getByRole('heading', { name: 'Configurações de segurança' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByRole('heading', { name: 'Acesso', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Proteção da API key' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Auditoria recente' })).toBeVisible();
    await expect(page.getByText('Sem eventos locais registrados.')).toBeVisible();
  });
});
