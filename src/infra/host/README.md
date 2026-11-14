# Preparação do host — E0 da Fase 0

Runbook para preparar o host da Fase 0 do Paperclip Medusa. O caminho original atende a um host
novo com **Ubuntu 24.04 LTS**; a execução aprovada usa o **host principal com Ubuntu 26.04.1 LTS** e
preserva sua stack Hermes existente.

## Metadados

| Campo | Valor |
|---|---|
| ID | 2026-11-11-plano-fase-0-e0 |
| Data | 2026-11-11 |
| Autor | OpenCode (GPT-5.6 Sol) |
| Tipo | runbook |
| Status | E0 concluída no host principal; trilha de plataforma e plano padrão concluídos |
| Relacionados | [`../../../docs/plans/2026-11-11-plano-fase-0-poc.md`](../../../docs/plans/2026-11-11-plano-fase-0-poc.md) |

## 1. Resultado esperado

Ao final, o host deve:

- rodar Docker Engine e Docker Compose v2;
- ter um usuário de serviço `paperclip` com acesso ao Docker;
- ter `/opt/paperclip-medusa/{config,data,secrets}` com permissões restritas;
- aceitar SSH do administrador e tráfego de serviço apenas pela tailnet;
- receber atualizações de segurança automaticamente;
- **não** expor as portas 5432, 3100 e 4000 fora do host.

## 2. Pré-requisitos

- acesso SSH com `sudo` ao host;
- conta Tailscale criada e um *auth key* ou login interativo disponível;
- nenhum serviço ocupando as portas 3100 e 4000.

### 2.1 Exceção aprovada para o host principal

O primary-host já possuía Docker, Compose, Tailscale, UFW e `unattended-upgrades`. Por isso,
`prepare-ubuntu-24.04.sh` **não deve ser executado nesse host**. Use
`prepare-primary-host-existing-host.sh`, que somente valida os componentes existentes, cria o usuário e os
diretórios do Paperclip e adiciona a regra específica da tailnet.

O usuário aprovou explicitamente a inclusão de `paperclip` no grupo `docker`. Esse grupo concede
privilégio equivalente a root e permite controlar os containers, volumes e segredos da stack
Hermes. Essa decisão é aceitável somente para esta PoC consciente do risco; não representa
isolamento de segurança entre Paperclip e Hermes.

## 3. Verificação inicial

```bash
lsb_release -a          # Ubuntu 24.04.x LTS
uname -m                # x86_64
nproc                   # vCPUs
free -h                 # 16 GB de RAM
df -h /                 # 50 GB+ livres
```

Registre a saída em `logs/commands/`. Se o host não for Ubuntu 24.04, adapte os comandos antes de continuar.

## 4. Execução automatizada

O script é idempotente: pode ser reexecutado sem duplicar usuários, regras ou diretórios.

```bash
scp src/infra/host/prepare-ubuntu-24.04.sh usuario@host:/tmp/
ssh usuario@host
sudo bash /tmp/prepare-ubuntu-24.04.sh --with-tailscale
```

Sem Tailscale (instalação manual depois):

```bash
sudo bash /tmp/prepare-ubuntu-24.04.sh
```

O script **não** contém segredos e não autentica na tailnet; ele apenas instala o cliente. A autenticação é um passo humano:

```bash
sudo tailscale up --ssh
tailscale status
```

### 4.1 host principal já configurado

```bash
scp src/infra/host/prepare-primary-host-existing-host.sh primary-host-jones-hermes:/tmp/
ssh primary-host-jones-hermes \
  'sudo bash /tmp/prepare-primary-host-existing-host.sh'
```

O script específico do primary-host é idempotente e falha fechado se o hostname, Docker, Compose,
Tailscale, UFW ou `unattended-upgrades` não corresponderem ao ambiente esperado. Ele não instala
pacotes, não reinicia Docker/Tailscale, não redefine o UFW e não toca nos containers existentes.

## 5. Passos manuais (quando não usar o script)

### 5.1 Docker Engine

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

### 5.2 Usuário de serviço

