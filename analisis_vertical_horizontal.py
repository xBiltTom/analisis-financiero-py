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
        Realiza análisis vertical del Estado de Situación Financiera/Balance General
        MEJORADO para manejar archivos de años ≤2009 y análisis de 4 bloques completos
        
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
        
        # Debug: Mostrar información de entrada
        print(f"DEBUG: Procesando {len(datos_estados)} archivos")
        print(f"DEBUG: Años solicitados: {años_disponibles}")
        
        # Procesar cada año disponible
        for año in años_disponibles:
            print(f"DEBUG: Procesando año {año}")
            
            # MÉTODO MEJORADO: Buscar datos que contengan este año
            datos_año = None
            
            for i, datos in enumerate(datos_estados):
                # Verificar metadatos
                metadatos = datos.get('datos', {}).get('metadatos', {})
                año_reporte = metadatos.get('año', '')
                años_disp = datos.get('datos', {}).get('años_disponibles', [])
                año_documento = datos.get('datos', {}).get('año_documento', None)
                
                print(f"DEBUG: Archivo {i} - año_reporte={año_reporte}, años_disp={años_disp}, año_doc={año_documento}")
                
                # Si este archivo contiene el año que buscamos
                if (año_reporte == año or año in años_disp or 
                    (año_documento and abs(int(año_documento) - int(año)) <= 1)):
                    datos_año = datos.get('datos', {})
                    print(f"DEBUG: Encontrado datos para año {año} en archivo {i}")
                    break
            
            if not datos_año:
                error_msg = f"No se encontraron datos para el año {año}"
                resultados['errores'].append(error_msg)
                print(f"DEBUG: {error_msg}")
                continue
            
            # Buscar Estado de Situación Financiera/Balance General
            estado_situacion = self._encontrar_estado_situacion_financiera(datos_año)
            if not estado_situacion:
                error_msg = f"No se encontró Estado de Situación Financiera/Balance General para {año}"
                resultados['errores'].append(error_msg)
                print(f"DEBUG: {error_msg}")
                continue
            
            print(f"DEBUG: Encontrado estado con {len(estado_situacion)} cuentas para {año}")
            
            # Realizar análisis vertical para este año
            analisis_año = self._calcular_analisis_vertical_año(estado_situacion, año)
            if analisis_año:
                resultados['analisis_por_año'][año] = analisis_año
                print(f"DEBUG: Análisis completado para {año}")
            else:
                error_msg = f"Error al calcular análisis vertical para {año}"
                resultados['errores'].append(error_msg)
                print(f"DEBUG: {error_msg}")
        
        # Generar resumen comparativo si hay múltiples años
        if len(resultados['analisis_por_año']) > 1:
            resultados['resumen'] = self._generar_resumen_comparativo(resultados['analisis_por_año'])
        
        return resultados
    
    def _encontrar_datos_por_año(self, datos_estados: List[Dict], año: str) -> Optional[Dict]:
        """Encuentra los datos correspondientes a un año específico - MEJORADO para 2009 hacia abajo"""
        for datos in datos_estados:
            # 1. Buscar en metadatos
            metadatos = datos.get('datos', {}).get('metadatos', {})
            año_reporte = metadatos.get('año', '')
            
            # 2. Buscar en años disponibles
            años_disponibles = datos.get('datos', {}).get('años_disponibles', [])
            
            # 3. Obtener año del documento
            año_documento = datos.get('datos', {}).get('año_documento', None)
            
            # 4. NUEVA LÓGICA: Para archivos de un solo año, buscar si contiene el año solicitado
            if año_reporte == año or año in años_disponibles:
                return datos.get('datos', {})
            
            # 5. CORRECCIÓN PRINCIPAL: Para archivos que contienen múltiples años
            # Si el archivo contiene el año solicitado en sus datos, lo devolvemos
            estados_financieros = datos.get('datos', {}).get('estados_financieros', {})
            
            # Buscar si algún estado financiero contiene datos para el año solicitado
            for clave_estado, info_estado in estados_financieros.items():
                datos_estado = info_estado.get('datos', [])
                for cuenta_data in datos_estado:
                    # Verificar si tiene una columna con el año solicitado
                    for clave, valor in cuenta_data.items():
                        if año in str(clave):  # El año está en el nombre de la columna
                            return datos.get('datos', {})
                        
                        # También verificar si el año está en el contenido del valor
                        if isinstance(valor, dict) and 'texto' in valor:
                            if año in str(valor['texto']):
                                return datos.get('datos', {})
            
            # 6. FALLBACK: Si el año del documento es cercano al año solicitado (±1 año)
            if año_documento and abs(int(año_documento) - int(año)) <= 1:
                return datos.get('datos', {})
        
        return None
    
    def _encontrar_estado_situacion_financiera(self, datos_año: Dict) -> Optional[List[Dict]]:
        """Encuentra el Estado/Balance General en los datos del año - MEJORADO para años ≤2009"""
        estados_financieros = datos_año.get('estados_financieros', {})
        año_documento = datos_año.get('año_documento', 2020)
        
        # Para años 2009 hacia abajo, buscar Balance General PRIMERO
        if año_documento <= 2009:
            claves_buscar = [
                'balance_general',
                'estado_situacion_financiera',
                'estado_situacion_patrimonial'
            ]
        else:
            # Para años 2010 hacia arriba, buscar Estado de Situación Financiera PRIMERO
            claves_buscar = [
                'estado_situacion_financiera',
                'balance_general',
                'estado_situacion_patrimonial'
            ]
        
        # Buscar por claves específicas
        for clave in claves_buscar:
            if clave in estados_financieros and estados_financieros[clave].get('datos'):
                return estados_financieros[clave]['datos']
        
        # FALLBACK: Si no encuentra por clave específica, buscar cualquier estado que contenga datos de activos/pasivos
        for clave, info_estado in estados_financieros.items():
            datos = info_estado.get('datos', [])
            if datos:
                # Verificar si contiene cuentas típicas de balance/situación financiera
                for cuenta_item in datos[:10]:  # Revisar solo los primeros 10 items
                    cuenta_nombre = cuenta_item.get('cuenta', '').lower()
                    if any(termino in cuenta_nombre for termino in [
                        'total activos', 'activos corrientes', 'total pasivos', 'patrimonio',
                        'balance general', 'situación financiera'
                    ]):
                        return datos
        
        return None
    
    def _calcular_analisis_vertical_año(self, estado_situacion: List[Dict], año: str) -> Dict[str, Any]:
        """
        Calcula el análisis vertical para un año específico - MEJORADO para 4 bloques completos
        
        Los 4 bloques son:
        1. ACTIVOS: (Cuenta / Total Activos) * 100
        2. PASIVOS: (Cuenta / Total Pasivos) * 100  
        3. PATRIMONIO: (Cuenta / Total Patrimonio) * 100
        4. TOTALES: Verificación de equilibrio contable
        
        Formula base: (Valor de Cuenta / Total del Bloque) * 100
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
            },
            'verificacion': {
                'total_activos_calculado': 0,
                'total_pasivos_patrimonio_calculado': 0,
                'equilibrio_contable': False,
                'diferencia': 0
            }
        }
        
        print(f"DEBUG: Calculando análisis vertical para año {año}")
        print(f"DEBUG: Total de cuentas a procesar: {len(estado_situacion)}")
        
        # Encontrar totales principales para el año específico
        total_activos = self._encontrar_total_activos_año(estado_situacion, año)
        total_pasivos = self._encontrar_total_pasivos_año(estado_situacion, año)
        total_patrimonio = self._encontrar_total_patrimonio_año(estado_situacion, año)
        
        print(f"DEBUG: Totales encontrados - Activos: {total_activos}, Pasivos: {total_pasivos}, Patrimonio: {total_patrimonio}")
        
        if total_activos is None or total_activos == 0:
            error_msg = "No se encontró Total de Activos válido"
            resultado['activos']['errores'].append(error_msg)
            print(f"DEBUG: {error_msg}")
            return resultado
        
        resultado['activos']['total_activos'] = total_activos
        resultado['pasivos']['total_pasivos'] = total_pasivos if total_pasivos else 0
        resultado['patrimonio']['total_patrimonio'] = total_patrimonio if total_patrimonio else 0
        
        # Contadores para verificación
        suma_activos = 0
        suma_pasivos = 0
        suma_patrimonio = 0
        cuentas_procesadas = 0
        
        # Clasificar y calcular porcentajes para cada cuenta
        for i, cuenta_data in enumerate(estado_situacion):
            cuenta_nombre = cuenta_data.get('cuenta', '').strip()
            if not cuenta_nombre:
                continue
            
            # Filtrar cuentas totales para evitar duplicación
            cuenta_lower = cuenta_nombre.lower()
            if any(total_word in cuenta_lower for total_word in [
                'total activos', 'total pasivos', 'total patrimonio', 
                'total pasivo y patrimonio', 'suma de activos', 'suma de pasivos'
            ]):
                print(f"DEBUG: Saltando cuenta total: {cuenta_nombre}")
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
                suma_patrimonio += valor_numerico
            
            # Contar cuentas procesadas
            if clasificacion in ['activo', 'pasivo', 'patrimonio']:
                cuentas_procesadas += 1
                if clasificacion == 'activo':
                    suma_activos += valor_numerico
                elif clasificacion == 'pasivo':
                    suma_pasivos += valor_numerico
        
        # BLOQUE 4: VERIFICACIÓN DE EQUILIBRIO CONTABLE
        resultado['verificacion']['total_activos_calculado'] = suma_activos
        resultado['verificacion']['total_pasivos_patrimonio_calculado'] = suma_pasivos + suma_patrimonio
        
        # Verificar equilibrio contable (Activos = Pasivos + Patrimonio)
        diferencia = abs(total_activos - (resultado['pasivos']['total_pasivos'] + resultado['patrimonio']['total_patrimonio']))
        resultado['verificacion']['diferencia'] = diferencia
        resultado['verificacion']['equilibrio_contable'] = diferencia < (total_activos * 0.01)  # Tolerancia del 1%
        
        print(f"DEBUG: Análisis completado - Cuentas procesadas: {cuentas_procesadas}")
        print(f"DEBUG: Activos: {len(resultado['activos']['cuentas'])}, Pasivos: {len(resultado['pasivos']['cuentas'])}, Patrimonio: {len(resultado['patrimonio']['cuentas'])}")
        print(f"DEBUG: Equilibrio contable: {resultado['verificacion']['equilibrio_contable']}, Diferencia: {diferencia}")
        
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
        """Clasifica una cuenta como activo, pasivo o patrimonio - MEJORADO para años ≤2009"""
        cuenta_lower = cuenta_nombre.lower().strip()
        
        # Filtrar cuentas totales que no deben clasificarse
        if any(total_word in cuenta_lower for total_word in [
            'total activos', 'total pasivos', 'total patrimonio', 'total pasivo y patrimonio',
            'suma de activos', 'suma de pasivos', 'suma de patrimonio'
        ]):
            return 'total'
        
        # PATRONES MEJORADOS PARA ACTIVOS (incluyendo terminología de años ≤2009)
        patrones_activos = [
            # Activos corrientes
            'activo', 'efectivo', 'caja', 'banco', 'valores negociables', 'valores realizables',
            'cuentas por cobrar', 'cuenta por cobrar', 'deudores', 'inventario', 'inventarios',
            'existencia', 'existencias', 'mercadería', 'mercaderías', 'productos terminados',
            'materias primas', 'productos en proceso', 'gastos pagados por anticipado',
            # Activos no corrientes
            'inmueble', 'maquinaria', 'equipo', 'propiedad', 'planta', 'edificio', 'edificios',
            'terreno', 'terrenos', 'vehículo', 'vehículos', 'muebles', 'enseres',
            'intangible', 'intangibles', 'inversión', 'inversiones', 'depreciación acumulada',
            'amortización acumulada', 'activos fijos', 'activo fijo', 'bienes de uso'
        ]
        
        # PATRONES MEJORADOS PARA PASIVOS (incluyendo terminología de años ≤2009)
        patrones_pasivos = [
            # Pasivos corrientes
            'pasivo', 'cuentas por pagar', 'cuenta por pagar', 'acreedores', 'proveedores',
            'préstamo', 'préstamos', 'deuda', 'deudas', 'obligación', 'obligaciones',
            'documentos por pagar', 'letras por pagar', 'pagarés', 'tributos por pagar',
            'impuestos por pagar', 'remuneraciones por pagar', 'provisión', 'provisiones',
            'ingreso diferido', 'ingresos diferidos', 'anticipo de clientes', 'anticipos recibidos',
            # Pasivos no corrientes
            'deuda a largo plazo', 'préstamos a largo plazo', 'hipoteca', 'hipotecas',
            'bonos por pagar', 'obligaciones a largo plazo'
        ]
        
        # PATRONES MEJORADOS PARA PATRIMONIO (incluyendo terminología de años ≤2009)
        patrones_patrimonio = [
            'patrimonio', 'patrimonio neto', 'capital', 'capital social', 'capital suscrito',
            'capital pagado', 'acciones comunes', 'acciones preferentes', 'acciones de inversión',
            'prima de emisión', 'reserva', 'reservas', 'reserva legal', 'reservas legales',
            'reservas estatutarias', 'reservas contractuales', 'reservas facultativas',
            'resultado', 'resultados', 'utilidad', 'utilidades', 'ganancia', 'ganancias',
            'pérdida', 'pérdidas', 'utilidades retenidas', 'resultados acumulados',
            'utilidades no distribuidas', 'superávit', 'excedente', 'revaluación',
            'superávit por revaluación', 'excedente de revaluación'
        ]
        
        # Clasificar por patrones
        if any(patron in cuenta_lower for patron in patrones_activos):
            return 'activo'
        elif any(patron in cuenta_lower for patron in patrones_pasivos):
            return 'pasivo'
        elif any(patron in cuenta_lower for patron in patrones_patrimonio):
            return 'patrimonio'
        
        # CLASIFICACIÓN POR CÓDIGOS CONTABLES (común en años ≤2009)
        # Activos: generalmente códigos 1X
        if cuenta_lower.startswith(('1', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19')):
            return 'activo'
        # Pasivos: generalmente códigos 2X
        elif cuenta_lower.startswith(('2', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29')):
            return 'pasivo'
        # Patrimonio: generalmente códigos 3X
        elif cuenta_lower.startswith(('3', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39')):
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