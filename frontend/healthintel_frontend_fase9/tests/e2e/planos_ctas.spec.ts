import { test, expect } from '@playwright/test';

test.describe('CTAs de planos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/precos');
  });

  test('CTA FREE leva para cadastro gratuito', async ({ page }) => {
    const href = await page.getByRole('link', { name: /começar grátis/i }).first().getAttribute('href');
    expect(href).toMatch(/\/login/);
  });

  test('CTAs STARTER, PRO e MAX usam Stripe ou fallback comercial', async ({ page }) => {
    const ctas = await page.locator('.pricing-card').getByRole('link').all();
    expect(ctas.length).toBeGreaterThanOrEqual(4);

    const paidHrefs = [];
    for (const cta of ctas) {
      const label = (await cta.textContent()) || '';
      const href = await cta.getAttribute('href');
      if (/adquirir plano|falar com comercial/i.test(label)) {
        paidHrefs.push(href || '');
      }
    }

    expect(paidHrefs.length).toBeGreaterThanOrEqual(3);
    for (const href of paidHrefs) {
      expect(
        href.includes('stripe.com') ||
          href.includes('buy.stripe') ||
          href.includes('/contato') ||
          href.includes('/checkout/')
      ).toBe(true);
    }
  });

  test('CTA Enterprise leva para contato', async ({ page }) => {
    const href = await page.getByRole('link', { name: /falar com comercial/i }).last().getAttribute('href');
    expect(href).toMatch(/\/contato/);
  });

  test('página de sucesso não exibe API key no navegador', async ({ page }) => {
    await page.goto('/checkout/sucesso?session_id=cs_test_sandbox');
    await expect(page.getByRole('heading', { name: 'Estamos liberando seu acesso' })).toBeVisible();
    await expect(page.getByText('API key está pronta')).toHaveCount(0);
    await expect(page.getByText('Copiar')).toHaveCount(0);
  });
});
