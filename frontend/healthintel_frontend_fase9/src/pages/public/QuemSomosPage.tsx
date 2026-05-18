import { Link } from 'react-router-dom';
import { ArrowRight, X } from 'lucide-react';

const PILLARS = [
  {
    num: '01 · Honestidade',
    title: 'Cobertura explícita, sem milagre',
    body: 'Cada dataset declara competência, fonte e status do pipeline. Se uma família ainda não está liberada, falamos. Se exige análise antes, falamos.',
  },
  {
    num: '02 · Engenharia',
    title: 'Contratos versionados, deprecação anunciada',
    body: (
      <>
        API com prefixo <code className="mono">/v1</code> e janela de deprecação publicada.
        Você integra hoje sem medo de quebra silenciosa amanhã.
      </>
    ),
  },
  {
    num: '03 · Governança',
    title: 'Audit log e LGPD por design',
    body: 'Toda chave gera logs auditáveis e exportáveis. Tratamos dados públicos — não armazenamos a base interna do cliente.',
  },
  {
    num: '04 · Self-service',
    title: 'Do checkout ao primeiro request em minutos',
    body: 'Adquira plano via Stripe, entre com Google e a API key aparece na área do cliente. Sem ticket, sem onboarding obrigatório.',
  },
];

const COMMITMENTS = [
  {
    t: 'Distribuição de dados pessoais identificáveis',
    d: 'Não vendemos nem expomos dado individual de beneficiário. SIB nível individual exige solicitação formal.',
  },
  {
    t: 'Pedido para enviar sua base interna',
    d: 'Não precisamos da sua tabela de beneficiários ou prestadores. Cruzamento fica do seu lado.',
  },
  {
    t: 'Quebra de contrato sem aviso',
    d: 'API versionada em /v1, com janela de deprecação anunciada e changelog público.',
  },
  {
    t: 'Promessas de SLA sem contrato',
    d: 'SLA contratual só existe em Enterprise. Os outros planos são best-effort transparente.',
  },
];

