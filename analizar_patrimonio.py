"""
Análisis del Estado de Cambios en el Patrimonio
Para entender la estructura y qué columnas extraer
"""
from extractor_estados_mejorado import extraer_estados_desde_archivo
import os

print("="*80)
print("ANÁLISIS: ESTADO DE CAMBIOS EN EL PATRIMONIO")
print("="*80 + "\n")

carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])

for i, archivo in enumerate(archivos[:2], 1):  # Solo primeros 2 archivos para análisis
    ruta = os.path.join(carpeta, archivo)
    print(f"\n{'='*80}")
    print(f"ARCHIVO {i}: {archivo}")
    print("="*80)
    
    try:
        resultado = extraer_estados_desde_archivo(ruta)
        año = resultado['año_documento']
        
        if 'patrimonio' in resultado['estados']:
            patrimonio = resultado['estados']['patrimonio']
            
            print(f"\n📊 Estado: {patrimonio['nombre']}")
            print(f"📅 Años disponibles: {patrimonio['años']}")
            print(f"📋 Total cuentas: {patrimonio['total_cuentas']}")
            
            print(f"\n🔍 ESTRUCTURA DE CUENTAS (primeras 15):")
            print("-"*80)
            
            for idx, cuenta in enumerate(patrimonio['cuentas'][:15], 1):
                nombre = cuenta['nombre']
                valores = cuenta['valores']
                es_total = cuenta.get('es_total', False)
                
                # Mostrar valores disponibles por año
                valores_str = " | ".join([f"{año}: {val:,.0f}" for año, val in sorted(valores.items(), reverse=True)])
                
                tipo = "TOTAL" if es_total else "CUENTA"
                print(f"{idx:2d}. [{tipo}] {nombre}")
                print(f"    Valores: {valores_str}")
            
            # Buscar columna "Total Patrimonio"
            print(f"\n🔍 BUSCANDO COLUMNA 'Total Patrimonio':")
            print("-"*80)
            
            for idx, cuenta in enumerate(patrimonio['cuentas'], 1):
                nombre_upper = cuenta['nombre'].upper()
                if 'TOTAL' in nombre_upper and 'PATRIMONIO' in nombre_upper:
                    print(f"✅ Encontrada en posición {idx}: {cuenta['nombre']}")
                    print(f"   Valores: {cuenta['valores']}")
            
            # Mostrar las últimas 10 cuentas (donde suele estar el total)
            print(f"\n🔍 ÚLTIMAS 10 CUENTAS:")
            print("-"*80)
            
            for cuenta in patrimonio['cuentas'][-10:]:
                nombre = cuenta['nombre']
                valores = cuenta['valores']
                valores_str = " | ".join([f"{año}: {val:,.0f}" for año, val in sorted(valores.items(), reverse=True)])
                print(f"• {nombre}")
                print(f"  {valores_str}")
        
        else:
            print("❌ No se encontró estado de patrimonio")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("FIN DEL ANÁLISIS")
print("="*80)
