# 🤖 Análisis Inteligente de Ratios Financieros con IA

## 📋 Descripción

Se ha integrado un módulo de análisis inteligente que utiliza el modelo **OpenAI GPT-4o-mini** a través de la API de **Groq** para analizar automáticamente los ratios financieros calculados y generar comentarios profesionales y conclusiones estratégicas.

## ✨ Características

### 🎯 Análisis Automatizado

El sistema analiza automáticamente:

1. **Ratios de Liquidez**
   - Liquidez Corriente
   - Prueba Ácida

2. **Ratios de Endeudamiento**
   - Razón de Deuda Total
   - Razón Deuda/Patrimonio

3. **Ratios de Rentabilidad**
   - Margen Neto
   - ROA (Return on Assets)
   - ROE (Return on Equity)

4. **Ratios de Actividad**
   - Rotación de Activos Totales
   - Rotación de Cuentas por Cobrar
   - Rotación de Inventarios

### 📊 Salidas del Análisis

El análisis de IA proporciona:

- ✅ **Evaluación de liquidez**: Capacidad para cumplir obligaciones a corto plazo
- ✅ **Evaluación de endeudamiento**: Nivel de apalancamiento y riesgo financiero
- ✅ **Evaluación de rentabilidad**: Capacidad de generación de ganancias
- ✅ **Evaluación de eficiencia**: Uso eficiente de los activos
- ✅ **Identificación de tendencias**: Patrones entre diferentes períodos
- ✅ **Recomendaciones estratégicas**: Sugerencias basadas en los datos

## 🚀 Cómo Usar

### 1. Acceder a la Funcionalidad

1. Ejecuta la aplicación Streamlit:
   ```bash
   streamlit run analizador_financiero.py
   ```

2. Carga archivos XLS con estados financieros (formato POST-2010)

3. Ve a la pestaña **"Vista Consolidada - Ratios"**

4. Desplázate hasta la sección **"🤖 Análisis Inteligente con IA"**

5. Haz clic en el botón **"🔍 Generar Análisis con IA"**

### 2. Ver y Descargar Resultados

- El análisis se mostrará en un panel expandible
- Puedes descargar el análisis en formato TXT usando el botón de descarga

## 🔧 Configuración Técnica

### Modelo de IA Utilizado

- **Modelo**: `openai/gpt-oss-20b`
- **Proveedor**: Groq (API de inferencia ultra-rápida)
- **Temperatura**: 0.7 (balance entre creatividad y precisión)
- **Max Tokens**: 2000 (suficiente para análisis detallado)

### API Key

La API key está configurada directamente en el código:
```python
client = Groq(api_key="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")
```

⚠️ **Nota de Seguridad**: En un entorno de producción, considera usar variables de entorno para almacenar la API key:
```python
import os
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
```

## 📦 Dependencias

### Nueva Dependencia Instalada

```bash
pip install groq
```

### Verificar Instalación

Ejecuta el script de prueba:
```bash
python test_groq_integration.py
```

## 🎨 Interfaz de Usuario

### Ubicación en la Aplicación

```
📊 Analizador Financiero
└── 📋 Tab: "Vista Consolidada - Ratios"
    ├── 📊 Tabla de Ratios
    ├── 📊 Resumen Estadístico
    ├── 📈 Gráficos de Tendencias
    ├── 🤖 Análisis Inteligente con IA  ← NUEVA SECCIÓN
    │   ├── Botón: "🔍 Generar Análisis con IA"
    │   ├── Panel: Análisis Completo
    │   └── Botón: "📥 Descargar Análisis de IA"
    └── 📥 Exportar Ratios a Excel
```

## 📝 Ejemplo de Prompt Enviado a la IA

```
Eres un analista financiero experto. Analiza los siguientes ratios financieros 
de la empresa [NOMBRE] y proporciona comentarios detallados y conclusiones profesionales.

**DATOS DE RATIOS FINANCIEROS:**

Años analizados: 2024, 2023, 2022

**RATIOS POR AÑO:**

Año 2024:
- Liquidez Corriente: 2.34
- Prueba Ácida: 1.98
- Razón de Deuda Total: 0.45
...

Por favor, proporciona:
1. Análisis de Liquidez
2. Análisis de Endeudamiento
3. Análisis de Rentabilidad
4. Análisis de Actividad
5. Tendencias Observadas
6. Conclusiones y Recomendaciones
```

## ⚡ Ventajas de Usar Groq

1. **Ultra-rápido**: Inferencia en milisegundos
2. **Rentable**: Precios competitivos
3. **Compatible**: API compatible con OpenAI
4. **Modelos variados**: Acceso a múltiples LLMs

## 🔍 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'groq'"

**Solución**: Instala el paquete groq
```bash
pip install groq
```

### Error: "Authentication failed"

**Solución**: Verifica que la API key sea correcta y esté activa en tu cuenta de Groq

### Error: "Rate limit exceeded"

**Solución**: Groq tiene límites de rate. Espera unos minutos antes de hacer otra solicitud

## 📚 Referencias

- [Groq API Documentation](https://console.groq.com/docs)
- [Groq Python SDK](https://github.com/groq/groq-python)
- [OpenAI API Compatibility](https://platform.openai.com/docs/api-reference)

## 🎓 Mejoras Futuras

- [ ] Agregar selección de modelo (permitir elegir entre diferentes LLMs)
- [ ] Implementar caché de análisis para evitar llamadas repetidas
- [ ] Agregar comparación con benchmarks de industria
- [ ] Generar visualizaciones adicionales basadas en el análisis de IA
- [ ] Exportar análisis en formato PDF con formato profesional

## 👨‍💻 Autor

Integración desarrollada para el sistema de Análisis Financiero V4

---

**Fecha de implementación**: 2 de octubre de 2025
