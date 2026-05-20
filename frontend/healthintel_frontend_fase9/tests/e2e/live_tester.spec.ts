import { test, expect } from '@playwright/test';

async function setupSession(page: import('@playwright/test').Page) {
  await page.addInitScript(() => { 
    localStorage.setItem('healthintel.auth.access_token', 'mock-access');
    localStorage.setItem('healthintel.auth.refresh_token', 'mock-refresh');
    localStorage.setItem('healthintel.portal.api_key', 'hi_test_1234567890abcdef');
  });
  await page.route('**/v1/me/perfil', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'u1', email: 't@e.com', nome: 'T', avatar_url: null, status: 'ativo',
        email_verificado: true, ultimo_login_em: null, criado_em: new Date().toISOString(),
        tenants: [{ cliente_id: 'c1', nome: 'E', role: 'owner', status: 'ativo', plano_nome: 'free' }],
        perfil_b2b: null,
      }),
    });
  });
}

test.describe('Explorer — live tester', () => {
  test('executa request e exibe JSON 200', async ({ page }) => {
    await setupSession(page);
    await page.route('**/v1/operadoras**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          dados: [{ registro_ans: '000337', razao_social: 'Operadora Teste S.A.' }],
          meta: { total: 1, pagina: 1, por_pagina: 20, competencia_referencia: '202603' },
        }),
      });
    });
    await page.goto('/app/explorer');
    // Clica Executar
    const executar = page.getByRole('button', { name: /^Executar$|Executando/i }).first();
    await executar.click();
    // Resposta com status 200 visível
    await expect(page.getByText(/200/).first()).toBeVisible({ timeout: 8000 });
    await expect(page.getByText(/Operadora Teste/i)).toBeVisible({ timeout: 5000 });
  });
});
