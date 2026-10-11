"""
Aplicación Web Interactiva de Pensamiento Crítico en Economía (U.I.A.)
Basada en la metodología socrática de aprendizaje y en el texto de Lynn Alden.
Integración con Supabase para persistencia de sesiones, estudiantes y analítica.
"""

import streamlit as st
import datetime
import json
import os
from PIL import Image

# Importación de módulos internos modulares
from db_service import (
    obtener_o_crear_estudiante,
    crear_sesion,
    registrar_interaccion,
    actualizar_calificacion_sesion,
    get_supabase_client
)
from socratic_engine import consultar_tutor_socratico
from charts import generar_grafico_deuda_vs_inflacion, generar_simulador_curva

# Configuración de página de Streamlit
st.set_page_config(
    page_title="U.I.A. - Cátedra de Economía Socrática",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS premium inspirados en paleta institucional UIA y degradados modernos
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    /* Tarjetas con contraste accesible y soporte para temas claro/oscuro */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 22px;
        color: #f8fafc !important;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.25);
        margin-bottom: 16px;
    }

    .metric-card h4 {
        color: #60a5fa !important;
        margin-bottom: 12px;
        font-size: 1.15rem;
    }

    .metric-card ul {
        margin: 0;
        padding-left: 1.2rem;
        color: #e2e8f0 !important;
    }

    .metric-card li {
        color: #e2e8f0 !important;
        line-height: 1.6;
        margin-bottom: 10px;
    }

    .metric-card b, .metric-card strong {
        color: #ffffff !important;
    }

    .badge-status-on {
        display: inline-block;
        padding: 4px 10px;
        background-color: #d1fae5;
        color: #065f46;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .badge-status-off {
        display: inline-block;
        padding: 4px 10px;
        background-color: #fee2e2;
        color: #991b1b;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Caja del tutor socrático */
    .socratic-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        color: #f8fafc !important;
        border-radius: 12px;
        padding: 18px 22px;
        margin: 15px 0;
        border-left: 5px solid #818cf8;
        box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.35);
    }

    .socratic-box h4 {
        color: #a5b4fc !important;
        margin-bottom: 8px;
    }

    .socratic-box p {
        color: #f8fafc !important;
    }

    /* Caja de respuestas del estudiante */
    .student-message-box {
        background: #1e293b;
        color: #f8fafc !important;
        padding: 14px 18px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #38bdf8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .student-message-box b {
        color: #38bdf8 !important;
    }

    .stButton>button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Inicialización de estado de sesión (st.session_state)
# -----------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "estudiante" not in st.session_state:
    st.session_state.estudiante = None
if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = None
if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []
if "evaluaciones" not in st.session_state:
    st.session_state.evaluaciones = []
if "etapa_activa" not in st.session_state:
    st.session_state.etapa_activa = 1
if "calificacion_acumulada" not in st.session_state:
    st.session_state.calificacion_acumulada = 0.0

# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar)
# -----------------------------------------------------------------------------
with st.sidebar:
    # Logo U.I.A.
    logo_path = os.path.join(os.path.dirname(__file__), "Logo-oscuro- UIA.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width="stretch")
    else:
        st.title("🏛️ U.I.A.")
    
    st.markdown("### **Cátedra de Economía**")
    st.caption("Universidad Internacional de las Américas")
    
    st.divider()
    
    # Estado de Conexión a Supabase
    st.markdown("#### **Infraestructura Cloud**")
    supabase_test = get_supabase_client()
    if supabase_test is not None:
        st.markdown('<span class="badge-status-on">● Supabase Conectado</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-status-off">● Modo Sin Conexión</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Resumen Pedagógico
    st.markdown("#### **Marco Pedagógico**")
    st.info(
        "**Método Socrático Activo:** La plataforma tiene prohibido resolver el dilema. "
        "Su objetivo es guiarte mediante interrogantes dialécticas para forzar la argumentación rigurosa."
    )
    
    st.markdown("#### **Lectura de Referencia**")
    st.caption("📖 *Lynn Alden (2021)* — *Inflación impulsada por el fiscal: El ciclo de deuda de largo plazo y el paralelismo de los años 40 vs 70.*")

    if st.session_state.autenticado:
        st.divider()
        st.write(f"**Estudiante:** {st.session_state.estudiante.get('nombre_completo', '')}")
        st.write(f"**Correo:** {st.session_state.estudiante.get('correo_institucional', '')}")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.estudiante = None
            st.session_state.sesion_id = None
            st.session_state.mensajes_chat = []
            st.rerun()

# -----------------------------------------------------------------------------
# Pantalla A: Autenticación / Acceso del Estudiante
# -----------------------------------------------------------------------------
if not st.session_state.autenticado:
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; color: #1e3a8a;">Portal de Pensamiento Crítico en Economía</h1>
            <p style="font-size: 1.15rem; color: #4b5563;">
                Fase de Aplicación Didáctica y Razonamiento Macroeconómico Socrático
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_center1, col_center2, col_center3 = st.columns([1, 2, 1])
    with col_center2:
        with st.form("form_login"):
            st.markdown("### Identificación Institucional")
            st.markdown("Ingresa tus credenciales oficiales para registrar tu participación en Supabase.")
            
            nombre_input = st.text_input("Nombre Completo:", placeholder="Ej. Mariana Jiménez Solano")
            correo_input = st.text_input("Correo Institucional (@est.uia.ac.cr):", placeholder="ejemplo@est.uia.ac.cr")
            
            submitted = st.form_submit_button("Ingresar a la Sesión")
            
            if submitted:
                if not nombre_input.strip() or not correo_input.strip():
                    st.error("Por favor completa tu nombre y correo institucional.")
                elif "@" not in correo_input:
                    st.error("Por favor ingresa un formato de correo electrónico válido.")
                else:
                    with st.spinner("Autenticando y sincronizando con Supabase..."):
                        estudiante = obtener_o_crear_estudiante(nombre_input, correo_input)
                        if estudiante:
                            st.session_state.estudiante = estudiante
                            # Crear sesión en Supabase
                            sesion_id = crear_sesion(
                                estudiante_id=estudiante["id"],
                                modulo="Lynn Alden: Inflación Impulsada por el Fiscal"
                            )
                            st.session_state.sesion_id = sesion_id
                            st.session_state.autenticado = True
                            st.success("¡Autenticación exitosa! Accediendo a la sesión sincrónica...")
                            st.rerun()
                        else:
                            st.error("No se pudo registrar la sesión en la base de datos.")

# -----------------------------------------------------------------------------
# Pantalla Principal (Estudiante Autenticado)
# -----------------------------------------------------------------------------
else:
    # Encabezado del Entorno de Trabajo
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <div>
                <h2>Sesión Socrática: Inflación Impulsada por el Fiscal</h2>
                <span style="color: #6b7280;">Módulo Interactivo basado en Lynn Alden | Participante: <b>{st.session_state.estudiante.get('nombre_completo')}</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Pestañas de la Aplicación según los requisitos pedagógicos
    tab_demo, tab_debate, tab_cierre = st.tabs([
        "📊 1. Bloque de Demostración Macroeconómica",
        "⚖️ 2. Simulador y Dilema Socrático en Vivo",
        "🎓 3. Cierre y Reporte Consolidado"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Bloque de Demostración Sincrónica (Gráficos y Métricas)
    # -------------------------------------------------------------------------
    with tab_demo:
        st.markdown("### Evidencia Empírica de Lynn Alden: Los Ciclos de Deuda de Largo Plazo")
        st.write(
            "El debate macroeconómico contemporáneo suele asumir que toda inflación es causada por el crédito bancario "
            "(como en la década de 1970) y que basta con subir las tasas de interés. Sin embargo, Lynn Alden demuestra que "
            "los episodios con **Deuda Pública/PIB superior al 100%** (1940s y 2020s) obedecen a **Dominancia Fiscal**."
        )

        # Gráfico comparativo de décadas
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            fig_hist = generar_grafico_deuda_vs_inflacion()
            st.plotly_chart(fig_hist, width="stretch")

        with col_g2:
            st.markdown("""
                <div class="metric-card">
                    <h4>Puntos Clave del Análisis:</h4>
                    <ul>
                        <li><b>Años 70:</b> Deuda/PIB baja (~30%). La inflación provino del multiplicador de préstamos bancarios. Subir tasas al 20% con Paul Volcker detuvo la emisión de crédito sin quebrar fiscalmente al Estado.</li>
                        <li><b>Años 40 y 2020s:</b> Deuda/PIB masiva (>100%). La inflación provino de inyecciones fiscales directas (M2). Subir tasas agresivamente dispara el déficit fiscal debido a la carga de intereses.</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🧪 Simulador de Dominancia Fiscal y Presión Financiera")
        st.caption("Experimenta cómo interactúan el nivel de deuda y la tasa de política monetaria:")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            deuda_sel = st.slider("Deuda Pública sobre el PIB (%)", min_value=30, max_value=160, value=125, step=5)
        with c2:
            deficit_sel = st.slider("Déficit Fiscal Primario (% del PIB)", min_value=1.0, max_value=15.0, value=7.5, step=0.5)
        with c3:
            tasa_sel = st.slider("Tasa de Interés del Banco Central (%)", min_value=0.5, max_value=18.0, value=5.25, step=0.25)
            
        fig_sim, gasto_intereses, infl_est = generar_simulador_curva(deuda_sel, deficit_sel, tasa_sel)
        st.plotly_chart(fig_sim, width="stretch")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Gasto Anual en Intereses Fiscales", f"${gasto_intereses:.2f} Trillones", delta="Carga Fiscal")
        m_col2.metric("Presión Inflacionaria Proyectada", f"{infl_est:.2f}%", delta="Riesgo IPC")
        m_col3.metric("Régimen Macroeconómico", "Dominancia Fiscal" if deuda_sel > 80 else "Dominancia Monetaria")

    # -------------------------------------------------------------------------
    # TAB 2: Módulo de Pensamiento Crítico y Tutor Socrático
    # -------------------------------------------------------------------------
    with tab_debate:
        st.markdown("### El Dilema del Comité de Estabilidad Financiera")
        
        st.markdown("""
            > **Escenario de Decisión:**  
            > Eres el asesor principal del Tesoro y la Reserva Federal. La inflación anual alcanza el **9.1%** impulsada por estímulos fiscales y cuellos de botella en la oferta global. La deuda pública se ubica en **$31 billones (125% del PIB)**.  
            >  
            > Tienes dos facciones en tu equipo:
            > - **Opción A (La Receta Volcker / Monetarista):** Subir drásticamente la tasa de interés al 9% para frenar la demanda.
            > - **Opción B (La Receta de los Años 40 / Represión Financiera):** Fijar un tope a los rendimientos de la deuda (Yield Curve Control) en 2.5% y tolerar inflación para licuar el valor real de la deuda.
            > - **Opción C (Tu Propia Tesis Híbrida / Alternativa Justificada):** Diseñar una estrategia diferenciada argumentando las variables del M2 y la oferta física.
        """)

        st.markdown("#### 1. Toma de Postura Inicial")
        postura_opcion = st.radio(
            "Selecciona la base de tu postura política y analítica:",
            [
                "Opción A: Subir tasas de interés al estilo de los años 70 para contener el IPC.",
                "Opción B: Aplicar represión financiera y control de la curva de rendimientos como en los años 40.",
                "Opción C: Propuesta alternativa estructurada basada en política fiscal y oferta."
            ]
        )

        st.markdown("#### 2. Justificación y Argumentación del Estudiante")
        argumento_texto = st.text_area(
            "Expón tus premisas fundamentales: ¿Por qué adoptas este curso de acción? ¿Qué trade-offs asumes y cómo responde tu modelo a la alta deuda pública?",
            placeholder="Escribe tu razonamiento detallado aquí...",
            height=130
        )

        btn_enviar_argumento = st.button("Enviar al Tutor Socrático")

        if btn_enviar_argumento:
            if not argumento_texto.strip() or len(argumento_texto.strip()) < 25:
                st.warning("⚠️ Tu argumentación es demasiado breve para un análisis universitario. Por favor profundiza tus premisas.")
            else:
                with st.spinner("El Tutor Socrático está evaluando tus premisas..."):
                    # Registrar interacción del estudiante en la BD
                    registrar_interaccion(
                        sesion_id=st.session_state.sesion_id,
                        emisor="estudiante",
                        mensaje=argumento_texto,
                        evaluacion={"postura": postura_opcion}
                    )
                    st.session_state.mensajes_chat.append({
                        "emisor": "estudiante",
                        "mensaje": argumento_texto,
                        "fecha": datetime.datetime.now().strftime("%H:%M")
                    })

                    # Consultar al motor socrático
                    respuesta_socratica = consultar_tutor_socratico(
                        historial_mensajes=st.session_state.mensajes_chat,
                        escenario_actual="Dilema de Inflación Fiscal con Deuda Pública > 120% del PIB (Lynn Alden)",
                        eleccion_estudiante=f"{postura_opcion}. Argumento: {argumento_texto}"
                    )

                    # Registrar la repregunta en Supabase
                    registrar_interaccion(
                        sesion_id=st.session_state.sesion_id,
                        emisor="ia_socratica",
                        mensaje=respuesta_socratica["comentario_socratico"],
                        evaluacion=respuesta_socratica
                    )

                    st.session_state.mensajes_chat.append({
                        "emisor": "ia_socratica",
                        "mensaje": respuesta_socratica["comentario_socratico"],
                        "evaluacion": respuesta_socratica,
                        "fecha": datetime.datetime.now().strftime("%H:%M")
                    })
                    
                    # Acumular calificación
                    puntos = respuesta_socratica.get("puntuacion_parcial", 7.0)
                    st.session_state.calificacion_acumulada = max(st.session_state.calificacion_acumulada, puntos)
                    st.session_state.evaluaciones.append(respuesta_socratica)
                    
                    actualizar_calificacion_sesion(
                        sesion_id=st.session_state.sesion_id,
                        calificacion=float(st.session_state.calificacion_acumulada),
                        estado_progreso={"etapa": 2, "total_interacciones": len(st.session_state.mensajes_chat)}
                    )
                    st.rerun()

        # Historial de Diálogo Socrático
        if st.session_state.mensajes_chat:
            st.markdown("---")
            st.markdown("#### 🗣️ Diálogo Socrático en Vivo")
            
            for item in st.session_state.mensajes_chat:
                if item["emisor"] == "estudiante":
                    st.markdown(f"""
                        <div class="student-message-box">
                            <b>👤 Estudiante ({item.get('fecha', '')}):</b><br>
                            <span style="color: #f1f5f9;">{item['mensaje']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    eval_data = item.get("evaluacion", {})
                    nivel = eval_data.get("nivel_rigor", "Medio")
                    st.markdown(f"""
                        <div class="socratic-box">
                            <h4>🏛️ Interrogante Socrático (Nivel de Rigor: {nivel}):</h4>
                            <p style="font-size: 1.05rem; line-height: 1.6;">{item['mensaje']}</p>
                            <small style="color: #cbd5e1;"><i>{eval_data.get('observacion_pedagogica', '')}</i></small>
                        </div>
                    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 3: Evaluación Formativa y Reporte Consolidado Descargable
    # -------------------------------------------------------------------------
    with tab_cierre:
        st.markdown("### Evaluación Formativa y Rúbrica de Maestría")
        
        calif = st.session_state.calificacion_acumulada
        
        col_res1, col_res2 = st.columns([1, 2])
        with col_res1:
            st.metric(label="Calificación Formativa Obtenida", value=f"{calif:.1f} / 10.0")
            if calif >= 8.5:
                st.success("🏆 **Nivel Sobresaliente:** Evidencia dominio de los trade-offs macroeconómicos y comprensión de la dominancia fiscal.")
            elif calif >= 6.5:
                st.info("📈 **Nivel Competente:** Argumentación clara pero con oportunidades para contrastar efectos de segundo orden sobre la deuda.")
            else:
                st.warning("🔄 **Nivel en Desarrollo:** Se requiere mayor profundidad analítica para evitar recetas mecánicas sin considerar el M2.")

        with col_res2:
            st.markdown("#### Registro Persistente en Supabase")
            st.write(f"- **ID de Sesión:** `{st.session_state.sesion_id}`")
            st.write(f"- **Total de Intercambios Socráticos:** {len(st.session_state.mensajes_chat)}")
            st.write(f"- **Estudiante:** {st.session_state.estudiante.get('nombre_completo')} ({st.session_state.estudiante.get('correo_institucional')})")

        st.divider()
        
        # Generación del Reporte Consolidado Descargable (.md)
        st.markdown("#### Descarga del Informe Oficial de la Sesión")
        
        reporte_md = f"""# REPORTE DE EVALUACIÓN DE PENSAMIENTO CRÍTICO EN ECONOMÍA
Universidad Internacional de las Américas (U.I.A.)
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Datos del Estudiante
- Nombre Completo: {st.session_state.estudiante.get('nombre_completo')}
- Correo Institucional: {st.session_state.estudiante.get('correo_institucional')}
- ID de Sesión Supabase: {st.session_state.sesion_id}
- Módulo: Lynn Alden - Inflación impulsada por el fiscal (1940s vs 1970s)

## 2. Calificación Final Formativa
- Puntuación Alcanzada: {calif:.2f} / 10.00
- Nivel de Pensamiento Crítico: {'Sobresaliente' if calif >= 8.5 else 'Competente' if calif >= 6.5 else 'En Desarrollo'}

## 3. Transcripción de Interacciones Socráticas
"""
        for i, m in enumerate(st.session_state.mensajes_chat, 1):
            reporte_md += f"\n### Intercambio {i} ({m['emisor'].upper()})\n"
            reporte_md += f"{m['mensaje']}\n"
            if "evaluacion" in m:
                reporte_md += f"- Rigor Pedagógico: {m['evaluacion'].get('nivel_rigor')}\n"
                reporte_md += f"- Observación del Tutor: {m['evaluacion'].get('observacion_pedagogica')}\n"

        reporte_md += """
---
Generado automáticamente por la Plataforma Interactiva de Pensamiento Crítico U.I.A.
"""
        
        st.download_button(
            label="📥 Descargar Reporte Consolidado (.md)",
            data=reporte_md,
            file_name=f"reporte_socratico_{st.session_state.estudiante.get('correo_institucional').split('@')[0]}.md",
            mime="text/markdown"
        )
