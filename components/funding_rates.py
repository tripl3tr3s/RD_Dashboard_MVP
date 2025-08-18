import streamlit as st
from utils.formatters import format_percentage
import random
import plotly.graph_objects as go

def generate_mock_funding_rates():
    """Generate 7-day mock funding rates and average"""
    history = {
        'BTC': [round(random.uniform(-0.03, 0.05), 4) for _ in range(7)],
        'ETH': [round(random.uniform(-0.03, 0.05), 4) for _ in range(7)]
    }
    averages = {asset: round(sum(rates)/len(rates), 4) for asset, rates in history.items()}
    latest = {asset: rates[-1] for asset, rates in history.items()}
    return history, latest, averages

def get_funding_interpretation(rate: float) -> tuple:
    """
    Interpret funding rate and return description with color
    """
    if rate > 0:
        return "Bullish (Longs pay shorts)", "#00d4aa"  # Green
    else:
        return "Bearish (Shorts pay longs)", "#ff5757"  # Red

def make_sparkline(data, color):
    """Return a tiny sparkline with single sentiment color"""
    fig = go.Figure(
        data=[go.Scatter(
            y=data,
            mode="lines",
            line=dict(color=color, width=2),
            hoverinfo="skip"
        )]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=50,
        width=220,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def render_funding_rates(skip_render=False):
    """Render funding rates component with colored cards"""
    history, latest, averages = generate_mock_funding_rates()
    data = {"history": history, "latest": latest, "averages": averages}
    
    if not skip_render:
        for asset in ["BTC", "ETH"]:
            latest_rate = latest[asset]
            avg_rate = averages[asset]
            hist = history[asset]
            
            # Interpret latest + avg independently
            latest_interp, latest_color = get_funding_interpretation(latest_rate)
            avg_interp, avg_color = get_funding_interpretation(avg_rate)

            # Card layout
            st.markdown(f"""
                <div style="margin: 15px 0; padding: 10px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border-left: 5px solid {latest_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: white; font-weight: 600; font-size: 16px;">{asset}</div>
                            <div style="color: {latest_color}; font-size: 12px;">{latest_interp}</div>
                        </div>
                        <div style="display: flex; gap: 30px;">
                            <div style="text-align: right;">
                                <div style="color: #aaa; font-size: 12px;">Latest</div>
                                <div style="color: {latest_color}; font-weight: 700; font-size: 18px;">{format_percentage(latest_rate)}</div>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: #aaa; font-size: 12px;">7-Day Avg</div>
                                <div style="color: {avg_color}; font-weight: 700; font-size: 18px;">{format_percentage(avg_rate)}</div>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Sparkline directly below card
            st.plotly_chart(make_sparkline(hist, latest_color), 
                            use_container_width=True, config={"displayModeBar": False})

        # Educational content
        st.markdown("""
        <div class="funding-explanation">
            <strong>📚 Funding Rates Explained:</strong><br><br>
            <strong>Positive rates:</strong> Longs pay shorts → Bullish sentiment<br>
            <strong>Negative rates:</strong> Shorts pay longs → Bearish sentiment
        </div>
        """, unsafe_allow_html=True)

    return data

