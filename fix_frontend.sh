#!/bin/bash

echo "🔧 Correction du frontend - Compilation forcée"
echo "=============================================="

cd frontend

# 1. Nettoyer complètement le cache
echo "🧹 Nettoyage du cache..."
rm -rf node_modules/.cache
rm -rf dist
rm -rf .vite
rm -rf dist-temp
rm -rf .next

# 2. Réinstaller les dépendances si nécessaire
echo "📦 Vérification des dépendances..."
if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances..."
    npm install
fi

# 3. Compiler en mode production
echo "⚡ Compilation en mode production..."
npm run build

# 4. Démarrer le serveur de développement
echo "🚀 Démarrage du serveur de développement..."
echo "Le frontend sera disponible sur http://localhost:3000"
npm run dev &

echo "✅ Correction terminée!"
echo "🔄 Actualisez votre navigateur avec Ctrl+F5"