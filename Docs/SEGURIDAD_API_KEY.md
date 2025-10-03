# 🔐 SEGURIDAD: SEPARACIÓN DE API KEY

## 📋 Resumen del Cambio

**Fecha:** 3 de octubre de 2025  
**Objetivo:** Proteger la API key de Groq separándola del código fuente

---

## 🎯 Problema Resuelto

### ❌ ANTES (Inseguro)
```python
# API key hardcoded en analizador_financiero.py
client = Groq(api_key="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")
```

**Riesgos:**
- ❌ API key visible en el código
- ❌ Se sube a Git expuesta
- ❌ Cualquiera con acceso al repo puede usar la key
- ❌ Difícil de rotar/cambiar

### ✅ DESPUÉS (Seguro)
```python
# API key en archivo separado (ignorado por Git)
from config_api import GROQ_API_KEY
client = Groq(api_key=GROQ_API_KEY)
```

**Beneficios:**
- ✅ API key en archivo separado
- ✅ `config_api.py` en `.gitignore`
- ✅ No se sube a Git
- ✅ Fácil de rotar sin tocar el código
- ✅ Template para nuevos usuarios

---

## 📁 Archivos Creados

### 1. `config_api.py` (IGNORADO POR GIT)
**Propósito:** Contiene las credenciales reales

```python
# ⚠️ ARCHIVO SENSIBLE - NO DEBE SUBIRSE A GIT

# API Key de Groq (https://console.groq.com/)
GROQ_API_KEY = "gsk_B9209fd..."  # Tu API key real

# Configuración del modelo de IA
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_TEMPERATURE = 0.6
GROQ_MAX_TOKENS_FASE1 = 2500
GROQ_MAX_TOKENS_FASE2 = 2800
GROQ_MAX_TOKENS_FASE3 = 2500
GROQ_TOP_P = 0.9
```

**Características:**
- ✅ Contiene API key real
- ✅ Está en `.gitignore`
- ✅ NO se sube a Git
- ✅ Cada usuario tiene su propia copia

### 2. `config_api.template.py` (SUBIDO A GIT)
**Propósito:** Template para nuevos usuarios

```python
# API Key de Groq (https://console.groq.com/)
GROQ_API_KEY = "TU_API_KEY_AQUI"  # 👈 REEMPLAZA ESTO

# Configuración del modelo de IA
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_TEMPERATURE = 0.6
...
```

**Características:**
- ✅ Template sin credenciales reales
- ✅ Subido a Git (seguro)
- ✅ Instrucciones de configuración
- ✅ Valores por defecto

### 3. `.gitignore` (ACTUALIZADO)
**Agregado:**
```gitignore
# ⚠️ CONFIGURACIÓN SENSIBLE - NO SUBIR A GIT
config_api.py
.env
```

---

## 🚀 Configuración Inicial

### Para Usuario Nuevo (Sin API Key)

**Paso 1:** Copiar template
```bash
copy config_api.template.py config_api.py
```

**Paso 2:** Obtener API key
1. Ir a: https://console.groq.com/
2. Registrarse o iniciar sesión
3. Navegar a "API Keys"
4. Crear nueva API key
5. Copiar la key

**Paso 3:** Editar `config_api.py`
```python
# Reemplazar esto:
GROQ_API_KEY = "TU_API_KEY_AQUI"

# Con tu API key real:
GROQ_API_KEY = "gsk_tu_api_key_real_aqui"
```

**Paso 4:** Verificar
```bash
python -c "from config_api import GROQ_API_KEY; print('✅ Configurado correctamente')"
```

---

## 🔄 Cambios en el Código

### analizador_financiero.py

**1. Import de configuración:**
```python
# Importar configuración de API
try:
    from config_api import (
        GROQ_API_KEY,
        GROQ_MODEL,
        GROQ_TEMPERATURE,
        GROQ_MAX_TOKENS_FASE1,
        GROQ_MAX_TOKENS_FASE2,
        GROQ_MAX_TOKENS_FASE3,
        GROQ_TOP_P
    )
except ImportError:
    st.error("""
    ❌ Error: Archivo de configuración no encontrado
    
    Por favor, crea el archivo config_api.py...
    """)
    st.stop()
```

**2. Uso de constantes:**
```python
# ANTES:
client = Groq(api_key="gsk_B9209fd...")
completion = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    temperature=0.6,
    max_tokens=2500,
    ...
)

# DESPUÉS:
client = Groq(api_key=GROQ_API_KEY)
completion = client.chat.completions.create(
    model=GROQ_MODEL,
    temperature=GROQ_TEMPERATURE,
    max_tokens=GROQ_MAX_TOKENS_FASE1,
    ...
)
```

---

## 🔐 Seguridad Mejorada

### Capas de Protección

**1. Separación de credenciales**
- API key NO está en el código
- Archivo separado `config_api.py`

**2. .gitignore**
- `config_api.py` ignorado
- NO se sube a repositorio

**3. Template seguro**
- `config_api.template.py` sin credenciales
- Subido a Git sin riesgos

