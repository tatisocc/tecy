#!/bin/bash

# Este script asume que ya estás dentro de la carpeta tecy/
# o que la acabas de clonar.

# 1. Crear entorno virtual dentro de la carpeta tecy/
echo "creando entorno virtual..."
python3 -m venv .venv

# 2. Instalar dependencias
echo "instalando dependencias..."
./.venv/bin/pip install -r requirements.txt

# 3. Asegurar que las carpetas existan según tu árbol exacto
echo "verificando estructura interna..."
mkdir -p .tecy/tmp alls/ letters/

# 4. Agregar alias al .bash_aliases
echo "configurando alias 'tecy'..."
TECY_PATH=$(pwd)

# Evitar duplicar el alias si ya existe
if ! grep -q "alias tecy=" ~/.bash_aliases; then
    echo "alias tecy='$TECY_PATH/.venv/bin/python3 $TECY_PATH/.tecy/tecy.py'" >> ~/.bash_aliases
fi

echo "instalación completada!"
echo "para activar el alias inmediatamente, ejecuta:"
echo "source ~/.bash_aliases"
