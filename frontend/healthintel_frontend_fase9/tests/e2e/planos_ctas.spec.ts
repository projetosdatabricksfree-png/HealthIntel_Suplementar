import { test, expect } from '@playwright/test';

const PLANO_CTA = [
  { label: 'Começar sandbox', plano: 'sandbox' },
  { label: 'Solicitar piloto', plano: 'piloto' },
  { label: 'Falar com vendas', plano: 'core' }
];

test.describe('CTAs de planos', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/v1/checkout/sessao', async (route) => {
      const body = route.request().postDataJSON() as { plano: string };
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          dados: {
            checkout_url: `http://localhost:5173/checkout/sucesso?mock_plano=${body.plano}`,
            session_id: `cs_test_${body.plano}`,
            plano: body.plano
          }
        })
      });
    });
    await page.goto('/precos');
  });

  for (const { label, plano } of PLANO_CTA) {
    test(`CTA ${label} cria checkout Stripe para ${plano}`, async ({ page }) => {
      const requestPromise = page.waitForRequest((request) => (
        request.url().includes('/v1/checkout/sessao')
        && request.method() === 'POST'
        && request.postDataJSON().plano === plano
      ));

      await page.getByRole('button', { name: label }).click();
      await requestPromise;
      await expect(page).toHaveURL(new RegExp(`/checkout/sucesso\\?mock_plano=${plano}`));
    });
  }

  test('página de sucesso não exibe API key no navegador', async ({ page }) => {
    await page.goto('/checkout/sucesso?session_id=cs_test_sandbox');
    await expect(page.getByRole('heading', { name: 'Estamos liberando seu acesso' })).toBeVisible();
    await expect(page.getByText('API key está pronta')).toHaveCount(0);
    await expect(page.getByText('Copiar')).toHaveCount(0);
  });
});
