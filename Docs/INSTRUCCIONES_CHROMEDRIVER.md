# COMO DESCARGAR E INSTALAR CHROMEDRIVER

## PASO 1: Verificar Version de Chrome

1. Abre Google Chrome
2. En la barra de direcciones escribe: `chrome://version/`
3. Presiona ENTER
4. Busca la linea que dice "Google Chrome" 
5. Anota el numero de version (ej: 120.0.6099.109)

```
Ejemplo:
Google Chrome: 120.0.6099.109 (Official Build) (64-bit)
                ^^^^^^^^^^^^^^
                Esta es tu version
```

---

## PASO 2: Descargar ChromeDriver

### Opcion A: Chrome 115 o superior (Mas reciente)

1. Ve a: https://googlechromelabs.github.io/chrome-for-testing/
2. Busca la seccion "Stable"
3. Encuentra tu version de Chrome
4. Descarga el archivo para Windows (win64 o win32)
5. Descomprime el archivo ZIP

### Opcion B: Chrome 114 o inferior (Versiones antiguas)

1. Ve a: https://chromedriver.chromium.org/downloads
2. Click en la version que coincida con tu Chrome
3. Descarga `chromedriver_win32.zip`
4. Descomprime el archivo ZIP

---

## PASO 3: Colocar ChromeDriver en la Carpeta Correcta

1. Abre el explorador de archivos de Windows
2. Navega a: `C:\Users\Usuario\AnalisisFinancieroV4\`
3. Abre la carpeta `drivers\`
4. Copia el archivo `chromedriver.exe` alli

```
Ruta completa esperada:
C:\Users\Usuario\AnalisisFinancieroV4\drivers\chromedriver.exe
```

---

## PASO 4: Verificar Instalacion

Ejecuta en terminal:

```bash
python verificar_descargador.py
```

Deberia mostrar:
```
=== 4. CHROMEDRIVER ===
✓ ChromeDriver ejecutable
  C:\Users\Usuario\AnalisisFinancieroV4\drivers\chromedriver.exe
```

---

## PROBLEMAS COMUNES

### Error: "ChromeDriver no encontrado"

**Causa:** Archivo no esta en la carpeta correcta

**Solucion:**
- Verificar ruta: `drivers\chromedriver.exe`
- Verificar que el archivo se llame exactamente `chromedriver.exe`
- No debe estar en subcarpetas adicionales

### Error: "Version incompatible"

**Causa:** Version de ChromeDriver no coincide con Chrome

**Solucion:**
1. Verificar version de Chrome (chrome://version/)
2. Descargar ChromeDriver de la MISMA version
3. Reemplazar el archivo anterior

### Error: "Access denied" o "Permisos"

**Causa:** Windows bloqueo el archivo

**Solucion:**
1. Click derecho en chromedriver.exe
2. Propiedades
3. General tab
4. Si hay un mensaje "Este archivo proviene de otro equipo..."
5. Click en "Desbloquear"
6. Aplicar > OK

---

## ALTERNATIVA: Usar WebDriver Manager (Automatico)

Si tienes problemas con ChromeDriver manual, puedes usar gestion automatica:

```bash
pip install webdriver-manager
```

Luego modificar `descargador_smv.py` (linea ~92):

```python
# Antes:
service = Service(executable_path=self.driver_path)

# Despues:
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
```

Esto descarga y actualiza ChromeDriver automaticamente.

---

## VERIFICACION FINAL

Ejecuta:

```bash
streamlit run analizador_financiero.py
```

1. Ve al sidebar
2. Expande "Descarga Automatica SMV"
3. Ingresa: "SAN JUAN"
4. Años: 2024 - 2023
5. Click "Iniciar Descarga Automatica"

Si se abre Chrome automaticamente = TODO CORRECTO

---

## RECURSOS

- ChromeDriver oficial: https://chromedriver.chromium.org/
- Chrome for Testing: https://googlechromelabs.github.io/chrome-for-testing/
- WebDriver Manager: https://github.com/SergeyPirogov/webdriver_manager

---

NOTA: Si Chrome se actualiza automaticamente, es posible que necesites
actualizar ChromeDriver tambien. El sistema te avisara si hay incompatibilidad.
