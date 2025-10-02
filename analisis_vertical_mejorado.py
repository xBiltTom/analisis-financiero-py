"""
Análisis Vertical Mejorado para Estados Financieros
====================================================
Calcula análisis vertical automático según formato del año (≤2009 vs ≥2010)

Estados analizados:
- ≤2009: BALANCE GENERAL, ESTADO DE GANANCIAS Y PERDIDAS, ESTADO DE FLUJO DE EFECTIVO
- ≥2010: ESTADO DE SITUACION FINANCIERA, ESTADO DE RESULTADOS, ESTADO DE FLUJO DE EFECTIVO

Reglas de cálculo:
1. ACTIVOS: (Cuenta / TOTAL ACTIVOS) * 100 - desde inicio hasta celda "TOTAL ACTIVOS"
2. PASIVOS: (Cuenta / Total Pasivos) * 100 - desde inicio pasivos hasta celda "Total Pasivos"
3. PATRIMONIO: NO SE CALCULA (se ignora todo después de "Total Pasivos")
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any


class AnalisisVerticalMejorado:
    """Clase para realizar análisis vertical automático de estados financieros"""
    
    # Mapeo de estados según el año
    ESTADOS_PRE_2010 = {
        'balance': 'BALANCE GENERAL',
        'resultados': 'ESTADO DE GANANCIAS Y PERDIDAS',
        'flujo': 'ESTADO DE FLUJO DE EFECTIVO'
    }
    
    ESTADOS_POST_2010 = {
        'balance': 'ESTADO DE SITUACION FINANCIERA',
        'resultados': 'ESTADO DE RESULTADOS',
        'flujo': 'ESTADO DE FLUJO DE EFECTIVO'
    }
    
    def __init__(self):
        self.resultados = {}
    
    def analizar_desde_extractor(self, resultados_extractor: Dict) -> Dict[str, Any]:
        """
        Realiza análisis vertical desde los resultados del extractor mejorado
        
        Args:
            resultados_extractor: Dict con resultados de extractor_estados_mejorado.py
        
        Returns:
            Dict con análisis vertical de los 3 estados principales
        """
        año_documento = resultados_extractor['año_documento']
        formato = resultados_extractor['formato']
        estados = resultados_extractor['estados']
        metadatos = resultados_extractor.get('metadatos', {})
        
        print(f"\n{'='*60}")
        print(f"📊 ANÁLISIS VERTICAL - {metadatos.get('empresa', 'N/A')}")
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
        
        # Analizar Balance General / Estado de Situación Financiera
        if 'balance' in estados:
            print(f"📋 Analizando Balance/Situación Financiera...")
            balance_analisis = self._analizar_balance(estados['balance'])
            resultados_analisis['estados_analizados']['balance'] = balance_analisis
            print(f"   ✅ Activos: {balance_analisis['total_cuentas_activos']} cuentas analizadas")
            print(f"   ✅ Pasivos: {balance_analisis['total_cuentas_pasivos']} cuentas analizadas")
            print(f"   ⚠️  Patrimonio: Ignorado (según especificación)\n")
        
        # Analizar Estado de Resultados / Ganancias y Pérdidas
        if 'resultados' in estados:
            print(f"📋 Analizando Estado de Resultados...")
            resultados_estado = self._analizar_resultados(estados['resultados'])
            resultados_analisis['estados_analizados']['resultados'] = resultados_estado
            print(f"   ✅ {resultados_estado['total_cuentas_analizadas']} cuentas analizadas\n")
        
        # Analizar Flujo de Efectivo
        if 'flujo' in estados:
            print(f"📋 Analizando Flujo de Efectivo...")
            flujo_analisis = self._analizar_flujo(estados['flujo'])
            resultados_analisis['estados_analizados']['flujo'] = flujo_analisis
            print(f"   ✅ {flujo_analisis['total_cuentas_analizadas']} cuentas analizadas\n")
        
        # Generar resumen
        resultados_analisis['resumen'] = self._generar_resumen(resultados_analisis)
        
        print(f"{'='*60}")
        print(f"✅ Análisis vertical completado")
        print(f"{'='*60}\n")
        
        return resultados_analisis
    
    def _analizar_balance(self, balance: Dict) -> Dict[str, Any]:
        """
        Analiza Balance General / Estado de Situación Financiera
        
        Reglas:
        - ACTIVOS: (Cuenta / TOTAL ACTIVOS) * 100 hasta encontrar "TOTAL ACTIVOS"
        - PASIVOS: (Cuenta / Total Pasivos) * 100 hasta encontrar "Total Pasivos"
        - PATRIMONIO: NO SE CALCULA
        """
        años = balance['años']
        año_analisis = años[0]  # Año más reciente
        cuentas = balance['cuentas']
        
        resultado = {
            'nombre_estado': balance['nombre'],
            'año_analisis': año_analisis,
            'activos': [],
            'pasivos': [],
            'total_activos': 0,
            'total_pasivos': 0,
            'total_cuentas_activos': 0,
            'total_cuentas_pasivos': 0
        }
        
        # Detectar si es formato pre-2010 o post-2010
        es_pre_2010 = 'BALANCE GENERAL' in balance['nombre'].upper()
        
        # Buscar totales primero con patrones específicos por formato
        if es_pre_2010:
            # Para años ≤2009: buscar "TOTAL ACTIVO" (singular)
            total_activos = self._buscar_total(cuentas, año_analisis, 
                ['TOTAL ACTIVO'])
            total_pasivos = self._buscar_total(cuentas, año_analisis,
                ['TOTAL PASIVO'])
        else:
            # Para años ≥2010: buscar "TOTAL ACTIVOS" (plural) o variaciones
            total_activos = self._buscar_total(cuentas, año_analisis, 
                ['TOTAL ACTIVOS', 'TOTAL DE ACTIVOS', 'Total Activos', 'ACTIVOS TOTALES'])
            total_pasivos = self._buscar_total(cuentas, año_analisis,
                ['TOTAL PASIVOS', 'TOTAL DE PASIVOS', 'Total Pasivos', 'PASIVOS TOTALES'])
        
        if not total_activos or total_activos == 0:
            print(f"   ⚠️ No se encontró TOTAL ACTIVO{'S' if not es_pre_2010 else ''} válido")
            return resultado
        
        if not total_pasivos or total_pasivos == 0:
            print(f"   ⚠️ No se encontró Total Pasivo{'s' if not es_pre_2010 else ''} válido")
        
        resultado['total_activos'] = total_activos
        resultado['total_pasivos'] = total_pasivos
        
        # Fase 1: Procesar ACTIVOS (hasta encontrar TOTAL ACTIVOS)
        fase = 'activos'
        for cuenta in cuentas:
            nombre = cuenta['nombre'].strip()
            nombre_upper = nombre.upper()
            
            # Verificar si llegamos al final de ACTIVOS
            if self._es_total_activos(nombre_upper, es_pre_2010):
                # Agregar el total con análisis vertical
                valor = cuenta['valores'].get(año_analisis, 0)
                porcentaje = 100.0  # El total siempre es 100%
                resultado['activos'].append({
                    'cuenta': nombre,
                    'valor': valor,
                    'analisis_vertical': porcentaje,
                    'es_total': True
                })
                resultado['total_cuentas_activos'] += 1
                # Cambiar a fase PASIVOS
                fase = 'pasivos'
                continue
            
            # Verificar si llegamos al final de PASIVOS (ignorar PATRIMONIO)
            if fase == 'pasivos' and self._es_total_pasivos(nombre_upper, es_pre_2010):
                # Agregar el total de pasivos
                valor = cuenta['valores'].get(año_analisis, 0)
                porcentaje = 100.0
                resultado['pasivos'].append({
                    'cuenta': nombre,
                    'valor': valor,
                    'analisis_vertical': porcentaje,
                    'es_total': True
                })
                resultado['total_cuentas_pasivos'] += 1
                # Terminar procesamiento (ignorar PATRIMONIO)
                print(f"   🛑 Deteniendo en '{nombre}' - Patrimonio ignorado")
                break
            
            # Procesar cuenta según la fase
            valor = cuenta['valores'].get(año_analisis, 0)
            
            if fase == 'activos' and total_activos > 0:
                porcentaje = (valor / total_activos) * 100
                resultado['activos'].append({
                    'cuenta': nombre,
                    'valor': valor,
                    'analisis_vertical': porcentaje,
                    'es_total': cuenta.get('es_total', False)
                })
                resultado['total_cuentas_activos'] += 1
            
            elif fase == 'pasivos' and total_pasivos > 0:
                porcentaje = (valor / total_pasivos) * 100
                resultado['pasivos'].append({
                    'cuenta': nombre,
                    'valor': valor,
                    'analisis_vertical': porcentaje,
                    'es_total': cuenta.get('es_total', False)
                })
                resultado['total_cuentas_pasivos'] += 1
        
        return resultado
    
    def _analizar_resultados(self, resultados: Dict) -> Dict[str, Any]:
        """
        Analiza Estado de Resultados / Ganancias y Pérdidas
        
        Calcula: (Cuenta / Ventas o Ingresos Totales) * 100
        """
        años = resultados['años']
        año_analisis = años[0]
        cuentas = resultados['cuentas']
        
        resultado = {
            'nombre_estado': resultados['nombre'],
            'año_analisis': año_analisis,
            'cuentas_analizadas': [],
            'total_ingresos': 0,
            'total_cuentas_analizadas': 0
        }
        
        # Buscar total de ventas/ingresos (primera cuenta principal)
        total_ingresos = self._buscar_total_ingresos(cuentas, año_analisis)
        
        if not total_ingresos or total_ingresos == 0:
            print(f"   ⚠️ No se encontró Total de Ingresos/Ventas válido")
            return resultado
        
        resultado['total_ingresos'] = total_ingresos
        
        # Calcular análisis vertical para cada cuenta
        for cuenta in cuentas:
            nombre = cuenta['nombre'].strip()
            valor = cuenta['valores'].get(año_analisis, 0)
            
            porcentaje = (valor / total_ingresos) * 100
            
            resultado['cuentas_analizadas'].append({
                'cuenta': nombre,
                'valor': valor,
                'analisis_vertical': porcentaje,
                'es_total': cuenta.get('es_total', False)
            })
            resultado['total_cuentas_analizadas'] += 1
        
        return resultado
    
    def _analizar_flujo(self, flujo: Dict) -> Dict[str, Any]:
        """
        Analiza Estado de Flujo de Efectivo
        
        Reglas ≥2010:
        - Cada sección (Operación, Inversión, Financiación) tiene su propia base (100%)
        - Las cuentas se dividen por la base de su sección correspondiente
        - Las bases son las celdas que contienen "Flujos de Efectivo procedente de Actividades de..."
        - IMPORTANTE: Las cuentas HACIA ARRIBA de cada base se calculan con esa base
        
        Reglas ≤2009:
        - Similar pero con nombres diferentes de secciones
        """
        años = flujo['años']
        año_analisis = años[0]
        cuentas = flujo['cuentas']
        
        resultado = {
            'nombre_estado': flujo['nombre'],
            'año_analisis': año_analisis,
            'cuentas_analizadas': [],
            'total_cuentas_analizadas': 0,
            'bases_detectadas': {}
        }
        
        # PASO 1: Identificar las bases y sus posiciones
        bases_posiciones = []
        for i, cuenta in enumerate(cuentas):
            nombre_upper = cuenta['nombre'].upper().strip()
            if self._es_base_flujo(nombre_upper):
                valor = cuenta['valores'].get(año_analisis, 0)
                bases_posiciones.append({
                    'indice': i,
                    'valor': valor if valor != 0 else 1,
                    'nombre': cuenta['nombre']
                })
        
        resultado['bases_detectadas'] = {f"base_{i+1}": b['nombre'] for i, b in enumerate(bases_posiciones)}
        
        # PASO 2: Procesar todas las cuentas asignando a cada una su base correspondiente
        for i, cuenta in enumerate(cuentas):
            nombre = cuenta['nombre'].strip()
            nombre_upper = nombre.upper()
            valor = cuenta['valores'].get(año_analisis, 0)
            
            # Verificar si esta cuenta es una base
            if self._es_base_flujo(nombre_upper):
                # Esta cuenta se marca como 100% de su sección
                porcentaje = 100.0
                
                resultado['cuentas_analizadas'].append({
                    'cuenta': nombre,
                    'valor': valor,
                    'analisis_vertical': porcentaje,
                    'es_total': True,
                    'es_base': True
                })
                resultado['total_cuentas_analizadas'] += 1
            else:
                # Encontrar la base más cercana HACIA ABAJO (siguiente base)
                base_correspondiente = None
                for base_info in bases_posiciones:
                    if i < base_info['indice']:
                        # Esta base está después de la cuenta actual
                        base_correspondiente = base_info['valor']
                        break
                
                # Si no hay base hacia abajo, usar la última base disponible
                if base_correspondiente is None and bases_posiciones:
                    base_correspondiente = bases_posiciones[-1]['valor']
                
                # Calcular porcentaje
                if base_correspondiente and base_correspondiente != 0:
                    porcentaje = (valor / base_correspondiente) * 100
                else:
                    porcentaje = 0.0
                
                resultado['cuentas_analizadas'].append({
                    'cuenta': nombre,
                    'valor': valor,
                    'analisis_vertical': porcentaje,
                    'es_total': cuenta.get('es_total', False),
                    'es_base': False
                })
                resultado['total_cuentas_analizadas'] += 1
        
        return resultado
    
    def _buscar_total(self, cuentas: List[Dict], año: int, patrones: List[str]) -> float:
        """Busca un valor total usando una lista de patrones"""
        for cuenta in cuentas:
            nombre_upper = cuenta['nombre'].upper().strip()
            for patron in patrones:
                if patron.upper() in nombre_upper and len(nombre_upper) <= len(patron) + 10:
                    return cuenta['valores'].get(año, 0)
        return 0
    
    def _buscar_total_ingresos(self, cuentas: List[Dict], año: int) -> float:
        """Busca el total de ingresos/ventas"""
        patrones = [
            'VENTAS NETAS',
            'INGRESOS DE ACTIVIDADES ORDINARIAS',
            'INGRESOS OPERACIONALES',
            'VENTAS',
            'INGRESOS'
        ]
        
        # Buscar la primera cuenta con estos patrones (suele ser la primera línea)
        for cuenta in cuentas[:5]:  # Revisar las primeras 5 cuentas
            nombre_upper = cuenta['nombre'].upper().strip()
            for patron in patrones:
                if patron in nombre_upper:
                    valor = cuenta['valores'].get(año, 0)
                    if valor > 0:  # Asegurar que sea positivo
                        return valor
        
        return 0
    
    def _buscar_flujo_neto(self, cuentas: List[Dict], año: int) -> float:
        """Busca el flujo neto de efectivo"""
        patrones = [
            'AUMENTO NETO DE EFECTIVO',
            'DISMINUCION NETA DE EFECTIVO',
            'EFECTIVO NETO',
            'FLUJO NETO'
        ]
        
        return self._buscar_total(cuentas, año, patrones)
    
    def _identificar_bases_flujo(self, cuentas: List[Dict], año: int) -> Dict[str, float]:
        """
        Identifica las bases (100%) de cada sección del flujo de efectivo
        
        Args:
            cuentas: Lista de cuentas del estado de flujo
            año: Año a analizar
        
        Returns:
            Dict con las bases encontradas por sección
        """
        bases = {}
        
        for cuenta in cuentas:
            nombre_upper = cuenta['nombre'].upper().strip()
            
            # Detectar base de Actividades de Operación
            if 'ACTIVIDADES DE OPERACION' in nombre_upper or 'ACTIVIDADES DE OPERACIÓN' in nombre_upper:
                if 'FLUJOS DE EFECTIVO' in nombre_upper and 'PROCEDENTE' in nombre_upper:
                    bases['operacion'] = cuenta['valores'].get(año, 0)
            
            # Detectar base de Actividades de Inversión
            elif 'ACTIVIDADES DE INVERSION' in nombre_upper or 'ACTIVIDADES DE INVERSIÓN' in nombre_upper:
                if 'FLUJOS DE EFECTIVO' in nombre_upper and 'PROCEDENTE' in nombre_upper:
                    bases['inversion'] = cuenta['valores'].get(año, 0)
            
            # Detectar base de Actividades de Financiación/Financiamiento
            elif 'ACTIVIDADES DE FINANCIACION' in nombre_upper or 'ACTIVIDADES DE FINANCIAMIENTO' in nombre_upper:
                if 'FLUJOS DE EFECTIVO' in nombre_upper and 'PROCEDENTE' in nombre_upper:
                    bases['financiacion'] = cuenta['valores'].get(año, 0)
        
        return bases
    
    def _es_base_flujo(self, nombre_upper: str) -> bool:
        """
        Verifica si una cuenta es una base (total de sección) en el flujo de efectivo
        
        Args:
            nombre_upper: Nombre de la cuenta en mayúsculas
        
        Returns:
            True si es una base de sección
        """
        # Patrones que indican que es una base (total de sección)
        # Formato POST-2010 (≥2010)
        patrones_base_post_2010 = [
            r'FLUJOS DE EFECTIVO.*PROCEDENTE.*ACTIVIDADES DE OPERACI[OÓ]N',
            r'FLUJOS DE EFECTIVO.*PROCEDENTE.*ACTIVIDADES DE INVERSI[OÓ]N',
            r'FLUJOS DE EFECTIVO.*PROCEDENTE.*ACTIVIDADES DE FINANCIACI[OÓ]N',
            r'FLUJOS DE EFECTIVO.*PROCEDENTE.*ACTIVIDADES DE FINANCIAMIENTO',
            r'FLUJOS DE EFECTIVO.*UTILIZAD[OA]S EN.*ACTIVIDADES DE OPERACI[OÓ]N',
            r'FLUJOS DE EFECTIVO.*UTILIZAD[OA]S EN.*ACTIVIDADES DE INVERSI[OÓ]N',
            r'FLUJOS DE EFECTIVO.*UTILIZAD[OA]S EN.*ACTIVIDADES DE FINANCIACI[OÓ]N',
            r'FLUJOS DE EFECTIVO.*UTILIZAD[OA]S EN.*ACTIVIDADES DE FINANCIAMIENTO'
        ]
        
        # Formato PRE-2010 (≤2009)
        patrones_base_pre_2010 = [
            r'AUMENTO.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE OPERACI[OÓ]N',
            r'AUMENTO.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE INVERSI[OÓ]N',
            r'AUMENTO.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE FINANCIACI[OÓ]N',
            r'AUMENTO.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE FINANCIAMIENTO',
            r'DISMINUCI[OÓ]N.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE OPERACI[OÓ]N',
            r'DISMINUCI[OÓ]N.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE INVERSI[OÓ]N',
            r'DISMINUCI[OÓ]N.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE FINANCIACI[OÓ]N',
            r'DISMINUCI[OÓ]N.*EFECTIVO.*PROVENIENTES DE ACTIVIDADES DE FINANCIAMIENTO'
        ]
        
        # Combinar todos los patrones
        todos_patrones = patrones_base_post_2010 + patrones_base_pre_2010
        
        for patron in todos_patrones:
            if re.search(patron, nombre_upper):
                return True
        
        return False
    
    def _es_total_activos(self, nombre: str, es_pre_2010: bool = False) -> bool:
        """
        Verifica si la cuenta es TOTAL ACTIVOS
        
        Args:
            nombre: Nombre de la cuenta en mayúsculas
            es_pre_2010: True si es formato ≤2009, False si es ≥2010
        """
        if es_pre_2010:
            # Para años ≤2009: "TOTAL ACTIVO" (singular)
            patrones = [
                r'^TOTAL\s+ACTIVO\s*$',
                r'^TOTAL\s+DEL\s+ACTIVO\s*$',
            ]
        else:
            # Para años ≥2010: "TOTAL ACTIVOS" (plural)
            patrones = [
                r'^TOTAL\s+ACTIVOS\s*$',
                r'^TOTAL\s+DE\s+ACTIVOS\s*$',
                r'^ACTIVOS\s+TOTALES\s*$',
                r'^TOTAL\s+DE\s+LOS\s+ACTIVOS\s*$'
            ]
        
        for patron in patrones:
            if re.match(patron, nombre):
                return True
        return False
    
    def _es_total_pasivos(self, nombre: str, es_pre_2010: bool = False) -> bool:
        """
        Verifica si la cuenta es Total Pasivos
        
        Args:
            nombre: Nombre de la cuenta en mayúsculas
            es_pre_2010: True si es formato ≤2009, False si es ≥2010
        """
        if es_pre_2010:
            # Para años ≤2009: "TOTAL PASIVO" (singular)
            # IMPORTANTE: NO incluir "PASIVO Y PATRIMONIO" aquí porque es el título de sección
            patrones = [
                r'^TOTAL\s+PASIVO\s*$',
                r'^TOTAL\s+DEL\s+PASIVO\s*$',
            ]
        else:
            # Para años ≥2010: "TOTAL PASIVOS" (plural)
            patrones = [
                r'^TOTAL\s+PASIVOS\s*$',
                r'^TOTAL\s+DE\s+PASIVOS\s*$',
                r'^PASIVOS\s+TOTALES\s*$',
                r'^TOTAL\s+DE\s+LOS\s+PASIVOS\s*$'
            ]
        
        for patron in patrones:
            if re.match(patron, nombre):
                return True
        return False
    
    def _generar_resumen(self, resultados: Dict) -> Dict[str, Any]:
        """Genera un resumen del análisis vertical"""
        resumen = {
            'total_estados_analizados': len(resultados['estados_analizados']),
            'estados': []
        }
        
        for clave, estado in resultados['estados_analizados'].items():
            resumen['estados'].append({
                'tipo': clave,
                'nombre': estado.get('nombre_estado', ''),
                'año': estado.get('año_analisis', 0)
            })
        
        return resumen
    
    def exportar_a_excel(self, resultados: Dict, archivo_salida: str):
        """
        Exporta los resultados del análisis vertical a Excel con formato
        """
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            
            # Hoja 1: Metadatos
            df_meta = pd.DataFrame([{
                'Empresa': resultados['empresa'],
                'Año': resultados['año_documento'],
                'Tipo': resultados['tipo'],
                'Formato': resultados['formato'].upper()
            }])
            df_meta.to_excel(writer, sheet_name='Información', index=False)
            
            # Hoja 2: Balance - Activos
            if 'balance' in resultados['estados_analizados']:
                balance = resultados['estados_analizados']['balance']
                
                if balance['activos']:
                    df_activos = pd.DataFrame(balance['activos'])
                    df_activos['analisis_vertical'] = df_activos['analisis_vertical'].round(2)
                    df_activos.to_excel(writer, sheet_name='Activos', index=False)
                
                # Hoja 3: Balance - Pasivos
                if balance['pasivos']:
                    df_pasivos = pd.DataFrame(balance['pasivos'])
                    df_pasivos['analisis_vertical'] = df_pasivos['analisis_vertical'].round(2)
                    df_pasivos.to_excel(writer, sheet_name='Pasivos', index=False)
            
            # Hoja 4: Estado de Resultados
            if 'resultados' in resultados['estados_analizados']:
                resultados_estado = resultados['estados_analizados']['resultados']
                if resultados_estado['cuentas_analizadas']:
                    df_resultados = pd.DataFrame(resultados_estado['cuentas_analizadas'])
                    df_resultados['analisis_vertical'] = df_resultados['analisis_vertical'].round(2)
                    df_resultados.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Hoja 5: Flujo de Efectivo
            if 'flujo' in resultados['estados_analizados']:
                flujo = resultados['estados_analizados']['flujo']
                if flujo['cuentas_analizadas']:
                    df_flujo = pd.DataFrame(flujo['cuentas_analizadas'])
                    df_flujo['analisis_vertical'] = df_flujo['analisis_vertical'].round(2)
                    df_flujo.to_excel(writer, sheet_name='Flujo Efectivo', index=False)
        
        print(f"✅ Análisis exportado a: {archivo_salida}")


# Función de uso rápido
def analizar_archivo_html(ruta_archivo: str, exportar: bool = True) -> Dict:
    """
    Analiza un archivo HTML y genera análisis vertical
    
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
    
    # Realizar análisis vertical
    analizador = AnalisisVerticalMejorado()
    resultados_analisis = analizador.analizar_desde_extractor(resultados_extractor)
    
    # Exportar a Excel si se solicita
    if exportar:
        import os
        nombre_base = os.path.basename(ruta_archivo).split('.')[0]
        archivo_salida = f"analisis_vertical_{nombre_base}.xlsx"
        analizador.exportar_a_excel(resultados_analisis, archivo_salida)
    
    return resultados_analisis


if __name__ == "__main__":
    print("="*70)
    print("📊 ANÁLISIS VERTICAL MEJORADO - DEMOSTRACIÓN")
    print("="*70)
    
    # Ejemplo 1: Archivo 2004 (Pre-2010)
    print("\n🔹 Ejemplo 1: Archivo 2004 (Formato Pre-2010)")
    print("-"*70)
    analisis_2004 = analizar_archivo_html(
        "ejemplos/ReporteDetalleInformacionFinanciero (6).html"
    )
    
    print("\n" + "="*70)
    
    # Ejemplo 2: Archivo 2024 (Post-2010)
    print("\n🔹 Ejemplo 2: Archivo 2024 (Formato Post-2010)")
    print("-"*70)
    analisis_2024 = analizar_archivo_html(
        "ejemplos/REPORTE DETALLE FINANCIERO 2024.html"
    )
    
    print("\n" + "="*70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("="*70)
