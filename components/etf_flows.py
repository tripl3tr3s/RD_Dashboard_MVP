import streamlit as st
from data.traditional_data import TraditionalDataFetcher
from utils.formatters import format_currency, format_percentage

def get_flow_interpretation(flow_7d: float, asset: str) -> tuple:
    """
    Interpret ETF flows and return description with color
    
    Args:
        flow_7d: 7-day net flow in millions
        asset: Asset name (BTC or ETH)
        
    Returns:
        Tuple of (interpretation, color)
    """
    thresholds = [
        (500, "Very Strong Inflows", "#00d4aa"),
        (200, "Strong Inflows", "#4ecdc4"),
        (50, "Moderate Inflows", "#45b7d1"),
        (0, "Light Inflows", "#a0c4d4"),
        (-50, "Light Outflows", "#ffb84d"),
        (-200, "Moderate Outflows", "#ff8c42"),
        (-500, "Strong Outflows", "#ff6b47"),
    ]
    for threshold, desc, color in thresholds:
        if flow_7d >= threshold:
            return desc, color
    return "Very Strong Outflows", "#ff5757"

def render_etf_flows():
    """Render ETF flows component"""
    traditional_fetcher = TraditionalDataFetcher()
    
    # Fetch ETF flow data
    with st.spinner("Loading ETF flow data..."):
        etf_flows = traditional_fetcher.get_etf_flows()
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Spot ETF Net Flows</div>', unsafe_allow_html=True)
    
    if etf_flows and isinstance(etf_flows, dict):
        for asset, data in etf_flows.items():
            flow_7d = data.get('net_flow_7d', 0)
            flow_1d = data.get('net_flow_1d', 0)
            change_pct = data.get('change_pct', 0)
            total_aum = data.get('total_aum', 0)
            
            interpretation, flow_color = get_flow_interpretation(flow_7d, asset)
            change_color = "positive" if change_pct > 0 else "negative" if change_pct < 0 else "neutral"
            
            html_content = f"""
                <div style="margin: 20px 0; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px; border-left: 4px solid {flow_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="color: white; font-weight: 700; font-size: 18px;">{asset} ETF</div>
                        <div style="text-align: right;">
                            <div style="color: {flow_color}; font-weight: 700; font-size: 20px;">
                                ${flow_7d:+,.0f}M
                            </div>
                            <div style="color: #a0a0a0; font-size: 12px;">7-day net</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #a0a0a0;">Daily Flow:</span>
                        <span style="color: white; font-weight: 600;">${flow_1d:+,.0f}M</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #a0a0a0;">Weekly Change:</span>
                        <span class="{change_color}" style="font-weight: 600;">{format_percentage(change_pct)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #a0a0a0;">Total AUM:</span>
                        <span style="color: white; font-weight: 600;">${total_aum:,.0f}M</span>
                    </div>
                    <div style="color: {flow_color}; font-size: 14px; font-weight: 600; text-align: center; margin-top: 10px; padding: 8px; background: rgba(0,0,0,0.3); border-radius: 6px;">
                        {interpretation}
                    </div>
                </div>
            """
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="color: #ff5757; text-align: center; padding: 20px;">
                Unable to fetch ETF flow data
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Educational content about ETF flows
    st.markdown("""
    <div class="funding-explanation">
        <strong>📈 ETF Flows Explained:</strong><br><br>
        <strong>Inflows (Positive):</strong> New institutional/retail money entering crypto → Bullish pressure<br>
        <strong>Outflows (Negative):</strong> Money leaving crypto markets → Bearish pressure<br><br>
        <strong>💡 Key Insights:</strong><br>
        • Large inflows (>$200M/week) often drive sustained rallies<br>
        • Consistent outflows may indicate trend reversal<br>
        • Daily vs weekly flows show short vs medium-term sentiment
    </div>
    """, unsafe_allow_html=True)
    
    # Market context
    total_flows = sum(data.get('net_flow_7d', 0) for data in (etf_flows.values() if etf_flows else []))
    flow_color = "positive" if total_flows > 0 else "negative" if total_flows < 0 else "neutral"
    
    st.markdown(f"""
    <div style="background: #2a2a3a; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px solid #3d3d4d;">
        <div style="text-align: center;">
            <div style="color: #a0a0a0; font-size: 14px; margin-bottom: 5px;">Combined 7-Day Net Flow</div>
            <div class="{flow_color}" style="font-size: 24px; font-weight: 700;">
                ${total_flows:+,.0f}M
            </div>
            <div style="color: #a0a0a0; font-size: 12px; margin-top: 5px;">
                {"Institutional buying pressure" if total_flows > 0 else "Institutional selling pressure" if total_flows < 0 else "Neutral institutional sentiment"}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)