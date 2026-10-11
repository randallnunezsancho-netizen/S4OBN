-- ==============================================================================
-- Script de Creación de Tablas en Supabase para:
-- Web App Interactiva de Pensamiento Crítico en Economía (U.I.A.)
-- ==============================================================================

-- 1. Tabla: estudiantes
CREATE TABLE IF NOT EXISTS public.estudiantes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_completo TEXT NOT NULL,
    correo_institucional TEXT UNIQUE NOT NULL,
    creado_en TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Tabla: sesiones_aprendizaje
CREATE TABLE IF NOT EXISTS public.sesiones_aprendizaje (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estudiante_id UUID NOT NULL REFERENCES public.estudiantes(id) ON DELETE CASCADE,
    modulo_activo TEXT NOT NULL,
    estado_progreso JSONB DEFAULT '{}'::jsonb NOT NULL,
    calificacion_final NUMERIC(4, 2) DEFAULT 0.00,
    actualizado_en TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Tabla: historial_interacciones_ia
CREATE TABLE IF NOT EXISTS public.historial_interacciones_ia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sesion_id UUID NOT NULL REFERENCES public.sesiones_aprendizaje(id) ON DELETE CASCADE,
    emisor TEXT NOT NULL CHECK (emisor IN ('estudiante', 'ia_socratica')),
    mensaje TEXT NOT NULL,
    evaluacion_razonamiento JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Índices para búsquedas y consultas rápidas
CREATE INDEX IF NOT EXISTS idx_sesiones_estudiante ON public.sesiones_aprendizaje(estudiante_id);
CREATE INDEX IF NOT EXISTS idx_historial_sesion ON public.historial_interacciones_ia(sesion_id);

-- Configuración de Seguridad por Nivel de Fila (RLS)
ALTER TABLE public.estudiantes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sesiones_aprendizaje ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.historial_interacciones_ia ENABLE ROW LEVEL SECURITY;

-- Políticas de acceso para permitir lectura y escritura desde la aplicación Streamlit
CREATE POLICY "Permitir acceso publico estudiantes" ON public.estudiantes
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Permitir acceso publico sesiones" ON public.sesiones_aprendizaje
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Permitir acceso publico historial" ON public.historial_interacciones_ia
    FOR ALL USING (true) WITH CHECK (true);
