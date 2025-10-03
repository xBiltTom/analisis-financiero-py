"""
Test Visual: Gráficos del Análisis Vertical Consolidado
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo
from analisis_vertical_mejorado import AnalisisVerticalMejorado
from analisis_vertical_consolidado import AnalisisVerticalConsolidado

print("="*80)
print("TEST VISUAL: GRÁFICOS DE ANÁLISIS VERTICAL CONSOLIDADO")
print("="*80 + "\n")

# Procesar 3 archivos
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:3]

print(f"Procesando {len(archivos)} archivos...")

# Extraer y analizar
analizador_vertical = AnalisisVerticalMejorado()
analisis_vertical_list = []

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    resultado_extractor = extraer_estados_desde_archivo(ruta)
    analisis = analizador_vertical.analizar_desde_extractor(resultado_extractor)
    analisis_vertical_list.append(analisis)
    print(f"  ✅ {resultado_extractor['año_documento']}")

# Consolidar
print("\nConsolidando...")
consolidador = AnalisisVerticalConsolidado()
consolidado = consolidador.consolidar_analisis_vertical(analisis_vertical_list)

# Generar gráficos para ACTIVOS
if 'situacion_financiera_activos' in consolidado:
    print("\n" + "="*80)
    print("GENERANDO GRÁFICOS PARA ACTIVOS")
    print("="*80)
    
    df_activos = consolidado['situacion_financiera_activos']
    graficos = consolidador.generar_graficos_tendencias(
        df_activos,
        "Activos - Estado de Situación Financiera",
        top_n=8
    )
    
    print(f"\n✅ {len(graficos)} gráficos generados:")
    print("  1. Gráfico de líneas de tendencia")
    print("  2. Mapa de calor (heatmap)")
    print("  3. Gráfico de barras agrupadas")
    
    # Guardar gráficos como HTML
    for i, fig in enumerate(graficos, 1):
        archivo_salida = f"grafico_activos_{i}.html"
        fig.write_html(archivo_salida)
        print(f"\n📊 Gráfico {i} guardado: {archivo_salida}")
        print(f"   Abre el archivo en tu navegador para visualizarlo")

print("\n" + "="*80)
print("✅ TEST VISUAL COMPLETADO")
print("="*80)
print("\nPara ver los gráficos:")
print("1. Abre los archivos .html en tu navegador")
print("2. O usa Streamlit: streamlit run analizador_financiero.py")
