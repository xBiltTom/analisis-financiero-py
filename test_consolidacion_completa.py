"""
Test: Verificar consolidación de Estado de Situación Financiera
"""
import os
import pandas as pd
from extractor_estados_mejorado import extraer_estados_desde_archivo
from analizador_financiero import AnalizadorFinanciero

print("="*80)
print("TEST: CONSOLIDACIÓN DE ESTADO DE SITUACIÓN FINANCIERA")
print("="*80 + "\n")

# Procesar 2 archivos
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:2]

print(f"📁 Archivos a procesar: {len(archivos)}")
for archivo in archivos:
    print(f"  - {archivo}")

# Extraer datos de cada archivo
resultados_analisis = []
for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    print(f"\n📄 Procesando: {archivo}")
    
    resultado_extractor = extraer_estados_desde_archivo(ruta)
    año = resultado_extractor['año_documento']
    
    # Simular estructura esperada por consolidar_multiples_archivos_post_2010
    resultado = {
        'archivo': archivo,
        'datos': {
            'año_documento': año,
            'estados_financieros': {}
        },
        'datos_extractor': resultado_extractor,
        'resumen': {
            'empresa': resultado_extractor['metadatos'].get('empresa', 'N/A'),
            'año_reporte': str(año)
        }
    }
    
    # Convertir formato extractor a formato legacy
    # Solo para Estado de Situación Financiera
    if 'balance' in resultado_extractor['estados']:
        balance = resultado_extractor['estados']['balance']
        
        # Convertir cuentas
        cuentas_legacy = []
        for cuenta in balance['cuentas']:
            cuenta_legacy = {
                'cuenta': cuenta['nombre'],
                'es_total': cuenta['es_total']
            }
            
            # Agregar valores por año
            for año_data, valor in cuenta['valores'].items():
                cuenta_legacy[año_data] = {
                    'numero': valor,
                    'texto': f"{valor:,.0f}"
                }
            
            cuentas_legacy.append(cuenta_legacy)
        
        resultado['datos']['estados_financieros']['estado_situacion_financiera'] = {
            'nombre': 'ESTADO DE SITUACION FINANCIERA',
            'años': balance['años'],
            'datos': cuentas_legacy,
            'total_cuentas': balance['total_cuentas']
        }
        
        print(f"   ✅ Año: {año} | Cuentas: {balance['total_cuentas']}")
    
    resultados_analisis.append(resultado)

# Consolidar
print(f"\n{'='*80}")
print("CONSOLIDANDO...")
print("="*80)

analizador = AnalizadorFinanciero()
consolidado = analizador.consolidar_multiples_archivos_post_2010(resultados_analisis)

if 'estado_situacion_financiera' in consolidado:
    df = consolidado['estado_situacion_financiera']
    
    print(f"\n✅ Consolidación completada")
    print(f"📊 Total de cuentas consolidadas: {len(df)}")
    print(f"📅 Columnas (años): {[col for col in df.columns if col != 'Cuenta']}")
    
    print(f"\n{'='*80}")
    print("PRIMERAS 20 CUENTAS CONSOLIDADAS:")
    print("="*80)
    
    for i, row in df.head(20).iterrows():
        cuenta = row['Cuenta']
        años_cols = [col for col in df.columns if col != 'Cuenta']
        valores_str = " | ".join([f"{col}: {row[col]:>12,.0f}" for col in años_cols])
        print(f"{i+1:3}. {cuenta:<55} | {valores_str}")
    
    print(f"\n{'='*80}")
    print("ÚLTIMAS 10 CUENTAS CONSOLIDADAS:")
    print("="*80)
    
    for i, row in df.tail(10).iterrows():
        cuenta = row['Cuenta']
        años_cols = [col for col in df.columns if col != 'Cuenta']
        valores_str = " | ".join([f"{col}: {row[col]:>12,.0f}" for col in años_cols])
        print(f"{i+1:3}. {cuenta:<55} | {valores_str}")
    
    # Verificar totales
    print(f"\n{'='*80}")
    print("VERIFICACIÓN DE TOTALES:")
    print("="*80)
    
    for i, row in df.iterrows():
        cuenta_upper = row['Cuenta'].upper()
        if 'TOTAL DE ACTIVOS' in cuenta_upper or 'TOTAL ACTIVOS' == cuenta_upper:
            if 'CORRIENTE' not in cuenta_upper and 'NO CORRIENTE' not in cuenta_upper:
                años_cols = [col for col in df.columns if col != 'Cuenta']
                valores_str = " | ".join([f"{col}: {row[col]:>15,.0f}" for col in años_cols])
                print(f"✓ TOTAL ACTIVOS: {valores_str}")
        
        if 'TOTAL PASIVOS' in cuenta_upper or 'TOTAL DE PASIVOS' in cuenta_upper:
            if 'CORRIENTE' not in cuenta_upper and 'NO CORRIENTE' not in cuenta_upper:
                años_cols = [col for col in df.columns if col != 'Cuenta']
                valores_str = " | ".join([f"{col}: {row[col]:>15,.0f}" for col in años_cols])
                print(f"✓ TOTAL PASIVOS: {valores_str}")
        
        if 'TOTAL PATRIMONIO' in cuenta_upper:
            años_cols = [col for col in df.columns if col != 'Cuenta']
            valores_str = " | ".join([f"{col}: {row[col]:>15,.0f}" for col in años_cols])
            print(f"✓ TOTAL PATRIMONIO: {valores_str}")

else:
    print("❌ No se encontró estado_situacion_financiera en consolidado")

print(f"\n{'='*80}")
print("✅ TEST COMPLETADO")
print("="*80)
