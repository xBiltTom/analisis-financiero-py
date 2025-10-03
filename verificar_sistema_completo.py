"""
CHECKLIST FINAL DE VERIFICACIÓN
================================

Ejecuta este script para verificar que todo está instalado y configurado correctamente.
"""

def verificar_instalacion():
    print("="*70)
    print("VERIFICACIÓN DE INSTALACIÓN - ANÁLISIS CON IA")
    print("="*70)
    print()
    
    # 1. Verificar importaciones
    print("1. Verificando importaciones...")
    try:
        import streamlit
        print("   ✅ Streamlit instalado")
    except ImportError:
        print("   ❌ Streamlit NO instalado")
        return False
    
    try:
        from groq import Groq
        print("   ✅ Groq instalado")
    except ImportError:
        print("   ❌ Groq NO instalado")
        return False
    
    try:
        import pandas
        print("   ✅ Pandas instalado")
    except ImportError:
        print("   ❌ Pandas NO instalado")
        return False
    
    print()
    
    # 2. Verificar conexión con Groq
    print("2. Verificando conexión con API de Groq...")
    try:
        client = Groq(api_key="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")
        
        # Hacer una llamada de prueba mínima
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": "Di 'OK'"}],
            max_tokens=10
        )
        
        print("   ✅ Conexión exitosa con Groq API")
        print(f"   📝 Respuesta de prueba: {completion.choices[0].message.content}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False
    
    print()
    
    # 3. Verificar archivos
    print("3. Verificando archivos del proyecto...")
    archivos_requeridos = [
        "analizador_financiero.py",
        "ratios_financieros.py",
        "extractor_estados_mejorado.py",
        "analisis_vertical_consolidado.py",
        "analisis_horizontal_consolidado.py"
    ]
    
    import os
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} NO encontrado")
            return False
    
    print()
    
    # 4. Verificar documentación
    print("4. Verificando documentación...")
    docs_requeridos = [
        "ANALISIS_IA_README.md",
        "GUIA_RAPIDA_IA.txt",
        "IMPLEMENTACION_COMPLETADA.md"
    ]
    
    for doc in docs_requeridos:
        if os.path.exists(doc):
            print(f"   ✅ {doc}")
        else:
            print(f"   ⚠️  {doc} NO encontrado (opcional)")
    
    print()
    
    # 5. Verificar función en código
    print("5. Verificando función analizar_ratios_con_ia()...")
    try:
        with open('analizador_financiero.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            if 'def analizar_ratios_con_ia' in contenido:
                print("   ✅ Función analizar_ratios_con_ia encontrada")
            else:
                print("   ❌ Función NO encontrada")
                return False
            
            if 'from groq import Groq' in contenido:
                print("   ✅ Import de Groq encontrado")
            else:
                print("   ❌ Import de Groq NO encontrado")
                return False
            
            if 'Análisis Inteligente con IA' in contenido:
                print("   ✅ UI de análisis IA encontrada")
            else:
                print("   ❌ UI de análisis IA NO encontrada")
                return False
    except Exception as e:
        print(f"   ❌ Error al verificar código: {str(e)}")
        return False
    
    print()
    print("="*70)
    print("✅ ¡TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE!")
    print("="*70)
    print()
    print("🚀 El sistema está listo para usar.")
    print()
    print("Para iniciar la aplicación, ejecuta:")
    print("   streamlit run analizador_financiero.py")
    print()
    print("Luego navega a la pestaña 'Vista Consolidada - Ratios'")
    print("y busca la sección '🤖 Análisis Inteligente con IA'")
    print()
    
    return True

if __name__ == "__main__":
    try:
        exito = verificar_instalacion()
        if not exito:
            print()
            print("="*70)
            print("❌ VERIFICACIÓN FALLIDA")
            print("="*70)
            print()
            print("Por favor revisa los errores anteriores y corrígelos.")
            print()
    except Exception as e:
        print()
        print("="*70)
        print(f"❌ ERROR INESPERADO: {str(e)}")
        print("="*70)
        import traceback
        print(traceback.format_exc())
