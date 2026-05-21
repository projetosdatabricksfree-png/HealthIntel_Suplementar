import { Link, useLocation } from 'react-router-dom';
import { ArrowLeft, BookOpen, Home, Search } from 'lucide-react';

export function NotFoundPage() {
  const { pathname } = useLocation();

  return (
    <div className="not-found">
      <div className="not-found__inner">
        <p className="eyebrow">Erro 404</p>
        <h1 className="not-found__title">Página não encontrada</h1>
        <p className="not-found__desc">
          A rota <code className="mono">{pathname}</code> não existe ou foi movida.
          Se você chegou aqui por um link interno, é provavelmente uma falha nossa —
          conte para a gente em <Link to="/contato">/contato</Link>.
        </p>

        <div className="not-found__actions">
          <Link to="/" className="btn btn--primary">
            <Home size={14} /> Voltar para home
          </Link>
          <Link to="/documentacao" className="btn btn--outline">
            <BookOpen size={14} /> Documentação
          </Link>
          <Link to="/app" className="btn btn--ghost">
            <ArrowLeft size={14} /> Portal do cliente
          </Link>
        </div>

        <div className="not-found__hints">
          <Search size={14} />
          <span>
            Procurando dados? Comece em{' '}
            <Link to="/produto">Produto</Link>,{' '}
            <Link to="/precos">Planos</Link> ou{' '}
            <Link to="/documentacao">Documentação</Link>.
          </span>
        </div>
      </div>
    </div>
  );
}
