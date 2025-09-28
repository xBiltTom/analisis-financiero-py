# Analizador Financiero con Streamlit

Este programa permite analizar archivos XLS de estados financieros, extrayendo automáticamente los datos más importantes para análisis financiero.

## Características principales

- **Conversión automática**: Convierte archivos XLS a HTML para facilitar la extracción de datos
- **Extracción inteligente**: Utiliza un diccionario de palabras clave para identificar cuentas importantes
- **Análisis por categorías**: Organiza los datos en activos, pasivos, patrimonio, estado de resultados y flujo de efectivo
- **Almacenamiento temporal**: Guarda archivos procesados en carpeta temporal para mejor organización
- **Interfaz intuitiva**: Interfaz web fácil de usar con Streamlit
- **Exportación**: Permite descargar resultados en formato CSV

## Requisitos

- Python 3.8+
- streamlit
- pandas
- openpyxl
- xlrd
- beautifulsoup4
- lxml
- numpy

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
```

2. Activar entorno virtual:
```bash
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install streamlit pandas openpyxl xlrd beautifulsoup4 lxml numpy
```

## Uso

1. Ejecutar la aplicación:
```bash
streamlit run analizador_financiero.py
```

2. Abrir el navegador en la URL que aparece (generalmente http://localhost:8501)

3. Subir uno o más archivos XLS de estados financieros

4. El sistema automáticamente:
   - Convierte los archivos XLS a HTML
   - Extrae los datos usando el diccionario de palabras clave
   - Organiza la información por categorías financieras
   - Presenta los resultados en forma organizada

## Diccionario de Palabras Clave

El sistema utiliza un diccionario completo de términos financieros para identificar cuentas importantes:

### Activos
- Activos corrientes/no corrientes
- Efectivo y equivalentes
- Cuentas por cobrar
- Inventarios
- Propiedades, planta y equipo
- Y más...

### Pasivos
- Pasivos corrientes/no corrientes
- Préstamos bancarios
- Cuentas por pagar
- Obligaciones financieras
- Y más...

### Patrimonio
- Capital
- Reservas
- Resultados acumulados
- Y más...

### Estado de Resultados
- Ingresos operacionales
- Costos de ventas
- Gastos operacionales
- Utilidad/pérdida neta
- Y más...

## Estructura de Archivos

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