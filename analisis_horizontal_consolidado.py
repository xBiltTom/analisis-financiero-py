"""
Análisis Horizontal Consolidado para Estados Financieros
=========================================================
Consolida análisis horizontal de múltiples años en una vista unificada.

Funcionalidad:
- Consolida análisis horizontal de múltiples archivos POST-2010 (≥2010)
- Genera tabla comparativa con columnas: CUENTA | 2024 vs 2023 | 2023 vs 2022 | ...
- Los valores son porcentajes (%) del análisis horizontal
- Estados consolidados: Situación Financiera, Resultados, Flujo de Efectivo
- Genera gráficos de tendencias para cuentas principales
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px


class AnalisisHorizontalConsolidado:
    """Clase para consolidar análisis horizontal de múltiples períodos"""
    
    def __init__(self):
        self.resultados = {}
    
    def consolidar_analisis_horizontal(
        self, 
        resultados_analisis_list: List[Dict]
    ) -> Dict[str, pd.DataFrame]:
        """
        Consolida análisis horizontal de múltiples archivos POST-2010
        
        Args:
            resultados_analisis_list: Lista de diccionarios con análisis horizontal de cada archivo
        
        Returns:
            Dict con DataFrames consolidados por estado:
            {
                'situacion_financiera': DataFrame,
                'resultados': DataFrame,
                'flujo_efectivo': DataFrame
            }
        """
        # Filtrar solo archivos POST-2010
        archivos_post_2010 = [
            r for r in resultados_analisis_list 
            if r.get('año_documento', 0) >= 2010
        ]
        
        if not archivos_post_2010:
            return {}
        
        # Ordenar por año descendente (más reciente primero)
        archivos_post_2010.sort(key=lambda x: x.get('año_documento', 0), reverse=True)
        
        consolidado = {}
        
        # Consolidar Estado de Situación Financiera
        if all('balance' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_balance = self._consolidar_estado(archivos_post_2010, 'balance')
            if df_balance is not None:
                consolidado['situacion_financiera'] = df_balance
        
        # Consolidar Estado de Resultados
        if all('resultados' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_resultados = self._consolidar_estado(archivos_post_2010, 'resultados')
            if df_resultados is not None:
                consolidado['resultados'] = df_resultados
        
        # Consolidar Flujo de Efectivo
        if all('flujo' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_flujo = self._consolidar_estado(archivos_post_2010, 'flujo')
            if df_flujo is not None:
                consolidado['flujo_efectivo'] = df_flujo
        
        return consolidado
    
    def _consolidar_estado(self, archivos: List[Dict], tipo_estado: str) -> pd.DataFrame:
        """
        Consolida análisis horizontal de un estado específico
        
        Args:
            archivos: Lista de análisis horizontal
            tipo_estado: 'balance', 'resultados' o 'flujo'
        
        Returns:
            DataFrame consolidado
        """
        datos_consolidados = {}
        comparaciones_disponibles = []
        
        for archivo in archivos:
            estado = archivo['estados_analizados'][tipo_estado]
            año_actual = estado['año_actual']
            año_base = estado['año_base']
            comparacion_label = f"{año_actual} vs {año_base}"
            comparaciones_disponibles.append(comparacion_label)
            
            # Extraer análisis horizontal de cada cuenta
            for cuenta_analisis in estado['cuentas_analizadas']:
                cuenta = cuenta_analisis['cuenta']
                ah_porcentaje = cuenta_analisis.get('analisis_horizontal', None)
                
                if cuenta not in datos_consolidados:
                    datos_consolidados[cuenta] = {}
                
                # Guardar el porcentaje del análisis horizontal
                if ah_porcentaje is not None:
                    datos_consolidados[cuenta][comparacion_label] = ah_porcentaje
                else:
                    datos_consolidados[cuenta][comparacion_label] = None
        
        # Convertir a DataFrame
        if not datos_consolidados:
            return None
        
        df = pd.DataFrame(datos_consolidados).T
        df.index.name = 'Cuenta'
        df.reset_index(inplace=True)
        
        # Ordenar columnas por año (más reciente primero)
        columnas_comparaciones = sorted(
            [col for col in df.columns if col != 'Cuenta'],
            key=lambda x: int(x.split(' vs ')[0]),
            reverse=True
        )
        df = df[['Cuenta'] + columnas_comparaciones]
        
        return df
    
    def generar_graficos_tendencias(
        self, 
        df: pd.DataFrame, 
        titulo_estado: str,
        top_n: int = 10
    ) -> List[go.Figure]:
        """
        Genera gráficos de tendencias para las principales cuentas
        
        Args:
            df: DataFrame consolidado
            titulo_estado: Título del estado financiero
            top_n: Número de cuentas principales a graficar
        
        Returns:
            Lista de figuras de Plotly
        """
        figuras = []
        
        # Obtener columnas de comparaciones
        columnas_comp = [col for col in df.columns if col != 'Cuenta' and 'vs' in col]
        
        if len(columnas_comp) < 1:
            return figuras  # Necesita al menos 1 comparación
        
        # Filtrar cuentas con datos válidos
        df_valido = df.dropna(subset=columnas_comp, how='all')
        
        # Calcular promedio absoluto de porcentajes para identificar cuentas con mayor variación
        df_valido['variacion_promedio_abs'] = df_valido[columnas_comp].abs().mean(axis=1)
        df_top = df_valido.nlargest(top_n, 'variacion_promedio_abs')
        
        # Gráfico 1: Líneas de tendencia para top N cuentas
        fig1 = go.Figure()
        
        # Extraer años de las comparaciones para el eje X
        años_eje = []
        for comp in columnas_comp:
            año_actual = int(comp.split(' vs ')[0])
            if año_actual not in años_eje:
                años_eje.append(año_actual)
        años_eje = sorted(años_eje, reverse=True)
        
        for idx, row in df_top.iterrows():
            cuenta = row['Cuenta']
            valores = [row[comp] for comp in columnas_comp]
            
            fig1.add_trace(go.Scatter(
                x=años_eje[:len(valores)],
                y=valores,
                mode='lines+markers',
                name=cuenta[:40],  # Truncar nombres largos
                line=dict(width=2),
                marker=dict(size=8)
            ))
        
        fig1.update_layout(
            title=f"Tendencias de Variación - {titulo_estado} (Top {top_n})",
            xaxis_title="Año",
            yaxis_title="Análisis Horizontal (%)",
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.05
            ),
            height=500
        )
        
        figuras.append(fig1)
        
        # Gráfico 2: Heatmap de variaciones
        df_heatmap = df_top[['Cuenta'] + columnas_comp].set_index('Cuenta')
        
        fig2 = go.Figure(data=go.Heatmap(
            z=df_heatmap.values,
            x=df_heatmap.columns,
            y=[cuenta[:40] for cuenta in df_heatmap.index],
            colorscale='RdYlGn',
            zmid=0,  # Centrar en 0
            text=df_heatmap.values.round(2),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title="A.H. (%)")
        ))
        
        fig2.update_layout(
            title=f"Mapa de Calor de Variaciones - {titulo_estado}",
            xaxis_title="Período de Comparación",
            yaxis_title="Cuenta",
            height=400 + (len(df_heatmap) * 20)
        )
        
        figuras.append(fig2)
        
        # Gráfico 3: Barras para identificar mayores aumentos y disminuciones
        # Cada período (año) tiene un color distintivo
        df_top5 = df_valido.nlargest(5, 'variacion_promedio_abs')
        
        fig3 = go.Figure()
        
        # Definir paleta de colores para diferentes años
        colores_por_periodo = [
            '#1f77b4',  # Azul
            '#ff7f0e',  # Naranja
            '#2ca02c',  # Verde
            '#d62728',  # Rojo
            '#9467bd',  # Púrpura
            '#8c564b',  # Marrón
            '#e377c2',  # Rosa
            '#7f7f7f',  # Gris
            '#bcbd22',  # Verde lima
            '#17becf'   # Cian
        ]
        
        for idx, comp in enumerate(columnas_comp):
            valores = df_top5[comp].tolist()
            cuentas = [c[:30] for c in df_top5['Cuenta'].tolist()]
            
            # Asignar color por período (índice)
            color = colores_por_periodo[idx % len(colores_por_periodo)]
            
            fig3.add_trace(go.Bar(
                name=comp,
                x=cuentas,
                y=valores,
                text=[f"{v:+.1f}%" if pd.notnull(v) else "" for v in valores],
                textposition='outside',
                marker_color=color
            ))
        
        fig3.update_layout(
            title=f"Mayores Variaciones - {titulo_estado} (Top 5)",
            xaxis_title="Cuenta",
            yaxis_title="Análisis Horizontal (%)",
            barmode='group',
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        figuras.append(fig3)
        
        # Gráfico 4: Gráfico de cascada para la comparación más reciente
        if len(columnas_comp) > 0:
            comp_reciente = columnas_comp[0]
            df_cascada = df_top.copy()
            df_cascada = df_cascada.sort_values(by=comp_reciente, ascending=False)
            
            fig4 = go.Figure(go.Waterfall(
                name="Variación",
                orientation="v",
                measure=["relative"] * len(df_cascada),
                x=[c[:30] for c in df_cascada['Cuenta'].tolist()],
                y=df_cascada[comp_reciente].tolist(),
                text=[f"{v:+.1f}%" if pd.notnull(v) else "N/A" for v in df_cascada[comp_reciente].tolist()],
                textposition="outside",
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": "green"}},
                decreasing={"marker": {"color": "red"}},
                totals={"marker": {"color": "blue"}}
            ))
            
            fig4.update_layout(
                title=f"Cascada de Variaciones - {titulo_estado} ({comp_reciente})",
                xaxis_title="Cuenta",
                yaxis_title="Variación (%)",
                height=450,
                showlegend=False
            )
            
            figuras.append(fig4)
        
        return figuras
    
    def exportar_consolidado_excel(
        self, 
        consolidado: Dict[str, pd.DataFrame], 
        archivo_salida: str
    ):
        """
        Exporta análisis horizontal consolidado a Excel
        
        Args:
            consolidado: Dict con DataFrames consolidados
            archivo_salida: Nombre del archivo Excel de salida
        """
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            
            if 'situacion_financiera' in consolidado:
                df = consolidado['situacion_financiera'].copy()
                # Formatear valores con sufijo %
                columnas_comp = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_comp:
                    df[col] = df[col].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Situación Financiera', index=False)
            
            if 'resultados' in consolidado:
                df = consolidado['resultados'].copy()
                columnas_comp = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_comp:
                    df[col] = df[col].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Estado de Resultados', index=False)
            
            if 'flujo_efectivo' in consolidado:
                df = consolidado['flujo_efectivo'].copy()
                columnas_comp = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_comp:
                    df[col] = df[col].apply(lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Flujo de Efectivo', index=False)
        
        print(f"✅ Análisis horizontal consolidado exportado a: {archivo_salida}")


# Función de prueba
if __name__ == "__main__":
    print("="*70)
    print("ANALISIS HORIZONTAL CONSOLIDADO - TEST")
    print("="*70)
    
    # Este script requiere tener análisis horizontal ya realizados
    print("\n⚠️ Este módulo debe usarse después de realizar análisis horizontal individual")
    print("✅ Módulo creado exitosamente")
