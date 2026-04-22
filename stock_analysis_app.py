"""
Stock Portfolio Analysis Dashboard
Supports:
  1. Dynamic Multi-Asset: Asks for N companies, calculates exact N-Asset Covariance & Portfolio Risk.
  2. Case Study: Compare any two assets.
  3. Single Custom CSV.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Portfolio Analyser",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS STYLING (Upgraded Fintech Color Palette)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem; font-weight: 800; color: #1a1a2e;
        text-align: center; padding: 1rem 0 0.3rem 0;
    }
    .sub-header {
        text-align: center; color: #888; font-size: 1rem; margin-bottom: 2rem;
    }
    .metric-card {
        border-radius: 12px; padding: 1rem 1.2rem;
        margin: 0.3rem 0; text-align: center;
        color: #ffffff !important; /* Forced white text */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-value { 
        font-size: 1.6rem; 
        font-weight: 700; 
        color: #ffffff !important; 
    }
    .metric-label { 
        font-size: 0.9rem; 
        font-weight: 500;
        opacity: 0.95; 
        color: #ffffff !important; 
    }
    
    /* NEW FINTECH COLORS */
    .card-green { background: linear-gradient(135deg, #00D09C 0%, #00A67C 100%); } /* Groww/Growth Green */
    .card-cobalt { background: linear-gradient(135deg, #0047AB 0%, #002266 100%); } /* Deep Cobalt Blue */
    .card-cyan { background: linear-gradient(135deg, #00C9FF 0%, #0088CC 100%); } /* Bright Cyan */
    .card-dark { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); } /* Slate Dark */
    
    .section-title {
        font-size: 1.4rem; font-weight: 700; color: #00D09C; /* Title Accent */
        border-left: 4px solid #00D09C; padding-left: 0.8rem; margin: 1.5rem 0 1rem 0;
    }
    .info-box {
        background: #1e293b; border: 1px solid #334155;
        border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0;
        font-size: 0.9rem; color: #e2e8f0;
    }
    div[data-testid="stTabs"] button { font-weight: 600; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CHART COLORS
# ─────────────────────────────────────────────────────────────────────────────
# Growth Green, Cyan, Cobalt, Vibrant Orange (for contrast), Pink, Purple
fintech_colors = ['#00D09C', '#00C9FF', '#0047AB', '#FF9F1C', '#E91E63', '#8E44AD']

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def auto_detect_columns(df):
    date_col = next((c for c in df.columns if 'date' in str(c).lower()), df.columns[0])
    price_col = next((c for c in df.columns if 'close' in str(c).lower() or 'price' in str(c).lower()), 
                     df.columns[1] if len(df.columns) > 1 else df.columns[0])
    div_col = next((c for c in df.columns if 'div' in str(c).lower()), None)
    return date_col, price_col, div_col

def calculate_metrics(df, price_col, div_col=None, freq="Monthly"):
    prices = pd.to_numeric(df[price_col], errors='coerce').dropna()
    divs = pd.to_numeric(df[div_col], errors='coerce').fillna(0) if div_col and div_col in df.columns else pd.Series([0]*len(prices), index=prices.index)
    
    total_prices = prices + divs
    returns = total_prices.pct_change().dropna() * 100
    
    ann_factor = 252 if freq == "Daily" else 12
    n_periods = len(prices) - 1
    
    if n_periods > 0 and prices.iloc[0] > 0:
        years = n_periods / ann_factor
        cagr = ((prices.iloc[-1] / prices.iloc[0]) ** (1 / years) - 1) * 100 if years > 0 else 0.0
    else:
        cagr = 0.0
        
    avg_ret = returns.mean()
    risk = returns.std()
    ann_risk = risk * np.sqrt(ann_factor)
    cv = (risk / avg_ret) if avg_ret != 0 else np.nan
    
    return {
        'returns': returns,
        'cagr': cagr,
        'risk': risk,           
        'ann_risk': ann_risk,   
        'avg_return': avg_ret,  
        'cv': cv
    }

def n_asset_portfolio_metrics(weights, cov_matrix, avg_returns, ann_factor):
    w = np.array(weights)
    ret = np.array(avg_returns)
    port_ret = np.sum(w * ret) * ann_factor
    port_var = np.dot(w.T, np.dot(cov_matrix, w)) * ann_factor
    port_risk = np.sqrt(port_var)
    return port_ret, port_risk

def color_metric(label, value, unit="", color="green"):
    css_class = {
        "green": "metric-card card-green",
        "cyan": "metric-card card-cyan",
        "cobalt": "metric-card card-cobalt",
        "dark": "metric-card card-dark",
    }.get(color, "metric-card card-dark")
    return f"""
    <div class="{css_class}">
        <div class="metric-value">{value}{unit}</div>
        <div class="metric-label">{label}</div>
    </div>"""

# ─────────────────────────────────────────────────────────────────────────────
# HEADER & SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header" style="color:white;">📈 Stock Portfolio Analyser</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload multiple companies to calculate exact Covariance & Portfolio Risk</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📂 Analysis Mode")
    mode = st.radio("", ["Dynamic Multi-Asset", "Case Study (2 Assets)", "Single Stock Deep Dive"])
    st.divider()
    theme_choice = st.selectbox("Chart Theme", ["plotly_dark", "plotly_white", "seaborn", "ggplot2"])
    show_raw = st.checkbox("Show Raw Data Tables", value=False)
    st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# MODE 1: DYNAMIC MULTI-ASSET PORTFOLIO
# ─────────────────────────────────────────────────────────────────────────────
if mode == "Dynamic Multi-Asset":
    
    st.markdown('<div class="section-title">Step 1: Portfolio Setup</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    data_freq = c1.radio("Data Frequency (Affects Annualization)", ["Monthly", "Daily"], horizontal=True)
    n_assets = c2.number_input("How many companies do you want to analyze?", min_value=2, max_value=10, value=3)
    
    st.markdown('<div class="section-title">Step 2: Upload Company Data</div>', unsafe_allow_html=True)
    
    upload_cols = st.columns(n_assets)
    uploaded_files = {}
    
    for i in range(n_assets):
        with upload_cols[i]:
            c_name = st.text_input(f"Name for Company {i+1}", f"Stock {i+1}")
            c_file = st.file_uploader(f"Upload CSV", type=["csv"], key=f"file_{i}")
            if c_file is not None:
                uploaded_files[c_name] = c_file

    if len(uploaded_files) < n_assets:
        st.info(f"⏳ Waiting for you to upload all {n_assets} files...")
        st.stop()
        
    all_metrics = {}
    combined_returns = pd.DataFrame()
    combined_prices = pd.DataFrame()
    
    with st.spinner("Aligning dates and calculating matrix data..."):
        for comp, file in uploaded_files.items():
            df = pd.read_csv(file)
            date_col, price_col, div_col = auto_detect_columns(df)
            
            df['Standard_Date'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
            df = df.dropna(subset=['Standard_Date']).sort_values('Standard_Date')
            df.set_index('Standard_Date', inplace=True)
            
            m = calculate_metrics(df, price_col, div_col, data_freq)
            m['data'] = df
            all_metrics[comp] = m
            
            combined_returns[comp] = m['returns']
            combined_prices[comp] = pd.to_numeric(df[price_col], errors='coerce')
            
        combined_returns = combined_returns.dropna()
        combined_prices = combined_prices.dropna()

    st.markdown('<div class="section-title">Step 3: Analytics Dashboard</div>', unsafe_allow_html=True)
    tabs = st.tabs(["📊 Price Chart", "📈 Return Distribution", "🧮 Metrics", "🗂 Portfolio & Covariance", "🔮 Efficient Frontier"])

    with tabs[0]:
        fig = px.line(combined_prices.reset_index(), x='Standard_Date', y=combined_prices.columns,
                      color_discrete_sequence=fintech_colors, # Custom Colors Applied
                      template=theme_choice, labels={'value': 'Price', 'Standard_Date': 'Date', 'variable': 'Company'})
        fig.update_layout(height=500, hovermode="x unified", legend=dict(orientation="h", y=1.02, x=0.5, xanchor='center'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        fig2 = go.Figure()
        for i, comp in enumerate(combined_returns.columns):
            fig2.add_trace(go.Histogram(
                x=combined_returns[comp], name=comp, opacity=0.8,
                marker_color=fintech_colors[i % len(fintech_colors)], nbinsx=30
            ))
        fig2.update_layout(template=theme_choice, height=450, barmode='overlay',
                           xaxis_title=f"{data_freq} Return (%)", yaxis_title="Frequency")
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
        weight_cols = st.columns(n_assets)
        weights_input = []
        default_weight = round(100 / n_assets, 1)
        for i, comp in enumerate(uploaded_files.keys()):
            with weight_cols[i]:
                w = st.number_input(f"{comp} Weight (%)", 0.0, 100.0, default_weight, 0.5, key=f"pw_{comp}")
                weights_input.append(w)
                
        if abs(sum(weights_input) - 100) > 0.01:
            st.warning(f"⚠️ Your weights currently sum to {sum(weights_input):.1f}%. Please adjust them to exactly 100%.")

        st.divider()
        st.markdown('### 🧮 2. Matrix Calculations')
        cov_matrix_df = combined_returns.cov()
        corr_matrix_df = combined_returns.corr()
        
        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**Covariance Matrix**")
            st.dataframe(cov_matrix_df.style.background_gradient(cmap='Greens'), use_container_width=True)
        with mc2:
            st.markdown("**Correlation Matrix**")
            st.dataframe(corr_matrix_df.style.background_gradient(cmap='RdBu', vmin=-1, vmax=1), use_container_width=True)

        st.divider()
        st.markdown('### 🚀 3. Final Portfolio Result')
        
        avg_rets = [all_metrics[c]['avg_return'] for c in uploaded_files.keys()]
        w_norm = [w / 100 for w in weights_input]
        ann_factor = 252 if data_freq == "Daily" else 12
        
        port_ret, port_risk = n_asset_portfolio_metrics(w_norm, cov_matrix_df.values, avg_rets, ann_factor)
        
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(color_metric("Portfolio Return (Ann.)", f"{port_ret:.3f}", "%", "green"), unsafe_allow_html=True)
        with r2: st.markdown(color_metric("Portfolio Risk (Ann.)", f"{port_risk:.3f}", "%", "cyan"), unsafe_allow_html=True)
        with r3: st.markdown(color_metric("Sharpe Ratio", f"{(port_ret/port_risk):.3f}" if port_risk>0 else "0", "", "cobalt"), unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('### Efficient Frontier (Monte Carlo)')
        n_sim = st.slider("Number of Simulations", 500, 5000, 2000, 500)
        
        avg_rets2 = combined_returns.mean().values
        cov_matrix2 = combined_returns.cov().values
        
        sim_rets, sim_risks, sim_sharpes, sim_weights = [], [], [], []
        np.random.seed(42)
        
        for _ in range(n_sim):
            w = np.random.dirichlet(np.ones(n_assets))
            r, risk = n_asset_portfolio_metrics(w, cov_matrix2, avg_rets2, ann_factor)
            sharpe = r / risk if risk > 0 else 0
            sim_rets.append(r)
            sim_risks.append(risk)
            sim_sharpes.append(sharpe)
            sim_weights.append(w)
            
        sim_df = pd.DataFrame({'Return': sim_rets, 'Risk': sim_risks, 'Sharpe': sim_sharpes})
        
        fig_ef = px.scatter(
            sim_df, x='Risk', y='Return', color='Sharpe', color_continuous_scale='Mint', # Upgraded color scale
            labels={'Risk': 'Annualized Risk (%)', 'Return': 'Annualized Return (%)'},
            template=theme_choice, height=500
        )
        
        best_idx = np.argmax(sim_sharpes)
        fig_ef.add_trace(go.Scatter(
            x=[sim_risks[best_idx]], y=[sim_rets[best_idx]],
            mode='markers+text', text=['⭐ Max Sharpe'], textposition='top left',
            marker=dict(size=18, color='#FF9F1C', symbol='star'), name='Max Sharpe Portfolio'
        ))
        
        st.plotly_chart(fig_ef, use_container_width=True)
        
        st.markdown("**Optimal Weights (Max Sharpe Ratio):**")
        opt_cols = st.columns(n_assets)
        best_w = sim_weights[best_idx]
        for i, comp in enumerate(uploaded_files.keys()):
            with opt_cols[i]:
                st.metric(comp, f"{best_w[i]*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# MODE 2: CASE STUDY (KO vs MSFT)
# ─────────────────────────────────────────────────────────────────────────────
elif mode == "Case Study (2 Assets)":
    uploaded_case = st.file_uploader("Upload Case Study CSV", type=["csv"])
    if not uploaded_case:
        st.info("👈 Upload your Case Study CSV (Year, Asset1 Returns, Asset2 Returns).")
        st.stop()
    
    raw = pd.read_csv(uploaded_case)
    year_col = next((c for c in raw.columns if 'year' in c.lower()), raw.columns[0])
    num_cols = [c for c in raw.columns if raw[c].dtype in ['float64', 'int64'] and c != year_col]
    
    a1 = st.text_input("Asset 1 Name", num_cols[0] if num_cols else "Asset 1")
    a2 = st.text_input("Asset 2 Name", num_cols[1] if len(num_cols)>1 else "Asset 2")
    
    data = raw[[year_col, num_cols[0], num_cols[1]]].dropna()
    data.columns = ['Year', a1, a2]
    
    r1, r2 = data[a1].astype(float), data[a2].astype(float)
    m1, m2 = r1.mean(), r2.mean()
    s1, s2 = r1.std(), r2.std()
    cov12, corr12 = r1.cov(r2), r1.corr(r2)
    
    t1, t2 = st.tabs(["📊 Compare Assets", "📈 Portfolio & Sensitivity"])
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(color_metric(f"{a1} Mean Return", f"{m1*100:.2f}", "%", "cobalt"), unsafe_allow_html=True)
            st.markdown(color_metric(f"{a1} Risk", f"{s1*100:.2f}", "%", "cyan"), unsafe_allow_html=True)
        with c2:
            st.markdown(color_metric(f"{a2} Mean Return", f"{m2*100:.2f}", "%", "cobalt"), unsafe_allow_html=True)
            st.markdown(color_metric(f"{a2} Risk", f"{s2*100:.2f}", "%", "cyan"), unsafe_allow_html=True)
        st.markdown(f'<div class="info-box" style="text-align:center;"><b>Correlation: {corr12:.3f}</b></div>', unsafe_allow_html=True)

    with t2:
        w1 = st.slider(f"Weight: {a1} (%)", 0, 100, 50, 5) / 100
        w2 = 1 - w1
        pr = w1 * m1 + w2 * m2
        pvar = (w1**2 * s1**2) + (w2**2 * s2**2) + (2 * w1 * w2 * cov12)
        prisk = np.sqrt(pvar)
        
        pc1, pc2 = st.columns(2)
        with pc1: st.markdown(color_metric("Portfolio Return", f"{pr*100:.2f}", "%", "green"), unsafe_allow_html=True)
        with pc2: st.markdown(color_metric("Portfolio Risk", f"{prisk*100:.2f}", "%", "cyan"), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 3: SINGLE STOCK
# ─────────────────────────────────────────────────────────────────────────────
else:
    uploaded_custom = st.file_uploader("Upload Single Stock CSV", type=["csv"])
    if not uploaded_custom:
        st.info("👈 Upload a CSV with Date and Closing Price.")
        st.stop()
        
    raw = pd.read_csv(uploaded_custom)
    d_col, p_col, div_col = auto_detect_columns(raw)
    freq = st.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
    
    st.markdown('<div class="section-title">Column Mapping Validation</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    date_col = c1.selectbox("Date Column", raw.columns.tolist(), index=raw.columns.tolist().index(d_col) if d_col in raw.columns else 0)
    price_col = c2.selectbox("Price Column", raw.columns.tolist(), index=raw.columns.tolist().index(p_col) if p_col in raw.columns else 0)
    div_col_sel = c3.selectbox("Dividend Column (Optional)", ['None'] + raw.columns.tolist(), index=(raw.columns.tolist().index(div_col)+1) if div_col in raw.columns else 0)
    
    raw['Date'] = pd.to_datetime(raw[date_col], errors='coerce', dayfirst=True)
    raw = raw.dropna(subset=['Date']).sort_values('Date')
    
    m = calculate_metrics(raw, price_col, None if div_col_sel == 'None' else div_col_sel, freq)
    
    fig = px.line(raw, x='Date', y=price_col, title="Price Timeline", template=theme_choice, color_discrete_sequence=['#00D09C'])
    st.plotly_chart(fig, use_container_width=True)
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1: st.markdown(color_metric("CAGR", f"{m['cagr']:.2f}", "%", "green"), unsafe_allow_html=True)
    with mc2: st.markdown(color_metric("Annualized Risk", f"{m['ann_risk']:.2f}", "%", "cyan"), unsafe_allow_html=True)
    with mc3: st.markdown(color_metric("Coeff. of Variation", f"{m['cv']:.3f}", "", "cobalt"), unsafe_allow_html=True)

st.divider()
st.markdown('<div style="text-align:center; color:#888; font-size:0.85rem;">Stock Portfolio Analyser · Built with Streamlit</div>', unsafe_allow_html=True)
