#!/usr/bin/env bash
# ============================================================
#  Elecciones Peru 2026 — Script de setup / actualizacion
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

# -- Git pull ------------------------------------------------
info "Actualizando codigo..."
git pull || true
ok "Codigo actualizado"

# -- Entorno virtual -----------------------------------------
if [[ ! -d "venv" ]]; then
    info "Creando entorno virtual..."
    python3 -m venv venv
    ok "Entorno virtual creado"
fi

source venv/bin/activate 2>/dev/null || true
ok "Entorno virtual activado"

# -- Dependencias --------------------------------------------
if [[ "$QUICK" == false ]]; then
    info "Instalando dependencias..."
    pip install -r requirements.txt --quiet
    ok "Dependencias instaladas"
fi

# -- Migraciones ---------------------------------------------
info "Aplicando migraciones..."
python manage.py migrate --run-syncdb
ok "Migraciones aplicadas"

# -- Datos ---------------------------------------------------
if [[ "$QUICK" == false ]]; then
    info "Importando candidatos desde JSON..."
    python manage.py import_json || true
    ok "Candidatos importados"

    info "Normalizando posiciones politicas..."
    python manage.py normalize_positions || true
    ok "Posiciones normalizadas"

    info "Cargando preguntas del quiz..."
    python manage.py load_quiz --reset || true
    ok "Quiz cargado"

    # -- Limpiar duplicados ----------------------------------
    info "Limpiando duplicados si existen..."
    python manage.py shell -c "
from candidatos.models import Candidato
eliminados = 0

# Perez Tello duplicado
pt_dup = Candidato.objects.filter(nombre__icontains='Perez Tello De Rodriguez').first()
if pt_dup:
    pt_orig = Candidato.objects.filter(nombre__icontains='rez Tello').exclude(id=pt_dup.id).first()
    if pt_orig:
        pt_orig.hoja_vida_jne = pt_dup.hoja_vida_jne
        pt_orig.rol_plancha = 'presidente'
        pt_orig.save()
        pt_dup.delete()
        eliminados += 1
        print(f'  Duplicado eliminado: {pt_dup.nombre} -> fusionado con {pt_orig.nombre}')

# Valderrama duplicado
v_dup = Candidato.objects.filter(nombre__icontains='Pitter').filter(nombre__icontains='Valderrama').first()
if v_dup:
    v_orig = Candidato.objects.filter(nombre__icontains='Valderrama').exclude(id=v_dup.id).first()
    if v_orig:
        v_orig.hoja_vida_jne = v_dup.hoja_vida_jne
        v_orig.rol_plancha = 'presidente'
        v_orig.save()
        v_dup.delete()
        eliminados += 1
        print(f'  Duplicado eliminado: {v_dup.nombre} -> fusionado con {v_orig.nombre}')

if eliminados == 0:
    print('  Sin duplicados, todo limpio.')
print(f'  Presidentes: {Candidato.objects.filter(rol_plancha=\"presidente\").count()}')
"
    ok "Duplicados limpiados"

    # -- Datos JNE (rol_plancha + hoja de vida + planes) -----
    info "Importando datos JNE (candidatos_jne.json)..."
    python manage.py setup_produccion --crear-faltantes
    ok "Datos JNE importados"

    # -- Congresales (requiere reporte_if.xlsx) ---------------
    if [[ -f "reporte_if.xlsx" ]]; then
        info "Importando congresales desde reporte_if.xlsx..."
        python manage.py importar_congresales --limpiar
        ok "Congresales importados"

        info "Importando transparencia ONPE..."
        python manage.py importar_onpe
        ok "Transparencia ONPE importada"
    else
        echo -e "${YELLOW}  ! reporte_if.xlsx no encontrado — congresales y transparencia ONPE omitidos${NC}"
        echo -e "${YELLOW}    Sube reporte_if.xlsx a la raiz del proyecto y vuelve a ejecutar${NC}"
    fi
fi

# -- Archivos estaticos --------------------------------------
info "Recopilando archivos estaticos..."
python manage.py collectstatic --noinput --clear -v 0 2>/dev/null || \
python manage.py collectstatic --noinput -v 0
ok "Archivos estaticos listos"

# -- Verificacion --------------------------------------------
info "Verificando configuracion..."
python manage.py check
ok "Django check OK"

# -- Verificacion de datos -----------------------------------
echo ""
echo -e "${YELLOW}=== VERIFICACION DE DATOS ===${NC}"
python manage.py shell -c "
from candidatos.models import Candidato, CandidatoCongresal, Partido
from django.db.models import Count

for r in Candidato.objects.values('rol_plancha').annotate(n=Count('id')).order_by('rol_plancha'):
    print(f\"  {r['rol_plancha'] or '(sin rol)':>12}: {r['n']}\")

total_cong = CandidatoCongresal.objects.count()
partidos_onpe = Partido.objects.filter(transparencia_onpe_total_candidatos__gt=0).count()
print(f'  congresales: {total_cong}')
print(f'  partidos ONPE: {partidos_onpe}')

n_pres = Candidato.objects.filter(rol_plancha='presidente').count()
print()
if n_pres == 36:
    print('  OK: 36 candidatos presidenciales')
else:
    print(f'  ATENCION: {n_pres} presidentes (esperado: 36)')

pres_sin_vps = []
for p in Candidato.objects.filter(rol_plancha='presidente').select_related('partido'):
    vps = Candidato.objects.filter(partido=p.partido, rol_plancha__in=['vp1','vp2']).count()
    if vps == 0:
        pres_sin_vps.append(f'{p.nombre} ({p.partido.siglas})')
if pres_sin_vps:
    print(f'  ATENCION: {len(pres_sin_vps)} presidentes sin VPs:')
    for x in pres_sin_vps:
        print(f'    - {x}')
else:
    print('  OK: Todos los presidentes tienen vicepresidentes')
"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  Elecciones Peru 2026 — Listo!       ${NC}"
echo -e "${GREEN}  Recuerda dar RELOAD a la web app     ${NC}"
echo -e "${GREEN}=======================================${NC}"
