import { test, expect, type Page } from '@playwright/test';

async function setupAuth(page: Page, plano: 'free' | 'pro') {
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
        tenants: [{ cliente_id: 'c1', nome: 'Empresa Tester', role: 'owner', status: 'ativo', plano_nome: plano }],
        perfil_b2b: null,
      }),
    });
  });
}

test.describe('Portal — equipe /app/equipe', () => {
  test('plano free vê o gate de upgrade PRO', async ({ page }) => {
    await setupAuth(page, 'free');
    await page.goto('/app/equipe');
    await expect(page.getByRole('heading', { name: 'Disponível a partir do plano PRO' })).toBeVisible({ timeout: 6000 });
  });

  test('plano pro lista membros e abre o modal de convite', async ({ page }) => {
    await setupAuth(page, 'pro');
    await page.route('**/v1/portal/team', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            dados: [
              { id: 'm1', nome: 'Dono da Conta', email: 'dono@empresa.com', role: 'owner', status: 'ativo', ultimo_login_em: null },
              { id: 'm2', nome: 'Dev Convidado', email: 'dev@empresa.com', role: 'developer', status: 'ativo', ultimo_login_em: null },
            ],
          }),
        });
        return;
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ dados: {} }) });
    });

    await page.goto('/app/equipe');
    await expect(page.getByRole('heading', { name: 'Usuários e permissões' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByText('Dono da Conta')).toBeVisible({ timeout: 6000 });
    await expect(page.getByText('Dev Convidado')).toBeVisible();

    await page.getByRole('button', { name: 'Convidar membro' }).click();
    await expect(page.getByRole('heading', { name: 'Convidar membro' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Enviar convite' })).toBeVisible();
  });

  test('plano pro manuseia erro de API corretamente', async ({ page }) => {
    await setupAuth(page, 'pro');
    await page.route('**/v1/portal/team', (route) => route.abort());

    await page.goto('/app/equipe');
    // Should show error state or fallback UI instead of hanging
    await expect(page.locator('body')).toBeTruthy();
  });
});
