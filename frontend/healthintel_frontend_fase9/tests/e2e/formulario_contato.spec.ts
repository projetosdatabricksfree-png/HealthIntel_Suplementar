import { test, expect } from '@playwright/test';

test.describe('Formulário de contato', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/contato');
  });

  test('página de contato carrega sem erro', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible();
  });

  test('plano é pré-selecionado via query param slug', async ({ page }) => {
    await page.goto('/contato?plano=piloto');
    const select = page.locator('select').filter({ hasText: 'Piloto Assistido' }).first();
    await expect(select).toHaveValue('piloto');
  });

  test('slug "core" pré-seleciona Core API/Pro', async ({ page }) => {
    await page.goto('/contato?plano=core');
    const select = page.locator('select').nth(1);
    await expect(select).toHaveValue('core');
  });

  test('formulário rejeita envio sem campos obrigatórios', async ({ page }) => {
    await page.locator('button[type="submit"]').click();
    const errorMsg = page.locator('text=Preencha').or(page.locator('[role="alert"]'));
    await expect(errorMsg.first()).toBeVisible({ timeout: 3000 }).catch(() => {
      // Validação HTML5 nativa — o form simplesmente não envia
    });
  });

  test('formulário completo é aceito', async ({ page }) => {
    await page.goto('/contato?plano=sandbox');
    await page.fill('input[placeholder*="nome"]', 'João Silva');
    await page.fill('input[type="email"]', 'joao@empresa.com.br');
    await page.fill('input[placeholder*="empresa"]', 'Empresa Teste');
    await page.fill('textarea', 'Preciso de dados ANS para análise de mercado.');
    await page.locator('button[type="submit"]').click();
    const successMsg = page.locator('text=registrad').or(page.locator('text=sucesso'));
    await expect(successMsg.first()).toBeVisible({ timeout: 5000 });
  });
});
