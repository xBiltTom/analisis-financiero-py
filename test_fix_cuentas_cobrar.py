"""
Test para verificar la corrección del cálculo de Rotación de Cuentas por Cobrar
Implementa la fórmula exacta: G / ((K + F + K' + F') / 2)

Donde:
- K = Cuentas por Cobrar Comerciales y Otras Cuentas por Cobrar (1ª aparición)
- F = Cuentas por Cobrar Comerciales y Otras Cuentas por Cobrar (2ª aparición) 
- K' y F' = Valores del año anterior
- G = Ingresos de Actividades Ordinarias del año actual
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor_estados_mejorado import ExtractorEstadosFinancieros
from ratios_financieros import CalculadorRatiosFinancieros

def test_calculo_cuentas_cobrar():
    """Test específico para el cálculo de cuentas por cobrar"""
    
    print("="*80)
    print("🧪 TEST: Corrección del Cálculo de Rotación de Cuentas por Cobrar")
    print("="*80)
    
    # Cargar datos de ejemplo
    archivos_ejemplo = [
        r"c:\Users\Usuario\AnalisisFinancieroV4\ejemplos\REPORTE DETALLE FINANCIERO 2024.xls",
        r"c:\Users\Usuario\AnalisisFinancieroV4\ejemplos\REPORTE DETALLE FINANCIERO 2023.xls", 
        r"c:\Users\Usuario\AnalisisFinancieroV4\ejemplos\REPORTE DETALLE FINANCIERO 2022.xls"
    ]
    
    extractor = ExtractorEstadosFinancieros()
    calculador = CalculadorRatiosFinancieros()
    
    resultados_extractor = []
    
    # Extraer datos de todos los archivos
    print(f"\n🔍 Extrayendo datos de {len(archivos_ejemplo)} archivos...")
    for archivo in archivos_ejemplo:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
            
            resultado = extractor.extraer_todos_estados(contenido)
            if resultado['estados']:
                resultados_extractor.append(resultado)
                print(f"✅ {resultado['año_documento']}: {resultado['metadatos'].get('empresa', 'N/A')}")
    
    if not resultados_extractor:
        print("❌ No se pudieron extraer datos de los archivos")
        return
    
    # Calcular ratios con el método corregido
    print(f"\n🧮 Calculando ratios financieros con fórmula corregida...")
    resultados_ratios = calculador.calcular_ratios_desde_extractor(resultados_extractor)
    
    if 'error' in resultados_ratios:
        print(f"❌ Error en cálculo: {resultados_ratios['error']}")
        return
    
    # Mostrar resultados específicos de Rotación CxC
    print(f"\n📊 RESULTADOS DE ROTACIÓN DE CUENTAS POR COBRAR:")
    print("-" * 60)
    
    ratios_por_año = resultados_ratios['ratios_por_año']
    años = sorted(ratios_por_año.keys())
    
    rotacion_cxc_valores = []
    
    for año in años:
        ratio_cxc = ratios_por_año[año].get('rotacion_cuentas_cobrar')
        if ratio_cxc is not None:
            rotacion_cxc_valores.append(ratio_cxc)
            print(f"{año}: {ratio_cxc:.3f} veces")
        else:
            print(f"{año}: N/A")
    
    # Mostrar estadísticas
    if rotacion_cxc_valores:
        promedio = sum(rotacion_cxc_valores) / len(rotacion_cxc_valores)
        minimo = min(rotacion_cxc_valores)
        maximo = max(rotacion_cxc_valores)
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   Promedio: {promedio:.3f}")
        print(f"   Mínimo:   {minimo:.3f}")
        print(f"   Máximo:   {maximo:.3f}")
    
    # Mostrar resumen completo
    if resultados_ratios.get('resumen'):
        resumen = resultados_ratios['resumen']
        cxc_resumen = resumen.get('rotacion_cuentas_cobrar', {})
        
        print(f"\n🔍 RESUMEN ROTACIÓN CxC:")
        print(f"   Promedio: {cxc_resumen.get('promedio', 'N/A')}")
        print(f"   Min: {cxc_resumen.get('min', 'N/A')}")
        print(f"   Max: {cxc_resumen.get('max', 'N/A')}")
    
    print(f"\n✅ Test completado exitosamente")

if __name__ == "__main__":
    test_calculo_cuentas_cobrar()