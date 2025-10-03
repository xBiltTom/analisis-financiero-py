"""
Script de prueba para verificar la integración con Groq
"""
from groq import Groq

def test_groq_connection():
    """Prueba la conexión con Groq usando la API key"""
    try:
        print("="*70)
        print("PRUEBA DE CONEXIÓN CON GROQ API")
        print("="*70 + "\n")
        
        # Inicializar cliente
        client = Groq(api_key="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")
        
        print("✅ Cliente Groq inicializado correctamente")
        print("📡 Enviando solicitud de prueba al modelo openai/gpt-oss-20b...")
        
        # Hacer una solicitud de prueba
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": "Explica brevemente qué es un ratio de liquidez corriente en finanzas."
                }
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        print("\n✅ Respuesta recibida exitosamente!\n")
        print("="*70)
        print("RESPUESTA DEL MODELO:")
        print("="*70)
        print(completion.choices[0].message.content)
        print("="*70)
        
        print("\n✅ PRUEBA EXITOSA - La integración con Groq funciona correctamente")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_groq_connection()
