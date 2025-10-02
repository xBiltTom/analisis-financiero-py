"""
Script de prueba para verificar los patrones de detección de totales
para archivos ≤2009 vs ≥2010
"""
import re

def test_patrones():
    """Prueba los patrones de detección"""
    
    # Patrones Pre-2010 (≤2009)
    patrones_activos_pre = [
        r'^TOTAL\s+ACTIVO\s*$',
        r'^TOTAL\s+DEL\s+ACTIVO\s*$',
    ]
    
    patrones_pasivos_pre = [
        r'^TOTAL\s+PASIVO\s*$',
        r'^TOTAL\s+DEL\s+PASIVO\s*$',
        r'^PASIVO\s+Y\s+PATRIMONIO\s*$',
        r'^TOTAL\s+PASIVO\s+Y\s+PATRIMONIO\s*$'
    ]
    
    # Patrones Post-2010 (≥2010)
    patrones_activos_post = [
        r'^TOTAL\s+ACTIVOS\s*$',
        r'^TOTAL\s+DE\s+ACTIVOS\s*$',
        r'^ACTIVOS\s+TOTALES\s*$',
        r'^TOTAL\s+DE\s+LOS\s+ACTIVOS\s*$'
    ]
    
    patrones_pasivos_post = [
        r'^TOTAL\s+PASIVOS\s*$',
        r'^TOTAL\s+DE\s+PASIVOS\s*$',
        r'^PASIVOS\s+TOTALES\s*$',
        r'^TOTAL\s+DE\s+LOS\s+PASIVOS\s*$'
    ]
    
    # Casos de prueba Pre-2010
    casos_pre_2010 = {
        'ACTIVOS': [
            'TOTAL ACTIVO',
            'TOTAL DEL ACTIVO',
        ],
        'PASIVOS': [
            'TOTAL PASIVO',
            'TOTAL DEL PASIVO',
            'PASIVO Y PATRIMONIO',
            'TOTAL PASIVO Y PATRIMONIO',
        ]
    }
    
    # Casos de prueba Post-2010
    casos_post_2010 = {
        'ACTIVOS': [
            'TOTAL ACTIVOS',
            'TOTAL DE ACTIVOS',
            'ACTIVOS TOTALES',
            'TOTAL DE LOS ACTIVOS',
        ],
        'PASIVOS': [
            'TOTAL PASIVOS',
            'TOTAL DE PASIVOS',
            'PASIVOS TOTALES',
            'TOTAL DE LOS PASIVOS',
        ]
    }
    
    print("="*70)
    print("PRUEBA DE PATRONES PRE-2010 (≤2009)")
    print("="*70)
    
    print("\n🔹 ACTIVOS:")
    for caso in casos_pre_2010['ACTIVOS']:
        match = False
        for patron in patrones_activos_pre:
            if re.match(patron, caso):
                match = True
                break
        print(f"  {'✅' if match else '❌'} '{caso}' - {'Detectado' if match else 'NO detectado'}")
    
    print("\n🔹 PASIVOS:")
    for caso in casos_pre_2010['PASIVOS']:
        match = False
        for patron in patrones_pasivos_pre:
            if re.match(patron, caso):
                match = True
                break
        print(f"  {'✅' if match else '❌'} '{caso}' - {'Detectado' if match else 'NO detectado'}")
    
    print("\n" + "="*70)
    print("PRUEBA DE PATRONES POST-2010 (≥2010)")
    print("="*70)
    
    print("\n🔹 ACTIVOS:")
    for caso in casos_post_2010['ACTIVOS']:
        match = False
        for patron in patrones_activos_post:
            if re.match(patron, caso):
                match = True
                break
        print(f"  {'✅' if match else '❌'} '{caso}' - {'Detectado' if match else 'NO detectado'}")
    
    print("\n🔹 PASIVOS:")
    for caso in casos_post_2010['PASIVOS']:
        match = False
        for patron in patrones_pasivos_post:
            if re.match(patron, caso):
                match = True
                break
        print(f"  {'✅' if match else '❌'} '{caso}' - {'Detectado' if match else 'NO detectado'}")
    
    print("\n" + "="*70)
    print("✅ PRUEBA COMPLETADA")
    print("="*70)

if __name__ == "__main__":
    test_patrones()
