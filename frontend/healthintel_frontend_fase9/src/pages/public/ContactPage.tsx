import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '../../components/Button';
import { Card } from '../../components/Card';
import { useNotification } from '../../components/NotificationProvider';
import { addAuditEvent, addLead } from '../../services/localPortalStore';

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function ContactPage() {
  const [searchParams] = useSearchParams();
  const { success, error } = useNotification();
  const initialPlan = useMemo(() => searchParams.get('plano') || '', [searchParams]);
  const origem = searchParams.get('origem') || 'site_publico';
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [empresa, setEmpresa] = useState('');
  const [perfil, setPerfil] = useState('Corretora / consultoria');
  const [plano, setPlano] = useState(initialPlan);
  const [mensagem, setMensagem] = useState('');

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!nome.trim() || !email.trim() || !empresa.trim() || !mensagem.trim()) {
      error('Preencha nome, e-mail, empresa e mensagem.');
      return;
    }
    if (!emailRegex.test(email.trim())) {
      error('Informe um e-mail válido.');
      return;
    }

    addLead({
      nome: nome.trim(),
      email: email.trim(),
      empresa: empresa.trim(),
      perfil,
      plano: plano.trim() || undefined,
      origem,
      mensagem: mensagem.trim()
    });
    addAuditEvent({
      tipo: 'contato_enviado',
      usuario: email.trim(),
      detalhe: `Lead salvo localmente. Plano: ${plano || 'nao informado'}. Origem: ${origem}.`,
      status: 'sucesso'
    });
    success('Solicitação registrada localmente para homologação. Nenhum e-mail externo foi enviado.');
    setMensagem('');
  }

  return (
    <section className="page section">
      <div className="section-heading">
        <p className="eyebrow">Contato</p>
        <h1>Solicitar piloto HealthIntel Core ANS</h1>
        <p>Registre interesse comercial para Sandbox Técnico, Piloto Assistido, Core API ou pacote sob contrato.</p>
      </div>

      <Card className="contact-card">
        <form className="form-grid" onSubmit={submit}>
          <label>
            Nome
            <input value={nome} onChange={(event) => setNome(event.target.value)} placeholder="Seu nome" />
          </label>
          <label>
            E-mail
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="voce@empresa.com.br" />
          </label>
          <label>
            Empresa
            <input value={empresa} onChange={(event) => setEmpresa(event.target.value)} placeholder="Nome da empresa" />
          </label>
          <label>
            Perfil
            <select value={perfil} onChange={(event) => setPerfil(event.target.value)}>
              <option>Corretora / consultoria</option>
              <option>Healthtech</option>
              <option>Operadora</option>
              <option>BI / analytics</option>
              <option>Hospital / rede</option>
            </select>
          </label>
          <label>
            Plano de interesse
            <input value={plano} onChange={(event) => setPlano(event.target.value)} placeholder="Sandbox Técnico, Piloto Assistido, Core API, Core Pro..." />
          </label>
          <label className="full">
            Mensagem
            <textarea
              rows={5}
              value={mensagem}
              onChange={(event) => setMensagem(event.target.value)}
              placeholder="Conte qual análise de ANS você precisa resolver."
            />
          </label>
          <Button type="submit">Solicitar demonstração</Button>
        </form>
      </Card>
    </section>
  );
}
