"""
TEST DE ANÁLISIS EN 3 FASES - Sistema Mejorado
==============================================

Prueba el nuevo sistema que divide el análisis en 3 solicitudes especializadas:
1. Liquidez y Endeudamiento
2. Rentabilidad y Actividad  
3. Conclusión General
"""

from groq import Groq

def test_analisis_3_fases():
    print("="*80)
    print("TEST DE ANÁLISIS EN 3 FASES ESPECIALIZADAS")
    print("="*80 + "\n")
    
    # Datos de ejemplo
    empresa = "CORPORACIÓN EJEMPLO S.A."
    años = [2024, 2023, 2022]
    
    # Ratios de ejemplo
    ratios_por_año = {
        2024: {
            'liquidez_corriente': 1.85,
            'prueba_acida': 1.45,
            'razon_deuda_total': 0.52,
            'razon_deuda_patrimonio': 1.08,
            'margen_neto': 0.08,
            'roa': 0.06,
            'roe': 0.12,
            'rotacion_activos_totales': 1.25,
            'rotacion_cuentas_cobrar': 8.5,
            'rotacion_inventarios': 6.2
        },
        2023: {
            'liquidez_corriente': 1.75,
            'prueba_acida': 1.35,
            'razon_deuda_total': 0.48,
            'razon_deuda_patrimonio': 0.92,
            'margen_neto': 0.07,
            'roa': 0.055,
            'roe': 0.11,
            'rotacion_activos_totales': 1.30,
            'rotacion_cuentas_cobrar': 7.8,
            'rotacion_inventarios': 5.9
        },
        2022: {
            'liquidez_corriente': 1.65,
            'prueba_acida': 1.25,
            'razon_deuda_total': 0.45,
            'razon_deuda_patrimonio': 0.82,
            'margen_neto': 0.065,
            'roa': 0.05,
            'roe': 0.09,
            'rotacion_activos_totales': 1.35,
            'rotacion_cuentas_cobrar': 7.2,
            'rotacion_inventarios': 5.5
        }
    }
    
    # Inicializar cliente
    client = Groq(api_key="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")
    
    analisis_partes = []
    
    # ==================== FASE 1: LIQUIDEZ Y ENDEUDAMIENTO ====================
    print("📊 FASE 1/3: Analizando Liquidez y Endeudamiento...")
    
    prompt1 = f"""Eres un analista financiero experto. Analiza ÚNICAMENTE los ratios de LIQUIDEZ y ENDEUDAMIENTO de {empresa}.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**DATOS DE LIQUIDEZ Y ENDEUDAMIENTO:**
"""
    for año in años:
        ratios = ratios_por_año[año]
        prompt1 += f"\n**{año}:**\n"
        prompt1 += f"• Liquidez Corriente: {ratios['liquidez_corriente']}\n"
        prompt1 += f"• Prueba Ácida: {ratios['prueba_acida']}\n"
        prompt1 += f"• Razón Deuda Total: {ratios['razon_deuda_total']}\n"
        prompt1 += f"• Razón Deuda/Patrimonio: {ratios['razon_deuda_patrimonio']}\n"
    
    prompt1 += """
**INSTRUCCIONES:**
- Analiza SOLO liquidez y endeudamiento (NO menciones rentabilidad ni actividad)
- Sé específico con los números y proporciona análisis DETALLADO
- Identifica tendencias, alertas y explica sus causas probables
- Proporciona contexto comparativo entre años
- Máximo 15-18 líneas

**ESTRUCTURA:**
1. **LIQUIDEZ** (8-9 líneas): Analiza Liquidez Corriente y Prueba Ácida. ¿Puede pagar obligaciones a corto plazo? ¿Cómo ha evolucionado? ¿Qué significa cada cambio? ¿Es saludable para la industria?
2. **ENDEUDAMIENTO** (7-9 líneas): Analiza Razón Deuda Total y Deuda/Patrimonio. ¿Nivel de riesgo? ¿Apalancamiento adecuado? ¿Tendencia? ¿Cómo afecta la capacidad de endeudamiento futuro? ¿Alertas específicas?
"""
    
    completion1 = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "Eres un analista financiero experto en análisis de liquidez y endeudamiento. Proporciona análisis DETALLADOS y específicos centrados ÚNICAMENTE en estos aspectos. Explica causas, consecuencias y contexto."
            },
            {
                "role": "user",
                "content": prompt1
            }
        ],
        temperature=0.6,
        max_tokens=2500,
        top_p=0.9
    )
    
    analisis_partes.append(completion1.choices[0].message.content)
    print("✅ Fase 1 completada\n")
    
    # ==================== FASE 2: RENTABILIDAD Y ACTIVIDAD ====================
    print("💰 FASE 2/3: Analizando Rentabilidad y Eficiencia...")
    
    prompt2 = f"""Eres un analista financiero experto. Analiza ÚNICAMENTE los ratios de RENTABILIDAD y ACTIVIDAD de {empresa}.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**DATOS DE RENTABILIDAD Y ACTIVIDAD:**
"""
    for año in años:
        ratios = ratios_por_año[año]
        prompt2 += f"\n**{año}:**\n"
        prompt2 += f"• Margen Neto: {ratios['margen_neto']}\n"
        prompt2 += f"• ROA: {ratios['roa']}\n"
        prompt2 += f"• ROE: {ratios['roe']}\n"
        prompt2 += f"• Rotación Activos Totales: {ratios['rotacion_activos_totales']}\n"
        prompt2 += f"• Rotación CxC: {ratios['rotacion_cuentas_cobrar']}\n"
        prompt2 += f"• Rotación Inventarios: {ratios['rotacion_inventarios']}\n"
    
    prompt2 += """
**INSTRUCCIONES:**
- Analiza SOLO rentabilidad y actividad (NO menciones liquidez ni endeudamiento)
- Sé específico con los números y proporciona análisis DETALLADO
- Identifica si genera valor para accionistas y explica por qué
- Compara entre años y explica cambios significativos
- Máximo 18-20 líneas

**ESTRUCTURA:**
1. **RENTABILIDAD** (9-10 líneas): Analiza Margen Neto, ROA y ROE. ¿Genera ganancias suficientes? ¿Cómo ha evolucionado cada indicador? ¿El retorno es adecuado para los accionistas? ¿Qué factores pueden estar influyendo? ¿Comparación con tendencias del sector?
2. **EFICIENCIA OPERATIVA** (9-10 líneas): Analiza rotaciones de activos, CxC e inventarios. ¿Uso eficiente de recursos? ¿Qué indican las rotaciones sobre la gestión operativa? ¿Problemas de cobranza o inventarios obsoletos? ¿Tendencia de mejora o deterioro?
"""
    
    completion2 = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "Eres un analista financiero experto en rentabilidad y eficiencia operativa. Proporciona análisis DETALLADOS y específicos centrados ÚNICAMENTE en estos aspectos. Explica causas, impactos y comparaciones."
            },
            {
                "role": "user",
                "content": prompt2
            }
        ],
        temperature=0.6,
        max_tokens=2800,
        top_p=0.9
    )
    
    analisis_partes.append(completion2.choices[0].message.content)
    print("✅ Fase 2 completada\n")
    
    # ==================== FASE 3: CONCLUSIÓN GENERAL ====================
    print("🎯 FASE 3/3: Generando Conclusión General...")
    
    prompt3 = f"""Eres un analista financiero experto. Genera una CONCLUSIÓN GENERAL integradora sobre {empresa}.

**EMPRESA:** {empresa}
**AÑOS:** {', '.join(map(str, años))}

**RESUMEN DE TODOS LOS RATIOS:**
"""
    for año in años:
        ratios = ratios_por_año[año]
        prompt3 += f"\n**{año}:** Liquidez={ratios['liquidez_corriente']}, Deuda={ratios['razon_deuda_total']}, ROE={ratios['roe']}, Rotación={ratios['rotacion_activos_totales']}\n"
    
    prompt3 += """
**INSTRUCCIONES:**
- Integra TODOS los aspectos: liquidez, endeudamiento, rentabilidad y eficiencia
- Identifica el PATRÓN GENERAL entre años con análisis PROFUNDO
- Evalúa salud financiera GLOBAL y perspectivas futuras
- Proporciona 3-4 RECOMENDACIONES específicas, accionables y priorizadas
- Máximo 15-18 líneas

**ESTRUCTURA:**
1. **DIAGNÓSTICO INTEGRAL** (6-7 líneas): ¿Cómo está la empresa en general? ¿Fortalezas principales? ¿Debilidades críticas? ¿Balance entre liquidez, rentabilidad y eficiencia? ¿Posición competitiva probable?
2. **TENDENCIA GLOBAL** (4-5 líneas): ¿Mejorando o deteriorándose? ¿Sostenible a mediano plazo? ¿Riesgos principales? ¿Oportunidades visibles?
3. **RECOMENDACIONES ESTRATÉGICAS** (5-6 líneas): 3-4 acciones concretas prioritarias con justificación breve. ¿Qué hacer primero? ¿Qué evitar?
"""
    
    completion3 = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "Eres un analista financiero senior que integra todos los aspectos financieros para dar un diagnóstico completo y recomendaciones estratégicas. Proporciona análisis PROFUNDO con visión holística y recomendaciones priorizadas."
            },
            {
                "role": "user",
                "content": prompt3
            }
        ],
        temperature=0.6,
        max_tokens=2500,
        top_p=0.9
    )
    
    analisis_partes.append(completion3.choices[0].message.content)
    print("✅ Fase 3 completada\n")
    
    # Combinar resultados
    analisis_completo = f"""# ANÁLISIS FINANCIERO INTEGRAL - {empresa}

## 📊 PARTE 1: ANÁLISIS DE LIQUIDEZ Y ENDEUDAMIENTO

{analisis_partes[0]}

---

## 💰 PARTE 2: ANÁLISIS DE RENTABILIDAD Y EFICIENCIA

{analisis_partes[1]}

---

## 🎯 PARTE 3: CONCLUSIÓN GENERAL Y RECOMENDACIONES

{analisis_partes[2]}

---

*Análisis generado mediante IA (OpenAI GPT-4o-mini via Groq) en 3 fases especializadas*
"""
    
    # Mostrar resultado final
    print("="*80)
    print("ANÁLISIS COMPLETO GENERADO")
    print("="*80)
    print(analisis_completo)
    print("="*80)
    
    # Estadísticas
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Total de caracteres: {len(analisis_completo)}")
    print(f"   Total de líneas: {analisis_completo.count(chr(10)) + 1}")
    print(f"   Fases generadas: 3")
    print(f"\n✅ PRUEBA COMPLETADA EXITOSAMENTE")

if __name__ == "__main__":
    test_analisis_3_fases()
