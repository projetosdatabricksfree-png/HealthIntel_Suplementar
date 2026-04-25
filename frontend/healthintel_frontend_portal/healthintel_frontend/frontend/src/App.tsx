import { useEffect, useMemo, useState } from "react";
import { apiRequest, DISPLAY_API_BASE_URL, maskKey } from "./lib/api";
import { endpointCatalog, layerCards, tiers } from "./data/catalog";

type Route = "home" | "pricing" | "docs" | "login" | "dashboard";
type ApiState = "idle" | "loading" | "success" | "error";

type Session = {
  email: string;
  company: string;
  apiKey: string;
};

const STORAGE_KEY = "healthintel.session";

function getRouteFromHash(): Route {
  const hash = window.location.hash.replace("#/", "").replace("#", "");
  if (["pricing", "docs", "login", "dashboard"].includes(hash)) return hash as Route;
  return "home";
}

function navigate(route: Route) {
  window.location.hash = route === "home" ? "/" : `/${route}`;
}

function loadSession(): Session {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { email: "", company: "", apiKey: "" };
    return { email: "", company: "", apiKey: "", ...JSON.parse(raw) };
  } catch {
    return { email: "", company: "", apiKey: "" };
  }
}

function saveSession(session: Session) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export default function App() {
  const [route, setRoute] = useState<Route>(getRouteFromHash());
  const [session, setSession] = useState<Session>(loadSession());

  useEffect(() => {
    const onHashChange = () => setRoute(getRouteFromHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  const isAuthenticated = Boolean(session.apiKey);

  function onLogin(next: Session) {
    setSession(next);
    saveSession(next);
    navigate("dashboard");
  }

  function onLogout() {
    const empty = { email: "", company: "", apiKey: "" };
    localStorage.removeItem(STORAGE_KEY);
    setSession(empty);
    navigate("home");
  }

  return (
    <div className="app-shell">
      <Header route={route} isAuthenticated={isAuthenticated} onLogout={onLogout} />

      {route === "home" && <Landing />}
      {route === "pricing" && <Pricing />}
      {route === "docs" && <Docs apiKey={session.apiKey} />}
      {route === "login" && <Login initialSession={session} onLogin={onLogin} />}
      {route === "dashboard" && (
        <Dashboard session={session} setSession={setSession} onLogout={onLogout} />
      )}

      <Footer />
    </div>
  );
}

function Header({
  route,
  isAuthenticated,
  onLogout
}: {
  route: Route;
  isAuthenticated: boolean;
  onLogout: () => void;
}) {
  return (
    <header className="header">
      <button className="brand" onClick={() => navigate("home")} aria-label="Página inicial">
        <span className="brand-mark">HI</span>
        <span>
          <strong>HealthIntel</strong>
          <small>Suplementar API</small>
        </span>
      </button>

      <nav className="nav">
        <button className={route === "home" ? "active" : ""} onClick={() => navigate("home")}>
          Produto
        </button>
        <button
          className={route === "pricing" ? "active" : ""}
          onClick={() => navigate("pricing")}
        >
          Planos
        </button>
        <button className={route === "docs" ? "active" : ""} onClick={() => navigate("docs")}>
          Documentação
        </button>
        {isAuthenticated ? (
          <>
            <button
              className={route === "dashboard" ? "active" : ""}
              onClick={() => navigate("dashboard")}
            >
              Console
            </button>
            <button className="ghost" onClick={onLogout}>
              Sair
            </button>
          </>
        ) : (
          <button className="primary small" onClick={() => navigate("login")}>
            Entrar
          </button>
        )}
      </nav>
    </header>
  );
}

function Landing() {
  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">API B2B de dados públicos da ANS</div>
          <h1>Dados de saúde suplementar prontos para consumo por API.</h1>
          <p>
            O HealthIntel transforma bases públicas complexas da ANS em endpoints estáveis,
            versionados e governados para times de engenharia, dados, risco, pricing,
            regulatório e produto.
          </p>
          <div className="hero-actions">
            <button className="primary" onClick={() => navigate("login")}>
              Acessar console
            </button>
            <button className="secondary" onClick={() => navigate("docs")}>
              Ver documentação
            </button>
          </div>

          <div className="trust-row">
            <span>REST API</span>
            <span>X-API-Key</span>
            <span>Rate limit</span>
            <span>Bronze / Prata / Ouro</span>
          </div>
        </div>

        <div className="hero-panel">
          <div className="terminal">
            <div className="terminal-bar">
              <span />
              <span />
              <span />
            </div>
            <pre>{`curl "${DISPLAY_API_BASE_URL}/v1/operadoras?uf=SP" \\
  -H "X-API-Key: hi_live_********"

{
  "data": [
    {
      "registro_ans": "123456",
      "razao_social": "Operadora Exemplo",
      "uf": "SP",
      "modalidade": "Medicina de Grupo"
    }
  ],
  "meta": {
    "camada": "ouro",
    "cache": "hit",
    "versao_dataset": "2026.04"
  }
}`}</pre>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <span className="eyebrow">Produto de dados, não dashboard</span>
          <h2>O cliente compra a infraestrutura pronta para integrar.</h2>
          <p>
            A proposta comercial é parecida com APIs de dados maduras: plano, chave, consumo,
            documentação, playground e SLA. A inteligência do cliente continua no cliente.
          </p>
        </div>

        <div className="grid three">
          {[
            {
              title: "Contrato por camada",
              text: "Ouro para consumo de negócio, Prata para dados padronizados e Bronze para auditoria técnica."
            },
            {
              title: "Governança de layout",
              text: "Layouts ANS versionados, aliases manuais, aprovação humana e compatibilidade retroativa."
            },
            {
              title: "API comercial",
              text: "Autenticação por chave, rate limit por plano, log de uso, billing e endpoints segmentados."
            }
          ].map((item) => (
            <article className="card" key={item.title}>
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section split">
        <div>
          <span className="eyebrow">Camadas comerciais</span>
          <h2>Medallion Architecture exposta como produto.</h2>
          <p>
            O frontend posiciona a plataforma como uma API de dados ANS curados, com diferenciação
            comercial por profundidade de acesso, volume, SLA e rastreabilidade.
          </p>
          <button className="secondary" onClick={() => navigate("pricing")}>
            Comparar planos
          </button>
        </div>

        <div className="layer-stack">
          {layerCards.map((layer) => (
            <div className="layer-card" key={layer.name}>
              <div>
                <strong>{layer.name}</strong>
                <small>{layer.schema}</small>
              </div>
              <p>{layer.copy}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section metrics">
        <div>
          <strong>22</strong>
          <span>datasets mapeados</span>
        </div>
        <div>
          <strong>5</strong>
          <span>tiers comerciais</span>
        </div>
        <div>
          <strong>3</strong>
          <span>camadas vendáveis</span>
        </div>
        <div>
          <strong>API</strong>
          <span>primeiro canal de consumo</span>
        </div>
      </section>
    </main>
  );
}

function Pricing() {
  return (
    <main className="page">
      <section className="page-heading">
        <span className="eyebrow">Modelo comercial</span>
        <h1>Planos por camada, volume e SLA.</h1>
        <p>
          A precificação abaixo é uma régua inicial de MVP. Ajuste os valores depois que medir
          custo real por requisição, latência p95 e uso por família de dataset.
        </p>
      </section>

      <section className="pricing-grid">
        {tiers.map((tier) => (
          <article className={`price-card ${tier.highlighted ? "highlighted" : ""}`} key={tier.key}>
            <div className="price-header">
              <span>{tier.subtitle}</span>
              <h2>{tier.name}</h2>
              <strong>{tier.price}</strong>
            </div>
            <div className="price-meta">
              <span>Camada: {tier.layer}</span>
              <span>{tier.requests}</span>
              <span>{tier.sla}</span>
            </div>
            <ul>
              {tier.features.map((feature) => (
                <li key={feature}>{feature}</li>
              ))}
            </ul>
            <button className={tier.highlighted ? "primary full" : "secondary full"}>{tier.cta}</button>
          </article>
        ))}
      </section>
    </main>
  );
}

function Docs({ apiKey }: { apiKey: string }) {
  const [selected, setSelected] = useState(endpointCatalog[3]);

  const curlSnippet = `curl "${DISPLAY_API_BASE_URL}${selected.samplePath}"${
    selected.auth ? ` \\\n  -H "X-API-Key: ${apiKey ? maskKey(apiKey) : "SUA_CHAVE"}"` : ""
  }`;

  const pythonSnippet = `import requests

url = "${DISPLAY_API_BASE_URL}${selected.samplePath}"
headers = ${selected.auth ? '{"X-API-Key": "SUA_CHAVE"}' : "{}"}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()
print(response.json())`;

  return (
    <main className="page">
      <section className="page-heading">
        <span className="eyebrow">Developer-first</span>
        <h1>Documentação de API para integração rápida.</h1>
        <p>
          O portal foi desenhado para o cliente testar endpoints, copiar exemplos e entender
          exatamente qual plano libera cada camada.
        </p>
      </section>

      <section className="docs-layout">
        <aside className="endpoint-list">
          {endpointCatalog.map((endpoint) => (
            <button
              key={`${endpoint.method}-${endpoint.path}`}
              className={selected.path === endpoint.path ? "selected" : ""}
              onClick={() => setSelected(endpoint)}
            >
              <span>{endpoint.method}</span>
              <strong>{endpoint.path}</strong>
              <small>{endpoint.layer} · {endpoint.tier}</small>
            </button>
          ))}
        </aside>

        <article className="docs-panel">
          <div className="endpoint-title">
            <span className={`pill ${selected.layer.toLowerCase().replace("ú", "u")}`}>
              {selected.layer}
            </span>
            <h2>{selected.method} {selected.path}</h2>
            <p>{selected.description}</p>
          </div>

          <div className="doc-grid">
            <div className="doc-box">
              <span>Autenticação</span>
              <strong>{selected.auth ? "X-API-Key obrigatória" : "Público"}</strong>
            </div>
            <div className="doc-box">
              <span>Plano mínimo</span>
              <strong>{selected.tier}</strong>
            </div>
            <div className="doc-box">
              <span>Base URL</span>
              <strong>{DISPLAY_API_BASE_URL}</strong>
            </div>
          </div>

          <CodeBlock title="cURL" code={curlSnippet} />
          <CodeBlock title="Python" code={pythonSnippet} />

          <div className="callout">
            <strong>Regra de produto:</strong> Bronze custa mais infraestrutura, então deve consumir
            mais quota do que Ouro. No frontend, isso precisa aparecer como explicação comercial
            para o cliente entender por que planos técnicos são mais caros.
          </div>
        </article>
      </section>
    </main>
  );
}

function Login({
  initialSession,
  onLogin
}: {
  initialSession: Session;
  onLogin: (session: Session) => void;
}) {
  const [email, setEmail] = useState(initialSession.email);
  const [company, setCompany] = useState(initialSession.company);
  const [apiKey, setApiKey] = useState(initialSession.apiKey);
  const [status, setStatus] = useState<ApiState>("idle");
  const [message, setMessage] = useState("");

  async function validateKey() {
    setStatus("loading");
    setMessage("");

    const result = await apiRequest("/v1/operadoras?pagina=1&por_pagina=1", apiKey);
    if (result.ok) {
      setStatus("success");
      setMessage("Chave validada com sucesso. Acesso à API confirmado.");
      return;
    }

    setStatus("error");
    setMessage(
      result.status === 401
        ? "Chave inválida ou ausente no backend."
        : `Não foi possível validar agora: ${result.error || `HTTP ${result.status}`}`
    );
  }

  function submit() {
    onLogin({ email, company, apiKey });
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <span className="eyebrow">Portal do desenvolvedor</span>
        <h1>Entrar com API key</h1>
        <p>
          O backend atual autentica por header <code>X-API-Key</code>. Este login salva a chave
          localmente para você testar os endpoints protegidos.
        </p>

        <label>
          E-mail
          <input
            type="email"
            placeholder="voce@empresa.com.br"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </label>

        <label>
          Empresa
          <input
            type="text"
            placeholder="Nome da empresa"
            value={company}
            onChange={(event) => setCompany(event.target.value)}
          />
        </label>

        <label>
          API key
          <input
            type="password"
            placeholder="hi_live_..."
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
          />
        </label>

        <div className="auth-actions">
          <button className="secondary" disabled={!apiKey || status === "loading"} onClick={validateKey}>
            {status === "loading" ? "Validando..." : "Validar chave"}
          </button>
          <button className="primary" disabled={!apiKey} onClick={submit}>
            Entrar no console
          </button>
        </div>

        {message && <div className={`message ${status}`}>{message}</div>}
      </section>
    </main>
  );
}

function Dashboard({
  session,
  setSession,
  onLogout
}: {
  session: Session;
  setSession: (session: Session) => void;
  onLogout: () => void;
}) {
  const [health, setHealth] = useState<{ status: ApiState; text: string }>({
    status: "idle",
    text: "Não verificado"
  });

  useEffect(() => {
    if (!session.apiKey) return;
    void checkHealth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session.apiKey]);

  async function checkHealth() {
    setHealth({ status: "loading", text: "Verificando..." });
    const [saude, prontidao] = await Promise.all([
      apiRequest<Record<string, unknown>>("/saude"),
      apiRequest<Record<string, unknown>>("/prontidao")
    ]);

    if (saude.ok && prontidao.ok) {
      setHealth({ status: "success", text: "API operacional" });
      return;
    }

    setHealth({
      status: "error",
      text: `Falha: /saude ${saude.status || "offline"} · /prontidao ${prontidao.status || "offline"}`
    });
  }

  if (!session.apiKey) {
    return (
      <main className="page">
        <section className="empty-state">
          <h1>Você ainda não configurou uma API key.</h1>
          <p>Entre no portal para testar os endpoints protegidos.</p>
          <button className="primary" onClick={() => navigate("login")}>
            Configurar acesso
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="page dashboard">
      <section className="dashboard-top">
        <div>
          <span className="eyebrow">Console</span>
          <h1>Olá{session.company ? `, ${session.company}` : ""}.</h1>
          <p>Gerencie acesso, teste endpoints e acompanhe o status operacional da API.</p>
        </div>
        <button className="ghost" onClick={onLogout}>Sair</button>
      </section>

      <section className="grid four">
        <StatusCard label="Status" value={health.text} state={health.status} action={checkHealth} />
        <InfoCard label="Base URL" value={DISPLAY_API_BASE_URL} />
        <InfoCard label="API key" value={maskKey(session.apiKey)} />
        <InfoCard label="Plano" value="Essencial / simulado" />
      </section>

      <section className="dashboard-grid">
        <ApiPlayground apiKey={session.apiKey} />
        <aside className="side-panel">
          <div className="panel">
            <h3>Consumo do mês</h3>
            <div className="usage-bar">
              <span style={{ width: "37%" }} />
            </div>
            <p><strong>37%</strong> da quota estimada usada.</p>
            <small>
              Este bloco está pronto para conectar em um futuro endpoint
              <code> GET /v1/portal/usage</code>.
            </small>
          </div>

          <div className="panel">
            <h3>Chave local</h3>
            <p>{maskKey(session.apiKey)}</p>
            <button
              className="secondary full"
              onClick={() => {
                const next = { ...session, apiKey: "" };
                setSession(next);
                saveSession(next);
              }}
            >
              Trocar chave
            </button>
          </div>

          <div className="panel">
            <h3>Upgrade comercial</h3>
            <p>
              Libere Prata para dados padronizados ou Enterprise Técnico para Bronze auditável.
            </p>
            <button className="primary full" onClick={() => navigate("pricing")}>
              Ver planos
            </button>
          </div>
        </aside>
      </section>
    </main>
  );
}

function ApiPlayground({ apiKey }: { apiKey: string }) {
  const protectedEndpoints = endpointCatalog.filter((endpoint) => endpoint.method === "GET");
  const [path, setPath] = useState(protectedEndpoints[3]?.samplePath || "/v1/operadoras");
  const [status, setStatus] = useState<ApiState>("idle");
  const [result, setResult] = useState<string>("");

  const curl = useMemo(() => {
    return `curl "${DISPLAY_API_BASE_URL}${path}"${apiKey ? ` \\\n  -H "X-API-Key: ${maskKey(apiKey)}"` : ""}`;
  }, [path, apiKey]);

  async function run() {
    setStatus("loading");
    setResult("");
    const response = await apiRequest(path, apiKey);
    setStatus(response.ok ? "success" : "error");
    setResult(
      JSON.stringify(
        {
          status: response.status,
          elapsedMs: response.elapsedMs,
          ok: response.ok,
          error: response.error,
          data: response.data
        },
        null,
        2
      )
    );
  }

  return (
    <section className="playground">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Live tester</span>
          <h2>Teste sua API sem sair do portal.</h2>
        </div>
        <button className="primary" disabled={status === "loading"} onClick={run}>
          {status === "loading" ? "Executando..." : "Executar GET"}
        </button>
      </div>

      <label>
        Endpoint
        <select value={path} onChange={(event) => setPath(event.target.value)}>
          {protectedEndpoints.map((endpoint) => (
            <option key={endpoint.samplePath} value={endpoint.samplePath}>
              {endpoint.samplePath}
            </option>
          ))}
        </select>
      </label>

      <label>
        Caminho customizado
        <input value={path} onChange={(event) => setPath(event.target.value)} />
      </label>

      <CodeBlock title="Requisição" code={curl} />

      <div className={`result-box ${status}`}>
        <div>
          <strong>Resposta</strong>
          <span>{status === "idle" ? "Aguardando execução" : status}</span>
        </div>
        <pre>{result || "Clique em Executar GET para testar."}</pre>
      </div>
    </section>
  );
}

function StatusCard({
  label,
  value,
  state,
  action
}: {
  label: string;
  value: string;
  state: ApiState;
  action: () => void;
}) {
  return (
    <article className={`stat-card ${state}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <button onClick={action}>Atualizar</button>
    </article>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function CodeBlock({ title, code }: { title: string; code: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return (
    <div className="code-block">
      <div>
        <strong>{title}</strong>
        <button onClick={copy}>{copied ? "Copiado" : "Copiar"}</button>
      </div>
      <pre>{code}</pre>
    </div>
  );
}

function Footer() {
  return (
    <footer className="footer">
      <div>
        <strong>HealthIntel Suplementar</strong>
        <p>Dados públicos da ANS como infraestrutura de API comercial.</p>
      </div>
      <div>
        <span>Produto</span>
        <button onClick={() => navigate("pricing")}>Planos</button>
        <button onClick={() => navigate("docs")}>Documentação</button>
      </div>
    </footer>
  );
}
