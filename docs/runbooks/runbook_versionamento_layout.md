# Runbook — Versionamento de layout

## Objetivo

Criar, aprovar, desativar e reativar versões de layout com governança humana.

## Passos

1. Cadastrar layout no registry.
2. Criar versão.
3. Cadastrar aliases manuais.
4. Validar arquivo candidato.
5. Aprovar versão.
6. Atualizar compatibilidade.
7. Se necessário, desativar ou reativar versão.

## Critério de encerramento

- `layout_versao` em estado correto;
- `historico_mapeamento` persistido;
- arquivo incompatível vai para quarentena;
- reprocessamento possível.

