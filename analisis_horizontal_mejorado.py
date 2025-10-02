"""
Análisis Horizontal Mejorado para Estados Financieros
======================================================
Calcula análisis horizontal automático para formato POST-2010 (≥2010)

Estados analizados:
- ESTADO DE SITUACION FINANCIERA
- ESTADO DE RESULTADOS
- ESTADO DE FLUJO DE EFECTIVO

Fórmula:
Análisis Horizontal = ((Año Actual - Año Base) / Año Base) × 100

Donde:
- Año Base = Año anterior al año actual del reporte
- Año Actual = Año del documento

Ejemplo:
- Reporte 2024 (contiene años 2024 y 2023)
- Año Base = 2023
- Año Actual = 2024
- Análisis Horizontal 2024 = ((Valor 2024 - Valor 2023) / Valor 2023) × 100
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any


class AnalisisHorizontalMejorado:
    """Clase para realizar análisis horizontal automático de estados financieros POST-2010"""
    
    # Estados a analizar (POST-2010)
    ESTADOS_POST_2010 = {
        'balance': 'ESTADO DE SITUACION FINANCIERA',
        'resultados': 'ESTADO DE RESULTADOS',
        'flujo': 'ESTADO DE FLUJO DE EFECTIVO'
    }
    
    def __init__(self):
        self.resultados = {}
    
    def analizar_desde_extractor(self, resultados_extractor: Dict) -> Dict[str, Any]:
        """
        Realiza análisis horizontal desde los resultados del extractor mejorado
        
        Args:
            resultados_extractor: Dict con resultados de extractor_estados_mejorado.py
        
        Returns:
            Dict con análisis horizontal de los 3 estados principales
        """
        año_documento = resultados_extractor['año_documento']
        formato = resultados_extractor['formato']
        estados = resultados_extractor['estados']
        metadatos = resultados_extractor.get('metadatos', {})
        
        # Solo procesar formatos POST-2010
        if año_documento < 2010:
            return {
                'error': 'Análisis horizontal solo disponible para formato POST-2010 (≥2010)',
                'año_documento': año_documento,
                'formato': formato
            }
        
        print(f"\n{'='*60}")
        print(f"📊 ANÁLISIS HORIZONTAL - {metadatos.get('empresa', 'N/A')}")
        print(f"📅 Año: {año_documento} | Formato: {formato.upper()}")
        print(f"{'='*60}\n")
        
        resultados_analisis = {
            'año_documento': año_documento,
            'formato': formato,
            'empresa': metadatos.get('empresa', 'No identificada'),
            'tipo': metadatos.get('tipo', 'No especificado'),
            'estados_analizados': {},
            'resumen': {}
        }
        
        # Analizar Estado de Situación Financiera
        if 'balance' in estados:
            print(f"📋 Analizando Estado de Situación Financiera...")
            balance_analisis = self._analizar_estado_general(estados['balance'], 'balance')
            if balance_analisis:
                resultados_analisis['estados_analizados']['balance'] = balance_analisis
                print(f"   ✅ {balance_analisis['total_cuentas_analizadas']} cuentas analizadas")
                print(f"   📊 Año base: {balance_analisis['año_base']} | Año actual: {balance_analisis['año_actual']}\n")
            else:
                print(f"   ⚠️  No se pudo analizar (necesita al menos 2 años)\n")
        
        # Analizar Estado de Resultados
        if 'resultados' in estados:
            print(f"📋 Analizando Estado de Resultados...")
            resultados_estado = self._analizar_estado_general(estados['resultados'], 'resultados')
            if resultados_estado:
                resultados_analisis['estados_analizados']['resultados'] = resultados_estado
                print(f"   ✅ {resultados_estado['total_cuentas_analizadas']} cuentas analizadas")
                print(f"   📊 Año base: {resultados_estado['año_base']} | Año actual: {resultados_estado['año_actual']}\n")
            else:
                print(f"   ⚠️  No se pudo analizar (necesita al menos 2 años)\n")
        
        # Analizar Flujo de Efectivo
        if 'flujo' in estados:
            print(f"📋 Analizando Flujo de Efectivo...")
            flujo_analisis = self._analizar_estado_general(estados['flujo'], 'flujo')
            if flujo_analisis:
                resultados_analisis['estados_analizados']['flujo'] = flujo_analisis
                print(f"   ✅ {flujo_analisis['total_cuentas_analizadas']} cuentas analizadas")
                print(f"   📊 Año base: {flujo_analisis['año_base']} | Año actual: {flujo_analisis['año_actual']}\n")
            else:
                print(f"   ⚠️  No se pudo analizar (necesita al menos 2 años)\n")
        
        # Generar resumen
        resultados_analisis['resumen'] = self._generar_resumen(resultados_analisis)
        
        print(f"{'='*60}")
        print(f"✅ Análisis horizontal completado")
        print(f"{'='*60}\n")
        
        return resultados_analisis
    
    def _analizar_estado_general(self, estado: Dict, tipo_estado: str) -> Optional[Dict[str, Any]]:
        """
        Analiza cualquier estado financiero calculando el análisis horizontal
        
        Fórmula: ((Año Actual - Año Base) / Año Base) × 100
        
        Args:
            estado: Dict con datos del estado financiero
            tipo_estado: Tipo de estado ('balance', 'resultados', 'flujo')
        
        Returns:
            Dict con análisis horizontal o None si no hay suficientes años
        """
        años = estado['años']
        cuentas = estado['cuentas']
        
        # Verificar que haya al menos 2 años
        if len(años) < 2:
            return None
        
        # Ordenar años de más reciente a más antiguo
        años_ordenados = sorted(años, reverse=True)
        
        # Año actual = año más reciente (año del documento)
        año_actual = años_ordenados[0]
        # Año base = año anterior al actual
        año_base = años_ordenados[1]
        
        resultado = {
            'nombre_estado': estado['nombre'],
            'tipo_estado': tipo_estado,
            'año_actual': año_actual,
            'año_base': año_base,
            'cuentas_analizadas': [],
            'total_cuentas_analizadas': 0,
            'estadisticas': {
                'variaciones_positivas': 0,
                'variaciones_negativas': 0,
                'sin_variacion': 0,
                'no_calculables': 0
            }
        }
        
        # Analizar cada cuenta
        for cuenta in cuentas:
            nombre = cuenta['nombre']
            valores = cuenta['valores']
            es_total = cuenta.get('es_total', False)
            
            # Obtener valores de ambos años
            valor_actual = valores.get(año_actual, 0)
            valor_base = valores.get(año_base, 0)
            
            # Calcular análisis horizontal
            analisis_horizontal = None
            variacion_absoluta = None
            estado_variacion = 'no_calculable'
            
            if valor_base != 0:
                # Fórmula: ((Año Actual - Año Base) / Año Base) × 100
                variacion_absoluta = valor_actual - valor_base
                analisis_horizontal = (variacion_absoluta / valor_base) * 100
                
                # Clasificar variación
                if analisis_horizontal > 0:
                    estado_variacion = 'aumento'
                    resultado['estadisticas']['variaciones_positivas'] += 1
                elif analisis_horizontal < 0:
                    estado_variacion = 'disminucion'
                    resultado['estadisticas']['variaciones_negativas'] += 1
                else:
                    estado_variacion = 'sin_cambio'
                    resultado['estadisticas']['sin_variacion'] += 1
            else:
                # Casos especiales
                if valor_actual == 0:
                    estado_variacion = 'sin_cambio'
                    analisis_horizontal = 0.0
                    variacion_absoluta = 0.0
                    resultado['estadisticas']['sin_variacion'] += 1
                else:
                    # Base es 0 pero actual no es 0 = incremento infinito
                    estado_variacion = 'incremento_infinito'
                    analisis_horizontal = None  # No se puede calcular
                    variacion_absoluta = valor_actual
                    resultado['estadisticas']['no_calculables'] += 1
            
            cuenta_analisis = {
                'cuenta': nombre,
                'es_total': es_total,
                'valor_año_base': valor_base,
                'valor_año_actual': valor_actual,
                'variacion_absoluta': variacion_absoluta,
                'analisis_horizontal': analisis_horizontal,
                'estado_variacion': estado_variacion
            }
            
            resultado['cuentas_analizadas'].append(cuenta_analisis)
            resultado['total_cuentas_analizadas'] += 1
        
        return resultado
    
    def _generar_resumen(self, resultados: Dict) -> Dict[str, Any]:
        """Genera un resumen del análisis horizontal"""
        resumen = {
            'total_estados_analizados': len(resultados['estados_analizados']),
            'estados': [],
            'estadisticas_globales': {
                'variaciones_positivas': 0,
                'variaciones_negativas': 0,
                'sin_variacion': 0,
                'no_calculables': 0
            }
        }
        
        for clave, estado in resultados['estados_analizados'].items():
            resumen['estados'].append({
                'tipo': clave,
                'nombre': estado.get('nombre_estado', ''),
                'año_actual': estado.get('año_actual', 0),
                'año_base': estado.get('año_base', 0),
                'total_cuentas': estado.get('total_cuentas_analizadas', 0)
            })
            
            # Acumular estadísticas
            stats = estado.get('estadisticas', {})
            resumen['estadisticas_globales']['variaciones_positivas'] += stats.get('variaciones_positivas', 0)
            resumen['estadisticas_globales']['variaciones_negativas'] += stats.get('variaciones_negativas', 0)
            resumen['estadisticas_globales']['sin_variacion'] += stats.get('sin_variacion', 0)
            resumen['estadisticas_globales']['no_calculables'] += stats.get('no_calculables', 0)
        
        return resumen
    
    def exportar_a_excel(self, resultados: Dict, archivo_salida: str):
        """
        Exporta los resultados del análisis horizontal a Excel con formato
        """
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            
            # Hoja 1: Metadatos
            df_meta = pd.DataFrame([{
                'Empresa': resultados['empresa'],
                'Año Actual': resultados['año_documento'],
                'Tipo': resultados['tipo'],
                'Formato': resultados['formato'].upper(),
                'Estados Analizados': len(resultados['estados_analizados'])
            }])
            df_meta.to_excel(writer, sheet_name='Información', index=False)
            
            # Hoja 2: Estado de Situación Financiera
            if 'balance' in resultados['estados_analizados']:
                balance = resultados['estados_analizados']['balance']
                if balance['cuentas_analizadas']:
                    df_balance = pd.DataFrame(balance['cuentas_analizadas'])
                    # Redondear columnas numéricas
                    if 'analisis_horizontal' in df_balance.columns:
                        df_balance['analisis_horizontal'] = df_balance['analisis_horizontal'].round(2)
                    df_balance.to_excel(writer, sheet_name='Situación Financiera', index=False)
            
            # Hoja 3: Estado de Resultados
            if 'resultados' in resultados['estados_analizados']:
                resultados_estado = resultados['estados_analizados']['resultados']
                if resultados_estado['cuentas_analizadas']:
                    df_resultados = pd.DataFrame(resultados_estado['cuentas_analizadas'])
                    if 'analisis_horizontal' in df_resultados.columns:
                        df_resultados['analisis_horizontal'] = df_resultados['analisis_horizontal'].round(2)
                    df_resultados.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Hoja 4: Flujo de Efectivo
            if 'flujo' in resultados['estados_analizados']:
                flujo = resultados['estados_analizados']['flujo']
                if flujo['cuentas_analizadas']:
                    df_flujo = pd.DataFrame(flujo['cuentas_analizadas'])
                    if 'analisis_horizontal' in df_flujo.columns:
                        df_flujo['analisis_horizontal'] = df_flujo['analisis_horizontal'].round(2)
                    df_flujo.to_excel(writer, sheet_name='Flujo Efectivo', index=False)
            
            # Hoja 5: Resumen y Estadísticas
            resumen = resultados['resumen']
            estadisticas = resumen['estadisticas_globales']
            df_stats = pd.DataFrame([{
                'Variaciones Positivas (%)': estadisticas['variaciones_positivas'],
                'Variaciones Negativas (%)': estadisticas['variaciones_negativas'],
                'Sin Variación': estadisticas['sin_variacion'],
                'No Calculables': estadisticas['no_calculables']
            }])
            df_stats.to_excel(writer, sheet_name='Resumen', index=False)
        
        print(f"✅ Análisis horizontal exportado a: {archivo_salida}")


# Función de uso rápido
def analizar_archivo_html(ruta_archivo: str, exportar: bool = True) -> Dict:
    """
    Analiza un archivo HTML y genera análisis horizontal
    
    Args:
        ruta_archivo: Ruta al archivo HTML
        exportar: Si True, exporta a Excel automáticamente
    
    Returns:
        Dict con resultados del análisis
    """
    from extractor_estados_mejorado import extraer_estados_desde_archivo
    
    # Extraer estados financieros
    print(f"📄 Procesando: {ruta_archivo}")
    resultados_extractor = extraer_estados_desde_archivo(ruta_archivo)
    
    # Realizar análisis horizontal
    analizador = AnalisisHorizontalMejorado()
    resultados_analisis = analizador.analizar_desde_extractor(resultados_extractor)
    
    # Exportar a Excel si se solicita
    if exportar and 'error' not in resultados_analisis:
        import os
        nombre_base = os.path.basename(ruta_archivo).split('.')[0]
        archivo_salida = f"analisis_horizontal_{nombre_base}.xlsx"
        analizador.exportar_a_excel(resultados_analisis, archivo_salida)
    
    return resultados_analisis


if __name__ == "__main__":
    print("="*70)
    print("ANALISIS HORIZONTAL MEJORADO - DEMOSTRACION")
    print("="*70)
    
    # Ejemplo: Archivo 2024 (Post-2010)
    print("\nEjemplo: Archivo 2024 (Formato Post-2010)")
    print("-"*70)
    analisis_2024 = analizar_archivo_html(
        "consolidar/ReporteDetalleInformacionFinanciero (15).html"
    )
    
    if 'error' not in analisis_2024:
        print("\nRESULTADOS DEL ANALISIS:")
        print("-"*70)
        
        # Mostrar algunas cuentas de ejemplo
        if 'balance' in analisis_2024['estados_analizados']:
            balance = analisis_2024['estados_analizados']['balance']
            print(f"\nEstado de Situacion Financiera (primeras 5 cuentas):")
            for i, cuenta in enumerate(balance['cuentas_analizadas'][:5], 1):
                ah = cuenta['analisis_horizontal']
                if ah is not None:
                    print(f"{i}. {cuenta['cuenta'][:50]}")
                    print(f"   Anio base ({balance['año_base']}): {cuenta['valor_año_base']:,.0f}")
                    print(f"   Anio actual ({balance['año_actual']}): {cuenta['valor_año_actual']:,.0f}")
                    print(f"   Analisis Horizontal: {ah:.2f}%")
        
        # Mostrar estadísticas
        print(f"\nESTADISTICAS GLOBALES:")
        print("-"*70)
        stats = analisis_2024['resumen']['estadisticas_globales']
        print(f"   Variaciones positivas: {stats['variaciones_positivas']}")
        print(f"   Variaciones negativas: {stats['variaciones_negativas']}")
        print(f"   Sin variacion: {stats['sin_variacion']}")
        print(f"   No calculables: {stats['no_calculables']}")
    
    print("\n" + "="*70)
    print("DEMOSTRACION COMPLETADA")
    print("="*70)
