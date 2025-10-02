"""
Test de consolidación del Estado de Cambios en el Patrimonio
con múltiples archivos POST-2010
"""
import os
from analizador_financiero import AnalizadorFinanciero

print("="*80)
print("TEST: CONSOLIDACIÓN DEL ESTADO DE CAMBIOS EN EL PATRIMONIO")
print("="*80 + "\n")

# Crear analizador
analizador = AnalizadorFinanciero()

# Simular procesamiento de archivos
archivos_html = sorted([
    "consolidar/ReporteDetalleInformacionFinanciero (15).html",  # 2024
    "consolidar/ReporteDetalleInformacionFinanciero (16).html",  # 2023
    "consolidar/ReporteDetalleInformacionFinanciero (17).html",  # 2022
])

resultados_analisis = []

print("PASO 1: Procesando archivos...\n")
for archivo_html in archivos_html:
    print(f"Procesando: {os.path.basename(archivo_html)}")
    
    # Extraer datos
    datos_extraidos = analizador.extraer_datos_html(archivo_html)
    
    if datos_extraidos:
        # Generar resumen
        resumen = analizador.generar_resumen_analisis(datos_extraidos)
        
        # Agregar a resultados
        resultado = {
            'archivo': os.path.basename(archivo_html),
            'datos': datos_extraidos,
            'resumen': resumen
        }
        resultados_analisis.append(resultado)
        
        print(f"   Anio: {datos_extraidos.get('año_documento', 'N/A')}")
        print(f"   Empresa: {resumen['empresa']}\n")

print("="*80)
print(f"PASO 2: Consolidando {len(resultados_analisis)} archivos...\n")

# Consolidar
consolidado = analizador.consolidar_multiples_archivos_post_2010(resultados_analisis)

if consolidado and 'estado_cambios_patrimonio' in consolidado:
    df_patrimonio = consolidado['estado_cambios_patrimonio']
    
    print(f"CONSOLIDACION EXITOSA!")
    print(f"   Columnas: {list(df_patrimonio.columns)}")
    print(f"   Total cuentas: {len(df_patrimonio)}")
    
    print(f"\n{'='*80}")
    print("PRIMERAS 15 FILAS DEL DATAFRAME CONSOLIDADO:")
    print("="*80 + "\n")
    
    # Formatear números para mostrar
    df_display = df_patrimonio.head(15).copy()
    for col in df_display.columns:
        if col not in ['CCUENTA', 'Cuenta']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}" if x != 0 else "-")
    
    print(df_display.to_string(index=False))
    
    print(f"\n{'='*80}")
    print("ÚLTIMAS 5 FILAS (SALDOS FINALES):")
    print("="*80 + "\n")
    
    df_display = df_patrimonio.tail(5).copy()
    for col in df_display.columns:
        if col not in ['CCUENTA', 'Cuenta']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}" if x != 0 else "-")
    
    print(df_display.to_string(index=False))
    
    # Buscar saldo final en cada año
    print(f"\n{'='*80}")
    print("SALDOS FINALES POR ANIO:")
    print("="*80 + "\n")
    
    for _, fila in df_patrimonio.iterrows():
        if 'SALDOS' in str(fila['Cuenta']).upper() and 'DICIEMBRE' in str(fila['Cuenta']).upper():
            ccuenta = fila.get('CCUENTA', '')
            cuenta = fila['Cuenta']
            print(f" {ccuenta} - {cuenta}")
            for col in df_patrimonio.columns:
                if col not in ['CCUENTA', 'Cuenta'] and fila[col] != 0:
                    print(f"   {col}: {fila[col]:,.0f}")
            print()
    
else:
    print("No se pudo consolidar el Estado de Cambios en el Patrimonio")

print("\n" + "="*80)
print("TEST COMPLETADO")
print("="*80)
