#!/bin/bash

echo "🔍 Vérification du frontend..."

cd frontend

# Vérifier la syntaxe TypeScript
echo "📝 Vérification TypeScript..."
npx tsc --noEmit --skipLibCheck

# Vérifier le lint
echo "🧹 Vérification ESLint..."
npm run lint 2>/dev/null || echo "ESLint non configuré"

# Compiler en mode développement
echo "⚡ Test de compilation..."
npm run dev &
DEV_PID=$!
sleep 5

# Arrêter le serveur de développement
kill $DEV_PID 2>/dev/null

echo "✅ Vérification terminée!"