```bash
sudo adduser --system --group --home /opt/paperclip-medusa --shell /bin/bash paperclip
sudo usermod -aG docker paperclip
```

### 5.3 Diretórios

```bash
sudo install -d -o paperclip -g paperclip -m 0750 /opt/paperclip-medusa/{config,data,secrets}
sudo chmod 0700 /opt/paperclip-medusa/secrets
```

### 5.4 Firewall

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow in on tailscale0
sudo ufw allow 22/tcp
sudo ufw enable
sudo ufw status verbose
```

> **SSH:** a regra `22/tcp` existe para não bloquear o acesso durante a configuração. Depois de confirmar que `tailscale ssh` funciona, restrinja ou remova essa regra e mantenha o SSH apenas pela tailnet.

**Atenção:** o Docker publica portas contornando o `ufw`. Na Fase 0, todo serviço deve ser publicado em `127.0.0.1` ou apenas em redes internas do Compose. Se precisar publicar em outra interface, use a cadeia `DOCKER-USER`.

### 5.5 Atualizações automáticas

```bash
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 5.6 Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh
```

## 6. Verificação de aceite

```bash
# Docker funcional
sudo -u paperclip docker run --rm hello-world

# Compose v2
sudo -u paperclip docker compose version

# Tailnet
tailscale status
tailscale ip -4

# Nada escutando em 0.0.0.0 nas portas do stack
sudo ss -lntp | grep -E ':(3100|4000|5432)\b' || echo 'OK: portas do stack fechadas'

# Diretórios e permissões
sudo ls -ld /opt/paperclip-medusa /opt/paperclip-medusa/{config,data,secrets}
```

Critérios:

- [ ] `hello-world` executa sem `sudo` para o usuário `paperclip`.
- [ ] `docker compose version` retorna v2.
- [ ] `tailscale status` mostra o host na tailnet.
- [ ] Nenhuma porta do stack escuta fora de `127.0.0.1`.
- [ ] `secrets/` está com modo `0700`.

### Resultado medido no primary-host em 2026-11-11

- Ubuntu 26.04.1 LTS, x86_64, 14 vCPU, 15 GiB de RAM e 831 GB livres;
- Docker 29.9.3 e Compose 5.7.1;
- usuário `paperclip` nos grupos `paperclip,docker`;
- diretórios com modos `0750/0750/0750/0700`;
- Tailscale conectado; regra `Paperclip tailnet` presente no UFW;
- portas 3100, 4000 e 5432 livres;
- `hello-world` executado pelo usuário de serviço;
- 12 containers Hermes preservados;
- oráculo antes e depois: `PASS=265 FAIL=5 WARN=2`, sem regressão da E0.

Os cinco `FAIL` são preexistentes e estão fora do escopo da E0: modelo local usando CPU, dois
smokes do eixo de estudos, backup antigo e retenção pendente. Tailscale SSH não foi habilitado;
o acesso administrativo continua usando a chave SSH já existente.

## 7. Registro

Depois da execução, registre em `logs/`:

- comando executado e código de saída (`logs/commands/`);
- execução do script (`logs/executions/`);
- resultado dos testes de aceite (`logs/tests/`);
- atualização do status de E0 em `logs/tasks/`.

## 8. Reversão

O procedimento genérico instala pacotes e sua reversão deve ser planejada conforme o host.

No primary-host, não remova Docker, Tailscale nem diretórios amplos: esses componentes também pertencem à
stack Hermes. Para reverter apenas a E0 do Paperclip, primeiro confirme que não há dados da E1 ou
posteriores e então remova, de forma explícita, somente a regra `Paperclip tailnet`, o usuário
`paperclip` e `/opt/paperclip-medusa`. A reversão é destrutiva e exige nova confirmação.

O exemplo abaixo aplica-se apenas a um host novo dedicado, nunca ao primary-host:

```bash
sudo systemctl disable --now docker
sudo apt-get remove --purge -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
sudo rm -rf /opt/paperclip-medusa
sudo deluser paperclip
```

Remova também as regras de `ufw` criadas e, se aplicável, o host da tailnet no painel do Tailscale.
