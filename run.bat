@echo off
echo === Setup e Execucao do Proof of Humans (Windows) ===

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python nao encontrado!
    echo Por favor, instale o Python em https://www.python.org/downloads/
    echo Lembre-se de marcar "Add Python to PATH" na instalacao.
    pause
    exit /b
)

if not exist venv (
    echo [!] Criando ambiente virtual venv...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [!] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo [!] Verificando cameras...
python tools\check_cameras.py
echo.
echo Escolha o indice da camera para usar (Ex: 0 ou 1).
echo Deixe em branco para usar o MOCK (Simulacao).
set /p CAM_INDEX="Indice da Camera: "

if "%CAM_INDEX%"=="" (
    echo [!] Usando modo SIMULACAO (Mock)
    set CAMERA_INDEX=
) else (
    echo [!] Usando Camera Real (Indice: %CAM_INDEX%)
    set CAMERA_INDEX=%CAM_INDEX%
)

echo.
echo [!] Iniciando servidor...
echo Acesse http://localhost:8000 no seu navegador
python -m uvicorn backend.main:app --reload

pause