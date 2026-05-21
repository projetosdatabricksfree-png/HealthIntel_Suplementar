import { useState } from 'react';
import { Check, Copy } from 'lucide-react';

interface CopyButtonProps {
  value: string;
  label?: string;
  copiedLabel?: string;
  size?: 'sm' | 'md';
  variant?: 'inline' | 'ghost';
}

export function CopyButton({
  value,
  label = 'Copiar',
  copiedLabel = 'Copiado!',
  size = 'sm',
  variant = 'inline',
}: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = value;
      ta.setAttribute('readonly', '');
      ta.style.position = 'absolute';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    }
  }

  return (
    <button
      type="button"
      className={`copy-btn copy-btn--${variant} copy-btn--${size}${copied ? ' is-copied' : ''}`}
      onClick={handleCopy}
      aria-label={copied ? copiedLabel : label}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      <span>{copied ? copiedLabel : label}</span>
    </button>
  );
}
