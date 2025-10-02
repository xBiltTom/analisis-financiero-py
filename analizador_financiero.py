import streamlit as st
import pandas as pd
import os
import tempfile
import shutil
from pathlib import Path
import re
from bs4 import BeautifulSoup
import numpy as np
import chardet
from typing import Dict, List, Tuple, Any
from analisis_vertical_horizontal import AnalisisVerticalHorizontal
from extractor_estados_mejorado import ExtractorEstadosFinancieros
from analisis_vertical_mejorado import AnalisisVerticalMejorado

# Configuración de la página
st.set_page_config(
    page_title="Analizador Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AnalizadorFinanciero:
    def __init__(self):
        self.temp_dir = "temp"
        self.crear_directorio_temporal()
        self.palabras_clave = self.cargar_diccionario_palabras_clave()
        self.extractor_mejorado = ExtractorEstadosFinancieros()  # ✨ Nuevo extractor mejorado
        self.analizador_vertical = AnalisisVerticalMejorado()  # ✨ Nuevo analizador vertical
        
    def crear_directorio_temporal(self):
        """Crear directorio temporal para almacenar archivos"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def cargar_diccionario_palabras_clave(self) -> Dict[str, List[str]]:
        """Cargar el diccionario de palabras clave para análisis financiero"""
        return {
            "activos": [
                "activos corrientes", "activo corriente", "activos no corrientes", 
                "activo no corriente", "efectivo y equivalentes", "caja y bancos",
                "valores negociables", "cuentas por cobrar comerciales", "cuentas por cobrar",
                "inventarios", "existencias", "propiedades, planta y equipo",
                "inmuebles, maquinaria y equipo", "activos intangibles", "inversiones",
                "activos biológicos", "total activos"
            ],
            "pasivos": [
                "pasivos corrientes", "pasivo corriente", "pasivos no corrientes",
                "pasivo no corriente", "préstamos bancarios", "cuentas por pagar comerciales",
                "cuentas por pagar", "deudas a largo plazo", "obligaciones financieras",
                "ingresos diferidos", "provisiones", "total pasivos"
            ],
            "patrimonio": [
                "patrimonio", "patrimonio neto", "capital", "capital emitido",
                "capital adicional", "primas de emisión", "acciones de inversión",
                "resultados acumulados", "reservas", "reservas legales",
                "excedente de revaluación", "superávit de revaluación", "total patrimonio"
            ],
            "estado_resultados": [
                "ingresos", "ventas netas", "ingresos operacionales",
                "ingresos de actividades ordinarias", "costo de ventas", "costo operacional",
                "utilidad bruta", "ganancia bruta", "gastos operacionales",
                "gastos de ventas", "gastos de administración", "utilidad operativa",
                "ganancia operativa", "resultado operativo", "ingresos financieros",
                "gastos financieros", "utilidad neta", "ganancia neta", "pérdida neta",
                "resultado del ejercicio"
            ],
            "flujo_efectivo": [
                "flujo de efectivo de operación", "actividades de operación",
                "flujo de efectivo de inversión", "actividades de inversión",
                "flujo de efectivo de financiamiento", "actividades de financiación",
                "efectivo neto"
            ],
            "años": ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015"],
            "totales": [
                "total activos", "total pasivos", "total patrimonio", "total pasivo y patrimonio",
                "total ingresos", "total gastos", "total costo"
            ]
        }
    
    def convertir_xls_a_html(self, archivo_xls: str) -> str:
        """Convertir archivo XLS a HTML (solo cambiar extensión)"""
        try:
            # Crear nombre del archivo HTML
            nombre_base = Path(archivo_xls).stem
            archivo_html = os.path.join(self.temp_dir, f"{nombre_base}.html")
            
            # Copiar el archivo XLS y guardarlo como HTML
            # El archivo XLS original ya tiene formato HTML
            shutil.copy2(archivo_xls, archivo_html)
            
            return archivo_html
        except Exception as e:
            st.error(f"Error al convertir XLS a HTML: {str(e)}")
            return None
    
    def extraer_datos_html(self, archivo_html: str) -> Dict[str, Any]:
        """
        Extraer datos importantes del archivo HTML usando el EXTRACTOR MEJORADO
        
        ✨ NUEVO: Usa extractor_estados_mejorado.py para extracción precisa de bloques
        """
        try:
            st.info("🔍 Usando Extractor Mejorado con detección automática de formato...")
            
            # Leer archivo HTML
            with open(archivo_html, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # ✨ USAR EL NUEVO EXTRACTOR MEJORADO
            resultados_mejorados = self.extractor_mejorado.extraer_todos_estados(html_content)
            
            # Mostrar información de extracción
            año_doc = resultados_mejorados['año_documento']
            formato = resultados_mejorados['formato']
            st.success(f"📅 Año detectado: {año_doc} | 📋 Formato: {formato.upper()}")
            
            # Convertir resultados del nuevo extractor al formato esperado por el resto del código
            datos_extraidos = self._convertir_formato_mejorado_a_legacy(resultados_mejorados)
            
            # Mostrar resumen de extracción
            if resultados_mejorados['estados']:
                st.info(f"✅ Estados extraídos: {len(resultados_mejorados['estados'])}")
                for key, estado in resultados_mejorados['estados'].items():
                    st.write(f"   📊 {estado['nombre']}: {estado['total_cuentas']} cuentas")
            
            # Mostrar validación de equilibrio
            if 'equilibrio_contable' in resultados_mejorados['validaciones']:
                validacion = resultados_mejorados['validaciones']['equilibrio_contable']
                if validacion['es_valido']:
                    st.success(f"✅ Equilibrio contable válido (diferencia: {validacion['diferencia']:,.2f})")
                else:
                    st.warning(f"⚠️ Equilibrio contable con diferencia de {validacion['diferencia']:,.2f}")
            
            # Mostrar errores si los hay
            if resultados_mejorados['errores']:
                st.warning("⚠️ Advertencias durante la extracción:")
                for error in resultados_mejorados['errores']:
                    st.write(f"   • {error}")
            
            return datos_extraidos
            
        except Exception as e:
            st.error(f"❌ Error al extraer datos con extractor mejorado: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return {}
    
    def _convertir_formato_mejorado_a_legacy(self, resultados_mejorados: Dict) -> Dict[str, Any]:
        """
        Convierte el formato del extractor mejorado al formato legacy esperado por el código existente
        
        Args:
            resultados_mejorados: Resultados del extractor mejorado
            
        Returns:
            Dict en formato legacy compatible con analisis_vertical_horizontal.py
        """
        año_doc = resultados_mejorados['año_documento']
        estados_mejorados = resultados_mejorados['estados']
        metadatos_mejorados = resultados_mejorados.get('metadatos', {})
        
        # Crear estructura legacy con metadatos mejorados
        datos_legacy = {
            'año_documento': año_doc,
            'metadatos': {
                'año': str(año_doc),
                'formato': resultados_mejorados['formato'],
                'empresa': metadatos_mejorados.get('empresa', 'No identificada'),
                'tipo': metadatos_mejorados.get('tipo', 'No especificado'),
                'periodo': metadatos_mejorados.get('periodo', 'No especificado')
            },
            'años_disponibles': [],
            'estados_financieros': {},
            'cabeceras_columnas': []
        }
        
        # Extraer años disponibles de las cuentas
        años_set = set()
        for estado in estados_mejorados.values():
            for cuenta in estado['cuentas']:
                años_set.update(cuenta['valores'].keys())
        datos_legacy['años_disponibles'] = sorted(años_set, reverse=True)
        datos_legacy['cabeceras_columnas'] = ['Cuenta', 'NOTA'] + datos_legacy['años_disponibles']
        
        # Mapear estados mejorados a formato legacy
        mapeo_estados = {
            'balance': 'estado_situacion_financiera' if año_doc >= 2010 else 'balance_general',
            'resultados': 'estado_resultados' if año_doc >= 2010 else 'estado_ganancias_perdidas',
            'patrimonio': 'estado_cambios_patrimonio',
            'flujo': 'estado_flujo_efectivo',
            'integrales': 'estado_resultados_integrales'
        }
        
        # Convertir cada estado
        for key_mejorado, nombre_legacy in mapeo_estados.items():
            if key_mejorado in estados_mejorados:
                estado_mejorado = estados_mejorados[key_mejorado]
                
                # Convertir cuentas al formato legacy
                cuentas_legacy = []
                for cuenta in estado_mejorado['cuentas']:
                    cuenta_legacy = {
                        'cuenta': cuenta['nombre'],
                        'es_total': cuenta['es_total']
                    }
                    
                    # Agregar valores por año
                    for año in datos_legacy['años_disponibles']:
                        valor = cuenta['valores'].get(año, 0.0)
                        cuenta_legacy[año] = {
                            'numero': valor,
                            'texto': self._formatear_numero(valor)
                        }
                    
                    cuentas_legacy.append(cuenta_legacy)
                
                # Agregar estado al diccionario legacy
                datos_legacy['estados_financieros'][nombre_legacy] = {
                    'nombre': estado_mejorado['nombre'],
                    'años': estado_mejorado['años'],
                    'datos': cuentas_legacy,
                    'total_cuentas': estado_mejorado['total_cuentas']
                }
        
        return datos_legacy
    
    def _formatear_numero(self, valor: float) -> str:
        """Formatea un número float al formato de texto esperado"""
        if valor == 0:
            return '0'
        elif valor < 0:
            return f"({abs(valor):,.0f})"
        else:
            return f"{valor:,.0f}"
    
    def extraer_metadatos(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extraer metadatos del documento - MEJORADO para años ≤2009"""
        metadatos = {}
        
        # Buscar información de la empresa
        texto_completo = soup.get_text().lower()
        
        # Buscar año - múltiples patrones
        años_encontrados = re.findall(r'\baño:\s*(\d{4})', texto_completo)
        if not años_encontrados:
            # Buscar años en divs específicos
            años_encontrados = re.findall(r'<div>a[ñn]o:\s*(\d{4})', str(soup).lower())
        if not años_encontrados:
            # Buscar el primer año que aparezca en el documento
            años_regex = re.findall(r'\b(19[9]\d|20[0-3]\d)\b', texto_completo)
            if años_regex:
                años_encontrados = [años_regex[0]]  # Tomar el primer año encontrado
        
        if años_encontrados:
            metadatos['año'] = años_encontrados[0]
        
        # Buscar empresa - múltiples patrones
        empresa_match = re.search(r'empresa:\s*([^\n\r<>]+)', texto_completo)
        if not empresa_match:
            # Buscar en divs específicos
            empresa_match = re.search(r'<div>empresa:\s*([^\n\r<>]+)', str(soup).lower())
        if not empresa_match:
            # Buscar nombres de empresas típicos
            empresa_match = re.search(r'(compañ[íi]a\s+[^<>\n\r]+s\.?a\.?)', texto_completo)
        
        if empresa_match:
            metadatos['empresa'] = empresa_match.group(1).strip()
        
        # Buscar tipo de reporte - múltiples patrones
        tipo_match = re.search(r'tipo:\s*([^\n\r<>]+)', texto_completo)
        if not tipo_match:
            tipo_match = re.search(r'<div>tipo:\s*([^\n\r<>]+)', str(soup).lower())
        if not tipo_match:
            # Si encuentra "balance general" o similar, usar como tipo
            if 'balance general' in texto_completo:
                metadatos['tipo'] = 'Balance General'
            elif 'estados financieros' in texto_completo:
                metadatos['tipo'] = 'Estados Financieros'
        
        if tipo_match:
            metadatos['tipo'] = tipo_match.group(1).strip()
        
        # Buscar período - múltiples patrones
        periodo_match = re.search(r'per[íi]odo:\s*([^\n\r<>]+)', texto_completo)
        if not periodo_match:
            periodo_match = re.search(r'<div>per[íi]odo:\s*([^\n\r<>]+)', str(soup).lower())
        if not periodo_match:
            # Buscar "anual", "trimestral", etc.
            if 'anual' in texto_completo:
                metadatos['periodo'] = 'Anual'
        
        if periodo_match:
            metadatos['periodo'] = periodo_match.group(1).strip()
        
        return metadatos
    
    def detectar_estados_financieros(self, soup: BeautifulSoup, año_documento: int = None) -> Dict[str, Dict]:
        """Detectar y extraer datos por cada estado financiero según el año"""
        
        # Detectar año del documento si no se proporciona
        if año_documento is None:
            años_encontrados = self.encontrar_años(soup)
            if años_encontrados:
                año_documento = int(años_encontrados[0])
            else:
                año_documento = 2020  # Por defecto
        
        # Definir estados financieros según el año
        if año_documento <= 2009:
            # Para años 2009 hacia abajo
            estados_financieros = {
                "balance_general": {
                    "nombre": "Balance General",
                    "patrones": [
                        r"balance\s+general",
                        r"estado\s+de\s+situaci[óo]n\s+financiera"
                    ],
                    "datos": []
                },
                "estado_ganancias_perdidas": {
                    "nombre": "Estado de Ganancias y Pérdidas",
                    "patrones": [
                        r"estado\s+de\s+ganancias\s+y\s+p[ée]rdidas",
                        r"estado\s+de\s+resultados"
                    ],
                    "datos": []
                },
                "estado_cambios_patrimonio": {
                    "nombre": "Estado de Cambios en el Patrimonio Neto",
                    "patrones": [
                        r"estado\s+de\s+cambios\s+en\s+el\s+patrimonio\s+neto",
                        r"estado\s+de\s+cambios\s+en\s+el\s+patrimonio"
                    ],
                    "datos": []
                },
                "estado_flujo_efectivo": {
                    "nombre": "Estado de Flujo de Efectivo",
                    "patrones": [
                        r"estado\s+de\s+flujo\s+de\s+efectivo",
                        r"estado\s+de\s+flujos\s+de\s+efectivo"
                    ],
                    "datos": []
                }
            }
        else:
            # Para años 2010 hacia arriba
            estados_financieros = {
                "estado_situacion_financiera": {
                    "nombre": "Estado de Situación Financiera",
                    "patrones": [
                        r"estado\s+de\s+situaci[óo]n\s+financiera",
                        r"balance\s+general"
                    ],
                    "datos": []
                },
                "estado_resultados": {
                    "nombre": "Estado de Resultados",
                    "patrones": [
                        r"estado\s+de\s+resultados",
                        r"estado\s+de\s+ganancias\s+y\s+p[ée]rdidas"
                    ],
                    "datos": []
                },
                "estado_cambios_patrimonio": {
                    "nombre": "Estado de Cambios en el Patrimonio Neto",
                    "patrones": [
                        r"estados?\s+de\s+cambios\s+en\s+el\s+patrimonio\s+neto",
                        r"estado\s+de\s+cambios\s+en\s+el\s+patrimonio"
                    ],
                    "datos": []
                },
                "estado_flujos_efectivo": {
                    "nombre": "Estado de Flujos de Efectivo",
                    "patrones": [
                        r"estado\s+de\s+flujos\s+de\s+efectivo",
                        r"estado\s+de\s+flujo\s+de\s+efectivo"
                    ],
                    "datos": []
                },
                "estado_resultados_integrales": {
                    "nombre": "Estado de Resultados Integrales",
                    "patrones": [
                        r"estado\s+de\s+resultados\s+integrales",
                        r"estado\s+del\s+resultado\s+integral"
                    ],
                    "datos": []
                }
            }
        
        # Buscar tablas y clasificarlas por estado financiero
        tablas = soup.find_all('table')
        
        for tabla in tablas:
            # Buscar el contexto antes de la tabla
            contexto = self.obtener_contexto_tabla(tabla)
            
            # Clasificar la tabla
            estado_identificado = None
            for clave_estado, info_estado in estados_financieros.items():
                for patron in info_estado["patrones"]:
                    if re.search(patron, contexto.lower()):
                        estado_identificado = clave_estado
                        break
                if estado_identificado:
                    break
            
            if estado_identificado:
                # Extraer datos de la tabla
                datos_tabla = self.extraer_datos_tabla(tabla)
                estados_financieros[estado_identificado]["datos"].extend(datos_tabla)
        
        return estados_financieros
    
    def obtener_contexto_tabla(self, tabla) -> str:
        """Obtener el contexto textual alrededor de una tabla"""
        contexto = ""
        
        # Buscar elementos anteriores (títulos, encabezados)
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'p']:
            elemento_anterior = tabla.find_previous(tag)
            if elemento_anterior:
                texto = elemento_anterior.get_text(strip=True)
                if len(texto) > 5:  # Evitar textos muy cortos
                    contexto += " " + texto
        
        # También buscar en elementos contenedores
        parent = tabla.parent
        while parent and parent.name != 'html':
            if parent.name in ['div', 'section', 'article']:
                # Buscar títulos en el contenedor
                titulos = parent.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span'], limit=5)
                for titulo in titulos:
                    texto = titulo.get_text(strip=True)
                    if len(texto) > 5:
                        contexto += " " + texto
            parent = parent.parent
        
        return contexto[:500]  # Limitar longitud
    
    def extraer_datos_tabla(self, tabla) -> List[Dict]:
        """Extraer datos estructurados de una tabla"""
        datos = []
        filas = tabla.find_all('tr')
        
        # Obtener cabeceras (primera fila o fila con th)
        cabeceras = []
        fila_cabecera = None
        
        for i, fila in enumerate(filas):
            celdas_th = fila.find_all('th')
            if celdas_th:
                fila_cabecera = i
                cabeceras = [th.get_text(strip=True) for th in celdas_th]
                break
        
        # Si no hay th, usar la primera fila como cabecera
        if not cabeceras and filas:
            primera_fila = filas[0].find_all(['td', 'th'])
            cabeceras = [celda.get_text(strip=True) for celda in primera_fila]
            fila_cabecera = 0
        
        # Procesar filas de datos
        filas_datos = filas[fila_cabecera + 1:] if fila_cabecera is not None else filas
        
        for fila in filas_datos:
            celdas = fila.find_all(['td', 'th'])
            if len(celdas) >= 2:  # Al menos cuenta y un valor
                fila_datos = {}
                
                for i, celda in enumerate(celdas):
                    valor_texto = celda.get_text(strip=True)
                    
                    if i == 0:  # Primera columna es generalmente la cuenta
                        fila_datos['cuenta'] = valor_texto
                    else:
                        # Usar cabecera si existe, sino usar índice
                        clave = cabeceras[i] if i < len(cabeceras) and cabeceras[i] else f"Columna_{i}"
                        fila_datos[clave] = {
                            'texto': valor_texto,
                            'numero': self.convertir_a_numero(valor_texto)
                        }
                
                if fila_datos.get('cuenta'):
                    datos.append(fila_datos)
        
        return datos
    
    def extraer_cabeceras_columnas(self, soup: BeautifulSoup) -> List[str]:
        """Extraer las cabeceras de las columnas de las tablas"""
        cabeceras_encontradas = set()
        
        tablas = soup.find_all('table')
        for tabla in tablas:
            # Buscar cabeceras en th
            headers_th = tabla.find_all('th')
            for header in headers_th:
                texto = header.get_text(strip=True)
                if texto and len(texto) > 1:
                    cabeceras_encontradas.add(texto)
            
            # También buscar en la primera fila si no hay th
            if not headers_th:
                primera_fila = tabla.find('tr')
                if primera_fila:
                    celdas = primera_fila.find_all('td')
                    for celda in celdas:
                        texto = celda.get_text(strip=True)
                        if texto and len(texto) > 1:
                            # Verificar si parece una cabecera (contiene años o palabras clave)
                            if re.match(r'^\d{4}$', texto) or any(palabra in texto.lower() for palabra in ['cuenta', 'nota', 'descripción']):
                                cabeceras_encontradas.add(texto)
        
        return sorted(list(cabeceras_encontradas))
    
    def convertir_a_numero(self, texto: str) -> float:
        """Convertir texto a número con manejo avanzado de formatos"""
        if not texto or texto.strip() == '':
            return 0.0
        
        texto_original = texto.strip()
        
        # Reemplazar espacios en blanco y guiones por 0
        if texto_original == '-' or texto_original == '--' or texto_original.isspace():
            return 0.0
        
        # Detectar números negativos en paréntesis
        es_negativo = False
        if texto_original.startswith('(') and texto_original.endswith(')'):
            es_negativo = True
            texto_original = texto_original[1:-1].strip()
        
        # Detectar signo negativo
        if texto_original.startswith('-'):
            es_negativo = True
            texto_original = texto_original[1:].strip()
        
        try:
            # Remover símbolos de moneda comunes
            texto_limpio = re.sub(r'[S/\$€£¥₹]', '', texto_original)
            
            # Remover espacios y otros caracteres no numéricos excepto punto, coma y guión
            texto_limpio = re.sub(r'[^\d.,\-]', '', texto_limpio)
            
            # FORMATO PERUANO/LATINOAMERICANO:
            # - Comas (,) = separadores de miles: 123,456 = 123456
            # - Puntos (.) = separadores decimales: 123.50 = 123.5
            
            # Caso 1: Número con comas y punto (ej: 1,234,567.89)
            if ',' in texto_limpio and '.' in texto_limpio:
                # Verificar que el punto esté al final para decimales
                partes = texto_limpio.split('.')
                if len(partes) == 2 and len(partes[1]) <= 3:  # Máximo 3 decimales
                    parte_entera = partes[0].replace(',', '')  # Remover comas de miles
                    parte_decimal = partes[1]
                    texto_limpio = f"{parte_entera}.{parte_decimal}"
                else:
                    # Si hay múltiples puntos, tratar todo como entero
                    texto_limpio = texto_limpio.replace(',', '').replace('.', '')
            
            # Caso 2: Solo comas (ej: 123,456 = 123456)
            elif ',' in texto_limpio and '.' not in texto_limpio:
                texto_limpio = texto_limpio.replace(',', '')
            
            # Caso 3: Solo punto (ej: 123.45 = 123.45)
            elif '.' in texto_limpio and ',' not in texto_limpio:
                # Verificar si es decimal válido
                partes = texto_limpio.split('.')
                if len(partes) == 2 and len(partes[1]) <= 3:
                    # Es decimal, mantener como está
                    pass
                else:
                    # Múltiples puntos o formato inválido, remover puntos
                    texto_limpio = texto_limpio.replace('.', '')
            
            # Caso 4: Solo números (ya está limpio)
            
            # Convertir a float
            if texto_limpio:
                numero = float(texto_limpio)
                return -numero if es_negativo else numero
            else:
                return 0.0
                
        except (ValueError, TypeError):
            # Si falla la conversión, intentar extraer solo los dígitos
            try:
                digitos = re.findall(r'\d', texto_original)
                if digitos:
                    numero = float(''.join(digitos))
                    return -numero if es_negativo else numero
                else:
                    return 0.0
            except:
                return 0.0
    
    def encontrar_años(self, soup: BeautifulSoup) -> List[str]:
        """Encontrar los años disponibles en el documento - MEJORADO para años ≤2009"""
        años_encontrados = set()
        
        # Buscar en el texto completo usando regex más flexible
        texto = soup.get_text()
        
        # Buscar años de 1990 a 2030 (rango amplio)
        import re
        años_regex = re.findall(r'\b(19[9]\d|20[0-3]\d)\b', texto)
        for año in años_regex:
            años_encontrados.add(año)
        
        # Buscar específicamente en headers de tablas con mayor precisión
        headers = soup.find_all(['th', 'td'])
        for header in headers:
            texto_header = header.get_text(strip=True)
            
            # Buscar años específicos en headers
            años_en_header = re.findall(r'\b(19[9]\d|20[0-3]\d)\b', texto_header)
            for año in años_en_header:
                años_encontrados.add(año)
            
            # También buscar años exactos de la lista predefinida
            for año in self.palabras_clave["años"]:
                if año == texto_header:
                    años_encontrados.add(año)
        
        # Filtrar años razonables (1990-2024) - excluir años futuros
        import datetime
        año_actual = datetime.datetime.now().year
        
        años_filtrados = []
        for año_str in años_encontrados:
            try:
                año_num = int(año_str)
                if 1990 <= año_num <= año_actual:
                    años_filtrados.append(año_str)
            except:
                continue
        
        return sorted(list(set(años_filtrados)), reverse=True)
    
    def generar_resumen_analisis(self, datos_extraidos: Dict[str, Any]) -> Dict[str, Any]:
        """Generar un resumen del análisis realizado"""
        resumen = {
            'total_datos_extraidos': 0,
            'estados_encontrados': [],
            'años_disponibles': datos_extraidos.get('años_disponibles', []),
            'empresa': datos_extraidos.get('metadatos', {}).get('empresa', 'No identificada'),
            'año_reporte': datos_extraidos.get('metadatos', {}).get('año', 'No identificado'),
            'tipo_reporte': datos_extraidos.get('metadatos', {}).get('tipo', 'No identificado'),
            'cabeceras_disponibles': datos_extraidos.get('cabeceras_columnas', [])
        }
        
        # Contar datos por estado financiero
        estados_financieros = datos_extraidos.get('estados_financieros', {})
        for clave_estado, info_estado in estados_financieros.items():
            if info_estado.get('datos'):
                resumen['estados_encontrados'].append(info_estado['nombre'])
                resumen['total_datos_extraidos'] += len(info_estado['datos'])
        
        return resumen
    
    def consolidar_multiples_archivos_post_2010(self, resultados_analisis: List[Dict]) -> Dict[str, pd.DataFrame]:
        """
        Consolida múltiples archivos POST-2010 (≥2010) en una vista unificada por bloque
        
        Args:
            resultados_analisis: Lista de resultados de análisis de múltiples archivos
        
        Returns:
            Dict con DataFrames consolidados por bloque: {
                'situacion_financiera': DataFrame,
                'resultados': DataFrame,
                'flujo_efectivo': DataFrame,
                'cambios_patrimonio': DataFrame
            }
        """
        # Filtrar solo archivos POST-2010 - CORREGIDO: buscar en 'datos' no en 'datos_extraidos'
        archivos_post_2010 = [r for r in resultados_analisis if r.get('datos', {}).get('año_documento', 0) >= 2010]
        
        if not archivos_post_2010:
            return {}
        
        # Ordenar por año descendente (más reciente primero) - CORREGIDO
        archivos_post_2010.sort(key=lambda x: x.get('datos', {}).get('año_documento', 0), reverse=True)
        
        # Mapeo de nombres de estados POST-2010
        estados_post_2010 = {
            'estado_situacion_financiera': 'Estado de Situación Financiera',
            'estado_resultados': 'Estado de Resultados',
            'estado_flujo_efectivo': 'Estado de Flujo de Efectivo',
            'estado_cambios_patrimonio': 'Estado de Cambios en el Patrimonio Neto'
        }
        
        consolidado = {}
        años_procesados = set()  # Para evitar duplicados
        
        for nombre_estado, titulo_estado in estados_post_2010.items():
            # Diccionario para consolidar: {nombre_cuenta: {año1: valor1, año2: valor2, ...}}
            cuentas_consolidadas = {}
            años_disponibles = set()
            
            # Procesar cada archivo
            for resultado in archivos_post_2010:
                datos_extraidos = resultado.get('datos', {})  # CORREGIDO: usar 'datos' no 'datos_extraidos'
                estados_financieros = datos_extraidos.get('estados_financieros', {})
                
                if nombre_estado in estados_financieros:
                    estado_datos = estados_financieros[nombre_estado]
                    
                    # Procesar cada cuenta del estado
                    for item in estado_datos.get('datos', []):
                        nombre_cuenta = item.get('cuenta', 'Sin cuenta')
                        
                        # Inicializar cuenta si no existe
                        if nombre_cuenta not in cuentas_consolidadas:
                            cuentas_consolidadas[nombre_cuenta] = {}
                        
                        # Agregar valores por año (solo si no se ha procesado ese año antes)
                        for clave, valor in item.items():
                            if clave != 'cuenta' and isinstance(valor, dict):
                                # Extraer año y valor numérico
                                año_str = str(clave)
                                if año_str.isdigit():
                                    año = int(año_str)
                                    
                                    # Solo agregar si ese año no ha sido procesado para esta cuenta
                                    if año not in cuentas_consolidadas[nombre_cuenta]:
                                        numero = valor.get('numero', 0)
                                        cuentas_consolidadas[nombre_cuenta][año] = numero
                                        años_disponibles.add(año)
            
            # Convertir a DataFrame
            if cuentas_consolidadas:
                # Crear lista de filas para DataFrame
                filas_consolidadas = []
                for nombre_cuenta, valores_años in cuentas_consolidadas.items():
                    fila = {'Cuenta': nombre_cuenta}
                    fila.update(valores_años)
                    filas_consolidadas.append(fila)
                
                df = pd.DataFrame(filas_consolidadas)
                
                # Ordenar columnas: primero 'Cuenta', luego años descendentes
                columnas = ['Cuenta']
                años_cols = sorted([col for col in df.columns if col != 'Cuenta'], reverse=True)
                columnas.extend(años_cols)
                
                # Reordenar y llenar valores faltantes con 0
                df = df[columnas].fillna(0)
                
                consolidado[nombre_estado] = df
        
        return consolidado

