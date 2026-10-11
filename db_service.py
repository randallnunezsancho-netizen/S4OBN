"""
Módulo de conexión y operaciones con Supabase para la plataforma educativa U.I.A.
Garantiza persistencia segura y manejo de excepciones.
"""

import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Any, List

@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """Inicializa y almacena en caché el cliente de Supabase usando st.secrets."""
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if not url or not key:
            st.warning("⚠️ No se encontraron las credenciales SUPABASE_URL o SUPABASE_KEY en .streamlit/secrets.toml.")
            return None
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        return None

def obtener_o_crear_estudiante(nombre: str, correo: str) -> Optional[Dict[str, Any]]:
    """Busca o registra un estudiante por correo institucional."""
    client = get_supabase_client()
    if not client:
        return {"id": "demo-local", "nombre_completo": nombre, "correo_institucional": correo}
    
    correo_limpio = correo.strip().lower()
    nombre_limpio = nombre.strip()
    
    try:
        # Verificar si ya existe
        res = client.table("estudiantes").select("*").eq("correo_institucional", correo_limpio).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        
        # Insertar nuevo registro
        nuevo = client.table("estudiantes").insert({
            "nombre_completo": nombre_limpio,
            "correo_institucional": correo_limpio
        }).execute()
        
        if nuevo.data and len(nuevo.data) > 0:
            return nuevo.data[0]
        return None
    except Exception as e:
        st.error(f"Error en base de datos al autenticar estudiante: {e}")
        return None

def crear_sesion(estudiante_id: str, modulo: str) -> Optional[str]:
    """Crea un registro de sesión de aprendizaje y retorna el ID generado."""
    client = get_supabase_client()
    if not client:
        return "local-session-id"
    
    try:
        res = client.table("sesiones_aprendizaje").insert({
            "estudiante_id": estudiante_id,
            "modulo_activo": modulo,
            "estado_progreso": {"etapa": 1, "respuestas": []},
            "calificacion_final": 0.0
        }).execute()
        
        if res.data and len(res.data) > 0:
            return res.data[0]["id"]
        return None
    except Exception as e:
        st.error(f"Error al iniciar sesión en base de datos: {e}")
        return None

def registrar_interaccion(sesion_id: str, emisor: str, mensaje: str, evaluacion: Optional[Dict[str, Any]] = None) -> bool:
    """Registra un mensaje de chat y su evaluación parcial en la base de datos."""
    client = get_supabase_client()
    if not client or sesion_id == "local-session-id":
        return True
    
    try:
        client.table("historial_interacciones_ia").insert({
            "sesion_id": sesion_id,
            "emisor": emisor,
            "mensaje": mensaje,
            "evaluacion_razonamiento": evaluacion or {}
        }).execute()
        return True
    except Exception as e:
        print(f"Error al guardar interacción en Supabase: {e}")
        return False

def actualizar_calificacion_sesion(sesion_id: str, calificacion: float, estado_progreso: Dict[str, Any]) -> bool:
    """Actualiza la nota final y el estado acumulado de la sesión."""
    client = get_supabase_client()
    if not client or sesion_id == "local-session-id":
        return True
    
    try:
        client.table("sesiones_aprendizaje").update({
            "calificacion_final": calificacion,
            "estado_progreso": estado_progreso
        }).eq("id", sesion_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la sesión: {e}")
        return False
