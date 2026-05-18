import { useState } from 'react';
import { Copy, ArrowRight, Check } from 'lucide-react';

const SNIPPET = `curl -H "X-API-Key: $HEALTHINTEL_KEY" \\
  "https://api.healthintel.tech/v1/operadoras?page=1&per_page=10"`;

export function CurlExample() {
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard?.writeText(SNIPPET).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  return (
    <div className="curl-example">
      <div className="curl-example__head">
        <div className="curl-example__head-left">
          <span className="method-badge method-badge--get">GET</span>
          <code className="mono">/v1/operadoras?page=1&amp;per_page=10</code>
        </div>
        <div className="curl-example__head-right">
          <span className="curl-example__label">Exemplo cURL</span>
          <button className="curl-example__copy" type="button" onClick={copy} title="Copiar">
            {copied ? <Check size={13} /> : <Copy size={13} />}
            {copied ? 'Copiado' : 'Copiar'}
          </button>
        </div>
      </div>
      <pre className="curl-example__code mono">{SNIPPET}</pre>
      <div className="curl-example__foot">
        <a href="/documentacao" className="btn btn--primary btn--sm">
          Abrir documentação
          <ArrowRight size={14} />
        </a>
      </div>
    </div>
  );
}
