import { ArrowUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Hero } from '../../components/marketing/Hero';
import { StatsStrip } from '../../components/marketing/StatsStrip';
import { TrustBar } from '../../components/marketing/TrustBar';
import { Section, SectionHeader } from '../../components/marketing/Section';
import { ProductSection } from '../../components/marketing/ProductSection';
import { CustomerJourney } from '../../components/marketing/CustomerJourney';
import { DataCatalog } from '../../components/marketing/DataCatalog';
import { SecurityStrip } from '../../components/marketing/SecurityStrip';
import { Coverage } from '../../components/marketing/Coverage';
import { FAQ } from '../../components/marketing/FAQ';
import { CTA } from '../../components/marketing/CTA';

export function HomePage() {
  return (
    <>
      <Hero variant="split" showWidget />

      <StatsStrip />

      <TrustBar />

      <Section id="datasets" surface="default" label="datasets">
        <SectionHeader
          eyebrow="Catálogo"
          title="O produto é o catálogo. Cada dataset, versionado e datado."
          description="Operadoras, beneficiários, financeiro DIOPS, IDSS, IGR, NIP, regulatório, score, rede, TUSS e mais — lidos do catálogo de produção com grão, janela de competência e contagem real de registros. Status por dataset em /status/cobertura."
          action={
            <Link to="/documentacao" className="btn btn--ghost btn--sm">
              Ver catálogo + cURL
              <ArrowUpRight size={14} />
            </Link>
          }
        />
        <div className="section__body">
          <DataCatalog />
        </div>
      </Section>

      <Section id="produto" surface="soft" label="produto">
        <SectionHeader
          eyebrow="Por que DaaS"
          title="Um contrato de dados — não mais um projeto de engenharia"
          description="Quatro garantias pelas quais healthtechs, operadoras e consultorias preferem assinar o dado pronto a montar e manter o próprio pipeline da ANS."
        />
        <div className="section__body">
          <ProductSection />
        </div>
      </Section>

      <Section id="como-funciona" surface="default" label="como-funciona">
        <SectionHeader
          eyebrow="Como você consome"
          title="Do request ao envelope { dados, meta } em 3 passos"
          description="Sem baixar ZIP, sem decifrar layout fixo, sem descobrir o que mudou no PDF de Resolução. Autentique, chame o endpoint e receba JSON versionado — datado por competência."
        />
        <div className="section__body">
          <CustomerJourney />
        </div>
      </Section>

      <Section id="seguranca" surface="soft" label="seguranca">
        <SectionHeader
          eyebrow="Segurança e governança"
          title="API key, rate limit, logs e versionamento"
          description="Operação previsível, com chave por cliente, limites por plano, trilha auditável e contratos versionados."
        />
        <div className="section__body">
          <SecurityStrip />
        </div>
      </Section>

      <Section id="escopo" surface="default" label="escopo">
        <SectionHeader
          eyebrow="Cobertura"
          title="Todas as tabelas ANS — com escopo controlado para dados sensíveis"
          description="Cobertura honesta, lida ao vivo de /status/cobertura: o release atual já inclui as famílias completas. TISS e SIB nível beneficiário individual passam por análise comercial antes da liberação."
        />
        <div className="section__body">
          <Coverage />
        </div>
      </Section>

      {/* Seção de planos desabilitada para posicionamento B2B */}

      <Section id="faq" surface="default" label="faq">
        <SectionHeader
          eyebrow="FAQ"
          title="Perguntas frequentes"
          description="Respostas diretas para times técnicos e comerciais avaliando a API."
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
