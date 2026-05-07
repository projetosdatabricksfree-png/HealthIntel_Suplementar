import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 812 } });

test.describe('Menu mobile', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('menu hamburger abre ao clicar', async ({ page }) => {
    const trigger = page.locator('button[aria-label], button:has(svg)').first();
    await trigger.click();
    const mobileNav = page.locator('nav a, .mobile-menu a').first();
    await expect(mobileNav).toBeVisible();
  });

  test('links de navegação funcionam em mobile', async ({ page }) => {
    const trigger = page.locator('button:has(svg)').first();
    await trigger.click();

    const precoLink = page.getByRole('link', { name: 'Preços' }).first();
    await expect(precoLink).toBeVisible();
    await precoLink.click();
    await expect(page).toHaveURL('/precos');
  });

  test('botão "Entrar" visível em mobile', async ({ page }) => {
    const entrarLink = page.getByRole('link', { name: 'Entrar' }).first();
    await expect(entrarLink).toBeVisible();
  });

  test('logo visível em mobile', async ({ page }) => {
    const logo = page.locator('a[href="/"]').first();
    await expect(logo).toBeVisible();
  });
});
