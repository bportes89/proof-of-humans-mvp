@echo off
echo === Setup e Execucao do Proof of Humans (Windows) ===

:: Verifica python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python nao encontrado!
    echo Por favor, instale o Python em https://www.python.org/downloads/
    echo Lembre-se de marcar "Add Python to PATH" na instalacao.
    pause
    exit /b
)

:: Cria venv
if not exist venv (
    echo [!] Criando ambiente virtual (venv)...
    python -m venv venv
)

:: Ativa venv
call venv\Scripts\activate

:: Instala dependencias
echo [!] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

:: Roda servidor
echo [!] Iniciando servidor...
echo Acesse http://localhost:8000 no seu navegador
python -m uvicorn backend.main:app --reload

pause
