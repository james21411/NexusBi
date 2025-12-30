#!/bin/bash

echo "🔨 Compilation du frontend..."

cd frontend

# Nettoyer le cache
echo "🧹 Nettoyage du cache..."
rm -rf node_modules/.cache
rm -rf dist
rm -rf .vite

# Installer les dépendances si nécessaire
echo "📦 Installation des dépendances..."
npm install

# Compiler le projet
echo "⚡ Compilation..."
npm run build

echo "✅ Frontend compilé avec succès!"