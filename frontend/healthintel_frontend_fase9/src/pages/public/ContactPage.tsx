import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ArrowRight, Mail } from 'lucide-react';
import { Section, SectionHeader } from '../../components/marketing/Section';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, addLead } from '../../services/localPortalStore';
import { enviarLead } from '../../services/contatoApi';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function ContactPage() {
  const [searchParams] = useSearchParams();
  const { success, error } = useNotification();
  const initialPlan = useMemo(() => searchParams.get('plano') || 'piloto', [searchParams]);
  const origem = searchParams.get('origem') || 'contato_page';

  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [empresa, setEmpresa] = useState('');
  const [perfil, setPerfil] = useState('Corretora / consultoria');
  const [plano, setPlano] = useState(initialPlan);
  const [mensagem, setMensagem] = useState('');
  const [honeypot, setHoneypot] = useState('');
  const [enviando, setEnviando] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!nome.trim() || !email.trim() || !empresa.trim() || !mensagem.trim()) {
      error('Preencha nome, e-mail, empresa e mensagem.');
      return;
    }
    if (!emailRegex.test(email.trim())) {
      error('Informe um e-mail válido.');
      return;
    }
    if (honeypot) return;

    setEnviando(true);
    addLead({
      nome: nome.trim(),
      email: email.trim(),
      empresa: empresa.trim(),
      perfil,
      plano: plano.trim() || undefined,
      origem,
      mensagem: mensagem.trim(),
    });
    try {
      const resp = await enviarLead({
        nome: nome.trim(),
        email: email.trim(),
        empresa: empresa.trim(),
        perfil,
        plano: plano.trim() || undefined,
        mensagem: mensagem.trim(),
        origem,
        honeypot,
      });
      if (resp.ok) {
        success('Solicitação enviada. Retornaremos em até 1 dia útil.');
        addAuditEvent({
          tipo: 'contato_enviado',
          usuario: email.trim(),
          detalhe: `Lead enviado. Plano: ${plano || 'nao informado'}. Status email: ${resp.email_status || 'desconhecido'}.`,
          status: 'sucesso',
        });
        setMensagem('');
      } else {
        error(resp.detalhe || 'Falha no envio. Tente novamente ou escreva direto para projetosdatabricksfree@gmail.com.');
        addAuditEvent({
          tipo: 'contato_enviado',
          usuario: email.trim(),
          detalhe: `Falha: ${resp.detalhe || 'erro desconhecido'}`,
          status: 'erro',
        });
      }
    } catch (e) {
      error('Falha de conexão. Tente novamente ou escreva para projetosdatabricksfree@gmail.com.');
      addAuditEvent({
        tipo: 'contato_enviado',
        usuario: email.trim(),
        detalhe: `Exception: ${(e as Error).message}`,
        status: 'erro',
      });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Section id="contato-top" label="contato">
      <SectionHeader
        eyebrow="Contato"
        title="Falar com comercial"
        description="Registre interesse em STARTER, PRO, MAX ou ENTERPRISE. Retornamos com onboarding quando o caso exigir venda assistida."
        align="center"
      />
      <div className="section__body">
        <div className="contact-page-card">
          <form className="contact-page-form" onSubmit={submit}>
            <label>
              Nome
              <input
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Seu nome"
                autoComplete="name"
              />
            </label>
            <label>
              E-mail
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="voce@empresa.com.br"
                autoComplete="email"
              />
            </label>
            <label>
              Empresa
              <input
                value={empresa}
                onChange={(e) => setEmpresa(e.target.value)}
                placeholder="Nome da empresa"
                autoComplete="organization"
              />
            </label>
            <label>
              Perfil
              <select value={perfil} onChange={(e) => setPerfil(e.target.value)}>
                <option>Corretora / consultoria</option>
                <option>Healthtech</option>
                <option>Operadora</option>
                <option>BI / analytics</option>
                <option>Hospital / rede</option>
              </select>
            </label>
            <label className="full">
              Plano de interesse
              <select value={plano} onChange={(e) => setPlano(e.target.value)}>
                <option value="">Selecione um plano...</option>
                <option value="starter">STARTER</option>
                <option value="pro">PRO</option>
                <option value="max">MAX</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </label>
            <label className="full">
              Mensagem
              <textarea
                rows={5}
                value={mensagem}
                onChange={(e) => setMensagem(e.target.value)}
                placeholder="Conte qual análise de ANS você precisa resolver."
              />
            </label>
            <input
              type="text"
              style={{ position: 'absolute', left: -9999, opacity: 0 }}
              value={honeypot}
              onChange={(e) => setHoneypot(e.target.value)}
              tabIndex={-1}
              autoComplete="off"
              aria-hidden="true"
            />
            <div className="full" style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, alignItems: 'center' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12 }} className="mono">
                <Mail size={12} /> projetosdatabricksfree@gmail.com
              </span>
              <button type="submit" className="btn btn--primary btn--lg" disabled={enviando}>
                {enviando ? 'Enviando...' : 'Enviar solicitação'}
                {!enviando && <ArrowRight size={16} />}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Section>
  );
}
