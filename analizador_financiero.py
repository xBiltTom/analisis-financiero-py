import streamlit as st
import pandas as pd
import os
import tempfile
import shutil
from pathlib import Path
import re
from bs4 import BeautifulSoup
import numpy as np
# import chardet  # No se usa en el código
from typing import Dict, List, Tuple, Any
from analisis_vertical_horizontal import AnalisisVerticalHorizontal
from extractor_estados_mejorado import ExtractorEstadosFinancieros
from analisis_vertical_mejorado import AnalisisVerticalMejorado
from analisis_horizontal_mejorado import AnalisisHorizontalMejorado
from analisis_vertical_consolidado import AnalisisVerticalConsolidado
from analisis_horizontal_consolidado import AnalisisHorizontalConsolidado
from ratios_financieros import CalculadorRatiosFinancieros
from groq import Groq

# Configuración de la página
st.set_page_config(
    page_title="Analizador Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def analizar_ratios_con_ia(resultados_ratios: Dict[str, Any], empresa: str) -> str:
    """
    Analiza los ratios financieros usando el modelo de IA de Groq en 3 solicitudes especializadas
    
    Args:
        resultados_ratios: Diccionario con los ratios calculados
        empresa: Nombre de la empresa
    
    Returns:
        str: Análisis completo generado por la IA (combinación de 3 análisis)
    """
    try:
        # Inicializar cliente Groq con API key
        client = Groq(api_key="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")
        
        # Preparar datos de ratios
        años = sorted(resultados_ratios['años'])
        ratios_por_año = resultados_ratios['ratios_por_año']
        
        # ==================== SOLICITUD 1: LIQUIDEZ Y ENDEUDAMIENTO ====================
        prompt1 = f"""Eres un analista financiero experto. Analiza ÚNICAMENTE los ratios de LIQUIDEZ y ENDEUDAMIENTO de {empresa}.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**DATOS DE LIQUIDEZ Y ENDEUDAMIENTO:**
"""
        for año in años:
            ratios = ratios_por_año[año]
            prompt1 += f"\n**{año}:**\n"
            prompt1 += f"• Liquidez Corriente: {ratios.get('liquidez_corriente', 'N/A')}\n"
            prompt1 += f"• Prueba Ácida: {ratios.get('prueba_acida', 'N/A')}\n"
            prompt1 += f"• Razón Deuda Total: {ratios.get('razon_deuda_total', 'N/A')}\n"
            prompt1 += f"• Razón Deuda/Patrimonio: {ratios.get('razon_deuda_patrimonio', 'N/A')}\n"
        
        prompt1 += """
**INSTRUCCIONES:**
- Analiza SOLO liquidez y endeudamiento (NO menciones rentabilidad ni actividad)
- Sé específico con los números y proporciona análisis DETALLADO
- Identifica tendencias, alertas y explica sus causas probables
- Proporciona contexto comparativo entre años
- Máximo 15-18 líneas

**ESTRUCTURA:**
1. **LIQUIDEZ** (8-9 líneas): Analiza Liquidez Corriente y Prueba Ácida. ¿Puede pagar obligaciones a corto plazo? ¿Cómo ha evolucionado? ¿Qué significa cada cambio? ¿Es saludable para la industria?
2. **ENDEUDAMIENTO** (7-9 líneas): Analiza Razón Deuda Total y Deuda/Patrimonio. ¿Nivel de riesgo? ¿Apalancamiento adecuado? ¿Tendencia? ¿Cómo afecta la capacidad de endeudamiento futuro? ¿Alertas específicas?
"""
        
        # ==================== SOLICITUD 2: RENTABILIDAD Y ACTIVIDAD ====================
        prompt2 = f"""Eres un analista financiero experto. Analiza ÚNICAMENTE los ratios de RENTABILIDAD y ACTIVIDAD de {empresa}.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**DATOS DE RENTABILIDAD Y ACTIVIDAD:**
"""
        for año in años:
            ratios = ratios_por_año[año]
            prompt2 += f"\n**{año}:**\n"
            prompt2 += f"• Margen Neto: {ratios.get('margen_neto', 'N/A')}\n"
            prompt2 += f"• ROA: {ratios.get('roa', 'N/A')}\n"
            prompt2 += f"• ROE: {ratios.get('roe', 'N/A')}\n"
            prompt2 += f"• Rotación Activos Totales: {ratios.get('rotacion_activos_totales', 'N/A')}\n"
            prompt2 += f"• Rotación CxC: {ratios.get('rotacion_cuentas_cobrar', 'N/A')}\n"
            prompt2 += f"• Rotación Inventarios: {ratios.get('rotacion_inventarios', 'N/A')}\n"
        
        prompt2 += """
**INSTRUCCIONES:**
- Analiza SOLO rentabilidad y actividad (NO menciones liquidez ni endeudamiento)
- Sé específico con los números y proporciona análisis DETALLADO
- Identifica si genera valor para accionistas y explica por qué
- Compara entre años y explica cambios significativos
- Máximo 18-20 líneas

**ESTRUCTURA:**
1. **RENTABILIDAD** (9-10 líneas): Analiza Margen Neto, ROA y ROE. ¿Genera ganancias suficientes? ¿Cómo ha evolucionado cada indicador? ¿El retorno es adecuado para los accionistas? ¿Qué factores pueden estar influyendo? ¿Comparación con tendencias del sector?
2. **EFICIENCIA OPERATIVA** (9-10 líneas): Analiza rotaciones de activos, CxC e inventarios. ¿Uso eficiente de recursos? ¿Qué indican las rotaciones sobre la gestión operativa? ¿Problemas de cobranza o inventarios obsoletos? ¿Tendencia de mejora o deterioro?
"""
        
        # ==================== SOLICITUD 3: CONCLUSIÓN GENERAL ====================
        prompt3 = f"""Eres un analista financiero experto. Genera una CONCLUSIÓN GENERAL integradora sobre {empresa}.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**RESUMEN DE TODOS LOS RATIOS:**
"""
        for año in años:
            ratios = ratios_por_año[año]
            prompt3 += f"\n**{año}:** Liquidez={ratios.get('liquidez_corriente', 'N/A')}, Deuda={ratios.get('razon_deuda_total', 'N/A')}, ROE={ratios.get('roe', 'N/A')}, Rotación={ratios.get('rotacion_activos_totales', 'N/A')}\n"
        
        prompt3 += """
**INSTRUCCIONES:**
- Integra TODOS los aspectos: liquidez, endeudamiento, rentabilidad y eficiencia
- Identifica el PATRÓN GENERAL entre años con análisis PROFUNDO
- Evalúa salud financiera GLOBAL y perspectivas futuras
- Proporciona 3-4 RECOMENDACIONES específicas, accionables y priorizadas
- Máximo 15-18 líneas

**ESTRUCTURA:**
1. **DIAGNÓSTICO INTEGRAL** (6-7 líneas): ¿Cómo está la empresa en general? ¿Fortalezas principales? ¿Debilidades críticas? ¿Balance entre liquidez, rentabilidad y eficiencia? ¿Posición competitiva probable?
2. **TENDENCIA GLOBAL** (4-5 líneas): ¿Mejorando o deteriorándose? ¿Sostenible a mediano plazo? ¿Riesgos principales? ¿Oportunidades visibles?
3. **RECOMENDACIONES ESTRATÉGICAS** (5-6 líneas): 3-4 acciones concretas prioritarias con justificación breve. ¿Qué hacer primero? ¿Qué evitar?
"""
        
        # Realizar las 3 solicitudes
        analisis_partes = []
        
        # PARTE 1: Liquidez y Endeudamiento
        completion1 = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analista financiero experto en análisis de liquidez y endeudamiento. Proporciona análisis DETALLADOS y específicos centrados ÚNICAMENTE en estos aspectos. Explica causas, consecuencias y contexto."
                },
                {
                    "role": "user",
                    "content": prompt1
                }
            ],
            temperature=0.6,
            max_tokens=2500,
            top_p=0.9
        )
        analisis_partes.append(completion1.choices[0].message.content)
        
        # PARTE 2: Rentabilidad y Actividad
        completion2 = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analista financiero experto en rentabilidad y eficiencia operativa. Proporciona análisis DETALLADOS y específicos centrados ÚNICAMENTE en estos aspectos. Explica causas, impactos y comparaciones."
                },
                {
                    "role": "user",
                    "content": prompt2
                }
            ],
            temperature=0.6,
            max_tokens=2800,
            top_p=0.9
        )
        analisis_partes.append(completion2.choices[0].message.content)
        
        # PARTE 3: Conclusión General
        completion3 = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analista financiero senior que integra todos los aspectos financieros para dar un diagnóstico completo y recomendaciones estratégicas. Proporciona análisis PROFUNDO con visión holística y recomendaciones priorizadas."
                },
                {
                    "role": "user",
                    "content": prompt3
                }
            ],
            temperature=0.6,
            max_tokens=2500,
            top_p=0.9
        )
        analisis_partes.append(completion3.choices[0].message.content)
        
        # Combinar los 3 análisis
        analisis_completo = f"""# ANÁLISIS FINANCIERO INTEGRAL - {empresa}

## 📊 PARTE 1: ANÁLISIS DE LIQUIDEZ Y ENDEUDAMIENTO

{analisis_partes[0]}

---

## 💰 PARTE 2: ANÁLISIS DE RENTABILIDAD Y EFICIENCIA

{analisis_partes[1]}

---

## 🎯 PARTE 3: CONCLUSIÓN GENERAL Y RECOMENDACIONES

{analisis_partes[2]}

---

*Análisis generado mediante IA (OpenAI GPT-4o-mini via Groq) en 3 fases especializadas*
"""
        
        return analisis_completo
        
    except Exception as e:
        return f"❌ Error al generar análisis con IA: {str(e)}"

