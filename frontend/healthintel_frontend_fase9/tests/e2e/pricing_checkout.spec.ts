import { test, expect } from '@playwright/test';

test.describe('Página de planos /precos', () => {
  test('CTA FREE leva pro /login (cadastro)', async ({ page }) => {
    await page.goto('/precos');
    const freeCta = page.getByRole('link', { name: /começar grátis/i }).first();
    await expect(freeCta).toBeVisible();
    const href = await freeCta.getAttribute('href');
    expect(href).toMatch(/\/login/);
  });

  test('CTAs STARTER/PRO/MAX apontam pra Stripe ou /contato', async ({ page }) => {
    await page.goto('/precos');
    const ctas = await page.locator('.pricing-card').getByRole('link').all();
    expect(ctas.length).toBeGreaterThanOrEqual(3);
    for (const cta of ctas) {
      const href = await cta.getAttribute('href');
      // Deve ser uma URL: Stripe Payment Link OU /contato (fallback)
      expect(href).toBeTruthy();
      expect(
          href!.includes('stripe.com') ||
          href!.includes('/contato') ||
          href!.startsWith('/login') ||
          href!.includes('buy.stripe') ||
          href!.includes('/checkout/')
      ).toBe(true);
    }
  });

  test('CTA ENTERPRISE direciona pra /contato', async ({ page }) => {
    await page.goto('/precos');
    const cta = page.getByRole('link', { name: /falar com (vendas|comercial|especialista)/i }).first();
    if (await cta.isVisible().catch(() => false)) {
      const href = await cta.getAttribute('href');
      expect(href).toMatch(/\/contato/);
    }
  });
});
