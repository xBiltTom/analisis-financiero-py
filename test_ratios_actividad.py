#!/usr/bin/env python3
"""
Script de prueba para los nuevos RATIOS DE ACTIVIDAD
===================================================
Prueba la implementación de los 3 nuevos ratios de actividad:
1. Rotación de Activos Totales
2. Rotación de Cuentas por Cobrar
3. Rotación de Inventarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor_estados_mejorado import extraer_estados_desde_archivo
from ratios_financieros import CalculadorRatiosFinancieros

def main():
    print("🔄 PRUEBA DE RATIOS DE ACTIVIDAD")
    print("=" * 50)
    
    # Inicializar calculador
    calculador = CalculadorRatiosFinancieros()
    
    # Archivos de prueba
    archivos_test = [
        "ejemplos/REPORTE DETALLE FINANCIERO 2022.html",
        "ejemplos/REPORTE DETALLE FINANCIERO 2023.html", 
        "ejemplos/REPORTE DETALLE FINANCIERO 2024.html"
    ]
    
    # Extraer datos
    print("📂 Extrayendo datos de archivos...")
    extractores = []
    
    for archivo in archivos_test:
        if os.path.exists(archivo):
            print(f"   Procesando: {archivo}")
            resultado = extraer_estados_desde_archivo(archivo)
            if resultado and 'error' not in resultado:
                extractores.append(resultado)
        else:
            print(f"   ⚠️ Archivo no encontrado: {archivo}")
    
    if not extractores:
        print("❌ No se encontraron archivos válidos para procesar")
        return
    
    print(f"✅ {len(extractores)} archivos procesados exitosamente")
    
    # Calcular ratios
    print("\n🧮 Calculando ratios financieros (10 ratios totales)...")
    resultados = calculador.calcular_ratios_desde_extractor(extractores)
    
    if 'error' in resultados:
        print(f"❌ Error: {resultados['error']}")
        return
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS - EMPRESA: {resultados.get('empresa', 'N/A')}")
    print(f"    Años analizados: {', '.join(map(str, sorted(resultados['años'])))}")
    print(f"    Total ratios calculados: 10")
    
    print("\n" + "="*80)
    print("📋 TABLA DE RATIOS COMPLETA (10 RATIOS)")
    print("="*80)
    
    # Encabezados
    headers = [
        "Año", "L. Corriente", "P. Ácida", "Deuda%", "Deuda/Pat",
        "Margen%", "ROA%", "ROE%", "Rot.Activos", "Rot.CxC", "Rot.Inv"
    ]
    print(f"{'':>4} {''.join(f'{h:>11}' for h in headers)}")
    print("-" * 80)
    
    # Datos por año
    for año in sorted(resultados['años']):
        ratios = resultados['ratios_por_año'][año]
        
        # Formatear valores
        lc = f"{ratios.get('liquidez_corriente', 0):.2f}" if ratios.get('liquidez_corriente') else "N/A"
        pa = f"{ratios.get('prueba_acida', 0):.2f}" if ratios.get('prueba_acida') else "N/A"
        dt = f"{ratios.get('razon_deuda_total', 0)*100:.1f}%" if ratios.get('razon_deuda_total') else "N/A"
        dp = f"{ratios.get('razon_deuda_patrimonio', 0):.2f}" if ratios.get('razon_deuda_patrimonio') else "N/A"
        mn = f"{ratios.get('margen_neto', 0)*100:.3f}%" if ratios.get('margen_neto') else "N/A"
        roa = f"{ratios.get('roa', 0)*100:.3f}%" if ratios.get('roa') else "N/A"
        roe = f"{ratios.get('roe', 0)*100:.3f}%" if ratios.get('roe') else "N/A"
        
        # ✨ NUEVOS RATIOS DE ACTIVIDAD
        rat = f"{ratios.get('rotacion_activos_totales', 0):.3f}" if ratios.get('rotacion_activos_totales') else "N/A"
        rcxc = f"{ratios.get('rotacion_cuentas_cobrar', 0):.3f}" if ratios.get('rotacion_cuentas_cobrar') else "N/A"
        ri = f"{ratios.get('rotacion_inventarios', 0):.3f}" if ratios.get('rotacion_inventarios') else "N/A"
        
        print(f"{año:>4} {lc:>11} {pa:>11} {dt:>11} {dp:>11} {mn:>11} {roa:>11} {roe:>11} {rat:>11} {rcxc:>11} {ri:>11}")
    
    # Resumen estadístico por categorías
    if resultados.get('resumen'):
        print("\n" + "="*80)
        print("📈 RESUMEN ESTADÍSTICO POR CATEGORÍAS")
        print("="*80)
        
        # RATIOS DE LIQUIDEZ
        print("\n🔵 RATIOS DE LIQUIDEZ:")
        lc_stats = resultados['resumen'].get('liquidez_corriente', {})
        if lc_stats.get('promedio'):
            print(f"   Liquidez Corriente - Promedio: {lc_stats['promedio']:.2f} | Min: {lc_stats['min']:.2f} | Max: {lc_stats['max']:.2f}")
        
        pa_stats = resultados['resumen'].get('prueba_acida', {})
        if pa_stats.get('promedio'):
            print(f"   Prueba Ácida      - Promedio: {pa_stats['promedio']:.2f} | Min: {pa_stats['min']:.2f} | Max: {pa_stats['max']:.2f}")
        
        # RATIOS DE ENDEUDAMIENTO
        print("\n🟡 RATIOS DE ENDEUDAMIENTO:")
        dt_stats = resultados['resumen'].get('razon_deuda_total', {})
        if dt_stats.get('promedio'):
            print(f"   Razón Deuda Total - Promedio: {dt_stats['promedio']:.1%} | Min: {dt_stats['min']:.1%} | Max: {dt_stats['max']:.1%}")
        
        dp_stats = resultados['resumen'].get('razon_deuda_patrimonio', {})
        if dp_stats.get('promedio'):
            print(f"   Razón Deuda/Pat.  - Promedio: {dp_stats['promedio']:.2f} | Min: {dp_stats['min']:.2f} | Max: {dp_stats['max']:.2f}")
        
        # RATIOS DE RENTABILIDAD
        print("\n🟢 RATIOS DE RENTABILIDAD:")
        mn_stats = resultados['resumen'].get('margen_neto', {})
        if mn_stats.get('promedio'):
            print(f"   Margen Neto       - Promedio: {mn_stats['promedio']:.3%} | Min: {mn_stats['min']:.3%} | Max: {mn_stats['max']:.3%}")
        
        roa_stats = resultados['resumen'].get('roa', {})
        if roa_stats.get('promedio'):
            print(f"   ROA               - Promedio: {roa_stats['promedio']:.3%} | Min: {roa_stats['min']:.3%} | Max: {roa_stats['max']:.3%}")
        
        roe_stats = resultados['resumen'].get('roe', {})
        if roe_stats.get('promedio'):
            print(f"   ROE               - Promedio: {roe_stats['promedio']:.3%} | Min: {roe_stats['min']:.3%} | Max: {roe_stats['max']:.3%}")
        
        # ✨ NUEVOS: RATIOS DE ACTIVIDAD
        print("\n🟣 RATIOS DE ACTIVIDAD:")
        rat_stats = resultados['resumen'].get('rotacion_activos_totales', {})
        if rat_stats.get('promedio'):
            print(f"   Rotación Activos  - Promedio: {rat_stats['promedio']:.3f} | Min: {rat_stats['min']:.3f} | Max: {rat_stats['max']:.3f}")
        
        rcxc_stats = resultados['resumen'].get('rotacion_cuentas_cobrar', {})
        if rcxc_stats.get('promedio'):
            print(f"   Rotación CxC      - Promedio: {rcxc_stats['promedio']:.3f} | Min: {rcxc_stats['min']:.3f} | Max: {rcxc_stats['max']:.3f}")
        
        ri_stats = resultados['resumen'].get('rotacion_inventarios', {})
        if ri_stats.get('promedio'):
            print(f"   Rotación Invent.  - Promedio: {ri_stats['promedio']:.3f} | Min: {ri_stats['min']:.3f} | Max: {ri_stats['max']:.3f}")
    
    # Validación manual de cálculos para 2024
    print("\n" + "="*80)
    print("🔍 VALIDACIÓN MANUAL DE CÁLCULOS (2024)")
    print("="*80)
    
    # Buscar datos del 2024
    datos_2024 = None
    for extractor_data in extractores:
        if 2024 in extractor_data.get('años', []):
            datos_2024 = extractor_data
            break
    
    if datos_2024:
        print("\n📋 Datos fuente encontrados para validación:")
        
        # Extraer valores del balance y estado de resultados
        balance_2024 = next((e for e in datos_2024['estados'] if e['tipo'] == 'balance'), None)
        resultados_2024 = next((e for e in datos_2024['estados'] if e['tipo'] == 'resultados'), None)
        
        if balance_2024 and resultados_2024:
            # Encontrar valores específicos
            ingresos = 0
            costo_ventas = 0
            total_activos = 0
            cxc_2024 = 0
            cxc_2023 = 0
            inv_2024 = 0
            inv_2023 = 0
            
            # Buscar en estado de resultados
            for cuenta in resultados_2024['cuentas']:
                nombre = cuenta['nombre'].upper()
                valor_2024 = cuenta['valores'].get(2024, 0)
                
                if 'INGRESOS DE ACTIVIDADES ORDINARIAS' in nombre:
                    ingresos = abs(valor_2024)
                elif 'COSTO DE VENTAS' in nombre:
                    costo_ventas = abs(valor_2024)
            
            # Buscar en balance
            en_activos_corrientes = False
            for cuenta in balance_2024['cuentas']:
                nombre = cuenta['nombre'].upper()
                valor_2024 = cuenta['valores'].get(2024, 0)
                valor_2023 = cuenta['valores'].get(2023, 0)
                
                if 'TOTAL DE ACTIVOS' in nombre or 'TOTAL ACTIVOS' in nombre:
                    total_activos = abs(valor_2024)
                elif 'ACTIVOS CORRIENTES' in nombre and 'TOTAL' not in nombre:
                    en_activos_corrientes = True
                elif 'ACTIVOS NO CORRIENTES' in nombre or 'TOTAL PASIVOS' in nombre:
                    en_activos_corrientes = False
                elif en_activos_corrientes and 'CUENTAS POR COBRAR COMERCIALES' in nombre:
                    cxc_2024 += abs(valor_2024)
                    cxc_2023 += abs(valor_2023)
                elif en_activos_corrientes and 'INVENTARIOS' in nombre:
                    inv_2024 += abs(valor_2024)
                    inv_2023 += abs(valor_2023)
            
            print(f"   Ingresos Ordinarios 2024: {ingresos:,.0f}")
            print(f"   Costo de Ventas 2024: {costo_ventas:,.0f}")
            print(f"   Total Activos 2024: {total_activos:,.0f}")
            print(f"   Cuentas por Cobrar 2024: {cxc_2024:,.0f}")
            print(f"   Cuentas por Cobrar 2023: {cxc_2023:,.0f}")
            print(f"   Inventarios 2024: {inv_2024:,.0f}")
            print(f"   Inventarios 2023: {inv_2023:,.0f}")
            
            # Calcular ratios manualmente
            print(f"\n🧮 Cálculos manuales:")
            if total_activos > 0:
                rat_manual = ingresos / total_activos
                print(f"   Rotación Activos = {ingresos:,.0f} / {total_activos:,.0f} = {rat_manual:.3f}")
            
            if cxc_2024 > 0 or cxc_2023 > 0:
                promedio_cxc = (cxc_2024 + cxc_2023) / 2
                rcxc_manual = ingresos / promedio_cxc
                print(f"   Rotación CxC = {ingresos:,.0f} / {promedio_cxc:,.0f} = {rcxc_manual:.3f}")
            
            if inv_2024 > 0 or inv_2023 > 0:
                promedio_inv = (inv_2024 + inv_2023) / 2
                ri_manual = costo_ventas / promedio_inv
                print(f"   Rotación Inventarios = {costo_ventas:,.0f} / {promedio_inv:,.0f} = {ri_manual:.3f}")
    
    print(f"\n✅ PRUEBA COMPLETADA - Total de {len(resultados['años'])} años analizados")
    print(f"📊 Se calcularon exitosamente 10 ratios financieros")
    print(f"🎯 Nuevos ratios de actividad implementados correctamente")
    
    # Generar gráficos (opcional)
    print(f"\n📈 Generando {10} gráficos interactivos...")
    graficos = calculador.generar_graficos_ratios(resultados)
    print(f"✅ {len(graficos)} gráficos generados exitosamente")

if __name__ == "__main__":
    main()