"""
Ratios Financieros para Estados Financieros POST-2010
======================================================
Calcula ratios financieros clave a partir del Estado de Situación Financiera y Estado de Resultados.

Ratios implementados (10 total):
- RATIOS DE LIQUIDEZ:
  * Liquidez Corriente: Total Activos Corrientes / Total Pasivos Corrientes
  * Prueba Ácida: (Total Activos Corrientes - Inventarios) / Total Pasivos Corrientes

- RATIOS DE ENDEUDAMIENTO:
  * Razón de Deuda Total: Total Pasivos / Total Activos
  * Razón de Deuda/Patrimonio: Total Pasivos / Total Patrimonio

- RATIOS DE RENTABILIDAD:
  * Margen Neto: Ganancia (Pérdida) Neta del Ejercicio / Ingresos de Actividades Ordinarias
  * ROA (Return on Assets): Ganancia (Pérdida) Neta del Ejercicio / Total Activos
  * ROE (Return on Equity): Ganancia (Pérdida) Neta del Ejercicio / Total Patrimonio

- RATIOS DE ACTIVIDAD:
  * Rotación de Activos Totales: Ingresos de Actividades Ordinarias / Total Activos
  * Rotación de Cuentas por Cobrar: Ingresos Ordinarios / Promedio Cuentas por Cobrar
  * Rotación de Inventarios: Costo de Ventas / Promedio Inventarios
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import re


class CalculadorRatiosFinancieros:
    """Clase para calcular ratios financieros desde el Estado de Situación Financiera"""
    
    def __init__(self):
        self.ratios_calculados = {}
    
    def calcular_ratios_desde_extractor(
        self, 
        resultados_extractor_list: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calcula ratios financieros de múltiples archivos POST-2010
        
        Args:
            resultados_extractor_list: Lista de resultados del extractor por archivo
        
        Returns:
            Dict con ratios calculados por año y gráficos
        """
        # Filtrar solo archivos POST-2010
        archivos_post_2010 = [
            r for r in resultados_extractor_list 
            if r.get('año_documento', 0) >= 2010
        ]
        
        if not archivos_post_2010:
            return {'error': 'No hay archivos POST-2010 disponibles'}
        
        # Ordenar por año
        archivos_post_2010.sort(key=lambda x: x.get('año_documento', 0))
        
        resultados = {
            'ratios_por_año': {},
            'años': [],
            'empresa': archivos_post_2010[0].get('metadatos', {}).get('empresa', 'N/A'),
            'resumen': {}
        }
        
        # Calcular ratios para cada año
        for archivo in archivos_post_2010:
            año = archivo['año_documento']
            
            # Verificar que tenga estado de situación financiera
            if 'balance' not in archivo.get('estados', {}):
                continue
            
            balance = archivo['estados']['balance']
            
            # Obtener estado de resultados si existe (necesario para ratios de rentabilidad)
            resultados_estado = archivo['estados'].get('resultados', None)
            
            # Calcular ratios para este año
            ratios_año = self._calcular_ratios_año(balance, resultados_estado, año)
            
            if ratios_año:
                resultados['ratios_por_año'][año] = ratios_año
                resultados['años'].append(año)
        
        # Generar resumen
        if resultados['ratios_por_año']:
            resultados['resumen'] = self._generar_resumen(resultados['ratios_por_año'])
        
        return resultados
    
    def _calcular_ratios_año(self, balance: Dict, resultados_estado: Optional[Dict], año: int) -> Optional[Dict[str, float]]:
        """
        Calcula todos los ratios para un año específico
        
        Args:
            balance: Dict con el estado de situación financiera
            resultados_estado: Dict con el estado de resultados (opcional)
            año: Año del análisis
        
        Returns:
            Dict con ratios calculados o None si faltan datos
        """
        cuentas = balance['cuentas']
        años_disponibles = balance['años']
        
        # Usar el año más reciente disponible
        año_analisis = años_disponibles[0] if años_disponibles else año
        
        # Buscar valores necesarios del balance
        valores = self._extraer_valores_balance(cuentas, año_analisis)
        
        # Buscar valores necesarios del estado de resultados
        valores_resultados = {}
        if resultados_estado:
            valores_resultados = self._extraer_valores_resultados(
                resultados_estado['cuentas'], 
                año_analisis
            )
        
        # Verificar que tengamos los valores mínimos necesarios
        if not valores.get('total_activos') or not valores.get('total_pasivos'):
            return None
        
        ratios = {}
        
        # RATIOS DE LIQUIDEZ
        if valores.get('activos_corrientes') and valores.get('pasivos_corrientes'):
            if valores['pasivos_corrientes'] != 0:
                ratios['liquidez_corriente'] = valores['activos_corrientes'] / valores['pasivos_corrientes']
            else:
                ratios['liquidez_corriente'] = None
            
            # Prueba Ácida
            if valores.get('inventarios') is not None:
                activos_sin_inventarios = valores['activos_corrientes'] - valores['inventarios']
                if valores['pasivos_corrientes'] != 0:
                    ratios['prueba_acida'] = activos_sin_inventarios / valores['pasivos_corrientes']
                else:
                    ratios['prueba_acida'] = None
            else:
                ratios['prueba_acida'] = None
        else:
            ratios['liquidez_corriente'] = None
            ratios['prueba_acida'] = None
        
        # RATIOS DE ENDEUDAMIENTO
        if valores['total_activos'] != 0:
            ratios['razon_deuda_total'] = valores['total_pasivos'] / valores['total_activos']
        else:
            ratios['razon_deuda_total'] = None
        
        if valores.get('total_patrimonio') and valores['total_patrimonio'] != 0:
            ratios['razon_deuda_patrimonio'] = valores['total_pasivos'] / valores['total_patrimonio']
        else:
            ratios['razon_deuda_patrimonio'] = None
        
        # ✨ NUEVOS: RATIOS DE RENTABILIDAD
        if valores_resultados.get('ganancia_neta') is not None:
            ganancia_neta = valores_resultados['ganancia_neta']
            
            # Margen Neto
            if valores_resultados.get('ingresos_ordinarios') and valores_resultados['ingresos_ordinarios'] != 0:
                ratios['margen_neto'] = ganancia_neta / valores_resultados['ingresos_ordinarios']
            else:
                ratios['margen_neto'] = None
            
            # ROA (Return on Assets)
            if valores['total_activos'] != 0:
                ratios['roa'] = ganancia_neta / valores['total_activos']
            else:
                ratios['roa'] = None
            
            # ROE (Return on Equity)
            if valores.get('total_patrimonio') and valores['total_patrimonio'] != 0:
                ratios['roe'] = ganancia_neta / valores['total_patrimonio']
            else:
                ratios['roe'] = None
        else:
            ratios['margen_neto'] = None
            ratios['roa'] = None
            ratios['roe'] = None
        
        # ✨ NUEVOS: RATIOS DE ACTIVIDAD
        # Necesitamos tanto el balance como el estado de resultados para estos ratios
        if valores_resultados.get('ingresos_ordinarios'):
            ingresos_ordinarios = valores_resultados['ingresos_ordinarios']
            
            # 1. Rotación de Activos Totales = Ingresos Ordinarios / Total Activos
            if valores['total_activos'] != 0:
                ratios['rotacion_activos_totales'] = ingresos_ordinarios / valores['total_activos']
            else:
                ratios['rotacion_activos_totales'] = None
            
            # 2. Rotación de Cuentas por Cobrar = Ingresos Ordinarios / Promedio CxC
            valores_multianio = self._extraer_valores_multianio(cuentas, año_analisis, años_disponibles)
            if valores_multianio.get('promedio_cuentas_cobrar') and valores_multianio['promedio_cuentas_cobrar'] != 0:
                ratios['rotacion_cuentas_cobrar'] = ingresos_ordinarios / valores_multianio['promedio_cuentas_cobrar']
            else:
                ratios['rotacion_cuentas_cobrar'] = None
            
            # 3. Rotación de Inventarios = Costo de Ventas / Promedio Inventarios
            if (valores_resultados.get('costo_ventas') and 
                valores_multianio.get('promedio_inventarios') and 
                valores_multianio['promedio_inventarios'] != 0):
                ratios['rotacion_inventarios'] = valores_resultados['costo_ventas'] / valores_multianio['promedio_inventarios']
            else:
                ratios['rotacion_inventarios'] = None
        else:
            ratios['rotacion_activos_totales'] = None
            ratios['rotacion_cuentas_cobrar'] = None
            ratios['rotacion_inventarios'] = None
        
        return ratios
    
    def _extraer_valores_balance(self, cuentas: List[Dict], año: int) -> Dict[str, float]:
        """
        Extrae los valores necesarios del balance para calcular ratios
        
        Args:
            cuentas: Lista de cuentas del balance
            año: Año a analizar
        
        Returns:
            Dict con valores extraídos
        """
        valores = {
            'total_activos': 0,
            'activos_corrientes': 0,
            'inventarios': 0,
            'total_pasivos': 0,
            'pasivos_corrientes': 0,
            'total_patrimonio': 0
        }
        
        # ✨ NUEVO: Detectar zona de activos corrientes
        en_activos_corrientes = False
        
        for cuenta in cuentas:
            nombre_upper = cuenta['nombre'].upper()
            valor = cuenta['valores'].get(año, 0)
            
            # Detectar inicio de Activos Corrientes
            if 'ACTIVOS CORRIENTES' in nombre_upper and 'TOTAL' not in nombre_upper:
                en_activos_corrientes = True
                continue
            
            # Detectar fin de Activos Corrientes (cuando llega a Total Activos Corrientes o Activos No Corrientes)
            if en_activos_corrientes and (
                self._es_activos_corrientes(nombre_upper) or 
                'ACTIVOS NO CORRIENTES' in nombre_upper
            ):
                en_activos_corrientes = False
            
            # Total Activos
            if self._es_total_activos(nombre_upper):
                valores['total_activos'] = abs(valor)
            
            # Activos Corrientes
            elif self._es_activos_corrientes(nombre_upper):
                valores['activos_corrientes'] = abs(valor)
            
            # Inventarios - SOLO dentro de la zona de Activos Corrientes
            elif en_activos_corrientes and self._es_inventarios(nombre_upper) and valor > 0:
                valores['inventarios'] = abs(valor)
            
            # Total Pasivos
            elif self._es_total_pasivos(nombre_upper):
                valores['total_pasivos'] = abs(valor)
            
            # Pasivos Corrientes
            elif self._es_pasivos_corrientes(nombre_upper):
                valores['pasivos_corrientes'] = abs(valor)
            
            # Total Patrimonio
            elif self._es_total_patrimonio(nombre_upper):
                valores['total_patrimonio'] = abs(valor)
        
        return valores
    
    def _extraer_valores_multianio(self, cuentas: List[Dict], año_actual: int, años_disponibles: List[int]) -> Dict[str, float]:
        """
        Extrae valores de múltiples años para calcular promedios (Cuentas por Cobrar e Inventarios)
        FÓRMULA CORREGIDA: K + F + K' + F' / 2
        Donde K y F son las DOS PARTES de "Cuentas por Cobrar Comerciales y Otras Cuentas por Cobrar"
        
        Args:
            cuentas: Lista de cuentas del balance
            año_actual: Año actual a analizar
            años_disponibles: Lista de años disponibles en los datos
        
        Returns:
            Dict con promedios calculados según fórmula (K + F + K' + F') / 2
        """
        valores = {
            'promedio_cuentas_cobrar': None,
            'promedio_inventarios': None
        }
        
        # Buscar el año anterior
        año_anterior = None
        for año in sorted(años_disponibles, reverse=True):
            if año < año_actual:
                año_anterior = año
                break
        
        if año_anterior is None:
            return valores  # No hay año anterior, no se pueden calcular promedios
        
        # ✨ NUEVO: Variables para implementar fórmula K + F + K' + F' / 2
        K_actual = 0    # Primera parte año actual
        F_actual = 0    # Segunda parte año actual  
        K_anterior = 0  # Primera parte año anterior
        F_anterior = 0  # Segunda parte año anterior
        
        inv_actual_total = 0
        inv_anterior_total = 0
        
        # Contadores para debug
        partes_cxc_encontradas = []
        inv_subdivisiones_encontradas = 0
        
        # ✨ DETECCIÓN EXACTA: Buscar las DOS apariciones de "Cuentas por Cobrar" en orden de aparición
        for cuenta in cuentas:
            nombre_upper = cuenta['nombre'].upper()
            # Obtener valores, probando tanto con int como con str 
            valor_actual = cuenta['valores'].get(año_actual) or cuenta['valores'].get(str(año_actual)) or 0
            valor_anterior = cuenta['valores'].get(año_anterior) or cuenta['valores'].get(str(año_anterior)) or 0
            
            # Detectar si es una aparición de "Cuentas por Cobrar Comerciales y Otras Cuentas por Cobrar"
            if self._es_cuentas_por_cobrar(nombre_upper):
                # Convertir valores a números absolutos
                val_actual = abs(float(valor_actual)) if valor_actual else 0
                val_anterior = abs(float(valor_anterior)) if valor_anterior else 0
                
                # Guardar esta aparición con su orden
                partes_cxc_encontradas.append({
                    'nombre': cuenta['nombre'],
                    'valor_actual': val_actual,
                    'valor_anterior': val_anterior
                })
                
                print(f"📋 Parte CxC #{len(partes_cxc_encontradas)}: {cuenta['nombre']}")
                print(f"    {año_actual}: {val_actual:,.0f} | {año_anterior}: {val_anterior:,.0f}")
            
            # Inventarios (mantener lógica existente)
            elif self._es_inventarios(nombre_upper):
                inv_actual_total += abs(valor_actual)
                inv_anterior_total += abs(valor_anterior)
                inv_subdivisiones_encontradas += 1
                
                if valor_actual > 0 or valor_anterior > 0:
                    print(f"   � Inventarios Subdivisión {inv_subdivisiones_encontradas}: {cuenta['nombre']}")
                    print(f"      {año_actual}: {valor_actual:,.0f} | {año_anterior}: {valor_anterior:,.0f}")
        
        # ✨ CORRECCIÓN: K = Primera aparición, F = Última aparición de "Cuentas por Cobrar Comerciales y Otras Cuentas por Cobrar"
        # Filtrar solo las apariciones completas (que contienen "Y OTRAS")
        partes_completas = [p for p in partes_cxc_encontradas if "Y OTRAS" in p['nombre'].upper()]
        
        if len(partes_completas) >= 2:
            # K = Primera aparición completa, F = Última aparición completa
            K_actual = partes_completas[0]['valor_actual']
            K_anterior = partes_completas[0]['valor_anterior']
            
            # F = Última aparición completa (no segunda)
            F_actual = partes_completas[-1]['valor_actual']
            F_anterior = partes_completas[-1]['valor_anterior']
            
            print(f"📋 Parte K (Primera completa): {partes_completas[0]['nombre']}")
            print(f"    {año_actual}: {K_actual:,.0f} | {año_anterior}: {K_anterior:,.0f}")
            print(f"📋 Parte F (Última completa): {partes_completas[-1]['nombre']}")
            print(f"    {año_actual}: {F_actual:,.0f} | {año_anterior}: {F_anterior:,.0f}")
            
        elif len(partes_completas) == 1:
            # Solo una aparición completa - usar como K, F = 0
            K_actual = partes_completas[0]['valor_actual']
            K_anterior = partes_completas[0]['valor_anterior']
            F_actual = 0
            F_anterior = 0
            
            print(f"⚠️ Solo 1 aparición completa CxC: {partes_completas[0]['nombre']}")
            print(f"    K: {K_actual:,.0f} | K': {K_anterior:,.0f}, F = F' = 0")
            
        elif len(partes_cxc_encontradas) >= 2:
            # Fallback: usar primera y segunda aparición general
            K_actual = partes_cxc_encontradas[0]['valor_actual']
            K_anterior = partes_cxc_encontradas[0]['valor_anterior']
            F_actual = partes_cxc_encontradas[1]['valor_actual']
            F_anterior = partes_cxc_encontradas[1]['valor_anterior']
            
            print(f"📋 Fallback K (Primera general): {partes_cxc_encontradas[0]['nombre']}")
            print(f"    {año_actual}: {K_actual:,.0f} | {año_anterior}: {K_anterior:,.0f}")
            print(f"📋 Fallback F (Segunda general): {partes_cxc_encontradas[1]['nombre']}")
            print(f"    {año_actual}: {F_actual:,.0f} | {año_anterior}: {F_anterior:,.0f}")
            
        elif len(partes_cxc_encontradas) == 1:
            # Solo una aparición encontrada - usar como K, F = 0
            K_actual = partes_cxc_encontradas[0]['valor_actual']
            K_anterior = partes_cxc_encontradas[0]['valor_anterior']
            F_actual = 0
            F_anterior = 0
            
            print(f"   � Solo Parte K encontrada: {partes_cxc_encontradas[0]['nombre']}")
            print(f"      {año_actual}: {K_actual:,.0f} | {año_anterior}: {K_anterior:,.0f}")
        
        # ✨ NUEVO: Aplicar fórmula correcta (K + F + K' + F') / 2
        if K_actual > 0 or F_actual > 0 or K_anterior > 0 or F_anterior > 0:
            suma_total = K_actual + F_actual + K_anterior + F_anterior
            valores['promedio_cuentas_cobrar'] = suma_total / 2
            
            print(f"   ✅ FÓRMULA: (K + F + K' + F') / 2")
            print(f"   ✅ CÁLCULO: ({K_actual:,.0f} + {F_actual:,.0f} + {K_anterior:,.0f} + {F_anterior:,.0f}) / 2")
            print(f"   ✅ RESULTADO: {suma_total:,.0f} / 2 = {valores['promedio_cuentas_cobrar']:,.0f}")
        
        # Inventarios (mantener cálculo existente)
        if inv_actual_total > 0 or inv_anterior_total > 0:
            valores['promedio_inventarios'] = (inv_actual_total + inv_anterior_total) / 2
            print(f"   ✅ Inventarios Total: {año_actual}={inv_actual_total:,.0f}, {año_anterior}={inv_anterior_total:,.0f}")
            print(f"   ✅ Inventarios Promedio: {valores['promedio_inventarios']:,.0f}")
        
        return valores
    
    def _es_cuentas_por_cobrar(self, nombre: str) -> bool:
        """Detecta si es Cuentas por Cobrar"""
        patrones = [
            r'CUENTAS\s+POR\s+COBRAR\s+COMERCIALES',
            r'CUENTAS\s+POR\s+COBRAR\s+COMERCIALES\s+Y\s+OTRAS',
            r'CUENTAS\s+POR\s+COBRAR\s+COMERCIALES\s*\(NETO\)',
            r'^CUENTAS\s+POR\s+COBRAR\s+COMERCIALES'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _extraer_valores_resultados(self, cuentas: List[Dict], año: int) -> Dict[str, float]:
        """
        Extrae los valores necesarios del Estado de Resultados para calcular ratios de rentabilidad y actividad
        
        Args:
            cuentas: Lista de cuentas del estado de resultados
            año: Año a analizar
        
        Returns:
            Dict con valores extraídos
        """
        valores = {
            'ganancia_neta': None,
            'ingresos_ordinarios': None,
            'costo_ventas': None
        }
        
        for cuenta in cuentas:
            nombre_upper = cuenta['nombre'].upper()
            valor = cuenta['valores'].get(año, 0)
            
            # Ganancia (Pérdida) Neta del Ejercicio
            if self._es_ganancia_neta(nombre_upper):
                valores['ganancia_neta'] = valor  # Puede ser negativo
            
            # Ingresos de Actividades Ordinarias
            elif self._es_ingresos_ordinarios(nombre_upper):
                valores['ingresos_ordinarios'] = abs(valor)
            
            # Costo de Ventas
            elif self._es_costo_ventas(nombre_upper):
                valores['costo_ventas'] = abs(valor)  # Convertir a positivo
        
        return valores
    
    def _es_ganancia_neta(self, nombre: str) -> bool:
        """Detecta si es Ganancia (Pérdida) Neta del Ejercicio"""
        patrones = [
            r'GANANCIA\s*\(P[ÉE]RDIDA\)\s*NETA\s+DEL\s+EJERCICIO',
            r'GANANCIA\s+NETA\s+DEL\s+EJERCICIO',
            r'P[ÉE]RDIDA\s+NETA\s+DEL\s+EJERCICIO',
            r'RESULTADO\s+DEL\s+EJERCICIO',
            r'UTILIDAD\s+NETA\s+DEL\s+EJERCICIO',
            r'^GANANCIA\s*\(P[ÉE]RDIDA\)\s*NETA',
            r'^UTILIDAD\s+NETA$',
            r'^GANANCIA\s+NETA$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_ingresos_ordinarios(self, nombre: str) -> bool:
        """Detecta si es Ingresos de Actividades Ordinarias"""
        patrones = [
            r'INGRESOS?\s+DE\s+ACTIVIDADES\s+ORDINARIAS',
            r'TOTAL\s+DE\s+INGRESOS?\s+DE\s+ACTIVIDADES\s+ORDINARIAS',
            r'INGRESOS?\s+OPERACIONALES?',
            r'VENTAS\s+NETAS?',
            r'^INGRESOS?\s+DE\s+ACTIVIDADES\s+ORDINARIAS'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_costo_ventas(self, nombre: str) -> bool:
        """Detecta si es Costo de Ventas"""
        patrones = [
            r'^COSTO\s+DE\s+VENTAS?$',
            r'COSTO\s+DE\s+VENTAS?\s*\(OPERACIONALES?\)',
            r'COSTO\s+DE\s+LAS?\s+VENTAS?',
            r'COSTOS?\s+DE\s+VENTAS?'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_total_activos(self, nombre: str) -> bool:
        """Detecta si es Total Activos"""
        patrones = [
            r'^TOTAL\s+DE?\s*ACTIVOS?$',
            r'^TOTAL\s+ACTIVOS?$',
            r'^ACTIVOS?\s+TOTALES?$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_activos_corrientes(self, nombre: str) -> bool:
        """Detecta si es Total Activos Corrientes"""
        patrones = [
            r'^TOTAL\s+ACTIVOS?\s+CORRIENTES?$',
            r'^ACTIVOS?\s+CORRIENTES?\s+TOTALES?$',
            r'^TOTAL\s+DE\s+ACTIVOS?\s+CORRIENTES?$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_activos_no_corrientes(self, nombre: str) -> bool:
        """Detecta si es Total Activos No Corrientes"""
        patrones = [
            r'^TOTAL\s+ACTIVOS?\s+NO\s+CORRIENTES?$',
            r'^ACTIVOS?\s+NO\s+CORRIENTES?\s+TOTALES?$',
            r'^TOTAL\s+DE\s+ACTIVOS?\s+NO\s+CORRIENTES?$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_inventarios(self, nombre: str) -> bool:
        """Detecta si es Inventarios"""
        patrones = [
            r'INVENTARIOS?$',
            r'EXISTENCIAS?$',
            r'^INVENTARIOS?\s+NETOS?$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_total_pasivos(self, nombre: str) -> bool:
        """Detecta si es Total Pasivos"""
        patrones = [
            r'^TOTAL\s+DE?\s*PASIVOS?$',
            r'^TOTAL\s+PASIVOS?$',
            r'^PASIVOS?\s+TOTALES?$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_pasivos_corrientes(self, nombre: str) -> bool:
        """Detecta si es Total Pasivos Corrientes"""
        patrones = [
            r'^TOTAL\s+PASIVOS?\s+CORRIENTES?$',
            r'^PASIVOS?\s+CORRIENTES?\s+TOTALES?$',
            r'^TOTAL\s+DE\s+PASIVOS?\s+CORRIENTES?$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _es_total_patrimonio(self, nombre: str) -> bool:
        """Detecta si es Total Patrimonio"""
        patrones = [
            r'^TOTAL\s+PATRIMONIO$',
            r'^PATRIMONIO\s+TOTAL$',
            r'^TOTAL\s+PATRIMONIO\s+NETO$',
            r'^PATRIMONIO\s+NETO\s+TOTAL$'
        ]
        return any(re.search(patron, nombre) for patron in patrones)
    
    def _generar_resumen(self, ratios_por_año: Dict[int, Dict[str, float]]) -> Dict[str, Any]:
        """Genera resumen estadístico de los ratios"""
        resumen = {
            'liquidez_corriente': {'min': None, 'max': None, 'promedio': None},
            'prueba_acida': {'min': None, 'max': None, 'promedio': None},
            'razon_deuda_total': {'min': None, 'max': None, 'promedio': None},
            'razon_deuda_patrimonio': {'min': None, 'max': None, 'promedio': None},
            'margen_neto': {'min': None, 'max': None, 'promedio': None},
            'roa': {'min': None, 'max': None, 'promedio': None},
            'roe': {'min': None, 'max': None, 'promedio': None},
            'rotacion_activos_totales': {'min': None, 'max': None, 'promedio': None},
            'rotacion_cuentas_cobrar': {'min': None, 'max': None, 'promedio': None},
            'rotacion_inventarios': {'min': None, 'max': None, 'promedio': None}
        }
        
        for ratio_nombre in resumen.keys():
            valores = [
                ratios[ratio_nombre] 
                for ratios in ratios_por_año.values() 
                if ratios.get(ratio_nombre) is not None
            ]
            
            if valores:
                resumen[ratio_nombre]['min'] = min(valores)
                resumen[ratio_nombre]['max'] = max(valores)
                resumen[ratio_nombre]['promedio'] = sum(valores) / len(valores)
        
        return resumen
    
    def generar_graficos_ratios(self, resultados: Dict[str, Any]) -> List[go.Figure]:
        """
        Genera gráficos de barras para visualizar tendencias de ratios
        
        Args:
            resultados: Dict con ratios calculados
        
        Returns:
            Lista de figuras de Plotly
        """
        figuras = []
        
        if not resultados.get('ratios_por_año'):
            return figuras
        
        años = sorted(resultados['años'])
        ratios_por_año = resultados['ratios_por_año']
        
        # Gráfico 1: Ratios de Liquidez
        fig1 = go.Figure()
        
        # Liquidez Corriente
        valores_lc = [ratios_por_año[año].get('liquidez_corriente') for año in años]
        fig1.add_trace(go.Bar(
            name='Liquidez Corriente',
            x=años,
            y=valores_lc,
            text=[f"{v:.2f}" if v else "N/A" for v in valores_lc],
            textposition='outside',
            marker_color='lightblue'
        ))
        
        # Prueba Ácida
        valores_pa = [ratios_por_año[año].get('prueba_acida') for año in años]
        fig1.add_trace(go.Bar(
            name='Prueba Ácida',
            x=años,
            y=valores_pa,
            text=[f"{v:.2f}" if v else "N/A" for v in valores_pa],
            textposition='outside',
            marker_color='darkblue'
        ))
        
        fig1.update_layout(
            title='Ratios de Liquidez por Año',
            xaxis_title='Año',
            yaxis_title='Ratio',
            barmode='group',
            hovermode='x unified',
            height=450,
            showlegend=True
        )
        
        # Agregar línea de referencia en 1.0 (valor ideal mínimo)
        fig1.add_hline(y=1.0, line_dash="dash", line_color="red", 
                       annotation_text="Nivel recomendado: 1.0")
        
        figuras.append(fig1)
        
        # Gráfico 2: Ratios de Endeudamiento
        fig2 = go.Figure()
        
        # Razón de Deuda Total
        valores_rdt = [ratios_por_año[año].get('razon_deuda_total') for año in años]
        fig2.add_trace(go.Bar(
            name='Razón Deuda Total',
            x=años,
            y=valores_rdt,
            text=[f"{v:.2%}" if v else "N/A" for v in valores_rdt],
            textposition='outside',
            marker_color='lightcoral'
        ))
        
        # Razón de Deuda/Patrimonio
        valores_rdp = [ratios_por_año[año].get('razon_deuda_patrimonio') for año in años]
        fig2.add_trace(go.Bar(
            name='Razón Deuda/Patrimonio',
            x=años,
            y=valores_rdp,
            text=[f"{v:.2f}" if v else "N/A" for v in valores_rdp],
            textposition='outside',
            marker_color='darkred'
        ))
        
        fig2.update_layout(
            title='Ratios de Endeudamiento por Año',
            xaxis_title='Año',
            yaxis_title='Ratio',
            barmode='group',
            hovermode='x unified',
            height=450,
            showlegend=True
        )
        
        # Agregar línea de referencia en 0.5 (50% recomendado para deuda total)
        fig2.add_hline(y=0.5, line_dash="dash", line_color="orange", 
                       annotation_text="Nivel recomendado deuda: 50%")
        
        figuras.append(fig2)
        
        # Gráfico 3: Tendencia de Liquidez Corriente (línea)
        fig3 = go.Figure()
        
        fig3.add_trace(go.Scatter(
            x=años,
            y=valores_lc,
            mode='lines+markers+text',
            name='Liquidez Corriente',
            text=[f"{v:.2f}" if v else "" for v in valores_lc],
            textposition='top center',
            line=dict(color='blue', width=3),
            marker=dict(size=10)
        ))
        
        fig3.update_layout(
            title='Tendencia de Liquidez Corriente',
            xaxis_title='Año',
            yaxis_title='Ratio',
            hovermode='x unified',
            height=400
        )
        
        fig3.add_hline(y=1.0, line_dash="dash", line_color="red", 
                       annotation_text="Nivel mínimo: 1.0")
        
        figuras.append(fig3)
        
        # Gráfico 4: Tendencia de Endeudamiento (línea)
        fig4 = go.Figure()
        
        fig4.add_trace(go.Scatter(
            x=años,
            y=valores_rdt,
            mode='lines+markers+text',
            name='Razón Deuda Total',
            text=[f"{v:.1%}" if v else "" for v in valores_rdt],
            textposition='top center',
            line=dict(color='red', width=3),
            marker=dict(size=10)
        ))
        
        fig4.update_layout(
            title='Tendencia de Endeudamiento',
            xaxis_title='Año',
            yaxis_title='Ratio',
            hovermode='x unified',
            height=400
        )
        
        fig4.add_hline(y=0.5, line_dash="dash", line_color="orange", 
                       annotation_text="Nivel máximo recomendado: 50%")
        
        figuras.append(fig4)
        
        # ✨ NUEVOS GRÁFICOS DE RENTABILIDAD
        
        # Gráfico 5: Ratios de Rentabilidad (Barras agrupadas)
        fig5 = go.Figure()
        
        # Margen Neto
        valores_mn = [ratios_por_año[año].get('margen_neto') for año in años]
        valores_mn_pct = [v * 100 if v is not None else None for v in valores_mn]
        fig5.add_trace(go.Bar(
            name='Margen Neto (%)',
            x=años,
            y=valores_mn_pct,
            text=[f"{v:.3f}%" if v is not None else "N/A" for v in valores_mn_pct],
            textposition='outside',
            marker_color='lightgreen'
        ))
        
        # ROA
        valores_roa = [ratios_por_año[año].get('roa') for año in años]
        valores_roa_pct = [v * 100 if v is not None else None for v in valores_roa]
        fig5.add_trace(go.Bar(
            name='ROA (%)',
            x=años,
            y=valores_roa_pct,
            text=[f"{v:.3f}%" if v is not None else "N/A" for v in valores_roa_pct],
            textposition='outside',
            marker_color='mediumseagreen'
        ))
        
        # ROE
        valores_roe = [ratios_por_año[año].get('roe') for año in años]
        valores_roe_pct = [v * 100 if v is not None else None for v in valores_roe]
        fig5.add_trace(go.Bar(
            name='ROE (%)',
            x=años,
            y=valores_roe_pct,
            text=[f"{v:.3f}%" if v is not None else "N/A" for v in valores_roe_pct],
            textposition='outside',
            marker_color='darkgreen'
        ))
        
        fig5.update_layout(
            title='Ratios de Rentabilidad por Año',
            xaxis_title='Año',
            yaxis_title='Porcentaje (%)',
            barmode='group',
            hovermode='x unified',
            height=450,
            showlegend=True
        )
        
        figuras.append(fig5)
        
        # Gráfico 6: Tendencia de Margen Neto (línea)
        fig6 = go.Figure()
        
        fig6.add_trace(go.Scatter(
            x=años,
            y=valores_mn_pct,
            mode='lines+markers+text',
            name='Margen Neto',
            text=[f"{v:.3f}%" if v is not None else "" for v in valores_mn_pct],
            textposition='top center',
            line=dict(color='green', width=3),
            marker=dict(size=10)
        ))
        
        fig6.update_layout(
            title='Tendencia del Margen Neto',
            xaxis_title='Año',
            yaxis_title='Porcentaje (%)',
            hovermode='x unified',
            height=400
        )
        
        figuras.append(fig6)
        
        # Gráfico 7: Comparación ROA vs ROE (líneas)
        fig7 = go.Figure()
        
        fig7.add_trace(go.Scatter(
            x=años,
            y=valores_roa_pct,
            mode='lines+markers+text',
            name='ROA',
            text=[f"{v:.3f}%" if v is not None else "" for v in valores_roa_pct],
            textposition='top center',
            line=dict(color='teal', width=3),
            marker=dict(size=10, symbol='circle')
        ))
        
        fig7.add_trace(go.Scatter(
            x=años,
            y=valores_roe_pct,
            mode='lines+markers+text',
            name='ROE',
            text=[f"{v:.3f}%" if v is not None else "" for v in valores_roe_pct],
            textposition='bottom center',
            line=dict(color='darkgreen', width=3),
            marker=dict(size=10, symbol='square')
        ))
        
        fig7.update_layout(
            title='Comparación ROA vs ROE',
            xaxis_title='Año',
            yaxis_title='Porcentaje (%)',
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        figuras.append(fig7)
        
        # ===== GRÁFICO 8: RATIOS DE ACTIVIDAD - BARRAS AGRUPADAS =====
        fig8 = go.Figure()
        
        # Extraer valores para ratios de actividad
        valores_rat = [ratios_por_año[año].get('rotacion_activos_totales') for año in años]
        valores_rcxc = [ratios_por_año[año].get('rotacion_cuentas_cobrar') for año in años]
        valores_ri = [ratios_por_año[año].get('rotacion_inventarios') for año in años]
        
        fig8.add_trace(go.Bar(
            name='Rotación Activos Totales',
            x=años,
            y=valores_rat,
            text=[f"{v:.3f}" if v else "N/A" for v in valores_rat],
            textposition='outside',
            marker_color='lightblue'
        ))
        
        fig8.add_trace(go.Bar(
            name='Rotación Cuentas por Cobrar',
            x=años,
            y=valores_rcxc,
            text=[f"{v:.3f}" if v else "N/A" for v in valores_rcxc],
            textposition='outside',
            marker_color='lightyellow'
        ))
        
        fig8.add_trace(go.Bar(
            name='Rotación Inventarios',
            x=años,
            y=valores_ri,
            text=[f"{v:.3f}" if v else "N/A" for v in valores_ri],
            textposition='outside',
            marker_color='lightcoral'
        ))
        
        fig8.update_layout(
            title='Ratios de Actividad por Año',
            xaxis_title='Año',
            yaxis_title='Veces',
            barmode='group',
            hovermode='x unified',
            height=450,
            showlegend=True
        )
        
        figuras.append(fig8)
        
        # ===== GRÁFICO 9: ROTACIÓN DE ACTIVOS TOTALES - LÍNEA DE TENDENCIA =====
        fig9 = go.Figure()
        
        fig9.add_trace(go.Scatter(
            x=años,
            y=valores_rat,
            mode='lines+markers',
            name='Rotación de Activos Totales',
            line=dict(color='blue', width=3),
            marker=dict(size=8),
            text=[f"{v:.3f}" if v else "N/A" for v in valores_rat],
            hovertemplate='<b>Año:</b> %{x}<br><b>Rotación:</b> %{y:.3f} veces<extra></extra>'
        ))
        
        fig9.update_layout(
            title='Tendencia de Rotación de Activos Totales',
            xaxis_title='Año',
            yaxis_title='Veces',
            hovermode='x unified',
            height=400,
            showlegend=False
        )
        
        figuras.append(fig9)
        
        # ===== GRÁFICO 10: ROTACIÓN CXC VS INVENTARIOS - COMPARACIÓN =====
        fig10 = go.Figure()
        
        fig10.add_trace(go.Scatter(
            x=años,
            y=valores_rcxc,
            mode='lines+markers',
            name='Rotación Cuentas por Cobrar',
            line=dict(color='orange', width=3),
            marker=dict(size=8),
            text=[f"{v:.3f}" if v else "N/A" for v in valores_rcxc],
            hovertemplate='<b>Año:</b> %{x}<br><b>CxC:</b> %{y:.3f} veces<extra></extra>'
        ))
        
        fig10.add_trace(go.Scatter(
            x=años,
            y=valores_ri,
            mode='lines+markers',
            name='Rotación Inventarios',
            line=dict(color='purple', width=3),
            marker=dict(size=8),
            text=[f"{v:.3f}" if v else "N/A" for v in valores_ri],
            hovertemplate='<b>Año:</b> %{x}<br><b>Inventarios:</b> %{y:.3f} veces<extra></extra>'
        ))
        
        fig10.update_layout(
            title='Comparación: Rotación de Cuentas por Cobrar vs Inventarios',
            xaxis_title='Año',
            yaxis_title='Veces',
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        figuras.append(fig10)
        
        return figuras
    
    def exportar_ratios_excel(self, resultados: Dict[str, Any], archivo_salida: str):
        """
        Exporta ratios financieros a Excel
        
        Args:
            resultados: Dict con ratios calculados
            archivo_salida: Nombre del archivo Excel de salida
        """
        if not resultados.get('ratios_por_año'):
            print("⚠️ No hay ratios para exportar")
            return
        
        # Crear DataFrame
        años = sorted(resultados['años'])
        ratios_por_año = resultados['ratios_por_año']
        
        data = {
            'Año': años,
            'Liquidez Corriente': [ratios_por_año[año].get('liquidez_corriente') for año in años],
            'Prueba Ácida': [ratios_por_año[año].get('prueba_acida') for año in años],
            'Razón Deuda Total': [ratios_por_año[año].get('razon_deuda_total') for año in años],
            'Razón Deuda/Patrimonio': [ratios_por_año[año].get('razon_deuda_patrimonio') for año in años],
            'Margen Neto': [ratios_por_año[año].get('margen_neto') for año in años],
            'ROA': [ratios_por_año[año].get('roa') for año in años],
            'ROE': [ratios_por_año[año].get('roe') for año in años],
            'Rotación Activos Totales': [ratios_por_año[año].get('rotacion_activos_totales') for año in años],
            'Rotación CxC': [ratios_por_año[año].get('rotacion_cuentas_cobrar') for año in años],
            'Rotación Inventarios': [ratios_por_año[año].get('rotacion_inventarios') for año in años]
        }
        
        df = pd.DataFrame(data)
        
        # Exportar a Excel
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ratios Financieros', index=False)
            
            # Agregar hoja de resumen
            if resultados.get('resumen'):
                resumen_data = []
                for ratio_nombre, stats in resultados['resumen'].items():
                    resumen_data.append({
                        'Ratio': ratio_nombre.replace('_', ' ').title(),
                        'Mínimo': stats.get('min'),
                        'Máximo': stats.get('max'),
                        'Promedio': stats.get('promedio')
                    })
                
                df_resumen = pd.DataFrame(resumen_data)
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        
        print(f"✅ Ratios financieros exportados a: {archivo_salida}")


# Función de prueba
if __name__ == "__main__":
    print("="*70)
    print("CALCULADOR DE RATIOS FINANCIEROS - TEST")
    print("="*70)
    
    print("\n⚠️ Este módulo requiere datos del extractor de estados financieros")
    print("✅ Módulo creado exitosamente")
