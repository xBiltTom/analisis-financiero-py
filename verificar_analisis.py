"""
Script de prueba para visualizar los resultados del análisis vertical
"""
import pandas as pd

print("="*70)
print("📊 VERIFICACIÓN DE ANÁLISIS VERTICAL")
print("="*70)

# Cargar archivo 2004
print("\n🔹 Archivo 2004 (Pre-2010) - COMPAÑÍA UNIVERSAL TEXTIL S.A.")
print("-"*70)

try:
    # Leer hoja de Activos
    df_activos_2004 = pd.read_excel(
        "analisis_vertical_ReporteDetalleInformacionFinanciero (6).xlsx",
        sheet_name="Activos"
    )
    
    print("\n📋 ACTIVOS (Primeras 10 cuentas):")
    print(df_activos_2004.head(10).to_string(index=False))
    
    # Leer hoja de Pasivos
    df_pasivos_2004 = pd.read_excel(
        "analisis_vertical_ReporteDetalleInformacionFinanciero (6).xlsx",
        sheet_name="Pasivos"
    )
    
    print("\n📋 PASIVOS (Primeras 10 cuentas):")
    print(df_pasivos_2004.head(10).to_string(index=False))
    
    print(f"\n✅ Total cuentas Activos: {len(df_activos_2004)}")
    print(f"✅ Total cuentas Pasivos: {len(df_pasivos_2004)}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)

# Cargar archivo 2024
print("\n🔹 Archivo 2024 (Post-2010) - CEMENTOS PACASMAYO S.A.A.")
print("-"*70)

try:
    # Leer hoja de Activos
    df_activos_2024 = pd.read_excel(
        "analisis_vertical_REPORTE DETALLE FINANCIERO 2024.xlsx",
        sheet_name="Activos"
    )
    
    print("\n📋 ACTIVOS (Primeras 10 cuentas):")
    print(df_activos_2024.head(10).to_string(index=False))
    
    # Leer hoja de Pasivos
    df_pasivos_2024 = pd.read_excel(
        "analisis_vertical_REPORTE DETALLE FINANCIERO 2024.xlsx",
        sheet_name="Pasivos"
    )
    
    print("\n📋 PASIVOS (Primeras 10 cuentas):")
    print(df_pasivos_2024.head(10).to_string(index=False))
    
    # Leer hoja de Resultados
    df_resultados_2024 = pd.read_excel(
        "analisis_vertical_REPORTE DETALLE FINANCIERO 2024.xlsx",
        sheet_name="Resultados"
    )
    
    print("\n📋 ESTADO DE RESULTADOS (Primeras 10 cuentas):")
    print(df_resultados_2024.head(10).to_string(index=False))
    
    print(f"\n✅ Total cuentas Activos: {len(df_activos_2024)}")
    print(f"\n✅ Total cuentas Pasivos: {len(df_pasivos_2024)}")
    print(f"✅ Total cuentas Resultados: {len(df_resultados_2024)}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70)
