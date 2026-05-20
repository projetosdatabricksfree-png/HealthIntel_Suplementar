import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 375, height: 812 } });

test.describe('Menu mobile', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('menu hamburger abre ao clicar', async ({ page }) => {
    const trigger = page.locator('button[aria-label], button:has(svg)').first();
    await trigger.click();
    const mobileNav = page.locator('.site-header__mobile.is-open a').first();
    await expect(mobileNav).toBeVisible();
  });

  test('links de navegação funcionam em mobile', async ({ page }) => {
    const trigger = page.locator('button:has(svg)').first();
    await trigger.click();

    const precoLink = page.getByRole('link', { name: 'Preços' }).first();
    await expect(precoLink).toBeVisible();
    await precoLink.click();
    await expect(page).toHaveURL('/#planos');
  });

  test('botão "Entrar" visível em mobile', async ({ page }) => {
    const trigger = page.locator('button:has(svg)').first();
    await trigger.click();
    const entrarLink = page.locator('.site-header__mobile.is-open').getByRole('link', { name: 'Entrar' });
    await expect(entrarLink).toBeVisible();
  });

  test('logo visível em mobile', async ({ page }) => {
    const logo = page.locator('a[href="/"]').first();
    await expect(logo).toBeVisible();
  });
});
