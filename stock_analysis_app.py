"""
Wealth Portfolio Analysis Dashboard
Supports:
  1. Dynamic Multi-Asset (Blend Stocks & MFs)
  2. Case Study (Compare 2 Assets)
  3. Single Stock Deep Dive
  4. Single Mutual Fund Deep Dive
  - Adaptive UI (Light/Dark Mode)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wealth Portfolio Analyser",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING (Adaptive Light/Dark Theme)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 800; color: var(--text-color); text-align: center; padding: 1rem 0 0.3rem 0; }
    .sub-header { text-align: center; color: var(--text-color); opacity: 0.8; font-size: 1.1rem; margin-bottom: 2rem; }
    .metric-card { border-radius: 12px; padding: 1rem 1.2rem; margin: 0.3rem 0; text-align: center; color: #ffffff !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #ffffff !important; }
    .metric-label { font-size: 0.9rem; font-weight: 500; opacity: 0.95; color: #ffffff !important; }
    .card-green { background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%); } 
    .card-cobalt { background: linear-gradient(135deg, #36D1DC 0%, #5B86E5 100%); } 
    .card-cyan { background: linear-gradient(135deg, #00C9FF 0%, #0088CC 100%); } 
    .card-dark { background: linear-gradient(135deg, #373B44 0%, #4286f4 100%); } 
    .card-orange { background: linear-gradient(135deg, #f12711 0%, #f5af19 100%); }
    .section-title { font-size: 1.4rem; font-weight: 700; color: var(--text-color); border-left: 4px solid #00b09b; padding-left: 0.8rem; margin: 1.5rem 0 1rem 0; }
    .subsection-title { font-size: 1.1rem; font-weight: 600; color: #5B86E5; margin-bottom: 0.5rem; }
    .info-box { background: var(--secondary-background-color); border: 1px solid #5B86E5; border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0; font-size: 0.9rem; color: var(--text-color); }
</style>
""", unsafe_allow_html=True)

fintech_colors = ['#00b09b', '#5B86E5', '#f5af19', '#00C9FF', '#E91E63', '#8E44AD', '#2ECC71']

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def auto_detect_columns(df):
    date_col = next((c for c in df.columns if 'date' in str(c).lower() or 'month' in str(c).lower()), df.columns[0])
    price_col = next((c for c in df.columns if any(x in str(c).lower() for x in ['close', 'price', 'nav'])), df.columns[1] if len(df.columns) > 1 else df.columns[0])
    div_col = next((c for c in df.columns if 'div' in str(c).lower()), None)
    return date_col, price_col, div_col

def calculate_metrics(df, price_col, div_col=None, freq="Monthly"):
    prices = pd.to_numeric(df[price_col], errors='coerce').dropna()
    divs = pd.to_numeric(df[div_col], errors='coerce').fillna(0) if div_col and div_col in df.columns else pd.Series([0]*len(prices), index=prices.index)
    
    returns = ((prices - prices.shift(1) + divs) / prices.shift(1)).dropna() * 100
    ann_factor = 252 if freq == "Daily" else 12
    
    if len(returns) > 0:
        compounded_growth = np.prod(1 + returns / 100)
        years = len(returns) / ann_factor
        cagr = (compounded_growth ** (1 / years) - 1) * 100 if years > 0 else 0.0
    else: cagr = 0.0
        
    avg_ret = returns.mean()
    risk = returns.std()
    ann_risk = risk * np.sqrt(ann_factor)
    cv = (risk / avg_ret) if avg_ret != 0 else np.nan
    return {'returns': returns, 'cagr': cagr, 'risk': risk, 'ann_risk': ann_risk, 'avg_return': avg_ret, 'cv': cv}

def n_asset_portfolio_metrics(weights, cov_matrix, avg_returns, ann_factor):
    w = np.array(weights)
    ret = np.array(avg_returns)
    port_var = np.dot(w.T, np.dot(cov_matrix, w)) * ann_factor
    return np.sum(w * ret) * ann_factor, np.sqrt(port_var)

