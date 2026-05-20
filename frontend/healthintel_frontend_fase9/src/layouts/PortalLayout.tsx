import { NavLink, Outlet, Navigate } from 'react-router-dom';
import { Activity, BarChart3, BookOpen, CreditCard, Database, KeyRound, LayoutDashboard, LogOut, Shield, Users, UserCircle, Wrench } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { canAccessFeature, getCurrentPlan } from '../data/planRules';

const links = [
  { to: '/app', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/endpoints', label: 'Endpoints', icon: BookOpen },
  { to: '/app/explorer', label: 'Live tester', icon: Wrench },
  { to: '/app/api-keys', label: 'API keys', icon: KeyRound },
  { to: '/app/uso', label: 'Uso', icon: BarChart3 },
  { to: '/app/datasets', label: 'Datasets', icon: Database },
  { to: '/app/billing', label: 'Billing', icon: CreditCard },
  { to: '/app/perfil', label: 'Perfil', icon: UserCircle },
  { to: '/app/seguranca', label: 'Segurança', icon: Shield, feature: 'security' as const },
  { to: '/app/equipe', label: 'Equipe', icon: Users, feature: 'team' as const }
];

export function PortalLayout() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const planoNome = user?.tenant_ativo?.plano_nome;
  const currentPlan = getCurrentPlan(planoNome);

  if (isLoading) {
    return (
      <div className="portal-auth-loading">
        Carregando portal...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="portal-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-mark"><Activity size={22} /></span>
          <div>
            <strong>HealthIntel</strong>
            <small>Core ANS</small>
          </div>
        </div>

        <nav className="sidebar-nav">
          {links.filter((item) => !item.feature || canAccessFeature(planoNome, item.feature)).map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} end={item.to === '/app'}>
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <button className="logout-button" onClick={() => void logout()}>
          <LogOut size={18} />
          Sair
        </button>
      </aside>

      <section className="portal-main">
        <header className="portal-topbar">
          <div>
            <strong>{user?.tenant_ativo?.nome || user?.nome}</strong>
            <small>Plano {currentPlan.nome}</small>
          </div>
          <div className="portal-user">
            <span>{user?.nome}</span>
            <div className="avatar">{user?.nome?.slice(0, 1) || 'U'}</div>
          </div>
        </header>
        <main className="portal-content">
          <Outlet />
        </main>
      </section>
    </div>
  );
}
