#!/usr/bin/env bash
# ============================================================
#  Elecciones Perú 2026 — Script de setup / actualización
#  Uso:  bash setup.sh          (setup completo)
#        bash setup.sh --quick  (solo migrate + collectstatic)
# ============================================================
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓ $1${NC}"; }
info() { echo -e "${YELLOW}→ $1${NC}"; }
fail() { echo -e "${RED}✗ $1${NC}"; exit 1; }

QUICK=false
[[ "${1:-}" == "--quick" ]] && QUICK=true

# ── Entorno virtual ──────────────────────────────────────────
if [[ ! -d "venv" ]]; then
    info "Creando entorno virtual..."
    python3 -m venv venv
    ok "Entorno virtual creado"
fi

source venv/bin/activate
ok "Entorno virtual activado"

# ── Dependencias ─────────────────────────────────────────────
if [[ "$QUICK" == false ]]; then
    info "Instalando dependencias..."
    pip install -r requirements.txt --quiet
    ok "Dependencias instaladas"
fi

# ── Migraciones ──────────────────────────────────────────────
info "Aplicando migraciones..."
python manage.py migrate --run-syncdb
ok "Migraciones aplicadas"

# ── Datos ────────────────────────────────────────────────────
if [[ "$QUICK" == false ]]; then
    info "Importando candidatos desde JSON..."
    python manage.py import_json
    ok "Candidatos importados"

    info "Normalizando posiciones políticas..."
    python manage.py normalize_positions
    ok "Posiciones normalizadas"

    info "Cargando preguntas del quiz..."
    python manage.py load_quiz --reset
    ok "Quiz cargado"
fi

# ── Archivos estáticos ───────────────────────────────────────
info "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear -v 0 2>/dev/null || \
python manage.py collectstatic --noinput -v 0
ok "Archivos estáticos listos"

# ── Verificación ─────────────────────────────────────────────
info "Verificando configuración..."
python manage.py check
ok "Todo en orden"

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  🗳️  Elecciones Perú 2026 — Listo!  ${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

