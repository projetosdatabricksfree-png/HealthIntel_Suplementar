import { test, expect } from '@playwright/test';

async function setupAuthAndRoutes(page: import('@playwright/test').Page, plano: 'free' | 'pro' = 'free') {
  await page.addInitScript(() => { 
    localStorage.setItem('healthintel.auth.access_token', 'mock-access');
    localStorage.setItem('healthintel.auth.refresh_token', 'mock-refresh');
  });
  await page.route('**/v1/me/perfil', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'u1',
        email: 'tester@empresa.com',
        nome: 'Tester',
        avatar_url: null,
        status: 'ativo',
        email_verificado: true,
        ultimo_login_em: null,
        criado_em: new Date().toISOString(),
        tenants: [{ cliente_id: 'c1', nome: 'Empresa Tester', role: 'owner', status: 'ativo', plano_nome: plano }],
        perfil_b2b: null,
      }),
    });
  });
}

test.describe('Portal — gerenciamento de API keys', () => {
  test('listagem inicial vazia + criação de nova chave', async ({ page }) => {
    await setupAuthAndRoutes(page);
    let listaChaves: unknown[] = [];

    await page.route('**/v1/portal/api-keys', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ dados: listaChaves }),
        });
        return;
      }
      // POST: criar chave
      const body = route.request().postDataJSON() as { nome: string; ambiente: string };
      const novaChave = {
        id: 'k1',
        nome: body.nome,
        prefixo: body.ambiente === 'sandbox' ? 'hi_test_abc' : 'hi_live_xyz',
        ambiente: body.ambiente,
        escopos: [],
        status: 'ativo',
        criado_em: new Date().toISOString(),
        ultimo_uso_em: null,
        revogada_em: null,
        expira_em: null,
      };
      listaChaves = [novaChave];
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          dados: { ...novaChave, chave_plain: 'hi_test_abc1234567890qwertyuiopASDFGHJKL' },
        }),
      });
    });

    await page.goto('/app/api-keys');
    // Encontra o botão Criar
    const criarBtn = page.getByRole('button', { name: /criar.+(api )?key|nova chave/i }).first();
    await criarBtn.click({ trial: false }).catch(() => undefined);

    // Form aparece — preenche
    const nomeInput = page.getByLabel(/nome/i).first();
    if (await nomeInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      await nomeInput.fill('Chave de teste');
    }
    // Submit
    await page.getByRole('button', { name: /^criar$|criar chave|gerar/i }).first().click().catch(() => undefined);

    // Aguarda chave aparecer na tela
    await expect(page.getByText(/hi_test_/i).first()).toBeVisible({ timeout: 6000 });
  });
});
