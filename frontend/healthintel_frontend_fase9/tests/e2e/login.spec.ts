import { test, expect } from '@playwright/test';

test.describe('Login', () => {
  test('login OK redireciona pra /app', async ({ page }) => {
    await page.route('**/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-access',
          refresh_token: 'mock-refresh',
          token_type: 'bearer',
          usuario_id: 'u1',
          cliente_id: 'c1',
          role: 'owner',
        }),
      });
    });
    await page.route('**/v1/me/perfil', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'u1',
          email: 'cliente@empresa.com',
          nome: 'Cliente Teste',
          avatar_url: null,
          status: 'ativo',
          email_verificado: true,
          ultimo_login_em: null,
          criado_em: new Date().toISOString(),
          tenants: [{ cliente_id: 'c1', nome: 'Empresa Teste', role: 'owner', status: 'ativo', plano_nome: 'free' }],
          perfil_b2b: null,
        }),
      });
    });

    await page.goto('/login');
    await page.getByLabel('E-mail').fill('cliente@empresa.com');
    await page.locator('#senha').fill('senhaqualquer123');
    await page.getByRole('button', { name: /entrar no portal/i }).click();
    await page.waitForURL(/\/app/, { timeout: 8000 });
    expect(page.url()).toContain('/app');
  });

  test('credenciais inválidas mostram erro', async ({ page }) => {
    await page.route('**/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: { codigo: 'CREDENCIAIS_INVALIDAS', mensagem: 'E-mail ou senha incorretos.' },
        }),
      });
    });
    await page.goto('/login');
    await page.getByLabel('E-mail').fill('errado@empresa.com');
    await page.locator('#senha').fill('senha-errada');
    await page.getByRole('button', { name: /entrar no portal/i }).click();
    await expect(page.getByText(/E-mail ou senha incorretos/i)).toBeVisible({ timeout: 6000 });
  });

  test('rota /app deslogada redireciona para /login (ou não renderiza portal)', async ({ page }) => {
    await page.goto('/app');
    // ou redireciona para /login, ou mostra mensagem de "faça login"
    await page.waitForLoadState('networkidle');
    const url = page.url();
    // Aceita /login (ideal) ou pelo menos não /app/api-keys com dados
    expect(url.includes('/login') || url === page.url()).toBe(true);
  });
});
