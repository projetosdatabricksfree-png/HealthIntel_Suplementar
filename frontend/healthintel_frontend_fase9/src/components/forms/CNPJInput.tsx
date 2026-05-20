import { useState } from 'react';
import { formatarCNPJ, normalizarCNPJ, validarCNPJ } from '../../utils/validators';

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

export function CNPJInput({
  id,
  value,
  onChange,
  required,
  className,
  placeholder = '00.000.000/0000-00',
  autoComplete,
  disabled,
}: Props) {
  const [erro, setErro] = useState<string | null>(null);
  const visivel = formatarCNPJ(value);

  return (
    <>
      <input
        id={id}
        className={className}
        type="text"
        inputMode="numeric"
        placeholder={placeholder}
        value={visivel}
        onChange={(e) => {
          const raw = normalizarCNPJ(e.target.value);
          onChange(raw);
          if (erro) setErro(null);
        }}
        onBlur={() => {
          if (value && !validarCNPJ(value)) {
            setErro('CNPJ inválido. Verifique os dígitos.');
          }
        }}
        required={required}
        autoComplete={autoComplete}
        disabled={disabled}
        maxLength={18}
      />
      {erro && <span className="field-error" role="alert">{erro}</span>}
    </>
  );
}
