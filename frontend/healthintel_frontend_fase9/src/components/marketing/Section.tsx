import type { ReactNode } from 'react';

type Surface = 'default' | 'soft';

interface SectionProps {
  id?: string;
  surface?: Surface;
  label?: string;
  children: ReactNode;
}

export function Section({ id, surface = 'default', label, children }: SectionProps) {
  return (
    <section id={id} data-screen-label={label || id} className={`section section--${surface}`}>
      <div className="container">{children}</div>
    </section>
  );
}

interface SectionHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
  action?: ReactNode;
}

export function SectionHeader({ eyebrow, title, description, align = 'left', action }: SectionHeaderProps) {
  return (
    <div className={`section-header section-header--${align}`}>
      <div className="section-header__copy">
        {eyebrow && <span className="eyebrow eyebrow--muted">{eyebrow}</span>}
        <h2 className="section-header__title">{title}</h2>
        {description && <p className="section-header__desc">{description}</p>}
      </div>
      {action && <div className="section-header__action">{action}</div>}
    </div>
  );
}
