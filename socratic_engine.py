"""
Motor Socrático de IA para Pensamiento Crítico en Economía.
Implementa el sistema pedagógico estricto: prohíbe resolver o dar respuestas
directas al estudiante y obliga a formular repreguntas analíticas profundas.
"""

import os
import json
import streamlit as st
from typing import Dict, Any, List

# Prompt Socrático rígido basado en los requisitos pedagógicos de la U.I.A.
PROMPT_SOCRATICO_SISTEMA = """
Eres el Tutor Socrático de la Cátedra de Economía de la Universidad Internacional de las Américas (U.I.A.).
Tu público son estudiantes de primer ingreso que están debatiendo el texto de Lynn Alden: "Inflación impulsada por el fiscal" (comparación histórica entre los años 1940 y 1970, ciclo de deuda a largo plazo, dominancia fiscal vs. crédito bancario privado, control de la curva de rendimientos y dinero helicóptero).

REGLAS PEDAGÓGICAS ABSOLUTAS:
1. TIENES ESTRICTAMENTE PROHIBIDO DAR LA RESPUESTA CORRECTA O RESOLVER EL DILEMA POR EL ALUMNO.
2. Si el alumno hace una afirmación superficial o comete un error conceptual (por ejemplo, creer que subir la tasa de interés resuelve una inflación con 130% de deuda pública sobre el PIB sin consecuencias fiscales graves), NO LO CORRIJAS DIRECTAMENTE. En su lugar, formula una repregunta incisiva que devele la contradicción o el trade-off oculto.
3. Estimula las 6 habilidades de pensamiento crítico:
   - Interpretar datos (M2 vs préstamos bancarios).
   - Analizar causas y efectos estructurales.
   - Evaluar trade-offs de política económica.
   - Inferir consecuencias de segundo y tercer orden.
   - Justificar posturas con rigor lógico y evidencia histórica.
   - Contrastar la postura monetarista pura (años 70) con la dominancia fiscal (años 40 y 2020s).
4. Sé retador, académico pero motivador, manteniendo respuestas breves y focalizadas (máximo 2 a 3 párrafos cortos y 1 o 2 preguntas directas que obliguen al estudiante a profundizar).
5. Debes evaluar de manera interna y objetiva el nivel del alumno (del 0 al 10) en rigor conceptual, justificación y detección de trade-offs.

FORMATO DE SALIDA REQUERIDO:
Debes responder SIEMPRE en formato JSON con la siguiente estructura:
{
  "comentario_socratico": "Tu respuesta socrática pedagógica para el estudiante aquí.",
  "nivel_rigor": "Bajo" | "Medio" | "Alto",
  "puntuacion_parcial": 8.5,
  "observacion_pedagogica": "Breve nota pedagógica sobre la premisa del estudiante."
}
"""

def consultar_tutor_socratico(
    historial_mensajes: List[Dict[str, str]], 
    escenario_actual: str,
    eleccion_estudiante: str
) -> Dict[str, Any]:
    """
    Invoca el modelo LLM para generar una repregunta socrática.
    Soporta Google Gemini si existe GEMINI_API_KEY en st.secrets u os.environ,
    y cuenta con un motor heurístico socrático de respaldo para contingencias.
    """
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            
            prompt_contexto = f"""
            ESCENARIO EN DEBATE:
            {escenario_actual}
            
            DECISIÓN / HIPÓTESIS DEL ESTUDIANTE:
            {eleccion_estudiante}
            
            HISTORIAL DE DISCUSIÓN HASTA AHORA:
            {json.dumps(historial_mensajes, ensure_ascii=False)}
            
            Analiza el último mensaje del alumno y genera la repregunta socrática en JSON.
            """
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_contexto,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_SOCRATICO_SISTEMA,
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            
            data = json.loads(response.text)
            return data
        except Exception as e:
            # En caso de error de conexión a la API externa, recurrir al motor heurístico pedagógico
            print(f"Aviso: Usando motor heurístico por: {e}")

    # Motor Socrático Heurístico Pedagógico de Respaldo
    return _generar_repregunta_heuristica(eleccion_estudiante, escenario_actual)

def _generar_repregunta_heuristica(mensaje: str, escenario: str) -> Dict[str, Any]:
    """Motor heurístico basado estrictamente en el contenido de Lynn Alden."""
    msg = mensaje.lower()
    
    if any(k in msg for k in ["subir tasa", "tasas altas", "volcker", "tasa de interes", "endurecer"]):
        pregunta = (
            "Propones una política similar a la aplicada por Volcker en los años 70. "
            "Sin embargo, de acuerdo con el análisis de Lynn Alden, en los años 70 la deuda pública era de apenas ~30% del PIB, "
            "mientras que hoy y en los años 40 supera el 100%. "
            "¿Qué pasaría con el déficit fiscal y el costo financiero de la deuda si el gobierno debe pagar un 6% o 10% anual "
            "sobre una deuda de 30 billones de dólares? ¿Frenaría eso la inflación o crearía una espiral de mayor emisión fiscal?"
        )
        return {
            "comentario_socratico": pregunta,
            "nivel_rigor": "Medio",
            "puntuacion_parcial": 6.5,
            "observacion_pedagogica": "Aplica recetas de los 70 ignorando la restricción de deuda/PIB de los 40."
        }
    
    elif any(k in msg for k in ["imprimir", "gasto", "estimulo", "deficit", "helicoptero"]):
        pregunta = (
            "Mencionas expandir el gasto fiscal o mantener estímulos. Si la capacidad productiva de materias primas y "
            "cadenas de suministro globales está saturada (cuello de botella de oferta), ¿a dónde se desplaza el exceso "
            "de circulante (M2) inyectado directamente en los bolsillos de los consumidores? "
            "¿Es posible aumentar la demanda agregada nominal sin desencadenar una pérdida de poder adquisitivo?"
        )
        return {
            "comentario_socratico": pregunta,
            "nivel_rigor": "Medio",
            "puntuacion_parcial": 7.0,
            "observacion_pedagogica": "Reconoce el canal fiscal pero no considera la restricción de oferta física."
        }
        
    elif any(k in msg for k in ["control", "curva", "rendimientos", "represion", "fijar"]):
        pregunta = (
            "Has identificado el mecanismo de represión financiera y control de la curva de rendimientos implementado en 1942-1951. "
            "Si el Banco Central mantiene los rendimientos de los bonos en 2.5% mientras la inflación corre al 8%, "
            "¿quién está pagando realmente el costo de licuar la deuda pública? ¿Qué repercusiones tiene esto sobre los ahorrantes "
            "y los fondos de pensiones del país?"
        )
        return {
            "comentario_socratico": pregunta,
            "nivel_rigor": "Alto",
            "puntuacion_parcial": 8.5,
            "observacion_pedagogica": "Identifica con precisión el rol de las tasas reales negativas."
        }
    
    else:
        pregunta = (
            "Tu planteamiento abre una vía de discusión interesante. Para profundizar tu postura: "
            "¿Consideras que la inflación en tu escenario proviene principalmente de una expansión del crédito bancario comercial "
            "(como en los 70s) o de inyecciones directas de déficit fiscal monetizado (como en los 40s y 2020)? "
            "Justifica tu respuesta contrastando el comportamiento del M2 con la deuda nacional."
        )
        return {
            "comentario_socratico": pregunta,
            "nivel_rigor": "Bajo",
            "puntuacion_parcial": 5.0,
            "observacion_pedagogica": "Respuesta general. Requiere contrastar las dos tipologías de inflación."
        }
