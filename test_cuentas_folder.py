"""
Test para analizar los archivos de la carpeta "cuentas" y corregir el cálculo de Rotación CxC
Datos esperados para 2024:
- G = 1,232,589 (Ingresos Ordinarios)
- K = 74,372 (Primera aparición CxC)
- F = 40,945 (Segunda aparición CxC)
- K' = 17,682 (Primera aparición 2023)
- F' = 40,569 (Segunda aparición 2023)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor_estados_mejorado import ExtractorEstadosFinancieros
from ratios_financieros import CalculadorRatiosFinancieros

def test_archivos_cuentas():
    """Test con archivos de la carpeta cuentas"""
    
    print("="*80)
    print("🧪 TEST: Análisis de archivos carpeta 'cuentas'")
    print("="*80)
    
    # Archivos de la carpeta cuentas
    carpeta_cuentas = "cuentas"
    archivos_cuentas = []
    
    # Buscar archivos en la carpeta cuentas
    if os.path.exists(carpeta_cuentas):
        for archivo in sorted(os.listdir(carpeta_cuentas)):
            if archivo.endswith('.xls'):
                ruta_completa = os.path.join(carpeta_cuentas, archivo)
                archivos_cuentas.append(ruta_completa)
    
    if not archivos_cuentas:
        print("❌ No se encontraron archivos XLS en la carpeta 'cuentas'")
        return
    
    print(f"📂 Archivos encontrados en carpeta 'cuentas': {len(archivos_cuentas)}")
    for archivo in archivos_cuentas:
        print(f"   📄 {archivo}")
    
    extractor = ExtractorEstadosFinancieros()
    calculador = CalculadorRatiosFinancieros()
    
    resultados_extractor = []
    
    # Extraer datos de todos los archivos
    print(f"\n🔍 Extrayendo datos de archivos...")
    for archivo in archivos_cuentas:
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
            
            resultado = extractor.extraer_todos_estados(contenido)
            if resultado['estados']:
                resultados_extractor.append(resultado)
                print(f"✅ {resultado['año_documento']}: {resultado['metadatos'].get('empresa', 'N/A')}")
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
    
    if not resultados_extractor:
        print("❌ No se pudieron extraer datos de los archivos")
        return
    
    # Ordenar por año
    resultados_extractor.sort(key=lambda x: x['año_documento'])
    
    print(f"\n🧮 Calculando ratios financieros...")
    resultados_ratios = calculador.calcular_ratios_desde_extractor(resultados_extractor)
    
    if 'error' in resultados_ratios:
        print(f"❌ Error en cálculo: {resultados_ratios['error']}")
        return
    
    # Mostrar resultados específicos de 2024
    print(f"\n📊 RESULTADOS ROTACIÓN CUENTAS POR COBRAR:")
    print("-" * 70)
    
    ratios_por_año = resultados_ratios['ratios_por_año']
    años = sorted(ratios_por_año.keys())
    
    for año in años:
        ratio_cxc = ratios_por_año[año].get('rotacion_cuentas_cobrar')
        if ratio_cxc is not None:
            print(f"{año}: {ratio_cxc:.3f} veces")
        else:
            print(f"{año}: N/A")
    
    # Validación específica para 2024
    if 2024 in ratios_por_año:
        print(f"\n🎯 VALIDACIÓN ESPECÍFICA PARA 2024:")
        print(f"   Datos esperados:")
        print(f"   - G (Ingresos 2024): 1,232,589")
        print(f"   - K (CxC Primera 2024): 74,372")
        print(f"   - F (CxC Segunda 2024): 40,945")
        print(f"   - K' (CxC Primera 2023): 17,682")
        print(f"   - F' (CxC Segunda 2023): 40,569")
        print(f"   - Promedio CxC = (74,372 + 40,945 + 17,682 + 40,569) / 2 = 86,784")
        print(f"   - Rotación esperada = 1,232,589 / 86,784 = 14.205 veces")
        
        ratio_real = ratios_por_año[2024]['rotacion_cuentas_cobrar']
        print(f"   - Rotación calculada: {ratio_real:.3f} veces")
        
        if abs(ratio_real - 14.205) < 0.1:
            print(f"   ✅ CÁLCULO CORRECTO")
        else:
            print(f"   ❌ CÁLCULO INCORRECTO - Revisar detección de K y F")
    
    print(f"\n✅ Test completado")

if __name__ == "__main__":
    test_archivos_cuentas()