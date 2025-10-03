"""
TEST DE PROMPT OPTIMIZADO - Análisis de IA
==========================================

Este script prueba el nuevo prompt optimizado que es más conciso y enfocado.
"""

from groq import Groq

def test_prompt_optimizado():
    print("="*70)
    print("TEST DE PROMPT OPTIMIZADO PARA ANÁLISIS DE RATIOS")
    print("="*70 + "\n")
    
    # Datos de ejemplo
    empresa = "EMPRESA EJEMPLO S.A."
    años = [2024, 2023, 2022]
    
    # Ratios de ejemplo (algunos con alertas)
    ratios_por_año = {
        2024: {
            'liquidez_corriente': 0.85,  # ⚠️ ALERTA: Bajo
            'razon_deuda_total': 0.72,   # ⚠️ ALERTA: Alto
            'roe': -0.05,                 # ⚠️ ALERTA: Negativo
            'rotacion_activos_totales': 1.2
        },
        2023: {
            'liquidez_corriente': 1.5,
            'razon_deuda_total': 0.55,
            'roe': 0.08,
            'rotacion_activos_totales': 1.3
        },
        2022: {
            'liquidez_corriente': 2.1,
            'razon_deuda_total': 0.45,
            'roe': 0.12,
            'rotacion_activos_totales': 1.4
        }
    }
    
    # Identificar ratios atípicos
    ratios_alarma = []
    for año in años:
        ratios = ratios_por_año[año]
        if ratios.get('liquidez_corriente') and (ratios['liquidez_corriente'] < 1.0 or ratios['liquidez_corriente'] > 3.0):
            ratios_alarma.append(f"Liquidez Corriente {año}: {ratios['liquidez_corriente']:.2f}")
        if ratios.get('razon_deuda_total') and ratios['razon_deuda_total'] > 0.6:
            ratios_alarma.append(f"Deuda Total {año}: {ratios['razon_deuda_total']:.1%}")
        if ratios.get('roe') and ratios['roe'] < 0:
            ratios_alarma.append(f"ROE {año}: {ratios['roe']:.2%}")
    
    # Construir prompt optimizado
    prompt = f"""Eres un analista financiero experto. Analiza BREVEMENTE los ratios financieros de {empresa} enfocándote en lo MÁS IMPORTANTE.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**RATIOS CLAVE POR AÑO:**
"""
    
    for año in años:
        ratios = ratios_por_año[año]
        prompt += f"\n**{año}:**\n"
        prompt += f"• Liquidez Corriente: {ratios.get('liquidez_corriente', 'N/A')}\n"
        prompt += f"• Razón Deuda Total: {ratios.get('razon_deuda_total', 'N/A')}\n"
        prompt += f"• ROE: {ratios.get('roe', 'N/A')}\n"
        prompt += f"• Rotación Activos: {ratios.get('rotacion_activos_totales', 'N/A')}\n"
    
    if ratios_alarma:
        prompt += f"\n⚠️ **ALERTAS IDENTIFICADAS:**\n"
        for alerta in ratios_alarma[:5]:
            prompt += f"• {alerta}\n"
    
    prompt += """
**INSTRUCCIONES IMPORTANTES:**
- Sé CONCISO y DIRECTO (máximo 1500 palabras)
- Enfócate SOLO en 1-2 ratios MÁS IMPORTANTES por categoría
- Prioriza ALERTAS y valores ATÍPICOS
- Omite explicaciones generales de qué son los ratios
- Ve directo al ANÁLISIS de los números específicos

**ESTRUCTURA REQUERIDA (BREVE):**

1. **LIQUIDEZ** (2-3 líneas): Liquidez Corriente. ¿Alerta? ¿Tendencia?

2. **ENDEUDAMIENTO** (2-3 líneas): Razón Deuda Total. ¿Riesgo? ¿Cambios?

3. **RENTABILIDAD** (3-4 líneas): ROE principalmente. ¿Genera valor? ¿Mejora/empeora?

4. **EFICIENCIA** (2-3 líneas): Rotación de Activos. ¿Uso eficiente?

5. **TENDENCIAS CLAVE** (3-4 líneas): Patrón general entre años. ¿Mejora o deterioro?

6. **CONCLUSIÓN Y ACCIÓN** (3-4 líneas): Salud financiera general. 1-2 recomendaciones específicas.

TOTAL: Máximo 20 líneas de análisis."""
    
    print("PROMPT GENERADO:")
    print("-"*70)
    print(prompt)
    print("-"*70)
    print()
    
    # Llamar a Groq
    print("Enviando solicitud a Groq...")
    print()
    
    try:
        client = Groq(api_key="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")
        
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un analista financiero senior experto en análisis de ratios. Proporciona análisis concisos, directos y enfocados en lo más relevante. Evita definiciones generales y ve directo al análisis de los números específicos."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=3000,
            top_p=0.9
        )
        
        respuesta = completion.choices[0].message.content
        
        print("="*70)
        print("RESPUESTA DEL MODELO (OPTIMIZADA):")
        print("="*70)
        print(respuesta)
        print("="*70)
        print()
        
        # Estadísticas
        tokens_usados = completion.usage.total_tokens if hasattr(completion, 'usage') else 'N/A'
        print(f"✅ Tokens utilizados: {tokens_usados}")
        print(f"✅ Longitud de respuesta: {len(respuesta)} caracteres")
        print(f"✅ Líneas de respuesta: {respuesta.count(chr(10)) + 1}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_prompt_optimizado()
