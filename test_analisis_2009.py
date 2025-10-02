"""
Prueba específica para análisis vertical de archivos de años 2009 hacia abajo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analisis_vertical_horizontal import AnalisisVerticalHorizontal

def crear_datos_prueba_2009():
    """Crear datos de prueba que simulan archivos de años ≤2009 con terminología específica"""
    
    # Simular datos de Balance General para años 2009 y 2008
    datos_2009_2008 = {
        'archivo': 'Balance_General_2009_2008.xls',
        'datos': {
            'metadatos': {
                'año': '2009',
                'empresa': 'Empresa Prueba S.A.',
                'tipo': 'Balance General'
            },
            'años_disponibles': ['2009', '2008'],
            'año_documento': 2009,
            'estados_financieros': {
                'balance_general': {  # Nota: balance_general en lugar de estado_situacion_financiera
                    'nombre': 'Balance General',
                    'datos': [
                        # === ACTIVOS ===
                        {'cuenta': 'ACTIVOS CORRIENTES'},
                        {'cuenta': 'Caja y Bancos', '2009': {'texto': '150,000', 'numero': 150000}, '2008': {'texto': '140,000', 'numero': 140000}},
                        {'cuenta': 'Valores Negociables', '2009': {'texto': '50,000', 'numero': 50000}, '2008': {'texto': '45,000', 'numero': 45000}},
                        {'cuenta': 'Cuentas por Cobrar Comerciales', '2009': {'texto': '200,000', 'numero': 200000}, '2008': {'texto': '180,000', 'numero': 180000}},
                        {'cuenta': 'Inventarios', '2009': {'texto': '300,000', 'numero': 300000}, '2008': {'texto': '280,000', 'numero': 280000}},
                        {'cuenta': 'Gastos Pagados por Anticipado', '2009': {'texto': '25,000', 'numero': 25000}, '2008': {'texto': '20,000', 'numero': 20000}},
                        {'cuenta': 'Total Activos Corrientes', '2009': {'texto': '725,000', 'numero': 725000}, '2008': {'texto': '665,000', 'numero': 665000}},
                        
                        {'cuenta': 'ACTIVOS NO CORRIENTES'},
                        {'cuenta': 'Inmuebles, Maquinaria y Equipo', '2009': {'texto': '450,000', 'numero': 450000}, '2008': {'texto': '420,000', 'numero': 420000}},
                        {'cuenta': 'Depreciación Acumulada', '2009': {'texto': '(125,000)', 'numero': -125000}, '2008': {'texto': '(110,000)', 'numero': -110000}},
                        {'cuenta': 'Inversiones a Largo Plazo', '2009': {'texto': '75,000', 'numero': 75000}, '2008': {'texto': '70,000', 'numero': 70000}},
                        {'cuenta': 'Total Activos No Corrientes', '2009': {'texto': '400,000', 'numero': 400000}, '2008': {'texto': '380,000', 'numero': 380000}},
                        
                        {'cuenta': 'TOTAL ACTIVOS', '2009': {'texto': '1,125,000', 'numero': 1125000}, '2008': {'texto': '1,045,000', 'numero': 1045000}},
                        
                        # === PASIVOS ===
                        {'cuenta': 'PASIVOS CORRIENTES'},
                        {'cuenta': 'Cuentas por Pagar Comerciales', '2009': {'texto': '180,000', 'numero': 180000}, '2008': {'texto': '160,000', 'numero': 160000}},
                        {'cuenta': 'Préstamos Bancarios Corrientes', '2009': {'texto': '100,000', 'numero': 100000}, '2008': {'texto': '90,000', 'numero': 90000}},
                        {'cuenta': 'Tributos por Pagar', '2009': {'texto': '45,000', 'numero': 45000}, '2008': {'texto': '40,000', 'numero': 40000}},
                        {'cuenta': 'Remuneraciones por Pagar', '2009': {'texto': '30,000', 'numero': 30000}, '2008': {'texto': '25,000', 'numero': 25000}},
                        {'cuenta': 'Total Pasivos Corrientes', '2009': {'texto': '355,000', 'numero': 355000}, '2008': {'texto': '315,000', 'numero': 315000}},
                        
                        {'cuenta': 'PASIVOS NO CORRIENTES'},
                        {'cuenta': 'Préstamos a Largo Plazo', '2009': {'texto': '200,000', 'numero': 200000}, '2008': {'texto': '220,000', 'numero': 220000}},
                        {'cuenta': 'Provisiones', '2009': {'texto': '25,000', 'numero': 25000}, '2008': {'texto': '20,000', 'numero': 20000}},
                        {'cuenta': 'Total Pasivos No Corrientes', '2009': {'texto': '225,000', 'numero': 225000}, '2008': {'texto': '240,000', 'numero': 240000}},
                        
                        {'cuenta': 'TOTAL PASIVOS', '2009': {'texto': '580,000', 'numero': 580000}, '2008': {'texto': '555,000', 'numero': 555000}},
                        
                        # === PATRIMONIO ===
                        {'cuenta': 'PATRIMONIO NETO'},
                        {'cuenta': 'Capital Social', '2009': {'texto': '400,000', 'numero': 400000}, '2008': {'texto': '400,000', 'numero': 400000}},
                        {'cuenta': 'Reservas Legales', '2009': {'texto': '45,000', 'numero': 45000}, '2008': {'texto': '35,000', 'numero': 35000}},
                        {'cuenta': 'Resultados Acumulados', '2009': {'texto': '100,000', 'numero': 100000}, '2008': {'texto': '55,000', 'numero': 55000}},
                        {'cuenta': 'TOTAL PATRIMONIO', '2009': {'texto': '545,000', 'numero': 545000}, '2008': {'texto': '490,000', 'numero': 490000}},
                        
                        {'cuenta': 'TOTAL PASIVO Y PATRIMONIO', '2009': {'texto': '1,125,000', 'numero': 1125000}, '2008': {'texto': '1,045,000', 'numero': 1045000}}
                    ]
                }
            }
        }
    }
    
    return [datos_2009_2008]

def ejecutar_prueba_2009():
    """Ejecutar prueba específica para años ≤2009"""
    print("🧪 INICIANDO PRUEBA ESPECÍFICA PARA AÑOS ≤2009")
    print("=" * 60)
    
    # Crear analizador
    analizador = AnalisisVerticalHorizontal()
    
    # Crear datos de prueba
    datos_prueba = crear_datos_prueba_2009()
    años_analizar = ['2009', '2008']
    
    print(f"📊 Analizando años: {años_analizar}")
    print(f"📁 Archivos de prueba: {len(datos_prueba)}")
    print()
    
    # Realizar análisis vertical
    resultados = analizador.realizar_analisis_vertical_situacion_financiera(datos_prueba, años_analizar)
    
    # Mostrar resultados
    print("📈 RESULTADOS DEL ANÁLISIS VERTICAL")
    print("=" * 50)
    
    if resultados['errores']:
        print("❌ ERRORES ENCONTRADOS:")
        for error in resultados['errores']:
            print(f"   - {error}")
        print()
    
    if resultados['analisis_por_año']:
        print(f"✅ Análisis completado para {len(resultados['analisis_por_año'])} año(s)")
        print()
        
        for año, datos_año in resultados['analisis_por_año'].items():
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
            
            # Activos principales (top 5)
            if datos_año['activos']['cuentas']:
                print("🔝 TOP 5 ACTIVOS (% del Total de Activos):")
                activos_ordenados = sorted(datos_año['activos']['cuentas'], 
                                         key=lambda x: x['porcentaje_vertical'], reverse=True)[:5]
                for i, activo in enumerate(activos_ordenados, 1):
                    print(f"   {i}. {activo['cuenta']}: {activo['porcentaje_vertical']:.2f}%")
                print()
            
            # Pasivos principales (top 3)
            if datos_año['pasivos']['cuentas']:
                print("🔝 TOP 3 PASIVOS (% del Total de Pasivos):")
                pasivos_ordenados = sorted(datos_año['pasivos']['cuentas'], 
                                         key=lambda x: x['porcentaje_vertical'], reverse=True)[:3]
                for i, pasivo in enumerate(pasivos_ordenados, 1):
                    print(f"   {i}. {pasivo['cuenta']}: {pasivo['porcentaje_vertical']:.2f}%")
                print()
            
            # Patrimonio
            if datos_año['patrimonio']['cuentas']:
                print("🏛️ PATRIMONIO (% del Total de Patrimonio):")
                for patrimonio in datos_año['patrimonio']['cuentas']:
                    print(f"   - {patrimonio['cuenta']}: {patrimonio['porcentaje_vertical']:.2f}%")
                print()
            
            print("=" * 50)
    
    # Generar tablas
    try:
        tablas = analizador.generar_tabla_analisis_vertical(resultados)
        print(f"📊 Tablas generadas: {len(tablas)}")
        for nombre_tabla in tablas.keys():
            print(f"   - {nombre_tabla}")
        print()
    except Exception as e:
        print(f"❌ Error al generar tablas: {e}")
    
    print("✅ Prueba completada para años ≤2009")
    return resultados

if __name__ == "__main__":
    ejecutar_prueba_2009()