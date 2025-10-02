"""
Test de la nueva extracción mejorada del Estado de Cambios en el Patrimonio
Con 3 columnas: CCUENTA, Cuenta, Total Patrimonio
"""
from extractor_estados_mejorado import extraer_estados_desde_archivo
import pandas as pd

print("="*80)
print("TEST: ESTADO DE CAMBIOS EN EL PATRIMONIO MEJORADO")
print("="*80 + "\n")

# Probar con un archivo
archivo = "consolidar/ReporteDetalleInformacionFinanciero (15).html"

print(f"📄 Procesando: {archivo}\n")

resultado = extraer_estados_desde_archivo(archivo)

if 'patrimonio' in resultado['estados']:
    patrimonio = resultado['estados']['patrimonio']
    
    print(f"✅ Estado: {patrimonio['nombre']}")
    print(f"📅 Años: {patrimonio['años']}")
    print(f"📋 Total cuentas: {patrimonio['total_cuentas']}")
    print(f"🔧 Columnas especiales: {patrimonio.get('columnas_especiales', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("PRIMERAS 15 CUENTAS:")
    print("="*80 + "\n")
    
    # Crear DataFrame para mostrar
    filas = []
    for cuenta in patrimonio['cuentas'][:15]:
        ccuenta = cuenta.get('ccuenta', '')
        nombre = cuenta['nombre']
        año = patrimonio['años'][0]
        valor = cuenta['valores'].get(año, 0)
        
        filas.append({
            'CCUENTA': ccuenta,
            'Cuenta': nombre[:60],  # Truncar para mostrar
            f'Total Patrimonio {año}': f"{valor:,.0f}"
        })
    
    df = pd.DataFrame(filas)
    print(df.to_string(index=False))
    
    print(f"\n{'='*80}")
    print("ÚLTIMAS 10 CUENTAS:")
    print("="*80 + "\n")
    
    filas = []
    for cuenta in patrimonio['cuentas'][-10:]:
        ccuenta = cuenta.get('ccuenta', '')
        nombre = cuenta['nombre']
        año = patrimonio['años'][0]
        valor = cuenta['valores'].get(año, 0)
        
        filas.append({
            'CCUENTA': ccuenta,
            'Cuenta': nombre[:60],
            f'Total Patrimonio {año}': f"{valor:,.0f}"
        })
    
    df = pd.DataFrame(filas)
    print(df.to_string(index=False))
    
    # Buscar saldo final
    print(f"\n{'='*80}")
    print("BUSCANDO SALDO FINAL:")
    print("="*80 + "\n")
    
    for cuenta in patrimonio['cuentas']:
        if 'SALDOS' in cuenta['nombre'].upper() and 'DICIEMBRE' in cuenta['nombre'].upper():
            print(f"✅ Encontrado: {cuenta['nombre']}")
            print(f"   CCUENTA: {cuenta.get('ccuenta', 'N/A')}")
            print(f"   Valor: {cuenta['valores'].get(patrimonio['años'][0], 0):,.0f}")

else:
    print("❌ No se encontró el estado de patrimonio")

print("\n" + "="*80)
print("TEST COMPLETADO")
print("="*80)
