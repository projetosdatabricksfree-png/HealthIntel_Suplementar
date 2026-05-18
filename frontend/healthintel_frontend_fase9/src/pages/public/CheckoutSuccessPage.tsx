import { Link } from 'react-router-dom';
import { LinkButton } from '../../components/Button';
import { Card } from '../../components/Card';

export function CheckoutSuccessPage() {
  return (
    <section className="page section">
      <Card className="checkout-card">
        <p className="eyebrow">Pagamento recebido</p>
        <h1>Estamos liberando seu acesso</h1>
        <p>
          Assim que o Stripe confirmar o pagamento, sua API key será enviada para o e-mail usado
          no checkout.
        </p>
        <p>
          Se o e-mail não chegar em alguns minutos, verifique spam ou fale com suporte informando o
          e-mail da compra:{' '}
          <Link to="/contato">
            <strong>Falar com suporte</strong>
          </Link>
        </p>
        <LinkButton to="/documentacao">Ver documentação</LinkButton>
      </Card>
    </section>
  );
}
