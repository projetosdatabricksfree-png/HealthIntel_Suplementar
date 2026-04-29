# Política de artefatos gerados

## Objetivo

Reduzir drift documental, ruído de revisão e custo de contexto mantendo no git
apenas código-fonte, documentação curada e artefatos realmente necessários para
auditoria.

## Regra geral

Artefatos reproduzíveis por comando não devem ser versionados por padrão.

Exemplos:

- `target/` do dbt;
- `dbt_packages/`;
- `node_modules/`;
- caches de build frontend;
- manifests e catálogos dbt exportados automaticamente;
- HTML de documentação gerado sem curadoria manual.

## Exceções permitidas

Um artefato gerado pode ser versionado somente quando todos os critérios abaixo
forem verdadeiros:

- existe justificativa de auditoria ou release;
- a versão do artefato está vinculada a uma tag ou release;
- há comando documentado para reproduzir o conteúdo;
- o arquivo não substitui a documentação curada em Markdown.

## Estado atual

O repositório ainda possui snapshots versionados em `docs/dbt_*`. Eles devem ser
tratados como snapshots históricos. Novas gerações automáticas devem ficar fora
do git, usando `.gitignore` e armazenamento externo quando houver necessidade de
retenção.

## Procedimento recomendado

Para documentação dbt local:

```bash
cd healthintel_dbt
DBT_LOG_PATH=/tmp/healthintel_dbt_logs DBT_TARGET_PATH=/tmp/healthintel_dbt_target dbt docs generate
```

Para publicar evidência de release, preferir anexar o artefato à release ou
armazenar em bucket operacional, registrando o link no changelog.

## Critério de aceite

- `git status --short` não deve listar `node_modules/`, `target/`,
  `dbt_packages/` ou novos `docs/dbt_*`.
- PRs não devem incluir grandes arquivos gerados sem justificativa explícita.
