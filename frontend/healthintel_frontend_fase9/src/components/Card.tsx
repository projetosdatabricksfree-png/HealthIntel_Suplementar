import type { ReactNode } from 'react';
import { cn } from '../utils/format';

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={cn('card', className)}>{children}</section>;
}

export function CardHeader({ eyebrow, title, description }: { eyebrow?: string; title: ReactNode; description?: ReactNode }) {
  return (
    <div className="card-header">
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
}

export function MetricCard({
  label,
  value,
  detail,
  loading,
}: {
  label: string;
  value: string;
  detail: string;
  loading?: boolean;
}) {
  return (
    <div className={cn('metric-card', loading && 'metric-card--loading')}>
      <span>{label}</span>
      {loading ? (
        <span className="skeleton skeleton--metric-value" aria-hidden="true" />
      ) : (
        <strong>{value}</strong>
      )}
      {loading ? (
        <span className="skeleton skeleton--metric-detail" aria-hidden="true" />
      ) : (
        <small>{detail}</small>
      )}
    </div>
  );
}
