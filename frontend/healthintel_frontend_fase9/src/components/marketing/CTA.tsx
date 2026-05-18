import { ArrowRight, Mail, GitBranch } from 'lucide-react';
import { Link } from 'react-router-dom';

export function CTA() {
  return (
    <section id="contato" className="cta" data-screen-label="cta">
      <div className="container">
        <div className="cta__inner cta__inner--actions">
          <div className="cta__grid-bg" aria-hidden="true"></div>
          <div className="cta__copy">
            <span className="eyebrow eyebrow--on-dark">
              <span className="pulse-dot pulse-dot--mint"></span>
              API em produção · São Paulo / sa-east-1
            </span>
            <h2 className="cta__title">
              Pronto para conectar<br />a ANS ao seu produto?
            </h2>
            <p className="cta__sub">
              Comece em minutos: <strong>Adquirir plano</strong> vai direto para o checkout
              via Stripe e libera sua API key na área do cliente. Volume alto ou contrato
              customizado? <strong>Falar com comercial</strong> abre o canal Enterprise.
            </p>
          </div>
          <div className="cta__actions">
            <a href="#planos" className="btn btn--primary btn--lg btn--on-dark" title="Checkout via Stripe">
              Adquirir plano
              <ArrowRight size={16} />
            </a>
            <Link to="/contato" className="btn btn--outline btn--lg btn--on-dark">
              Falar com comercial
            </Link>
            <div className="cta__meta mono">
              <span><Mail size={12} /> contato@healthintel.com.br</span>
              <span><GitBranch size={12} /> v1 · sa-east-1</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