class AnalizadorFinanciero:
    def __init__(self):
        self.temp_dir = "temp"
        self.crear_directorio_temporal()
        self.palabras_clave = self.cargar_diccionario_palabras_clave()
        self.extractor_mejorado = ExtractorEstadosFinancieros()  # ✨ Nuevo extractor mejorado
        self.analizador_vertical = AnalisisVerticalMejorado()  # ✨ Nuevo analizador vertical
        self.analizador_horizontal = AnalisisHorizontalMejorado()  # ✨ Nuevo analizador horizontal
        self.consolidador_vertical = AnalisisVerticalConsolidado()  # ✨ Consolidador vertical
        self.consolidador_horizontal = AnalisisHorizontalConsolidado()  # ✨ Consolidador horizontal
        self.calculador_ratios = CalculadorRatiosFinancieros()  # ✨ Calculador de ratios financieros
        
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
    
    def extraer_datos_html(self, archivo_html: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extraer datos importantes del archivo HTML usando el EXTRACTOR MEJORADO
        
        ✨ NUEVO: Usa extractor_estados_mejorado.py para extracción precisa de bloques
        
        Returns:
            Tuple con (datos_legacy, resultados_extractor_mejorado)
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
            
            # Retornar AMBOS formatos
            return datos_extraidos, resultados_mejorados
            
        except Exception as e:
            st.error(f"❌ Error al extraer datos con extractor mejorado: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return {}, {}
    
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
                    # ✨ NUEVO: Para patrimonio, incluir CCUENTA si existe
                    if 'ccuenta' in cuenta:
                        cuenta_legacy = {
                            'ccuenta': cuenta.get('ccuenta', ''),
                            'cuenta': cuenta['nombre'],
                            'es_total': cuenta['es_total']
                        }
                    else:
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
                    'total_cuentas': estado_mejorado['total_cuentas'],
                    'columnas_especiales': estado_mejorado.get('columnas_especiales', None)  # ✨ NUEVO
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
            tiene_ccuenta = False  # ✨ NUEVO: Flag para patrimonio
            orden_cuentas = []  # ✨ NUEVO: Mantener orden de aparición
            
            # Procesar cada archivo
            for resultado in archivos_post_2010:
                datos_extraidos = resultado.get('datos', {})  # CORREGIDO: usar 'datos' no 'datos_extraidos'
                estados_financieros = datos_extraidos.get('estados_financieros', {})
                
                if nombre_estado in estados_financieros:
                    estado_datos = estados_financieros[nombre_estado]
                    
                    # ✨ NUEVO: Detectar si este estado tiene CCUENTA (Estado de Cambios en Patrimonio)
                    if estado_datos.get('columnas_especiales'):
                        tiene_ccuenta = True
                    
                    # Procesar cada cuenta del estado
                    for idx, item in enumerate(estado_datos.get('datos', [])):
                        # ✨ MEJORADO: Usar índice + nombre para evitar duplicados
                        nombre_cuenta = item.get('cuenta', 'Sin cuenta')
                        
                        # Para patrimonio, usar CCUENTA como identificador
                        if tiene_ccuenta and 'ccuenta' in item:
                            ccuenta = item.get('ccuenta', '')
                            clave_cuenta = f"{ccuenta}|{nombre_cuenta}"  # Usar CCUENTA|Cuenta como clave única
                        else:
                            # ✨ NUEVO: Usar índice + nombre para garantizar unicidad
                            clave_cuenta = f"{idx:04d}|{nombre_cuenta}"
                        
                        # Inicializar cuenta si no existe
                        if clave_cuenta not in cuentas_consolidadas:
                            if tiene_ccuenta:
                                cuentas_consolidadas[clave_cuenta] = {
                                    'ccuenta': item.get('ccuenta', ''),
                                    'cuenta': nombre_cuenta,
                                    'idx': idx  # ✨ NUEVO: Mantener orden
                                }
                            else:
                                cuentas_consolidadas[clave_cuenta] = {
                                    'cuenta': nombre_cuenta,
                                    'idx': idx  # ✨ NUEVO: Mantener orden
                                }
                            # Registrar orden de aparición solo la primera vez
                            if clave_cuenta not in orden_cuentas:
                                orden_cuentas.append(clave_cuenta)
                        
                        # Agregar valores por año (solo si no se ha procesado ese año antes)
                        for clave, valor in item.items():
                            if clave not in ['cuenta', 'ccuenta', 'es_total'] and isinstance(valor, dict):
                                # Extraer año y valor numérico
                                año_str = str(clave)
                                if año_str.isdigit():
                                    año = int(año_str)
                                    
                                    # Solo agregar si ese año no ha sido procesado para esta cuenta
                                    if año not in cuentas_consolidadas[clave_cuenta]:
                                        numero = valor.get('numero', 0)
                                        cuentas_consolidadas[clave_cuenta][año] = numero
                                        años_disponibles.add(año)
            
            # Convertir a DataFrame
            if cuentas_consolidadas:
                # ✨ MEJORADO: Crear lista de filas en el orden correcto
                filas_consolidadas = []
                
                # Iterar en el orden de aparición original
                for clave_cuenta in orden_cuentas:
                    if clave_cuenta in cuentas_consolidadas:
                        datos_cuenta = cuentas_consolidadas[clave_cuenta]
                        fila = {}
                        
                        # ✨ NUEVO: Para patrimonio, incluir CCUENTA
                        if tiene_ccuenta:
                            fila['CCUENTA'] = datos_cuenta.get('ccuenta', '')
                            fila['Cuenta'] = datos_cuenta.get('cuenta', '')
                        else:
                            fila['Cuenta'] = datos_cuenta.get('cuenta', '')
                        
                        # Agregar valores por año
                        for año in sorted(años_disponibles, reverse=True):
                            if año in datos_cuenta:
                                fila[año] = datos_cuenta[año]
                        
                        filas_consolidadas.append(fila)
                
                df = pd.DataFrame(filas_consolidadas)
                
                # ✨ NUEVO: Ordenar columnas según el tipo de estado
                if tiene_ccuenta:
                    # Para patrimonio: CCUENTA, Cuenta, luego años descendentes
                    columnas = ['CCUENTA', 'Cuenta']
                    años_cols = sorted([col for col in df.columns if col not in ['CCUENTA', 'Cuenta']], reverse=True)
                    columnas.extend(años_cols)
                else:
                    # Para otros estados: Cuenta, luego años descendentes
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
                        
                        # Extraer datos (retorna tupla: datos_legacy, resultados_extractor)
                        datos_extraidos, resultados_extractor = analizador.extraer_datos_html(archivo_html)
                        
                        if datos_extraidos:
                            st.success("✅ Extracción de datos completada")
                            
                            # Generar resumen
                            resumen = analizador.generar_resumen_analisis(datos_extraidos)
                            
                            # Realizar análisis horizontal si es POST-2010
                            analisis_horizontal = None
                            if datos_extraidos.get('año_documento', 0) >= 2010:
                                try:
                                    analisis_horizontal = analizador.analizador_horizontal.analizar_desde_extractor(resultados_extractor)
                                except Exception as e:
                                    st.warning(f"⚠️ No se pudo realizar análisis horizontal: {str(e)}")
                            
                            resultados_analisis.append({
                                'archivo': archivo.name,
                                'datos': datos_extraidos,
                                'datos_extractor': resultados_extractor,  # ✨ Formato extractor para análisis horizontal/vertical
                                'analisis_horizontal': analisis_horizontal,  # ✨ Análisis horizontal ya calculado
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
                                st.write(", ".join(str(año) for año in resumen['años_disponibles']))
                            
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
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                "Resumen General", 
                "Estados Financieros", 
                "Análisis Vertical", 
                "Análisis Horizontal",
                "Análisis Vertical Consolidado",
                "Análisis Horizontal Consolidado",
                "Vista Consolidada - Ratios", 
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
            
            with tab7:
                st.subheader("📊 Vista Consolidada Multi-Período - Ratios Financieros")
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
                    
                    # ===== SECCIÓN DE RATIOS FINANCIEROS =====
                    st.markdown("---")
                    st.subheader("📊 Ratios Financieros")
                    st.caption("Indicadores calculados desde el Estado de Situación Financiera")
                    
                    try:
                        # Extraer solo los datos_extractor de los archivos POST-2010
                        extractores_post_2010 = [
                            r.get('datos_extractor') 
                            for r in archivos_post_2010 
                            if r.get('datos_extractor') is not None
                        ]
                        
                        if len(extractores_post_2010) > 0:
                            with st.spinner("Calculando ratios financieros..."):
                                resultados_ratios = analizador.calculador_ratios.calcular_ratios_desde_extractor(extractores_post_2010)
                            
                            if 'error' not in resultados_ratios and resultados_ratios.get('ratios_por_año'):
                                st.success(f"✅ Ratios calculados para {len(resultados_ratios['años'])} años")
                                
                                # Crear DataFrame con los ratios
                                años_ratios = sorted(resultados_ratios['años'])
                                ratios_data = []
                                
                                for año in años_ratios:
                                    ratios_año = resultados_ratios['ratios_por_año'][año]
                                    ratios_data.append({
                                        'Año': año,
                                        'Liquidez Corriente': ratios_año.get('liquidez_corriente'),
                                        'Prueba Ácida': ratios_año.get('prueba_acida'),
                                        'Razón Deuda Total': ratios_año.get('razon_deuda_total'),
                                        'Razón Deuda/Patrimonio': ratios_año.get('razon_deuda_patrimonio'),
                                        'Margen Neto': ratios_año.get('margen_neto'),
                                        'ROA': ratios_año.get('roa'),
                                        'ROE': ratios_año.get('roe'),
                                        'Rotación Activos Totales': ratios_año.get('rotacion_activos_totales'),
                                        'Rotación CxC': ratios_año.get('rotacion_cuentas_cobrar'),
                                        'Rotación Inventarios': ratios_año.get('rotacion_inventarios')
                                    })
                                
                                df_ratios = pd.DataFrame(ratios_data)
                                
                                # Mostrar tabla de ratios
                                st.markdown("##### 📋 Tabla de Ratios")
                                df_ratios_display = df_ratios.copy()
                                df_ratios_display['Liquidez Corriente'] = df_ratios_display['Liquidez Corriente'].apply(
                                    lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Prueba Ácida'] = df_ratios_display['Prueba Ácida'].apply(
                                    lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Razón Deuda Total'] = df_ratios_display['Razón Deuda Total'].apply(
                                    lambda x: f"{x:.1%}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Razón Deuda/Patrimonio'] = df_ratios_display['Razón Deuda/Patrimonio'].apply(
                                    lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Margen Neto'] = df_ratios_display['Margen Neto'].apply(
                                    lambda x: f"{x:.3%}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['ROA'] = df_ratios_display['ROA'].apply(
                                    lambda x: f"{x:.3%}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['ROE'] = df_ratios_display['ROE'].apply(
                                    lambda x: f"{x:.3%}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Rotación Activos Totales'] = df_ratios_display['Rotación Activos Totales'].apply(
                                    lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Rotación CxC'] = df_ratios_display['Rotación CxC'].apply(
                                    lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A"
                                )
                                df_ratios_display['Rotación Inventarios'] = df_ratios_display['Rotación Inventarios'].apply(
                                    lambda x: f"{x:.3f}" if pd.notnull(x) else "N/A"
                                )
                                
                                st.dataframe(df_ratios_display, use_container_width=True)
                                
                                # Mostrar resumen estadístico
                                if resultados_ratios.get('resumen'):
                                    st.markdown("##### 📊 Resumen Estadístico")
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.markdown("**Ratios de Liquidez**")
                                        lc_stats = resultados_ratios['resumen'].get('liquidez_corriente', {})
                                        if lc_stats.get('promedio'):
                                            st.metric("Liquidez Corriente (Promedio)", f"{lc_stats['promedio']:.2f}")
                                            st.caption(f"Min: {lc_stats['min']:.2f} | Max: {lc_stats['max']:.2f}")
                                        
                                        pa_stats = resultados_ratios['resumen'].get('prueba_acida', {})
                                        if pa_stats.get('promedio'):
                                            st.metric("Prueba Ácida (Promedio)", f"{pa_stats['promedio']:.2f}")
                                            st.caption(f"Min: {pa_stats['min']:.2f} | Max: {pa_stats['max']:.2f}")
                                    
                                    with col2:
                                        st.markdown("**Ratios de Endeudamiento**")
                                        rdt_stats = resultados_ratios['resumen'].get('razon_deuda_total', {})
                                        if rdt_stats.get('promedio'):
                                            st.metric("Razón Deuda Total (Promedio)", f"{rdt_stats['promedio']:.1%}")
                                            st.caption(f"Min: {rdt_stats['min']:.1%} | Max: {rdt_stats['max']:.1%}")
                                        
                                        rdp_stats = resultados_ratios['resumen'].get('razon_deuda_patrimonio', {})
                                        if rdp_stats.get('promedio'):
                                            st.metric("Razón Deuda/Patrimonio (Promedio)", f"{rdp_stats['promedio']:.2f}")
                                            st.caption(f"Min: {rdp_stats['min']:.2f} | Max: {rdp_stats['max']:.2f}")
                                    
                                    with col3:
                                        st.markdown("**Ratios de Rentabilidad**")
                                        mn_stats = resultados_ratios['resumen'].get('margen_neto', {})
                                        if mn_stats.get('promedio'):
                                            st.metric("Margen Neto (Promedio)", f"{mn_stats['promedio']:.3%}")
                                            st.caption(f"Min: {mn_stats['min']:.3%} | Max: {mn_stats['max']:.3%}")
                                        
                                        roa_stats = resultados_ratios['resumen'].get('roa', {})
                                        if roa_stats.get('promedio'):
                                            st.metric("ROA (Promedio)", f"{roa_stats['promedio']:.3%}")
                                            st.caption(f"Min: {roa_stats['min']:.3%} | Max: {roa_stats['max']:.3%}")
                                        
                                        roe_stats = resultados_ratios['resumen'].get('roe', {})
                                        if roe_stats.get('promedio'):
                                            st.metric("ROE (Promedio)", f"{roe_stats['promedio']:.3%}")
                                            st.caption(f"Min: {roe_stats['min']:.3%} | Max: {roe_stats['max']:.3%}")
                                    
                                    with col4:
                                        st.markdown("**Ratios de Actividad**")
                                        rat_stats = resultados_ratios['resumen'].get('rotacion_activos_totales', {})
                                        if rat_stats.get('promedio'):
                                            st.metric("Rotación Activos (Promedio)", f"{rat_stats['promedio']:.3f}")
                                            st.caption(f"Min: {rat_stats['min']:.3f} | Max: {rat_stats['max']:.3f}")
                                        
                                        rcxc_stats = resultados_ratios['resumen'].get('rotacion_cuentas_cobrar', {})
                                        if rcxc_stats.get('promedio'):
                                            st.metric("Rotación CxC (Promedio)", f"{rcxc_stats['promedio']:.3f}")
                                            st.caption(f"Min: {rcxc_stats['min']:.3f} | Max: {rcxc_stats['max']:.3f}")
                                        
                                        ri_stats = resultados_ratios['resumen'].get('rotacion_inventarios', {})
                                        if ri_stats.get('promedio'):
                                            st.metric("Rotación Inventarios (Promedio)", f"{ri_stats['promedio']:.3f}")
                                            st.caption(f"Min: {ri_stats['min']:.3f} | Max: {ri_stats['max']:.3f}")
                                
                                # Generar y mostrar gráficos
                                st.markdown("---")
                                st.markdown("##### 📈 Gráficos de Tendencias")
                                
                                graficos_ratios = analizador.calculador_ratios.generar_graficos_ratios(resultados_ratios)
                                
                                if graficos_ratios:
                                    for i, fig in enumerate(graficos_ratios, 1):
                                        st.plotly_chart(fig, use_container_width=True)
                                
                                # ===== ANÁLISIS CON IA =====
                                st.markdown("---")
                                st.markdown("##### 🤖 Análisis Inteligente con IA")
                                st.caption("Análisis generado por IA en 3 fases especializadas (OpenAI GPT-4o-mini via Groq)")
                                
                                if st.button("🔍 Generar Análisis con IA (3 Fases)", key="btn_analisis_ia"):
                                    # Contenedor para el progreso
                                    progress_text = st.empty()
                                    progress_bar = st.progress(0)
                                    
                                    progress_text.text("⏳ Fase 1/3: Analizando Liquidez y Endeudamiento...")
                                    progress_bar.progress(0)
                                    
                                    # Generar análisis (internamente hace 3 solicitudes)
                                    analisis_ia = analizar_ratios_con_ia(resultados_ratios, empresa)
                                    
                                    progress_bar.progress(100)
                                    progress_text.text("✅ Análisis completado!")
                                    
                                    # Limpiar indicadores de progreso después de 1 segundo
                                    import time
                                    time.sleep(1)
                                    progress_text.empty()
                                    progress_bar.empty()
                                    
                                    # Mostrar el análisis en un expander
                                    with st.expander("📄 Ver Análisis Completo de IA (3 Fases)", expanded=True):
                                        st.markdown(analisis_ia)
                                    
                                    # Opción para descargar el análisis
                                    st.download_button(
                                        label="📥 Descargar Análisis de IA (TXT)",
                                        data=analisis_ia,
                                        file_name=f"analisis_ia_ratios_{empresa.replace(' ', '_')}.txt",
                                        mime="text/plain",
                                        key="download_analisis_ia"
                                    )
                                
                                # Botón de exportación
                                st.markdown("---")
                                if st.button("📥 Exportar Ratios a Excel", key="export_ratios"):
                                    archivo_salida = f"ratios_financieros_{empresa.replace(' ', '_')}.xlsx"
                                    analizador.calculador_ratios.exportar_ratios_excel(resultados_ratios, archivo_salida)
                                    st.success(f"✅ Ratios exportados a: {archivo_salida}")
                            
                            else:
                                st.warning("⚠️ No se pudieron calcular los ratios financieros")
                                if 'error' in resultados_ratios:
                                    st.error(resultados_ratios['error'])
                        else:
                            st.warning("⚠️ No hay datos disponibles para calcular ratios financieros")
                            st.info("Los ratios requieren archivos con datos del extractor mejorado")
                    
                    except Exception as e:
                        st.error(f"❌ Error al calcular ratios financieros: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            with tab2:
                st.subheader("📋 Estados Financieros")
                st.info("📊 Vista detallada de estados financieros (solo formato POST-2010 ≥2010)")
                
                try:
                    # Filtrar solo archivos POST-2010
                    archivos_post_2010 = [
                        r for r in resultados_analisis 
                        if r.get('datos', {}).get('año_documento', 0) >= 2010
                    ]
                    
                    if not archivos_post_2010:
                        st.warning("⚠️ No hay archivos del formato POST-2010 (≥2010) para mostrar estados financieros")
                        st.info("Los estados financieros solo se muestran para archivos de años 2010 en adelante")
                    else:
                        st.success(f"✅ {len(archivos_post_2010)} archivo(s) POST-2010 encontrado(s)")
                        
                        # Crear opciones del selector con formato "Empresa - Año"
                        opciones_selector = {}
                        for r in archivos_post_2010:
                            año_doc = r.get('datos', {}).get('año_documento', 'N/A')
                            empresa = r.get('datos', {}).get('metadatos', {}).get('empresa', 'No identificada')
                            etiqueta = f"{empresa} - {año_doc}"
                            opciones_selector[etiqueta] = r['archivo']
                        
                        # Selector de archivo con etiquetas de empresa-año
                        archivo_seleccionado_label = st.selectbox(
                            "Selecciona una empresa y año para ver estados financieros:",
                            list(opciones_selector.keys()),
                            key="selector_estados_financieros"
                        )
                        
                        # Obtener el archivo correspondiente
                        archivo_seleccionado = opciones_selector[archivo_seleccionado_label]
                        
                        # Obtener resultado seleccionado
                        resultado_sel = next(r for r in archivos_post_2010 if r['archivo'] == archivo_seleccionado)
                        
                        año_doc = resultado_sel['datos'].get('año_documento', 2020)
                        estados_financieros = resultado_sel['datos'].get('estados_financieros', {})
                        
                        if not estados_financieros:
                            st.warning("⚠️ No se detectaron estados financieros en este archivo")
                        else:
                            # Crear sub-tabs para cada estado financiero
                            tab_situacion, tab_resultados, tab_patrimonio, tab_flujo = st.tabs([
                                "📊 Estado de Situación Financiera",
                                "💰 Estado de Resultados",
                                "🏛️ Estado de Cambios en el Patrimonio",
                                "💵 Estado de Flujo de Efectivo"
                            ])
                            
                            # Tab: Estado de Situación Financiera
                            with tab_situacion:
                                estado_key = 'estado_situacion_financiera'
                                if estado_key in estados_financieros and estados_financieros[estado_key].get('datos'):
                                    info_estado = estados_financieros[estado_key]
                                    st.write(f"### {info_estado['nombre']}")
                                    
                                    # Convertir datos a DataFrame
                                    datos_estado = []
                                    for item in info_estado['datos']:
                                        fila = {'Cuenta': item.get('cuenta', 'Sin cuenta')}
                                        
                                        # Agregar solo las columnas numéricas (años)
                                        for clave, valor in item.items():
                                            if clave != 'cuenta':
                                                if isinstance(valor, dict):
                                                    numero_convertido = valor.get('numero', 0)
                                                    fila[clave] = numero_convertido
                                                else:
                                                    if clave.isdigit() or any(char.isdigit() for char in str(clave)):
                                                        fila[clave] = valor if valor else 0
                                        
                                        datos_estado.append(fila)
                                    
                                    if datos_estado:
                                        df_estado = pd.DataFrame(datos_estado)
                                        
                                        # Ordenar columnas: primero 'Cuenta', luego años en orden descendente
                                        columnas = ['Cuenta']
                                        años_cols = [col for col in df_estado.columns if col != 'Cuenta']
                                        años_cols_sorted = sorted(años_cols, reverse=True)
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
                                        st.write(f"**Total de cuentas:** {len(datos_estado)}")
                                    else:
                                        st.info("No se encontraron datos para este estado financiero")
                                else:
                                    st.info("📭 No hay datos disponibles para Estado de Situación Financiera")
                            
                            # Tab: Estado de Resultados
                            with tab_resultados:
                                estado_key = 'estado_resultados'
                                if estado_key in estados_financieros and estados_financieros[estado_key].get('datos'):
                                    info_estado = estados_financieros[estado_key]
                                    st.write(f"### {info_estado['nombre']}")
                                    
                                    # Convertir datos a DataFrame
                                    datos_estado = []
                                    for item in info_estado['datos']:
                                        fila = {'Cuenta': item.get('cuenta', 'Sin cuenta')}
                                        
                                        for clave, valor in item.items():
                                            if clave != 'cuenta':
                                                if isinstance(valor, dict):
                                                    numero_convertido = valor.get('numero', 0)
                                                    fila[clave] = numero_convertido
                                                else:
                                                    if clave.isdigit() or any(char.isdigit() for char in str(clave)):
                                                        fila[clave] = valor if valor else 0
                                        
                                        datos_estado.append(fila)
                                    
                                    if datos_estado:
                                        df_estado = pd.DataFrame(datos_estado)
                                        
                                        columnas = ['Cuenta']
                                        años_cols = [col for col in df_estado.columns if col != 'Cuenta']
                                        años_cols_sorted = sorted(años_cols, reverse=True)
                                        columnas.extend(años_cols_sorted)
                                        
                                        df_estado = df_estado[columnas]
                                        
                                        for col in df_estado.columns:
                                            if col != 'Cuenta':
                                                try:
                                                    df_estado[col] = df_estado[col].apply(
                                                        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else '-'
                                                    )
                                                except:
                                                    pass
                                        
                                        st.dataframe(df_estado, use_container_width=True)
                                        st.write(f"**Total de cuentas:** {len(datos_estado)}")
                                    else:
                                        st.info("No se encontraron datos para este estado financiero")
                                else:
                                    st.info("📭 No hay datos disponibles para Estado de Resultados")
                            
                            # Tab: Estado de Cambios en el Patrimonio
                            with tab_patrimonio:
                                estado_key = 'estado_cambios_patrimonio'
                                if estado_key in estados_financieros and estados_financieros[estado_key].get('datos'):
                                    info_estado = estados_financieros[estado_key]
                                    st.write(f"### {info_estado['nombre']}")
                                    
                                    # Convertir datos a DataFrame
                                    datos_estado = []
                                    for item in info_estado['datos']:
                                        fila = {'Cuenta': item.get('cuenta', 'Sin cuenta')}
                                        
                                        for clave, valor in item.items():
                                            if clave != 'cuenta':
                                                if isinstance(valor, dict):
                                                    numero_convertido = valor.get('numero', 0)
                                                    fila[clave] = numero_convertido
                                                else:
                                                    if clave.isdigit() or any(char.isdigit() for char in str(clave)):
                                                        fila[clave] = valor if valor else 0
                                        
                                        datos_estado.append(fila)
                                    
                                    if datos_estado:
                                        df_estado = pd.DataFrame(datos_estado)
                                        
                                        columnas = ['Cuenta']
                                        años_cols = [col for col in df_estado.columns if col != 'Cuenta']
                                        años_cols_sorted = sorted(años_cols, reverse=True)
                                        columnas.extend(años_cols_sorted)
                                        
                                        df_estado = df_estado[columnas]
                                        
                                        for col in df_estado.columns:
                                            if col != 'Cuenta':
                                                try:
                                                    df_estado[col] = df_estado[col].apply(
                                                        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else '-'
                                                    )
                                                except:
                                                    pass
                                        
                                        st.dataframe(df_estado, use_container_width=True)
                                        st.write(f"**Total de cuentas:** {len(datos_estado)}")
                                    else:
                                        st.info("No se encontraron datos para este estado financiero")
                                else:
                                    st.info("📭 No hay datos disponibles para Estado de Cambios en el Patrimonio")
                            
                            # Tab: Estado de Flujo de Efectivo
                            with tab_flujo:
                                estado_key = 'estado_flujo_efectivo'
                                if estado_key in estados_financieros and estados_financieros[estado_key].get('datos'):
                                    info_estado = estados_financieros[estado_key]
                                    st.write(f"### {info_estado['nombre']}")
                                    
                                    # Convertir datos a DataFrame
                                    datos_estado = []
                                    for item in info_estado['datos']:
                                        fila = {'Cuenta': item.get('cuenta', 'Sin cuenta')}
                                        
                                        for clave, valor in item.items():
                                            if clave != 'cuenta':
                                                if isinstance(valor, dict):
                                                    numero_convertido = valor.get('numero', 0)
                                                    fila[clave] = numero_convertido
                                                else:
                                                    if clave.isdigit() or any(char.isdigit() for char in str(clave)):
                                                        fila[clave] = valor if valor else 0
                                        
                                        datos_estado.append(fila)
                                    
                                    if datos_estado:
                                        df_estado = pd.DataFrame(datos_estado)
                                        
                                        columnas = ['Cuenta']
                                        años_cols = [col for col in df_estado.columns if col != 'Cuenta']
                                        años_cols_sorted = sorted(años_cols, reverse=True)
                                        columnas.extend(años_cols_sorted)
                                        
                                        df_estado = df_estado[columnas]
                                        
                                        for col in df_estado.columns:
                                            if col != 'Cuenta':
                                                try:
                                                    df_estado[col] = df_estado[col].apply(
                                                        lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x != 0 else '-'
                                                    )
                                                except:
                                                    pass
                                        
                                        st.dataframe(df_estado, use_container_width=True)
                                        st.write(f"**Total de cuentas:** {len(datos_estado)}")
                                    else:
                                        st.info("No se encontraron datos para este estado financiero")
                                else:
                                    st.info("📭 No hay datos disponibles para Estado de Flujo de Efectivo")
                
                except Exception as e:
                    st.error(f"❌ Error al mostrar estados financieros: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            
            with tab3:
                st.subheader("📊 Análisis Vertical Mejorado")
                
                try:
                    # Crear opciones del selector con "Empresa - Año"
                    opciones_selector = {}
                    for resultado in resultados_analisis:
                        año_doc = resultado.get('datos', {}).get('año_documento', 'N/A')
                        empresa = resultado.get('datos', {}).get('metadatos', {}).get('empresa', 'No identificada')
                        etiqueta = f"{empresa} - {año_doc}"
                        opciones_selector[etiqueta] = resultado['archivo']
                    
                    if not opciones_selector:
                        st.warning("⚠️ No hay archivos disponibles para análisis vertical")
                    else:
                        st.success(f"✅ {len(opciones_selector)} archivo(s) disponible(s)")
                        
                        # Selector de archivo
                        archivo_seleccionado_label = st.selectbox(
                            "Selecciona una empresa y año para análisis vertical:",
                            list(opciones_selector.keys()),
                            key="selector_vertical"
                        )
                        
                        # Obtener el archivo correspondiente
                        archivo_seleccionado = opciones_selector[archivo_seleccionado_label]
                        resultado = next(r for r in resultados_analisis if r['archivo'] == archivo_seleccionado)
                        
                        st.write(f"### 📄 {archivo_seleccionado_label}")
                        
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
                                    
                                    tab_idx += 1
                                
                                # Flujo de Efectivo
                                if 'flujo' in estados_analizados:
                                    with tabs_sub[tab_idx]:
                                        flujo_data = estados_analizados['flujo']
                                        st.write(f"#### 💵 {flujo_data['nombre_estado']}")
                                        st.write(f"**Año analizado:** {flujo_data['año_analisis']}")
                                        
                                        if flujo_data['cuentas_analizadas']:
                                            st.write("##### 📊 Análisis Vertical por Secciones")
                                            st.caption("*Cada cuenta como % de su base correspondiente (Operación, Inversión, Financiación)*")
                                            
                                            df_flujo = pd.DataFrame(flujo_data['cuentas_analizadas'])
                                            df_flujo['Valor'] = df_flujo['valor'].apply(lambda x: f"{x:,.0f}")
                                            df_flujo['% Vertical'] = df_flujo['analisis_vertical'].apply(lambda x: f"{x:.2f}%")
                                            
                                            df_mostrar_f = df_flujo[['cuenta', 'Valor', '% Vertical']].copy()
                                            df_mostrar_f.columns = ['Cuenta', 'Valor', '% de Base']
                                            
                                            st.dataframe(df_mostrar_f, use_container_width=True, height=400)
                        
                        else:
                            st.warning(f"❌ No se encontró el archivo HTML: {ruta_html}")
                    
                except Exception as e:
                    st.error(f"❌ Error en análisis vertical: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            
            with tab5:
                st.subheader("📊 Análisis Vertical Consolidado")
                st.info("🔄 Vista consolidada de análisis vertical de múltiples años (solo formato POST-2010 ≥2010)")
                
                try:
                    # Obtener todos los análisis verticales realizados
                    analisis_vertical_list = []
                    
                    for resultado in resultados_analisis:
                        año_doc = resultado.get('datos', {}).get('año_documento', 0)
                        if año_doc >= 2010:
                            # Extraer datos del extractor
                            datos_extractor = resultado.get('datos_extractor')
                            if datos_extractor:
                                # Realizar análisis vertical
                                analisis_vert = analizador.analizador_vertical.analizar_desde_extractor(datos_extractor)
                                analisis_vertical_list.append(analisis_vert)
                    
                    if not analisis_vertical_list:
                        st.warning("⚠️ No hay archivos del formato POST-2010 (≥2010) para análisis vertical consolidado")
                        st.info("Carga al menos 2 archivos POST-2010 para ver el análisis consolidado")
                    elif len(analisis_vertical_list) < 2:
                        st.warning("⚠️ Se necesitan al menos 2 archivos POST-2010 para consolidar")
                        st.info(f"Actualmente tienes {len(analisis_vertical_list)} archivo(s). Carga más para comparar.")
                    else:
                        st.success(f"✅ {len(analisis_vertical_list)} archivos POST-2010 listos para consolidar")
                        
                        # Realizar consolidación
                        with st.spinner("Consolidando análisis vertical..."):
                            consolidado = analizador.consolidador_vertical.consolidar_analisis_vertical(analisis_vertical_list)
                        
                        if not consolidado:
                            st.error("❌ No se pudo consolidar el análisis vertical")
                        else:
                            st.success("✅ Análisis vertical consolidado generado")
                            
                            # Mostrar información
                            años_consolidados = []
                            for av in analisis_vertical_list:
                                años_consolidados.append(av['año_documento'])
                            años_consolidados.sort(reverse=True)
                            
                            st.info(f"📅 Años consolidados: {', '.join(map(str, años_consolidados))}")
                            
                            # Tabs por estado financiero
                            estados_disponibles = list(consolidado.keys())
                            
                            if 'situacion_financiera_activos' in estados_disponibles or 'situacion_financiera_pasivos' in estados_disponibles:
                                tabs_estados = st.tabs([
                                    "📊 Situación Financiera",
                                    "💰 Estado de Resultados" if 'resultados' in estados_disponibles else None,
                                    "💵 Flujo de Efectivo" if 'flujo_efectivo' in estados_disponibles else None
                                ])
                                
                                # TAB: Situación Financiera
                                with tabs_estados[0]:
                                    st.write("#### Estado de Situación Financiera - Análisis Vertical Consolidado")
                                    
                                    # Sub-tabs para Activos y Pasivos
                                    sub_tabs = st.tabs(["📈 ACTIVOS", "📉 PASIVOS"])
                                    
                                    # ACTIVOS
                                    with sub_tabs[0]:
                                        if 'situacion_financiera_activos' in consolidado:
                                            df_activos = consolidado['situacion_financiera_activos']
                                            
                                            st.write(f"**Total de cuentas:** {len(df_activos)}")
                                            
                                            # Formatear DataFrame para visualización
                                            df_display = df_activos.copy()
                                            columnas_años = [col for col in df_display.columns if col != 'Cuenta']
                                            
                                            for col in columnas_años:
                                                df_display[col] = df_display[col].apply(
                                                    lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
                                                )
                                            
                                            st.dataframe(
                                                df_display,
                                                use_container_width=True,
                                                height=500
                                            )
                                            
                                            # Gráficos de tendencias
                                            st.divider()
                                            st.write("##### 📈 Gráficos de Tendencias")
                                            
                                            graficos = analizador.consolidador_vertical.generar_graficos_tendencias(
                                                df_activos,
                                                "Activos - Estado de Situación Financiera",
                                                top_n=10
                                            )
                                            
                                            if graficos and len(graficos) >= 3:
                                                # Mostrar gráfico de líneas (primer gráfico)
                                                st.plotly_chart(graficos[0], use_container_width=True)
                                                
                                                # Mostrar mapa de calor (segundo gráfico)
                                                st.plotly_chart(graficos[1], use_container_width=True)
                                            
                                            # Gráfico de barras de composición por año
                                            st.divider()
                                            st.write("##### 📊 Composición con años - Activos")
                                            
                                            # Buscar las filas específicas en el DataFrame con orden de prioridad
                                            # IMPORTANTE: Buscar primero las más específicas para evitar coincidencias incorrectas
                                            cuentas_buscar_orden = [
                                                ('Total Activos No Corrientes', ['TOTAL DE ACTIVOS NO CORRIENTES', 'TOTAL ACTIVOS NO CORRIENTES', 'TOTAL DE ACTIVO NO CORRIENTE', 'TOTAL ACTIVO NO CORRIENTE']),
                                                ('Total Activos Corrientes', ['TOTAL DE ACTIVOS CORRIENTES', 'TOTAL ACTIVOS CORRIENTES', 'TOTAL ACTIVO CORRIENTE']),
                                                ('TOTAL DE ACTIVOS', ['TOTAL DE ACTIVOS', 'TOTAL ACTIVOS', 'TOTAL ACTIVO'])
                                            ]
                                            
                                            datos_grafico = {}
                                            filas_usadas = set()  # Para evitar usar la misma fila dos veces
                                            
                                            for nombre_display, variantes in cuentas_buscar_orden:
                                                for idx, row in df_activos.iterrows():
                                                    if idx in filas_usadas:
                                                        continue
                                                    cuenta_upper = str(row['Cuenta']).strip().upper()
                                                    for variante in variantes:
                                                        if cuenta_upper == variante.upper():
                                                            datos_grafico[nombre_display] = row
                                                            filas_usadas.add(idx)
                                                            break
                                                    if nombre_display in datos_grafico:
                                                        break
                                            
                                            if len(datos_grafico) == 3 and len(columnas_años) > 0:
                                                import plotly.graph_objects as go
                                                
                                                fig = go.Figure()
                                                años_sorted = sorted(columnas_años, reverse=True)
                                                
                                                # Agregar las 3 barras por año
                                                for nombre, row in datos_grafico.items():
                                                    valores = [row[año] if pd.notnull(row[año]) else 0 for año in años_sorted]
                                                    fig.add_trace(go.Bar(
                                                        name=nombre,
                                                        x=[str(año) for año in años_sorted],
                                                        y=valores,
                                                        text=[f"{v:.1f}%" if v != 0 else "" for v in valores],
                                                        textposition='auto'
                                                    ))
                                                
                                                fig.update_layout(
                                                    title="Composición con años - Activos",
                                                    xaxis_title="Año",
                                                    yaxis_title="Análisis Vertical (%)",
                                                    barmode='group',
                                                    height=450,
                                                    showlegend=True,
                                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                                                )
                                                
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info(f"⚠️ No se encontraron todas las cuentas requeridas. Encontradas: {list(datos_grafico.keys())}")
                                        else:
                                            st.warning("No hay datos de activos consolidados")
                                    
                                    # PASIVOS
                                    with sub_tabs[1]:
                                        if 'situacion_financiera_pasivos' in consolidado:
                                            df_pasivos = consolidado['situacion_financiera_pasivos']
                                            
                                            st.write(f"**Total de cuentas:** {len(df_pasivos)}")
                                            
                                            # Formatear DataFrame
                                            df_display = df_pasivos.copy()
                                            columnas_años = [col for col in df_display.columns if col != 'Cuenta']
                                            
                                            for col in columnas_años:
                                                df_display[col] = df_display[col].apply(
                                                    lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
                                                )
                                            
                                            st.dataframe(
                                                df_display,
                                                use_container_width=True,
                                                height=500
                                            )
                                            
                                            # Gráficos de tendencias
                                            st.divider()
                                            st.write("##### 📈 Gráficos de Tendencias")
                                            
                                            graficos = analizador.consolidador_vertical.generar_graficos_tendencias(
                                                df_pasivos,
                                                "Pasivos - Estado de Situación Financiera",
                                                top_n=10
                                            )
                                            
                                            if graficos and len(graficos) >= 3:
                                                # Mostrar gráfico de líneas (primer gráfico)
                                                st.plotly_chart(graficos[0], use_container_width=True)
                                                
                                                # Mostrar mapa de calor (segundo gráfico)
                                                st.plotly_chart(graficos[1], use_container_width=True)
                                            
                                            # Gráfico de barras de composición por año
                                            st.divider()
                                            st.write("##### 📊 Composición con años - Pasivos")
                                            
                                            # Buscar las filas específicas en el DataFrame con orden de prioridad
                                            # IMPORTANTE: Buscar primero las más específicas para evitar coincidencias incorrectas
                                            cuentas_buscar_orden = [
                                                ('Total Pasivos No Corrientes', ['TOTAL DE PASIVOS NO CORRIENTES', 'TOTAL PASIVOS NO CORRIENTES', 'TOTAL DE PASIVO NO CORRIENTE', 'TOTAL PASIVO NO CORRIENTE']),
                                                ('Total Pasivos Corrientes', ['TOTAL DE PASIVOS CORRIENTES', 'TOTAL PASIVOS CORRIENTES', 'TOTAL PASIVO CORRIENTE']),
                                                ('Total Pasivos', ['TOTAL DE PASIVOS', 'TOTAL PASIVOS', 'TOTAL PASIVO'])
                                            ]
                                            
                                            datos_grafico = {}
                                            filas_usadas = set()  # Para evitar usar la misma fila dos veces
                                            
                                            for nombre_display, variantes in cuentas_buscar_orden:
                                                for idx, row in df_pasivos.iterrows():
                                                    if idx in filas_usadas:
                                                        continue
                                                    cuenta_upper = str(row['Cuenta']).strip().upper()
                                                    for variante in variantes:
                                                        if cuenta_upper == variante.upper():
                                                            datos_grafico[nombre_display] = row
                                                            filas_usadas.add(idx)
                                                            break
                                                    if nombre_display in datos_grafico:
                                                        break
                                            
                                            if len(datos_grafico) == 3 and len(columnas_años) > 0:
                                                import plotly.graph_objects as go
                                                
                                                fig = go.Figure()
                                                años_sorted = sorted(columnas_años, reverse=True)
                                                
                                                # Agregar las 3 barras por año
                                                for nombre, row in datos_grafico.items():
                                                    valores = [row[año] if pd.notnull(row[año]) else 0 for año in años_sorted]
                                                    fig.add_trace(go.Bar(
                                                        name=nombre,
                                                        x=[str(año) for año in años_sorted],
                                                        y=valores,
                                                        text=[f"{v:.1f}%" if v != 0 else "" for v in valores],
                                                        textposition='auto'
                                                    ))
                                                
                                                fig.update_layout(
                                                    title="Composición con años - Pasivos",
                                                    xaxis_title="Año",
                                                    yaxis_title="Análisis Vertical (%)",
                                                    barmode='group',
                                                    height=450,
                                                    showlegend=True,
                                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                                                )
                                                
                                                st.plotly_chart(fig, use_container_width=True)
                                            else:
                                                st.info(f"⚠️ No se encontraron todas las cuentas requeridas. Encontradas: {list(datos_grafico.keys())}")
                                        else:
                                            st.warning("No hay datos de pasivos consolidados")
                                
                                # TAB: Estado de Resultados
                                if 'resultados' in estados_disponibles:
                                    with tabs_estados[1]:
                                        st.write("#### Estado de Resultados - Análisis Vertical Consolidado")
                                        
                                        df_resultados = consolidado['resultados']
                                        st.write(f"**Total de cuentas:** {len(df_resultados)}")
                                        
                                        # Formatear DataFrame
                                        df_display = df_resultados.copy()
                                        columnas_años = [col for col in df_display.columns if col != 'Cuenta']
                                        
                                        for col in columnas_años:
                                            df_display[col] = df_display[col].apply(
                                                lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
                                            )
                                        
                                        st.dataframe(
                                            df_display,
                                            use_container_width=True,
                                            height=500
                                        )
                                        
                                        # Gráficos
                                        st.divider()
                                        st.write("##### 📈 Gráficos de Tendencias")
                                        
                                        graficos = analizador.consolidador_vertical.generar_graficos_tendencias(
                                            df_resultados,
                                            "Estado de Resultados",
                                            top_n=10
                                        )
                                        
                                        if graficos:
                                            for fig in graficos:
                                                st.plotly_chart(fig, use_container_width=True)
                                
                                # TAB: Flujo de Efectivo
                                if 'flujo_efectivo' in estados_disponibles:
                                    with tabs_estados[2]:
                                        st.write("#### Flujo de Efectivo - Análisis Vertical Consolidado")
                                        
                                        df_flujo = consolidado['flujo_efectivo']
                                        st.write(f"**Total de cuentas:** {len(df_flujo)}")
                                        
                                        # Formatear DataFrame
                                        df_display = df_flujo.copy()
                                        columnas_años = [col for col in df_display.columns if col != 'Cuenta']
                                        
                                        for col in columnas_años:
                                            df_display[col] = df_display[col].apply(
                                                lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
                                            )
                                        
                                        st.dataframe(
                                            df_display,
                                            use_container_width=True,
                                            height=500
                                        )
                            
                            # Botón de descarga Excel
                            st.divider()
                            if st.button("📥 Exportar Análisis Vertical Consolidado a Excel", key="btn_export_av_consolidado"):
                                archivo_salida = "analisis_vertical_consolidado.xlsx"
                                analizador.consolidador_vertical.exportar_consolidado_excel(consolidado, archivo_salida)
                                st.success(f"✅ Archivo exportado: {archivo_salida}")
                
                except Exception as e:
                    st.error(f"❌ Error en análisis vertical consolidado: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            
            with tab6:
                st.subheader("📊 Análisis Horizontal Consolidado")
                st.info("📈 Vista consolidada de variaciones interanuales (POST-2010 ≥2010)")
                
                try:
                    # Filtrar solo archivos POST-2010 con análisis horizontal
                    archivos_post_2010_ah = [
                        r for r in resultados_analisis 
                        if r.get('datos', {}).get('año_documento', 0) >= 2010 
                        and r.get('analisis_horizontal') is not None
                    ]
                    
                    if len(archivos_post_2010_ah) < 2:
                        st.warning("⚠️ Se necesitan al menos 2 archivos POST-2010 para consolidar análisis horizontal")
                        st.info("El análisis horizontal consolidado compara las variaciones de múltiples períodos")
                    else:
                        st.success(f"✅ {len(archivos_post_2010_ah)} archivos disponibles para consolidación")
                        
                        # Extraer análisis horizontal de cada archivo
                        analisis_horizontal_list = [r['analisis_horizontal'] for r in archivos_post_2010_ah]
                        
                        # Consolidar análisis horizontal
                        with st.spinner("Consolidando análisis horizontal..."):
                            consolidado_ah = analizador.consolidador_horizontal.consolidar_analisis_horizontal(
                                analisis_horizontal_list
                            )
                        
                        if not consolidado_ah:
                            st.warning("⚠️ No se pudo consolidar el análisis horizontal")
                        else:
                            st.success(f"✅ Consolidación completada: {len(consolidado_ah)} estados procesados")
                            
                            # Crear sub-tabs por estado
                            estados_disponibles = list(consolidado_ah.keys())
                            
                            if 'situacion_financiera' in estados_disponibles:
                                sub_tabs_ah = st.tabs([
                                    "💼 Situación Financiera",
                                    "📊 Estado de Resultados",
                                    "💰 Flujo de Efectivo"
                                ])
                                
                                # Tab Situación Financiera
                                with sub_tabs_ah[0]:
                                    if 'situacion_financiera' in consolidado_ah:
                                        st.markdown("#### Estado de Situación Financiera - Consolidado")
                                        df_sf = consolidado_ah['situacion_financiera']
                                        
                                        # Mostrar tabla
                                        st.dataframe(
                                            df_sf.style.format(
                                                {col: "{:+.2f}%" for col in df_sf.columns if col != 'Cuenta'},
                                                na_rep="N/A"
                                            ),
                                            use_container_width=True,
                                            height=400
                                        )
                                        
                                        st.markdown(f"**Total de cuentas:** {len(df_sf)}")
                                        
                                        # Gráficos (sin cascada, barras con colores por año)
                                        st.markdown("---")
                                        st.markdown("#### 📈 Gráficos de Tendencias")
                                        
                                        graficos_sf = analizador.consolidador_horizontal.generar_graficos_tendencias(
                                            df_sf,
                                            "Situación Financiera",
                                            top_n=10
                                        )
                                        
                                        # Mostrar solo los primeros 3 gráficos (sin cascada)
                                        for i, fig in enumerate(graficos_sf[:3], 1):
                                            st.plotly_chart(fig, use_container_width=True)
                                
                                # Tab Estado de Resultados
                                with sub_tabs_ah[1]:
                                    if 'resultados' in consolidado_ah:
                                        st.markdown("#### Estado de Resultados - Consolidado")
                                        df_res = consolidado_ah['resultados']
                                        
                                        st.dataframe(
                                            df_res.style.format(
                                                {col: "{:+.2f}%" for col in df_res.columns if col != 'Cuenta'},
                                                na_rep="N/A"
                                            ),
                                            use_container_width=True,
                                            height=400
                                        )
                                        
                                        st.markdown(f"**Total de cuentas:** {len(df_res)}")
                                        
                                        # Gráficos (solo líneas y heatmap, sin barras)
                                        st.markdown("---")
                                        st.markdown("#### 📈 Gráficos de Tendencias")
                                        
                                        graficos_res = analizador.consolidador_horizontal.generar_graficos_tendencias(
                                            df_res,
                                            "Estado de Resultados",
                                            top_n=10
                                        )
                                        
                                        # Mostrar solo los primeros 2 gráficos (líneas y heatmap)
                                        for i, fig in enumerate(graficos_res[:2], 1):
                                            st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.info("No hay datos de estado de resultados disponibles")
                                
                                # Tab Flujo de Efectivo
                                with sub_tabs_ah[2]:
                                    if 'flujo_efectivo' in consolidado_ah:
                                        st.markdown("#### Flujo de Efectivo - Consolidado")
                                        df_flujo = consolidado_ah['flujo_efectivo']
                                        
                                        st.dataframe(
                                            df_flujo.style.format(
                                                {col: "{:+.2f}%" for col in df_flujo.columns if col != 'Cuenta'},
                                                na_rep="N/A"
                                            ),
                                            use_container_width=True,
                                            height=400
                                        )
                                        
                                        st.markdown(f"**Total de cuentas:** {len(df_flujo)}")
                                        # No mostrar gráficos para Flujo de Efectivo
                                    else:
                                        st.info("No hay datos de flujo de efectivo disponibles")
                            
                            # Botón de exportación
                            st.markdown("---")
                            st.markdown("#### 💾 Exportar Consolidado")
                            
                            if st.button("📥 Descargar Excel - Análisis Horizontal Consolidado"):
                                archivo_salida = "analisis_horizontal_consolidado.xlsx"
                                analizador.consolidador_horizontal.exportar_consolidado_excel(
                                    consolidado_ah,
                                    archivo_salida
                                )
                                st.success(f"✅ Archivo exportado: {archivo_salida}")
                
                except Exception as e:
                    st.error(f"❌ Error en análisis horizontal consolidado: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            
            with tab4:
                st.subheader("📈 Análisis Horizontal Mejorado")
                st.info("📊 Análisis horizontal año a año (solo formato POST-2010 ≥2010)")
                
                try:
                    # Filtrar solo archivos POST-2010
                    archivos_post_2010 = [
                        r for r in resultados_analisis 
                        if r.get('datos', {}).get('año_documento', 0) >= 2010
                    ]
                    
                    if not archivos_post_2010:
                        st.warning("⚠️ No hay archivos del formato POST-2010 (≥2010) para análisis horizontal")
                        st.info("El análisis horizontal solo está disponible para archivos de años 2010 en adelante")
                    else:
                        st.success(f"✅ {len(archivos_post_2010)} archivo(s) POST-2010 encontrado(s)")
                        
                        # Crear opciones del selector con formato "Empresa - Año"
                        opciones_selector = {}
                        for r in archivos_post_2010:
                            año_doc = r.get('datos', {}).get('año_documento', 'N/A')
                            empresa = r.get('datos', {}).get('metadatos', {}).get('empresa', 'No identificada')
                            etiqueta = f"{empresa} - {año_doc}"
                            opciones_selector[etiqueta] = r['archivo']
                        
                        # Selector de archivo con etiquetas de empresa-año
                        archivo_seleccionado_label = st.selectbox(
                            "Selecciona una empresa y año para análisis horizontal:",
                            list(opciones_selector.keys()),
                            key="selector_horizontal"
                        )
                        
                        # Obtener el archivo correspondiente
                        archivo_seleccionado = opciones_selector[archivo_seleccionado_label]
                        
                        # Obtener resultado seleccionado
                        resultado_sel = next(r for r in archivos_post_2010 if r['archivo'] == archivo_seleccionado)
                        datos_extractor = resultado_sel.get('datos_extractor', {})
                        
                        if datos_extractor and datos_extractor.get('estados'):
                            # Realizar análisis horizontal
                            with st.spinner("Realizando análisis horizontal..."):
                                analisis_horizontal_resultados = analizador.analizador_horizontal.analizar_desde_extractor(datos_extractor)
                            
                            if 'error' in analisis_horizontal_resultados:
                                st.error(f"❌ {analisis_horizontal_resultados['error']}")
                            else:
                                st.success("✅ Análisis horizontal completado")
                                
                                # Mostrar información general
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Empresa", analisis_horizontal_resultados['empresa'])
                                with col2:
                                    st.metric("Año Documento", analisis_horizontal_resultados['año_documento'])
                                with col3:
                                    st.metric("Estados Analizados", len(analisis_horizontal_resultados['estados_analizados']))
                                
                                st.divider()
                                
                                # Tabs para cada estado financiero
                                estados_disponibles = list(analisis_horizontal_resultados['estados_analizados'].keys())
                                
                                if estados_disponibles:
                                    tabs_estados = st.tabs([
                                        "📊 Estado de Situación Financiera" if 'balance' in estados_disponibles else None,
                                        "💰 Estado de Resultados" if 'resultados' in estados_disponibles else None,
                                        "💵 Flujo de Efectivo" if 'flujo' in estados_disponibles else None
                                    ])
                                    
                                    # Estado de Situación Financiera
                                    if 'balance' in estados_disponibles:
                                        with tabs_estados[0]:
                                            balance_ah = analisis_horizontal_resultados['estados_analizados']['balance']
                                            
                                            st.write(f"**Año Base:** {balance_ah['año_base']} | **Año Actual:** {balance_ah['año_actual']}")
                                            st.write(f"**Total Cuentas:** {balance_ah['total_cuentas_analizadas']}")
                                            
                                            # Estadísticas
                                            col1, col2, col3, col4 = st.columns(4)
                                            stats = balance_ah['estadisticas']
                                            with col1:
                                                st.metric("✅ Aumentos", stats['variaciones_positivas'], delta="Positivo")
                                            with col2:
                                                st.metric("⬇️ Disminuciones", stats['variaciones_negativas'], delta="Negativo")
                                            with col3:
                                                st.metric("➖ Sin Cambio", stats['sin_variacion'])
                                            with col4:
                                                st.metric("⚠️ N/A", stats['no_calculables'])
                                            
                                            st.divider()
                                            
                                            # Tabla de análisis horizontal
                                            st.write("##### 📊 Análisis Horizontal Detallado")
                                            
                                            df_balance = pd.DataFrame(balance_ah['cuentas_analizadas'])
                                            
                                            # Formatear DataFrame
                                            df_display = df_balance.copy()
                                            df_display['valor_año_base'] = df_display['valor_año_base'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
                                            df_display['valor_año_actual'] = df_display['valor_año_actual'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
                                            df_display['variacion_absoluta'] = df_display['variacion_absoluta'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
                                            df_display['analisis_horizontal'] = df_display['analisis_horizontal'].apply(
                                                lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A"
                                            )
                                            
                                            # Renombrar columnas
                                            df_display = df_display.rename(columns={
                                                'cuenta': 'Cuenta',
                                                'valor_año_base': f'Valor {balance_ah["año_base"]}',
                                                'valor_año_actual': f'Valor {balance_ah["año_actual"]}',
                                                'variacion_absoluta': 'Variación Absoluta',
                                                'analisis_horizontal': 'Análisis Horizontal (%)',
                                                'estado_variacion': 'Estado'
                                            })
                                            
                                            st.dataframe(
                                                df_display[['Cuenta', f'Valor {balance_ah["año_base"]}', f'Valor {balance_ah["año_actual"]}', 'Variación Absoluta', 'Análisis Horizontal (%)']],
                                                use_container_width=True,
                                                height=400
                                            )
                                    
                                    # Estado de Resultados
                                    if 'resultados' in estados_disponibles:
                                        tab_idx = 1 if 'balance' in estados_disponibles else 0
                                        with tabs_estados[tab_idx]:
                                            resultados_ah = analisis_horizontal_resultados['estados_analizados']['resultados']
                                            
                                            st.write(f"**Año Base:** {resultados_ah['año_base']} | **Año Actual:** {resultados_ah['año_actual']}")
                                            st.write(f"**Total Cuentas:** {resultados_ah['total_cuentas_analizadas']}")
                                            
                                            # Estadísticas
                                            col1, col2, col3, col4 = st.columns(4)
                                            stats = resultados_ah['estadisticas']
                                            with col1:
                                                st.metric("✅ Aumentos", stats['variaciones_positivas'], delta="Positivo")
                                            with col2:
                                                st.metric("⬇️ Disminuciones", stats['variaciones_negativas'], delta="Negativo")
                                            with col3:
                                                st.metric("➖ Sin Cambio", stats['sin_variacion'])
                                            with col4:
                                                st.metric("⚠️ N/A", stats['no_calculables'])
                                            
                                            st.divider()
                                            
                                            # Tabla de análisis horizontal
                                            st.write("##### 💰 Análisis Horizontal Detallado")
                                            
                                            df_resultados = pd.DataFrame(resultados_ah['cuentas_analizadas'])
                                            
                                            # Formatear DataFrame
                                            df_display = df_resultados.copy()
                                            df_display['valor_año_base'] = df_display['valor_año_base'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
                                            df_display['valor_año_actual'] = df_display['valor_año_actual'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
                                            df_display['variacion_absoluta'] = df_display['variacion_absoluta'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
                                            df_display['analisis_horizontal'] = df_display['analisis_horizontal'].apply(
                                                lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A"
                                            )
                                            
                                            # Renombrar columnas
                                            df_display = df_display.rename(columns={
                                                'cuenta': 'Cuenta',
                                                'valor_año_base': f'Valor {resultados_ah["año_base"]}',
                                                'valor_año_actual': f'Valor {resultados_ah["año_actual"]}',
                                                'variacion_absoluta': 'Variación Absoluta',
                                                'analisis_horizontal': 'Análisis Horizontal (%)',
                                                'estado_variacion': 'Estado'
                                            })
                                            
                                            st.dataframe(
                                                df_display[['Cuenta', f'Valor {resultados_ah["año_base"]}', f'Valor {resultados_ah["año_actual"]}', 'Variación Absoluta', 'Análisis Horizontal (%)']],
                                                use_container_width=True,
                                                height=400
                                            )
                                    
                                    # Flujo de Efectivo
                                    if 'flujo' in estados_disponibles:
                                        tab_idx = 2 if 'balance' in estados_disponibles and 'resultados' in estados_disponibles else (1 if 'balance' in estados_disponibles or 'resultados' in estados_disponibles else 0)
                                        with tabs_estados[tab_idx]:
                                            flujo_ah = analisis_horizontal_resultados['estados_analizados']['flujo']
                                            
                                            st.write(f"**Año Base:** {flujo_ah['año_base']} | **Año Actual:** {flujo_ah['año_actual']}")
                                            st.write(f"**Total Cuentas:** {flujo_ah['total_cuentas_analizadas']}")
                                            
                                            # Estadísticas
                                            col1, col2, col3, col4 = st.columns(4)
                                            stats = flujo_ah['estadisticas']
                                            with col1:
                                                st.metric("✅ Aumentos", stats['variaciones_positivas'], delta="Positivo")
                                            with col2:
                                                st.metric("⬇️ Disminuciones", stats['variaciones_negativas'], delta="Negativo")
                                            with col3:
                                                st.metric("➖ Sin Cambio", stats['sin_variacion'])
                                            with col4:
                                                st.metric("⚠️ N/A", stats['no_calculables'])
                                            
                                            st.divider()
                                            
                                            # Tabla de análisis horizontal
                                            st.write("##### 💵 Análisis Horizontal Detallado")
                                            
                                            df_flujo = pd.DataFrame(flujo_ah['cuentas_analizadas'])
                                            
                                            # Formatear DataFrame
                                            df_display = df_flujo.copy()
                                            df_display['valor_año_base'] = df_display['valor_año_base'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
                                            df_display['valor_año_actual'] = df_display['valor_año_actual'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
                                            df_display['variacion_absoluta'] = df_display['variacion_absoluta'].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
                                            df_display['analisis_horizontal'] = df_display['analisis_horizontal'].apply(
                                                lambda x: f"{x:+.2f}%" if pd.notnull(x) else "N/A"
                                            )
                                            
                                            # Renombrar columnas
                                            df_display = df_display.rename(columns={
                                                'cuenta': 'Cuenta',
                                                'valor_año_base': f'Valor {flujo_ah["año_base"]}',
                                                'valor_año_actual': f'Valor {flujo_ah["año_actual"]}',
                                                'variacion_absoluta': 'Variación Absoluta',
                                                'analisis_horizontal': 'Análisis Horizontal (%)',
                                                'estado_variacion': 'Estado'
                                            })
                                            
                                            st.dataframe(
                                                df_display[['Cuenta', f'Valor {flujo_ah["año_base"]}', f'Valor {flujo_ah["año_actual"]}', 'Variación Absoluta', 'Análisis Horizontal (%)']],
                                                use_container_width=True,
                                                height=400
                                            )
                                
                                st.divider()
                                
                                # Botón de descarga Excel
                                if st.button("📥 Exportar Análisis Horizontal a Excel", key="btn_export_horizontal"):
                                    nombre_archivo = f"analisis_horizontal_{archivo_seleccionado.split('.')[0]}.xlsx"
                                    analizador.analizador_horizontal.exportar_a_excel(analisis_horizontal_resultados, nombre_archivo)
                                    st.success(f"✅ Archivo exportado: {nombre_archivo}")
                        
                        else:
                            st.warning("⚠️ No hay datos extraídos disponibles para este archivo")
                
                except Exception as e:
                    st.error(f"❌ Error en análisis horizontal: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
            
            with tab8:
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