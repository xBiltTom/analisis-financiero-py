"""
Análisis detallado del HTML crudo del Estado de Cambios en el Patrimonio
"""
from bs4 import BeautifulSoup
import re

print("="*80)
print("ANÁLISIS DETALLADO: HTML DEL ESTADO DE CAMBIOS EN EL PATRIMONIO")
print("="*80 + "\n")

archivo = "consolidar/ReporteDetalleInformacionFinanciero (15).html"

with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Buscar el título del estado
print("🔍 Buscando título del estado...")
for span in soup.find_all('span', style=re.compile(r'font-weight:bold')):
    texto = span.get_text(strip=True).upper()
    if 'PATRIMONIO' in texto and 'CAMBIOS' in texto:
        print(f"✅ Encontrado: {span.get_text(strip=True)}")
        
        # Buscar la tabla siguiente
        tabla = span.find_next('table')
        if tabla:
            print("\n📊 ESTRUCTURA DE LA TABLA:")
            print("-"*80)
            
            filas = tabla.find_all('tr')
            print(f"Total de filas: {len(filas)}")
            
            # Analizar header
            print("\n🔹 FILA 1 (HEADER):")
            if filas:
                headers = filas[0].find_all('th')
                for i, th in enumerate(headers):
                    print(f"  Columna {i}: '{th.get_text(strip=True)}'")
            
            # Mostrar primeras 20 filas de datos
            print("\n🔹 PRIMERAS 20 FILAS DE DATOS:")
            print("-"*80)
            for i, fila in enumerate(filas[1:21], 1):
                celdas = fila.find_all(['td', 'th'])
                if len(celdas) >= 3:
                    # Asumiendo: CCUENTA | Cuenta | Total Patrimonio
                    ccuenta = celdas[0].get_text(strip=True)
                    cuenta = celdas[1].get_text(strip=True) if len(celdas) > 1 else ''
                    valor = celdas[-1].get_text(strip=True) if len(celdas) > 2 else ''
                    
                    print(f"{i:2d}. CCUENTA: {ccuenta:15s} | Cuenta: {cuenta[:50]:50s} | Valor: {valor}")
            
            # Mostrar últimas 10 filas
            print("\n🔹 ÚLTIMAS 10 FILAS:")
            print("-"*80)
            for i, fila in enumerate(filas[-10:], len(filas)-9):
                celdas = fila.find_all(['td', 'th'])
                if len(celdas) >= 3:
                    ccuenta = celdas[0].get_text(strip=True)
                    cuenta = celdas[1].get_text(strip=True) if len(celdas) > 1 else ''
                    valor = celdas[-1].get_text(strip=True) if len(celdas) > 2 else ''
                    
                    print(f"{i:2d}. CCUENTA: {ccuenta:15s} | Cuenta: {cuenta[:50]:50s} | Valor: {valor}")
        
        break

print("\n" + "="*80)
