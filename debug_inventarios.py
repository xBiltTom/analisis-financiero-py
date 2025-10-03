"""
Debug: Verificar nombres de cuentas para detectar Inventarios
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo

print("="*80)
print("DEBUG: NOMBRES DE CUENTAS DEL BALANCE")
print("="*80 + "\n")

# Procesar un archivo de ejemplo
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:1]  # Solo 1 archivo

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    print(f"📄 Archivo: {archivo}")
    
    resultado = extraer_estados_desde_archivo(ruta)
    año = resultado['año_documento']
    print(f"📅 Año: {año}\n")
    
    # Obtener balance
    if 'balance' in resultado['estados']:
        balance = resultado['estados']['balance']
        print(f"🏦 ESTADO DE SITUACIÓN FINANCIERA ({balance['total_cuentas']} cuentas)\n")
        
        # Buscar cuentas relacionadas con Activos Corrientes
        print("🔍 ACTIVOS CORRIENTES:")
        print("-" * 80)
        for cuenta in balance['cuentas']:
            nombre = cuenta['nombre']
            if 'ACTIVO' in nombre.upper() and 'CORRIENTE' in nombre.upper():
                valor = cuenta['valores'].get(año, 0)
                print(f"  ✓ {nombre:<60} = {valor:>15,.2f}")
        
        print("\n🔍 INVENTARIOS / EXISTENCIAS:")
        print("-" * 80)
        for cuenta in balance['cuentas']:
            nombre = cuenta['nombre']
            nombre_upper = nombre.upper()
            if 'INVENTARIO' in nombre_upper or 'EXISTENCIA' in nombre_upper:
                valor = cuenta['valores'].get(año, 0)
                print(f"  ✓ {nombre:<60} = {valor:>15,.2f}")
        
        print("\n🔍 PASIVOS CORRIENTES:")
        print("-" * 80)
        for cuenta in balance['cuentas']:
            nombre = cuenta['nombre']
            if 'PASIVO' in nombre.upper() and 'CORRIENTE' in nombre.upper():
                valor = cuenta['valores'].get(año, 0)
                print(f"  ✓ {nombre:<60} = {valor:>15,.2f}")
        
        print("\n📋 TODAS LAS CUENTAS (primeras 30):")
        print("-" * 80)
        for i, cuenta in enumerate(balance['cuentas'][:30], 1):
            nombre = cuenta['nombre']
            valor = cuenta['valores'].get(año, 0)
            es_total = '⭐' if cuenta.get('es_total') else '  '
            print(f"{es_total} {i:2}. {nombre:<55} = {valor:>15,.2f}")

print("\n" + "="*80)
