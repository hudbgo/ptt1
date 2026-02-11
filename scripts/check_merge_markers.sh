#!/usr/bin/env bash
set -euo pipefail

if rg -n "^<<<<<<<|^=======|^>>>>>>>" -S .; then
  echo "❌ Se detectaron marcadores de conflicto sin resolver."
  exit 1
fi

echo "✅ No hay marcadores de conflicto en el repositorio."
