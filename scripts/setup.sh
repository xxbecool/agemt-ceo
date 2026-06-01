#!/usr/bin/env bash
# =============================================================================
# ExecutiveAI — Full Setup Script
# Usage: bash scripts/setup.sh [--skip-seed] [--skip-ssl]
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

SKIP_SEED=false
SKIP_SSL=false
for arg in "$@"; do
  case $arg in
    --skip-seed) SKIP_SEED=true ;;
    --skip-ssl)  SKIP_SSL=true  ;;
    --help|-h)
      echo "Usage: bash scripts/setup.sh [--skip-seed] [--skip-ssl]"
      exit 0
      ;;
  esac
done

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
die()     { error "$*"; exit 1; }

section() {
  echo ""
  echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════${RESET}"
  echo -e "${BOLD}${CYAN}  $*${RESET}"
  echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════${RESET}"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo -e "${BOLD}${CYAN}"
echo "  ╔═══════════════════════════════════╗"
echo "  ║     ExecutiveAI Setup Script      ║"
echo "  ╚═══════════════════════════════════╝"
echo -e "${RESET}"

section "Step 1/6: Checking Prerequisites"

check_command() {
  local cmd=$1
  local name=${2:-$1}
  local install_hint=${3:-"Please install $name"}
  if command -v "$cmd" &>/dev/null; then
    local version
    version=$("$cmd" --version 2>&1 | head -1)
    success "$name found: $version"
  else
    die "$name not found. $install_hint"
  fi
}

check_docker_running() {
  if ! docker info &>/dev/null; then
    die "Docker daemon is not running. Start Docker and retry."
  fi
  success "Docker daemon is running"
}

check_command docker    "Docker"         "Install from https://docs.docker.com/get-docker/"
check_docker_running
check_command git       "Git"            "Install from https://git-scm.com/"

if command -v docker-compose &>/dev/null; then
  DC="docker-compose"
  success "docker-compose (standalone) found"
elif docker compose version &>/dev/null 2>&1; then
  DC="docker compose"
  success "docker compose (plugin) found"
else
  die "Docker Compose not found. Install from https://docs.docker.com/compose/install/"
fi

section "Step 2/6: Environment Configuration"

if [ ! -f ".env" ]; then
  cp .env.example .env
  warn ".env created from .env.example"
  warn "Please review .env and fill in your API keys before continuing."
  echo ""
  echo -e "${YELLOW}  Required values to set in .env:${RESET}"
  echo "    POSTGRES_PASSWORD  — choose a strong password"
  echo "    SECRET_KEY         — run: python3 -c \"import secrets; print(secrets.token_hex(32))\""
  echo "    ANTHROPIC_API_KEY  — get at https://console.anthropic.com/"
  echo ""
  read -r -p "Press Enter when .env is ready, or Ctrl+C to abort... "
else
  success ".env already exists"
fi

section "Step 3/6: Creating Directories"

DIRS=(
  "infrastructure/nginx/ssl"
  "uploads"
  "logs"
  "backups"
)

for dir in "${DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    success "Created: $dir"
  else
    info "Exists: $dir"
  fi
done

if [ "$SKIP_SSL" = false ]; then
  if [ ! -f "infrastructure/nginx/ssl/fullchain.pem" ]; then
    if command -v openssl &>/dev/null; then
      info "Generating self-signed SSL certificate for local development..."
      openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout infrastructure/nginx/ssl/privkey.pem \
        -out    infrastructure/nginx/ssl/fullchain.pem \
        -subj   "/C=US/ST=Dev/L=Local/O=ExecutiveAI/CN=localhost" \
        2>/dev/null
      chmod 600 infrastructure/nginx/ssl/privkey.pem
      success "Self-signed certificate created in infrastructure/nginx/ssl/"
    else
      warn "openssl not found — skipping SSL cert generation."
    fi
  else
    success "SSL certificate already exists"
  fi
else
  info "Skipping SSL setup (--skip-ssl flag)"
fi

section "Step 4/6: Building Docker Images"

info "This may take several minutes on first run..."
$DC build --parallel
success "Docker images built successfully"

section "Step 5/6: Starting Services"

$DC up -d
info "Services started. Waiting for health checks..."

MAX_WAIT=60
WAITED=0
while ! $DC ps postgres 2>/dev/null | grep -q "healthy"; do
  if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    die "PostgreSQL did not become healthy within ${MAX_WAIT}s."
  fi
  printf "  Waiting for PostgreSQL... (%ds)\r" "$WAITED"
  sleep 3
  WAITED=$((WAITED + 3))
done
success "PostgreSQL is healthy"

section "Step 6/6: Database Setup"

info "Running Alembic migrations..."
$DC exec backend alembic upgrade head
success "Migrations applied"

if [ "$SKIP_SEED" = false ]; then
  info "Seeding demo data..."
  bash scripts/seed_demo.sh
  success "Demo data seeded"
else
  info "Skipping seed (--skip-seed flag)"
fi

echo ""
echo -e "${BOLD}${GREEN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║      Setup Complete!                ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${RESET}"
echo -e "  ${CYAN}Frontend  ${RESET}→  http://localhost:3000"
echo -e "  ${CYAN}Backend   ${RESET}→  http://localhost:8000"
echo -e "  ${CYAN}API Docs  ${RESET}→  http://localhost:8000/docs"
echo ""
