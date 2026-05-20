import { useState } from 'react';
import { Plus, Minus } from 'lucide-react';

const FAQ_ITEMS = [
  { q: 'De onde vêm os dados?', a: 'Bases públicas da ANS. A HealthIntel trata, padroniza, versiona e expõe via API. Não distribuímos dados pessoais sensíveis de beneficiários.' },
  { q: 'Como é feita a autenticação?', a: 'Por API key, enviada no header HTTP X-API-Key. Cada plano define limites, escopo e rate limit.' },
  { q: 'Existe rate limit?', a: 'Sim. Cada plano tem rate limit próprio, com paginação consistente e logs de consumo por chave para governança.' },
  { q: 'Vocês entregam dados brutos?', a: 'Não. A entrega é via API com endpoints curados. Não fazemos extração integral das bases públicas para clientes.' },
  { q: 'Como funcionam atualizações e versionamento?', a: 'A API é versionada (ex.: /v1). Mudanças que quebram contrato passam por janela de deprecação anunciada.' },
  { q: 'Tem SLA?', a: 'SLA contratual é negociado no ENTERPRISE. MAX tem SLA de resposta; FREE, STARTER e PRO têm suporte conforme a matriz do plano.' },
  { q: 'Posso testar antes de contratar?', a: 'Sim. O FREE permite avaliação técnica com 100 requisições por dia e uma chave de teste.' },
  { q: 'Como começo em produção?', a: 'STARTER, PRO e MAX usam checkout self-service. ENTERPRISE é negociado pelo formulário comercial.' },
];

export function FAQ() {
  const [open, setOpen] = useState<number>(0);
  return (
    <div className="faq">
      {FAQ_ITEMS.map((it, i) => {
        const isOpen = open === i;
        return (
          <div key={it.q} className={`faq__item${isOpen ? ' is-open' : ''}`}>
            <button className="faq__trigger" onClick={() => setOpen(isOpen ? -1 : i)} type="button">
              <span>{it.q}</span>
              {isOpen ? <Minus size={16} /> : <Plus size={16} />}
            </button>
            <div className="faq__content">
              <p>{it.a}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
