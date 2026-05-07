import { test, expect } from '@playwright/test';

const NAV_LINKS = [
  { label: 'Produto', url: '/produto' },
  { label: 'Documentação', url: '/documentacao' },
  { label: 'Preços', url: '/precos' },
  { label: 'Segurança', url: '/seguranca' },
  { label: 'Contato', url: '/contato' },
];

test.describe('Navbar e links principais', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('logo leva para a home', async ({ page }) => {
    await page.click('a[href="/"]');
    await expect(page).toHaveURL('/');
  });

  for (const link of NAV_LINKS) {
    test(`link "${link.label}" navega para ${link.url}`, async ({ page }) => {
      await page.getByRole('link', { name: link.label }).first().click();
      await expect(page).toHaveURL(link.url);
    });
  }

  test('botão "Entrar" navega para /login', async ({ page }) => {
    await page.getByRole('link', { name: 'Entrar' }).click();
    await expect(page).toHaveURL('/login');
  });

  test('nenhum link com href="#" na navbar', async ({ page }) => {
    const hrefs = await page.locator('nav a').evaluateAll(
      (els) => els.map((el) => (el as HTMLAnchorElement).getAttribute('href'))
    );
    const broken = hrefs.filter((h) => h === '#' || h === null);
    expect(broken).toHaveLength(0);
  });
});
