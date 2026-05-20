import { useState } from 'react';
import { formatarTelefone, normalizarTelefone, validarTelefoneBR } from '../../utils/validators';

interface Props {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  className?: string;
  placeholder?: string;
  autoComplete?: string;
  disabled?: boolean;
}

export function TelefoneInput({
  id,
  value,
  onChange,
  required,
  className,
  placeholder = '(11) 98765-4321',
  autoComplete = 'tel',
  disabled,
}: Props) {
  const [erro, setErro] = useState<string | null>(null);
  const visivel = formatarTelefone(value);

  return (
    <>
      <input
        id={id}
        className={className}
        type="tel"
        inputMode="tel"
        placeholder={placeholder}
        value={visivel}
        onChange={(e) => {
          const raw = normalizarTelefone(e.target.value);
          onChange(raw);
          if (erro) setErro(null);
        }}
        onBlur={() => {
          if (value && !validarTelefoneBR(value)) {
            setErro('Telefone inválido. Use DDD + número.');
          }
        }}
        required={required}
        autoComplete={autoComplete}
        disabled={disabled}
        maxLength={16}
      />
      {erro && <span className="field-error" role="alert">{erro}</span>}
    </>
  );
}
