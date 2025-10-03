# 📊 Sistema de Análisis Financiero Automatizado

Sistema integral que automatiza **completamente** el análisis financiero de empresas peruanas desde la descarga hasta el análisis con IA.

## 🎯 ¿Qué hace el sistema?

1. **Descarga automática** desde SMV (Superintendencia del Mercado de Valores)
2. **Extrae datos** de estados financieros de forma inteligente
3. **Analiza vertical y horizontalmente** la información
4. **Calcula 10 ratios financieros** clave
5. **Visualiza** con gráficos interactivos
6. **Interpreta** con Inteligencia Artificial (Groq + GPT-4o-mini)
7. **Exporta** resultados a Excel

## ✨ Características Principales

- **🤖 Descarga automática**: Búsqueda inteligente de empresas y descarga desde SMV
- **📊 Análisis Vertical**: Estructura porcentual de estados financieros
- **📈 Análisis Horizontal**: Evolución temporal y variaciones
- **🔢 10 Ratios Financieros**: Liquidez, endeudamiento, rentabilidad y eficiencia
- **📉 7 Gráficos Interactivos**: Visualización de tendencias con Plotly
- **🤖 Análisis con IA**: Interpretación profesional en 3 fases especializadas
- **💾 Exportación Excel**: Todos los análisis exportables
- **⚡ Modo Headless**: 50% más rápido que navegación visible

## 🚀 Inicio Rápido (3 Pasos)

### 1. Configurar API Key

```bash
# Copiar template de configuración
copy config_api.template.py config_api.py

# Editar config_api.py y agregar tu API key de Groq
# Obtén tu API key en: https://console.groq.com/
```

### 2. Instalar Dependencias

```bash
# Activar entorno virtual
venv\Scripts\Activate

# Instalar requerimientos
pip install -r requirements.txt
```

### 3. Ejecutar Aplicación

```bash
streamlit run analizador_financiero.py
```

### 4. Usar el Sistema

1. **Sidebar** → Expandir "📥 Configurar Descarga Automática"
2. **Buscar empresa**: Escribe "SAN JUAN" (3+ caracteres)
3. **Seleccionar** de lista desplegable
4. **Configurar años**: 2024 → 2020
5. **Click**: "🚀 Iniciar Descarga Automática"
6. **Esperar** 1-2 minutos (descarga + análisis automático)
7. **Explorar** resultados en 5 pestañas

## 📚 Documentación Completa

**Toda la documentación está organizada en la carpeta `Docs/`**

### 📖 Documentos Clave

- **[Docs/INDICE.md](Docs/INDICE.md)** - 📋 Índice completo de documentación
- **[Docs/RESUMEN_GENERAL.md](Docs/RESUMEN_GENERAL.md)** - ⭐ Flujo del programa y arquitectura
- **[Docs/QUICK_START_DESCARGADOR.md](Docs/QUICK_START_DESCARGADOR.md)** - ⚡ Guía rápida (3 pasos)

### 📂 Categorías de Documentación

```
Docs/
├── 🚀 Guías de Usuario (5 docs)
├── 🛠️ Documentación Técnica (5 docs)
├── 🔄 Mejoras y Optimizaciones (7 docs)
├── 📋 Resúmenes (8 docs)
└── 🔧 Solución de Problemas (3 docs)

Total: 29 documentos organizados
```

### 🎯 Por Dónde Empezar

1. **[Docs/INDICE.md](Docs/INDICE.md)** - Ver índice completo
2. **[Docs/RESUMEN_GENERAL.md](Docs/RESUMEN_GENERAL.md)** - Entender el sistema
3. **[Docs/QUICK_START_DESCARGADOR.md](Docs/QUICK_START_DESCARGADOR.md)** - Empezar a usar

## 💻 Requisitos

### Software
- **Python 3.12+**
- **Google Chrome** (para descarga automática)
- **Conexión a internet** (para SMV y API Groq)

### Dependencias Python
Ver archivo `requirements.txt`:
- streamlit 1.50.0
- selenium 4.x
- webdriver-manager
- pandas
- openpyxl
- beautifulsoup4
- plotly
- groq

## 🏗️ Arquitectura

### 10 Módulos Python (~7,500 líneas)

```
analizador_financiero.py          (3,056) - UI principal Streamlit
descargador_smv.py                (  600) - Descarga automática SMV
extractor_estados_mejorado.py     (  800) - Parser de datos
analisis_vertical_mejorado.py     (  400) - Análisis vertical POST-2010
analisis_horizontal_mejorado.py   (  350) - Análisis horizontal POST-2010
analisis_vertical_consolidado.py  (  450) - Consolidación vertical
analisis_horizontal_consolidado.py(  400) - Consolidación horizontal
ratios_financieros.py             (  721) - 10 ratios + 7 gráficos
analisis_vertical_horizontal.py   (  500) - Legacy PRE-2010
limpiar_archivos.py               (  200) - Mantenimiento
```

## 📊 Funcionalidades

### 1. Descarga Automática desde SMV
- Búsqueda inteligente de empresas (3 niveles: exacta, parcial, palabras clave)
- Descarga por rango de años
- Modo headless (50% más rápido)
- Carga automática post-descarga

### 2. Análisis Vertical
- Estructura porcentual de estados financieros
- Balance: Base = Total Activos (100%)
- Resultados: Base = Ingresos Ordinarios (100%)
- Vista consolidada multi-período

### 3. Análisis Horizontal
- Variaciones año a año (% y monto)
- Identificación de tendencias
- Gráficos de evolución temporal
- Vista consolidada de todas las variaciones

### 4. Ratios Financieros (10 ratios)

**Liquidez:**
- Liquidez Corriente
- Prueba Ácida

