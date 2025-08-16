# rsi_widget.py
import streamlit as st
import plotly.graph_objects as go

def render_rsi_widget(rsi_value: float):
    """Render a gauge widget for 14-day RSI"""
    # Define gauge zones
    zones = [
        {"range": [0, 30], "color": "#0dad3a", "label": "Oversold"},
        {"range": [30, 70], "color": "#FBFF27", "label": "Normal"},
        {"range": [70, 100], "color": "#e70606", "label": "Overbought"}
    ]
    
    # Determine current zone
    zone_label = "Normal"
    for zone in zones:
        if rsi_value <= zone["range"][1]:
            zone_label = zone["label"]
            break
    
    # Create gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rsi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "14-Day RSI"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#000000"},
            'steps': [
                {'range': [z["range"][0], z["range"][1]], 'color': z["color"]}
                for z in zones
            ],
            'threshold': {
                'line': {'color': "white", 'width': 2},
                'thickness': 0.75,
                'value': rsi_value
            }
        },
        number={'suffix': "", 'font': {'size': 20, 'color': 'orange'}}
    ))
    
    fig.update_layout(
        height=200,
        width=200,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<div class='rsi-gauge'>{zone_label}</div>", unsafe_allow_html=True)