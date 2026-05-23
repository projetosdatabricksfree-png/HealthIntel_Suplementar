import { test, expect, type Page } from '@playwright/test';

async function setupAuth(page: Page) {
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
        tenants: [{ cliente_id: 'c1', nome: 'Empresa Tester', role: 'owner', status: 'ativo', plano_nome: 'pro' }],
        perfil_b2b: null,
      }),
    });
  });
  await page.route('**/v1/auth/logout', (route) => route.fulfill({ status: 204, body: '' }));
  await page.route('**/v1/auth/logout-tudo', (route) => route.fulfill({ status: 204, body: '' }));
}

test.describe('Portal — idle logout (5 min)', () => {
  test('faz logout automático após 5 minutos de inatividade', async ({ page }) => {
    await page.clock.install();
    await setupAuth(page);
    await page.goto('/app');
    await expect(page.getByRole('heading', { name: /Dashboard|HealthIntel/i }).first()).toBeVisible({ timeout: 6000 });

    await page.clock.fastForward('05:00');

    await page.waitForURL(/\/login/, { timeout: 8000 });
    const access = await page.evaluate(() => localStorage.getItem('healthintel.auth.access_token'));
    expect(access).toBeNull();
  });

  test('mostra modal aos 4 minutos e dismiss reseta o timer', async ({ page }) => {
    await page.clock.install();
    await setupAuth(page);
    await page.goto('/app');
    await expect(page.locator('.portal-shell')).toBeVisible({ timeout: 6000 });

    await page.clock.fastForward('04:00');

    const stayButton = page.getByRole('button', { name: 'Continuar conectado' });
    await expect(stayButton).toBeVisible({ timeout: 4000 });
    await stayButton.click();
    await expect(stayButton).not.toBeVisible();

    await page.clock.fastForward('04:00');
    await expect(page.getByRole('button', { name: 'Continuar conectado' })).toBeVisible({ timeout: 4000 });
    expect(page.url()).toContain('/app');
  });

  test('atividade do mouse reseta o contador de inatividade', async ({ page }) => {
    await page.clock.install();
    await setupAuth(page);
    await page.goto('/app');
    await expect(page.locator('.portal-shell')).toBeVisible({ timeout: 6000 });

    await page.clock.fastForward('03:00');
    await page.mouse.move(200, 200);
    await page.mouse.move(220, 220);
    await page.clock.fastForward('03:00');

    expect(page.url()).toContain('/app');
    await expect(page.getByRole('button', { name: 'Continuar conectado' })).not.toBeVisible();
  });
});
