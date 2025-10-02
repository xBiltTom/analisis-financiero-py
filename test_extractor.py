"""Script de prueba para analizar los totales del balance"""
import extractor_estados_mejorado as ext

# Analizar archivo 2004
print("="*60)
print("ANÁLISIS DE ARCHIVO 2004")
print("="*60)

r = ext.extraer_estados_desde_archivo('ejemplos/ReporteDetalleInformacionFinanciero (6).html')
balance = r['estados']['balance']

print("\n=== TOTALES ENCONTRADOS ===")
for cuenta in balance['cuentas']:
    if 'TOTAL' in cuenta['nombre'].upper() and cuenta['es_total']:
        print(f"{cuenta['nombre']}: {cuenta['valores']}")

print("\n=== VALIDACIÓN ===")
val = r['validaciones']['equilibrio_contable']
print(f"Total Activos: {val['total_activos']}")
print(f"Total Pasivos: {val['total_pasivos']}")
print(f"Total Patrimonio: {val['total_patrimonio']}")
print(f"Suma P+P: {val['total_pasivos'] + val['total_patrimonio']}")
print(f"Diferencia: {val['diferencia']}")
print(f"Es válido: {val['es_valido']}")

# Ver todas las cuentas con "TOTAL" en el nombre
print("\n=== TODAS LAS CUENTAS CON 'TOTAL' ===")
for cuenta in balance['cuentas']:
    if 'TOTAL' in cuenta['nombre'].upper():
        print(f"{cuenta['nombre']} [es_total={cuenta['es_total']}]: {cuenta['valores']}")
