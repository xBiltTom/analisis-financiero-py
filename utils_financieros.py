"""
Utilidades adicionales para el analizador financiero
Funciones auxiliares para procesamiento y análisis de datos financieros
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Any
import numpy as np
from bs4 import BeautifulSoup

class UtilsFinancieros:
    
    @staticmethod
    def limpiar_texto_financiero(texto: str) -> str:
        """Limpia y normaliza texto de cuentas financieras"""
        # Convertir a minúsculas
        texto = texto.lower().strip()
        
        # Remover caracteres especiales excepto básicos
        texto = re.sub(r'[^\w\s\-\(\)\.]', ' ', texto)
        
        # Normalizar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        # Remover espacios al inicio y final
        texto = texto.strip()
        
        return texto
    
    @staticmethod
    def extraer_numeros_con_formato(texto: str) -> Dict[str, Any]:
        """Extrae números de texto con diferentes formatos"""
        resultado = {
            'valor_numerico': 0.0,
            'es_negativo': False,
            'formato_detectado': 'desconocido',
            'texto_original': texto
        }
        
        if not texto or texto.strip() == '':
            return resultado
        
        texto_limpio = texto.strip()
        
        # Detectar si es negativo
        if '(' in texto_limpio and ')' in texto_limpio:
            resultado['es_negativo'] = True
            texto_limpio = texto_limpio.replace('(', '').replace(')', '')
            resultado['formato_detectado'] = 'parentesis'
        elif texto_limpio.startswith('-'):
            resultado['es_negativo'] = True
            texto_limpio = texto_limpio[1:]
            resultado['formato_detectado'] = 'signo_menos'
        
        # Remover símbolos de moneda y otros caracteres
        texto_limpio = re.sub(r'[S/\$€£¥₹]', '', texto_limpio)
        
        # Manejar diferentes formatos de separadores
        # Formato: 1,234.56 (US)
        if re.match(r'^\d{1,3}(,\d{3})*\.?\d*$', texto_limpio):
            texto_limpio = texto_limpio.replace(',', '')
            resultado['formato_detectado'] = 'us_format'
        
        # Formato: 1.234,56 (European)
        elif re.match(r'^\d{1,3}(\.\d{3})*,?\d*$', texto_limpio):
            # Cambiar punto por separador temporal y coma por punto decimal
            texto_limpio = texto_limpio.replace('.', '|').replace(',', '.').replace('|', '')
            resultado['formato_detectado'] = 'eu_format'
        
        # Intentar convertir a float
        try:
            valor = float(texto_limpio)
            if resultado['es_negativo']:
                valor = -valor
            resultado['valor_numerico'] = valor
        except ValueError:
            # Si falla, intentar extraer solo dígitos
            digitos = re.findall(r'\d', texto_limpio)
            if digitos:
                try:
                    valor = float(''.join(digitos))
                    if resultado['es_negativo']:
                        valor = -valor
                    resultado['valor_numerico'] = valor
                    resultado['formato_detectado'] = 'solo_digitos'
                except ValueError:
                    pass
        
        return resultado
    
    @staticmethod
    def detectar_tipo_estado_financiero(texto: str, contexto: str = '') -> str:
        """Detecta el tipo de estado financiero basado en el contexto"""
        texto_completo = (texto + ' ' + contexto).lower()
        
        # Patrones para cada tipo de estado
        patrones = {
            'balance_general': [
                r'estado\s+de\s+situaci[óo]n\s+financiera',
                r'balance\s+general',
                r'activos?\s+(corrientes?|no\s+corrientes?)',
                r'pasivos?\s+(corrientes?|no\s+corrientes?)',
                r'patrimonio\s+neto'
            ],
            'estado_resultados': [
                r'estado\s+de\s+resultados',
                r'estado\s+de\s+ganancias\s+y\s+p[ée]rdidas',
                r'ingresos?\s+(operacionales?|de\s+actividades\s+ordinarias)',
                r'costo\s+de\s+ventas',
                r'utilidad\s+(bruta|operativa|neta)',
                r'resultado\s+del\s+ejercicio'
            ],
            'flujo_efectivo': [
                r'estado\s+de\s+flujos?\s+de\s+efectivo',
                r'flujo\s+de\s+efectivo\s+de\s+operaci[óo]n',
                r'actividades\s+de\s+operaci[óo]n',
                r'actividades\s+de\s+inversi[óo]n',
                r'actividades\s+de\s+financiamiento'
            ],
            'cambios_patrimonio': [
                r'estado\s+de\s+cambios\s+en\s+el\s+patrimonio',
                r'estado\s+de\s+variaciones\s+en\s+el\s+patrimonio',
                r'movimiento\s+del\s+patrimonio'
            ]
        }
        
        # Buscar coincidencias
        for tipo, lista_patrones in patrones.items():
            for patron in lista_patrones:
                if re.search(patron, texto_completo):
                    return tipo
        
        return 'no_identificado'
    
    @staticmethod
    def calcular_ratios_basicos(datos: Dict[str, Any]) -> Dict[str, float]:
        """Calcula ratios financieros básicos a partir de los datos extraídos"""
        ratios = {}
        
        try:
            # Buscar valores necesarios para ratios
            activo_corriente = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['activos corrientes', 'activo corriente', 'total activos corrientes']
            )
            
            pasivo_corriente = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['pasivos corrientes', 'pasivo corriente', 'total pasivos corrientes']
            )
            
            total_activos = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total activos', 'activos totales']
            )
            
            total_pasivos = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total pasivos', 'pasivos totales']
            )
            
            patrimonio = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['patrimonio', 'patrimonio neto', 'total patrimonio']
            )
            
            utilidad_neta = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['utilidad neta', 'ganancia neta', 'resultado del ejercicio']
            )
            
            ventas = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['ventas', 'ventas netas', 'ingresos operacionales']
            )
            
            # Calcular ratios
            if activo_corriente and pasivo_corriente and pasivo_corriente != 0:
                ratios['liquidez_corriente'] = activo_corriente / pasivo_corriente
            
            if total_pasivos and total_activos and total_activos != 0:
                ratios['endeudamiento'] = total_pasivos / total_activos
            
            if patrimonio and total_activos and total_activos != 0:
                ratios['autonomia'] = patrimonio / total_activos
            
            if utilidad_neta and total_activos and total_activos != 0:
                ratios['roa'] = utilidad_neta / total_activos
            
            if utilidad_neta and patrimonio and patrimonio != 0:
                ratios['roe'] = utilidad_neta / patrimonio
            
            if utilidad_neta and ventas and ventas != 0:
                ratios['margen_neto'] = utilidad_neta / ventas
        
        except Exception as e:
            print(f"Error calculando ratios: {e}")
        
        return ratios
    
    @staticmethod
    def _buscar_valor_cuenta(datos: Dict[str, Any], nombres_cuenta: List[str]) -> float:
        """Busca el valor de una cuenta específica en los datos"""
        for categoria in ['activos', 'pasivos', 'patrimonio', 'estado_resultados']:
            if categoria in datos:
                for item in datos[categoria]:
                    cuenta_texto = item.get('cuenta', '').lower()
                    
                    for nombre in nombres_cuenta:
                        if nombre.lower() in cuenta_texto:
                            valores = item.get('valores', [])
                            if valores and len(valores) > 0:
                                # Tomar el primer valor numérico encontrado
                                return valores[0].get('numero', 0.0)
        return 0.0
    
    @staticmethod
    def validar_consistencia_datos(datos: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la consistencia de los datos extraídos"""
        validacion = {
            'es_consistente': True,
            'errores': [],
            'advertencias': [],
            'metricas': {}
        }
        
        try:
            # Verificar ecuación contable básica: Activos = Pasivos + Patrimonio
            total_activos = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total activos']
            )
            
            total_pasivos = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total pasivos']
            )
            
            total_patrimonio = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total patrimonio', 'patrimonio neto']
            )
            
            if total_activos and total_pasivos and total_patrimonio:
                diferencia = abs(total_activos - (total_pasivos + total_patrimonio))
                tolerancia = total_activos * 0.01  # 1% de tolerancia
                
                validacion['metricas']['total_activos'] = total_activos
                validacion['metricas']['total_pasivos'] = total_pasivos
                validacion['metricas']['total_patrimonio'] = total_patrimonio
                validacion['metricas']['diferencia_ecuacion'] = diferencia
                
                if diferencia > tolerancia:
                    validacion['es_consistente'] = False
                    validacion['errores'].append(
                        f"Ecuación contable no balanceada. Diferencia: {diferencia:,.2f}"
                    )
            
            # Verificar que hay datos en categorías principales
            categorias_esperadas = ['activos', 'pasivos', 'patrimonio']
            for categoria in categorias_esperadas:
                if categoria not in datos or not datos[categoria]:
                    validacion['advertencias'].append(
                        f"No se encontraron datos para {categoria}"
                    )
            
            # Verificar años
            años = datos.get('años_disponibles', [])
            if len(años) == 0:
                validacion['advertencias'].append("No se detectaron años en los datos")
            
        except Exception as e:
            validacion['errores'].append(f"Error en validación: {str(e)}")
            validacion['es_consistente'] = False
        
        return validacion
    
    @staticmethod
    def generar_tabla_comparativa(resultados_multiples: List[Dict]) -> pd.DataFrame:
        """Genera una tabla comparativa de múltiples períodos"""
        datos_comparativos = []
        
        for resultado in resultados_multiples:
            resumen = resultado.get('resumen', {})
            datos = resultado.get('datos', {})
            
            fila = {
                'Archivo': resultado.get('archivo', ''),
                'Empresa': resumen.get('empresa', ''),
                'Año': resumen.get('año_reporte', ''),
                'Tipo': resumen.get('tipo_reporte', '')
            }
            
            # Extraer métricas principales
            fila['Total_Activos'] = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total activos']
            )
            
            fila['Total_Pasivos'] = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total pasivos']
            )
            
            fila['Total_Patrimonio'] = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['total patrimonio', 'patrimonio neto']
            )
            
            fila['Utilidad_Neta'] = UtilsFinancieros._buscar_valor_cuenta(
                datos, ['utilidad neta', 'ganancia neta', 'resultado del ejercicio']
            )
            
            # Calcular ratios
            ratios = UtilsFinancieros.calcular_ratios_basicos(datos)
            fila.update(ratios)
            
            datos_comparativos.append(fila)
        
        return pd.DataFrame(datos_comparativos)
    
    @staticmethod
    def exportar_datos_detallados(datos_extraidos: Dict[str, Any], archivo_salida: str):
        """Exporta datos detallados a un archivo Excel con múltiples hojas"""
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            
            # Hoja de metadatos
            metadatos = datos_extraidos.get('metadatos', {})
            df_metadatos = pd.DataFrame([metadatos])
            df_metadatos.to_excel(writer, sheet_name='Metadatos', index=False)
            
            # Hojas por categoría
            categorias = ['activos', 'pasivos', 'patrimonio', 'estado_resultados', 'flujo_efectivo']
            
            for categoria in categorias:
                if categoria in datos_extraidos and datos_extraidos[categoria]:
                    datos_categoria = []
                    
                    for item in datos_extraidos[categoria]:
                        fila_base = {'Cuenta': item['cuenta']}
                        
                        for i, valor in enumerate(item['valores']):
                            fila_base[f'Valor_{i+1}'] = valor['numero']
                            fila_base[f'Texto_{i+1}'] = valor['texto']
                        
                        datos_categoria.append(fila_base)
                    
                    df_categoria = pd.DataFrame(datos_categoria)
                    nombre_hoja = categoria.replace('_', ' ').title()[:31]  # Límite Excel
                    df_categoria.to_excel(writer, sheet_name=nombre_hoja, index=False)
            
            # Hoja de validación
            validacion = UtilsFinancieros.validar_consistencia_datos(datos_extraidos)
            df_validacion = pd.DataFrame([validacion['metricas']])
            df_validacion.to_excel(writer, sheet_name='Validacion', index=False)

def ejemplo_uso():
    """Ejemplo de uso de las utilidades"""
    utils = UtilsFinancieros()
    
    # Ejemplo de limpieza de texto
    texto_sucio = "  Cuentas por Cobrar - Comerciales  (Neto) "
    texto_limpio = utils.limpiar_texto_financiero(texto_sucio)
    print(f"Texto limpio: {texto_limpio}")
    
    # Ejemplo de extracción de números
    valores_prueba = ["1,234.56", "(500.00)", "$ 1.500,50", "0", "N/A"]
    
    for valor in valores_prueba:
        resultado = utils.extraer_numeros_con_formato(valor)
        print(f"'{valor}' -> {resultado['valor_numerico']} ({resultado['formato_detectado']})")

if __name__ == "__main__":
    ejemplo_uso()