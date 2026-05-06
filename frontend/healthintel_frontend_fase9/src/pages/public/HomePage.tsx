import { ArrowRight, BarChart3, DatabaseZap, KeyRound, ShieldCheck, Stethoscope, TrendingUp } from 'lucide-react';
import { LinkButton } from '../../components/Button';
import { Card } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';
import { plans } from '../../data/plans';
import { PlanCard } from '../../components/PlanCard';

export function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">DaaS/API para saúde suplementar</p>
          <h1>Dados da ANS tratados, versionados e prontos para consumir.</h1>
          <p>
            API para análise de operadoras, beneficiários, rede CNES, mercado, rankings,
            score, financeiro e risco regulatório — sem sua equipe montar pipeline próprio.
          </p>
          <div className="hero-actions">
            <LinkButton to="/contato?origem=hero&plano=Piloto%20Assistido">Solicitar piloto <ArrowRight size={18} /></LinkButton>
            <LinkButton to="/documentacao" variant="secondary">Ver documentação</LinkButton>
          </div>
          <div className="trust-strip">
            <span>API-first</span>
            <span>Dados validados</span>
            <span>Rate limit</span>
            <span>Governança ANS</span>
          </div>
        </div>

        <div className="hero-panel">
          <div className="hero-panel-header">
            <span className="status-dot" />
            <span>Live tester</span>
          </div>
          <CodeBlock code={`curl -X GET \
  "https://api.healthintel.com.br/v1/operadoras?uf=SP&limite=20" \
  -H "X-API-Key: SUA_CHAVE"`} />
          <div className="hero-metrics">
            <div><strong>7</strong><span>famílias Core</span></div>
            <div><strong>12-24m</strong><span>SIB hot</span></div>
            <div><strong>100%</strong><span>API controlada</span></div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <p className="eyebrow">Produto comercial</p>
          <h2>Inteligência ANS pronta para uso</h2>
          <p>
            Uma solução robusta, estável e de alto impacto para transformar dados regulatórios
            em decisão comercial sem exigir infraestrutura própria do cliente.
          </p>
        </div>
        <div className="feature-grid">
          {[
            { icon: Stethoscope, title: 'Operadoras 360', desc: 'Cadastro, modalidade, situação, UF, score e sinais de risco.' },
            { icon: TrendingUp, title: 'Mercado e beneficiários', desc: 'Visão por operadora, município e competência com janela controlada.' },
            { icon: DatabaseZap, title: 'Rede CNES', desc: 'Estabelecimentos de saúde por município e UF para leitura regional de cobertura.' },
            { icon: BarChart3, title: 'Rankings e score', desc: 'Rankings de crescimento, oportunidade e score composto.' },
            { icon: DatabaseZap, title: 'Dados curados', desc: 'API pronta para consumo, sem expor bases internas ao cliente.' },
            { icon: KeyRound, title: 'Acesso por API key', desc: 'Planos, rate limit, paginação e logs de consumo por cliente.' },
            { icon: ShieldCheck, title: 'Consumo controlado', desc: 'Paginação, limites por plano e controle de uso por API key.' }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.title} className="feature-card">
                <Icon size={30} />
                <h3>{item.title}</h3>
                <p>{item.desc}</p>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="section section-soft">
        <div className="section-heading">
          <p className="eyebrow">Planos</p>
          <h2>Comece com piloto, evolua para API recorrente</h2>
        </div>
        <div className="plans-grid">
          {plans.slice(0, 3).map((plan) => <PlanCard key={plan.nome} plan={plan} />)}
        </div>
      </section>
    </>
  );
}
