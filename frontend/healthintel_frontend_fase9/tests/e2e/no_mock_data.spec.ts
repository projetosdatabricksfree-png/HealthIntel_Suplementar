import { test, expect } from '@playwright/test';

test.describe('Anti-mock — dashboards não exibem dados fake', () => {
  test('UsagePage sem API key mostra empty state honesto e direciona ao Explorer', async ({ page }) => {
    // Mock sessão autenticada (sem API key configurada)
    await page.addInitScript(() => {
      localStorage.setItem('healthintel.auth.access_token', 'fake-access');
      localStorage.setItem('healthintel.auth.refresh_token', 'fake-refresh');
    });
    await page.route('**/v1/me/perfil', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'u1',
          email: 'teste@empresa.com',
          nome: 'Tester',
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

    await page.goto('/app/uso');
    // Sem API key salva no storage → empty state honesto
    await expect(page.locator('.empty-state-inline')).toContainText('Configure uma API key', { timeout: 6000 });
  });

  test('Mock `data/mock.ts` não é o que o dashboard renderiza em produção', async ({ page }) => {
    // Não há dados mockados específicos como "Operadora Demonstração Saúde S.A." na UI
    await page.goto('/');
    const html = await page.content();
    // Strings clássicas do mock.ts não devem aparecer na home pública
    expect(html).not.toContain('Operadora Demonstração Saúde S.A.');
  });
});
