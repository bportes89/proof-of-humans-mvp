#!/bin/bash
echo "=== Setup e Execução do Proof of Humans (Mac/Linux) ==="

# Verifica se python3 existe
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 não encontrado!"
    echo "Por favor, instale o Python 3 antes de continuar."
    echo "No Mac (com Homebrew): brew install python"
    exit 1
fi

# Cria venv se não existir
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual (venv)..."
    python3 -m venv venv
fi

# Ativa venv
source venv/bin/activate

# Instala dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Roda o servidor
echo "🚀 Iniciando servidor..."
echo "Acesse http://localhost:8000 no seu navegador"
python -m uvicorn backend.main:app --reload