**4. Validación en runtime**
- Error claro si falta configuración
- Instrucciones de configuración

**5. Documentación**
- Guía clara de configuración
- Buenas prácticas documentadas

---

## 📊 Beneficios del Cambio

### Seguridad
✅ API key no expuesta en código  
✅ No se sube a Git  
✅ Cada usuario tiene su propia key  
✅ Fácil rotación de credenciales

### Mantenibilidad
✅ Configuración centralizada  
✅ Fácil de actualizar  
✅ Sin tocar código para cambiar key  
✅ Template para nuevos usuarios

### Flexibilidad
✅ Diferentes keys por entorno  
✅ Configuración por usuario  
✅ Parámetros del modelo centralizados  
✅ Fácil agregar nuevas configuraciones

---

## ⚠️ Advertencias de Seguridad

### ❌ NO HACER:

1. **NO subir `config_api.py` a Git**
   ```bash
   # Verificar que está en .gitignore
   git check-ignore config_api.py
   # Debe devolver: config_api.py
   ```

2. **NO hacer commit con API key**
   ```bash
   # ANTES de commit, verificar:
   git status
   # NO debe aparecer config_api.py
   ```

3. **NO compartir archivo config_api.py**
   - Cada usuario debe tener su propia copia
   - Usar config_api.template.py para compartir

4. **NO hardcodear API key nuevamente**
   - Siempre usar las constantes de config_api
   - No volver a escribir la key en el código

### ✅ HACER:

1. **Verificar .gitignore**
   ```bash
   cat .gitignore | findstr config_api
   ```

2. **Rotar API key si se expone**
   - Ir a https://console.groq.com/
   - Revocar key expuesta
   - Generar nueva key
   - Actualizar config_api.py

3. **Mantener template actualizado**
   - Actualizar config_api.template.py
   - Documentar nuevos parámetros
   - Mantener valores por defecto

---

## 🔄 Rotación de API Key

### Cuándo Rotar

- ⚠️ Si la key se expone accidentalmente
- ⚠️ Si se sube a Git por error
- ⚠️ Cada 90 días (buena práctica)
- ⚠️ Al cambiar de equipo/proyecto

### Cómo Rotar

**1. Revocar key antigua:**
- Ir a: https://console.groq.com/
- Encontrar la key actual
- Click "Revoke" o "Delete"

**2. Generar nueva key:**
- Click "Create API Key"
- Copiar la nueva key

**3. Actualizar config_api.py:**
```python
# Reemplazar:
GROQ_API_KEY = "gsk_key_antigua"

# Con:
GROQ_API_KEY = "gsk_key_nueva"
```

**4. Verificar:**
```bash
streamlit run analizador_financiero.py
# Probar análisis con IA
```

---

## 📝 Checklist de Seguridad

Antes de hacer commit:

- [ ] `config_api.py` está en `.gitignore`
- [ ] `config_api.py` NO aparece en `git status`
- [ ] `config_api.template.py` NO tiene API key real
- [ ] Template tiene "TU_API_KEY_AQUI" como placeholder
- [ ] Código usa constantes de config_api
- [ ] No hay API keys hardcoded en el código
- [ ] Documentación actualizada

Antes de compartir proyecto:

- [ ] README menciona config_api.template.py
- [ ] Instrucciones claras de configuración
- [ ] `.gitignore` actualizado
- [ ] Template subido a Git
- [ ] config_api.py NO incluido

---

## 🎓 Buenas Prácticas

### Variables de Entorno (Opcional - Avanzado)

Para mayor seguridad, también puedes usar variables de entorno:

**1. Crear archivo `.env`:**
```bash
GROQ_API_KEY=gsk_tu_api_key_aqui
GROQ_MODEL=openai/gpt-oss-20b
```

**2. Cargar en Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```

**3. Agregar `.env` a `.gitignore`:**
```gitignore
.env
config_api.py
```

### Gestión de Secretos (Producción)

Para entornos de producción:

- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Secret Manager**
- **HashiCorp Vault**

---

## 📚 Referencias

- **Groq Console:** https://console.groq.com/
- **Git Ignore:** https://git-scm.com/docs/gitignore
- **Python-dotenv:** https://pypi.org/project/python-dotenv/

---

## ✅ Verificación Final

**Estado del sistema después del cambio:**

```
✅ config_api.py creado (con API key real)
✅ config_api.template.py creado (template seguro)
✅ .gitignore actualizado
✅ analizador_financiero.py modificado
✅ API key removida del código
✅ Configuración centralizada
✅ Sistema funcionando normalmente
```

**Archivos en Git:**
- ✅ `config_api.template.py` (SÍ subir)
- ✅ `.gitignore` (SÍ subir)
- ✅ `analizador_financiero.py` (SÍ subir)
- ❌ `config_api.py` (NO subir - ignorado)

---

**Última actualización:** 3 de octubre de 2025  
**Seguridad:** ✅ MEJORADA  
**Estado:** ✅ IMPLEMENTADO
