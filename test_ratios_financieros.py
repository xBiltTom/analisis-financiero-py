"""
Test del Calculador de Ratios Financieros
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo
from ratios_financieros import CalculadorRatiosFinancieros

print("="*80)
print("TEST: CALCULADOR DE RATIOS FINANCIEROS")
print("="*80 + "\n")

# Procesar múltiples archivos de la carpeta consolidar
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:3]  # Primeros 3

print(f"📁 Archivos a procesar: {len(archivos)}")
for archivo in archivos:
    print(f"  - {archivo}")

# Paso 1: Extraer estados financieros de cada archivo
print(f"\n{'='*80}")
print("PASO 1: Extrayendo estados financieros...")
print("="*80)

resultados_extractor_list = []
for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    print(f"\n📄 Procesando: {archivo}")
    resultado = extraer_estados_desde_archivo(ruta)
    resultados_extractor_list.append(resultado)
    print(f"   ✅ Año: {resultado['año_documento']} | Estados: {len(resultado['estados'])}")

# Paso 2: Calcular ratios financieros
print(f"\n{'='*80}")
print("PASO 2: Calculando ratios financieros...")
print("="*80)

calculador = CalculadorRatiosFinancieros()
resultados_ratios = calculador.calcular_ratios_desde_extractor(resultados_extractor_list)

if 'error' in resultados_ratios:
    print(f"❌ Error: {resultados_ratios['error']}")
else:
    print(f"\n✅ Ratios calculados para {len(resultados_ratios['años'])} años")
    print(f"🏢 Empresa: {resultados_ratios['empresa']}")
    
    # Mostrar ratios por año
    print(f"\n{'='*80}")
    print("RATIOS POR AÑO")
    print("="*80)
    
    for año in sorted(resultados_ratios['años']):
        ratios = resultados_ratios['ratios_por_año'][año]
        print(f"\n📅 Año {año}:")
        print(f"   Liquidez Corriente:      {ratios.get('liquidez_corriente', 'N/A'):.2f}" if ratios.get('liquidez_corriente') else "   Liquidez Corriente:      N/A")
        print(f"   Prueba Ácida:            {ratios.get('prueba_acida', 'N/A'):.2f}" if ratios.get('prueba_acida') else "   Prueba Ácida:            N/A")
        print(f"   Razón Deuda Total:       {ratios.get('razon_deuda_total', 'N/A'):.1%}" if ratios.get('razon_deuda_total') else "   Razón Deuda Total:       N/A")
        print(f"   Razón Deuda/Patrimonio:  {ratios.get('razon_deuda_patrimonio', 'N/A'):.2f}" if ratios.get('razon_deuda_patrimonio') else "   Razón Deuda/Patrimonio:  N/A")
    
    # Mostrar resumen estadístico
    if resultados_ratios.get('resumen'):
        print(f"\n{'='*80}")
        print("RESUMEN ESTADÍSTICO")
        print("="*80)
        
        for ratio_nombre, stats in resultados_ratios['resumen'].items():
            if stats.get('promedio'):
                print(f"\n{ratio_nombre.replace('_', ' ').title()}:")
                print(f"   Mínimo:   {stats['min']:.2f}")
                print(f"   Máximo:   {stats['max']:.2f}")
                print(f"   Promedio: {stats['promedio']:.2f}")

# Paso 3: Generar gráficos
print(f"\n{'='*80}")
print("PASO 3: Generando gráficos...")
print("="*80)

if 'error' not in resultados_ratios:
    graficos = calculador.generar_graficos_ratios(resultados_ratios)
    print(f"\n✅ {len(graficos)} gráficos generados")
    
    # Guardar gráficos como HTML
    for i, fig in enumerate(graficos, 1):
        archivo_salida = f"grafico_ratios_{i}.html"
        fig.write_html(archivo_salida)
        print(f"   📊 Gráfico {i} guardado: {archivo_salida}")

# Paso 4: Exportar a Excel
print(f"\n{'='*80}")
print("PASO 4: Exportando a Excel...")
print("="*80)

if 'error' not in resultados_ratios:
    archivo_excel = "test_ratios_financieros.xlsx"
    calculador.exportar_ratios_excel(resultados_ratios, archivo_excel)

print(f"\n{'='*80}")
print("✅ TEST COMPLETADO")
print("="*80)
