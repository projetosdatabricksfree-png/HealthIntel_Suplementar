import { Link } from 'react-router-dom';
import type { ReactNode } from 'react';
import { cn } from '../utils/format';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
}

interface LinkButtonProps {
  to: string;
  variant?: ButtonVariant;
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

const variantClass: Record<ButtonVariant, string> = {
  primary: 'btn btn-primary',
  secondary: 'btn btn-secondary',
  ghost: 'btn btn-ghost',
  danger: 'btn btn-danger'
};

export function Button({ variant = 'primary', children, className, ...props }: ButtonProps) {
  return (
    <button className={cn(variantClass[variant], className)} {...props}>
      {children}
    </button>
  );
}

export function LinkButton({ to, variant = 'primary', children, className, onClick }: LinkButtonProps) {
  return (
    <Link to={to} className={cn(variantClass[variant], className)} onClick={onClick}>
      {children}
    </Link>
  );
}

interface ExternalLinkButtonProps {
  href: string;
  variant?: ButtonVariant;
  children: ReactNode;
  className?: string;
}

export function ExternalLinkButton({ href, variant = 'primary', children, className }: ExternalLinkButtonProps) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={cn(variantClass[variant], className)}>
      {children}
    </a>
  );
}
