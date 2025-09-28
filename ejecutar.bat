@echo off
echo ==========================================
echo    ANALIZADOR FINANCIERO CON STREAMLIT
echo ==========================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual.
    echo Por favor, ejecuta primero: python -m venv venv
    pause
    exit /b 1
)

echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [INFO] Verificando instalacion de dependencias...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install streamlit pandas openpyxl xlrd beautifulsoup4 lxml numpy
)

echo [INFO] Creando directorio temporal...
if not exist "temp" mkdir temp

echo.
echo [INFO] Iniciando aplicacion Streamlit...
echo [INFO] La aplicacion se abrira en tu navegador automaticamente
echo [INFO] URL: http://localhost:8501
echo.
echo [INFO] Para detener la aplicacion, presiona Ctrl+C
echo.

REM Ejecutar la aplicación
streamlit run analizador_financiero.py

echo.
echo [INFO] Aplicacion cerrada.
pause