import { useEffect, useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

interface NavItem {
  href: string;
  label: string;
  anchor?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { href: '#produto', label: 'Produto', anchor: true },
  { href: '#como-funciona', label: 'Como funciona', anchor: true },
  { href: '#datasets', label: 'Datasets', anchor: true },
  { href: '#planos', label: 'Preços', anchor: true },
  { href: '#seguranca', label: 'Segurança', anchor: true },
];

export function PublicLayout() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const onHome = location.pathname === '/';

  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 8);
    on();
    window.addEventListener('scroll', on, { passive: true });
    return () => window.removeEventListener('scroll', on);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname, location.hash]);

  function handleAnchorClick(e: React.MouseEvent<HTMLAnchorElement>, hash: string) {
    if (!onHome) {
      e.preventDefault();
      navigate(`/${hash}`);
      return;
    }
    const id = hash.replace('#', '');
    const el = document.getElementById(id);
    if (el) {
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      window.history.replaceState(null, '', hash);
    }
  }

  return (
    <div className="public-shell">
      <header className={`site-header${scrolled ? ' is-scrolled' : ''}`}>
        <div className="container site-header__inner">
          <Link to="/" className="logo" onClick={() => setMobileOpen(false)}>
            <img src="/logo-mark.png" alt="HealthIntel" width={28} height={28} />
            <span className="logo__word">healthintel</span>
          </Link>
          <nav className="site-header__nav">
            {NAV_ITEMS.map((item) =>
              item.anchor ? (
                <a key={item.href} href={item.href} onClick={(e) => handleAnchorClick(e, item.href)}>
                  {item.label}
                </a>
              ) : (
                <Link key={item.href} to={item.href}>
                  {item.label}
                </Link>
              )
            )}
          </nav>
          <div className="site-header__cta">
            <Link to="/login" className="btn btn--ghost btn--sm">
              Entrar
            </Link>
            <a
              href="#planos"
              className="btn btn--primary btn--sm"
              onClick={(e) => handleAnchorClick(e, '#planos')}
              title="Checkout via Stripe"
            >
              Adquirir plano
            </a>
          </div>
          <button
            className="site-header__menu"
            onClick={() => setMobileOpen((v) => !v)}
            aria-label="Menu"
            type="button"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className={`site-header__mobile${mobileOpen ? ' is-open' : ''}`}>
            {NAV_ITEMS.map((item) =>
              item.anchor ? (
                <a
                  key={item.href}
                  href={item.href}
                  onClick={(e) => {
                    handleAnchorClick(e, item.href);
                    setMobileOpen(false);
                  }}
                >
                  {item.label}
                </a>
              ) : (
                <Link key={item.href} to={item.href} onClick={() => setMobileOpen(false)}>
                  {item.label}
                </Link>
              )
            )}
            <Link to="/documentacao" onClick={() => setMobileOpen(false)}>
              Documentação
            </Link>
            <Link to="/contato" onClick={() => setMobileOpen(false)}>
              Contato
            </Link>
            <div className="site-header__mobile-actions">
              <Link to="/login" className="btn btn--outline btn--sm">
                Entrar
              </Link>
              <a
                href="#planos"
                className="btn btn--primary btn--sm"
                onClick={(e) => {
                  handleAnchorClick(e, '#planos');
                  setMobileOpen(false);
                }}
              >
                Adquirir plano
              </a>
            </div>
          </div>
        </div>
      </header>

      <main>
        <Outlet />
      </main>

      <footer className="footer">
        <div className="container footer__inner">
          <div className="footer__brand">
            <Link to="/" className="logo">
              <img src="/logo-mark.png" alt="HealthIntel" width={28} height={28} />
              <span className="logo__word">healthintel</span>
            </Link>
            <p className="footer__tagline">
              Core ANS via API. Dados públicos tratados, versionados e auditáveis —
              entregues como infraestrutura de dados, não como planilha nem consultoria.
            </p>
            <p className="footer__domain mono">healthintel.com.br</p>
          </div>
          <div className="footer__cols">
            <div>
              <p className="footer__col-title">Produto</p>
              <a href="/#produto">Para quem é</a>
              <a href="/#como-funciona">Como funciona</a>
              <a href="/#datasets">Datasets</a>
              <a href="/#planos">Preços</a>
              <Link to="/documentacao">Documentação</Link>
            </div>
            <div>
              <p className="footer__col-title">Empresa</p>
              <Link to="/seguranca">Segurança</Link>
              <Link to="/contato">Contato</Link>
              <Link to="/login">Portal</Link>
            </div>
            <div>
              <p className="footer__col-title">Legal</p>
              <Link to="/seguranca">LGPD</Link>
              <Link to="/seguranca">Termos</Link>
              <Link to="/seguranca">Privacidade</Link>
            </div>
          </div>
        </div>
        <div className="container footer__bottom">
          <span className="mono">© 2026 HealthIntel · CNPJ 53.936.542/0001-37</span>
          <span className="mono">São Paulo · BR · sa-east-1</span>
        </div>
      </footer>
    </div>
  );
}
