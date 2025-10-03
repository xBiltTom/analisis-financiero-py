# 📊 Nuevo Extractor de Estados Financieros - Documentación

## ✅ Análisis Completado

He analizado detalladamente los archivos de la carpeta `ejemplos` y creado un **nuevo extractor mejorado** que identifica correctamente los 4 bloques principales de estados financieros, con detección automática de formato según el año.

---

## 📁 Archivos Creados

### 1. **ESTRUCTURA_BLOQUES.md**
Documento completo con análisis detallado de:
- Estructura exacta de cada estado financiero
- Diferencias entre formato Pre-2010 (≤2009) y Post-2010 (≥2010)
- Patrones de inicio y fin de cada bloque
- Ejemplos de extracción
- Formato de números y conversión

### 2. **extractor_estados_mejorado.py**
Módulo Python especializado que incluye:
- ✅ Detección automática de año del documento
- ✅ Extracción precisa de los 4-5 bloques principales
- ✅ Conversión automática de texto a números (formato latino: `1,234.56`)
- ✅ Manejo correcto de negativos en paréntesis: `(1,234)` → `-1234.0`
- ✅ Validación de equilibrio contable
- ✅ Estructura de datos completa con años y valores

### 3. **test_extractor.py**
Script de prueba para validar la extracción

---

## 🔍 Características Principales

### Detección Automática de Formato

#### Para años ≤ 2009:
```
1. BALANCE GENERAL
2. ESTADO DE GANANCIAS Y PERDIDAS
3. ESTADO DE CAMBIOS EN EL PATRIMONIO NETO
4. ESTADO DE FLUJO DE EFECTIVO (sin "S")
```

#### Para años ≥ 2010 (NIIF):
```
1. ESTADO DE SITUACION FINANCIERA
2. ESTADO DE RESULTADOS
3. ESTADO DE CAMBIOS EN EL PATRIMONIO NETO
4. ESTADO DE FLUJO DE EFECTIVO
5. ESTADO DE RESULTADOS INTEGRALES ⭐ (nuevo)
```

### Extracción de Datos

Cada estado financiero se extrae con:
```python
{
    'nombre': 'BALANCE GENERAL',
    'años': [2004, 2003],  # Ordenados del más reciente al más antiguo
    'cuentas': [
        {
            'nombre': 'Caja y Bancos',
            'nota': '0',
            'es_total': False,  # True para subtotales/totales
            'valores': {
                2004: 1511.0,
                2003: 389.0
            },
            'fila': 3
        },
        ...
    ],
    'total_cuentas': 58
}
```

### Conversión de Números

El extractor maneja correctamente:
- ✅ `"1,234"` → `1234.0`
- ✅ `"1,234.56"` → `1234.56`
- ✅ `"(1,234)"` → `-1234.0`
- ✅ `"-1,234"` → `-1234.0`
- ✅ `"0"` → `0.0`
- ✅ `""` o `"&nbsp;"` → `0.0`

### Validación de Equilibrio Contable

Automáticamente valida que:
```
TOTAL ACTIVOS = TOTAL PASIVOS + TOTAL PATRIMONIO
```

Con tolerancia del 1% para manejar redondeos.

---

## 📝 Resultados de Pruebas

### Archivo 2004 (Pre-2010):
```
📅 Año detectado: 2004
📋 Formato: Pre-2010 (PCG)
✅ BALANCE GENERAL: 58 cuentas
✅ ESTADO DE GANANCIAS Y PERDIDAS: 36 cuentas
✅ ESTADO DE CAMBIOS EN EL PATRIMONIO NETO: 32 cuentas
✅ ESTADO DE FLUJO DE EFECTIVO: 107 cuentas
✅ Equilibrio contable OK: Activos = Pasivos + Patrimonio
```

**Validación de números:**
- Total Activos: 200,282
- Total Pasivos: 75,440
- Total Patrimonio: 124,842
- **Verificación: 75,440 + 124,842 = 200,282 ✅**

### Archivo 2024 (Post-2010):
```
📅 Año detectado: 2024
📋 Formato: Post-2010 (NIIF)
✅ ESTADO DE SITUACION FINANCIERA: 76 cuentas
✅ ESTADO DE RESULTADOS: 40 cuentas
✅ ESTADO DE CAMBIOS EN EL PATRIMONIO NETO: 48 cuentas
✅ ESTADO DE FLUJO DE EFECTIVO: 93 cuentas
✅ ESTADO DE RESULTADOS INTEGRALES: 41 cuentas
✅ Equilibrio contable OK: Activos = Pasivos + Patrimonio
```

**Validación de números:**
- Total Activos: 3,072,012
- Total Pasivos: 1,858,914
- Total Patrimonio: 1,213,098
- **Verificación: 1,858,914 + 1,213,098 = 3,072,012 ✅**

