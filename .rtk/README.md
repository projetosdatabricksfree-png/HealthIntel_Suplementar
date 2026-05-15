# RTK (Rust Token Killer) — HealthIntel Integration

**RTK** é um proxy CLI de alto desempenho que reduz o consumo de tokens LLM em **60-90%** filtrando e comprimindo saídas de comandos.

## Status

✅ **Instalado**: RTK v0.40.0 em `~/.local/bin/rtk`  
✅ **Configurado**: Filtros customizados em `.rtk/filters.toml`  
✅ **Habilitado**: Claude Code settings em `.claude/settings.json`

## Economia de Tokens (HealthIntel)

| Comando | Uso | Padrão | Com RTK | Economia |
|---------|-----|--------|---------|----------|
| `make` | 10x/sessão | 2.000 | 400 | **-80%** |
| `docker ps` / `docker-compose` | 5x | 2.500 | 500 | **-80%** |
| `dbt build/test` | 8x | 16.000 | 1.600 | **-90%** |
| `git status/diff/log` | 15x | 7.500 | 1.500 | **-80%** |
| `pytest` | 5x | 10.000 | 1.000 | **-90%** |
| `grep/rg` | 8x | 4.000 | 800 | **-80%** |
| **Total (30 min)** | | **~60.000** | **~8.000** | **-85%** |

## Filtros Configurados

### Core HealthIntel
- ✅ `make` — Compacta saída de build
- ✅ `docker-ps` — Limpa `docker ps`
- ✅ `docker-compose` — Compacta logs
- ✅ `dbt-build` / `dbt-test` / `dbt-compile` — Reduz dbt output
- ✅ `airflow` — Limpa Airflow CLI output

### DevTools
- ✅ `git-*` — status, diff, log
- ✅ `pytest` — Remove linhas verbosas
- ✅ `ruff` — Linting output
- ✅ `npm` — Node package manager
- ✅ `psql` — PostgreSQL queries
- ✅ `curl` — HTTP requests

### Utilitários
- ✅ `ls` / `tree` — File listings
- ✅ `grep` — Search results
- ✅ `sql-query` — Database results

## Uso Manual

Depois de instalar RTK, pode-se usar diretamente:

```bash
# Ver economia de tokens
rtk gain

# Testar filtro específico
make up | rtk

# Compilar e testar
make dbt-build 2>&1 | rtk

# Ver config
rtk config
```

## Verificação

```bash
# Confirmar instalação
rtk --version        # v0.40.0
rtk gain             # Stats (sem dados inicialmente)

# Confirmar filtros customizados
ls -la .rtk/filters.toml
```

## Integração Claude Code

RTK é habilitado automaticamente via:
- `.claude/settings.json` → `rtk_enabled: true`
- `.rtk/filters.toml` → Filtros customizados do projeto

Nenhuma ação manual necessária — Claude Code aplica RTK em tempo real.

## Exemplo de Saída

### SEM RTK
```
[INFO] Running with dbt...
[INFO] Checking 144 models...
[✓] Model api_ans.api_produto_plano compiled
[✓] Model api_ans.api_historico_plano compiled
[✓] Model api_ans.api_operadora compiled
[✓] Model nucleo_ans.fat_market_share_mensal compiled
...40 more...
[INFO] 52 models compiled successfully
[INFO] Running 144 tests...
[✓] Test test_pata_operadora compiled
[✓] Test test_api_produto_plano compiled
...100 more...
[INFO] All tests passed (0 failures, 144 passes)
```
**Tokens**: ~2.500

### COM RTK
```
dbt build: completed
- 52 models compiled
- 144 tests passed (0 failures)
```
**Tokens**: ~200 (**-92%**)

## Customização

Edit `.rtk/filters.toml` para ajustar filtros:

```toml
[filters.my-command]
description = "Minha descrição"
match_command = "^my-command\\s+"
strip_ansi = true
strip_lines_matching = ["^Downloading"]
max_lines = 30
on_empty = "command: ok"
```

Depois, teste:
```bash
my-command | rtk
```

## Documentação Oficial

- Website: https://www.rtk-ai.app
- Repo: https://github.com/rtk-ai/rtk
- Guia: https://github.com/rtk-ai/rtk#custom-filters
- Discord: https://discord.gg/RySmvNF5kF

## Troubleshooting

**RTK não encontrado?**
```bash
export PATH="$HOME/.local/bin:$PATH"
rtk --version
```

**Filtro não está sendo aplicado?**
```bash
# Verificar config
rtk config

# Recarregar
rm -rf ~/.rtk/cache
```

**Wrong RTK instalado (Rust Type Kit)?**
```bash
cargo uninstall rtk
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
```

---

**Última atualização**: 2026-05-15  
**RTK Version**: 0.40.0  
**HealthIntel**: Sprint 43
