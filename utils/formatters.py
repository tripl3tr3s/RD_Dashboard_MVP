import streamlit as st
from typing import Union

def format_currency(value: Union[int, float, None], decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    try:
        if abs(value) >= 1_000_000_000:
            return f"${value/1_000_000_000:.{decimals}f}B"
        elif abs(value) >= 1_000_000:
            return f"${value/1_000_000:.{decimals}f}M"
        elif abs(value) >= 1_000:
            return f"${value/1_000:.{decimals}f}K"
        else:
            return f"${value:,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"

def format_percentage(value: Union[int, float, None], decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{value:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"

def format_large_number(value: Union[int, float, None], decimals: int = 1) -> str:
    if value is None:
        return "N/A"
    try:
        if abs(value) >= 1_000_000_000_000:
            return f"{value/1_000_000_000_000:.{decimals}f}T"
        elif abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:.{decimals}f}B"
        elif abs(value) >= 1_000_000:
            return f"{value/1_000_000:.{decimals}f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.{decimals}f}K"
        else:
            return f"{value:,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"

def get_color_for_change(value: Union[int, float, None]) -> str:
    if value is None:
        return "neutral"
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        .main > div {
            padding: 1rem 2rem;
        }
        
        .stMetric {
            background-color: #2a2a3a;
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid #3d3d4d;
        }
        
        .metric-card, .widget {
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);
            border: 1px solid #3d3d4d;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        /* Rounded edges for Plotly plots */
        .js-plotly-plot {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #3d3d4d; /* Light grey outline */
            background-color: #2a2a3a; /* Match background */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow */
        }
        
        .metric-title, .widget-title {
            color: #a0a0a0;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .metric-value, .widget-value {
            color: #ffffff;
            font-size: 28px;
            font-weight: 700;
            line-height: 1.2;
        }
        
        .metric-change, .widget-subtext {
            font-size: 14px;
            font-weight: 500;
            margin-top: 4px;
        }
        
        .positive { color: #00d4aa; }
        .negative { color: #ff5757; }
        .neutral { color: #a0a0a0; }
        
        .header-title {
            color: #FFA500; /* Orange */
            font-size: 50px;
            font-weight: 800;
            margin-bottom: 8px;
            text-align: center;
        }
        
        .header-subtitle {
            color: #FFA500; /* Orange */
            font-size: 32px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .rsi-gauge {
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3a 100%);
            border: 1px solid #3d3d4d;
        }
        
        .funding-explanation {
            background: #2a2a3a;
            border-left: 4px solid #00d4aa;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin: 15px 0;
            font-size: 14px;
            color: #cccccc;
        }
        
        .dxy-explanation {
            background: #2a2a3a;
            border-left: 4px solid #ffa500;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin: 15px 0;
            font-size: 14px;
            color: #cccccc;
        }
        
        /* Hide Streamlit footer and menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stApp {
            background-color: #0E1117;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e1e2e;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #3d3d4d;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #4d4d5d;
        }
        
        /* Plotly chart styling */
        .js-plotly-plot .plotly .modebar {
            background-color: rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Spinner styling */
        .stSpinner > div > div {
            border-top-color: #00d4aa !important;
        }
    </style>
    """, unsafe_allow_html=True)