#!/usr/bin/env bash
# Script de build para Render
set -o errexit

echo "🔨 Iniciando build del proyecto..."

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip install -r requirements.txt

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python biblioteca/manage.py collectstatic --noinput

echo "✅ Build completado exitosamente"
