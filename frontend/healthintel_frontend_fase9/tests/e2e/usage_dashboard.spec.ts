import { test, expect } from '@playwright/test';

async function setupSession(page: import('@playwright/test').Page, comApiKey: boolean) {
  await page.addInitScript((withKey) => {
    localStorage.setItem('healthintel.auth.access_token', 'mock-access');
    localStorage.setItem('healthintel.auth.refresh_token', 'mock-refresh');
    if (withKey) localStorage.setItem('healthintel.portal.api_key', 'hi_test_1234567890abcdef');
  }, comApiKey);
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

test.describe('Dashboard de uso /app/uso', () => {
  test('sem API key configurada mostra empty state honesto', async ({ page }) => {
    await setupSession(page, false);
    await page.goto('/app/uso');
    await expect(page.getByText(/Configure uma .*API key/i)).toBeVisible({ timeout: 6000 });
  });

  test('com uso registrado mostra série diária real e quota_daily', async ({ page }) => {
    await setupSession(page, true);
    await page.route('**/v1/me/uso**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          dados: {
            periodo: '7d',
            total_requisicoes: 17,
            total_erros: 1,
            latencia_media_ms: 120,
            success_rate: 94.1,
            serie_diaria: [
              { dia: '2026-05-20', requisicoes: 17, erros: 1, latencia_ms: 120 },
            ],
            por_endpoint: [
              { endpoint: '/v1/operadoras', requisicoes: 17, erros: 1 },
            ],
          },
          meta: {
            periodo: '7d',
            inicio: '2026-05-13',
            fim: '2026-05-20',
            plano: 'free',
            quota_daily: 100,
            quota_used_today: 17,
          },
        }),
      });
    });

    await page.goto('/app/uso');
    await expect(page.getByText(/17/).first()).toBeVisible({ timeout: 6000 });
    // quota diária 17/100 deve aparecer
    await expect(page.getByText(/17\/100/)).toBeVisible({ timeout: 4000 });
    await expect(page.getByText('/v1/operadoras')).toBeVisible();
  });
});
