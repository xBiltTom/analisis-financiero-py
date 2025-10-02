"""
Prueba del análisis vertical con archivo real de años ≤2009
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analizador_financiero import AnalizadorFinanciero
from analisis_vertical_horizontal import AnalisisVerticalHorizontal

def probar_archivo_real_2009():
    """Probar análisis vertical con archivo real de años ≤2009"""
    print("🧪 PRUEBA CON ARCHIVO REAL DE AÑOS ≤2009")
    print("=" * 60)
    
    # Crear analizador
    analizador = AnalizadorFinanciero()
    analizador_vertical = AnalisisVerticalHorizontal()
    
    # Archivo de prueba (2004-2003)
    archivo_html = "temp/ReporteDetalleInformacionFinanciero (6).html"
    
    if not os.path.exists(archivo_html):
        print(f"❌ No se encontró el archivo: {archivo_html}")
        return
    
    print(f"📄 Analizando archivo: {archivo_html}")
    print("   Años esperados: 2004, 2003")
    print()
    
    # Extraer datos del archivo
    print("⏳ Extrayendo datos del archivo HTML...")
    datos_extraidos = analizador.extraer_datos_html(archivo_html)
    
    if not datos_extraidos:
        print("❌ No se pudieron extraer datos del archivo")
        return
    
    # Mostrar información básica
    print("✅ Datos extraídos exitosamente")
    print(f"📊 Año documento: {datos_extraidos.get('año_documento', 'No detectado')}")
    print(f"📅 Años disponibles: {datos_extraidos.get('años_disponibles', [])}")
    print(f"🏢 Empresa: {datos_extraidos.get('metadatos', {}).get('empresa', 'No detectada')}")
    print()
    
    # Verificar estados financieros detectados
    estados_financieros = datos_extraidos.get('estados_financieros', {})
    print("📋 Estados financieros detectados:")
    for clave, info in estados_financieros.items():
        if info.get('datos'):
            print(f"   ✅ {info['nombre']}: {len(info['datos'])} cuentas")
        else:
            print(f"   ❌ {info['nombre']}: Sin datos")
    print()
    
    # Preparar datos para análisis vertical
    resultados_analisis = [{
        'archivo': 'ReporteDetalleInformacionFinanciero (6).html',
        'datos': datos_extraidos,
        'resumen': {
            'empresa': datos_extraidos.get('metadatos', {}).get('empresa', 'COMPAÑÍA UNIVERSAL TEXTIL S.A.'),
            'año_reporte': datos_extraidos.get('metadatos', {}).get('año', '2004'),
            'años_disponibles': datos_extraidos.get('años_disponibles', ['2004', '2003'])
        }
    }]
    
    # Realizar análisis vertical
    años_para_analisis = datos_extraidos.get('años_disponibles', ['2004', '2003'])
    print(f"🔍 Realizando análisis vertical para años: {años_para_analisis}")
    print()
    
    try:
        resultados_vertical = analizador_vertical.realizar_analisis_vertical_situacion_financiera(
            resultados_analisis, años_para_analisis
        )
        
        # Mostrar resultados
        print("📈 RESULTADOS DEL ANÁLISIS VERTICAL")
        print("=" * 50)
        
        if resultados_vertical['errores']:
            print("❌ ERRORES ENCONTRADOS:")
            for error in resultados_vertical['errores']:
                print(f"   - {error}")
            print()
        
        if resultados_vertical['analisis_por_año']:
            print(f"✅ Análisis completado para {len(resultados_vertical['analisis_por_año'])} año(s)")
            print()
            
            for año, datos_año in resultados_vertical['analisis_por_año'].items():
                print(f"📅 AÑO {año}")
                print("-" * 30)
                
                # Totales principales
                print(f"💰 Total Activos: {datos_año['activos']['total_activos']:,.2f}")
                print(f"💳 Total Pasivos: {datos_año['pasivos']['total_pasivos']:,.2f}")  
                print(f"🏛️ Total Patrimonio: {datos_año['patrimonio']['total_patrimonio']:,.2f}")
                print()
                
                # Verificación de equilibrio contable
                verificacion = datos_año['verificacion']
                print(f"⚖️ Equilibrio Contable: {'✅ SÍ' if verificacion['equilibrio_contable'] else '❌ NO'}")
                print(f"📊 Diferencia: {verificacion['diferencia']:,.2f}")
                print()
                
                # Mostrar estructura detallada
                print("📊 ESTRUCTURA DETALLADA:")
                print()
                
                # Activos
                if datos_año['activos']['cuentas']:
                    print("💰 ACTIVOS (% del Total de Activos):")
                    for activo in datos_año['activos']['cuentas']:
                        print(f"   • {activo['cuenta']}: {activo['valor']:,.0f} ({activo['porcentaje_vertical']:.2f}%)")
                    print()
                
                # Pasivos
                if datos_año['pasivos']['cuentas']:
                    print("💳 PASIVOS (% del Total de Pasivos):")
                    for pasivo in datos_año['pasivos']['cuentas']:
                        print(f"   • {pasivo['cuenta']}: {pasivo['valor']:,.0f} ({pasivo['porcentaje_vertical']:.2f}%)")
                    print()
                
                # Patrimonio
                if datos_año['patrimonio']['cuentas']:
                    print("🏛️ PATRIMONIO (% del Total de Patrimonio):")
                    for patrimonio in datos_año['patrimonio']['cuentas']:
                        print(f"   • {patrimonio['cuenta']}: {patrimonio['valor']:,.0f} ({patrimonio['porcentaje_vertical']:.2f}%)")
                    print()
                
                print("=" * 50)
        else:
            print("❌ No se pudieron generar resultados de análisis vertical")
            
    except Exception as e:
        print(f"❌ Error durante el análisis vertical: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("✅ Prueba con archivo real completada")

if __name__ == "__main__":
    probar_archivo_real_2009()