**Endeudamiento:**
- Razón Deuda Total
- Deuda/Patrimonio

**Rentabilidad:**
- Margen Neto
- ROA (Return on Assets)
- ROE (Return on Equity)

**Eficiencia:**
- Rotación Activos Totales
- Rotación Cuentas por Cobrar
- Rotación Inventarios

### 5. Análisis con IA (3 Fases)
- **Fase 1**: Liquidez y Endeudamiento (15-18 líneas)
- **Fase 2**: Rentabilidad y Eficiencia (18-20 líneas)
- **Fase 3**: Conclusión y Recomendaciones (15-18 líneas)
- **Total**: 48-56 líneas de análisis profesional

### 6. Visualizaciones
- 7 gráficos interactivos (Plotly)
- Exportación a Excel de todos los análisis
- Interface intuitiva con Streamlit

## 📈 Métricas de Rendimiento

```
Descarga 5 años (headless):    1-1.5 min
Extracción + Análisis:         2-3 seg
Análisis con IA (3 fases):     10-15 seg
────────────────────────────────────────
TOTAL (end-to-end):            2-3 min

vs Proceso Manual:             3.5 horas
Ahorro de tiempo:              93%
```

## 🛠️ Solución de Problemas

### Error: ChromeDriver
Ver: **[Docs/INSTRUCCIONES_CHROMEDRIVER.md](Docs/INSTRUCCIONES_CHROMEDRIVER.md)**

### Otros Problemas
Ver: **[Docs/SOLUCION_VISUAL_V2.md](Docs/SOLUCION_VISUAL_V2.md)**

## 🎓 Casos de Uso

- 📊 **Analistas financieros**: Análisis rápido de múltiples empresas
- 💼 **Inversionistas**: Evaluación de oportunidades de inversión
- 🎓 **Estudiantes**: Aprendizaje de análisis financiero
- 🏢 **Consultoras**: Reportes profesionales automatizados
- 📈 **Traders**: Análisis fundamental para decisiones

## 🔐 Seguridad

### Configuración de API Key

La API key de Groq está en un archivo separado `config_api.py` (ignorado por Git):

**Primera vez:**
```bash
# 1. Copiar template
copy config_api.template.py config_api.py

# 2. Editar config_api.py y agregar tu API key
# GROQ_API_KEY = "tu_api_key_aqui"

# 3. Obtener API key: https://console.groq.com/
```

**Importante:**
- ⚠️ `config_api.py` está en `.gitignore` y NO se sube a Git
- ✅ Cada usuario debe configurar su propia API key
- ✅ Ver documentación completa: [Docs/SEGURIDAD_API_KEY.md](Docs/SEGURIDAD_API_KEY.md)

## 📞 Soporte

1. **Revisar documentación**: [Docs/INDICE.md](Docs/INDICE.md)
2. **Guía de inicio**: [Docs/QUICK_START_DESCARGADOR.md](Docs/QUICK_START_DESCARGADOR.md)
3. **Arquitectura completa**: [Docs/RESUMEN_GENERAL.md](Docs/RESUMEN_GENERAL.md)

## 📜 Licencia

Este proyecto es de uso educativo y profesional.

## 🎉 Versión

**Versión 4.0** - Sistema completamente automatizado
- Descarga automática SMV
- Análisis completo (vertical, horizontal, ratios)
- Interpretación con IA (3 fases)
- Exportación Excel
- 81% menos archivos (limpieza completada)

---

**Última actualización:** 3 de octubre de 2025

**Toda la documentación está en:** [Docs/](Docs/)

**Empezar aquí:** [Docs/INDICE.md](Docs/INDICE.md) o [Docs/RESUMEN_GENERAL.md](Docs/RESUMEN_GENERAL.md)

```
AnalisisFinancieroV4/
├── analizador_financiero.py    # Programa principal
├── temp/                       # Carpeta temporal (se crea automáticamente)
├── ejemplos/                   # Archivos de ejemplo
├── venv/                       # Entorno virtual
└── README.md                   # Esta documentación
```

## Funcionalidades del Programa

### 1. Carga de Archivos
- Soporte para múltiples archivos XLS/XLSX
- Validación automática de formato

### 2. Procesamiento
- Conversión XLS → HTML
- Extracción de metadatos (empresa, año, tipo de reporte)
- Identificación de tablas de estados financieros
- Extracción de datos por categorías

### 3. Análisis
- Organización por categorías financieras
- Detección automática de años disponibles
- Clasificación de estados financieros

### 4. Resultados
- Vista de resumen general
- Análisis por categorías
- Comparativo entre períodos
- Datos detallados
- Exportación a CSV

## Notas Técnicas

- Los archivos se procesan en una carpeta temporal `temp/`
- La conversión a HTML facilita la extracción de datos estructurados
- El sistema es tolerante a diferentes formatos de estados financieros
- Utiliza Beautiful Soup para parsing HTML
- Pandas para manejo de datos tabulares

## Troubleshooting

### Error al cargar archivo
- Verificar que el archivo sea XLS o XLSX válido
- Asegurarse de que el archivo no esté corrupto

### No se extraen datos
- Verificar que el archivo contenga estados financieros
- El sistema busca términos específicos del diccionario de palabras clave

### Problemas de codificación
- Los archivos se procesan con codificación UTF-8
- Algunos archivos pueden requerir conversión de codificación

## Contribuciones

Para mejorar el diccionario de palabras clave o agregar funcionalidades:

1. Modificar el método `cargar_diccionario_palabras_clave()`
2. Agregar nuevas categorías de análisis
3. Mejorar los métodos de extracción de datos

## Licencia

Proyecto de uso académico y profesional para análisis financiero automatizado.