# Análisis de Estructura de Bloques - Estados Financieros

## Resumen Ejecutivo
Los archivos HTML tienen una estructura clara donde cada estado financiero está delimitado por:
1. **Inicio**: `<span style="font-weight:bold;">NOMBRE DEL ESTADO</span>`
2. **Contenido**: Una tabla HTML `<table>` con los datos
3. **Fin**: Tag de cierre `</table>` seguido de `</div></form>`

## Estructura por Año

### 📊 AÑOS ≤ 2009 (Formato Antiguo)

#### 1. BALANCE GENERAL
- **Inicio**: `<span style="font-weight:bold;">BALANCE GENERAL</span>`
- **Estructura**:
  - Header: `Cuenta | NOTA | [Años]` (ej: 2004, 2003)
  - Secciones principales:
    * **Activo** → **Activo Corriente** → cuentas → **Total Activo Corriente**
    * **Activo No Corriente** → cuentas → **Total Activo No Corriente**
    * **TOTAL ACTIVO** (clase "pinta")
    * **Pasivo y Patrimonio** → **Pasivo Corriente** → cuentas → **Total Pasivo Corriente**
    * **Pasivo No Corriente** → cuentas → **Total Pasivo No Corriente**
    * **Total Pasivo** (clase "pinta")
    * **Patrimonio Neto** → cuentas → **Total Patrimonio Neto**
    * **TOTAL PASIVO Y PATRIMONIO NETO** (clase "pinta")
- **Formato números**: `1,511` | `25,178` | `(15,099)` (negativos en paréntesis)
- **Fin**: `</table></div></form>`

#### 2. ESTADO DE GANANCIAS Y PERDIDAS
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE GANANCIAS Y PERDIDAS</span>`
- **Estructura**:
  - Header: `Cuenta | NOTA | [Años]`
  - Secciones:
    * **Ingresos Operacionales** → cuentas → **Total de Ingresos Brutos**
    * Costo de Ventas → **Utilidad Bruta**
    * **Gastos Operacionales** → cuentas → **Utilidad Operativa**
    * **Otros Ingresos (gastos)** → cuentas → Resultado antes de impuestos
    * Impuestos y participaciones
    * **Utilidad (Perdida) Neta del Ejercicio**
    * Utilidad por acción
- **Formato números**: `91,334` | `(69,173)` | `0.038`
- **Fin**: `</table></div></form>`

#### 3. ESTADO DE CAMBIOS EN EL PATRIMONIO NETO
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE CAMBIOS EN EL PATRIMONIO NETO</span>`
- **Estructura**:
  - Header: `CCUENTA | Cuenta | Capital | Capital Adicional | Acciones de Inversión | ... | Total`
  - Filas especiales con códigos: `4D0101`, `4D0102`, etc.
  - Saldos iniciales y finales: clase "background-color:LightGrey"
  - Movimientos del período
- **Formato números**: Igual que balance
- **Fin**: `</table></div></form>`

#### 4. ESTADO DE FLUJO DE EFECTIVO (sin "S")
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE FLUJO DE EFECTIVO</span>`
- **Estructura**:
  - **ACTIVIDADES DE OPERACIÓN** → Cobranzas → Pagos → Subtotal
  - **ACTIVIDADES DE INVERSIÓN** → Cobranzas → Pagos → Subtotal
  - **ACTIVIDADES DE FINANCIACION** → Cobranzas → Pagos → Subtotal
  - Aumento/Disminución Neto
  - Saldo inicial y final
  - **CONCILIACIÓN DE LA UTILIDAD NETA**
- **Formato números**: `99,778` | `(51,074)`
- **Fin**: `</table></div></form>`

---

### 📈 AÑOS ≥ 2010 (Formato NIIF)

#### 1. ESTADO DE SITUACION FINANCIERA
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE SITUACION FINANCIERA</span>`
- **Estructura**:
  - Header: `Cuenta | NOTA | [Años]` (ej: 2024, 2023)
  - Secciones principales:
    * **Activos** → **Activos Corrientes** → cuentas detalladas → **Total Activos Corrientes**
    * **Activos No Corrientes** → cuentas detalladas → **Total Activos No Corrientes**
    * **TOTAL DE ACTIVOS** (clase "pinta")
    * **Pasivos y Patrimonio** → **Pasivos Corrientes** → cuentas → **Total Pasivos Corrientes**
    * **Pasivos No Corrientes** → cuentas → **Total Pasivos No Corrientes**
    * **Total Pasivos** (clase "pinta")
    * **Patrimonio** → cuentas → **Total Patrimonio**
    * **TOTAL PASIVO Y PATRIMONIO** (clase "pinta")
