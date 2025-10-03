# 🤖 DESCARGADOR AUTOMÁTICO SMV - Guía de Uso

## 📋 Descripción

El **Descargador Automático SMV** es un módulo que automatiza la descarga de estados financieros desde la web de la **Superintendencia del Mercado de Valores (SMV)** del Perú.

---

## ✨ Características

✅ **Búsqueda inteligente de empresas**
- Búsqueda por nombre completo o parcial
- Coincidencia flexible (ej: "SAN JUAN" encuentra "CERVECERIA SAN JUAN S.A.")

✅ **Descarga consecutiva de múltiples años**
- Rango personalizable (ej: 2024 a 2020)
- Descarga automática en segundo plano

✅ **Barra de progreso en tiempo real**
- Monitoreo del proceso en vivo
- Mensajes informativos en cada paso

✅ **Integración con Streamlit**
- Interfaz gráfica intuitiva
- Configuración visual en sidebar
- Análisis automático de archivos descargados

---

## 📦 Requisitos

### 1. ChromeDriver

El driver debe estar ubicado en: `drivers/chromedriver.exe`

**Descarga:** https://chromedriver.chromium.org/downloads

⚠️ **Importante:** La versión del ChromeDriver debe coincidir con la versión de Google Chrome instalada.

### 2. Dependencias de Python

```bash
pip install selenium
```

(Selenium ya fue instalado automáticamente en el entorno virtual)

---

## 🚀 Uso desde Streamlit (Interfaz Gráfica)

### Paso 1: Abrir el Analizador Financiero

```bash
streamlit run analizador_financiero.py
```

### Paso 2: Configurar Descarga Automática

En el **sidebar izquierdo**, busca la sección **"🤖 Descarga Automática SMV"**:

1. **Expandir** la sección "📥 Configurar Descarga Automática"

2. **Ingresar nombre de la empresa**:
   ```
   Ej: SAN JUAN
   Ej: BACKUS
   Ej: ALICORP
   ```
   
   ✅ Búsqueda inteligente: No necesitas el nombre completo

3. **Seleccionar rango de años**:
   - **Año inicio** (más reciente): Ej. 2024
   - **Año fin** (más antiguo): Ej. 2020
   
   📅 Descargará: 2024, 2023, 2022, 2021, 2020

4. **Clic en "🚀 Iniciar Descarga Automática"**

### Paso 3: Monitorear Progreso

Verás un registro en tiempo real con mensajes como:

```
🚀 Iniciando navegador...
📋 Obteniendo lista de empresas...
🔍 Buscando empresa: SAN JUAN
✅ Empresa encontrada: CERVECERIA SAN JUAN S.A.
📅 Seleccionando periodo anual...
📥 Iniciando descargas de 2024 a 2020...

🔄 Procesando año 2024 (1/5)...
📅 Seleccionando año 2024...
🔍 Buscando registros del año 2024...
✅ 12 registros encontrados para 2024
📥 Descargando archivo Excel del año 2024...
✅ Archivo 2024 descargado: REPORTE_2024.xls

🔄 Procesando año 2023 (2/5)...
...
```

### Paso 4: Ver Resultados

Al finalizar, verás un resumen:

```
✅ Descarga completada!

Empresa: CERVECERIA SAN JUAN S.A.
Archivos descargados: 5
Errores: 0

✅ Años descargados: 2024, 2023, 2022, 2021, 2020
📂 Carpeta de descargas: C:\...\descargas
```

### Paso 5: Analizar Archivos Descargados

Tienes 2 opciones:

**Opción A:** Clic en botón "📊 Analizar Archivos Descargados" (dentro del expander)

**Opción B:** En el sidebar, clic en "📊 Cargar archivos desde carpeta descargas"

Los archivos se procesarán automáticamente y estarán disponibles en todas las vistas del sistema.

---

## 💻 Uso Programático (Python Script)

### Ejemplo Básico

```python
from descargador_smv import DescargadorSMV

# Crear descargador
descargador = DescargadorSMV(
    download_dir="C:/mis_descargas",
    driver_path="C:/drivers/chromedriver.exe"
)

# Descargar estados financieros
resultado = descargador.proceso_completo(
    nombre_empresa="SAN JUAN",
    año_inicio=2024,
    año_fin=2020,
    callback_progreso=print  # Mostrar progreso en consola
)

# Ver resultados
if 'error' in resultado:
    print(f"Error: {resultado['error']}")
else:
    print(f"Empresa: {resultado['empresa']}")
    print(f"Descargados: {resultado['años_exitosos']}")
```

### Ejemplo con Callback Personalizado

```python
from descargador_smv import DescargadorSMV

def mi_callback(mensaje):
    """Callback personalizado para progreso"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")

descargador = DescargadorSMV()

resultado = descargador.proceso_completo(
    nombre_empresa="ALICORP",
    año_inicio=2023,
    año_fin=2020,
    callback_progreso=mi_callback
)

print(f"\nArchivos descargados: {resultado['total_exitosos']}")
print(f"Carpeta: {resultado['carpeta_descargas']}")
```

### Métodos Disponibles

```python
# 1. Iniciar navegador
descargador.iniciar_navegador()

# 2. Obtener lista de empresas
empresas = descargador.obtener_empresas_disponibles()
# Retorna: [{'value': '1', 'text': 'EMPRESA A S.A.'}, ...]

# 3. Buscar empresa
empresa = descargador.buscar_empresa("SAN JUAN")
# Retorna: {'value': '49', 'text': 'CERVECERIA SAN JUAN S.A.'}

# 4. Seleccionar empresa
descargador.seleccionar_empresa(empresa)

# 5. Seleccionar periodo anual
descargador.seleccionar_periodo_anual()

# 6. Descargar un año específico
exito = descargador.descargar_año(2024, callback_progreso=print)

# 7. Descargar rango de años
resultados = descargador.descargar_rango_años(2024, 2020, callback_progreso=print)
# Retorna: {'exitosos': [2024, 2023, 2022], 'fallidos': [2021, 2020]}

# 8. Cerrar navegador
descargador.cerrar_navegador()
```