def main():
    st.title("📊 Analizador Financiero con Streamlit")
    st.markdown("### Análisis automático de estados financieros desde archivos XLS")
    
    # Crear instancia del analizador
    analizador = AnalizadorFinanciero()
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración")
    st.sidebar.markdown("Sube uno o varios archivos XLS para analizar")
    
    # Upload de archivos
    archivos_subidos = st.file_uploader(
        "Selecciona archivos XLS de estados financieros",
        type=['xls', 'xlsx'],
        accept_multiple_files=True,
        help="Puedes subir múltiples archivos XLS con estados financieros"
    )
    
    if archivos_subidos:
        st.success(f"✅ {len(archivos_subidos)} archivo(s) cargado(s)")
        
        # Procesar cada archivo
        resultados_analisis = []
        
        for archivo in archivos_subidos:
            with st.expander(f"📄 Analizando: {archivo.name}"):
                try:
                    # Guardar archivo en directorio temporal
                    ruta_temp = os.path.join(analizador.temp_dir, archivo.name)
                    with open(ruta_temp, 'wb') as f:
                        f.write(archivo.getbuffer())
                    
                    st.info("⏳ Convirtiendo XLS a HTML...")
                    
                    # Convertir a HTML
                    archivo_html = analizador.convertir_xls_a_html(ruta_temp)
                    
                    if archivo_html:
                        st.success("✅ Conversión a HTML completada")
                        
                        st.info("⏳ Extrayendo datos financieros...")
                        
                        # Extraer datos
                        datos_extraidos = analizador.extraer_datos_html(archivo_html)
                        
                        if datos_extraidos:
                            st.success("✅ Extracción de datos completada")
                            
                            # Generar resumen
                            resumen = analizador.generar_resumen_analisis(datos_extraidos)
                            resultados_analisis.append({
                                'archivo': archivo.name,
                                'datos': datos_extraidos,
                                'resumen': resumen
                            })
                            
                            # Mostrar información básica
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Empresa", resumen['empresa'])
                            
                            with col2:
                                st.metric("Año", resumen['año_reporte'])
                            
                            with col3:
                                st.metric("Datos extraídos", resumen['total_datos_extraidos'])
                            
                            # Mostrar estados encontrados
                            if resumen['estados_encontrados']:
                                st.write("**Estados financieros detectados:**")
                                for estado in resumen['estados_encontrados']:
                                    st.write(f"- {estado}")
                            
                            # Mostrar años disponibles
                            if resumen['años_disponibles']:
                                st.write("**Años disponibles:**")
                                st.write(", ".join(resumen['años_disponibles']))
                            
                            # Mostrar cabeceras disponibles
                            if resumen['cabeceras_disponibles']:
                                st.write("**Cabeceras de columnas detectadas:**")
                                st.write(", ".join(resumen['cabeceras_disponibles'][:10]))  # Mostrar solo las primeras 10
                        
                        else:
                            st.error("❌ Error al extraer datos del archivo")
                    
                    else:
                        st.error("❌ Error al convertir archivo a HTML")
                
                except Exception as e:
                    st.error(f"❌ Error al procesar {archivo.name}: {str(e)}")
        
        # Mostrar análisis consolidado
        if resultados_analisis:
            st.header("📈 Análisis Consolidado")
            
            # Crear tabs para diferentes vistas
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "Resumen General", 
                "Vista Consolidada (≥2010)", 
                "Estados Financieros", 
                "Análisis Vertical", 
                "Comparativo", 
                "Datos Detallados"
            ])
            
            with tab1:
                st.subheader("Resumen de todos los archivos procesados")
                
                # Tabla resumen
                datos_resumen = []
                for resultado in resultados_analisis:
                    datos_resumen.append({
                        'Archivo': resultado['archivo'],
                        'Empresa': resultado['resumen']['empresa'],
                        'Año': resultado['resumen']['año_reporte'],
                        'Tipo': resultado['resumen']['tipo_reporte'],
                        'Datos Extraídos': resultado['resumen']['total_datos_extraidos'],
                        'Estados Detectados': len(resultado['resumen']['estados_encontrados'])
                    })
                
                df_resumen = pd.DataFrame(datos_resumen)
                st.dataframe(df_resumen, use_container_width=True)
            
            with tab2:
                st.subheader("📊 Vista Consolidada Multi-Período (Formato ≥2010)")
                st.caption("*Consolida automáticamente múltiples archivos de años consecutivos en una sola vista por bloque*")
                
                # Verificar si hay archivos POST-2010 - CORREGIDO: usar 'datos' no 'datos_extraidos'
                archivos_post_2010 = [r for r in resultados_analisis 
                                      if r.get('datos', {}).get('año_documento', 0) >= 2010]
                
                if not archivos_post_2010:
                    st.warning("⚠️ No hay archivos del formato POST-2010 (≥2010) para consolidar.")
                    st.info("Esta vista solo funciona con archivos del año 2010 en adelante.")
                else:
                    # Detectar empresa (asumiendo que todos son de la misma empresa)
                    empresa = archivos_post_2010[0].get('resumen', {}).get('empresa', 'No identificada')
                    años_detectados = sorted([r.get('datos', {}).get('año_documento', 0) 
                                             for r in archivos_post_2010], reverse=True)
                    
                    st.success(f"✅ **Empresa:** {empresa}")
                    st.info(f"📅 **Años detectados:** {', '.join(map(str, años_detectados))}")
                    
                    # Consolidar datos
                    with st.spinner("Consolidando datos de múltiples archivos..."):
                        consolidado = analizador.consolidar_multiples_archivos_post_2010(resultados_analisis)
                    
                    if consolidado:
                        # Crear sub-tabs por cada bloque
                        bloques = []
                        titulos_bloques = []
                        
                        if 'estado_situacion_financiera' in consolidado:
                            bloques.append('estado_situacion_financiera')
                            titulos_bloques.append("📈 Situación Financiera")
                        
                        if 'estado_resultados' in consolidado:
                            bloques.append('estado_resultados')
                            titulos_bloques.append("💰 Resultados")
                        
                        if 'estado_flujo_efectivo' in consolidado:
                            bloques.append('estado_flujo_efectivo')
                            titulos_bloques.append("💵 Flujo de Efectivo")
                        
                        if 'estado_cambios_patrimonio' in consolidado:
                            bloques.append('estado_cambios_patrimonio')
                            titulos_bloques.append("🏦 Cambios en Patrimonio")
                        
                        if bloques:
                            tabs_consolidado = st.tabs(titulos_bloques)
                            
                            for idx, bloque in enumerate(bloques):
                                with tabs_consolidado[idx]:
                                    df_bloque = consolidado[bloque]
                                    
                                    # Formatear números
                                    df_display = df_bloque.copy()
                                    for col in df_display.columns:
                                        if col != 'Cuenta':
                                            df_display[col] = df_display[col].apply(
                                                lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else '-'
                                            )
                                    
                                    st.dataframe(df_display, use_container_width=True, height=600)
                                    
                                    # Métricas
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Total de Cuentas", len(df_bloque))
                                    with col2:
                                        años_cols = [col for col in df_bloque.columns if col != 'Cuenta']
                                        st.metric("Años Consolidados", len(años_cols))
                                    
                                    # Botón de descarga
                                    csv = df_display.to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        label=f"⬇️ Descargar {titulos_bloques[idx]} (CSV)",
                                        data=csv,
                                        file_name=f"{empresa}_{bloque}_consolidado.csv",
                                        mime="text/csv",
                                        key=f"download_{bloque}"
                                    )
                    else:
                        st.warning("No se pudo consolidar la información. Verifica que los archivos sean del formato POST-2010.")
            
            with tab3:
                st.subheader("Datos organizados por estado financiero")
                
                for resultado in resultados_analisis:
                    st.write(f"### 📄 {resultado['archivo']}")
                    año_doc = resultado['datos'].get('año_documento', 2020)
                    st.write(f"**Año del documento:** {año_doc}")
                    
                    if año_doc <= 2009:
                        st.info("📅 Formato aplicable para años 2009 hacia abajo")
                    else:
                        st.info("📅 Formato aplicable para años 2010 hacia arriba")
                    
                    estados_financieros = resultado['datos'].get('estados_financieros', {})
                    
                    if not estados_financieros:
                        st.warning("No se detectaron estados financieros en este archivo")
                        continue
                    
                    for clave_estado, info_estado in estados_financieros.items():
                        if info_estado.get('datos'):
                            st.write(f"#### 📋 {info_estado['nombre']}")
                            
                            # Convertir datos a DataFrame - SOLO VALORES NUMÉRICOS
                            datos_estado = []
                            for item in info_estado['datos']:
                                fila = {'Cuenta': item.get('cuenta', 'Sin cuenta')}
                                
                                # Agregar solo las columnas numéricas (años)
                                for clave, valor in item.items():
                                    if clave != 'cuenta':
                                        if isinstance(valor, dict):
                                            # Solo agregar el valor numérico sin sufijo
                                            numero_convertido = valor.get('numero', 0)
                                            fila[clave] = numero_convertido
                                        else:
                                            # Para otros campos que no son dict (ej: 'es_total', 'NOTA')
                                            # No incluirlos si no son años
                                            if clave.isdigit() or any(char.isdigit() for char in str(clave)):
                                                fila[clave] = valor if valor else 0
                                
                                datos_estado.append(fila)
                            
                            if datos_estado:
                                df_estado = pd.DataFrame(datos_estado)
                                
                                # Ordenar columnas: primero 'Cuenta', luego años en orden descendente
                                columnas = ['Cuenta']
                                años_cols = [col for col in df_estado.columns if col != 'Cuenta']
                                años_cols_sorted = sorted(años_cols, reverse=True)  # Más reciente primero
                                columnas.extend(años_cols_sorted)
                                
                                df_estado = df_estado[columnas]
                                
                                # Formatear números para mejor visualización
                                for col in df_estado.columns:
                                    if col != 'Cuenta':
                                        try:
                                            df_estado[col] = df_estado[col].apply(
                                                lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else '-'
                                            )
                                        except:
                                            pass
                                
                                st.dataframe(df_estado, use_container_width=True)
                                
                                # Mostrar estadísticas básicas
                                st.write(f"**Total de cuentas detectadas:** {len(datos_estado)}")
                            else:
                                st.info("No se encontraron datos para este estado financiero")
                        else:
                            st.write(f"#### 📋 {info_estado['nombre']}")
                            st.info("No se encontraron datos para este estado financiero")
                    
                    st.divider()
            
            with tab4:
                st.subheader("📊 Análisis Vertical Mejorado")
                
                try:
                    for resultado in resultados_analisis:
                        st.write(f"### 📄 {resultado['archivo']}")
                        
                        # Leer el archivo HTML original para análisis
                        ruta_html = os.path.join(analizador.temp_dir, resultado['archivo'].replace('.xls', '.html').replace('.xlsx', '.html'))
                        
                        if os.path.exists(ruta_html):
                            with open(ruta_html, 'r', encoding='utf-8', errors='ignore') as f:
                                html_content = f.read()
                            
                            # Extraer estados con el extractor mejorado
                            with st.spinner("Extrayendo estados financieros..."):
                                resultados_extractor = analizador.extractor_mejorado.extraer_todos_estados(html_content)
                            
                            # Mostrar metadatos
                            metadatos = resultados_extractor.get('metadatos', {})
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("🏢 Empresa", metadatos.get('empresa', 'N/A'))
                            with col2:
                                st.metric("📅 Año", resultados_extractor['año_documento'])
                            with col3:
                                st.metric("📋 Tipo", metadatos.get('tipo', 'N/A'))
                            with col4:
                                formato_txt = "Pre-2010 (PCG)" if resultados_extractor['formato'] == 'pre_2010' else "Post-2010 (NIIF)"
                                st.metric("📊 Formato", formato_txt)
                            
                            # Realizar análisis vertical
                            with st.spinner("Realizando análisis vertical..."):
                                analisis_vertical = analizador.analizador_vertical.analizar_desde_extractor(resultados_extractor)
                            
                            st.success("✅ Análisis vertical completado")
                            
                            # Mostrar resumen
                            resumen = analisis_vertical.get('resumen', {})
                            st.info(f"📊 Total de estados analizados: {resumen.get('total_estados_analizados', 0)}")
                            
                            estados_analizados = analisis_vertical.get('estados_analizados', {})
                            
                            # TAB para cada estado financiero
                            tabs_estados = []
                            if 'balance' in estados_analizados:
                                tabs_estados.append("Balance/Situación Financiera")
                            if 'resultados' in estados_analizados:
                                tabs_estados.append("Estado de Resultados")
                            if 'flujo' in estados_analizados:
                                tabs_estados.append("Flujo de Efectivo")
                            
                            if tabs_estados:
                                tabs_sub = st.tabs(tabs_estados)
                                tab_idx = 0
                                
                                # Balance / Situación Financiera
                                if 'balance' in estados_analizados:
                                    with tabs_sub[tab_idx]:
                                        balance_data = estados_analizados['balance']
                                        st.write(f"#### 💰 {balance_data['nombre_estado']}")
                                        st.write(f"**Año analizado:** {balance_data['año_analisis']}")
                                        
                                        # Métricas principales
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Total Activos", f"{balance_data['total_activos']:,.0f}")
                                        with col2:
                                            st.metric("Total Pasivos", f"{balance_data['total_pasivos']:,.0f}")
                                        with col3:
                                            patrimonio = balance_data['total_activos'] - balance_data['total_pasivos']
                                            st.metric("Patrimonio", f"{patrimonio:,.0f}")
                                        
                                        # ACTIVOS
                                        if balance_data['activos']:
                                            st.write("##### 📊 ACTIVOS - Análisis Vertical")
                                            st.caption("*Cada cuenta como % del Total de Activos*")
                                            
                                            df_activos = pd.DataFrame(balance_data['activos'])
                                            df_activos['Valor'] = df_activos['valor'].apply(lambda x: f"{x:,.0f}")
                                            df_activos['% Vertical'] = df_activos['analisis_vertical'].apply(lambda x: f"{x:.2f}%")
                                            
                                            df_mostrar = df_activos[['cuenta', 'Valor', '% Vertical']].copy()
                                            df_mostrar.columns = ['Cuenta', 'Valor', '% del Total Activos']
                                            
                                            st.dataframe(df_mostrar, use_container_width=True, height=400)
                                            
                                            # Gráfico de barras de principales activos
                                            st.write("**Top 10 Activos por Participación:**")
                                            df_chart = df_activos.nlargest(10, 'analisis_vertical')
                                            if not df_chart.empty:
                                                chart_data = df_chart.set_index('cuenta')['analisis_vertical']
                                                st.bar_chart(chart_data)
                                        
                                        # PASIVOS
                                        if balance_data['pasivos']:
                                            st.write("##### 💳 PASIVOS - Análisis Vertical")
                                            st.caption("*Cada cuenta como % del Total de Pasivos*")
                                            
                                            df_pasivos = pd.DataFrame(balance_data['pasivos'])
                                            df_pasivos['Valor'] = df_pasivos['valor'].apply(lambda x: f"{x:,.0f}")
                                            df_pasivos['% Vertical'] = df_pasivos['analisis_vertical'].apply(lambda x: f"{x:.2f}%")
                                            
                                            df_mostrar_p = df_pasivos[['cuenta', 'Valor', '% Vertical']].copy()
                                            df_mostrar_p.columns = ['Cuenta', 'Valor', '% del Total Pasivos']
                                            
                                            st.dataframe(df_mostrar_p, use_container_width=True, height=400)
                                            
                                            # Gráfico de barras de principales pasivos
                                            st.write("**Top 10 Pasivos por Participación:**")
                                            df_chart_p = df_pasivos.nlargest(10, 'analisis_vertical')
                                            if not df_chart_p.empty:
                                                chart_data_p = df_chart_p.set_index('cuenta')['analisis_vertical']
                                                st.bar_chart(chart_data_p)
                                        
                                        st.info(f"⚠️ PATRIMONIO: No se calcula análisis vertical (según especificación)")
                                    
                                    tab_idx += 1
                                
                                # Estado de Resultados
                                if 'resultados' in estados_analizados:
                                    with tabs_sub[tab_idx]:
                                        resultados_data = estados_analizados['resultados']
                                        st.write(f"#### 📈 {resultados_data['nombre_estado']}")
                                        st.write(f"**Año analizado:** {resultados_data['año_analisis']}")
                                        
                                        # Métrica principal
                                        st.metric("Total Ingresos (Base)", f"{resultados_data['total_ingresos']:,.0f}")
                                        
                                        if resultados_data['cuentas_analizadas']:
                                            st.write("##### 📊 Análisis Vertical")
                                            st.caption("*Cada cuenta como % del Total de Ingresos*")
                                            
                                            df_resultados = pd.DataFrame(resultados_data['cuentas_analizadas'])
                                            df_resultados['Valor'] = df_resultados['valor'].apply(lambda x: f"{x:,.0f}")
                                            df_resultados['% Vertical'] = df_resultados['analisis_vertical'].apply(lambda x: f"{x:.2f}%")
                                            
                                            df_mostrar_r = df_resultados[['cuenta', 'Valor', '% Vertical']].copy()
                                            df_mostrar_r.columns = ['Cuenta', 'Valor', '% de Ingresos']
                                            
                                            st.dataframe(df_mostrar_r, use_container_width=True, height=400)
                                            
                                            # Gráfico de composición
                                            st.write("**Composición del Estado de Resultados:**")
                                            df_chart_r = df_resultados[df_resultados['analisis_vertical'].abs() > 1]  # Solo > 1%
                                            if not df_chart_r.empty:
                                                chart_data_r = df_chart_r.set_index('cuenta')['analisis_vertical']
                                                st.bar_chart(chart_data_r)
                                    
                                    tab_idx += 1
                                
                                # Flujo de Efectivo
                                if 'flujo' in estados_analizados:
                                    with tabs_sub[tab_idx]:
                                        flujo_data = estados_analizados['flujo']
                                        st.write(f"#### 💵 {flujo_data['nombre_estado']}")
                                        st.write(f"**Año analizado:** {flujo_data['año_analisis']}")
                                        
                                        # Mostrar bases detectadas (múltiples secciones)
                                        if flujo_data.get('bases_detectadas'):
                                            st.write("##### 🎯 Bases Detectadas (100%)")
                                            cols_bases = st.columns(len(flujo_data['bases_detectadas']))
                                            for idx, (key, nombre_base) in enumerate(flujo_data['bases_detectadas'].items()):
                                                with cols_bases[idx]:
                                                    st.info(f"**{key.replace('_', ' ').title()}**\n\n{nombre_base}")
                                        
                                        if flujo_data['cuentas_analizadas']:
                                            st.write("##### 📊 Análisis Vertical por Secciones")
                                            st.caption("*Cada cuenta como % de su base correspondiente (Operación, Inversión, Financiación)*")
                                            
                                            df_flujo = pd.DataFrame(flujo_data['cuentas_analizadas'])
                                            df_flujo['Valor'] = df_flujo['valor'].apply(lambda x: f"{x:,.0f}")
                                            df_flujo['% Vertical'] = df_flujo['analisis_vertical'].apply(lambda x: f"{x:.2f}%")
                                            df_flujo['Es Base'] = df_flujo.get('es_base', False)
                                            
                                            df_mostrar_f = df_flujo[['cuenta', 'Valor', '% Vertical', 'Es Base']].copy()
                                            df_mostrar_f.columns = ['Cuenta', 'Valor', '% de Base', 'Es Base 100%']
                                            
                                            st.dataframe(df_mostrar_f, use_container_width=True, height=400)
                            
                            # Botón de exportación a Excel
                            st.write("---")
                            nombre_base = resultado['archivo'].split('.')[0]
                            archivo_excel = f"analisis_vertical_{nombre_base}.xlsx"
                            
                            if st.button(f"📥 Exportar a Excel: {archivo_excel}", key=f"export_{resultado['archivo']}"):
                                analizador.analizador_vertical.exportar_a_excel(analisis_vertical, archivo_excel)
                                st.success(f"✅ Archivo exportado: {archivo_excel}")
                                
                                # Ofrecer descarga
                                with open(archivo_excel, 'rb') as f:
                                    st.download_button(
                                        label="⬇️ Descargar Excel",
                                        data=f.read(),
                                        file_name=archivo_excel,
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        key=f"download_{resultado['archivo']}"
                                    )
                        
                        else:
                            st.warning(f"❌ No se encontró el archivo HTML: {ruta_html}")
                        
                        st.divider()
                    
                except Exception as e:
                    st.error(f"❌ Error en análisis vertical: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            
            with tab5:
                st.subheader("📊 Análisis Comparativo (Multi-período)")
                st.info("Esta sección permite comparar múltiples períodos cuando se cargan varios archivos.")
                
                if len(resultados_analisis) > 1:
                    st.success(f"✅ {len(resultados_analisis)} archivos disponibles para comparación")
                else:
                    st.warning("⚠️ Carga más de un archivo para habilitar el análisis comparativo")
            
            with tab6:
                st.subheader("Datos detallados por archivo")
                
                for resultado in resultados_analisis:
                    with st.expander(f"Ver detalles de {resultado['archivo']}"):
                        st.json(resultado['datos'], expanded=False)
        
        # Botón para descargar resultados
        if resultados_analisis:
            st.header("💾 Exportar Resultados")
            
            # Crear DataFrame consolidado para descarga
            datos_exportar = []
            for resultado in resultados_analisis:
                base_row = {
                    'archivo': resultado['archivo'],
                    'empresa': resultado['resumen']['empresa'],
                    'año': resultado['resumen']['año_reporte'],
                    'tipo': resultado['resumen']['tipo_reporte']
                }
                
                # Agregar datos por estado financiero
                estados_financieros = resultado['datos'].get('estados_financieros', {})
                for clave_estado, info_estado in estados_financieros.items():
                    for item in info_estado.get('datos', []):
                        row = base_row.copy()
                        row['estado_financiero'] = info_estado['nombre']
                        row['cuenta'] = item.get('cuenta', '')
                        
                        # Agregar todas las columnas
                        for clave, valor in item.items():
                            if clave != 'cuenta':
                                if isinstance(valor, dict):
                                    row[f'{clave}_texto'] = valor.get('texto', '')
                                    row[f'{clave}_numero'] = valor.get('numero', 0)
                                else:
                                    row[clave] = valor
                        
                        datos_exportar.append(row)
            
            if datos_exportar:
                df_exportar = pd.DataFrame(datos_exportar)
                
                # Convertir a CSV para descarga
                csv = df_exportar.to_csv(index=False, encoding='utf-8')
                
                st.download_button(
                    label="📥 Descargar resultados en CSV",
                    data=csv,
                    file_name=f"analisis_financiero_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("👆 Sube uno o más archivos XLS para comenzar el análisis")
        
        # Mostrar información sobre los estados financieros detectados
        with st.expander("📚 Estados financieros que se pueden detectar"):
            st.write("""
            El sistema puede identificar y analizar los siguientes estados financieros:
            
            - **Estado de Situación Financiera** (Balance General)
            - **Estado de Resultados** (Estado de Ganancias y Pérdidas)
            - **Estado de Cambios en el Patrimonio Neto**
            - **Estado de Flujo de Efectivo**
            - **Estado de Resultados Integrales**
            
            El sistema detecta automáticamente el tipo de estado financiero basado en:
            - Títulos y encabezados en el documento
            - Contexto de las tablas
            - Patrones de texto característicos
            """)
        
        # Mostrar información sobre las cabeceras
        with st.expander("🏷️ Manejo de cabeceras de columnas"):
            st.write("""
            El sistema identifica automáticamente las cabeceras de las columnas:
            
            - **Años**: 2024, 2023, 2022, etc.
            - **Notas**: Referencias a notas explicativas
            - **Descripciones**: Cuenta, Descripción, etc.
            - **Valores**: Importes en diferentes monedas
            
            Las cabeceras se extraen de:
            - Elementos `<th>` en las tablas HTML
            - Primera fila de datos cuando no hay `<th>`
            - Detección inteligente de años y términos financieros
            """)

if __name__ == "__main__":
    main()