#!/usr/bin/env bash
# Regenera el repositorio público de showcase a partir del estado actual de `main`.
#
# Publica un único commit, sin historial, con exactamente los archivos versionados en HEAD.
# El repositorio privado (este) no se modifica.
#
# Uso:
#   scripts/publicar-showcase.sh            # prueba: arma el snapshot y muestra qué se publicaría
#   scripts/publicar-showcase.sh --push     # publica (pide confirmación; reemplaza el contenido remoto)
#   scripts/publicar-showcase.sh --push --yes   # publica sin preguntar
#
# Variables opcionales:
#   SHOWCASE_REPO   repositorio destino (por defecto: quietforz87/iaChallenge-showcase)
#   SHOWCASE_MSG    archivo con un mensaje de commit propio (por defecto se genera solo)
#
# Requisitos: git, gh autenticado con la cuenta dueña del repositorio destino (scope `repo`).
set -euo pipefail

SHOWCASE_REPO="${SHOWCASE_REPO:-quietforz87/iaChallenge-showcase}"
PUSH=0
YES=0
for arg in "$@"; do
  case "$arg" in
    --push) PUSH=1 ;;
    --yes) YES=1 ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $arg" >&2; exit 2 ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# 1. Validaciones: rama main y sin cambios pendientes.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "main" ]]; then
  echo "Error: hay que estar en la rama main (actual: $BRANCH)." >&2; exit 1
fi
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: hay cambios sin commitear. Commiteá o descartá antes de publicar." >&2
  git status --short >&2; exit 1
fi
if git rev-parse --verify -q origin/main >/dev/null && [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]]; then
  echo "Aviso: main local y origin/main difieren; se publica el main local ($(git rev-parse --short HEAD))." >&2
fi

NAME="$(git config user.name)"
EMAIL="$(git config user.email)"
SOURCE_SHA="$(git rev-parse --short HEAD)"

# 2. Snapshot de HEAD en una carpeta temporal.
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git archive HEAD | tar -x -C "$WORK"

# 3. Mensaje del commit.
MSG="$WORK.msg"
trap 'rm -rf "$WORK" "$MSG"' EXIT
if [[ -n "${SHOWCASE_MSG:-}" ]]; then
  cp "$SHOWCASE_MSG" "$MSG"
else
  {
    echo "Propuestas técnicas de IA — Célula IA (showcase)"
    echo
    echo "Espacio de trabajo de preventa de la Célula IA: cada escenario de cliente se"
    echo "convierte en una propuesta técnica con arquitectura, alcance, estimación,"
    echo "riesgos y supuestos, pensada para el cliente y para el equipo de delivery."
    echo
    echo "Contenido:"
    echo "- CLAUDE.md: rol, estructura de directorios, convenciones y uso de skills."
    echo "- templates/: plantillas de propuesta, supuestos, riesgos, ADR y diagramas."
    echo "- escenarios/:"
    for dir in "$WORK"/escenarios/*/; do
      [[ -d "$dir" ]] || continue
      slug="$(basename "$dir")"
      title="$(grep -m1 '^# ' "$dir/00-brief/escenario.md" 2>/dev/null | sed 's/^# //')"
      echo "  - ${slug}${title:+: $title}"
    done
    echo "- .claude/skills/: skills usadas en el trabajo."
    echo
    echo "Versión publicada sin historial; el historial de trabajo se mantiene en un"
    echo "repositorio privado."
  } > "$MSG"
fi

# 4. Repositorio de un solo commit.
git -C "$WORK" init -q -b main
git -C "$WORK" config user.name "$NAME"
git -C "$WORK" config user.email "$EMAIL"
git -C "$WORK" add -A
git -C "$WORK" commit -q -F "$MSG"

echo "Snapshot de main ($SOURCE_SHA): $(git -C "$WORK" ls-files | wc -l) archivos, autor $NAME <$EMAIL>"
echo "Destino: https://github.com/$SHOWCASE_REPO"
echo "----- mensaje del commit -----"
cat "$MSG"
echo "------------------------------"

if [[ "$PUSH" -eq 0 ]]; then
  echo "Prueba terminada: no se publicó nada. Para publicar, volvé a correr con --push."
  exit 0
fi

# 5. Publicación: reemplaza el contenido del repositorio remoto (push forzado).
if [[ "$YES" -eq 0 ]]; then
  read -r -p "Esto REEMPLAZA el contenido público de $SHOWCASE_REPO. ¿Continuar? [s/N] " answer
  [[ "$answer" =~ ^[sS]$ ]] || { echo "Cancelado."; exit 1; }
fi
git -C "$WORK" remote add origin "https://github.com/$SHOWCASE_REPO.git"
git -C "$WORK" push --force -u origin main
echo "Publicado: https://github.com/$SHOWCASE_REPO"
