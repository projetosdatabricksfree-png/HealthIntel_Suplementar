export function formatNumber(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value);
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 1 }).format(value);
}

export function cn(...values: Array<string | false | undefined | null>): string {
  return values.filter(Boolean).join(' ');
}
