#!/bin/bash

echo "Inicializando arquitectura profesional Django..."

APPS_DIR="apps"

mkdir -p $APPS_DIR

create_app_structure () {

APP_NAME=$1

echo "Creando app: $APP_NAME"

python manage.py startapp $APP_NAME

mv $APP_NAME $APPS_DIR/

cd $APPS_DIR/$APP_NAME

# crear estructura modular
mkdir -p models views services serializers

# eliminar archivos default
rm models.py views.py tests.py

# crear init
touch models/__init__.py
touch views/__init__.py
touch services/__init__.py
touch serializers/__init__.py

# archivos base
touch models/base.py
touch services/${APP_NAME}_service.py

cd ../../

}

# Crear apps principales
create_app_structure "proyectos"
create_app_structure "mandantes"
create_app_structure "red_vial"
create_app_structure "usuarios"

# estructura especial para storage
mkdir -p $APPS_DIR/imagenes/services
mkdir -p $APPS_DIR/imagenes/utils

touch $APPS_DIR/imagenes/services/storage_service.py
touch $APPS_DIR/imagenes/utils/supabase_client.py

echo "Estructura de apps creada."

# agregar apps a settings.py
echo "Registrando apps en settings.py..."

SETTINGS_FILE="transito_backend/settings.py"

sed -i '' "/INSTALLED_APPS = \[/a\\
    'apps.proyectos',\\
    'apps.mandantes',\\
    'apps.red_vial',\\
    'apps.usuarios',\\
" $SETTINGS_FILE

echo "Apps registradas."

echo "Arquitectura Django lista."