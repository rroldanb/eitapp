#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Uso: $0 <usuario@ip-del-servidor>"
  echo "Ej:  $0 root@161.153.14.37"
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
  docker compose build

  echo "🔄 Reiniciando contenedor..."
  docker compose down
  docker compose up -d

  echo "🧹 Limpiando imágenes viejas..."
  docker image prune -f

  echo "✅ Deploy completado"
EOF

echo "✅ Hecho"
