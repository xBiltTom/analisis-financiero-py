"""
Test de integración del análisis horizontal en analizador_financiero.py
"""

from extractor_estados_mejorado import ExtractorEstadosFinancieros
from analisis_horizontal_mejorado import AnalisisHorizontalMejorado

def test_flujo_completo():
    """Simula el flujo completo de la aplicación"""
    print("="*70)
    print("TEST DE INTEGRACIÓN - ANÁLISIS HORIZONTAL")
    print("="*70)
    
    # 1. Crear instancias (como lo hace AnalizadorFinanciero.__init__)
    extractor = ExtractorEstadosFinancieros()
    analizador_horizontal = AnalisisHorizontalMejorado()
    
    # 2. Leer archivo HTML (como lo hace extraer_datos_html)
    archivo = "consolidar/ReporteDetalleInformacionFinanciero (15).html"
    print(f"\n📄 Procesando: {archivo}")
    
    with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
    
    # 3. Extraer con extractor mejorado
    print("\n⏳ Extrayendo estados financieros...")
    resultados_extractor = extractor.extraer_todos_estados(html_content)
    
    print(f"✅ Año documento: {resultados_extractor['año_documento']}")
    print(f"✅ Formato: {resultados_extractor['formato']}")
    print(f"✅ Estados extraídos: {len(resultados_extractor['estados'])}")
    
    # 4. Verificar que hay datos_extractor (como se guarda en resultados_analisis)
    datos_extractor = resultados_extractor
    
    if datos_extractor and datos_extractor.get('estados'):
        print(f"✅ datos_extractor tiene estados: {list(datos_extractor['estados'].keys())}")
        
        # 5. Realizar análisis horizontal (como en tab5)
        print("\n⏳ Realizando análisis horizontal...")
        analisis_horizontal_resultados = analizador_horizontal.analizar_desde_extractor(datos_extractor)
        
        if 'error' in analisis_horizontal_resultados:
            print(f"❌ ERROR: {analisis_horizontal_resultados['error']}")
        else:
            print(f"✅ Análisis horizontal completado exitosamente!")
            print(f"   • Empresa: {analisis_horizontal_resultados['empresa']}")
            print(f"   • Año: {analisis_horizontal_resultados['año_documento']}")
            print(f"   • Estados analizados: {len(analisis_horizontal_resultados['estados_analizados'])}")
            
            # Mostrar estadísticas
            resumen = analisis_horizontal_resultados['resumen']
            stats = resumen['estadisticas_globales']
            print(f"\n📊 ESTADÍSTICAS:")
            print(f"   • Variaciones positivas: {stats['variaciones_positivas']}")
            print(f"   • Variaciones negativas: {stats['variaciones_negativas']}")
            print(f"   • Sin variación: {stats['sin_variacion']}")
            print(f"   • No calculables: {stats['no_calculables']}")
            
            print("\n✅ TEST EXITOSO - La integración funciona correctamente!")
            return True
    else:
        print("❌ ERROR: datos_extractor no tiene estados")
        return False
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_flujo_completo()
