"""
Debug script para analizar el patrón de K y F en cada año
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor_estados_mejorado import ExtractorEstadosFinancieros

def debug_cxc_por_año():
    """Analiza las apariciones de Cuentas por Cobrar en cada año"""
    
    print("="*80)
    print("🔍 DEBUG: Análisis de Cuentas por Cobrar por Año")
    print("="*80)
    
    carpeta_cuentas = "cuentas"
    archivos_cuentas = []
    
    if os.path.exists(carpeta_cuentas):
        for archivo in sorted(os.listdir(carpeta_cuentas)):
            if archivo.endswith('.xls'):
                ruta_completa = os.path.join(carpeta_cuentas, archivo)
                archivos_cuentas.append(ruta_completa)
    
    if not archivos_cuentas:
        print("❌ No se encontraron archivos")
        return
    
    extractor = ExtractorEstadosFinancieros()
    
    # Procesar cada archivo y mostrar TODAS las cuentas por cobrar
    for archivo in archivos_cuentas:
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
            
            resultado = extractor.extraer_todos_estados(contenido)
            año = resultado['año_documento']
            
            print(f"\n{'='*80}")
            print(f"📅 AÑO {año}")
            print(f"{'='*80}")
            
            if 'balance' in resultado['estados']:
                balance = resultado['estados']['balance']
                cuentas = balance['cuentas']
                
                print(f"\n🔎 Buscando 'Cuentas por Cobrar' en Balance (Total: {len(cuentas)} cuentas)")
                print("-" * 80)
                
                contador = 0
                for i, cuenta in enumerate(cuentas):
                    nombre = cuenta['nombre'].upper()
                    
                    # Buscar cualquier mención de "CUENTAS POR COBRAR"
                    if 'CUENTAS' in nombre and 'COBRAR' in nombre:
                        contador += 1
                        valores = cuenta['valores']
                        
                        # Obtener valores del año actual y anterior
                        val_actual = valores.get(año) or valores.get(str(año)) or 0
                        
                        # Buscar año anterior
                        año_ant = año - 1
                        val_anterior = valores.get(año_ant) or valores.get(str(año_ant)) or 0
                        
                        print(f"\n#{contador} [Posición {i+1}]: {cuenta['nombre']}")
                        print(f"    {año}: {abs(val_actual):,.0f}")
                        print(f"    {año_ant}: {abs(val_anterior):,.0f}")
                        print(f"    Tiene 'Y OTRAS': {'Y OTRAS' in nombre}")
            
            # Mostrar Ingresos Ordinarios
            if 'resultados' in resultado['estados']:
                resultados = resultado['estados']['resultados']
                cuentas_res = resultados['cuentas']
                
                print(f"\n💰 Ingresos de Actividades Ordinarias:")
                print("-" * 80)
                
                for cuenta in cuentas_res:
                    nombre = cuenta['nombre'].upper()
                    if 'INGRESOS' in nombre and 'ACTIVIDADES' in nombre and 'ORDINARIAS' in nombre:
                        valores = cuenta['valores']
                        val = valores.get(año) or valores.get(str(año)) or 0
                        print(f"G ({año}): {abs(val):,.0f}")
                        break
                        
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
    
    print(f"\n{'='*80}")
    print("✅ Análisis completado")
    print(f"{'='*80}")

if __name__ == "__main__":
    debug_cxc_por_año()
