"""Script para verificar los años de los archivos en la carpeta consolidar"""
from extractor_estados_mejorado import extraer_estados_desde_archivo
import os

print("="*70)
print("VERIFICANDO AÑOS DE ARCHIVOS EN CARPETA 'consolidar'")
print("="*70 + "\n")

carpeta = "consolidar"
archivos = sorted([f for f in os.listdir(carpeta) if f.endswith('.html')])

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    try:
        resultado = extraer_estados_desde_archivo(ruta)
        año = resultado['año_documento']
        formato = resultado['formato']
        empresa = resultado['metadatos'].get('empresa', 'N/A')
        
        print(f"📄 {archivo}")
        print(f"   Año: {año}")
        print(f"   Formato: {formato}")
        print(f"   Empresa: {empresa}")
        print()
    except Exception as e:
        print(f"❌ Error en {archivo}: {e}\n")

print("="*70)
