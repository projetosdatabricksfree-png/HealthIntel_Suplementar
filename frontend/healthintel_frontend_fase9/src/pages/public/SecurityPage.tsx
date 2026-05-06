import { Card, CardHeader } from '../../components/Card';
import { CodeBlock } from '../../components/CodeBlock';

export function SecurityPage() {
  return (
    <section className="page section">
      <div className="section-heading align-left">
        <p className="eyebrow">Segurança</p>
        <h1>Segurança técnica e proteção comercial</h1>
        <p>
          O produto precisa proteger a API e também impedir uso que transforme o DaaS em um dump único da base.
        </p>
      </div>

      <div className="split-grid">
        <Card>
          <CardHeader title="Segurança técnica" description="Controle operacional da API." />
          <ul className="check-list">
            <li>API key obrigatória nos endpoints protegidos.</li>
            <li>Rate limit por plano.</li>
            <li>Trusted hosts e CORS restrito por ambiente.</li>
            <li>Logs por chave, cliente, endpoint, status e latência.</li>
            <li>Headers de hardening no Nginx/frontend.</li>
          </ul>
        </Card>
        <Card>
          <CardHeader title="Proteção comercial" description="Evitar extração integral e redistribuição." />
          <ul className="check-list">
            <li>Sem endpoint de exportação full.</li>
            <li>Paginação obrigatória.</li>
            <li>Limite máximo por página.</li>
            <li>Detecção de consumo anômalo.</li>
            <li>Contrato proibindo redistribuição/scraping.</li>
          </ul>
        </Card>
      </div>

      <Card>
        <CardHeader title="Exemplo de chamada segura" description="O cliente usa chave própria e limites do plano." />
        <CodeBlock code={`curl -X GET "https://api.healthintel.com.br/v1/rankings/operadora/score?limite=20" \
  -H "X-API-Key: hi_live_xxxxxxxxx"`} />
      </Card>
    </section>
  );
}
