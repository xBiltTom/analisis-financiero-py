"""
Test Visual: Gráficos del Análisis Horizontal Consolidado
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo
from analisis_horizontal_mejorado import AnalisisHorizontalMejorado
from analisis_horizontal_consolidado import AnalisisHorizontalConsolidado

print("="*80)
print("TEST VISUAL: GRÁFICOS DE ANÁLISIS HORIZONTAL CONSOLIDADO")
print("="*80 + "\n")

# Procesar 3 archivos
carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])[:3]

print(f"Procesando {len(archivos)} archivos...")

# Extraer y analizar
analizador_horizontal = AnalisisHorizontalMejorado()
analisis_horizontal_list = []

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    resultado_extractor = extraer_estados_desde_archivo(ruta)
    analisis = analizador_horizontal.analizar_desde_extractor(resultado_extractor)
    analisis_horizontal_list.append(analisis)
    print(f"  ✅ {resultado_extractor['año_documento']}")

# Consolidar
print("\nConsolidando...")
consolidador = AnalisisHorizontalConsolidado()
consolidado = consolidador.consolidar_analisis_horizontal(analisis_horizontal_list)

# Generar gráficos para SITUACIÓN FINANCIERA
if 'situacion_financiera' in consolidado:
    print("\n" + "="*80)
    print("GENERANDO GRÁFICOS PARA SITUACIÓN FINANCIERA")
    print("="*80)
    
    df_sf = consolidado['situacion_financiera']
    graficos = consolidador.generar_graficos_tendencias(
        df_sf,
        "Situación Financiera",
        top_n=8
    )
    
    print(f"\n✅ {len(graficos)} gráficos generados:")
    print("  1. Gráfico de líneas de tendencia")
    print("  2. Mapa de calor (heatmap)")
    print("  3. Gráfico de barras agrupadas (mayores variaciones)")
    print("  4. Gráfico de cascada (comparación más reciente)")
    
    # Guardar gráficos como HTML
    for i, fig in enumerate(graficos, 1):
        archivo_salida = f"grafico_ah_sf_{i}.html"
        fig.write_html(archivo_salida)
        print(f"\n📊 Gráfico {i} guardado: {archivo_salida}")
        print(f"   Abre el archivo en tu navegador para visualizarlo")

# Generar gráficos para ESTADO DE RESULTADOS
if 'resultados' in consolidado:
    print("\n" + "="*80)
    print("GENERANDO GRÁFICOS PARA ESTADO DE RESULTADOS")
    print("="*80)
    
    df_res = consolidado['resultados']
    graficos = consolidador.generar_graficos_tendencias(
        df_res,
        "Estado de Resultados",
        top_n=8
    )
    
    print(f"\n✅ {len(graficos)} gráficos generados")
    
    # Guardar gráficos como HTML
    for i, fig in enumerate(graficos, 1):
        archivo_salida = f"grafico_ah_resultados_{i}.html"
        fig.write_html(archivo_salida)
        print(f"\n📊 Gráfico {i} guardado: {archivo_salida}")

print("\n" + "="*80)
print("✅ TEST VISUAL COMPLETADO")
print("="*80)
print("\nPara ver los gráficos:")
print("1. Abre los archivos .html en tu navegador")
print("2. O usa Streamlit: streamlit run analizador_financiero.py")
