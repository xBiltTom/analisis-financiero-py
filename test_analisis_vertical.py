#!/usr/bin/env python3
"""
Script de prueba para el análisis vertical
Prueba la funcionalidad de análisis vertical con datos simulados
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from analisis_vertical_horizontal import AnalisisVerticalHorizontal
import pandas as pd

def crear_datos_prueba():
    """Crear datos de prueba simulando un Estado de Situación Financiera"""
    return [
        {
            'archivo': 'Reporte_2024.xls',
            'resumen': {
                'empresa': 'EMPRESA PRUEBA S.A.',
                'año_reporte': '2024'
            },
            'datos': {
                'metadatos': {'año': '2024', 'empresa': 'EMPRESA PRUEBA S.A.'},
                'años_disponibles': ['2024', '2023'],
                'estados_financieros': {
                    'estado_situacion_financiera': {
                        'nombre': 'Estado de Situación Financiera',
                        'datos': [
                            # ACTIVOS
                            {
                                'cuenta': 'Total Activos',
                                '2024': {'numero': 1000000, 'texto': '1,000,000'},
                                '2023': {'numero': 900000, 'texto': '900,000'}
                            },
                            {
                                'cuenta': 'Activos Corrientes',
                                '2024': {'numero': 600000, 'texto': '600,000'},
                                '2023': {'numero': 550000, 'texto': '550,000'}
                            },
                            {
                                'cuenta': 'Efectivo y Equivalentes al Efectivo',
                                '2024': {'numero': 200000, 'texto': '200,000'},
                                '2023': {'numero': 180000, 'texto': '180,000'}
                            },
                            {
                                'cuenta': 'Cuentas por Cobrar Comerciales',
                                '2024': {'numero': 250000, 'texto': '250,000'},
                                '2023': {'numero': 220000, 'texto': '220,000'}
                            },
                            {
                                'cuenta': 'Inventarios',
                                '2024': {'numero': 150000, 'texto': '150,000'},
                                '2023': {'numero': 150000, 'texto': '150,000'}
                            },
                            {
                                'cuenta': 'Activos No Corrientes',
                                '2024': {'numero': 400000, 'texto': '400,000'},
                                '2023': {'numero': 350000, 'texto': '350,000'}
                            },
                            {
                                'cuenta': 'Propiedades, Planta y Equipo',
                                '2024': {'numero': 350000, 'texto': '350,000'},
                                '2023': {'numero': 300000, 'texto': '300,000'}
                            },
                            {
                                'cuenta': 'Activos Intangibles',
                                '2024': {'numero': 50000, 'texto': '50,000'},
                                '2023': {'numero': 50000, 'texto': '50,000'}
                            },
                            
                            # PASIVOS
                            {
                                'cuenta': 'Total Pasivos',
                                '2024': {'numero': 600000, 'texto': '600,000'},
                                '2023': {'numero': 540000, 'texto': '540,000'}
                            },
                            {
                                'cuenta': 'Pasivos Corrientes',
                                '2024': {'numero': 300000, 'texto': '300,000'},
                                '2023': {'numero': 270000, 'texto': '270,000'}
                            },
                            {
                                'cuenta': 'Cuentas por Pagar Comerciales',
                                '2024': {'numero': 150000, 'texto': '150,000'},
                                '2023': {'numero': 135000, 'texto': '135,000'}
                            },
                            {
                                'cuenta': 'Préstamos Bancarios Corrientes',
                                '2024': {'numero': 100000, 'texto': '100,000'},
                                '2023': {'numero': 90000, 'texto': '90,000'}
                            },
                            {
                                'cuenta': 'Otras Cuentas por Pagar',
                                '2024': {'numero': 50000, 'texto': '50,000'},
                                '2023': {'numero': 45000, 'texto': '45,000'}
                            },
                            {
                                'cuenta': 'Pasivos No Corrientes',
                                '2024': {'numero': 300000, 'texto': '300,000'},
                                '2023': {'numero': 270000, 'texto': '270,000'}
                            },
                            {
                                'cuenta': 'Préstamos Bancarios a Largo Plazo',
                                '2024': {'numero': 250000, 'texto': '250,000'},
                                '2023': {'numero': 230000, 'texto': '230,000'}
                            },
                            {
                                'cuenta': 'Obligaciones Financieras',
                                '2024': {'numero': 50000, 'texto': '50,000'},
                                '2023': {'numero': 40000, 'texto': '40,000'}
                            },
                            
                            # PATRIMONIO
                            {
                                'cuenta': 'Total Patrimonio',
                                '2024': {'numero': 400000, 'texto': '400,000'},
                                '2023': {'numero': 360000, 'texto': '360,000'}
                            },
                            {
                                'cuenta': 'Capital',
                                '2024': {'numero': 200000, 'texto': '200,000'},
                                '2023': {'numero': 200000, 'texto': '200,000'}
                            },
                            {
                                'cuenta': 'Reservas',
                                '2024': {'numero': 100000, 'texto': '100,000'},
                                '2023': {'numero': 80000, 'texto': '80,000'}
                            },
                            {
                                'cuenta': 'Resultados Acumulados',
                                '2024': {'numero': 100000, 'texto': '100,000'},
                                '2023': {'numero': 80000, 'texto': '80,000'}
                            }
                        ]
                    }
                }
            }
        }
    ]

def test_analisis_vertical():
    """Prueba el análisis vertical con datos simulados"""
    print("=== Prueba de Análisis Vertical ===")
    
    # Crear instancia del analizador
    analizador = AnalisisVerticalHorizontal()
    
    # Crear datos de prueba
    datos_prueba = crear_datos_prueba()
    años = ['2024', '2023']
    
    # Realizar análisis
    print("Realizando análisis vertical...")
    resultados = analizador.realizar_analisis_vertical_situacion_financiera(datos_prueba, años)
    
    # Mostrar resultados
    print(f"\nAños analizados: {list(resultados['analisis_por_año'].keys())}")
    print(f"Errores encontrados: {len(resultados['errores'])}")
    
    if resultados['errores']:
        print("Errores:")
        for error in resultados['errores']:
            print(f"  - {error}")
    
    # Mostrar análisis detallado para cada año
    for año, datos_año in resultados['analisis_por_año'].items():
        print(f"\n--- ANÁLISIS VERTICAL {año} ---")
        
        # Totales principales
        print(f"Total Activos: {datos_año['activos']['total_activos']:,.2f}")
        print(f"Total Pasivos: {datos_año['pasivos']['total_pasivos']:,.2f}")
        print(f"Total Patrimonio: {datos_año['patrimonio']['total_patrimonio']:,.2f}")
        
        # Mostrar análisis de activos
        if datos_año['activos']['cuentas']:
            print(f"\n📊 ACTIVOS (% del Total de Activos = {datos_año['activos']['total_activos']:,.0f}):")
            for cuenta in datos_año['activos']['cuentas']:
                print(f"  {cuenta['cuenta']}: {cuenta['valor']:,.2f} ({cuenta['porcentaje_vertical']:.2f}%)")
        
        # Mostrar análisis de pasivos
        if datos_año['pasivos']['cuentas']:
            print(f"\n📊 PASIVOS (% del Total de Pasivos = {datos_año['pasivos']['total_pasivos']:,.0f}):")
            for cuenta in datos_año['pasivos']['cuentas']:
                print(f"  {cuenta['cuenta']}: {cuenta['valor']:,.2f} ({cuenta['porcentaje_vertical']:.2f}%)")
        
        # Mostrar análisis de patrimonio
        if datos_año['patrimonio']['cuentas']:
            print(f"\n📊 PATRIMONIO (% del Total de Patrimonio = {datos_año['patrimonio']['total_patrimonio']:,.0f}):")
            for cuenta in datos_año['patrimonio']['cuentas']:
                print(f"  {cuenta['cuenta']}: {cuenta['valor']:,.2f} ({cuenta['porcentaje_vertical']:.2f}%)")

def test_generar_tablas():
    """Prueba la generación de tablas pandas"""
    print("\n=== Prueba de Generación de Tablas ===")
    
    analizador = AnalisisVerticalHorizontal()
    datos_prueba = crear_datos_prueba()
    años = ['2024', '2023']
    
    resultados = analizador.realizar_analisis_vertical_situacion_financiera(datos_prueba, años)
    tablas = analizador.generar_tabla_analisis_vertical(resultados)
    
    print(f"Tablas generadas: {list(tablas.keys())}")
    
    for nombre_tabla, df in tablas.items():
        print(f"\nTabla: {nombre_tabla}")
        print(f"  Filas: {len(df)}, Columnas: {len(df.columns)}")
        print(f"  Columnas: {list(df.columns)}")

if __name__ == "__main__":
    test_analisis_vertical()
    test_generar_tablas()
    print("\n✅ Todas las pruebas de análisis vertical completadas")