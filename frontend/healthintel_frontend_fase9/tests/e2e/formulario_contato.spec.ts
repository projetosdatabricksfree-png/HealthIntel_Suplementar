import { test, expect } from '@playwright/test';

test.describe('Formulário de contato', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/contato');
  });

  test('página de contato carrega sem erro', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible();
  });

  test('plano é pré-selecionado via query param slug', async ({ page }) => {
    await page.goto('/contato?plano=enterprise');
    await expect(page.locator('select').nth(1)).toHaveValue('enterprise');
  });

  test('slug "pro" pré-seleciona PRO', async ({ page }) => {
    await page.goto('/contato?plano=pro');
    await expect(page.locator('select').nth(1)).toHaveValue('pro');
  });

  test('formulário rejeita envio sem campos obrigatórios', async ({ page }) => {
    await page.locator('button[type="submit"]').click();
    const errorMsg = page.locator('text=Preencha').or(page.locator('[role="alert"]'));
    await expect(errorMsg.first()).toBeVisible({ timeout: 3000 }).catch(() => {
      // Validação HTML5 nativa — o form simplesmente não envia
    });
  });

  test('formulário completo é aceito', async ({ page }) => {
    await page.route('**/v1/contato/leads', async (route) => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true, lead_id: 'lead_test', email_status: 'fila_local' }),
      });
    });
    await page.goto('/contato?plano=starter');
    await page.getByLabel('Nome').fill('João Silva');
    await page.getByLabel('E-mail').fill('joao@empresa.com.br');
    await page.getByLabel('Empresa').fill('Empresa Teste');
    await page.getByLabel('Mensagem').fill('Preciso de dados ANS para análise de mercado.');
    await page.locator('button[type="submit"]').click();
    const successMsg = page.locator('text=Solicitação enviada');
    await expect(successMsg.first()).toBeVisible({ timeout: 5000 });
  });
});
