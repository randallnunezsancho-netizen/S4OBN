# Documento de Especificación de Requisitos Técnicos: Aplicación Web Interactiva de Pensamiento Crítico en Economía (U.I.A.)

## 1\. Información General y Contexto Pedagógico

* **Proyecto:** Web App Interactiva de Pensamiento Crítico en Economía con IA Socrática y Supabase.
* **Institución / Público Objetivo:** Estudiantes de primer ingreso de la carrera de Economía de la **Universidad Internacional de las Américas (U.I.A.)**.
* **Momento Didáctico:** Sesión sincrónica (*Raíces analógicas: Fase de Demostración - Exposición docente* y *Comprobación de Maestría: Fase de Aplicación - Defensa oral*).
* **Objetivo Pedagógico Central:** Lograr que los estudiantes piensen por sí mismos, abandonando la memorización pasiva y la repetición ciega de modelos económicos.
* **Restricción Cognitiva Absoluta:** La aplicación y el modelo de IA **tienen estrictamente prohibido resolver el problema o dar la respuesta correcta al alumno**. Su función es obligar activamente al estudiante a interpretar, analizar, evaluar, inferir, justificar y contrastar perspectivas económicas mediante el método socrático.

\---

## 2\. Arquitectura Tecnológica y Despliegue

* **Frontend y Framework de Interfaz:** **Streamlit** (Python), garantizando una experiencia reactiva, fluida y centrada en el contenido académico.
* **Infraestructura de Despliegue:** **Streamlit Community Cloud** (conectado directamente al repositorio de código en GitHub).
* **Base de Datos y Persistencia:** **Supabase** (PostgreSQL) para almacenar de forma estructurada:

  * Registro y credenciales de los estudiantes.
  * Historial acumulativo de respuestas y elecciones en los ejercicios.
  * Registro completo de las interacciones con el tutor socrático (IA).
  * Métricas de desempeño, notas cualitativas y cuantitativas alcanzadas.

\---

## 3\. Estructura de la Base de Datos en Supabase

La aplicación deberá interactuar con tres tablas relacionales principales en Supabase utilizando la librería `supabase-py`:

1. **`estudiantes`**:

   * `id` (UUID, Primary Key)
   * `nombre\_completo` (Text)
   * `correo\_institucional` (Text, Unique)
   * `creado\_en` (Timestamp)

1. **`sesiones\_aprendizaje`**:

   * `id` (UUID, Primary Key)
   * `estudiante\_id` (Foreign Key -> `estudiantes.id`)
   * `modulo\_activo` (Text - define la dinámica interactiva generada)
   * `estado\_progreso` (JSONB - guarda el estado actual de los ejercicios)
   * `calificacion\_final` (Numeric)
   * `actualizado\_en` (Timestamp)

1. **`historial\_interacciones\_ia`**:

   * `id` (UUID, Primary Key)
   * `sesion\_id` (Foreign Key -> `sesiones\_aprendizaje.id`)
   * `emisor` (Text - `'estudiante'` o `'ia\_socratica'`)
   * `mensaje` (Text)
   * `evaluacion\_razonamiento` (JSONB - feedback parcial del modelo)
   * `timestamp` (Timestamp)

\---

## 4\. Requisitos Funcionales de la Aplicación

### A. Pantalla de Acceso y Autenticación

* Modelo web design propuesto: coleccion-kits-interfaz-usuario-degradados 2
* El estudiante ingresa su **Nombre Completo** y **Correo Institucional**.
* La app valida o registra automáticamente al usuario en la tabla `estudiantes` de Supabase e inicia la sesión en `st.session\_state`.

### B. Barra Lateral de Contexto (Sidebar)

* Visualización destacada del **Logo de la U.I.A.**
* Resumen ejecutivo de los principios didácticos de la sesión y las fuentes de lectura asignadas.
* Indicador visual del estado de conexión con Supabase.

### C. Bloque de Demostración Sincrónica

* Componentes visuales, gráficos y métricas basados estrictamente en el contenido teórico de la lectura de Lynn Alden: *"2021 05 - Inflación impulsada por el fiscal"*.

### D. Módulo Dinámico y Creativo de Pensamiento Crítico (El Núcleo de IA)

* **Instrucción para Antigravity:** *A partir de la lectura asignada, la aplicación debe diseñar de manera creativa la dinámica interactiva más adecuada (por ejemplo: simuladores de mercado, mesas de negociación de política fiscal/monetaria, análisis de dilemas empresariales, juegos de roles institucionales, etc.). No te limites a un formato preestablecido; usa la creatividad didáctica para convertir la lectura en un desafío analítico estimulante.*
* **Componentes del Módulo:**

  1. **Planteamiento del Escenario:** Presentación clara del dilema económico, variables en conflicto y trade-offs derivados del texto.
  2. **Toma de Postura del Estudiante:** Espacio donde el alumno redacta su hipótesis, defiende un curso de acción o toma decisiones tácticas justificadas.
  3. **Motor de IA Socrática en Tiempo Real:**

     * Cada aportación del estudiante es analizada por el LLM configurado bajo un **System Prompt Socrático**.
     * Si el argumento es superficial, incompleto o erróneo, la IA **jamás corrige al alumno**, sino que le formula una pregunta focalizada para poner a prueba sus premisas (ejemplo: *"¿Qué efecto secundario tendría sobre la inversión privada si asumes esa elasticidad en el corto plazo?"*).
     * El intercambio se persiste en tiempo real en la tabla `historial\_interacciones\_ia` de Supabase.

### E. Módulo de Retroalimentación Formativa y Cierre

* Mensajes condicionales en la app que valoran la solidez argumentativa del estudiante a lo largo de la sesión.
* Al concluir los ejercicios, la app procesa el desempeño global, calcula una nota cualitativa/cuantitativa, la almacena en Supabase y genera un **reporte consolidado descargable** (en formato `.md` o `.txt`) que incluye el resumen de respuestas, la retroalimentación de la IA y la calificación final.

\---

## 5\. Directrices Técnicas para el Desarrollo en Streamlit (`app.py`)

* Utilizar `st.session\_state` para mantener la fluidez de la interfaz interactiva durante la clase sincrónica.
* Gestionar las llaves de Supabase de manera segura mediante el gestor de secretos de Streamlit (`st.secrets`), evitando exponer credenciales en el código fuente.
* Estructurar el código de manera modular para separar la interfaz gráfica (UI), la lógica de negocio y las llamadas a la base de datos y al modelo de IA.
