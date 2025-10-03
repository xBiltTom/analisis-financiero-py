"""
Análisis Vertical Consolidado para Estados Financieros
=======================================================
Consolida análisis vertical de múltiples años en una vista unificada.

Funcionalidad:
- Consolida análisis vertical de múltiples archivos POST-2010 (≥2010)
- Genera tabla comparativa con columnas: CUENTA | 2024 | 2023 | 2022 | ...
- Los valores son porcentajes (%) del análisis vertical
- Estados consolidados: Situación Financiera, Resultados, Flujo de Efectivo
- Genera gráficos de tendencias para cuentas principales
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px


class AnalisisVerticalConsolidado:
    """Clase para consolidar análisis vertical de múltiples períodos"""
    
    def __init__(self):
        self.resultados = {}
    
    def consolidar_analisis_vertical(
        self, 
        resultados_analisis_list: List[Dict]
    ) -> Dict[str, pd.DataFrame]:
        """
        Consolida análisis vertical de múltiples archivos POST-2010
        
        Args:
            resultados_analisis_list: Lista de diccionarios con análisis vertical de cada archivo
        
        Returns:
            Dict con DataFrames consolidados por estado:
            {
                'situacion_financiera_activos': DataFrame,
                'situacion_financiera_pasivos': DataFrame,
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
        
        # Consolidar Estado de Situación Financiera - ACTIVOS
        if all('balance' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_activos = self._consolidar_balance_activos(archivos_post_2010)
            if df_activos is not None:
                consolidado['situacion_financiera_activos'] = df_activos
        
        # Consolidar Estado de Situación Financiera - PASIVOS
        if all('balance' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_pasivos = self._consolidar_balance_pasivos(archivos_post_2010)
            if df_pasivos is not None:
                consolidado['situacion_financiera_pasivos'] = df_pasivos
        
        # Consolidar Estado de Resultados
        if all('resultados' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_resultados = self._consolidar_resultados(archivos_post_2010)
            if df_resultados is not None:
                consolidado['resultados'] = df_resultados
        
        # Consolidar Flujo de Efectivo
        if all('flujo' in r.get('estados_analizados', {}) for r in archivos_post_2010):
            df_flujo = self._consolidar_flujo(archivos_post_2010)
            if df_flujo is not None:
                consolidado['flujo_efectivo'] = df_flujo
        
        return consolidado
    
    def _consolidar_balance_activos(self, archivos: List[Dict]) -> pd.DataFrame:
        """Consolida análisis vertical de ACTIVOS"""
        datos_consolidados = {}
        años_disponibles = []
        
        for archivo in archivos:
            año_doc = archivo['año_documento']
            años_disponibles.append(año_doc)
            
            balance = archivo['estados_analizados']['balance']
            activos = balance.get('activos', [])
            
            for cuenta_analisis in activos:
                cuenta = cuenta_analisis['cuenta']
                av_porcentaje = cuenta_analisis.get('analisis_vertical', None)
                
                if cuenta not in datos_consolidados:
                    datos_consolidados[cuenta] = {}
                
                # Guardar el porcentaje del análisis vertical
                if av_porcentaje is not None:
                    datos_consolidados[cuenta][año_doc] = av_porcentaje
                else:
                    datos_consolidados[cuenta][año_doc] = None
        
        # Convertir a DataFrame
        if not datos_consolidados:
            return None
        
        df = pd.DataFrame(datos_consolidados).T
        df.index.name = 'Cuenta'
        df.reset_index(inplace=True)
        
        # Ordenar columnas de años de más reciente a más antiguo
        columnas_años = sorted([col for col in df.columns if col != 'Cuenta'], reverse=True)
        df = df[['Cuenta'] + columnas_años]
        
        return df
    
    def _consolidar_balance_pasivos(self, archivos: List[Dict]) -> pd.DataFrame:
        """Consolida análisis vertical de PASIVOS"""
        datos_consolidados = {}
        años_disponibles = []
        
        for archivo in archivos:
            año_doc = archivo['año_documento']
            años_disponibles.append(año_doc)
            
            balance = archivo['estados_analizados']['balance']
            pasivos = balance.get('pasivos', [])
            
            for cuenta_analisis in pasivos:
                cuenta = cuenta_analisis['cuenta']
                av_porcentaje = cuenta_analisis.get('analisis_vertical', None)
                
                if cuenta not in datos_consolidados:
                    datos_consolidados[cuenta] = {}
                
                if av_porcentaje is not None:
                    datos_consolidados[cuenta][año_doc] = av_porcentaje
                else:
                    datos_consolidados[cuenta][año_doc] = None
        
        # Convertir a DataFrame
        if not datos_consolidados:
            return None
        
        df = pd.DataFrame(datos_consolidados).T
        df.index.name = 'Cuenta'
        df.reset_index(inplace=True)
        
        # Ordenar columnas
        columnas_años = sorted([col for col in df.columns if col != 'Cuenta'], reverse=True)
        df = df[['Cuenta'] + columnas_años]
        
        return df
    
    def _consolidar_resultados(self, archivos: List[Dict]) -> pd.DataFrame:
        """Consolida análisis vertical de Estado de Resultados"""
        datos_consolidados = {}
        años_disponibles = []
        
        for archivo in archivos:
            año_doc = archivo['año_documento']
            años_disponibles.append(año_doc)
            
            resultados = archivo['estados_analizados']['resultados']
            cuentas = resultados.get('cuentas_analizadas', [])
            
            for cuenta_analisis in cuentas:
                cuenta = cuenta_analisis['cuenta']
                av_porcentaje = cuenta_analisis.get('analisis_vertical', None)
                
                if cuenta not in datos_consolidados:
                    datos_consolidados[cuenta] = {}
                
                if av_porcentaje is not None:
                    datos_consolidados[cuenta][año_doc] = av_porcentaje
                else:
                    datos_consolidados[cuenta][año_doc] = None
        
        # Convertir a DataFrame
        if not datos_consolidados:
            return None
        
        df = pd.DataFrame(datos_consolidados).T
        df.index.name = 'Cuenta'
        df.reset_index(inplace=True)
        
        # Ordenar columnas
        columnas_años = sorted([col for col in df.columns if col != 'Cuenta'], reverse=True)
        df = df[['Cuenta'] + columnas_años]
        
        return df
    
    def _consolidar_flujo(self, archivos: List[Dict]) -> pd.DataFrame:
        """Consolida análisis vertical de Flujo de Efectivo"""
        datos_consolidados = {}
        años_disponibles = []
        
        for archivo in archivos:
            año_doc = archivo['año_documento']
            años_disponibles.append(año_doc)
            
            flujo = archivo['estados_analizados']['flujo']
            cuentas = flujo.get('cuentas_analizadas', [])
            
            for cuenta_analisis in cuentas:
                cuenta = cuenta_analisis['cuenta']
                av_porcentaje = cuenta_analisis.get('analisis_vertical', None)
                
                if cuenta not in datos_consolidados:
                    datos_consolidados[cuenta] = {}
                
                if av_porcentaje is not None:
                    datos_consolidados[cuenta][año_doc] = av_porcentaje
                else:
                    datos_consolidados[cuenta][año_doc] = None
        
        # Convertir a DataFrame
        if not datos_consolidados:
            return None
        
        df = pd.DataFrame(datos_consolidados).T
        df.index.name = 'Cuenta'
        df.reset_index(inplace=True)
        
        # Ordenar columnas
        columnas_años = sorted([col for col in df.columns if col != 'Cuenta'], reverse=True)
        df = df[['Cuenta'] + columnas_años]
        
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
        
        # Obtener columnas de años
        columnas_años = [col for col in df.columns if col != 'Cuenta' and isinstance(col, int)]
        
        if len(columnas_años) < 2:
            return figuras  # Necesita al menos 2 años para tendencias
        
        # Filtrar cuentas con datos válidos
        df_valido = df.dropna(subset=columnas_años, how='all')
        
        # Calcular promedio de porcentajes para identificar cuentas principales
        df_valido['promedio_abs'] = df_valido[columnas_años].abs().mean(axis=1)
        df_top = df_valido.nlargest(top_n, 'promedio_abs')
        
        # Gráfico 1: Líneas de tendencia para top N cuentas
        fig1 = go.Figure()
        
        for idx, row in df_top.iterrows():
            cuenta = row['Cuenta']
            valores = [row[año] for año in sorted(columnas_años, reverse=True)]
            años_sorted = sorted(columnas_años, reverse=True)
            
            fig1.add_trace(go.Scatter(
                x=años_sorted,
                y=valores,
                mode='lines+markers',
                name=cuenta[:40],  # Truncar nombres largos
                line=dict(width=2),
                marker=dict(size=8)
            ))
        
        fig1.update_layout(
            title=f"Tendencias - {titulo_estado} (Top {top_n} Cuentas)",
            xaxis_title="Año",
            yaxis_title="Análisis Vertical (%)",
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
        
        # Gráfico 2: Heatmap de evolución
        # Preparar datos para heatmap
        df_heatmap = df_top[['Cuenta'] + columnas_años].set_index('Cuenta')
        df_heatmap = df_heatmap[sorted(columnas_años)]  # Ordenar años ascendente para heatmap
        
        fig2 = go.Figure(data=go.Heatmap(
            z=df_heatmap.values,
            x=df_heatmap.columns,
            y=[cuenta[:40] for cuenta in df_heatmap.index],
            colorscale='RdYlGn',
            text=df_heatmap.values.round(2),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title="A.V. (%)")
        ))
        
        fig2.update_layout(
            title=f"Mapa de Calor - {titulo_estado}",
            xaxis_title="Año",
            yaxis_title="Cuenta",
            height=400 + (len(df_heatmap) * 20)
        )
        
        figuras.append(fig2)
        
        # Gráfico 3: Barras apiladas para comparar composición año a año (solo para top 5)
        df_top5 = df_valido.nlargest(5, 'promedio_abs')
        
        fig3 = go.Figure()
        
        for idx, row in df_top5.iterrows():
            cuenta = row['Cuenta']
            valores = [row[año] for año in sorted(columnas_años, reverse=True)]
            años_sorted = sorted(columnas_años, reverse=True)
            
            fig3.add_trace(go.Bar(
                name=cuenta[:30],
                x=años_sorted,
                y=valores,
                text=[f"{v:.1f}%" if pd.notnull(v) else "" for v in valores],
                textposition='auto'
            ))
        
        fig3.update_layout(
            title=f"Composición por Año - {titulo_estado} (Top 5)",
            xaxis_title="Año",
            yaxis_title="Análisis Vertical (%)",
            barmode='group',
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        figuras.append(fig3)
        
        return figuras
    
    def exportar_consolidado_excel(
        self, 
        consolidado: Dict[str, pd.DataFrame], 
        archivo_salida: str
    ):
        """
        Exporta análisis vertical consolidado a Excel
        
        Args:
            consolidado: Dict con DataFrames consolidados
            archivo_salida: Nombre del archivo Excel de salida
        """
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            
            if 'situacion_financiera_activos' in consolidado:
                df = consolidado['situacion_financiera_activos'].copy()
                # Formatear valores con sufijo %
                columnas_años = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_años:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Situación F. - Activos', index=False)
            
            if 'situacion_financiera_pasivos' in consolidado:
                df = consolidado['situacion_financiera_pasivos'].copy()
                columnas_años = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_años:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Situación F. - Pasivos', index=False)
            
            if 'resultados' in consolidado:
                df = consolidado['resultados'].copy()
                columnas_años = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_años:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Estado de Resultados', index=False)
            
            if 'flujo_efectivo' in consolidado:
                df = consolidado['flujo_efectivo'].copy()
                columnas_años = [col for col in df.columns if col != 'Cuenta']
                for col in columnas_años:
                    df[col] = df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
                df.to_excel(writer, sheet_name='Flujo de Efectivo', index=False)
        
        print(f"✅ Análisis vertical consolidado exportado a: {archivo_salida}")


# Función de prueba
if __name__ == "__main__":
    print("="*70)
    print("ANALISIS VERTICAL CONSOLIDADO - TEST")
    print("="*70)
    
    # Este script requiere tener análisis vertical ya realizados
    print("\n⚠️ Este módulo debe usarse después de realizar análisis vertical individual")
    print("✅ Módulo creado exitosamente")
