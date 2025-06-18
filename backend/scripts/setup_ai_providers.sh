#!/bin/bash
# Script d'installation des providers AI pour Linguify

echo "Installation des dépendances pour les providers AI de Linguify..."

# Détecter si Poetry est utilisé
if [ -f "pyproject.toml" ]; then
    echo "Poetry détecté, installation avec Poetry..."
    
    # OpenAI
    echo "Installation du package OpenAI..."
    poetry add openai
    
    echo "Installation terminée avec Poetry!"
else
    # Utiliser pip si Poetry n'est pas détecté
    echo "Utilisation de pip pour l'installation..."
    
    # OpenAI
    echo "Installation du package OpenAI..."
    pip install openai
    
    echo "Installation terminée avec pip!"
fi

echo ""
echo "Installation des dépendances AI terminée."
echo ""
echo "Pour utiliser Ollama (option gratuite locale):"
echo "1. Téléchargez Ollama depuis: https://ollama.ai/download"
echo "2. Exécutez la commande 'ollama pull mistral' pour télécharger le modèle"
echo ""
echo "Configuration dans .env:"
echo "-------------------------------------------"
echo "# Pour le simulateur (défaut, gratuit)"
echo "AI_PROVIDER=simulator"
echo ""
echo "# Pour OpenAI (payant)"
echo "AI_PROVIDER=openai"
echo "OPENAI_API_KEY=votre_clé_api"
echo ""
echo "# Pour Hugging Face (gratuit avec limites)"
echo "AI_PROVIDER=huggingface"
echo "HUGGINGFACE_API_TOKEN=votre_token"
echo ""
echo "# Pour Ollama (local, gratuit)"
echo "AI_PROVIDER=ollama"
echo "OLLAMA_API_URL=http://localhost:11434"
echo "OLLAMA_MODEL=mistral"
echo "-------------------------------------------"
echo ""
echo "Pour plus d'informations, consultez:"
echo "docs/backend/features/ai_integration.md"