"""
Script para eliminar archivos no necesarios del proyecto
=========================================================
Identifica y elimina archivos de prueba, debug y no utilizados
"""
import os
import shutil

# ========== ARCHIVOS ESENCIALES DEL PROGRAMA PRINCIPAL ==========
archivos_esenciales = {
    # Programa principal
    'analizador_financiero.py',
    
    # Módulos de análisis (importados por analizador_financiero.py)
    'analisis_vertical_horizontal.py',
    'extractor_estados_mejorado.py',
    'analisis_vertical_mejorado.py',
    'analisis_horizontal_mejorado.py',
    'analisis_vertical_consolidado.py',
    'analisis_horizontal_consolidado.py',
    'ratios_financieros.py',
    'descargador_smv.py',
    
    # Este script de limpieza
    'limpiar_archivos.py'
}

# ========== ARCHIVOS A ELIMINAR ==========
archivos_a_eliminar = {
    # Archivos de prueba (test_*.py)
    'test_analisis_2009.py',
    'test_analisis_3_fases.py',
    'test_analisis_horizontal_integracion.py',
    'test_analisis_vertical.py',
    'test_analizador.py',
    'test_archivo_real_2009.py',
    'test_consolidacion.py',
    'test_consolidacion_completa.py',
    'test_consolidacion_debug.py',
    'test_consolidacion_patrimonio.py',
    'test_consolidacion_simple.py',
    'test_cuentas_folder.py',
    'test_extractor.py',
    'test_filtro_simple.py',
    'test_fix_cuentas_cobrar.py',
    'test_graficos_consolidado.py',
    'test_graficos_horizontal_consolidado.py',
    'test_groq_integration.py',
    'test_horizontal_consolidado.py',
    'test_mejoras_v2.py',
    'test_patrimonio_mejorado.py',
    'test_patrones_2009.py',
    'test_prompt_optimizado.py',
    'test_ratios_actividad.py',
    'test_ratios_financieros.py',
    'test_ratios_rentabilidad.py',
    'test_vertical_consolidado.py',
    
    # Archivos de debug (debug_*.py)
    'debug_cxc_pattern.py',
    'debug_estructura_balance.py',
    'debug_inventarios.py',
    
    # Archivos de análisis manual
    'analizar_patrimonio.py',
    'analizar_patrimonio_html.py',
    'validacion_manual_cxc.py',
    
    # Archivos de verificación
    'verificar_analisis.py',
    'verificar_años_consolidar.py',
    'verificar_descargador.py',
    'verificar_sistema_completo.py',
    
    # Archivos de resumen (RESUMEN_*.py - solo ejemplos, no ejecutables)
    'RESUMEN_ANALISIS_VERTICAL_CONSOLIDADO.py',
    'RESUMEN_CAMBIOS_IA.py',
    'RESUMEN_CORRECCION.py',
    'RESUMEN_MEJORAS_PATRIMONIO.py',
    
    # Archivos de corrección temporal
    'fix_indentation.py',
    
    # Backup
    'analizador_financiero_backup.py',
    
    # Utilidades no usadas
    'utils_financieros.py'
}

def eliminar_archivos():
    """Elimina archivos no necesarios de forma segura"""
    
    print("="*80)
    print("LIMPIEZA DE ARCHIVOS NO NECESARIOS")
    print("="*80)
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('analizador_financiero.py'):
        print("❌ ERROR: No se encuentra analizador_financiero.py")
        print("   Ejecuta este script desde el directorio del proyecto")
        return
    
    print("\n📋 ARCHIVOS ESENCIALES (se mantendrán):")
    for archivo in sorted(archivos_esenciales):
        if os.path.exists(archivo):
            print(f"  ✅ {archivo}")
        else:
            print(f"  ⚠️ {archivo} (no encontrado)")
    
    print(f"\n🗑️ ARCHIVOS A ELIMINAR ({len(archivos_a_eliminar)}):")
    archivos_eliminados = []
    archivos_no_encontrados = []
    
    for archivo in sorted(archivos_a_eliminar):
        if os.path.exists(archivo):
            print(f"  🔴 {archivo}")
            archivos_eliminados.append(archivo)
        else:
            archivos_no_encontrados.append(archivo)
    
    if archivos_no_encontrados:
        print(f"\n⚠️ Archivos ya eliminados o no encontrados ({len(archivos_no_encontrados)}):")
        for archivo in sorted(archivos_no_encontrados):
            print(f"  - {archivo}")
    
    # Auto-confirmar (sin interacción)
    print(f"\n{'='*80}")
    print(f"Se eliminarán {len(archivos_eliminados)} archivos")
    print("="*80)
    print("\n✅ Procediendo con la eliminación automática...")
    
    # Crear carpeta backup
    backup_dir = "archivos_eliminados_backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"\n📁 Creada carpeta de backup: {backup_dir}")
    
    # Eliminar archivos
    print(f"\n🗑️ Eliminando archivos...")
    eliminados_exitosos = 0
    errores = []
    
    for archivo in archivos_eliminados:
        try:
            # Hacer backup primero
            shutil.copy2(archivo, os.path.join(backup_dir, archivo))
            
            # Eliminar archivo
            os.remove(archivo)
            print(f"  ✅ Eliminado: {archivo}")
            eliminados_exitosos += 1
            
        except Exception as e:
            print(f"  ❌ Error al eliminar {archivo}: {str(e)}")
            errores.append((archivo, str(e)))
    
    # Resumen final
    print(f"\n{'='*80}")
    print("RESUMEN DE LIMPIEZA")
    print("="*80)
    print(f"✅ Archivos eliminados: {eliminados_exitosos}")
    print(f"❌ Errores: {len(errores)}")
    print(f"💾 Backup guardado en: {backup_dir}")
    
    if errores:
        print(f"\n⚠️ Errores encontrados:")
        for archivo, error in errores:
            print(f"  - {archivo}: {error}")
    
    # Mostrar archivos restantes
    print(f"\n📂 ARCHIVOS PYTHON RESTANTES:")
    archivos_restantes = sorted([f for f in os.listdir('.') if f.endswith('.py')])
    for archivo in archivos_restantes:
        print(f"  📄 {archivo}")
    
    print(f"\n{'='*80}")
    print("✅ LIMPIEZA COMPLETADA")
    print("="*80)
    print("\n💡 NOTAS:")
    print("  • Los archivos eliminados están respaldados en 'archivos_eliminados_backup/'")
    print("  • Si algo falla, puedes restaurar desde el backup")
    print("  • Ejecuta 'streamlit run analizador_financiero.py' para verificar")

if __name__ == "__main__":
    eliminar_archivos()
