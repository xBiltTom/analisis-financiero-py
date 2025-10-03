"""
Debug: Analizar estructura completa del Estado de Situación Financiera
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo

print("="*80)
print("ANÁLISIS COMPLETO: ESTADO DE SITUACIÓN FINANCIERA")
print("="*80 + "\n")

# Procesar un archivo de ejemplo
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:1]

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    print(f"📄 Archivo: {archivo}")
    
    resultado = extraer_estados_desde_archivo(ruta)
    año = resultado['año_documento']
    print(f"📅 Año: {año}\n")
    
    # Obtener balance
    if 'balance' in resultado['estados']:
        balance = resultado['estados']['balance']
        print(f"🏦 ESTADO DE SITUACIÓN FINANCIERA")
        print(f"   Total cuentas: {balance['total_cuentas']}\n")
        
        print("📋 TODAS LAS CUENTAS (con valores):")
        print("-" * 80)
        
        # Detectar zonas
        en_activos = False
        en_pasivos = False
        en_patrimonio = False
        
        for i, cuenta in enumerate(balance['cuentas'], 1):
            nombre = cuenta['nombre']
            nombre_upper = nombre.upper()
            valor = cuenta['valores'].get(año, 0)
            es_total = '⭐' if cuenta.get('es_total') else '  '
            
            # Detectar cambio de sección
            if 'ACTIVO' in nombre_upper and not en_activos:
                print(f"\n{'='*80}")
                print(f"SECCIÓN: ACTIVOS")
                print(f"{'='*80}")
                en_activos = True
                en_pasivos = False
                en_patrimonio = False
            
            if 'PASIVO' in nombre_upper and not en_pasivos:
                print(f"\n{'='*80}")
                print(f"SECCIÓN: PASIVOS")
                print(f"{'='*80}")
                en_activos = False
                en_pasivos = True
                en_patrimonio = False
            
            if 'PATRIMONIO' in nombre_upper and not en_patrimonio:
                print(f"\n{'='*80}")
                print(f"SECCIÓN: PATRIMONIO")
                print(f"{'='*80}")
                en_activos = False
                en_pasivos = False
                en_patrimonio = True
            
            # Mostrar cuenta
            print(f"{es_total} {i:3}. {nombre:<60} = {valor:>15,.2f}")
        
        # Resumen por sección
        print(f"\n{'='*80}")
        print("RESUMEN:")
        print(f"{'='*80}")
        
        total_activos = 0
        total_pasivos = 0
        total_patrimonio = 0
        
        for cuenta in balance['cuentas']:
            nombre_upper = cuenta['nombre'].upper()
            valor = cuenta['valores'].get(año, 0)
            
            if 'TOTAL ACTIVOS' in nombre_upper or 'TOTAL DE ACTIVOS' in nombre_upper:
                if 'CORRIENTE' not in nombre_upper and 'NO CORRIENTE' not in nombre_upper:
                    total_activos = valor
            
            if 'TOTAL PASIVOS' in nombre_upper or 'TOTAL DE PASIVOS' in nombre_upper:
                if 'CORRIENTE' not in nombre_upper and 'NO CORRIENTE' not in nombre_upper:
                    total_pasivos = valor
            
            if 'TOTAL PATRIMONIO' in nombre_upper:
                total_patrimonio = valor
        
        print(f"\nTotal Activos:    {total_activos:>20,.2f}")
        print(f"Total Pasivos:    {total_pasivos:>20,.2f}")
        print(f"Total Patrimonio: {total_patrimonio:>20,.2f}")
        print(f"Suma P+P:         {(total_pasivos + total_patrimonio):>20,.2f}")
        print(f"\nEquilibrio: {'✅ OK' if abs(total_activos - (total_pasivos + total_patrimonio)) < 1 else '❌ ERROR'}")

print("\n" + "="*80)
