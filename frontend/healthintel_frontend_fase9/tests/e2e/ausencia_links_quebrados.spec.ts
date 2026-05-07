import { test, expect } from '@playwright/test';

const PUBLIC_ROUTES = ['/', '/produto', '/precos', '/documentacao', '/seguranca', '/contato'];

test.describe('Ausência de links quebrados', () => {
  for (const route of PUBLIC_ROUTES) {
    test(`rota pública ${route} carrega sem erro 4xx/5xx`, async ({ page }) => {
      const response = await page.goto(route);
      expect(response?.status()).toBeLessThan(400);
      // SPA não retorna 404 no navigate — verificar que a página renderizou
      await expect(page.locator('#root')).not.toBeEmpty();
    });
  }

  test('rotas públicas não contêm links internos quebrados (/404)', async ({ page }) => {
    const failedRequests: string[] = [];

    page.on('response', (response) => {
      if (
        response.status() >= 400 &&
        response.request().resourceType() === 'document'
      ) {
        failedRequests.push(`${response.url()} → ${response.status()}`);
      }
    });

    for (const route of PUBLIC_ROUTES) {
      await page.goto(route);
    }

    expect(failedRequests).toHaveLength(0);
  });

  test('não há links <a> apontando para #', async ({ page }) => {
    await page.goto('/');
    const hrefs = await page.locator('a').evaluateAll(
      (els) => els.map((el) => (el as HTMLAnchorElement).getAttribute('href'))
    );
    const broken = hrefs.filter((h) => h === '#');
    expect(broken).toHaveLength(0);
  });

  test('robots.txt acessível', async ({ page }) => {
    const response = await page.goto('/robots.txt');
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain('User-agent');
  });

  test('sitemap.xml acessível', async ({ page }) => {
    const response = await page.goto('/sitemap.xml');
    expect(response?.status()).toBe(200);
    const text = await response?.text();
    expect(text).toContain('urlset');
  });
});
