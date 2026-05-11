# Fase 11b: HTTPS, Caddy e Configuração de Domínios

Este documento descreve como configurar o Caddy na VPS para servir o HealthIntel via HTTPS, garantindo o isolamento correto entre o Frontend, API e Grafana.

## ⚠️ Diagnóstico de Bug Comum: "Grafana no Domínio Raiz"

Se ao acessar `https://healthintel.com.br` você for direcionado para a tela de login do **Grafana** em vez do portal, significa que o Caddy está configurado para apontar o domínio raiz diretamente para a porta `:3000` ou `:3001`.

### A Solução
O Caddy deve atuar como o "porteiro" (Edge Proxy), distribuindo o tráfego para os subdomínios corretos.

## Configuração Recomendada

Use o arquivo de exemplo em [Caddyfile.hml.example](../../infra/caddy/Caddyfile.hml.example) como base.

### 1. Preparação na VPS
Instale o Caddy se ainda não o fez:
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### 2. Aplicando a Configuração
1. Edite o arquivo `/etc/caddy/Caddyfile`:
   ```bash
   sudo nano /etc/caddy/Caddyfile
   ```
2. Cole o conteúdo do nosso exemplo, ajustando os subdomínios se necessário.
3. Recarregue o Caddy:
   ```bash
   sudo systemctl reload caddy
   ```

### 3. Estrutura de Roteamento Final
- **https://healthintel.com.br** -> Redireciona para `app.healthintel.com.br`
- **https://app.healthintel.com.br** -> Frontend (Porta 3000)
- **https://api.healthintel.com.br** -> Nginx Gateway (Porta 8080)
- **https://grafana.healthintel.com.br** -> Grafana (Porta 3001)

---
*Documento atualizado em: 2026-05-08*
