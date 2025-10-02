"""
Test simple de consolidación sin Streamlit
"""
from extractor_estados_mejorado import extraer_estados_desde_archivo
import pandas as pd

print("="*80)
print("TEST SIMPLE: CONSOLIDACION ESTADO DE CAMBIOS EN PATRIMONIO")
print("="*80 + "\n")

# Archivos a procesar
archivos = [
    "consolidar/ReporteDetalleInformacionFinanciero (15).html",  # 2024
    "consolidar/ReporteDetalleInformacionFinanciero (16).html",  # 2023
    "consolidar/ReporteDetalleInformacionFinanciero (17).html",  # 2022
]

# Consolidar datos manualmente
datos_consolidados = {}

for archivo in archivos:
    print(f"\nProcesando: {archivo}")
    resultado = extraer_estados_desde_archivo(archivo)
    
    if 'patrimonio' in resultado['estados']:
        patrimonio = resultado['estados']['patrimonio']
        año_doc = resultado['año_documento']
        
        print(f"  Anio documento: {año_doc}")
        print(f"  Cuentas: {len(patrimonio['cuentas'])}")
        
        # Consolidar cada cuenta
        for cuenta in patrimonio['cuentas']:
            ccuenta = cuenta.get('ccuenta', '')
            nombre = cuenta['nombre']
            clave = f"{ccuenta}|{nombre}"
            
            if clave not in datos_consolidados:
                datos_consolidados[clave] = {
                    'CCUENTA': ccuenta,
                    'Cuenta': nombre
                }
            
            # Agregar valor del año
            valores = cuenta['valores']
            for año, valor in valores.items():
                datos_consolidados[clave][año] = valor

# Crear DataFrame
print(f"\n{'='*80}")
print(f"RESULTADOS DE LA CONSOLIDACION:")
print("="*80 + "\n")

filas = list(datos_consolidados.values())
df = pd.DataFrame(filas)

# Ordenar columnas: CCUENTA, Cuenta, luego años descendentes
años_cols = sorted([col for col in df.columns if col not in ['CCUENTA', 'Cuenta']], reverse=True)
columnas = ['CCUENTA', 'Cuenta'] + años_cols
df = df[columnas].fillna(0)

print(f"Columnas: {list(df.columns)}")
print(f"Total filas: {len(df)}")
print(f"\nPrimeras 10 filas:\n")
print(df.head(10).to_string(index=False))

print(f"\nUltimas 5 filas:\n")
print(df.tail(5).to_string(index=False))

# Buscar saldos finales
print(f"\n{'='*80}")
print("SALDOS FINALES:")
print("="*80 + "\n")

for _, fila in df.iterrows():
    if 'SALDOS' in str(fila['Cuenta']).upper() and 'DICIEMBRE' in str(fila['Cuenta']).upper():
        print(f"{fila['CCUENTA']} - {fila['Cuenta']}")
        for col in df.columns:
            if col not in ['CCUENTA', 'Cuenta'] and fila[col] != 0:
                print(f"  {col}: {fila[col]:,.0f}")

print(f"\n{'='*80}")
print("TEST COMPLETADO")
print("="*80)
