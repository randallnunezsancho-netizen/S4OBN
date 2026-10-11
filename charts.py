"""
Generador de visualizaciones macroeconómicas interactivas
basadas estrictamente en el texto de Lynn Alden (2021).
Compara la dinámica 1940s vs 1970s vs 2020s.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

def generar_grafico_deuda_vs_inflacion():
    """Compara los niveles de Deuda Pública/PIB frente a los ciclos inflacionarios."""
    decadas = ['1940s (Guerra/Fiscal)', '1970s (Préstamos/Bancos)', '2020s (Fiscal/Pandemia)']
    deuda_pib = [118, 32, 128] # Deuda federal como % del PIB
    tasa_interes_max = [2.5, 20.0, 5.5] # Rendimientos o tasa Fed
    pico_inflacion = [19.0, 14.8, 9.1]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=decadas,
        y=deuda_pib,
        name='Deuda Pública / PIB (%)',
        marker_color='#3b82f6',
        text=[f"{v}%" for v in deuda_pib],
        textposition='auto',
    ))

    fig.add_trace(go.Bar(
        x=decadas,
        y=pico_inflacion,
        name='Pico de Inflación CPI (%)',
        marker_color='#ef4444',
        text=[f"{v}%" for v in pico_inflacion],
        textposition='auto',
    ))

    fig.add_trace(go.Bar(
        x=decadas,
        y=tasa_interes_max,
        name='Tasa de Interés / Rendimiento Bonos (%)',
        marker_color='#10b981',
        text=[f"{v}%" for v in tasa_interes_max],
        textposition='auto',
    ))

    fig.update_layout(
        title="<b>Evolución Estructural: El Dilema de la Deuda y los Tipos de Interés</b>",
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.03)',
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="Inter, sans-serif", size=13),
        height=380
    )
    return fig

def generar_simulador_curva(deuda_pib: float, deficit_fiscal: float, tasa_interes: float):
    """
    Modela el impacto del costo financiero de la deuda en el presupuesto fiscal,
    demostrando la trampa de la dominancia fiscal explicada por Lynn Alden.
    Utiliza doble eje Y para máxima claridad visual y sensibilidad en los sliders.
    """
    anios = [1, 2, 3, 4, 5]
    
    # Base de deuda estimada en trillones de dólares ($30T para 120% del PIB aprox.)
    base_deuda = 30.0 * (deuda_pib / 120.0)
    gasto_intereses_anual = base_deuda * (tasa_interes / 100.0)
    
    # Dinámica a 5 años: si la tasa y el déficit son altos, el déficit se capitaliza aumentando la deuda
    proyeccion_intereses = []
    proyeccion_inflacion = []
    deuda_acumulada = base_deuda
    
    for anio in anios:
        # Crecimiento de la deuda por acumulación del déficit primario + pago de intereses
        nuevo_endeudamiento = (deficit_fiscal / 100.0 * 25.0) + (gasto_intereses_anual * 0.8)
        deuda_acumulada += nuevo_endeudamiento * 0.4
        
        interes_del_anio = deuda_acumulada * (tasa_interes / 100.0)
        proyeccion_intereses.append(interes_del_anio)
        
        # En dominancia fiscal (deuda > 80%), subir tasas incrementa el déficit y la emisión fiscal:
        if deuda_pib > 80:
            efecto_fiscal_perverso = (tasa_interes * (deuda_pib / 100.0)) * 0.35
            infl_anio = max(1.5, (deficit_fiscal * 0.7) + efecto_fiscal_perverso + (anio * 0.25))
        else:
            # En régimen tradicional monetarista (baja deuda), subir tasas sí enfría la inflación:
            infl_anio = max(1.0, (deficit_fiscal * 0.8) - (tasa_interes * 0.45) - (anio * 0.2))
            
        proyeccion_inflacion.append(infl_anio)

    from plotly.subplots import make_subplots
    
    # Crear figura con doble eje Y (eje izquierdo: $ Trillones, eje derecho: % Inflación)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(
            x=[f"Año {a}" for a in anios],
            y=proyeccion_intereses,
            mode='lines+markers',
            name='Pago Intereses Fiscales ($ Trillones)',
            line=dict(color='#a855f7', width=3.5),
            marker=dict(size=9, color='#c084fc')
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=[f"Año {a}" for a in anios],
            y=proyeccion_inflacion,
            mode='lines+markers',
            name='Presión Inflacionaria IPC (%)',
            line=dict(color='#f59e0b', width=3.5, dash='dash'),
            marker=dict(size=9, color='#fbbf24')
        ),
        secondary_y=True
    )
    
    # Ajustar escalas de los ejes Y para que el movimiento sea evidente e intuitivo
    max_interes = max(proyeccion_intereses)
    max_infl = max(proyeccion_inflacion)
    
    fig.update_layout(
        title=f"<b>Simulación Dinámica: Tasa {tasa_interes}% | Deuda {deuda_pib}% PIB | Déficit {deficit_fiscal}%</b>",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.03)',
        margin=dict(l=40, r=40, t=50, b=20),
        font=dict(family="Inter, sans-serif", size=13),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    fig.update_yaxes(
        title_text="<b>Gasto en Intereses ($ Trillones)</b>",
        title_font=dict(color="#a855f7"),
        tickfont=dict(color="#c084fc"),
        range=[0, max(4.0, max_interes * 1.25)],
        gridcolor='rgba(255,255,255,0.08)',
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text="<b>Tasa de Inflación Estimada (%)</b>",
        title_font=dict(color="#f59e0b"),
        tickfont=dict(color="#fbbf24"),
        range=[0, max(15.0, max_infl * 1.25)],
        showgrid=False,
        secondary_y=True
    )
    
    return fig, gasto_intereses_anual, proyeccion_inflacion[0]

