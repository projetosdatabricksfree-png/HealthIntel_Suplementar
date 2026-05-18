const STATS = [
  { value: '743', label: 'Operadoras (CADOP)', sub: 'Cadastro ANS · set/2025' },
  { value: '50,8M', label: 'Vidas (SIB)', sub: 'Beneficiários agregados' },
  { value: '351k', label: 'Estabelecimentos (CNES)', sub: 'Rede por município/UF' },
  { value: '/v1', label: 'API versionada', sub: 'Janela de deprecação anunciada' },
];

export function StatsStrip() {
  return (
    <section className="stats" data-screen-label="stats">
      <div className="container">
        <div className="stats__grid">
          {STATS.map((s) => (
            <div key={s.label} className="stat">
              <div className="stat__value">{s.value}</div>
              <div className="stat__label">{s.label}</div>
              <div className="stat__sub">{s.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
