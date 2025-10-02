"""
Extractor Mejorado de Estados Financieros
==========================================
Extrae de forma precisa los 4 bloques principales de estados financieros desde archivos HTML,
con detección automática de formato según el año (≤2009 vs ≥2010).

Características:
- Detección automática de inicio y fin de cada bloque
- Conversión automática de texto a números (formato latino: 1,234.56 y negativos en paréntesis)
- Preservación de la estructura jerárquica (totales, subtotales, cuentas)
- Validación de equilibrio contable
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup, Tag


class ExtractorEstadosFinancieros:
    """Extractor especializado para estados financieros en formato HTML"""
    
    # Nombres de estados por año
    ESTADOS_PRE_2010 = {
        'balance': 'BALANCE GENERAL',
        'resultados': 'ESTADO DE GANANCIAS Y PERDIDAS',
        'patrimonio': 'ESTADO DE CAMBIOS EN EL PATRIMONIO NETO',
        'flujo': 'ESTADO DE FLUJO DE EFECTIVO'
    }
    
    ESTADOS_POST_2010 = {
        'balance': 'ESTADO DE SITUACION FINANCIERA',
        'resultados': 'ESTADO DE RESULTADOS',
        'patrimonio': 'ESTADO DE CAMBIOS EN EL PATRIMONIO NETO',
        'flujo': 'ESTADO DE FLUJO DE EFECTIVO',
        'integrales': 'ESTADO DE RESULTADOS INTEGRALES'
    }
    
    def __init__(self):
        self.año_documento = None
        self.estados_config = None
    
    def extraer_todos_estados(self, html_content: str, año_documento: int = None) -> Dict[str, Any]:
        """
        Extrae todos los estados financieros del documento HTML
        
        Args:
            html_content: Contenido HTML del archivo
            año_documento: Año del documento (opcional, se detecta automáticamente)
        
        Returns:
            Dict con todos los estados extraídos y metadatos
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extraer metadatos (empresa, tipo, periodo)
        metadatos = self._extraer_metadatos(soup)
        
        # Detectar año si no se proporciona
        if año_documento is None:
            año_documento = self._detectar_año(soup)
        
        self.año_documento = año_documento
        self.estados_config = self.ESTADOS_PRE_2010 if año_documento <= 2009 else self.ESTADOS_POST_2010
        
        print(f"📅 Año detectado: {año_documento}")
        print(f"📋 Formato: {'Pre-2010 (PCG)' if año_documento <= 2009 else 'Post-2010 (NIIF)'}")
        if metadatos.get('empresa'):
            print(f"🏢 Empresa: {metadatos['empresa']}")
        if metadatos.get('tipo'):
            print(f"📑 Tipo: {metadatos['tipo']}")
        
        # Extraer cada estado
        resultados = {
            'año_documento': año_documento,
            'formato': 'pre_2010' if año_documento <= 2009 else 'post_2010',
            'metadatos': metadatos,
            'estados': {},
            'errores': [],
            'validaciones': {}
        }
        
        # Extraer estado de situación financiera / balance general
        balance = self._extraer_estado_por_nombre(soup, self.estados_config['balance'])
        if balance:
            resultados['estados']['balance'] = balance
            print(f"✅ {self.estados_config['balance']}: {len(balance['cuentas'])} cuentas")
        else:
            resultados['errores'].append(f"No se encontró {self.estados_config['balance']}")
            print(f"❌ No se encontró {self.estados_config['balance']}")
        
        # Extraer estado de resultados
        resultados_estado = self._extraer_estado_por_nombre(soup, self.estados_config['resultados'])
        if resultados_estado:
            resultados['estados']['resultados'] = resultados_estado
            print(f"✅ {self.estados_config['resultados']}: {len(resultados_estado['cuentas'])} cuentas")
        else:
            resultados['errores'].append(f"No se encontró {self.estados_config['resultados']}")
            print(f"❌ No se encontró {self.estados_config['resultados']}")
        
        # Extraer estado de cambios en patrimonio
        patrimonio = self._extraer_estado_por_nombre(soup, self.estados_config['patrimonio'])
        if patrimonio:
            resultados['estados']['patrimonio'] = patrimonio
            print(f"✅ {self.estados_config['patrimonio']}: {len(patrimonio['cuentas'])} cuentas")
        else:
            resultados['errores'].append(f"No se encontró {self.estados_config['patrimonio']}")
            print(f"❌ No se encontró {self.estados_config['patrimonio']}")
        
        # Extraer estado de flujo de efectivo
        flujo = self._extraer_estado_por_nombre(soup, self.estados_config['flujo'])
        if flujo:
            resultados['estados']['flujo'] = flujo
            print(f"✅ {self.estados_config['flujo']}: {len(flujo['cuentas'])} cuentas")
        else:
            resultados['errores'].append(f"No se encontró {self.estados_config['flujo']}")
            print(f"❌ No se encontró {self.estados_config['flujo']}")
        
        # Extraer estado de resultados integrales (solo post-2010)
        if año_documento >= 2010:
            integrales = self._extraer_estado_por_nombre(soup, self.estados_config['integrales'])
            if integrales:
                resultados['estados']['integrales'] = integrales
                print(f"✅ {self.estados_config['integrales']}: {len(integrales['cuentas'])} cuentas")
        
        # Validar equilibrio contable
        if balance:
            validacion = self._validar_equilibrio_contable(balance)
            resultados['validaciones']['equilibrio_contable'] = validacion
            if validacion['es_valido']:
                print(f"✅ Equilibrio contable OK: Activos = Pasivos + Patrimonio")
            else:
                print(f"⚠️ Diferencia en equilibrio: {validacion['diferencia']}")
        
        return resultados
    
    def _extraer_estado_por_nombre(self, soup: BeautifulSoup, nombre_estado: str) -> Optional[Dict]:
        """
        Extrae un estado financiero específico buscando por su nombre exacto
        
        Args:
            soup: BeautifulSoup object
            nombre_estado: Nombre exacto del estado a buscar
        
        Returns:
            Dict con la estructura del estado o None si no se encuentra
        """
        # Buscar el span con el nombre del estado (case insensitive y flexible con espacios)
        estado_span = None
        nombre_normalizado = re.sub(r'\s+', ' ', nombre_estado.strip().upper())
        
        for span in soup.find_all('span', style=re.compile(r'font-weight:bold')):
            texto_span = re.sub(r'\s+', ' ', span.get_text(strip=True).upper())
            if texto_span == nombre_normalizado:
                estado_span = span
                break
        
        if not estado_span:
            # Segundo intento: búsqueda más flexible
            for span in soup.find_all('span'):
                if 'font-weight:bold' in str(span.get('style', '')):
                    texto_span = re.sub(r'\s+', ' ', span.get_text(strip=True).upper())
                    if nombre_normalizado in texto_span or texto_span in nombre_normalizado:
                        estado_span = span
                        break
        
        if not estado_span:
            return None
        
        # Buscar la tabla siguiente
        tabla = estado_span.find_next('table')
        if not tabla:
            return None
        
        # Extraer datos de la tabla
        return self._extraer_datos_tabla(tabla, nombre_estado)
    
    def _extraer_datos_tabla(self, tabla: Tag, nombre_estado: str) -> Dict:
        """
        Extrae todos los datos de una tabla de estado financiero
        
        Args:
            tabla: Tag de BeautifulSoup con la tabla
            nombre_estado: Nombre del estado para referencia
        
        Returns:
            Dict con estructura completa del estado
        """
        # ✨ NUEVO: Para Estado de Cambios en Patrimonio, usar extracción especializada
        if 'PATRIMONIO' in nombre_estado.upper() and 'CAMBIOS' in nombre_estado.upper():
            return self._extraer_patrimonio_simplificado(tabla, nombre_estado)
        
        filas = tabla.find_all('tr')
        
        if not filas:
            return {'nombre': nombre_estado, 'años': [], 'cuentas': []}
        
        # Primera fila contiene los headers
        header_fila = filas[0]
        headers = [th.get_text(strip=True) for th in header_fila.find_all('th')]
        
        # Detectar columnas de años (son números de 4 dígitos)
        años = []
        columnas_años = {}  # {año: índice_columna}
        for i, header in enumerate(headers):
            match = re.search(r'\b(20\d{2}|19\d{2})\b', header)
            if match:
                año = int(match.group(1))
                años.append(año)
                columnas_años[año] = i
        
        # Si no se encuentran años en headers, buscar en la segunda fila
        if not años and len(filas) > 1:
            segunda_fila = filas[1]
            celdas = segunda_fila.find_all('td')
            for i, celda in enumerate(celdas):
                texto = celda.get_text(strip=True)
                match = re.search(r'\b(20\d{2}|19\d{2})\b', texto)
                if match:
                    año = int(match.group(1))
                    if año not in años:
                        años.append(año)
                        columnas_años[año] = i
        
        # Extraer cuentas (filas de datos)
        cuentas = []
        for i, fila in enumerate(filas[1:], start=1):  # Saltar header
            celdas = fila.find_all('td')
            if not celdas or len(celdas) < 2:
                continue
            
            # Primera celda es el nombre de la cuenta
            nombre_cuenta = celdas[0].get_text(strip=True)
            if not nombre_cuenta:
                continue
            
            # Detectar si es un total/subtotal (tiene class="pinta")
            es_total = 'pinta' in celdas[0].get('class', [])
            
            # Segunda celda es NOTA (generalmente)
            nota = celdas[1].get_text(strip=True) if len(celdas) > 1 else ''
            
            # Extraer valores por año
            valores = {}
            for año, idx in columnas_años.items():
                if idx < len(celdas):
                    texto_valor = celdas[idx].get_text(strip=True)
                    valor_numerico = self._convertir_a_numero(texto_valor)
                    valores[año] = valor_numerico
            
            # Solo agregar si tiene valores
            if valores:
                cuenta_info = {
                    'nombre': nombre_cuenta,
                    'nota': nota,
                    'es_total': es_total,
                    'valores': valores,
                    'fila': i
                }
                cuentas.append(cuenta_info)
        
        return {
            'nombre': nombre_estado,
            'años': sorted(años, reverse=True),  # Más reciente primero
            'cuentas': cuentas,
            'total_cuentas': len(cuentas)
        }
    
    def _extraer_patrimonio_simplificado(self, tabla: Tag, nombre_estado: str) -> Dict:
        """
        Extrae Estado de Cambios en el Patrimonio mostrando solo 3 columnas:
        - CCUENTA (código)
        - Cuenta (descripción)
        - Total Patrimonio (última columna con valores consolidados)
        
        Args:
            tabla: Tag de BeautifulSoup con la tabla
            nombre_estado: Nombre del estado
        
        Returns:
            Dict con estructura simplificada del patrimonio
        """
        filas = tabla.find_all('tr')
        
        if not filas:
            return {'nombre': nombre_estado, 'años': [], 'cuentas': []}
        
        # Analizar header para encontrar columnas
        header_fila = filas[0]
        headers = [th.get_text(strip=True) for th in header_fila.find_all('th')]
        
        # Identificar índices de columnas
        idx_ccuenta = None
        idx_cuenta = None
        idx_total_patrimonio = None
        
        for i, header in enumerate(headers):
            header_upper = header.upper()
            if 'CCUENTA' in header_upper:
                idx_ccuenta = i
            elif header_upper == 'CUENTA' or 'CUENTA' in header_upper and len(header) < 15:
                idx_cuenta = i
            elif 'TOTAL' in header_upper and 'PATRIMONIO' in header_upper:
                idx_total_patrimonio = i
        
        # Si no se encontró "Total Patrimonio", usar la última columna
        if idx_total_patrimonio is None:
            idx_total_patrimonio = len(headers) - 1
        
        # Por defecto, si no se encuentran, usar posiciones estándar
        if idx_ccuenta is None:
            idx_ccuenta = 0
        if idx_cuenta is None:
            idx_cuenta = 1
        
        # Detectar año del documento (el reporte solo tiene 1 año en patrimonio)
        año_doc = self.año_documento if self.año_documento else 2024
        
        # Extraer datos de las filas
        cuentas = []
        for i, fila in enumerate(filas[1:], start=1):
            celdas = fila.find_all('td')
            if not celdas or len(celdas) < 3:
                continue
            
            # Extraer CCUENTA, Cuenta y Total Patrimonio
            ccuenta = celdas[idx_ccuenta].get_text(strip=True) if idx_ccuenta < len(celdas) else ''
            cuenta = celdas[idx_cuenta].get_text(strip=True) if idx_cuenta < len(celdas) else ''
            valor_texto = celdas[idx_total_patrimonio].get_text(strip=True) if idx_total_patrimonio < len(celdas) else '0'
            
            if not ccuenta and not cuenta:
                continue
            
            # Convertir valor a número
            valor_numerico = self._convertir_a_numero(valor_texto)
            
            # Detectar si es total/subtotal
            es_total = 'pinta' in celdas[0].get('class', []) or 'SALDOS' in cuenta.upper() or 'TOTAL' in cuenta.upper()
            
            cuenta_info = {
                'ccuenta': ccuenta,
                'nombre': cuenta,
                'es_total': es_total,
                'valores': {año_doc: valor_numerico},  # Solo tiene el año del documento
                'fila': i
            }
            cuentas.append(cuenta_info)
        
        return {
            'nombre': nombre_estado,
            'años': [año_doc],  # Solo el año del documento
            'cuentas': cuentas,
            'total_cuentas': len(cuentas),
            'columnas_especiales': ['CCUENTA', 'Cuenta', 'Total Patrimonio']  # Metadato
        }
    
    def _convertir_a_numero(self, texto: str) -> float:
        """
        Convierte texto a número manejando formato latino y negativos
        
        Formatos soportados:
        - "1,234.56" → 1234.56
        - "(1,234)" → -1234.0
        - "-1,234" → -1234.0
        - "1,234" → 1234.0
        - "0" → 0.0
        - "" → 0.0
        - "&nbsp;" → 0.0
        
        Args:
            texto: String con el número
        
        Returns:
            float con el valor numérico
        """
        if not texto or texto.strip() == '' or texto == '&nbsp;':
            return 0.0
        
        texto_limpio = texto.strip()
        
        # Detectar negativo entre paréntesis
        es_negativo = False
        if texto_limpio.startswith('(') and texto_limpio.endswith(')'):
            es_negativo = True
            texto_limpio = texto_limpio[1:-1]
        
        # Detectar signo negativo
        if texto_limpio.startswith('-'):
            es_negativo = True
            texto_limpio = texto_limpio[1:]
        
        # Remover caracteres no numéricos excepto comas, puntos
        texto_limpio = re.sub(r'[^\d,.]', '', texto_limpio)
        
        if not texto_limpio:
            return 0.0
        
        try:
            # Formato latino: comas = miles, punto = decimal
            # Remover comas (separadores de miles)
            texto_limpio = texto_limpio.replace(',', '')
            
            # Convertir a float
            valor = float(texto_limpio)
            
            return -valor if es_negativo else valor
            
        except (ValueError, TypeError):
            return 0.0
    
    def _detectar_año(self, soup: BeautifulSoup) -> int:
        """
        Detecta el año del documento desde los metadatos del HTML
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            int con el año detectado (default: 2020)
        """
        # Obtener el texto completo del documento
        texto_completo = soup.get_text()
        
        # Buscar patrón "Año: XXXX" (case insensitive)
        match = re.search(r'año:\s*(\d{4})', texto_completo, re.IGNORECASE)
        if match:
            año = int(match.group(1))
            # Validar que no sea el año de generación del reporte (ej: 2025)
            if año < 2025:
                return año
        
        # Buscar patrón "A�o: XXXX" (encoding issue - case insensitive)
        match = re.search(r'a[ñn�]o:\s*(\d{4})', texto_completo, re.IGNORECASE)
        if match:
            año = int(match.group(1))
            if año < 2025:
                return año
        
        # Buscar en las primeras 500 caracteres (donde suele estar la metadata)
        texto_inicio = texto_completo[:500]
        años_inicio = re.findall(r'\b(20\d{2}|19\d{2})\b', texto_inicio)
        if años_inicio:
            # Filtrar el año de generación (suele ser 2025)
            años_validos = [int(a) for a in años_inicio if int(a) < 2025]
            if años_validos:
                return max(años_validos)
        
        # Buscar años en todo el documento como último recurso
        años_encontrados = re.findall(r'\b(20\d{2}|19\d{2})\b', texto_completo)
        if años_encontrados:
            años_unicos = sorted(set(int(a) for a in años_encontrados if int(a) < 2025), reverse=True)
            if años_unicos:
                return años_unicos[0]  # Retornar el más reciente válido
        
        return 2020  # Default
    
    def _extraer_metadatos(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extrae metadatos del documento (empresa, tipo, periodo)
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            Dict con metadatos extraídos
        """
        metadatos = {
            'empresa': None,
            'tipo': None,
            'periodo': None
        }
        
        # Buscar en divs específicos primero (formato nuevo)
        divs = soup.find_all('div')
        for div in divs:
            texto = div.get_text(strip=True)
            
            # Buscar Empresa (con manejo de encoding issues)
            if texto.startswith('Empresa:') or re.match(r'^Empresa:\s*', texto):
                empresa = re.sub(r'^Empresa:\s*', '', texto, flags=re.IGNORECASE).strip()
                if empresa:
                    # Limpiar caracteres de encoding mal formados comunes
                    empresa = self._limpiar_encoding(empresa)
                    metadatos['empresa'] = empresa
            
            # Buscar Tipo
            elif texto.startswith('Tipo:') or re.match(r'^Tipo:\s*', texto):
                tipo = re.sub(r'^Tipo:\s*', '', texto, flags=re.IGNORECASE).strip()
                if tipo:
                    metadatos['tipo'] = tipo
            
            # Buscar Periodo
            elif texto.startswith('Periodo:') or texto.startswith('Per�odo:') or re.match(r'^Per[ií�]odo:\s*', texto):
                periodo = re.sub(r'^Per[ií�]odo:\s*', '', texto, flags=re.IGNORECASE).strip()
                if periodo:
                    metadatos['periodo'] = periodo
        
        # Si no se encontró, buscar en el texto completo con patrones más amplios
        texto_completo = soup.get_text()
        
        if not metadatos['empresa']:
            # Buscar patrón "Empresa: NOMBRE"
            match = re.search(r'Empresa:\s*([^\n\r]+?)(?:\s*</div>|\s*Tipo:|\s*Per[ií�]odo:|\n|\r|$)', texto_completo, re.IGNORECASE)
            if match:
                empresa = match.group(1).strip()
                # Limpiar encoding issues
                empresa = self._limpiar_encoding(empresa)
                metadatos['empresa'] = empresa
            else:
                # Buscar nombres de empresas comunes (S.A.A., S.A., S.A.C., etc.)
                # Permitir � en la búsqueda para detectar COMPA�IA
                match = re.search(r'([A-ZÁÉÍÓÚÑ�][A-ZÁÉÍÓÚÑa-záéíóúñ�\s]+(?:S\.A\.A\.?|S\.A\.C\.?|S\.A\.?|S\.R\.L\.?))', texto_completo)
                if match:
                    empresa = match.group(1).strip()
                    empresa = self._limpiar_encoding(empresa)
                    metadatos['empresa'] = empresa
        
        if not metadatos['tipo']:
            # Buscar patrón "Tipo: TIPO"
            match = re.search(r'Tipo:\s*([^\n\r]+?)(?:\s*</div>|\s*Periodo:|\n|\r|$)', texto_completo, re.IGNORECASE)
            if match:
                metadatos['tipo'] = match.group(1).strip()
            else:
                # Inferir tipo basado en el contenido
                if 'consolidado' in texto_completo.lower():
                    metadatos['tipo'] = 'Consolidado'
                elif 'individual' in texto_completo.lower():
                    metadatos['tipo'] = 'Individual'
        
        if not metadatos['periodo']:
            # Buscar patrón "Periodo: PERIODO"
            match = re.search(r'Per[ií�]odo:\s*([^\n\r]+?)(?:\s*</div>|\s*Empresa:|\n|\r|$)', texto_completo, re.IGNORECASE)
            if match:
                metadatos['periodo'] = match.group(1).strip()
            else:
                # Inferir periodo común
                if 'anual' in texto_completo.lower():
                    metadatos['periodo'] = 'Anual'
                elif 'trimestral' in texto_completo.lower():
                    metadatos['periodo'] = 'Trimestral'
        
        return metadatos
    
    def _limpiar_encoding(self, texto: str) -> str:
        """
        Limpia problemas comunes de encoding en el texto
        
        Args:
            texto: String con posibles problemas de encoding
        
        Returns:
            String con encoding corregido
        """
        if not texto:
            return texto
        
        # Mapeo de palabras mal codificadas comunes
        reemplazos_palabras = {
            'COMPAIA': 'COMPAÑÍA',
            'Compaia': 'Compañía',
            'COMPA IA': 'COMPAÑÍA',
        }
        
        # Mapeo de caracteres mal codificados comunes
        reemplazos = {
            '�': 'Ñ',
            'Ã±': 'ñ',
            'Ã‰': 'É',
            'Ã': 'Í',
            'Ã"': 'Ó',
            'Ãš': 'Ú',
            'Ã': 'Á',
            'Â': '',  # Remover caracteres extras
        }
        
        texto_limpio = texto
        
        # Primero reemplazar palabras completas mal codificadas
        for mal_codificado, correcto in reemplazos_palabras.items():
            texto_limpio = texto_limpio.replace(mal_codificado, correcto)
        
        # Luego reemplazar caracteres individuales
        for mal_codificado, correcto in reemplazos.items():
            texto_limpio = texto_limpio.replace(mal_codificado, correcto)
        
        # Limpiar espacios múltiples
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        
        return texto_limpio
    
    def _validar_equilibrio_contable(self, balance: Dict) -> Dict:
        """
        Valida el equilibrio contable: Activos = Pasivos + Patrimonio
        
        Args:
            balance: Dict con el estado de situación financiera
        
        Returns:
            Dict con resultado de la validación
        """
        validacion = {
            'es_valido': False,
            'total_activos': 0.0,
            'total_pasivos': 0.0,
            'total_patrimonio': 0.0,
            'diferencia': 0.0,
            'tolerancia_porcentual': 0.01  # 1% de tolerancia
        }
        
        # Buscar totales (usar el primer año disponible)
        primer_año = None
        if balance['años']:
            primer_año = balance['años'][0]
        
        for cuenta in balance['cuentas']:
            nombre_upper = cuenta['nombre'].upper()
            
            # TOTAL ACTIVO (pero no TOTAL ACTIVOS CORRIENTES ni NO CORRIENTES ni "Y PATRIMONIO")
            if (('TOTAL ACTIVO' in nombre_upper or 'TOTAL DE ACTIVO' in nombre_upper) and 
                'PATRIMONIO' not in nombre_upper and 
                'CORRIENTE' not in nombre_upper and 
                'NO CORRIENTE' not in nombre_upper):
                if cuenta['valores'] and primer_año in cuenta['valores']:
                    validacion['total_activos'] = cuenta['valores'][primer_año]
            
            # TOTAL PASIVO (pero no TOTAL PASIVOS CORRIENTES ni NO CORRIENTES ni "Y PATRIMONIO")
            elif (('TOTAL PASIVO' in nombre_upper or 'TOTAL DE PASIVO' in nombre_upper) and 
                  'PATRIMONIO' not in nombre_upper and 
                  'CORRIENTE' not in nombre_upper and 
                  'NO CORRIENTE' not in nombre_upper and
                  ' Y ' not in nombre_upper):
                if cuenta['valores'] and primer_año in cuenta['valores']:
                    validacion['total_pasivos'] = cuenta['valores'][primer_año]
            
            # TOTAL PATRIMONIO (pero no "PASIVO Y PATRIMONIO")
            elif (('PATRIMONIO NETO' in nombre_upper or 
                   'PATRIMONIO TOTAL' in nombre_upper or
                   nombre_upper == 'TOTAL PATRIMONIO') and
                  'PASIVO' not in nombre_upper):
                if cuenta['valores'] and primer_año in cuenta['valores']:
                    validacion['total_patrimonio'] = cuenta['valores'][primer_año]
        
        # Calcular diferencia
        if validacion['total_activos'] > 0:
            suma_pasivo_patrimonio = validacion['total_pasivos'] + validacion['total_patrimonio']
            validacion['diferencia'] = abs(validacion['total_activos'] - suma_pasivo_patrimonio)
            
            # Calcular tolerancia basada en porcentaje del total de activos
            tolerancia = validacion['total_activos'] * validacion['tolerancia_porcentual']
            validacion['es_valido'] = validacion['diferencia'] <= tolerancia
        
        return validacion
    
    def exportar_a_dict_simple(self, resultados: Dict) -> Dict:
        """
        Convierte los resultados a un diccionario más simple para análisis
        
        Args:
            resultados: Dict completo de resultados
        
        Returns:
            Dict simplificado con solo datos esenciales
        """
        simple = {
            'año': resultados['año_documento'],
            'formato': resultados['formato']
        }
        
        for nombre_estado, datos_estado in resultados['estados'].items():
            simple[nombre_estado] = {
                'años': datos_estado['años'],
                'cuentas': {}
            }
            
            for cuenta in datos_estado['cuentas']:
                simple[nombre_estado]['cuentas'][cuenta['nombre']] = {
                    'es_total': cuenta['es_total'],
                    **cuenta['valores']
                }
        
        return simple


# Función auxiliar para uso rápido
def extraer_estados_desde_archivo(ruta_archivo: str) -> Dict:
    """
    Función auxiliar para extraer estados financieros desde un archivo HTML
    
    Args:
        ruta_archivo: Ruta al archivo HTML
    
    Returns:
        Dict con todos los estados extraídos
    """
    with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
    
    extractor = ExtractorEstadosFinancieros()
    return extractor.extraer_todos_estados(html_content)


if __name__ == "__main__":
    # Ejemplo de uso
    print("=== Extractor de Estados Financieros ===\n")
    
    # Ejemplo con archivo 2004
    print("📄 Analizando archivo 2004...")
    try:
        resultados_2004 = extraer_estados_desde_archivo(
            "ejemplos/ReporteDetalleInformacionFinanciero (6).html"
        )
        print(f"\n📊 Resumen:")
        print(f"   - Año: {resultados_2004['año_documento']}")
        print(f"   - Estados encontrados: {len(resultados_2004['estados'])}")
        print(f"   - Errores: {len(resultados_2004['errores'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Ejemplo con archivo 2024
    print("📄 Analizando archivo 2024...")
    try:
        resultados_2024 = extraer_estados_desde_archivo(
            "ejemplos/REPORTE DETALLE FINANCIERO 2024.html"
        )
        print(f"\n📊 Resumen:")
        print(f"   - Año: {resultados_2024['año_documento']}")
        print(f"   - Estados encontrados: {len(resultados_2024['estados'])}")
        print(f"   - Errores: {len(resultados_2024['errores'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
