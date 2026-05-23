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
        tenants: [{ cliente_id: 'c1', nome: 'Empresa Tester', role: 'owner', status: 'ativo', plano_nome: 'pro' }],
        perfil_b2b: null,
      }),
    });
  });
}

test.describe('Portal — perfil /app/perfil', () => {
  test('renderiza dados da conta e salva o nome', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/perfil');

    await expect(page.getByRole('heading', { name: 'Dados da conta' })).toBeVisible({ timeout: 6000 });
    await expect(page.getByLabel('Nome')).toHaveValue('Tester');
    await expect(page.getByLabel('E-mail')).toHaveValue('tester@empresa.com');

    await page.getByLabel('Nome').fill('Tester Atualizado');
    await page.getByRole('button', { name: 'Salvar nome' }).click();
    await expect(page.getByText('Perfil atualizado.')).toBeVisible({ timeout: 6000 });
  });

  test('nome vazio bloqueia o salvamento', async ({ page }) => {
    await setupAuth(page);
    await page.goto('/app/perfil');
    await expect(page.getByLabel('Nome')).toBeVisible({ timeout: 6000 });

    await page.getByLabel('Nome').fill('');
    await page.getByRole('button', { name: 'Salvar nome' }).click();
    await expect(page.getByText('Informe seu nome.')).toBeVisible({ timeout: 6000 });
  });
});
