"""
Descargador Automático de Estados Financieros desde SMV
========================================================
Automatiza la descarga de estados financieros desde la web de la SMV (Superintendencia del Mercado de Valores)

Características:
- Búsqueda automática de empresas por nombre
- Descarga consecutiva de múltiples años
- Barra de progreso en tiempo real
- Configuración de carpeta de descargas personalizada
- Manejo de errores robusto
- Compatible con ChromeDriver

Autor: Sistema de Análisis Financiero
Fecha: 3 de octubre de 2025
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager  # ✨ Gestión automática de ChromeDriver
import time
import os
from typing import List, Dict, Callable, Optional
from pathlib import Path
import streamlit as st


class DescargadorSMV:
    """Clase para automatizar descargas de estados financieros desde la SMV"""
    
    # URL base de la SMV
    URL_SMV = "https://www.smv.gob.pe/SIMV/Frm_InformacionFinanciera?data=A70181B60967D74090DCD93C4920AA1D769614EC12"
    
    def __init__(self, download_dir: str = None, driver_path: str = None, headless: bool = True):
        """
        Inicializa el descargador
        
        Args:
            download_dir: Ruta de la carpeta de descargas (default: ./descargas)
            driver_path: Ruta del ChromeDriver (default: gestión automática con webdriver-manager)
            headless: Si True, ejecuta sin mostrar ventana de Chrome (más rápido)
        """
        # Configurar carpeta de descargas
        if download_dir is None:
            self.download_dir = os.path.join(os.getcwd(), "descargas")
        else:
            self.download_dir = download_dir
        
        # Crear carpeta si no existe
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Configurar ruta del driver (None = usar webdriver-manager automático)
        self.driver_path = driver_path
        self.headless = headless
        
        self.driver = None
        self.empresas_disponibles = []
    
    def _configurar_chrome(self) -> webdriver.Chrome:
        """
        Configura y devuelve una instancia de Chrome con opciones optimizadas
        
        Returns:
            webdriver.Chrome: Instancia configurada del navegador
        """
        options = webdriver.ChromeOptions()
        
        # Configurar descargas automáticas
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True  # Descargar PDFs automáticamente
        }
        options.add_experimental_option("prefs", prefs)
        
        # Opciones adicionales para mejor rendimiento
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Evitar detección
        options.add_argument("--log-level=3")  # Reducir logs
        
        # ✨ MODO HEADLESS - No mostrar navegador (más rápido)
        if self.headless:
            options.add_argument("--headless=new")  # Nuevo modo headless de Chrome
            options.add_argument("--window-size=1920,1080")  # Tamaño de ventana virtual
        
        # ✨ Usar webdriver-manager para gestión automática de ChromeDriver
        if self.driver_path is None:
            # Gestión automática - descarga la versión correcta automáticamente
            service = Service(ChromeDriverManager().install())
        else:
            # Usar ruta manual si se especificó
            service = Service(executable_path=self.driver_path)
        
        # Inicializar driver
        driver = webdriver.Chrome(service=service, options=options)
        
        if not self.headless:
            driver.maximize_window()
        
        return driver
    
    def iniciar_navegador(self) -> bool:
        """
        Inicia el navegador y navega a la página de la SMV
        
        Returns:
            bool: True si se inició correctamente, False en caso contrario
        """
        try:
            self.driver = self._configurar_chrome()
            self.driver.get(self.URL_SMV)
            
            # Esperar a que cargue la página
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "MainContent_cboDenominacionSocial"))
            )
            
            return True
        except Exception as e:
            print(f"❌ Error al iniciar navegador: {str(e)}")
            return False
    
    def cerrar_navegador(self):
        """Cierra el navegador y libera recursos"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def obtener_empresas_disponibles(self) -> List[Dict[str, str]]:
        """
        Obtiene la lista de empresas disponibles en el combo
        
        Returns:
            List[Dict]: Lista de diccionarios con 'value' y 'text' de cada empresa
        """
        try:
            select_element = self.driver.find_element(By.ID, "MainContent_cboDenominacionSocial")
            combo = Select(select_element)
            
            empresas = []
            for option in combo.options:
                value = option.get_attribute("value")
                text = option.text.strip()
                
                # Filtrar opción vacía o "Seleccione"
                if value and value != "0" and text.lower() != "seleccione":
                    empresas.append({
                        'value': value,
                        'text': text
                    })
            
            self.empresas_disponibles = empresas
            return empresas
        
        except Exception as e:
            print(f"❌ Error al obtener empresas: {str(e)}")
            return []
    
    def buscar_empresa(self, nombre_busqueda: str) -> Optional[Dict[str, str]]:
        """
        Busca una empresa por nombre (búsqueda parcial)
        
        Args:
            nombre_busqueda: Texto a buscar en el nombre de la empresa
        
        Returns:
            Dict con 'value' y 'text' de la primera empresa encontrada, o None
        """
        if not self.empresas_disponibles:
            self.obtener_empresas_disponibles()
        
        nombre_busqueda_lower = nombre_busqueda.lower()
        
        # Búsqueda exacta primero
        for empresa in self.empresas_disponibles:
            if empresa['text'].lower() == nombre_busqueda_lower:
                return empresa
        
        # Búsqueda parcial (contiene)
        for empresa in self.empresas_disponibles:
            if nombre_busqueda_lower in empresa['text'].lower():
                return empresa
        
        # Búsqueda por palabras clave (cualquier palabra coincide)
        palabras_busqueda = nombre_busqueda_lower.split()
        for empresa in self.empresas_disponibles:
            texto_empresa_lower = empresa['text'].lower()
            if any(palabra in texto_empresa_lower for palabra in palabras_busqueda):
                return empresa
        
        return None
    
    def seleccionar_empresa(self, empresa: Dict[str, str]) -> bool:
        """
        Selecciona una empresa del combo
        
        Args:
            empresa: Dict con 'value' y 'text' de la empresa
        
        Returns:
            bool: True si se seleccionó correctamente
        """
        try:
            select_element = self.driver.find_element(By.ID, "MainContent_cboDenominacionSocial")
            combo = Select(select_element)
            combo.select_by_value(empresa['value'])
            
            time.sleep(1)  # Esperar recarga
            return True
        
        except Exception as e:
            print(f"❌ Error al seleccionar empresa: {str(e)}")
            return False
    
    def seleccionar_periodo_anual(self) -> bool:
        """
        Selecciona el periodo 'Anual'
        
        Returns:
            bool: True si se seleccionó correctamente
        """
        try:
            radio_anual = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "MainContent_cboPeriodo_1"))
            )
            radio_anual.click()
            
            time.sleep(1)  # Esperar postback
            return True
        
        except Exception as e:
            print(f"❌ Error al seleccionar periodo anual: {str(e)}")
            return False
    
    def descargar_año(self, año: int, callback_progreso: Callable = None) -> bool:
        """
        Descarga los estados financieros de un año específico
        
        Args:
            año: Año a descargar (ej: 2024)
            callback_progreso: Función callback para actualizar progreso
        
        Returns:
            bool: True si se descargó correctamente
        """
        try:
            if callback_progreso:
                callback_progreso(f"📅 Seleccionando año {año}...")
            
            # Seleccionar año
            anio_dropdown = Select(self.driver.find_element(By.ID, "MainContent_cboAnio"))
            anio_dropdown.select_by_value(str(año))
            time.sleep(1)
            
            if callback_progreso:
                callback_progreso(f"🔍 Buscando registros del año {año}...")
            
            # Clic en Buscar
            btn_buscar = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "MainContent_cbBuscar"))
            )
            btn_buscar.click()
            
            # Esperar a que desaparezca el modal de carga
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located((By.ID, "myLoading"))
            )
            
            if callback_progreso:
                callback_progreso(f"📊 Esperando resultados del año {año}...")
            
            # Esperar resultados
            filas = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#MainContent_grdInfoFinanciera tr.item-grid"))
            )
            
            if callback_progreso:
                callback_progreso(f"✅ {len(filas)} registros encontrados para {año}")
            
            # Buscar fila con "Estado Financiero"
            link = None
            for fila in filas:
                columnas = fila.find_elements(By.TAG_NAME, "td")
                if len(columnas) > 1:
                    texto_col = self._normalizar_texto(columnas[1].text.strip())
                    if "estado financiero" in texto_col:
                        try:
                            link = fila.find_element(By.XPATH, ".//a[contains(@title, 'detalle') and contains(@title, 'Financieros')]")
                            if link:
                                break
                        except:
                            continue
            
            if not link:
                if callback_progreso:
                    callback_progreso(f"⚠️ No se encontró 'Estados Financieros' para el año {año}")
                return False
            
            if callback_progreso:
                callback_progreso(f"🔗 Abriendo detalle de Estados Financieros {año}...")
            
            # Guardar ventana principal
            main_window = self.driver.current_window_handle
            
            # Asegurar que modal desapareció
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located((By.ID, "myLoading"))
            )
            
            # Re-buscar link (DOM pudo recargarse)
            link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@title, 'detalle') and contains(@title, 'Financieros')]"))
            )
            
            # Scroll y clic con JavaScript
            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
            self.driver.execute_script("arguments[0].click();", link)
            
            # Esperar nueva pestaña
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
            
            # Cambiar a nueva pestaña
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            if callback_progreso:
                callback_progreso(f"📥 Descargando archivo Excel del año {año}...")
            
            # Clic en botón Excel
            excel_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "cbExcel"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", excel_btn)
            excel_btn.click()
            
            # Esperar descarga
            time.sleep(3)  # Ajustar según velocidad de red
            
            # Verificar descarga
            archivo_descargado = self._verificar_descarga_reciente()
            
            # Cerrar pestaña y volver a principal
            self.driver.close()
            self.driver.switch_to.window(main_window)
            
            if archivo_descargado:
                if callback_progreso:
                    callback_progreso(f"✅ Archivo {año} descargado: {archivo_descargado}")
                return True
            else:
                if callback_progreso:
                    callback_progreso(f"⚠️ No se detectó archivo descargado para {año}")
                return False
        
        except TimeoutException:
            if callback_progreso:
                callback_progreso(f"⏱️ Timeout al procesar año {año}")
            return False
        except Exception as e:
            if callback_progreso:
                callback_progreso(f"❌ Error al descargar año {año}: {str(e)}")
            return False
    
    def descargar_rango_años(
        self, 
        año_inicio: int, 
        año_fin: int, 
        callback_progreso: Callable = None
    ) -> Dict[str, List[int]]:
        """
        Descarga estados financieros de un rango de años
        
        Args:
            año_inicio: Año inicial (más reciente, ej: 2024)
            año_fin: Año final (más antiguo, ej: 2020)
            callback_progreso: Función callback para actualizar progreso
        
        Returns:
            Dict con listas de años 'exitosos' y 'fallidos'
        """
        resultados = {
            'exitosos': [],
            'fallidos': []
        }
        
        # Generar lista de años (descendente)
        años = list(range(año_inicio, año_fin - 1, -1))
        total_años = len(años)
        
        for idx, año in enumerate(años, 1):
            if callback_progreso:
                callback_progreso(f"\n🔄 Procesando año {año} ({idx}/{total_años})...")
            
            exito = self.descargar_año(año, callback_progreso)
            
            if exito:
                resultados['exitosos'].append(año)
            else:
                resultados['fallidos'].append(año)
            
            # Pequeña pausa entre descargas
            time.sleep(2)
        
        return resultados
    
    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas"""
        texto = texto.lower()
        reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
        for original, reemplazo in reemplazos.items():
            texto = texto.replace(original, reemplazo)
        return texto
    
    def _verificar_descarga_reciente(self, timeout: int = 10) -> Optional[str]:
        """
        Verifica si se descargó un archivo recientemente
        
        Args:
            timeout: Segundos a esperar por el archivo
        
        Returns:
            Nombre del archivo descargado o None
        """
        tiempo_inicio = time.time()
        
        while time.time() - tiempo_inicio < timeout:
            try:
                archivos = os.listdir(self.download_dir)
                excel_files = [f for f in archivos if f.endswith((".xls", ".xlsx"))]
                
                if excel_files:
                    # Obtener el archivo más reciente
                    archivos_con_tiempo = [
                        (f, os.path.getmtime(os.path.join(self.download_dir, f)))
                        for f in excel_files
                    ]
                    archivo_mas_reciente = max(archivos_con_tiempo, key=lambda x: x[1])
                    
                    # Verificar que se descargó hace menos de 10 segundos
                    if time.time() - archivo_mas_reciente[1] < 10:
                        return archivo_mas_reciente[0]
            except:
                pass
            
            time.sleep(0.5)
        
        return None
    
    def proceso_completo(
        self, 
        nombre_empresa: str, 
        año_inicio: int, 
        año_fin: int,
        callback_progreso: Callable = None
    ) -> Dict:
        """
        Proceso completo: buscar empresa y descargar rango de años
        
        Args:
            nombre_empresa: Nombre de la empresa a buscar
            año_inicio: Año inicial (más reciente)
            año_fin: Año final (más antiguo)
            callback_progreso: Función callback para actualizar progreso
        
        Returns:
            Dict con resultados del proceso
        """
        try:
            if callback_progreso:
                callback_progreso("🚀 Iniciando navegador...")
            
            if not self.iniciar_navegador():
                return {'error': 'No se pudo iniciar el navegador'}
            
            if callback_progreso:
                callback_progreso("📋 Obteniendo lista de empresas...")
            
            self.obtener_empresas_disponibles()
            
            if callback_progreso:
                callback_progreso(f"🔍 Buscando empresa: {nombre_empresa}")
            
            empresa = self.buscar_empresa(nombre_empresa)
            
            if not empresa:
                self.cerrar_navegador()
                return {'error': f'No se encontró la empresa: {nombre_empresa}'}
            
            if callback_progreso:
                callback_progreso(f"✅ Empresa encontrada: {empresa['text']}")
            
            if not self.seleccionar_empresa(empresa):
                self.cerrar_navegador()
                return {'error': 'No se pudo seleccionar la empresa'}
            
            if callback_progreso:
                callback_progreso("📅 Seleccionando periodo anual...")
            
            if not self.seleccionar_periodo_anual():
                self.cerrar_navegador()
                return {'error': 'No se pudo seleccionar periodo anual'}
            
            if callback_progreso:
                callback_progreso(f"📥 Iniciando descargas de {año_inicio} a {año_fin}...")
            
            resultados = self.descargar_rango_años(año_inicio, año_fin, callback_progreso)
            
            if callback_progreso:
                callback_progreso("🔒 Cerrando navegador...")
            
            self.cerrar_navegador()
            
            return {
                'empresa': empresa['text'],
                'años_exitosos': resultados['exitosos'],
                'años_fallidos': resultados['fallidos'],
                'total_exitosos': len(resultados['exitosos']),
                'total_fallidos': len(resultados['fallidos']),
                'carpeta_descargas': self.download_dir
            }
        
        except Exception as e:
            self.cerrar_navegador()
            return {'error': f'Error en proceso completo: {str(e)}'}


# ===== FUNCIÓN DE PRUEBA =====
if __name__ == "__main__":
    print("="*80)
    print("DESCARGADOR AUTOMÁTICO DE ESTADOS FINANCIEROS - SMV")
    print("="*80)
    
    def callback_test(mensaje):
        """Callback simple para testing"""
        print(f"  {mensaje}")
    
    # Configuración
    descargador = DescargadorSMV(
        download_dir=os.path.join(os.getcwd(), "descargas"),
        driver_path=os.path.join(os.getcwd(), "drivers", "chromedriver.exe")
    )
    
    # Proceso completo
    print("\n🚀 Iniciando proceso de descarga...")
    print(f"📂 Carpeta de descargas: {descargador.download_dir}\n")
    
    resultado = descargador.proceso_completo(
        nombre_empresa="SAN JUAN",  # Prueba con búsqueda parcial
        año_inicio=2024,
        año_fin=2022,
        callback_progreso=callback_test
    )
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("RESUMEN DE DESCARGAS")
    print("="*80)
    
    if 'error' in resultado:
        print(f"❌ ERROR: {resultado['error']}")
    else:
        print(f"✅ Empresa: {resultado['empresa']}")
        print(f"📂 Carpeta: {resultado['carpeta_descargas']}")
        print(f"✅ Años exitosos: {resultado['total_exitosos']} - {resultado['años_exitosos']}")
        if resultado['años_fallidos']:
            print(f"⚠️ Años fallidos: {resultado['total_fallidos']} - {resultado['años_fallidos']}")
        print(f"\n🎉 Proceso completado exitosamente!")
