#!/usr/bin/env python3
"""
Script de prueba para el analizador financiero
Prueba la funcionalidad de conversión de números y detección de estados
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from analizador_financiero import AnalizadorFinanciero

def test_convertir_numero():
    """Prueba la función de conversión de números"""
    print("=== Prueba de Conversión de Números (Formato Peruano/Latinoamericano) ===")
    
    analizador = AnalizadorFinanciero()
    
    casos_prueba = [
        # Formato peruano/latinoamericano
        "123,456",       # Miles: 123456
        "1,234,567",     # Millones: 1234567
        "123.50",        # Decimal: 123.5
        "1,234.56",      # Miles con decimales: 1234.56
        "1,234,567.89",  # Millones con decimales: 1234567.89
        
        # Casos especiales
        "(500.00)",      # Negativo en paréntesis: -500.0
        "-1,000",        # Negativo con signo: -1000.0
        "0",             # Cero: 0.0
        "-",             # Guión: 0.0
        "--",            # Doble guión: 0.0
        "   ",           # Espacios: 0.0
        
        # Con símbolos de moneda
        "S/ 1,500.25",   # Con símbolo: 1500.25
        "$ 123,456",     # Dólares: 123456.0
        
        # Cases edge
        "0.75",          # Decimal simple: 0.75
        "(1,234.56)",    # Negativo complejo: -1234.56
        "",              # Vacío: 0.0
        "N/A",           # Texto: 0.0
        "12.345",        # Decimal: 12.345
        "1.000",         # Mil como decimal: 1000.0
        "10,500"         # Diez mil quinientos: 10500
    ]
    
    for caso in casos_prueba:
        resultado = analizador.convertir_a_numero(caso)
        print(f"'{caso}' -> {resultado}")

def test_detectar_año():
    """Prueba detección de año desde nombre de archivo"""
    print("\n=== Prueba de Detección de Año ===")
    
    archivos_prueba = [
        "REPORTE DETALLE FINANCIERO 2020.xls",
        "REPORTE DETALLE FINANCIERO 2021.xls", 
        "REPORTE 2009.xls",
        "Estado Financiero 2015.xlsx",
        "Reporte 2008 Final.xls",
        "Estados 2024.xls"
    ]
    
    for archivo in archivos_prueba:
        # Extraer año del nombre del archivo
        import re
        años = re.findall(r'20\d{2}|19\d{2}', archivo)
        if años:
            año = int(años[0])
            formato = "≤2009 (Balance General, Estado Ganancias y Pérdidas)" if año <= 2009 else "≥2010 (Estado Situación Financiera, Estado Resultados)"
            print(f"'{archivo}' -> Año: {año} ({formato})")

if __name__ == "__main__":
    test_convertir_numero()
    test_detectar_año()
    print("\n✅ Pruebas completadas")