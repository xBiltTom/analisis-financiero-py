"""
Módulo de Análisis Vertical y Horizontal para Estados Financieros
Realiza cálculos de análisis vertical y horizontal sobre los datos extraídos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import re

class AnalisisVerticalHorizontal:
    def __init__(self):
        self.resultados_analisis = {}
    
    def realizar_analisis_vertical_situacion_financiera(self, datos_estados: List[Dict], años_disponibles: List[str]) -> Dict[str, Any]:
        """
        Realiza análisis vertical del Estado de Situación Financiera
        
        Args:
            datos_estados: Lista de datos por año con estados financieros
            años_disponibles: Lista de años disponibles para análisis
        
        Returns:
            Dict con resultados del análisis vertical
        """
        resultados = {
            'analisis_por_año': {},
            'resumen': {},
            'errores': []
        }
        
        # Procesar cada año disponible
        for año in años_disponibles:
            datos_año = self._encontrar_datos_por_año(datos_estados, año)
            if not datos_año:
                resultados['errores'].append(f"No se encontraron datos para el año {año}")
                continue
            
            # Buscar Estado de Situación Financiera
            estado_situacion = self._encontrar_estado_situacion_financiera(datos_año)
            if not estado_situacion:
                resultados['errores'].append(f"No se encontró Estado de Situación Financiera para {año}")
                continue
            
            # Realizar análisis vertical para este año
            analisis_año = self._calcular_analisis_vertical_año(estado_situacion, año)
            if analisis_año:
                resultados['analisis_por_año'][año] = analisis_año
        
        # Generar resumen comparativo si hay múltiples años
        if len(resultados['analisis_por_año']) > 1:
            resultados['resumen'] = self._generar_resumen_comparativo(resultados['analisis_por_año'])
        
        return resultados
    
    def _encontrar_datos_por_año(self, datos_estados: List[Dict], año: str) -> Optional[Dict]:
        """Encuentra los datos correspondientes a un año específico"""
        for datos in datos_estados:
            # Buscar el año en metadatos o años disponibles
            metadatos = datos.get('datos', {}).get('metadatos', {})
            año_reporte = metadatos.get('año', '')
            años_disponibles = datos.get('datos', {}).get('años_disponibles', [])
            
            if año_reporte == año or año in años_disponibles:
                return datos.get('datos', {})
        
        return None
    
    def _encontrar_estado_situacion_financiera(self, datos_año: Dict) -> Optional[List[Dict]]:
        """Encuentra el Estado de Situación Financiera en los datos del año"""
        estados_financieros = datos_año.get('estados_financieros', {})
        
        # Buscar por diferentes claves posibles
        claves_buscar = [
            'estado_situacion_financiera',
            'balance_general',
            'estado_situacion_patrimonial'
        ]
        
        for clave in claves_buscar:
            if clave in estados_financieros and estados_financieros[clave].get('datos'):
                return estados_financieros[clave]['datos']
        
        return None
    
    def _calcular_analisis_vertical_año(self, estado_situacion: List[Dict], año: str) -> Dict[str, Any]:
        """
        Calcula el análisis vertical para un año específico
        
        Formula:
        - Para ACTIVOS: (Cuenta / Total Activos) * 100
        - Para PASIVOS: (Cuenta / Total Pasivos) * 100
        """
        resultado = {
            'año': año,
            'activos': {
                'cuentas': [],
                'total_activos': 0,
                'errores': []
            },
            'pasivos': {
                'cuentas': [],
                'total_pasivos': 0,
                'errores': []
            },
            'patrimonio': {
                'cuentas': [],
                'total_patrimonio': 0,
                'errores': []
            }
        }
        
        # Encontrar totales principales para el año específico
        total_activos = self._encontrar_total_activos_año(estado_situacion, año)
        total_pasivos = self._encontrar_total_pasivos_año(estado_situacion, año)
        total_patrimonio = self._encontrar_total_patrimonio_año(estado_situacion, año)
        
        if total_activos is None:
            resultado['activos']['errores'].append("No se encontró Total de Activos")
            return resultado
        
        resultado['activos']['total_activos'] = total_activos
        resultado['pasivos']['total_pasivos'] = total_pasivos if total_pasivos else 0
        resultado['patrimonio']['total_patrimonio'] = total_patrimonio if total_patrimonio else 0
        
        # Clasificar y calcular porcentajes para cada cuenta
        for cuenta_data in estado_situacion:
            cuenta_nombre = cuenta_data.get('cuenta', '').strip()
            if not cuenta_nombre:
                continue
            
            # Obtener el valor numérico más reciente
            valor_numerico = self._extraer_valor_numerico(cuenta_data, año)
            if valor_numerico is None:
                continue
            
            # Clasificar la cuenta
            clasificacion = self._clasificar_cuenta(cuenta_nombre)
            
            if clasificacion == 'activo':
                porcentaje = (valor_numerico / total_activos) * 100 if total_activos != 0 else 0
                resultado['activos']['cuentas'].append({
                    'cuenta': cuenta_nombre,
                    'valor': valor_numerico,
                    'porcentaje_vertical': porcentaje,
                    'es_total': 'total' in cuenta_nombre.lower()
                })
            
            elif clasificacion == 'pasivo' and total_pasivos:
                porcentaje = (valor_numerico / total_pasivos) * 100 if total_pasivos != 0 else 0
                resultado['pasivos']['cuentas'].append({
                    'cuenta': cuenta_nombre,
                    'valor': valor_numerico,
                    'porcentaje_vertical': porcentaje,
                    'es_total': 'total' in cuenta_nombre.lower()
                })
            
            elif clasificacion == 'patrimonio' and total_patrimonio:
                porcentaje = (valor_numerico / total_patrimonio) * 100 if total_patrimonio != 0 else 0
                resultado['patrimonio']['cuentas'].append({
                    'cuenta': cuenta_nombre,
                    'valor': valor_numerico,
                    'porcentaje_vertical': porcentaje,
                    'es_total': 'total' in cuenta_nombre.lower()
                })
        
        return resultado
    
    def _encontrar_total_activos_año(self, estado_situacion: List[Dict], año: str) -> Optional[float]:
        """Encuentra el valor de Total de Activos para un año específico"""
        patrones_total_activos = [
            r'^total\s+activos?$',
            r'^activos?\s+totales?$',
            r'^total\s+de\s+activos?$'
        ]
        
        return self._buscar_valor_por_patrones_año(estado_situacion, patrones_total_activos, año)
    
    def _encontrar_total_pasivos_año(self, estado_situacion: List[Dict], año: str) -> Optional[float]:
        """Encuentra el valor de Total de Pasivos para un año específico"""
        patrones_total_pasivos = [
            r'^total\s+pasivos?$',
            r'^pasivos?\s+totales?$',
            r'^total\s+de\s+pasivos?$'
        ]
        
        return self._buscar_valor_por_patrones_año(estado_situacion, patrones_total_pasivos, año)
    
    def _encontrar_total_patrimonio_año(self, estado_situacion: List[Dict], año: str) -> Optional[float]:
        """Encuentra el valor de Total Patrimonio para un año específico"""
        patrones_total_patrimonio = [
            r'^total\s+patrimonio$',
            r'^patrimonio\s+total$',
            r'^total\s+patrimonio\s+neto$',
            r'^patrimonio\s+neto\s+total$'
        ]
        
        return self._buscar_valor_por_patrones_año(estado_situacion, patrones_total_patrimonio, año)
    
    def _encontrar_total_activos(self, estado_situacion: List[Dict]) -> Optional[float]:
        """Encuentra el valor de Total de Activos (método legacy)"""
        patrones_total_activos = [
            r'^total\s+activos?$',
            r'^activos?\s+totales?$',
            r'^total\s+de\s+activos?$'
        ]
        
        return self._buscar_valor_por_patrones(estado_situacion, patrones_total_activos)
    
    def _encontrar_total_pasivos(self, estado_situacion: List[Dict]) -> Optional[float]:
        """Encuentra el valor de Total de Pasivos (método legacy)"""
        patrones_total_pasivos = [
            r'^total\s+pasivos?$',
            r'^pasivos?\s+totales?$',
            r'^total\s+de\s+pasivos?$'
        ]
        
        return self._buscar_valor_por_patrones(estado_situacion, patrones_total_pasivos)
    
    def _encontrar_total_patrimonio(self, estado_situacion: List[Dict]) -> Optional[float]:
        """Encuentra el valor de Total Patrimonio (método legacy)"""
        patrones_total_patrimonio = [
            r'^total\s+patrimonio$',
            r'^patrimonio\s+total$',
            r'^total\s+patrimonio\s+neto$',
            r'^patrimonio\s+neto\s+total$'
        ]
        
        return self._buscar_valor_por_patrones(estado_situacion, patrones_total_patrimonio)
    
    def _buscar_valor_por_patrones_año(self, estado_situacion: List[Dict], patrones: List[str], año: str) -> Optional[float]:
        """Busca un valor usando patrones de regex para un año específico"""
        for cuenta_data in estado_situacion:
            cuenta_nombre = cuenta_data.get('cuenta', '').strip().lower()
            
            for patron in patrones:
                if re.match(patron, cuenta_nombre):
                    valor = self._extraer_valor_numerico(cuenta_data, año)
                    if valor is not None:
                        return valor
        
        return None
    
    def _buscar_valor_por_patrones(self, estado_situacion: List[Dict], patrones: List[str]) -> Optional[float]:
        """Busca un valor usando patrones de regex"""
        for cuenta_data in estado_situacion:
            cuenta_nombre = cuenta_data.get('cuenta', '').strip().lower()
            
            for patron in patrones:
                if re.match(patron, cuenta_nombre):
                    valor = self._extraer_valor_numerico(cuenta_data)
                    if valor is not None:
                        return valor
        
        return None
    
    def _extraer_valor_numerico(self, cuenta_data: Dict, año_preferido: str = None) -> Optional[float]:
        """Extrae el valor numérico de una cuenta, priorizando el año especificado"""
        # Buscar en todas las columnas que no sean 'cuenta'
        mejores_candidatos = []
        
        for clave, valor in cuenta_data.items():
            if clave == 'cuenta':
                continue
            
            if isinstance(valor, dict):
                numero = valor.get('numero', 0)
                texto = valor.get('texto', '')
                
                # Priorizar si el nombre de la columna contiene el año preferido
                if año_preferido and año_preferido in clave:
                    return numero if numero != 0 else 0
                
                if numero != 0:
                    mejores_candidatos.append((numero, texto, clave))
        
        # Si no encontramos el año preferido, usar el primer valor no cero
        if mejores_candidatos:
            return mejores_candidatos[0][0]
        
        return None
    
    def _clasificar_cuenta(self, cuenta_nombre: str) -> str:
        """Clasifica una cuenta como activo, pasivo o patrimonio"""
        cuenta_lower = cuenta_nombre.lower()
        
        # Patrones para activos
        if any(palabra in cuenta_lower for palabra in [
            'activo', 'efectivo', 'caja', 'banco', 'inventario', 'existencia',
            'cuenta por cobrar', 'cuentas por cobrar', 'inmueble', 'maquinaria', 'equipo',
            'propiedad', 'planta', 'intangible', 'inversión', 'depreciación'
        ]):
            return 'activo'
        
        # Patrones para pasivos
        elif any(palabra in cuenta_lower for palabra in [
            'pasivo', 'cuenta por pagar', 'cuentas por pagar', 'préstamo', 'deuda',
            'obligación', 'provisión', 'ingreso diferido', 'pasivo corriente', 'pasivo no corriente'
        ]):
            return 'pasivo'
        
        # Patrones para patrimonio
        elif any(palabra in cuenta_lower for palabra in [
            'patrimonio', 'capital', 'reserva', 'resultado', 'ganancia', 'pérdida',
            'superávit', 'excedente', 'revaluación'
        ]):
            return 'patrimonio'
        
        # Por defecto, intentar clasificar por posición o contexto
        return 'desconocido'
    
    def _generar_resumen_comparativo(self, analisis_por_año: Dict) -> Dict[str, Any]:
        """Genera un resumen comparativo entre años"""
        resumen = {
            'años_analizados': list(analisis_por_año.keys()),
            'totales_comparados': {},
            'variaciones_principales': []
        }
        
        # Comparar totales entre años
        años_ordenados = sorted(analisis_por_año.keys())
        
        for año in años_ordenados:
            data = analisis_por_año[año]
            resumen['totales_comparados'][año] = {
                'total_activos': data['activos']['total_activos'],
                'total_pasivos': data['pasivos']['total_pasivos'],
                'total_patrimonio': data['patrimonio']['total_patrimonio']
            }
        
        return resumen
    
    def generar_tabla_analisis_vertical(self, resultados_analisis: Dict) -> Dict[str, pd.DataFrame]:
        """Genera tablas de pandas para visualizar el análisis vertical"""
        tablas = {}
        
        for año, datos_año in resultados_analisis.get('analisis_por_año', {}).items():
            # Tabla para activos
            if datos_año['activos']['cuentas']:
                df_activos = pd.DataFrame(datos_año['activos']['cuentas'])
                df_activos['Año'] = año
                df_activos['Categoría'] = 'Activos'
                tablas[f'activos_{año}'] = df_activos
            
            # Tabla para pasivos
            if datos_año['pasivos']['cuentas']:
                df_pasivos = pd.DataFrame(datos_año['pasivos']['cuentas'])
                df_pasivos['Año'] = año
                df_pasivos['Categoría'] = 'Pasivos'
                tablas[f'pasivos_{año}'] = df_pasivos
            
            # Tabla para patrimonio
            if datos_año['patrimonio']['cuentas']:
                df_patrimonio = pd.DataFrame(datos_año['patrimonio']['cuentas'])
                df_patrimonio['Año'] = año
                df_patrimonio['Categoría'] = 'Patrimonio'
                tablas[f'patrimonio_{año}'] = df_patrimonio
        
        return tablas
    
    def exportar_analisis_vertical(self, resultados_analisis: Dict, archivo_salida: str):
        """Exporta el análisis vertical a un archivo Excel"""
        tablas = self.generar_tabla_analisis_vertical(resultados_analisis)
        
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            # Hoja de resumen
            if 'resumen' in resultados_analisis:
                resumen_df = pd.DataFrame([resultados_analisis['resumen']])
                resumen_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hojas por año y categoría
            for nombre_tabla, df in tablas.items():
                nombre_hoja = nombre_tabla.replace('_', ' ').title()[:31]  # Límite Excel
                df.to_excel(writer, sheet_name=nombre_hoja, index=False)

def ejemplo_uso():
    """Ejemplo de uso del análisis vertical"""
    # Este sería llamado desde el analizador principal
    analisis = AnalisisVerticalHorizontal()
    
    # Datos de ejemplo (normalmente vendrían del analizador principal)
    datos_ejemplo = [
        {
            'archivo': 'Reporte 2024.xls',
            'datos': {
                'metadatos': {'año': '2024'},
                'años_disponibles': ['2024', '2023'],
                'estados_financieros': {
                    'estado_situacion_financiera': {
                        'datos': [
                            {
                                'cuenta': 'Total Activos',
                                '2024': {'numero': 1000000, 'texto': '1,000,000'},
                                '2023': {'numero': 900000, 'texto': '900,000'}
                            },
                            {
                                'cuenta': 'Activos Corrientes',
                                '2024': {'numero': 600000, 'texto': '600,000'},
                                '2023': {'numero': 550000, 'texto': '550,000'}
                            }
                        ]
                    }
                }
            }
        }
    ]
    
    # Realizar análisis
    años = ['2024', '2023']
    resultados = analisis.realizar_analisis_vertical_situacion_financiera(datos_ejemplo, años)
    
    print("Análisis Vertical completado:")
    print(f"Años analizados: {list(resultados['analisis_por_año'].keys())}")
    print(f"Errores encontrados: {len(resultados['errores'])}")

if __name__ == "__main__":
    ejemplo_uso()