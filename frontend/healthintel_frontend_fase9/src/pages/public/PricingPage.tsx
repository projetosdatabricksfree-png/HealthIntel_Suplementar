import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Section, SectionHeader } from '../../components/marketing/Section';
import { FAQ } from '../../components/marketing/FAQ';
import { CTA } from '../../components/marketing/CTA';

export function PricingPage() {
  return (
    <>
      <Section id="planos-top" surface="default" label="planos">
        <SectionHeader
          eyebrow="Planos"
          title="Modelo de acesso customizado por volume"
          description="HealthIntel é uma plataforma de dados com modelo B2B. Cada integração é negociada de acordo com o volume de requisições, dados necessários e escopo de acesso."
          align="center"
        />
        <div className="section__body">
          <div className="b2b-cta" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Solicite um orçamento</h3>
            <p style={{ fontSize: '0.95rem', marginBottom: '2rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
              Fale com nosso time comercial para discussão de volume, escopo de dados e plano customizado.
            </p>
            <Link to="/contato" className="btn btn--primary btn--lg">
              <span>Falar com comercial</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </Section>

      <Section id="faq" surface="soft" label="faq">
        <SectionHeader
          eyebrow="FAQ"
          title="Perguntas frequentes"
          description="Sobre cobrança, SLA, limites e governança."
          align="center"
        />
        <div className="section__body section__body--narrow">
          <FAQ />
        </div>
      </Section>

      <CTA />
    </>
  );
}
