import { Outlet, NavLink, Link } from 'react-router-dom';
import { Activity, Menu } from 'lucide-react';
import { useState } from 'react';
import { LinkButton } from '../components/Button';

export function PublicLayout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="public-shell">
      <header className="public-header">
        <Link to="/" className="brand">
          <span className="brand-mark"><Activity size={22} /></span>
          <span>HealthIntel <b>Core ANS</b></span>
        </Link>
        <button className="mobile-menu" onClick={() => setOpen((value) => !value)} aria-label="Abrir menu">
          <Menu />
        </button>
        <nav className={open ? 'nav nav-open' : 'nav'}>
          <NavLink to="/produto" onClick={() => setOpen(false)}>Produto</NavLink>
          <NavLink to="/documentacao" onClick={() => setOpen(false)}>Documentação</NavLink>
          <NavLink to="/precos" onClick={() => setOpen(false)}>Preços</NavLink>
          <NavLink to="/seguranca" onClick={() => setOpen(false)}>Segurança</NavLink>
          <NavLink to="/contato" onClick={() => setOpen(false)}>Contato</NavLink>
          <LinkButton to="/login" variant="primary" onClick={() => setOpen(false)}>Entrar</LinkButton>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="public-footer">
        <div>
          <Link to="/" className="brand">
            <span className="brand-mark"><Activity size={20} /></span>
            <span>HealthIntel <b>Core ANS</b></span>
          </Link>
          <p>API de inteligência para saúde suplementar brasileira.</p>
        </div>
        <div className="footer-links">
          <Link to="/documentacao">Docs</Link>
          <Link to="/seguranca">Segurança</Link>
          <Link to="/precos">Planos</Link>
          <Link to="/login">Portal</Link>
        </div>
      </footer>
    </div>
  );
}
