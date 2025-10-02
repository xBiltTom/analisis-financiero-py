"""
Script para arreglar la indentación del archivo analizador_financiero.py
"""

# Leer el archivo
with open('analizador_financiero.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar y eliminar las líneas duplicadas (1064-1090)
# Mantener solo la sección correcta

# Buscar "with tab5:" duplicado
tab5_indices = []
for i, line in enumerate(lines):
    if 'with tab5:' in line:
        tab5_indices.append(i)
        print(f"Encontrado 'with tab5:' en línea {i+1}")

# Si hay duplicados, eliminar el primero (que tiene código incorrecto)
if len(tab5_indices) >= 2:
    print(f"\nEliminando líneas {tab5_indices[0]+1} a {tab5_indices[1]}")
    # Eliminar desde el primer tab5 hasta antes del segundo
    del lines[tab5_indices[0]:tab5_indices[1]]
    print("✅ Líneas duplicadas eliminadas")

# Guardar el archivo corregido
with open('analizador_financiero.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Archivo corregido y guardado")