---

## 💻 Uso del Extractor

### Opción 1: Uso Simple
```python
from extractor_estados_mejorado import extraer_estados_desde_archivo

# Extraer todos los estados de un archivo
resultados = extraer_estados_desde_archivo('ruta/al/archivo.html')

# Acceder a los datos
print(f"Año: {resultados['año_documento']}")
print(f"Estados encontrados: {len(resultados['estados'])}")

# Acceder a un estado específico
balance = resultados['estados']['balance']
print(f"Años disponibles: {balance['años']}")

# Acceder a una cuenta específica
for cuenta in balance['cuentas']:
    if 'CAJA' in cuenta['nombre'].upper():
        print(f"{cuenta['nombre']}: {cuenta['valores']}")
```

### Opción 2: Uso Avanzado
```python
from extractor_estados_mejorado import ExtractorEstadosFinancieros

# Crear instancia
extractor = ExtractorEstadosFinancieros()

# Leer archivo HTML
with open('archivo.html', 'r', encoding='utf-8', errors='ignore') as f:
    html_content = f.read()

# Extraer estados
resultados = extractor.extraer_todos_estados(html_content, año_documento=2024)

# Validar equilibrio
if 'balance' in resultados['estados']:
    validacion = extractor._validar_equilibrio_contable(resultados['estados']['balance'])
    print(f"Equilibrio válido: {validacion['es_valido']}")
    
# Convertir a formato simple
simple = extractor.exportar_a_dict_simple(resultados)
```

---

## 🎯 Próximos Pasos

### 1. Integrar con el analizador principal
Reemplazar la extracción actual en `analizador_financiero.py` con este nuevo extractor.

### 2. Actualizar análisis vertical/horizontal
Adaptar `analisis_vertical_horizontal.py` para usar la nueva estructura de datos.

### 3. Crear interfaz Streamlit mejorada
Nueva aplicación que use el extractor mejorado con:
- Selección automática de formato según año
- Visualización de los 4-5 bloques separados
- Validación de equilibrio contable en tiempo real
- Exportación a Excel con todos los datos numéricos

### 4. Procesar todos los archivos de ejemplos
Aplicar el extractor a los 15 archivos HTML de la carpeta ejemplos y validar consistencia.

---

## 📊 Ventajas del Nuevo Extractor

1. **Precisión**: Identifica exactamente donde empieza y termina cada bloque
2. **Automático**: Detecta el formato (Pre/Post 2010) sin configuración manual
3. **Robusto**: Maneja todos los formatos de números y casos especiales
4. **Validado**: Verifica el equilibrio contable automáticamente
5. **Estructurado**: Datos organizados de forma clara y accesible
6. **Documentado**: Código bien documentado y probado

---

## 📈 Estadísticas de Extracción

| Aspecto | Archivo 2004 | Archivo 2024 |
|---------|--------------|--------------|
| **Año detectado** | 2004 ✅ | 2024 ✅ |
| **Formato** | Pre-2010 (PCG) | Post-2010 (NIIF) |
| **Estados extraídos** | 4/4 (100%) | 5/5 (100%) |
| **Total de cuentas** | 233 | 298 |
| **Balance** | 58 cuentas | 76 cuentas |
| **Resultados** | 36 cuentas | 40 cuentas |
| **Patrimonio** | 32 cuentas | 48 cuentas |
| **Flujo** | 107 cuentas | 93 cuentas |
| **Integrales** | N/A | 41 cuentas |
| **Equilibrio** | ✅ Válido | ✅ Válido |
| **Errores** | 0 | 0 |

---

## 🔧 Mantenimiento

### Agregar soporte para nuevos formatos:
1. Actualizar diccionarios `ESTADOS_PRE_2010` y `ESTADOS_POST_2010`
2. Ajustar lógica de detección en `_detectar_año()`
3. Probar con archivos de ejemplo

### Mejorar conversión de números:
1. Modificar método `_convertir_a_numero()`
2. Agregar casos especiales según sea necesario

---

## 🎓 Lecciones Aprendidas

1. **Estructura HTML consistente**: Los archivos SMV usan estructura muy regular
2. **Encoding issues**: Caracteres especiales (ñ) pueden tener problemas, usar `errors='ignore'`
3. **Nombres variables**: "FLUJO DE EFECTIVO" vs "FLUJOS DE EFECTIVO" requiere búsqueda flexible
4. **Validación crítica**: Siempre validar el equilibrio contable para detectar errores
5. **Año en metadata**: El año del documento está al inicio del HTML en formato específico

---

**Fecha**: 1 de octubre de 2025  
**Autor**: GitHub Copilot  
**Estado**: ✅ Completado y probado
