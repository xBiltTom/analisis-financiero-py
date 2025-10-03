"""
Test del Análisis Vertical Consolidado
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo
from analisis_vertical_mejorado import AnalisisVerticalMejorado
from analisis_vertical_consolidado import AnalisisVerticalConsolidado

print("="*80)
print("TEST: ANÁLISIS VERTICAL CONSOLIDADO")
print("="*80 + "\n")

# Procesar múltiples archivos de la carpeta consolidar
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:3]  # Primeros 3

print(f"📁 Archivos a procesar: {len(archivos)}")
for archivo in archivos:
    print(f"  - {archivo}")

# Paso 1: Extraer estados financieros de cada archivo
print(f"\n{'='*80}")
print("PASO 1: Extrayendo estados financieros...")
print("="*80)

resultados_extractor_list = []
for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    print(f"\n📄 Procesando: {archivo}")
    resultado = extraer_estados_desde_archivo(ruta)
    resultados_extractor_list.append(resultado)
    print(f"   ✅ Año: {resultado['año_documento']} | Estados: {len(resultado['estados'])}")

# Paso 2: Realizar análisis vertical individual
print(f"\n{'='*80}")
print("PASO 2: Realizando análisis vertical individual...")
print("="*80)

analizador_vertical = AnalisisVerticalMejorado()
resultados_analisis_list = []

for i, resultado_extractor in enumerate(resultados_extractor_list):
    año = resultado_extractor['año_documento']
    print(f"\n📊 Analizando año {año}...")
    analisis = analizador_vertical.analizar_desde_extractor(resultado_extractor)
    resultados_analisis_list.append(analisis)
    
    # Mostrar resumen
    if 'balance' in analisis['estados_analizados']:
        balance = analisis['estados_analizados']['balance']
        print(f"   ✅ Balance: {balance['total_cuentas_activos']} activos, {balance['total_cuentas_pasivos']} pasivos")

# Paso 3: Consolidar análisis vertical
print(f"\n{'='*80}")
print("PASO 3: Consolidando análisis vertical...")
print("="*80)

consolidador = AnalisisVerticalConsolidado()
consolidado = consolidador.consolidar_analisis_vertical(resultados_analisis_list)

print(f"\n✅ Estados consolidados: {len(consolidado)}")
for nombre_estado, df in consolidado.items():
    print(f"\n📊 {nombre_estado.upper().replace('_', ' ')}")
    print(f"   Cuentas: {len(df)}")
    print(f"   Columnas: {list(df.columns)}")
    
    # Mostrar primeras 5 filas
    print(f"\n   Primeras 5 cuentas:")
    print(df.head().to_string(index=False))

# Paso 4: Exportar a Excel
print(f"\n{'='*80}")
print("PASO 4: Exportando a Excel...")
print("="*80)

archivo_salida = "test_analisis_vertical_consolidado.xlsx"
consolidador.exportar_consolidado_excel(consolidado, archivo_salida)

print(f"\n{'='*80}")
print("✅ TEST COMPLETADO")
print("="*80)
