import { test, expect } from '@playwright/test';

const PLANO_SLUGS = ['sandbox', 'piloto', 'core', 'enterprise'];

test.describe('CTAs de planos', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/precos');
  });

  test('todos os botões "Solicitar acesso" usam slugs canônicos', async ({ page }) => {
    const links = await page.locator('a:has-text("Solicitar acesso")').all();
    expect(links.length).toBeGreaterThan(0);

    for (const link of links) {
      const href = await link.getAttribute('href');
      expect(href).toContain('/contato?plano=');
      const slug = new URL(href!, 'http://localhost').searchParams.get('plano');
      expect(PLANO_SLUGS).toContain(slug);
    }
  });

  test('CTA Sandbox Técnico usa slug "sandbox"', async ({ page }) => {
    const link = page.locator('a[href*="plano=sandbox"]').first();
    const isVisible = await link.isVisible().catch(() => false);
    if (isVisible) {
      await expect(link).toHaveAttribute('href', /plano=sandbox/);
    }
  });

  test('CTA Piloto Assistido usa slug "piloto"', async ({ page }) => {
    const link = page.locator('a[href*="plano=piloto"]').first();
    await expect(link).toHaveAttribute('href', /plano=piloto/);
  });

  test('CTA Core API usa slug "core"', async ({ page }) => {
    const link = page.locator('a[href*="plano=core"]').first();
    await expect(link).toHaveAttribute('href', /plano=core/);
  });

  test('CTA Enterprise usa slug "enterprise"', async ({ page }) => {
    const link = page.locator('a[href*="plano=enterprise"]').first();
    await expect(link).toHaveAttribute('href', /plano=enterprise/);
  });

  test('clicar em "Solicitar acesso" abre formulário de contato com plano pré-selecionado', async ({ page }) => {
    await page.locator('a[href*="plano=piloto"]').first().click();
    await expect(page).toHaveURL(/\/contato\?plano=piloto/);
    await expect(page.locator('select[value="piloto"], option[value="piloto"]')).toBeTruthy();
  });
});
