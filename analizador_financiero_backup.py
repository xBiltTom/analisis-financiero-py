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
import chardet

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
            
            # Detectar estados financieros
            estados_detectados = self.detectar_estados_financieros(soup)
            
            # Extraer información general
            datos_extraidos = {
                "metadatos": self.extraer_metadatos(soup),
                "estados_financieros": estados_detectados,
                "años_disponibles": self.encontrar_años(soup),
                "cabeceras_columnas": self.extraer_cabeceras_columnas(soup)
            }
            
            return datos_extraidos
        except Exception as e:
            st.error(f"Error al extraer datos del HTML: {str(e)}")
            return {}
            soup = BeautifulSoup(contenido, 'html.parser')
            
            # Extraer información general
            datos_extraidos = {
                "metadatos": self.extraer_metadatos(soup),
                "activos": self.extraer_categoria_datos(soup, "activos"),
                "pasivos": self.extraer_categoria_datos(soup, "pasivos"),
                "patrimonio": self.extraer_categoria_datos(soup, "patrimonio"),
                "estado_resultados": self.extraer_categoria_datos(soup, "estado_resultados"),
                "flujo_efectivo": self.extraer_categoria_datos(soup, "flujo_efectivo"),
                "años_disponibles": self.encontrar_años(soup),
                "tablas_detectadas": self.detectar_tablas_estados_financieros(soup)
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
    
    def detectar_estados_financieros(self, soup: BeautifulSoup) -> Dict[str, Dict]:
        """Detectar y extraer datos por cada estado financiero"""
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
                    r"estado\s+de\s+cambios\s+en\s+el\s+patrimonio",
                    r"estado\s+de\s+cambios\s+en\s+el\s+patrimonio\s+neto"
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
    
    def extraer_categoria_datos(self, soup: BeautifulSoup, categoria: str) -> List[Dict[str, Any]]:
        """Extraer datos de una categoría específica"""
        datos_encontrados = []
        palabras_categoria = self.palabras_clave.get(categoria, [])
        
        # Buscar en todas las tablas
        tablas = soup.find_all('table')
        
        for tabla in tablas:
            filas = tabla.find_all('tr')
            
            for fila in filas:
                celdas = fila.find_all(['td', 'th'])
                if len(celdas) >= 2:
                    texto_cuenta = celdas[0].get_text(strip=True).lower()
                    
                    # Verificar si el texto coincide con alguna palabra clave
                    for palabra in palabras_categoria:
                        if palabra.lower() in texto_cuenta:
                            datos_fila = {
                                'cuenta': celdas[0].get_text(strip=True),
                                'valores': []
                            }
                            
                            # Extraer valores numéricos
                            for i in range(1, len(celdas)):
                                valor_texto = celdas[i].get_text(strip=True)
                                valor_numerico = self.convertir_a_numero(valor_texto)
                                datos_fila['valores'].append({
                                    'texto': valor_texto,
                                    'numero': valor_numerico
                                })
                            
                            datos_encontrados.append(datos_fila)
                            break
        
        return datos_encontrados
    
    def convertir_a_numero(self, texto: str) -> float:
        """Convertir texto a número"""
        try:
            # Limpiar el texto
            texto_limpio = re.sub(r'[^\d.,\-]', '', texto)
            texto_limpio = texto_limpio.replace(',', '')
            
            if texto_limpio:
                return float(texto_limpio)
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
    
    def detectar_tablas_estados_financieros(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Detectar y clasificar las tablas de estados financieros"""
        tablas_detectadas = []
        tablas = soup.find_all('table')
        
        estados_financieros = [
            "estado de situación financiera",
            "balance general",
            "estado de resultados",
            "estado de ganancias y pérdidas",
            "estado de flujo de efectivo",
            "estado de cambios en el patrimonio"
        ]
        
        for i, tabla in enumerate(tablas):
            # Buscar el contexto antes de la tabla
            texto_previo = ""
            elemento_previo = tabla.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'])
            if elemento_previo:
                texto_previo = elemento_previo.get_text().lower().strip()
            
            # Clasificar la tabla
            tipo_estado = "no identificado"
            for estado in estados_financieros:
                if estado in texto_previo:
                    tipo_estado = estado
                    break
            
            # Contar filas y columnas
            filas = tabla.find_all('tr')
            num_filas = len(filas)
            num_columnas = 0
            if filas:
                num_columnas = len(filas[0].find_all(['td', 'th']))
            
            tablas_detectadas.append({
                'indice': i,
                'tipo_estado': tipo_estado,
                'num_filas': num_filas,
                'num_columnas': num_columnas,
                'texto_contexto': texto_previo[:100]  # Primeros 100 caracteres
            })
        
        return tablas_detectadas
    
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
                            
                            # Mostrar categorías encontradas
                            if resumen['categorias_encontradas']:
                                st.write("**Categorías financieras detectadas:**")
                                st.write(", ".join(resumen['categorias_encontradas']))
                            
                            # Mostrar años disponibles
                            if resumen['años_disponibles']:
                                st.write("**Años disponibles:**")
                                st.write(", ".join(resumen['años_disponibles']))
                        
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
            tab1, tab2, tab3, tab4 = st.tabs(["Resumen General", "Datos por Categoría", "Comparativo", "Datos Detallados"])
            
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
                        'Categorías': len(resultado['resumen']['categorias_encontradas'])
                    })
                
                df_resumen = pd.DataFrame(datos_resumen)
                st.dataframe(df_resumen, use_container_width=True)
            
            with tab2:
                st.subheader("Datos organizados por categoría financiera")
                
                for resultado in resultados_analisis:
                    st.write(f"### {resultado['archivo']}")
                    
                    datos = resultado['datos']
                    
                    # Mostrar cada categoría
                    for categoria in ['activos', 'pasivos', 'patrimonio', 'estado_resultados']:
                        if categoria in datos and datos[categoria]:
                            st.write(f"**{categoria.replace('_', ' ').title()}:**")
                            
                            categoria_df = []
                            for item in datos[categoria]:
                                fila = {'Cuenta': item['cuenta']}
                                for i, valor in enumerate(item['valores']):
                                    fila[f'Valor_{i+1}'] = valor['texto']
                                categoria_df.append(fila)
                            
                            if categoria_df:
                                df_categoria = pd.DataFrame(categoria_df)
                                st.dataframe(df_categoria, use_container_width=True)
            
            with tab3:
                st.subheader("Análisis comparativo entre períodos")
                
                if len(resultados_analisis) > 1:
                    st.info("Comparación disponible entre múltiples archivos")
                    
                    # Aquí se podría implementar lógica de comparación
                    empresas = set([r['resumen']['empresa'] for r in resultados_analisis])
                    años = set([r['resumen']['año_reporte'] for r in resultados_analisis])
                    
                    st.write(f"**Empresas analizadas:** {len(empresas)}")
                    st.write(f"**Años cubiertos:** {sorted(años, reverse=True)}")
                
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
                
                # Agregar datos por categoría
                for categoria in ['activos', 'pasivos', 'patrimonio', 'estado_resultados']:
                    if categoria in resultado['datos']:
                        for item in resultado['datos'][categoria]:
                            row = base_row.copy()
                            row['categoria'] = categoria
                            row['cuenta'] = item['cuenta']
                            
                            # Agregar valores
                            for i, valor in enumerate(item['valores']):
                                row[f'valor_{i+1}'] = valor['numero']
                                row[f'valor_texto_{i+1}'] = valor['texto']
                            
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
        
        # Mostrar información sobre el diccionario de palabras clave
        with st.expander("📚 Ver diccionario de palabras clave utilizadas"):
            st.write("El sistema utiliza las siguientes palabras clave para identificar datos importantes:")
            
            for categoria, palabras in analizador.palabras_clave.items():
                st.write(f"**{categoria.replace('_', ' ').title()}:**")
                st.write(", ".join(palabras))
                st.write("")

if __name__ == "__main__":
    main()