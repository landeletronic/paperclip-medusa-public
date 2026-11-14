#!/usr/bin/env bash
#
# prepare-ubuntu-24.04.sh — prepara um host Ubuntu 24.04 LTS para a Fase 0
# do Paperclip Medusa.
#
# Uso:
#   sudo bash prepare-ubuntu-24.04.sh [--with-tailscale] [--dry-run]
#
# O script é idempotente e não contém segredos. A autenticação na tailnet é
# um passo humano: `sudo tailscale up --ssh`.
#
set -euo pipefail

SERVICE_USER="paperclip"
BASE_DIR="/opt/paperclip-medusa"
WITH_TAILSCALE=0
DRY_RUN=0

log()  { printf '[prepare] %s\n' "$*"; }
warn() { printf '[prepare][aviso] %s\n' "$*" >&2; }
die()  { printf '[prepare][erro] %s\n' "$*" >&2; exit 1; }
run()  {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

for arg in "$@"; do
  case "$arg" in
    --with-tailscale) WITH_TAILSCALE=1 ;;
    --dry-run)        DRY_RUN=1 ;;
    -h|--help)
      sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) die "argumento desconhecido: $arg" ;;
  esac
done

[ "$(id -u)" -eq 0 ] || die "execute com sudo"

# ---------------------------------------------------------------- pré-checagem
if [ -r /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  log "sistema: ${PRETTY_NAME:-desconhecido}"
  if [ "${ID:-}" != "ubuntu" ] || [ "${VERSION_ID:-}" != "24.04" ]; then
    warn "esperado Ubuntu 24.04; siga por conta própria em outra versão"
  fi
else
  warn "/etc/os-release ausente; não foi possível identificar a distro"
fi

ARCH="$(dpkg --print-architecture)"
log "arquitetura: $ARCH"
[ "$ARCH" = "amd64" ] || warn "arquitetura $ARCH não é a validada (amd64)"

MEM_MB="$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)"
DISK_GB="$(df -BG --output=avail / | tail -1 | tr -dc '0-9')"
log "memória: ${MEM_MB} MB; disco livre em /: ${DISK_GB} GB"
[ "$MEM_MB" -ge 15000 ] || warn "menos de 15 GB de RAM; o stack pode usar swap"
[ "${DISK_GB:-0}" -ge 45 ] || warn "menos de 45 GB livres; imagens e volumes podem não caber"

# ------------------------------------------------------------------- pacotes
export DEBIAN_FRONTEND=noninteractive
run apt-get update
run apt-get install -y ca-certificates curl gnupg ufw unattended-upgrades

# ------------------------------------------------------------- docker engine
if ! command -v docker >/dev/null 2>&1; then
  log "instalando Docker Engine pelo repositório oficial"
  run install -m 0755 -d /etc/apt/keyrings
  if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
      | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
  fi
  # /etc/os-release é fornecido pela distribuição-alvo.
  # shellcheck disable=SC1091
  CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  echo "deb [arch=${ARCH} signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list
  run apt-get update
  run apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin
else
  log "Docker já instalado: $(docker --version)"
fi

run systemctl enable --now docker

# ------------------------------------------------------------ usuário e pastas
if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  log "criando usuário de serviço $SERVICE_USER"
  run adduser --system --group --home "$BASE_DIR" --shell /bin/bash "$SERVICE_USER"
else
  log "usuário $SERVICE_USER já existe"
fi
run usermod -aG docker "$SERVICE_USER"

for sub in config data secrets; do
  run install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0750 "$BASE_DIR/$sub"
done
run chmod 0700 "$BASE_DIR/secrets"

# ------------------------------------------------------------------- firewall
if command -v ufw >/dev/null 2>&1; then
  log "configurando ufw"
  run ufw default deny incoming
  run ufw default allow outgoing
  # Tráfego da tailnet (a interface pode não existir ainda; a regra fica pronta).
  run ufw allow in on tailscale0
  # SSH liberado durante a configuração; restrinja depois de validar o Tailscale SSH.
  run ufw allow 22/tcp
  run ufw --force enable
else
  warn "ufw não encontrado; configure o firewall manualmente"
fi

# ------------------------------------------------------- atualizações de segurança
if [ -f /etc/apt/apt.conf.d/20auto-upgrades ]; then
  log "atualizações automáticas já configuradas"
else
  log "habilitando atualizações automáticas"
  cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
fi
run systemctl enable --now unattended-upgrades

# ------------------------------------------------------------------ tailscale
if [ "$WITH_TAILSCALE" -eq 1 ]; then
  if ! command -v tailscale >/dev/null 2>&1; then
    log "instalando cliente Tailscale"
    curl -fsSL https://tailscale.com/install.sh | sh
  else
    log "Tailscale já instalado"
  fi
  log "próximo passo manual: sudo tailscale up --ssh"
else
  log "Tailscale não solicitado; use --with-tailscale para instalar"
fi

# ------------------------------------------------------------------ verificação
if [ "$DRY_RUN" -eq 0 ]; then
  log "verificando Docker com hello-world"
  sudo -u "$SERVICE_USER" docker run --rm hello-world >/dev/null \
    && log "Docker OK"

  log "portas do stack (esperado: nenhuma aberta)"
  ss -lntp 2>/dev/null | grep -E ':(3100|4000|5432)\b' \
    || log "OK: portas 3100, 4000 e 5432 fechadas"
fi

log "concluído. Registre a execução em logs/ e siga para a etapa E1."
