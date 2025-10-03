"""
Validación manual de todos los cálculos de Rotación CxC
"""

print("="*80)
print("🧮 VALIDACIÓN MANUAL DE ROTACIÓN DE CUENTAS POR COBRAR")
print("="*80)

# Datos extraídos del debug
datos_años = {
    2020: {
        'G': 853_586,
        'K': 160_633,
        'F': 1_638,
        'K_ant': 117_340,  # 2019
        'F_ant': 732  # 2019
    },
    2021: {
        'G': 1_194_911,
        'K': 116_952,
        'F': 38_242,
        'K_ant': 160_633,  # 2020
        'F_ant': 1_638  # 2020
    },
    2022: {
        'G': 1_365_057,
        'K': 57_669,
        'F': 40_034,
        'K_ant': 116_952,  # 2021
        'F_ant': 38_242  # 2021
    },
    2023: {
        'G': 1_275_355,
        'K': 17_682,
        'F': 40_569,
        'K_ant': 57_669,  # 2022
        'F_ant': 40_034  # 2022
    },
    2024: {
        'G': 1_232_589,
        'K': 74_372,
        'F': 40_945,
        'K_ant': 17_682,  # 2023
        'F_ant': 40_569  # 2023
    }
}

print("\n📊 CÁLCULOS DETALLADOS POR AÑO:")
print("-" * 80)

for año, datos in sorted(datos_años.items()):
    print(f"\n🗓️  AÑO {año}:")
    print(f"   G (Ingresos Ordinarios {año}): {datos['G']:,.0f}")
    print(f"   K (CxC Primera {año}): {datos['K']:,.0f}")
    print(f"   F (CxC Segunda {año}): {datos['F']:,.0f}")
    print(f"   K' (CxC Primera {año-1}): {datos['K_ant']:,.0f}")
    print(f"   F' (CxC Segunda {año-1}): {datos['F_ant']:,.0f}")
    
    # Aplicar fórmula
    suma = datos['K'] + datos['F'] + datos['K_ant'] + datos['F_ant']
    promedio = suma / 2
    rotacion = datos['G'] / promedio
    
    print(f"   ➗ Promedio CxC = ({datos['K']:,.0f} + {datos['F']:,.0f} + {datos['K_ant']:,.0f} + {datos['F_ant']:,.0f}) / 2")
    print(f"   ➗ Promedio CxC = {suma:,.0f} / 2 = {promedio:,.2f}")
    print(f"   🎯 Rotación = {datos['G']:,.0f} / {promedio:,.2f} = {rotacion:.3f} veces")

print("\n" + "="*80)
print("✅ VALIDACIÓN COMPLETADA")
print("="*80)
