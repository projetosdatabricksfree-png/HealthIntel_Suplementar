import { test, expect } from '@playwright/test';

test.describe('Página /documentacao pública', () => {
  test('renderiza catálogo de datasets com status + endpoint + cURL', async ({ page }) => {
    await page.goto('/documentacao');
    await expect(page.getByRole('heading', { name: /api healthintel/i })).toBeVisible();

    // Seções obrigatórias
    await expect(page.locator('#visao-geral')).toBeVisible();
    await expect(page.locator('#quickstart')).toBeVisible();
    await expect(page.locator('#autenticacao')).toBeVisible();
    await expect(page.locator('#rate-limits')).toBeVisible();
    await expect(page.locator('#erros')).toBeVisible();
    await expect(page.locator('#catalogo')).toBeVisible();

    // Quickstart cURL deve mostrar X-API-Key e a base URL
    const quickstart = page.locator('#quickstart');
    await expect(quickstart).toContainText('X-API-Key');
    await expect(quickstart).toContainText('api.healthintel.com.br');

    // Catálogo deve listar pelo menos alguns datasets-chave (nomes vêm sem acento de datasets.ts)
    const cat = page.locator('#catalogo');
    await expect(cat).toContainText(/Operadora 360/i);
    await expect(cat).toContainText(/Beneficiarios/i);
    await expect(cat).toContainText(/IDSS/i);

    // Filtro de status existe e funciona
    await page.locator('#filtro-status').selectOption('pronto');
    await expect(cat).toContainText(/Pronto para consumo/i);
  });

  test('rate limits por plano são exibidos com FREE até ENTERPRISE', async ({ page }) => {
    await page.goto('/documentacao');
    const rates = page.locator('#rate-limits');
    await expect(rates).toContainText('FREE');
    await expect(rates).toContainText('STARTER');
    await expect(rates).toContainText('PRO');
    await expect(rates).toContainText('MAX');
    await expect(rates).toContainText('ENTERPRISE');
    await expect(rates).toContainText('100 req/dia');
  });

  test('erros HTTP comuns documentados (401, 403, 422, 429)', async ({ page }) => {
    await page.goto('/documentacao');
    const erros = page.locator('#erros');
    await expect(erros).toContainText('401');
    await expect(erros).toContainText('403');
    await expect(erros).toContainText('422');
    await expect(erros).toContainText('429');
  });
});
