#!/bin/bash
# ⚠️  DEPRECADO — El deploy se maneja via Coolify + GitHub Actions CI
#    Mantenido solo como referencia/fallback manual.
#    Usar: git push origin main  → CI corre → webhook gatilla rebuild en Coolify
set -e

if [ -z "$1" ]; then
  echo "Uso: $0 <usuario@ip-del-servidor>"
  echo "Ej:  $0 root@161.153.14.37"
  echo ""
  echo "⚠️  DEPRECADO: usa Coolify + GitHub Actions en su lugar"
  exit 1
fi

SERVER="$1"
REMOTE_DIR="/opt/eit-app"

echo "▶️  Conectando a $SERVER..."
ssh "$SERVER" bash -s <<EOF
  set -e
  cd $REMOTE_DIR

  echo "📥 Pull de últimos cambios..."
  git pull origin main

  echo "🐳 Reconstruyendo imagen Docker..."
  docker compose -f docker-compose.prod.yml build

  echo "🔄 Reiniciando contenedor..."
  docker compose -f docker-compose.prod.yml down
  docker compose -f docker-compose.prod.yml up -d

  echo "🧹 Limpiando imágenes viejas..."
  docker image prune -f

  echo "✅ Deploy completado"
EOF

echo "✅ Hecho"
