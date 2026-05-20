const PESOS_CNPJ_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
const PESOS_CNPJ_2 = [6, ...PESOS_CNPJ_1];

export function normalizarCNPJ(cnpj: string): string {
  return (cnpj || '').replace(/\D/g, '');
}

export function validarCNPJ(cnpj: string): boolean {
  const d = normalizarCNPJ(cnpj);
  if (d.length !== 14 || /^(\d)\1+$/.test(d)) return false;
  const base = d.slice(0, 12);
  const soma1 = base.split('').reduce((acc, c, i) => acc + Number(c) * PESOS_CNPJ_1[i], 0);
  const dv1 = soma1 % 11 < 2 ? 0 : 11 - (soma1 % 11);
  if (dv1 !== Number(d[12])) return false;
  const base2 = base + String(dv1);
  const soma2 = base2.split('').reduce((acc, c, i) => acc + Number(c) * PESOS_CNPJ_2[i], 0);
  const dv2 = soma2 % 11 < 2 ? 0 : 11 - (soma2 % 11);
  return dv2 === Number(d[13]);
}

export function formatarCNPJ(cnpj: string): string {
  const d = normalizarCNPJ(cnpj).slice(0, 14);
  if (d.length <= 2) return d;
  if (d.length <= 5) return `${d.slice(0, 2)}.${d.slice(2)}`;
  if (d.length <= 8) return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5)}`;
  if (d.length <= 12) return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8)}`;
  return `${d.slice(0, 2)}.${d.slice(2, 5)}.${d.slice(5, 8)}/${d.slice(8, 12)}-${d.slice(12, 14)}`;
}

export function normalizarTelefone(tel: string): string {
  return (tel || '').replace(/\D/g, '');
}

export function validarTelefoneBR(tel: string): boolean {
  let d = normalizarTelefone(tel);
  if (d.startsWith('55') && d.length > 11) d = d.slice(2);
  if (d.length !== 10 && d.length !== 11) return false;
  const ddd = Number(d.slice(0, 2));
  return ddd >= 11 && ddd <= 99;
}

export function formatarTelefone(tel: string): string {
  const d = normalizarTelefone(tel).slice(0, 11);
  if (d.length <= 2) return d.length > 0 ? `(${d}` : '';
  if (d.length <= 6) return `(${d.slice(0, 2)}) ${d.slice(2)}`;
  if (d.length <= 10) return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
  return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

export interface SenhaForteResult {
  ok: boolean;
  motivo?: string;
}

export function validarSenhaForte(senha: string): SenhaForteResult {
  if (!senha || senha.length < 8) return { ok: false, motivo: 'Mínimo 8 caracteres.' };
  if (!/[A-Za-z]/.test(senha)) return { ok: false, motivo: 'Deve conter ao menos uma letra.' };
  if (!/\d/.test(senha)) return { ok: false, motivo: 'Deve conter ao menos um número.' };
  return { ok: true };
}