- **Cuentas nuevas**: "Efectivo y Equivalentes al Efectivo", "Propiedades, Planta y Equipo"
- **Formato números**: `25,019` | `(121,258)` | `3,072,012`
- **Fin**: `</table></div></form>`

#### 2. ESTADO DE RESULTADOS
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE RESULTADOS</span>`
- **Estructura**:
  - **Ingresos de Actividades Ordinarias**
  - Costo de Ventas
  - **Ganancia (Pérdida) Bruta**
  - Gastos de Ventas y Distribución
  - Gastos de Administración
  - Otros ingresos/gastos operativos
  - **Ganancia (Pérdida) Operativa**
  - Ingresos y gastos financieros
  - **Ganancia (Pérdida) antes de Impuestos**
  - Impuesto a la Renta
  - **Ganancia (Pérdida) Neta del Ejercicio**
  - Ganancias por acción (básica y diluida)
- **Formato números**: `1,232,589` | `(721,363)` | `0.460`
- **Fin**: `</table></div></form>`

#### 3. ESTADO DE CAMBIOS EN EL PATRIMONIO NETO
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE CAMBIOS EN EL PATRIMONIO NETO</span>`
- **Estructura similar a ≤2009 pero con más columnas NIIF**:
  - Capital Emitido, Primas de Emisión, Acciones de Inversión
  - Acciones Propias en Cartera
  - Reservas múltiples (nuevas mediciones, coberturas, etc.)
  - Resultados Acumulados
  - Total Patrimonio
- **Códigos**: `4D0101`, `4D0126`, `4D0127`, etc.
- **Fin**: `</table></div></form>`

#### 4. ESTADO DE FLUJO DE EFECTIVO (sin "S")
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE FLUJO DE EFECTIVO</span>`
- **Estructura**: Similar a ≤2009 con terminología NIIF
- **Actividades de Operación, Inversión y Financiamiento**
- **Fin**: `</table></div></form>`

#### 5. ESTADO DE RESULTADOS INTEGRALES ⭐ (SOLO ≥2010)
- **Inicio**: `<span style="font-weight:bold;">ESTADO DE RESULTADOS INTEGRALES </span>`
- **Nuevo estado exclusivo de NIIF**
- **Estructura**:
  - Ganancia (Pérdida) Neta del Ejercicio
  - Otro Resultado Integral (componentes)
  - Resultado Integral Total del Ejercicio
- **Fin**: `</table></div></form>`

---

## Patrones de Identificación

### Clases CSS importantes:
- `class="pinta"` → Totales y subtotales (fondo gris #BDBDBD, alineación derecha)
- `background-color:LightGrey` → Saldos iniciales/finales en cambios de patrimonio
- `background-color:#FFFFFF` / sin background → Filas de datos alternadas

### Patrones de texto para totales:
```python
TOTALES_ACTIVOS = [
    "TOTAL ACTIVO", "TOTAL DE ACTIVOS", "Total Activo", 
    "Total Activos Corrientes", "Total Activos No Corrientes"
]

TOTALES_PASIVOS = [
    "TOTAL PASIVO", "Total Pasivo", "Total Pasivos",
    "Total Pasivos Corrientes", "Total Pasivos No Corrientes"
]

TOTALES_PATRIMONIO = [
    "TOTAL PATRIMONIO NETO", "Total Patrimonio Neto", 
    "Total Patrimonio", "PATRIMONIO NETO"
]

TOTALES_PASIVO_PATRIMONIO = [
    "TOTAL PASIVO Y PATRIMONIO NETO", 
    "TOTAL PASIVO Y PATRIMONIO",
    "TOTAL DE PASIVOS Y PATRIMONIO"
]
```

### Formato de números:
- **Separador de miles**: Coma `,`
- **Separador decimal**: Punto `.`
- **Negativos**: Entre paréntesis `(1,234)` o con signo `-`
- **Ceros**: `0` o cadena vacía

