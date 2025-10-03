"""
Test de Ratios de Rentabilidad
================================
Verifica que los nuevos ratios (Margen Neto, ROA, ROE) se calculen correctamente
"""

from extractor_estados_mejorado import ExtractorEstadosFinancieros
from ratios_financieros import CalculadorRatiosFinancieros

def test_ratios_rentabilidad():
    print("="*80)
    print("TEST DE RATIOS DE RENTABILIDAD")
    print("="*80)
    
    # Inicializar extractor y calculador
    extractor = ExtractorEstadosFinancieros()
    calculador = CalculadorRatiosFinancieros()
    
    # Archivos de prueba
    archivos_test = [
        'ejemplos/REPORTE DETALLE FINANCIERO 2024.html',
        'ejemplos/REPORTE DETALLE FINANCIERO 2023.html',
        'ejemplos/REPORTE DETALLE FINANCIERO 2022.html'
    ]
    
    # Extraer datos de cada archivo
    extractores_list = []
    
    for archivo in archivos_test:
        print(f"\n📄 Procesando: {archivo}")
        
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Extraer estados
            resultados = extractor.extraer_todos_estados(html_content)
            
            # Verificar que tenga estados necesarios
            if 'balance' in resultados['estados']:
                print(f"   ✅ Balance: {resultados['estados']['balance']['total_cuentas']} cuentas")
            else:
                print(f"   ❌ Balance: No encontrado")
            
            if 'resultados' in resultados['estados']:
                print(f"   ✅ Estado de Resultados: {resultados['estados']['resultados']['total_cuentas']} cuentas")
                
                # Verificar que contenga las cuentas necesarias
                cuentas_resultados = resultados['estados']['resultados']['cuentas']
                ganancia_neta = None
                ingresos_ordinarios = None
                
                for cuenta in cuentas_resultados:
                    nombre_upper = cuenta['nombre'].upper()
                    
                    if 'GANANCIA' in nombre_upper and 'NETA' in nombre_upper and 'EJERCICIO' in nombre_upper:
                        año_mas_reciente = resultados['estados']['resultados']['años'][0]
                        ganancia_neta = cuenta['valores'].get(año_mas_reciente, 0)
                        print(f"      📊 Ganancia Neta: {ganancia_neta:,.0f}")
                    
                    if 'INGRESOS' in nombre_upper and 'ACTIVIDADES' in nombre_upper and 'ORDINARIAS' in nombre_upper:
                        año_mas_reciente = resultados['estados']['resultados']['años'][0]
                        ingresos_ordinarios = cuenta['valores'].get(año_mas_reciente, 0)
                        print(f"      📊 Ingresos Ordinarios: {ingresos_ordinarios:,.0f}")
                
                if ganancia_neta is not None and ingresos_ordinarios and ingresos_ordinarios != 0:
                    margen_calculado = (ganancia_neta / ingresos_ordinarios) * 100
                    print(f"      💡 Margen Neto estimado: {margen_calculado:.2f}%")
            else:
                print(f"   ❌ Estado de Resultados: No encontrado")
            
            extractores_list.append(resultados)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Calcular ratios consolidados
    print("\n" + "="*80)
    print("CÁLCULO DE RATIOS FINANCIEROS CONSOLIDADOS")
    print("="*80)
    
    if extractores_list:
        resultados_ratios = calculador.calcular_ratios_desde_extractor(extractores_list)
        
        if 'error' not in resultados_ratios:
            print(f"\n✅ Ratios calculados exitosamente")
            print(f"📅 Años procesados: {', '.join(map(str, sorted(resultados_ratios['años'])))}")
            print(f"🏢 Empresa: {resultados_ratios['empresa']}")
            
            # Mostrar tabla de ratios
            print("\n" + "-"*80)
            print("TABLA DE RATIOS POR AÑO")
            print("-"*80)
            print(f"{'Año':<6} | {'Liq.Corr.':<10} | {'P.Ácida':<10} | {'Deuda%':<8} | {'D/P':<6} | {'Marg.N%':<10} | {'ROA%':<10} | {'ROE%':<10}")
            print("-"*80)
            
            for año in sorted(resultados_ratios['años']):
                ratios_año = resultados_ratios['ratios_por_año'][año]
                
                lc = f"{ratios_año['liquidez_corriente']:.2f}" if ratios_año['liquidez_corriente'] else "N/A"
                pa = f"{ratios_año['prueba_acida']:.2f}" if ratios_año['prueba_acida'] else "N/A"
                dt = f"{ratios_año['razon_deuda_total']:.1%}" if ratios_año['razon_deuda_total'] else "N/A"
                dp = f"{ratios_año['razon_deuda_patrimonio']:.2f}" if ratios_año['razon_deuda_patrimonio'] else "N/A"
                mn = f"{ratios_año['margen_neto']:.3%}" if ratios_año['margen_neto'] is not None else "N/A"
                roa = f"{ratios_año['roa']:.3%}" if ratios_año['roa'] is not None else "N/A"
                roe = f"{ratios_año['roe']:.3%}" if ratios_año['roe'] is not None else "N/A"
                
                print(f"{año:<6} | {lc:<10} | {pa:<10} | {dt:<8} | {dp:<6} | {mn:<10} | {roa:<10} | {roe:<10}")
            
            # Mostrar resumen estadístico
            print("\n" + "-"*80)
            print("RESUMEN ESTADÍSTICO")
            print("-"*80)
            
            resumen = resultados_ratios.get('resumen', {})
            
            print("\n📊 RATIOS DE LIQUIDEZ:")
            if resumen.get('liquidez_corriente', {}).get('promedio'):
                lc_stats = resumen['liquidez_corriente']
                print(f"   • Liquidez Corriente:")
                print(f"     - Promedio: {lc_stats['promedio']:.2f}")
                print(f"     - Rango: {lc_stats['min']:.2f} - {lc_stats['max']:.2f}")
            
            if resumen.get('prueba_acida', {}).get('promedio'):
                pa_stats = resumen['prueba_acida']
                print(f"   • Prueba Ácida:")
                print(f"     - Promedio: {pa_stats['promedio']:.2f}")
                print(f"     - Rango: {pa_stats['min']:.2f} - {pa_stats['max']:.2f}")
            
            print("\n💰 RATIOS DE ENDEUDAMIENTO:")
            if resumen.get('razon_deuda_total', {}).get('promedio'):
                rdt_stats = resumen['razon_deuda_total']
                print(f"   • Razón Deuda Total:")
                print(f"     - Promedio: {rdt_stats['promedio']:.1%}")
                print(f"     - Rango: {rdt_stats['min']:.1%} - {rdt_stats['max']:.1%}")
            
            if resumen.get('razon_deuda_patrimonio', {}).get('promedio'):
                rdp_stats = resumen['razon_deuda_patrimonio']
                print(f"   • Razón Deuda/Patrimonio:")
                print(f"     - Promedio: {rdp_stats['promedio']:.2f}")
                print(f"     - Rango: {rdp_stats['min']:.2f} - {rdp_stats['max']:.2f}")
            
            print("\n📈 RATIOS DE RENTABILIDAD:")
            if resumen.get('margen_neto', {}).get('promedio'):
                mn_stats = resumen['margen_neto']
                print(f"   • Margen Neto:")
                print(f"     - Promedio: {mn_stats['promedio']:.3%}")
                print(f"     - Rango: {mn_stats['min']:.3%} - {mn_stats['max']:.3%}")
            
            if resumen.get('roa', {}).get('promedio'):
                roa_stats = resumen['roa']
                print(f"   • ROA (Return on Assets):")
                print(f"     - Promedio: {roa_stats['promedio']:.3%}")
                print(f"     - Rango: {roa_stats['min']:.3%} - {roa_stats['max']:.3%}")
            
            if resumen.get('roe', {}).get('promedio'):
                roe_stats = resumen['roe']
                print(f"   • ROE (Return on Equity):")
                print(f"     - Promedio: {roe_stats['promedio']:.3%}")
                print(f"     - Rango: {roe_stats['min']:.3%} - {roe_stats['max']:.3%}")
            
            # Verificar que los nuevos ratios existan y no sean None
            print("\n" + "="*80)
            print("VERIFICACIÓN DE NUEVOS RATIOS")
            print("="*80)
            
            todos_calculados = True
            for año in sorted(resultados_ratios['años']):
                ratios_año = resultados_ratios['ratios_por_año'][año]
                
                if ratios_año.get('margen_neto') is None:
                    print(f"⚠️  Año {año}: Margen Neto no calculado")
                    todos_calculados = False
                
                if ratios_año.get('roa') is None:
                    print(f"⚠️  Año {año}: ROA no calculado")
                    todos_calculados = False
                
                if ratios_año.get('roe') is None:
                    print(f"⚠️  Año {año}: ROE no calculado")
                    todos_calculados = False
            
            if todos_calculados:
                print("✅ Todos los ratios de rentabilidad fueron calculados exitosamente")
            
            print("\n" + "="*80)
            print("✅ TEST COMPLETADO")
            print("="*80)
        
        else:
            print(f"\n❌ Error al calcular ratios: {resultados_ratios['error']}")
    
    else:
        print("\n❌ No se pudieron extraer datos de los archivos")


if __name__ == "__main__":
    test_ratios_rentabilidad()
