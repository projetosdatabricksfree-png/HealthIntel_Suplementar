import { Button } from '../../components/Button';
import { Card } from '../../components/Card';

export function ContactPage() {
  return (
    <section className="page section">
      <div className="section-heading">
        <p className="eyebrow">Contato</p>
        <h1>Solicitar piloto HealthIntel Core ANS</h1>
        <p>Use este formulário como base para captar leads na primeira versão.</p>
      </div>

      <Card className="contact-card">
        <form className="form-grid" onSubmit={(event) => event.preventDefault()}>
          <label>
            Nome
            <input placeholder="Seu nome" />
          </label>
          <label>
            E-mail
            <input type="email" placeholder="voce@empresa.com.br" />
          </label>
          <label>
            Empresa
            <input placeholder="Nome da empresa" />
          </label>
          <label>
            Perfil
            <select>
              <option>Corretora / consultoria</option>
              <option>Healthtech</option>
              <option>Operadora</option>
              <option>BI / analytics</option>
              <option>Hospital / rede</option>
            </select>
          </label>
          <label className="full">
            Mensagem
            <textarea rows={5} placeholder="Conte qual análise de ANS você precisa resolver." />
          </label>
          <Button type="submit">Solicitar demonstração</Button>
        </form>
      </Card>
    </section>
  );
}
