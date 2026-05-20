import { test, expect } from '@playwright/test';

test.describe('Cadastro B2B (Free)', () => {
  test.beforeEach(async ({ page }) => {
    // Mock do POST /v1/auth/cadastro para evitar criar usuário real em produção
    await page.route('**/v1/auth/cadastro', async (route) => {
      const body = route.request().postDataJSON() as Record<string, unknown>;
      // Eco do payload pra inspeção do teste
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'pendente_verificacao',
          mensagem: 'Verifique seu e-mail.',
          eco: body,
        }),
      });
    });
    await page.goto('/login?mode=signup');
    // O modo cadastro é interno ao LoginPage — clica no botão de criar conta se não estiver
    const criarBtn = page.getByRole('button', { name: 'Criar conta grátis' }).first();
    if (await criarBtn.isVisible({ timeout: 1000 }).catch(() => false)) {
      await criarBtn.click();
    }
  });

  test('renderiza form B2B com todos os campos obrigatórios', async ({ page }) => {
    const tituloOk = await page.getByRole('heading', { name: /criar conta/i }).isVisible({ timeout: 4000 }).catch(() => false);
    if (!tituloOk) {
      // navegação direta pro signup mode via clique
      await page.getByText('Criar conta grátis', { exact: false }).first().click({ trial: false }).catch(() => undefined);
    }
    await expect(page.getByLabel(/Nome completo/i)).toBeVisible();
    await expect(page.getByLabel(/E-mail corporativo/i)).toBeVisible();
    await expect(page.getByLabel(/Senha \(mín/i)).toBeVisible();
    await expect(page.getByLabel(/Confirmar senha/i)).toBeVisible();
    await expect(page.getByLabel(/Nome da empresa/i)).toBeVisible();
    await expect(page.getByLabel(/CNPJ/i)).toBeVisible();
    await expect(page.getByLabel(/Telefone/i)).toBeVisible();
    await expect(page.getByLabel(/Cargo/i)).toBeVisible();
    await expect(page.getByLabel('Segmento *')).toBeVisible();
    await expect(page.getByLabel('Objetivo de uso *')).toBeVisible();
    await expect(page.getByText(/Termos de Uso/i)).toBeVisible();
    await expect(page.getByText(/Política de Privacidade e LGPD/i)).toBeVisible();
  });

  test('CNPJ inválido bloqueia o envio', async ({ page }) => {
    await page.getByLabel(/Nome completo/i).fill('Ana Teste');
    await page.getByLabel(/E-mail corporativo/i).fill('ana@empresa.com.br');
    await page.getByLabel(/Senha \(mín/i).fill('senha-segura-1');
    await page.getByLabel(/Confirmar senha/i).fill('senha-segura-1');
    await page.getByLabel(/Nome da empresa/i).fill('Empresa Teste LTDA');
    await page.getByLabel(/CNPJ/i).fill('11111111111111'); // inválido
    await page.getByLabel(/Telefone/i).fill('11987654321');
    await page.getByLabel(/Cargo/i).fill('Analista');
    await page.getByLabel('Segmento *').selectOption('healthtech');
    await page.getByLabel('Objetivo de uso *').selectOption('testar_api');
    // marca aceites
    const checks = page.locator('input[type="checkbox"]');
    await checks.nth(0).check();
    await checks.nth(1).check();

    let requestSent = false;
    page.on('request', (req) => {
      if (req.url().includes('/v1/auth/cadastro')) requestSent = true;
    });
    await page.getByRole('button', { name: /criar conta grátis/i }).click();
    // Aguarda um beat — não deve disparar a request porque CNPJ inválido
    await page.waitForTimeout(800);
    expect(requestSent).toBe(false);
  });

  test('cadastro válido envia payload completo com 8 campos B2B', async ({ page }) => {
    await page.getByLabel(/Nome completo/i).fill('Ana Costa');
    await page.getByLabel(/E-mail corporativo/i).fill('ana.teste@empresa.com.br');
    await page.getByLabel(/Senha \(mín/i).fill('senha-segura-1');
    await page.getByLabel(/Confirmar senha/i).fill('senha-segura-1');
    await page.getByLabel(/Nome da empresa/i).fill('Empresa Teste LTDA');
    await page.getByLabel(/CNPJ/i).fill('53.936.542/0001-37'); // válido
    await page.getByLabel(/Telefone/i).fill('11987654321');
    await page.getByLabel(/Cargo/i).fill('Analista de Dados');
    await page.getByLabel('Segmento *').selectOption('healthtech');
    await page.getByLabel('Objetivo de uso *').selectOption('testar_api');
    const checks = page.locator('input[type="checkbox"]');
    await checks.nth(0).check();
    await checks.nth(1).check();

    const reqPromise = page.waitForRequest('**/v1/auth/cadastro');
    await page.getByRole('button', { name: /criar conta grátis/i }).click();
    const req = await reqPromise;
    const payload = req.postDataJSON() as Record<string, unknown>;
    expect(payload.email).toBe('ana.teste@empresa.com.br');
    expect(payload.empresa).toBe('Empresa Teste LTDA');
    expect(payload.cnpj).toBe('53936542000137');
    expect(payload.telefone).toBe('11987654321');
    expect(payload.cargo).toBe('Analista de Dados');
    expect(payload.segmento).toBe('healthtech');
    expect(payload.objetivo_uso).toBe('testar_api');
    expect(payload.aceite_termos).toBe(true);
    expect(payload.aceite_lgpd).toBe(true);
    await expect(page.getByText(/Verifique seu e-mail/i)).toBeVisible();
  });
});
