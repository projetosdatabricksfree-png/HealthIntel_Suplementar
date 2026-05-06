import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { PublicLayout } from './layouts/PublicLayout';
import { PortalLayout } from './layouts/PortalLayout';
import { HomePage } from './pages/public/HomePage';
import { ProductPage } from './pages/public/ProductPage';
import { PricingPage } from './pages/public/PricingPage';
import { PublicDocsPage } from './pages/public/PublicDocsPage';
import { SecurityPage } from './pages/public/SecurityPage';
import { ContactPage } from './pages/public/ContactPage';
import { LoginPage } from './pages/public/LoginPage';
import { DashboardPage } from './pages/portal/DashboardPage';
import { EndpointsPage } from './pages/portal/EndpointsPage';
import { ExplorerPage } from './pages/portal/ExplorerPage';
import { ApiKeysPage } from './pages/portal/ApiKeysPage';
import { UsagePage } from './pages/portal/UsagePage';
import { DatasetsPage } from './pages/portal/DatasetsPage';
import { BillingPage } from './pages/portal/BillingPage';
import { TeamPage } from './pages/portal/TeamPage';
import { ProfilePage } from './pages/portal/ProfilePage';
import { PortalSecurityPage } from './pages/portal/PortalSecurityPage';
import { AdminBillingPage } from './pages/portal/AdminBillingPage';
import { AdminLayoutsPage } from './pages/portal/AdminLayoutsPage';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/produto" element={<ProductPage />} />
            <Route path="/precos" element={<PricingPage />} />
            <Route path="/documentacao" element={<PublicDocsPage />} />
            <Route path="/seguranca" element={<SecurityPage />} />
            <Route path="/contato" element={<ContactPage />} />
            <Route path="/login" element={<LoginPage />} />
          </Route>

          <Route path="/app" element={<PortalLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="endpoints" element={<EndpointsPage />} />
            <Route path="explorer" element={<ExplorerPage />} />
            <Route path="api-keys" element={<ApiKeysPage />} />
            <Route path="uso" element={<UsagePage />} />
            <Route path="datasets" element={<DatasetsPage />} />
            <Route path="billing" element={<BillingPage />} />
            <Route path="equipe" element={<TeamPage />} />
            <Route path="perfil" element={<ProfilePage />} />
            <Route path="seguranca" element={<PortalSecurityPage />} />
            <Route path="admin/billing" element={<AdminBillingPage />} />
            <Route path="admin/layouts" element={<AdminLayoutsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