export function QuemSomosPage() {
  return (
    <>
      <section className="qs-hero">
        <div className="qs-hero__inner">
          <span className="qs-mission__eyebrow">
            <span className="pulse-dot pulse-dot--mint"></span>
            Quem somos
          </span>
          <h1 className="qs-hero__title">
            Engenharia de dados ANS,<br />
            <span>entregue como infraestrutura.</span>
          </h1>
          <p className="qs-hero__sub">
            HealthIntel é a infraestrutura de dados públicos da ANS para o mercado de saúde
            suplementar. Tratamos, padronizamos, versionamos e expomos via API as bases que
            healthtechs, operadoras, consultorias e times de BI precisam — sem que ninguém
            tenha que manter um robô da ANS internamente.
          </p>
        </div>
      </section>

      <section className="qs-section">
        <div className="qs-mission">
          <span className="qs-mission__eyebrow">Nossa missão</span>
          <p className="qs-mission__quote">
            Que <em>nenhuma empresa no Brasil</em> precise montar e sustentar o seu próprio
            pipeline da ANS para tomar decisões em saúde suplementar.
          </p>
        </div>
      </section>

      <section className="qs-section qs-section--soft">
        <div className="qs-grid">
          <div>
            <span className="qs-block__eyebrow">O que somos</span>
            <h2 className="qs-block__title">
              Uma camada de dados gerenciada sobre as bases públicas da ANS
            </h2>
            <div className="qs-block__body">
              <p>
                Construímos e mantemos um pipeline que <strong>ingere, valida, padroniza e versiona</strong> as
                tabelas publicadas pela ANS — CADOP, SIB, CNES, DIOPS, IDSS, NIP, Reajustes,
                Rol/TUSS, Garantias Financeiras e derivados.
              </p>
              <p>
                Esse pipeline roda do nosso lado, com janela de competência clara e contratos
                versionados em <code className="mono">/v1</code>. Você consome via API REST autenticada,
                paga por uso e foca no seu produto.
              </p>
              <p>
                Tabelas sensíveis como <strong>TISS</strong> e <strong>SIB nível beneficiário individual</strong> são
                liberadas sob solicitação, após análise técnica e comercial.
              </p>
            </div>
          </div>
          <div>
            <span className="qs-block__eyebrow">O que não somos</span>
            <h2 className="qs-block__title">
              Não somos dashboard, BI embutido nem consultoria
            </h2>
            <div className="qs-block__body">
              <p>
                Não entregamos <strong>relatórios prontos</strong>. Não montamos painéis no seu Power BI.
                Não vamos cobrar você por hora de analista.
              </p>
              <p>
                Não pedimos que você <strong>envie sua base interna</strong> para cruzar com a ANS.
                Você consome dados públicos curados, com logs auditáveis por chave.
              </p>
              <p>
                Não fazemos <strong>extração integral</strong> das bases para o cliente. Entregamos
                endpoints e datasets curados — não dumps de FTP.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="qs-section">
        <div style={{ maxWidth: 'var(--container)', margin: '0 auto', padding: '0 32px', textAlign: 'center' }}>
          <span className="qs-block__eyebrow">Como atuamos</span>
          <h2 className="qs-block__title" style={{ maxWidth: 720, margin: '14px auto 0' }}>
            Quatro princípios que orientam cada release
          </h2>
        </div>
        <div className="qs-pillars">
          {PILLARS.map((p) => (
            <article key={p.num} className="qs-pillar">
              <span className="qs-pillar__num">{p.num}</span>
              <h3 className="qs-pillar__title">{p.title}</h3>
              <p className="qs-pillar__body">{p.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="qs-section qs-section--soft">
        <div className="qs-grid" style={{ gridTemplateColumns: '1fr', maxWidth: 820 }}>
          <div>
            <span className="qs-block__eyebrow">Para quem é</span>
            <h2 className="qs-block__title">Times que tomam decisão em saúde suplementar</h2>
            <div className="qs-block__body">
              <p>
                <strong>Healthtechs</strong> — para acelerar produto com dados de mercado, sem
                criar equipe interna de engenharia de dados ANS.
              </p>
              <p>
                <strong>Operadoras</strong> — para comparar com pares, monitorar concentração
                regional e antecipar movimentos regulatórios.
              </p>
              <p>
                <strong>Consultorias regulatórias</strong> — para entregar análise sem
                reconstruir o pipeline da ANS em cada projeto.
              </p>
              <p>
                <strong>Times de BI / Dados / Produto / Regulação</strong> — para integrar
                ANS direto no seu data warehouse via REST, sem extração manual.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="qs-section">
        <div style={{ maxWidth: 'var(--container)', margin: '0 auto', padding: '0 32px', textAlign: 'center' }}>
          <span className="qs-block__eyebrow">Compromissos</span>
          <h2 className="qs-block__title" style={{ maxWidth: 720, margin: '14px auto 0' }}>
            O que você nunca vai ver da gente
          </h2>
        </div>
        <div className="qs-not-list">
          {COMMITMENTS.map((c) => (
            <div key={c.t} className="qs-not">
              <span className="qs-not__icon">
                <X size={14} strokeWidth={2.5} />
              </span>
              <div>
                <p className="qs-not__t">{c.t}</p>
                <p className="qs-not__d">{c.d}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="qs-section qs-section--soft">
        <div className="qs-cta">
          <h2 className="qs-cta__title">Pronto pra integrar a ANS sem manter pipeline?</h2>
          <p className="qs-cta__sub">
            Comece pelo plano FREE com 100 req/dia, ou vá direto pro STARTER e tenha 30.000 req/dia
            após o checkout via Stripe.
          </p>
          <div className="qs-cta__actions">
            <Link
              to="/#planos"
              className="btn btn--primary btn--lg btn--on-dark"
              style={{ background: 'white', color: 'var(--primary-600)' }}
            >
              Ver planos
              <ArrowRight size={14} />
            </Link>
            <Link to="/contato" className="btn btn--outline btn--lg btn--on-dark">
              Falar com comercial
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