---

## Algoritmo de Extracción Propuesto

```python
def extraer_bloque_estado_financiero(html_content, nombre_estado, año_documento):
    """
    1. Buscar el span con el nombre exacto del estado
    2. Encontrar la tabla siguiente (<table>)
    3. Extraer el header para identificar columnas de años
    4. Iterar por cada <tr> (fila):
       - Si tiene class="pinta" → es subtotal/total
       - Primera <td> → nombre de cuenta
       - Segunda <td> → NOTA (generalmente ignorar)
       - Siguientes <td> → valores por año
    5. Convertir cada valor de texto a número
    6. Detectar fin cuando se encuentra </table></div></form>
    7. Retornar estructura dict con:
       {
         'nombre': nombre_estado,
         'años': [2024, 2023],
         'cuentas': [
           {'nombre': 'Efectivo y Equivalentes', 
            'es_total': False,
            'valores': {2024: 25019.0, 2023: 26973.0}},
           ...
         ]
       }
    """
```

## Validaciones Importantes

1. **Equilibrio contable**: TOTAL ACTIVO = TOTAL PASIVO + TOTAL PATRIMONIO
2. **Años consistentes**: Mismos años en todos los estados
3. **Números válidos**: Todos convertibles a float
4. **Estructura completa**: Los 4 bloques deben existir (5 para ≥2010)

---

## Ejemplos de Extracción

### Ejemplo 1: Fila simple de Activo (2004)
```html
<tr style="font-size:8pt;">
    <td>Caja y Bancos</td>
    <td style="width:50px;">0</td>
    <td style="width:50px;">1,511</td>
    <td style="width:50px;">389</td>
</tr>
```
**Resultado**: 
```python
{
  'nombre': 'Caja y Bancos',
  'nota': '0',
  'es_total': False,
  'valores': {2004: 1511.0, 2003: 389.0}
}
```

### Ejemplo 2: Total Activo (clase pinta)
```html
<tr style="color:#000000;background-color:#FFFFFF;font-size:8pt;">
    <td class="pinta">TOTAL ACTIVO</td>
    <td class="pinta" style="width:50px;">0</td>
    <td class="pinta" style="width:50px;">200,282</td>
    <td class="pinta" style="width:50px;">205,650</td>
</tr>
```
**Resultado**:
```python
{
  'nombre': 'TOTAL ACTIVO',
  'nota': '0',
  'es_total': True,
  'valores': {2004: 200282.0, 2003: 205650.0}
}
```

### Ejemplo 3: Valor negativo (2024)
```html
<tr style="font-size:8pt;">
    <td>Acciones Propias en Cartera</td>
    <td style="width:50px;">16(c)</td>
    <td style="width:50px;">(121,258)</td>
    <td style="width:50px;">(121,258)</td>
</tr>
```
**Resultado**:
```python
{
  'nombre': 'Acciones Propias en Cartera',
  'nota': '16(c)',
  'es_total': False,
  'valores': {2024: -121258.0, 2023: -121258.0}
}
```

---

## Resumen de Diferencias Clave

| Aspecto | ≤ 2009 | ≥ 2010 |
|---------|--------|--------|
| **Estado 1** | BALANCE GENERAL | ESTADO DE SITUACION FINANCIERA |
| **Estado 2** | ESTADO DE GANANCIAS Y PERDIDAS | ESTADO DE RESULTADOS |
| **Estado 3** | Igual nombre | Igual nombre (más columnas) |
| **Estado 4** | ESTADO DE FLUJO DE EFECTIVO | ESTADO DE FLUJO DE EFECTIVO |
| **Estado 5** | ❌ No existe | ✅ ESTADO DE RESULTADOS INTEGRALES |
| **Terminología** | PCG Peruano antiguo | NIIF/NIC |
| **Cuentas** | "Caja y Bancos" | "Efectivo y Equivalentes al Efectivo" |

---

**Fecha de análisis**: 1 de octubre de 2025  
**Archivos analizados**: 
- ReporteDetalleInformacionFinanciero (6).html (2004-2003)
- REPORTE DETALLE FINANCIERO 2024.html (2024-2023)