def color_metric(label, value, unit="", color="green"):
    css_class = {"green": "metric-card card-green", "cyan": "metric-card card-cyan", "cobalt": "metric-card card-cobalt", "dark": "metric-card card-dark", "orange": "metric-card card-orange"}.get(color, "metric-card card-dark")
    return f'<div class="{css_class}"><div class="metric-value">{value}{unit}</div><div class="metric-label">{label}</div></div>'

# ─────────────────────────────────────────────────────────────────────────────
# HEADER & SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">📈 Wealth Portfolio Analyser</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Data-Driven Optimization for Stocks & Mutual Funds</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📂 Analysis Mode")
    # THE 4 EXPLICIT OPTIONS
    mode = st.radio("", [
        "1. Dynamic Multi-Asset", 
        "2. Case Study (2 Assets)", 
        "3. Single Stock Deep Dive",
        "4. Single Mutual Fund Deep Dive"
    ])
    st.divider()
    
    st.markdown("### 💰 Investment Setup")
    investment_amount = st.number_input("Total Investment (₹)", min_value=1000, value=100000, step=10000)
    st.divider()
    show_raw = st.checkbox("Show Raw Data Tables", value=False)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 1: DYNAMIC MULTI-ASSET PORTFOLIO
# ─────────────────────────────────────────────────────────────────────────────
if mode == "1. Dynamic Multi-Asset":
    st.markdown('<div class="section-title">Step 1: Portfolio Setup</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    data_freq = c1.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
    n_stocks = c2.number_input("How many Stocks?", min_value=0, max_value=10, value=2)
    n_mfs = c3.number_input("How many Mutual Funds?", min_value=0, max_value=10, value=1)
    n_total = n_stocks + n_mfs
    
    if n_total < 2:
        st.warning("⚠️ Please select at least 2 assets in total (Stocks + Mutual Funds).")
        st.stop()
        
    st.markdown('<div class="section-title">Step 2: Upload Asset Data</div>', unsafe_allow_html=True)
    upload_cols = st.columns(n_total)
    uploaded_files = {}
    
    col_idx = 0
    for i in range(n_stocks):
        with upload_cols[col_idx]:
            st.markdown(f'<div class="subsection-title">📈 Stock {i+1}</div>', unsafe_allow_html=True)
            c_name = st.text_input(f"Name", f"Stock {i+1}", key=f"s_name_{i}")
            c_file = st.file_uploader(f"Upload CSV", type=["csv"], key=f"s_file_{i}")
            if c_file: uploaded_files[c_name] = c_file
        col_idx += 1
        
    for i in range(n_mfs):
        with upload_cols[col_idx]:
            st.markdown(f'<div class="subsection-title">🏦 MF {i+1}</div>', unsafe_allow_html=True)
            c_name = st.text_input(f"Name", f"MF {i+1}", key=f"m_name_{i}")
            c_file = st.file_uploader(f"Upload CSV", type=["csv"], key=f"m_file_{i}")
            if c_file: uploaded_files[c_name] = c_file
        col_idx += 1

    if len(uploaded_files) < n_total:
        st.info(f"⏳ Waiting for you to upload all {n_total} files...")
        st.stop()
        
    all_metrics = {}
    combined_returns = pd.DataFrame()
    combined_prices = pd.DataFrame()
    
    with st.spinner("Aligning Dates, Prices, and NAVs into a single matrix..."):
        for comp, file in uploaded_files.items():
            df = pd.read_csv(file)
            date_col, price_col, div_col = auto_detect_columns(df)
            df['Standard_Date'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['Standard_Date']).sort_values('Standard_Date').set_index('Standard_Date')
            m = calculate_metrics(df, price_col, div_col, data_freq)
            all_metrics[comp] = m
            combined_returns[comp] = m['returns']
            combined_prices[comp] = pd.to_numeric(df[price_col], errors='coerce')
        combined_returns = combined_returns.dropna()
        combined_prices = combined_prices.dropna()
        ann_factor = 252 if data_freq == "Daily" else 12

    st.markdown('<div class="section-title">Step 3: Analytics Dashboard</div>', unsafe_allow_html=True)
    tabs = st.tabs(["📊 Price Chart", "📈 Return Distribution", "🧮 Metrics", "🗂 Portfolio & Projections", "🔮 Efficient Frontier"])

    with tabs[0]:
        normalized_prices = (combined_prices / combined_prices.iloc[0]) * 100
        fig = px.line(normalized_prices.reset_index(), x='Standard_Date', y=normalized_prices.columns, color_discrete_sequence=fintech_colors, labels={'value': 'Growth (Base 100)', 'Standard_Date': 'Date', 'variable': 'Asset'})
        fig.update_layout(height=500, hovermode="x unified", legend=dict(orientation="h", y=1.02, x=0.5, xanchor='center'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        fig2 = go.Figure()
        for i, comp in enumerate(combined_returns.columns):
            fig2.add_trace(go.Histogram(x=combined_returns[comp], name=comp, opacity=0.8, marker_color=fintech_colors[i % len(fintech_colors)], nbinsx=30))
        fig2.update_layout(height=450, barmode='overlay', xaxis_title=f"{data_freq} Return (%)", yaxis_title="Frequency")
        st.plotly_chart(fig2, use_container_width=True)

    with tabs[2]:
        cols = st.columns(len(uploaded_files))
        for i, comp in enumerate(uploaded_files.keys()):
            m = all_metrics[comp]
            with cols[i]:
                st.markdown(f"<h3 style='text-align:center;'>{comp}</h3>", unsafe_allow_html=True)
                st.markdown(color_metric(f"Avg {data_freq} Return", f"{m['avg_return']:.3f}", "%", "cobalt"), unsafe_allow_html=True)
                st.markdown(color_metric("CAGR (Annualized)", f"{m['cagr']:.2f}", "%", "green"), unsafe_allow_html=True)
                st.markdown(color_metric("Risk (Annualized)", f"{m['ann_risk']:.2f}", "%", "cyan"), unsafe_allow_html=True)
                st.markdown(color_metric("Coeff. of Variation", f"{m['cv']:.3f}", "", "dark"), unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('### ⚖️ 1. Set Portfolio Weights')
        weight_cols = st.columns(n_total)
        weights_input = []
        for i, comp in enumerate(uploaded_files.keys()):
            with weight_cols[i]:
                w = st.number_input(f"{comp} Weight (%)", 0.0, 100.0, round(100/n_total, 1), 0.5, key=f"pw_{comp}")
                weights_input.append(w)
        if abs(sum(weights_input) - 100) > 0.01: st.warning(f"⚠️ Your weights sum to {sum(weights_input):.1f}%. Adjust to 100%.")

        st.divider()
        st.markdown('### 🧮 2. Covariance & Correlation')
        mc1, mc2 = st.columns(2)
        with mc1: st.write("**Covariance Matrix**"); st.dataframe(combined_returns.cov().style.background_gradient(cmap='Greens'), use_container_width=True)
        with mc2: st.write("**Correlation Matrix**"); st.dataframe(combined_returns.corr().style.background_gradient(cmap='RdBu', vmin=-1, vmax=1), use_container_width=True)

        st.divider()
        st.markdown('### 🚀 3. Final Portfolio Result & Projections')
        w_norm = [w / 100 for w in weights_input]
        port_ret, port_risk = n_asset_portfolio_metrics(w_norm, combined_returns.cov().values, [all_metrics[c]['avg_return'] for c in uploaded_files.keys()], ann_factor)
        
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(color_metric("Portfolio Return (Ann.)", f"{port_ret:.3f}", "%", "green"), unsafe_allow_html=True)
        with r2: st.markdown(color_metric("Portfolio Risk (Ann.)", f"{port_risk:.3f}", "%", "cyan"), unsafe_allow_html=True)
        with r3: st.markdown(color_metric("Sharpe Ratio", f"{(port_ret/port_risk):.3f}" if port_risk>0 else "0", "", "dark"), unsafe_allow_html=True)
        
        expected_return_rs = investment_amount * (port_ret / 100)
        v1, v2, v3 = st.columns(3)
        with v1: st.markdown(color_metric("Projected Total Value", f"₹{(investment_amount + expected_return_rs):,.0f}", "", "cobalt"), unsafe_allow_html=True)
        with v2: st.markdown(color_metric("Expected Return", f"+₹{expected_return_rs:,.0f}", "", "green"), unsafe_allow_html=True)
        with v3: st.markdown(color_metric("Potential Risk (±1σ)", f"±₹{(investment_amount * (port_risk / 100)):,.0f}", "", "orange"), unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('### Efficient Frontier (Monte Carlo)')
        n_sim = st.slider("Number of Simulations", 500, 5000, 2000, 500)
        sim_rets, sim_risks, sim_sharpes, sim_weights = [], [], [], []
        np.random.seed(42)
        for _ in range(n_sim):
            w = np.random.dirichlet(np.ones(n_total))
            r, risk = n_asset_portfolio_metrics(w, combined_returns.cov().values, combined_returns.mean().values, ann_factor)
            sim_rets.append(r); sim_risks.append(risk); sim_sharpes.append(r / risk if risk > 0 else 0); sim_weights.append(w)
            
        best_idx = np.argmax(sim_sharpes)
        fig_ef = px.scatter(pd.DataFrame({'Return': sim_rets, 'Risk': sim_risks, 'Sharpe': sim_sharpes}), x='Risk', y='Return', color='Sharpe', color_continuous_scale='Mint', height=500)
        fig_ef.add_trace(go.Scatter(x=[sim_risks[best_idx]], y=[sim_rets[best_idx]], mode='markers+text', text=['⭐ Max Sharpe'], textposition='top left', marker=dict(size=18, color='#FF9F1C', symbol='star'), name='Max Sharpe'))
        st.plotly_chart(fig_ef, use_container_width=True)
        
        st.markdown("**Optimal Weights:**")
        opt_cols = st.columns(n_total)
        for i, comp in enumerate(uploaded_files.keys()):
            with opt_cols[i]: st.metric(comp, f"{sim_weights[best_idx][i]*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# MODE 2: CASE STUDY (KO vs MSFT)
# ─────────────────────────────────────────────────────────────────────────────
elif mode == "2. Case Study (2 Assets)":
    uploaded_case = st.file_uploader("Upload Case Study CSV", type=["csv"])
    if not uploaded_case: st.stop()
    raw = pd.read_csv(uploaded_case)
    year_col = next((c for c in raw.columns if 'year' in c.lower()), raw.columns[0])
    num_cols = [c for c in raw.columns if raw[c].dtype in ['float64', 'int64'] and c != year_col]
    a1 = st.text_input("Asset 1 Name", num_cols[0] if num_cols else "Asset 1")
    a2 = st.text_input("Asset 2 Name", num_cols[1] if len(num_cols)>1 else "Asset 2")
    data = raw[[year_col, num_cols[0], num_cols[1]]].dropna()
    r1, r2 = data[num_cols[0]].astype(float), data[num_cols[1]].astype(float)
    m1, m2, s1, s2, cov12 = r1.mean(), r2.mean(), r1.std(), r2.std(), r1.cov(r2)
    
    t1, t2 = st.tabs(["📊 Compare Assets", "📈 Portfolio & Projections"])
    with t1:
        c1, c2 = st.columns(2)
        with c1: st.markdown(color_metric(f"{a1} Mean Return", f"{m1*100:.2f}", "%", "cobalt"), unsafe_allow_html=True); st.markdown(color_metric(f"{a1} Risk", f"{s1*100:.2f}", "%", "cyan"), unsafe_allow_html=True)
        with c2: st.markdown(color_metric(f"{a2} Mean Return", f"{m2*100:.2f}", "%", "cobalt"), unsafe_allow_html=True); st.markdown(color_metric(f"{a2} Risk", f"{s2*100:.2f}", "%", "cyan"), unsafe_allow_html=True)

    with t2:
        w1 = st.slider(f"Weight: {a1} (%)", 0, 100, 50, 5) / 100
        pr, prisk = w1*m1 + (1-w1)*m2, np.sqrt((w1**2 * s1**2) + ((1-w1)**2 * s2**2) + (2 * w1 * (1-w1) * cov12))
        pc1, pc2 = st.columns(2)
        with pc1: st.markdown(color_metric("Portfolio Return", f"{pr*100:.2f}", "%", "green"), unsafe_allow_html=True)
        with pc2: st.markdown(color_metric("Portfolio Risk", f"{prisk*100:.2f}", "%", "cyan"), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 3: SINGLE STOCK DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
elif mode == "3. Single Stock Deep Dive":
    st.markdown('<div class="section-title">Single Stock Deep Dive</div>', unsafe_allow_html=True)
    uploaded_custom = st.file_uploader("Upload Stock CSV", type=["csv"])
    if not uploaded_custom: st.stop()
        
    raw = pd.read_csv(uploaded_custom)
    d_col, p_col, div_col = auto_detect_columns(raw)
    freq = st.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
    
    c1, c2, c3 = st.columns(3)
    date_col = c1.selectbox("Date Column", raw.columns.tolist(), index=raw.columns.tolist().index(d_col) if d_col in raw.columns else 0)
    price_col = c2.selectbox("Close Price Column", raw.columns.tolist(), index=raw.columns.tolist().index(p_col) if p_col in raw.columns else 0)
    div_col_sel = c3.selectbox("Dividend Column (Optional)", ['None'] + raw.columns.tolist(), index=(raw.columns.tolist().index(div_col)+1) if div_col in raw.columns else 0)
    
    raw['Date'] = pd.to_datetime(raw[date_col], errors='coerce', dayfirst=True)
    raw = raw.dropna(subset=['Date']).sort_values('Date')
    m = calculate_metrics(raw, price_col, None if div_col_sel == 'None' else div_col_sel, freq)
    
    fig = px.line(raw, x='Date', y=price_col, title="Stock Price Timeline", color_discrete_sequence=['#00D09C'])
    st.plotly_chart(fig, use_container_width=True)
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1: st.markdown(color_metric("CAGR (Annualized)", f"{m['cagr']:.2f}", "%", "green"), unsafe_allow_html=True)
    with mc2: st.markdown(color_metric("Annualized Risk", f"{m['ann_risk']:.2f}", "%", "cyan"), unsafe_allow_html=True)
    with mc3: st.markdown(color_metric("Coeff. of Variation", f"{m['cv']:.3f}", "", "cobalt"), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 4: SINGLE MUTUAL FUND DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────
elif mode == "4. Single Mutual Fund Deep Dive":
    st.markdown('<div class="section-title">Mutual Fund Deep Dive</div>', unsafe_allow_html=True)
    uploaded_custom = st.file_uploader("Upload Mutual Fund CSV", type=["csv"])
    if not uploaded_custom: st.stop()
        
    raw = pd.read_csv(uploaded_custom)
    d_col, p_col, _ = auto_detect_columns(raw)
    freq = st.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
    
    c1, c2 = st.columns(2)
    date_col = c1.selectbox("Date Column", raw.columns.tolist(), index=raw.columns.tolist().index(d_col) if d_col in raw.columns else 0)
    # Using explicit NAV terminology for Mutual Funds
    price_col = c2.selectbox("NAV Column", raw.columns.tolist(), index=raw.columns.tolist().index(p_col) if p_col in raw.columns else 0)
    
    raw['Date'] = pd.to_datetime(raw[date_col], errors='coerce', dayfirst=True)
    raw = raw.dropna(subset=['Date']).sort_values('Date')
    m = calculate_metrics(raw, price_col, None, freq) # MFs don't typically use raw dividends in this analysis
    
    fig = px.line(raw, x='Date', y=price_col, title="Mutual Fund NAV Timeline", color_discrete_sequence=['#5B86E5'])
    st.plotly_chart(fig, use_container_width=True)
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1: st.markdown(color_metric("CAGR (Annualized)", f"{m['cagr']:.2f}", "%", "green"), unsafe_allow_html=True)
    with mc2: st.markdown(color_metric("Annualized Risk", f"{m['ann_risk']:.2f}", "%", "cyan"), unsafe_allow_html=True)
    with mc3: st.markdown(color_metric("Coeff. of Variation", f"{m['cv']:.3f}", "", "cobalt"), unsafe_allow_html=True)

st.divider()
st.markdown('<div style="text-align:center; color:var(--text-color); opacity: 0.6; font-size:0.85rem;">Wealth Portfolio Analyser · Built with Streamlit</div>', unsafe_allow_html=True)