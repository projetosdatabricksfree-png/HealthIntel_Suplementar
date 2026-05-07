# Acesso SSH à VPS HealthIntel

## Dados da VPS

| Item | Valor |
|------|-------|
| IP | 5.189.160.27 |
| OS | Ubuntu 22.04 LTS |
| Usuario padrao | ubuntu (ou root conforme provedor) |
| Diretorio do projeto | /opt/healthintel |

## Chave SSH autorizada

Fingerprint da chave ed25519 em uso:

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICMy5R/RLbrssHKH/DCjgtY8bNCp+o3SiNmdMArbySES
```

Host: `healthintel-vps-5.189.160.27`

**Esta chave privada nao deve ser versionada. Manter somente na maquina do operador.**

## Conectar

```bash
ssh -i ~/.ssh/healthintel_vps ubuntu@5.189.160.27
```

Ou com alias em `~/.ssh/config`:

```
Host healthintel-vps
    HostName 5.189.160.27
    User ubuntu
    IdentityFile ~/.ssh/healthintel_vps
    ServerAliveInterval 60
```

Depois: `ssh healthintel-vps`

## Adicionar nova chave de acesso

Na VPS, como usuario com permissao sudo:

```bash
# Adicionar chave publica de novo operador
echo "ssh-ed25519 AAAA... operador@maquina" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Verificar
cat ~/.ssh/authorized_keys
```

Registrar aqui (neste arquivo) o fingerprint e nome do operador.

## Operadores com acesso

| Operador | Fingerprint | Data de adicao | Expiracao |
|----------|-------------|----------------|-----------|
| Projetos Databricks | `AAAAC3NzaC1lZDI1NTE5AAAAICMy5R/RLbrssHKH/DCjgtY8bNCp+o3SiNmdMArbySES` | 2026-05-06 | Sem expiracao definida |

## Revogar acesso

```bash
# Editar authorized_keys e remover a linha da chave revogada
nano ~/.ssh/authorized_keys

# Confirmar que a chave nao esta mais presente
grep "fingerprint_da_chave_revogada" ~/.ssh/authorized_keys && echo "AINDA PRESENTE" || echo "OK: removida"
```

## Politica de rotacao

- Rotacionar chaves a cada 12 meses ou quando operador deixar o projeto.
- Ao rotacionar: gerar novo par `ssh-keygen -t ed25519 -C "healthintel-vps-$(date +%Y)"`, adicionar nova chave antes de remover a antiga.
- Registrar a troca neste documento com data.

## Firewall

Apenas as portas abaixo estao abertas na VPS (verificado em 2026-05-06):

| Porta | Protocolo | Servico |
|-------|-----------|---------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP (redirect para HTTPS via Caddy) |
| 443 | TCP | HTTPS (Caddy) |

Todos os outros servicos (PostgreSQL 5432, Redis 6379, MongoDB 27017, Airflow 8088, API 8080) estao ligados a `127.0.0.1` e nao sao acessiveis externamente.

## Verificar regras de firewall

```bash
sudo ufw status verbose
# ou
sudo iptables -L -n | grep -E "ACCEPT|DROP"
```