---

## 🗂️ Estructura de Archivos

```
AnalisisFinancieroV4/
│
├── drivers/
│   └── chromedriver.exe          ← Driver de Chrome
│
├── descargas/                     ← Archivos descargados aquí
│   ├── REPORTE_2024.xls
│   ├── REPORTE_2023.xls
│   └── ...
│
├── descargador_smv.py             ← Módulo de descarga
├── analizador_financiero.py       ← Programa principal
└── README_DESCARGADOR.md          ← Este archivo
```

---

## ⚙️ Configuración Avanzada

### Cambiar Carpeta de Descargas

```python
descargador = DescargadorSMV(
    download_dir="C:/MisDescargas/Financieros"
)
```

### Usar ChromeDriver Personalizado

```python
descargador = DescargadorSMV(
    driver_path="C:/WebDrivers/chromedriver.exe"
)
```

### Modo Headless (Sin Interfaz Gráfica)

Editar `descargador_smv.py`, línea ~94:

```python
# Descomentar esta línea:
options.add_argument("--headless")
```

---

## 🐛 Solución de Problemas

### Error: "ChromeDriver no encontrado"

**Solución:**
1. Descargar ChromeDriver desde https://chromedriver.chromium.org/downloads
2. Colocar `chromedriver.exe` en carpeta `drivers/`
3. Verificar que la versión coincida con Google Chrome instalado

### Error: "Versión de ChromeDriver incompatible"

**Problema:** ChromeDriver no coincide con la versión de Chrome

**Solución:**
1. Ver versión de Chrome: `chrome://version/`
2. Descargar ChromeDriver de la misma versión

### Error: "No se encontró la empresa"

**Posibles causas:**
- Nombre mal escrito
- Empresa no registrada en SMV
- Empresa fusionada o inactiva

**Solución:**
1. Verificar nombre en web de SMV manualmente
2. Probar con nombre parcial (ej: "BACKUS" en lugar de "UNION DE CERVECERIAS PERUANAS BACKUS Y JOHNSTON S.A.A.")

### Timeout al descargar

**Posibles causas:**
- Internet lento
- Servidor SMV saturado

**Solución:**
1. Aumentar timeout en `descargador_smv.py`, línea ~400:
   ```python
   time.sleep(5)  # Aumentar de 3 a 5 segundos
   ```

---

## 📊 Integración con Análisis Financiero

Los archivos descargados automáticamente se pueden:

1. ✅ **Cargar automáticamente** desde carpeta descargas
2. ✅ **Analizar verticalmente** (estructura de estados financieros)
3. ✅ **Analizar horizontalmente** (variaciones interanuales)
4. ✅ **Calcular ratios financieros** (liquidez, endeudamiento, rentabilidad)
5. ✅ **Generar análisis con IA** (interpretación inteligente)

---

## 🎯 Casos de Uso

### Caso 1: Análisis Multi-Período

```
1. Descargar años 2020-2024 de una empresa
2. Sistema carga automáticamente todos los archivos
3. Vista consolidada muestra evolución en el tiempo
4. Ratios calculados automáticamente
5. Análisis de IA genera recomendaciones
```

### Caso 2: Comparación de Empresas

```
1. Descargar empresa A (2024)
2. Descargar empresa B (2024)
3. Subir manualmente ambos archivos
4. Comparar ratios lado a lado
5. Identificar fortalezas y debilidades relativas
```

### Caso 3: Seguimiento Trimestral

```
1. Configurar descarga periódica (manual por ahora)
2. Ejecutar cada trimestre
3. Archivos se acumulan en carpeta descargas
4. Análisis histórico disponible inmediatamente
```

---

## 🔐 Seguridad y Privacidad

- ✅ **No almacena credenciales**: Sistema usa web pública de SMV
- ✅ **Datos en local**: Archivos se guardan solo en tu computadora
- ✅ **Sin tracking**: No envía información a servidores externos
- ✅ **Código abierto**: Puedes revisar todo el código fuente

---

## 📝 Notas Adicionales

### Limitaciones

- ⚠️ Solo funciona con la web de SMV de Perú
- ⚠️ Requiere Google Chrome instalado
- ⚠️ Depende de la estructura HTML de la web (puede cambiar)

### Frecuencia de Uso Recomendada

- 📅 **No abusar**: La SMV es un servicio público
- 🕐 **Espaciar descargas**: Esperar 2-3 segundos entre archivos (ya implementado)
- 📊 **Descargar solo lo necesario**: Evitar descargas masivas innecesarias

### Mantenimiento

Si la web de SMV cambia su estructura:

1. Los selectores CSS/XPath pueden fallar
2. Revisar y actualizar `descargador_smv.py`
3. Principales elementos a verificar:
   - IDs de combos y botones
   - Estructura de tabla de resultados
   - Links de descarga

---

## 📞 Soporte

Si encuentras problemas:

1. Revisar sección "Solución de Problemas"
2. Verificar que ChromeDriver esté actualizado
3. Probar descarga manual en web de SMV primero
4. Revisar logs en consola de Streamlit

---

## 🎉 Créditos

**Desarrollado para:** Sistema de Análisis Financiero V4  
**Fecha:** 3 de octubre de 2025  
**Tecnologías:** Python, Selenium, Streamlit, ChromeDriver

---

**¡Disfruta de las descargas automatizadas! 🚀📊**
