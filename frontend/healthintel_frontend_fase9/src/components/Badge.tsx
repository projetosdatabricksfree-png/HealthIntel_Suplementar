import { cn } from '../utils/format';

export function Badge({ children, tone = 'blue' }: { children: React.ReactNode; tone?: 'blue' | 'green' | 'yellow' | 'red' | 'gray' }) {
  return <span className={cn('badge', `badge-${tone}`)}>{children}</span>;
}
