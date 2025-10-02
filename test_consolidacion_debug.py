"""Script para debuggear la consolidación en Streamlit"""
import os
from analizador_financiero import AnalizadorFinanciero

print("="*80)
print("DEBUG: SIMULACIÓN DE CONSOLIDACIÓN EN STREAMLIT")
print("="*80 + "\n")

# Crear analizador
analizador = AnalizadorFinanciero()

# Simular el procesamiento de archivos como lo hace Streamlit
archivos_html = sorted([
    "consolidar/ReporteDetalleInformacionFinanciero (15).html",
    "consolidar/ReporteDetalleInformacionFinanciero (16).html", 
    "consolidar/ReporteDetalleInformacionFinanciero (17).html",
    "consolidar/ReporteDetalleInformacionFinanciero (18).html",
    "consolidar/ReporteDetalleInformacionFinanciero (19).html"
])

resultados_analisis = []

print("PASO 1: Procesando archivos...\n")
for archivo_html in archivos_html:
    print(f"📄 Procesando: {archivo_html}")
    
    # Extraer datos (simula lo que hace Streamlit)
    datos_extraidos = analizador.extraer_datos_html(archivo_html)
    
    if datos_extraidos:
        # Generar resumen
        resumen = analizador.generar_resumen_analisis(datos_extraidos)
        
        # Agregar a resultados (IGUAL que en Streamlit)
        resultado = {
            'archivo': os.path.basename(archivo_html),
            'datos': datos_extraidos,  # ← CLAVE: se guarda en 'datos'
            'resumen': resumen
        }
        resultados_analisis.append(resultado)
        
        print(f"   ✅ Año documento: {datos_extraidos.get('año_documento', 'N/A')}")
        print(f"   ✅ Empresa: {resumen['empresa']}")
        print()
    else:
        print(f"   ❌ Error al extraer datos\n")

print("="*80)
print(f"PASO 2: Intentando consolidar {len(resultados_analisis)} archivos...\n")

# Debug: Verificar estructura antes de consolidar
print("DEBUG: Estructura de resultados_analisis:")
for i, resultado in enumerate(resultados_analisis):
    print(f"\nResultado {i+1}:")
    print(f"  - Claves: {list(resultado.keys())}")
    print(f"  - 'datos' existe: {'datos' in resultado}")
    print(f"  - 'datos_extraidos' existe: {'datos_extraidos' in resultado}")
    
    if 'datos' in resultado:
        datos = resultado['datos']
        print(f"  - 'datos' contiene 'año_documento': {'año_documento' in datos}")
        if 'año_documento' in datos:
            año = datos.get('año_documento', 'N/A')
            print(f"  - Año documento en 'datos': {año}")
            print(f"  - Año >= 2010: {año >= 2010 if isinstance(año, int) else 'N/A'}")

print("\n" + "="*80)
print("PASO 3: Llamando a consolidar_multiples_archivos_post_2010...\n")

consolidado = analizador.consolidar_multiples_archivos_post_2010(resultados_analisis)

if consolidado:
    print(f"✅ CONSOLIDACIÓN EXITOSA!")
    print(f"   Estados consolidados: {list(consolidado.keys())}")
    for nombre_estado, df in consolidado.items():
        print(f"   - {nombre_estado}: {len(df)} cuentas, {len(df.columns)-1} años")
else:
    print("❌ CONSOLIDACIÓN FALLÓ - No se generaron datos consolidados")

print("\n" + "="*80)
