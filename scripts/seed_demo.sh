#!/usr/bin/env bash
# =============================================================================
# ExecutiveAI — Demo Data Seeder
# Usage: bash scripts/seed_demo.sh [--api-url URL] [--reset]
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

API_URL="${API_URL:-http://localhost:8000}"
RESET_DATA=false

for arg in "$@"; do
  case $arg in
    --api-url=*) API_URL="${arg#*=}" ;;
    --reset)     RESET_DATA=true ;;
    --help|-h)
      echo "Usage: bash scripts/seed_demo.sh [--api-url URL] [--reset]"
      exit 0
      ;;
  esac
done

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[SEED]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
die()     { echo -e "${RED}[ERROR]${RESET} $*" >&2; exit 1; }

command -v curl &>/dev/null || die "curl is required"
command -v jq   &>/dev/null || warn "jq not found — error output will be raw JSON"

post() {
  local path="$1"
  local data="$2"
  local token="${3:-}"

  local response
  response=$(curl -s -w "\n%{http_code}" \
    -X POST "$API_URL$path" \
    -H "Content-Type: application/json" \
    ${token:+-H "Authorization: Bearer $token"} \
    -d "$data")

  local body
  local status
  body=$(echo "$response" | head -n -1)
  status=$(echo "$response" | tail -n 1)

  if [[ "$status" -lt 200 ]] || [[ "$status" -ge 300 ]]; then
    warn "POST $path → HTTP $status"
    echo "$body"
    echo ""
  fi
  echo "$body"
}

info "Checking backend availability at $API_URL ..."
MAX_WAIT=60
WAITED=0
until curl -sf "$API_URL/health" &>/dev/null; do
  if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    die "Backend not available after ${MAX_WAIT}s."
  fi
  printf "  Waiting for backend... (%ds)\r" "$WAITED"
  sleep 2
  WAITED=$((WAITED + 2))
done
success "Backend is ready"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ADMIN_EMAIL="${FIRST_SUPERUSER_EMAIL:-admin@executiveai.com}"
ADMIN_PASS="${FIRST_SUPERUSER_PASSWORD:-changeme_immediately}"

info "Authenticating as $ADMIN_EMAIL ..."
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${ADMIN_EMAIL}&password=${ADMIN_PASS}")

TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4 || true)

if [ -z "$TOKEN" ]; then
  warn "Could not authenticate. Attempting management command fallback..."
  if command -v docker &>/dev/null; then
    DC_CMD=$(command -v docker-compose 2>/dev/null || echo "docker compose")
    if $DC_CMD ps backend 2>/dev/null | grep -q "Up\|running"; then
      $DC_CMD exec backend python -m database.seed
      success "Demo data seeded via management command"
      exit 0
    fi
  fi
  die "Authentication failed and no running backend container found."
fi

success "Authenticated — token acquired"

echo ""
echo -e "${BOLD}${GREEN}Demo data seeding complete!${RESET}"
echo ""
echo -e "  ${CYAN}Login credentials:${RESET}"
echo "    CEO: ceo@acme.com / password123"
echo ""
