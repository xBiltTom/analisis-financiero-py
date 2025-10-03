"""
Configuración de API Keys - TEMPLATE
====================================

📝 INSTRUCCIONES DE USO:

1. Copia este archivo a 'config_api.py':
   ```
   copy config_api.template.py config_api.py
   ```

2. Edita 'config_api.py' y reemplaza "TU_API_KEY_AQUI" con tu API key real

3. Obtén tu API key de Groq:
   - Visita: https://console.groq.com/
   - Regístrate o inicia sesión
   - Ve a "API Keys"
   - Crea una nueva API key
   - Copia y pega en config_api.py

⚠️ IMPORTANTE:
   - NO edites este archivo template
   - NO subas config_api.py a Git (está en .gitignore)
   - Mantén tu API key privada
"""

# API Key de Groq (https://console.groq.com/)
GROQ_API_KEY = "TU_API_KEY_AQUI"  # 👈 REEMPLAZA ESTO CON TU API KEY REAL

# Configuración del modelo de IA
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_TEMPERATURE = 0.6
GROQ_MAX_TOKENS_FASE1 = 2500
GROQ_MAX_TOKENS_FASE2 = 2800
GROQ_MAX_TOKENS_FASE3 = 2500
GROQ_TOP_P = 0.9
