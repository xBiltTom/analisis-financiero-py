"""Script simple para debuggear la consolidación"""
import os
import sys

# Simular la estructura de resultados_analisis como la genera Streamlit
print("="*80)
print("DEBUG SIMPLE: VERIFICANDO FILTRO DE CONSOLIDACIÓN")
print("="*80 + "\n")

# Datos de prueba simulando lo que genera Streamlit
resultados_analisis = [
    {
        'archivo': 'ReporteDetalleInformacionFinanciero (15).html',
        'datos': {'año_documento': 2024, 'estados_financieros': {}},
        'resumen': {'empresa': 'CERVECERIA SAN JUAN S.A.'}
    },
    {
        'archivo': 'ReporteDetalleInformacionFinanciero (16).html',
        'datos': {'año_documento': 2023, 'estados_financieros': {}},
        'resumen': {'empresa': 'CERVECERIA SAN JUAN S.A.'}
    },
    {
        'archivo': 'ReporteDetalleInformacionFinanciero (17).html',
        'datos': {'año_documento': 2022, 'estados_financieros': {}},
        'resumen': {'empresa': 'CERVECERIA SAN JUAN S.A.'}
    },
    {
        'archivo': 'ReporteDetalleInformacionFinanciero (18).html',
        'datos': {'año_documento': 2021, 'estados_financieros': {}},
        'resumen': {'empresa': 'CERVECERIA SAN JUAN S.A.'}
    },
    {
        'archivo': 'ReporteDetalleInformacionFinanciero (19).html',
        'datos': {'año_documento': 2020, 'estados_financieros': {}},
        'resumen': {'empresa': 'CERVECERIA SAN JUAN S.A.'}
    }
]

print("Estructura de resultados_analisis:")
for i, r in enumerate(resultados_analisis):
    print(f"\n{i+1}. Archivo: {r['archivo']}")
    print(f"   Claves: {list(r.keys())}")
    print(f"   Año en 'datos': {r.get('datos', {}).get('año_documento', 'N/A')}")
    año_doc = r.get('datos', {}).get('año_documento', 0)
    print(f"   Acceso correcto: r.get('datos', dict()).get('año_documento', 0) = {año_doc}")
    print(f"   Es >= 2010: {r.get('datos', {}).get('año_documento', 0) >= 2010}")

print("\n" + "="*80)
print("FILTRO DE LA FUNCIÓN consolidar_multiples_archivos_post_2010:")
print("="*80 + "\n")

# Simular el filtro CORREGIDO
print("Código del filtro:")
print("archivos_post_2010 = [r for r in resultados_analisis if r.get('datos', {}).get('año_documento', 0) >= 2010]")
print()

archivos_post_2010 = [r for r in resultados_analisis if r.get('datos', {}).get('año_documento', 0) >= 2010]

print(f"Resultado del filtro:")
print(f"  Total archivos entrada: {len(resultados_analisis)}")
print(f"  Total archivos POST-2010: {len(archivos_post_2010)}")
print()

if archivos_post_2010:
    print("✅ FILTRO CORRECTO - Archivos encontrados:")
    for r in archivos_post_2010:
        año = r.get('datos', {}).get('año_documento', 0)
        print(f"   - {r['archivo']}: Año {año}")
else:
    print("❌ FILTRO INCORRECTO - No se encontraron archivos POST-2010")

print("\n" + "="*80)
