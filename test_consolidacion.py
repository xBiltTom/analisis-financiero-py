"""
Script de prueba para la funcionalidad de consolidación multi-período
"""
import os
from extractor_estados_mejorado import extraer_estados_desde_archivo

# Procesar múltiples archivos POST-2010
archivos_post_2010 = [
    "ejemplos/REPORTE DETALLE FINANCIERO 2024.html",
    "ejemplos/REPORTE DETALLE FINANCIERO 2023.html",
    "ejemplos/REPORTE DETALLE FINANCIERO 2022.html",
    "ejemplos/REPORTE DETALLE FINANCIERO 2021.html",
    "ejemplos/REPORTE DETALLE FINANCIERO 2020.html"
]

print("="*80)
print("PRUEBA DE CONSOLIDACIÓN MULTI-PERÍODO (POST-2010)")
print("="*80)

# Extraer datos de cada archivo
datos_extraidos = []
for archivo in archivos_post_2010:
    if os.path.exists(archivo):
        print(f"\n📄 Procesando: {archivo}")
        resultados = extraer_estados_desde_archivo(archivo)
        
        empresa = resultados['metadatos'].get('empresa', 'N/A')
        año = resultados['año_documento']
        
        # Contar años únicos en cada estado
        años_unicos = set()
        for estado in resultados['estados'].values():
            años_unicos.update(estado['años'])
        
        print(f"   ✅ Empresa: {empresa}")
        print(f"   ✅ Año del reporte: {año}")
        print(f"   ✅ Años disponibles en datos: {sorted(años_unicos, reverse=True)}")
        
        datos_extraidos.append(resultados)
    else:
        print(f"❌ Archivo no encontrado: {archivo}")

print("\n" + "="*80)
print(f"✅ Total de archivos procesados: {len(datos_extraidos)}")

# Recolectar todos los años únicos
todos_los_años = set()
for datos in datos_extraidos:
    for estado in datos['estados'].values():
        todos_los_años.update(estado['años'])

print(f"📅 Años únicos consolidados: {sorted(todos_los_años, reverse=True)}")
print("="*80)

# Mostrar ejemplo de consolidación para Estado de Situación Financiera
print("\n📊 EJEMPLO: Consolidación de Estado de Situación Financiera")
print("-"*80)

# Diccionario para consolidar cuentas
cuentas_consolidadas = {}

for datos in datos_extraidos:
    if 'balance' in datos['estados']:
        balance = datos['estados']['balance']
        
        for cuenta in balance['cuentas'][:10]:  # Solo las primeras 10 cuentas como ejemplo
            nombre_cuenta = cuenta['nombre']
            
            if nombre_cuenta not in cuentas_consolidadas:
                cuentas_consolidadas[nombre_cuenta] = {}
            
            # Agregar valores por año
            for año, valor in cuenta['valores'].items():
                if año not in cuentas_consolidadas[nombre_cuenta]:
                    cuentas_consolidadas[nombre_cuenta][año] = valor

# Mostrar resultado
print(f"\nCuentas consolidadas (primeras 10):\n")
for cuenta, valores in list(cuentas_consolidadas.items())[:10]:
    años_str = ", ".join([f"{año}: {val:,.0f}" for año, val in sorted(valores.items(), reverse=True)])
    print(f"• {cuenta}")
    print(f"  {años_str}")

print("\n" + "="*80)
print("✅ PRUEBA COMPLETADA")
print("="*80)
