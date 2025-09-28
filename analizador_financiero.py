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
        """Extraer datos importantes del archivo HTML"""
        try:
            # Detectar codificación automáticamente
            with open(archivo_html, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                codificacion = result['encoding'] or 'latin-1'
            
            # Leer con la codificación detectada
            try:
                with open(archivo_html, 'r', encoding=codificacion) as f:
                    contenido = f.read()
                st.info(f"✅ Archivo leído correctamente con codificación: {codificacion}")
            except:
                # Si falla, probar con latin-1 como fallback
                with open(archivo_html, 'r', encoding='latin-1', errors='ignore') as f:
                    contenido = f.read()
                st.warning("⚠️ Se usó codificación latin-1 ignorando errores")
            
            # Parsear el HTML
            soup = BeautifulSoup(contenido, 'html.parser')
            
            # Extraer metadatos primero para obtener el año
            metadatos = self.extraer_metadatos(soup)
            
            # Determinar el año del documento
            año_documento = None
            if 'año' in metadatos:
                try:
                    año_documento = int(metadatos['año'])
                except:
                    pass
            
            # Si no se encuentra en metadatos, buscar en años disponibles
            if año_documento is None:
                años_disponibles = self.encontrar_años(soup)
                if años_disponibles:
                    try:
                        año_documento = int(años_disponibles[0])
                    except:
                        año_documento = 2020  # Por defecto
            
            # Detectar estados financieros con el año del documento
            estados_detectados = self.detectar_estados_financieros(soup, año_documento)
            
            # Extraer información general
            datos_extraidos = {
                "metadatos": metadatos,
                "estados_financieros": estados_detectados,
                "años_disponibles": self.encontrar_años(soup),
                "cabeceras_columnas": self.extraer_cabeceras_columnas(soup),
                "año_documento": año_documento
            }
            
            return datos_extraidos
        except Exception as e:
            st.error(f"Error al extraer datos del HTML: {str(e)}")
            return {}
    
    def extraer_metadatos(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extraer metadatos del documento"""
        metadatos = {}
        
        # Buscar información de la empresa
        texto_completo = soup.get_text().lower()
        
        # Buscar año
        años_encontrados = re.findall(r'\baño:\s*(\d{4})', texto_completo)
        if años_encontrados:
            metadatos['año'] = años_encontrados[0]
        
        # Buscar empresa
        empresa_match = re.search(r'empresa:\s*([^\n\r]+)', texto_completo)
        if empresa_match:
            metadatos['empresa'] = empresa_match.group(1).strip()
        
        # Buscar tipo de reporte
        tipo_match = re.search(r'tipo:\s*([^\n\r]+)', texto_completo)
        if tipo_match:
            metadatos['tipo'] = tipo_match.group(1).strip()
        
        # Buscar período
        periodo_match = re.search(r'período:\s*([^\n\r]+)', texto_completo)
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
        """Encontrar los años disponibles en el documento"""
        años_encontrados = set()
        
        # Buscar en el texto completo
        texto = soup.get_text()
        for año in self.palabras_clave["años"]:
            if año in texto:
                años_encontrados.add(año)
        
        # Buscar en headers de tablas
        headers = soup.find_all(['th', 'td'])
        for header in headers:
            texto_header = header.get_text(strip=True)
            for año in self.palabras_clave["años"]:
                if año == texto_header:
                    años_encontrados.add(año)
        
        return sorted(list(años_encontrados), reverse=True)
    
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
            tab1, tab2, tab3, tab4 = st.tabs(["Resumen General", "Estados Financieros", "Comparativo", "Datos Detallados"])
            
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
                            
                            # Convertir datos a DataFrame
                            datos_estado = []
                            for item in info_estado['datos']:
                                fila = {'Cuenta': item.get('cuenta', 'Sin cuenta')}
                                
                                # Agregar todas las columnas que no sean 'cuenta'
                                for clave, valor in item.items():
                                    if clave != 'cuenta':
                                        if isinstance(valor, dict):
                                            # Mostrar tanto el texto original como el número convertido
                                            texto_original = valor.get('texto', '')
                                            numero_convertido = valor.get('numero', 0)
                                            
                                            # Si el texto original es diferente del número, mostrar ambos
                                            if texto_original and str(numero_convertido) != texto_original:
                                                fila[f"{clave}_Original"] = texto_original
                                                fila[f"{clave}_Numérico"] = numero_convertido
                                            else:
                                                fila[clave] = numero_convertido if numero_convertido != 0 else (texto_original or '-')
                                        else:
                                            fila[clave] = valor if valor else '-'
                                
                                datos_estado.append(fila)
                            
                            if datos_estado:
                                df_estado = pd.DataFrame(datos_estado)
                                
                                # Formatear números para mejor visualización
                                for col in df_estado.columns:
                                    if 'Numérico' in col or df_estado[col].dtype in ['float64', 'int64']:
                                        try:
                                            df_estado[col] = df_estado[col].apply(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) and x != 0 else (x if x != 0 else '-'))
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
            
            with tab3:
                st.subheader("Análisis comparativo entre períodos")
                
                if len(resultados_analisis) > 1:
                    st.info("Comparación disponible entre múltiples archivos")
                    
                    # Crear tabla comparativa
                    datos_comparativos = []
                    for resultado in resultados_analisis:
                        fila_comparativa = {
                            'Archivo': resultado['archivo'],
                            'Empresa': resultado['resumen']['empresa'],
                            'Año': resultado['resumen']['año_reporte'],
                            'Total_Datos': resultado['resumen']['total_datos_extraidos']
                        }
                        
                        # Agregar estados detectados
                        estados_financieros = resultado['datos'].get('estados_financieros', {})
                        for clave_estado, info_estado in estados_financieros.items():
                            nombre_col = info_estado['nombre'].replace(' ', '_')
                            fila_comparativa[nombre_col] = len(info_estado.get('datos', []))
                        
                        datos_comparativos.append(fila_comparativa)
                    
                    if datos_comparativos:
                        df_comparativo = pd.DataFrame(datos_comparativos)
                        st.dataframe(df_comparativo, use_container_width=True)
                
                else:
                    st.info("Sube más de un archivo para realizar comparaciones")
            
            with tab4:
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