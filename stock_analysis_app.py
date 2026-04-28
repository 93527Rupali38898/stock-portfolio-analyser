"""
Wealth Portfolio Analysis Dashboard
Supports:
  1. Dynamic Multi-Asset (All Combined)
  2. Multi-Stock Portfolio
  3. Multi-Mutual Fund Portfolio
  4. Single Stock Deep Dive
  5. Single Mutual Fund Deep Dive
  6. Fixed Deposit & Credit Risk Analysis (With Live API)
  - Adaptive UI (Light/Dark Mode)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests

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
# CSS STYLING
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
    .risk-box { background-color: rgba(241, 39, 17, 0.05); border-left: 4px solid #f12711; padding: 1rem; margin: 1rem 0; border-radius: 4px; font-size: 0.95rem; }
    .api-badge { display: inline-block; padding: 0.2rem 0.6rem; background-color: #2ECC71; color: white; border-radius: 4px; font-size: 0.8rem; font-weight: bold; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

fintech_colors = ['#00b09b', '#5B86E5', '#f5af19', '#00C9FF', '#E91E63', '#8E44AD', '#2ECC71']

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS & API INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400)
def fetch_live_inflation_india():
    """Fetches real-time inflation data for India from the World Bank API"""
    try:
        url = "http://api.worldbank.org/v2/country/IN/indicator/FP.CPI.TOTL.ZG?format=json&per_page=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_inflation = data[1][0]['value']
            return round(latest_inflation, 2), data[1][0]['date']
        return 5.5, "Fallback" 
    except Exception as e:
        return 5.5, "Offline Fallback"

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
st.markdown('<div class="sub-header">Enterprise-Grade Asset & Risk Management Platform</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📂 Analytics Modules")
    mode = st.radio("Select Module:", [
        "1. Dynamic Multi-Asset (All Combined)", 
        "2. Multi-Stock Portfolio",
        "3. Multi-Mutual Fund Portfolio",
        "4. Single Stock Deep Dive",
        "5. Single Mutual Fund Deep Dive",
        "6. Fixed Deposit & Credit Risk Analysis"
    ], label_visibility="collapsed")
    
    st.divider()
    
    st.markdown("### 🌐 Macroeconomic Data")
    use_live_api = st.toggle("Fetch Live World Bank Inflation (India)", value=True)
    if use_live_api:
        live_rate, data_year = fetch_live_inflation_india()
        if data_year not in ["Fallback", "Offline Fallback"]:
            st.success(f"Live Inflation: {live_rate}% ({data_year})")
            default_inflation = float(live_rate)
        else:
            st.warning("API Offline. Fallback: 5.5%")
            default_inflation = 5.5
    else:
        default_inflation = st.number_input("Manual Inflation (%)", value=5.5, step=0.1)

    st.divider()
    investment_amount = st.number_input("Capital Deployed (₹)", min_value=1000, value=100000, step=10000)

# ─────────────────────────────────────────────────────────────────────────────
# MODES 1, 2 & 3: MULTI-ASSET PORTFOLIO ENGINES
# ─────────────────────────────────────────────────────────────────────────────
if mode in ["1. Dynamic Multi-Asset (All Combined)", "2. Multi-Stock Portfolio", "3. Multi-Mutual Fund Portfolio"]:
    st.markdown('<div class="section-title">Step 1: Portfolio Configuration</div>', unsafe_allow_html=True)
    
    if mode == "1. Dynamic Multi-Asset (All Combined)":
        c1, c2, c3, c4 = st.columns(4)
        data_freq = c1.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
        n_stocks = c2.number_input("Equities (Stocks)", min_value=0, max_value=5, value=2)
        n_mfs = c3.number_input("Mutual Funds", min_value=0, max_value=5, value=1)
        n_fds = c4.number_input("Debt Instruments (FDs)", min_value=0, max_value=2, value=1)
    
    elif mode == "2. Multi-Stock Portfolio":
        c1, c2 = st.columns(2)
        data_freq = c1.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
        n_stocks = c2.number_input("Number of Equities", min_value=2, max_value=10, value=3)
        n_mfs, n_fds = 0, 0
        
    elif mode == "3. Multi-Mutual Fund Portfolio":
        c1, c2 = st.columns(2)
        data_freq = c1.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
        n_mfs = c2.number_input("Number of Mutual Funds", min_value=2, max_value=10, value=2)
        n_stocks, n_fds = 0, 0

    n_total = n_stocks + n_mfs + n_fds
    if n_total < 2:
        st.warning("⚠️ Please allocate at least 2 instruments to construct a valid portfolio matrix.")
        st.stop()
        
    st.markdown('<div class="section-title">Step 2: Ingest Asset Data</div>', unsafe_allow_html=True)
    upload_cols = st.columns(min(n_total, 4)) 
    uploaded_files, fd_data = {}, {}
    
    col_idx = 0
    for i in range(n_stocks):
        with upload_cols[col_idx % 4]:
            st.markdown(f'<div class="subsection-title">📈 Equity {i+1}</div>', unsafe_allow_html=True)
            c_name = st.text_input(f"Ticker", f"Stock {i+1}", key=f"s_name_{i}")
            c_file = st.file_uploader(f"Upload CSV", type=["csv"], key=f"s_file_{i}")
            if c_file: uploaded_files[c_name] = c_file
        col_idx += 1
        
    for i in range(n_mfs):
        with upload_cols[col_idx % 4]:
            st.markdown(f'<div class="subsection-title">🏦 Fund {i+1}</div>', unsafe_allow_html=True)
            c_name = st.text_input(f"Scheme Name", f"MF {i+1}", key=f"m_name_{i}")
            c_file = st.file_uploader(f"Upload CSV", type=["csv"], key=f"m_file_{i}")
            if c_file: uploaded_files[c_name] = c_file
        col_idx += 1
        
    for i in range(n_fds):
        with upload_cols[col_idx % 4]:
            st.markdown(f'<div class="subsection-title">🛡️ Debt/FD {i+1}</div>', unsafe_allow_html=True)
            fd_name = st.text_input(f"Instrument", f"HDFC Bank FD", key=f"fd_name_{i}")
            fd_rate = st.number_input(f"Nominal Yield (%)", min_value=1.0, max_value=15.0, value=6.5, step=0.1, key=f"fd_rate_{i}")
            
            # --- NEW FIX: Applying Credit Risk in Multi-Asset Mode ---
            inst_type = st.selectbox("Credit Profile", ["Tier-1 Private (0.05% Risk)", "Sovereign (0.00% Risk)", "AAA NBFC (0.25% Risk)"], key=f"fd_risk_{i}")
            if "0.00%" in inst_type: def_prob = 0.0000
            elif "0.05%" in inst_type: def_prob = 0.0005
            else: def_prob = 0.0025
            
            fd_data[fd_name] = {'rate': fd_rate, 'risk': def_prob}
        col_idx += 1

    if len(uploaded_files) < (n_stocks + n_mfs):
        st.info("⏳ Awaiting raw market data CSVs...")
        st.stop()
        
    all_metrics, combined_returns, combined_prices = {}, pd.DataFrame(), pd.DataFrame()
    with st.spinner("Processing Time Series & Computing Covariance Matrices..."):
        if uploaded_files:
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
        
        for fd_name, data in fd_data.items():
            rate = data['rate']
            def_prob = data['risk']
            
            # --- THE TRUE REAL YIELD FIX ---
            # 1. Calculate Expected Payoff considering default risk (Standard 3 Year Horizon for math)
            survival_prob = (1 - def_prob) ** 3
            expected_payoff = ((1 + rate/100)**3 * survival_prob) + (0.5 * (1 - survival_prob))
            risk_adjusted_cagr = ((expected_payoff) ** (1 / 3) - 1) * 100
            
            # 2. Apply Fisher Equation using Live Inflation
            real_rate = (((1 + risk_adjusted_cagr/100) / (1 + default_inflation/100)) - 1) * 100
            
            period_rate = real_rate / ann_factor 
            
            if combined_returns.empty:
                dummy_dates = pd.date_range(start='2023-01-01', periods=12, freq='M')
                combined_returns = pd.DataFrame(index=dummy_dates)
                combined_prices = pd.DataFrame(index=dummy_dates)
            combined_returns[fd_name] = period_rate
            growth_factors = 1 + (combined_returns[fd_name] / 100)
            combined_prices[fd_name] = 100 * growth_factors.cumprod() 
            
            # Dashboard will now show the TRUE Real Yield instead of Nominal
            all_metrics[fd_name] = {'cagr': real_rate, 'ann_risk': 0.0, 'avg_return': period_rate, 'cv': 0.0}

    all_assets = list(uploaded_files.keys()) + list(fd_data.keys())

    st.markdown('<div class="section-title">Step 3: Quantitative Dashboard</div>', unsafe_allow_html=True)
    if n_fds > 0:
        st.info(f"💡 Notice: Debt/FD assets are displaying **Real Yield (Inflation & Risk Adjusted)**. (Using Inflation: {default_inflation}%)")
        
    tabs = st.tabs(["📊 Price Action", "📈 Return Distribution", "🧮 Asset Metrics", "🗂 Portfolio Modeler", "🔮 Efficient Frontier"])

    with tabs[0]:
        normalized_prices = (combined_prices / combined_prices.iloc[0]) * 100
        fig = px.line(normalized_prices.reset_index(), x='Standard_Date', y=normalized_prices.columns, color_discrete_sequence=fintech_colors, labels={'value': 'Capital Growth (Base 100)', 'Standard_Date': 'Date', 'variable': 'Asset'})
        fig.update_layout(height=500, hovermode="x unified", legend=dict(orientation="h", y=1.02, x=0.5, xanchor='center'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        fig2 = go.Figure()
        for i, comp in enumerate(combined_returns.columns):
            fig2.add_trace(go.Histogram(x=combined_returns[comp], name=comp, opacity=0.8, marker_color=fintech_colors[i % len(fintech_colors)], nbinsx=30))
        fig2.update_layout(height=450, barmode='overlay', xaxis_title=f"{data_freq} Return (%)", yaxis_title="Frequency")
        st.plotly_chart(fig2, use_container_width=True)

    with tabs[2]:
        cols = st.columns(len(all_assets))
        for i, comp in enumerate(all_assets):
            m = all_metrics[comp]
            with cols[i]:
                st.markdown(f"<h3 style='text-align:center;'>{comp}</h3>", unsafe_allow_html=True)
                st.markdown(color_metric(f"Avg {data_freq} Return", f"{m['avg_return']:.3f}", "%", "cobalt"), unsafe_allow_html=True)
                st.markdown(color_metric("Real CAGR (Ann.)" if comp in fd_data else "CAGR (Ann.)", f"{m['cagr']:.2f}", "%", "green"), unsafe_allow_html=True)
                st.markdown(color_metric("Volatility (Risk)", f"{m['ann_risk']:.2f}", "%", "cyan"), unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('### ⚖️ 1. Capital Allocation')
        weight_cols = st.columns(n_total)
        weights_input = []
        default_weight = round(100 / n_total, 1)
        for i, comp in enumerate(all_assets):
            with weight_cols[i]:
                w = st.number_input(f"{comp} Weight (%)", 0.0, 100.0, default_weight, 0.5, key=f"pw_{comp}")
                weights_input.append(w)
        if abs(sum(weights_input) - 100) > 0.01: st.warning(f"⚠️ Allocation sums to {sum(weights_input):.1f}%. Must equal 100%.")

        st.divider()
        st.markdown('### 🧮 2. Risk Matrix (Covariance & Correlation)')
        cov_matrix_df = combined_returns.cov().fillna(0)
        corr_matrix_df = combined_returns.corr().fillna(0) 
        mc1, mc2 = st.columns(2)
        with mc1: st.write("**Covariance Matrix**"); st.dataframe(cov_matrix_df.style.background_gradient(cmap='Greens'), use_container_width=True)
        with mc2: st.write("**Correlation Matrix**"); st.dataframe(corr_matrix_df.style.background_gradient(cmap='RdBu', vmin=-1, vmax=1), use_container_width=True)

        st.divider()
        st.markdown('### 🚀 3. Portfolio Projections (Real Growth)')
        w_norm = [w / 100 for w in weights_input]
        port_ret, port_risk = n_asset_portfolio_metrics(w_norm, cov_matrix_df.values, [all_metrics[c]['avg_return'] for c in all_assets], ann_factor)
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(color_metric("Expected Return (Ann.)", f"{port_ret:.3f}", "%", "green"), unsafe_allow_html=True)
        with r2: st.markdown(color_metric("Portfolio Volatility", f"{port_risk:.3f}", "%", "cyan"), unsafe_allow_html=True)
        with r3: st.markdown(color_metric("Sharpe Ratio", f"{(port_ret/port_risk):.3f}" if port_risk>0 else "0", "", "dark"), unsafe_allow_html=True)
        
        expected_return_rs = investment_amount * (port_ret / 100)
        v1, v2, v3 = st.columns(3)
        with v1: st.markdown(color_metric("Projected AUM", f"₹{(investment_amount + expected_return_rs):,.0f}", "", "cobalt"), unsafe_allow_html=True)
        with v2: st.markdown(color_metric("Net Capital Gain", f"+₹{expected_return_rs:,.0f}", "", "green"), unsafe_allow_html=True)
        with v3: st.markdown(color_metric("Value at Risk (1σ)", f"±₹{(investment_amount * (port_risk / 100)):,.0f}", "", "orange"), unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('### Efficient Frontier Optimization (Monte Carlo)')
        n_sim = st.slider("Simulation Iterations", 500, 5000, 2000, 500)
        sim_rets, sim_risks, sim_sharpes, sim_weights = [], [], [], []
        np.random.seed(42)
        for _ in range(n_sim):
            w = np.random.dirichlet(np.ones(n_total))
            r, risk = n_asset_portfolio_metrics(w, cov_matrix_df.values, combined_returns.mean().values, ann_factor)
            sim_rets.append(r); sim_risks.append(risk); sim_sharpes.append(r / risk if risk > 0 else 0); sim_weights.append(w)
            
        best_idx = np.argmax(sim_sharpes)
        fig_ef = px.scatter(pd.DataFrame({'Return': sim_rets, 'Risk': sim_risks, 'Sharpe': sim_sharpes}), x='Risk', y='Return', color='Sharpe', color_continuous_scale='Mint', height=500)
        fig_ef.add_trace(go.Scatter(x=[sim_risks[best_idx]], y=[sim_rets[best_idx]], mode='markers+text', text=['⭐ Optimal Sharpe'], textposition='top left', marker=dict(size=18, color='#FF9F1C', symbol='star'), name='Optimal Portfolio'))
        st.plotly_chart(fig_ef, use_container_width=True)
        
        st.markdown("**Algorithmic Optimal Weights:**")
        opt_cols = st.columns(n_total)
        for i, comp in enumerate(all_assets):
            with opt_cols[i]: st.metric(comp, f"{sim_weights[best_idx][i]*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# MODES 4 & 5: SINGLE ASSET DEEP DIVES
# ─────────────────────────────────────────────────────────────────────────────
elif mode in ["4. Single Stock Deep Dive", "5. Single Mutual Fund Deep Dive"]:
    asset_type = "Stock" if "Stock" in mode else "Mutual Fund"
    st.markdown(f'<div class="section-title">{asset_type} Deep Dive Analytics</div>', unsafe_allow_html=True)
    uploaded_custom = st.file_uploader(f"Upload {asset_type} Data (CSV)", type=["csv"])
    if not uploaded_custom: st.stop()
        
    raw = pd.read_csv(uploaded_custom)
    d_col, p_col, div_col = auto_detect_columns(raw)
    freq = st.radio("Data Frequency", ["Monthly", "Daily"], horizontal=True)
    c1, c2, c3 = st.columns(3)
    date_col = c1.selectbox("Date Column", raw.columns.tolist(), index=raw.columns.tolist().index(d_col) if d_col in raw.columns else 0)
    price_col = c2.selectbox(f"{'Price' if asset_type=='Stock' else 'NAV'} Column", raw.columns.tolist(), index=raw.columns.tolist().index(p_col) if p_col in raw.columns else 0)
    if asset_type == "Stock":
        div_col_sel = c3.selectbox("Dividend Column (Optional)", ['None'] + raw.columns.tolist(), index=(raw.columns.tolist().index(div_col)+1) if div_col in raw.columns else 0)
    else:
        div_col_sel = 'None'
        
    raw['Date'] = pd.to_datetime(raw[date_col], errors='coerce', dayfirst=True)
    raw = raw.dropna(subset=['Date']).sort_values('Date')
    m = calculate_metrics(raw, price_col, None if div_col_sel == 'None' else div_col_sel, freq)
    
    fig = px.line(raw, x='Date', y=price_col, title=f"Historical {asset_type} Action", color_discrete_sequence=['#00D09C' if asset_type=='Stock' else '#5B86E5'])
    st.plotly_chart(fig, use_container_width=True)
    
    mc1, mc2, mc3 = st.columns(3)
    with mc1: st.markdown(color_metric("CAGR (Annualized)", f"{m['cagr']:.2f}", "%", "green"), unsafe_allow_html=True)
    with mc2: st.markdown(color_metric("Volatility (Risk)", f"{m['ann_risk']:.2f}", "%", "cyan"), unsafe_allow_html=True)
    with mc3: st.markdown(color_metric("Coeff. of Variation", f"{m['cv']:.3f}", "", "cobalt"), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 6: FIXED DEPOSIT & CREDIT RISK ANALYSIS 
# ─────────────────────────────────────────────────────────────────────────────
elif mode == "6. Fixed Deposit & Credit Risk Analysis":
    st.markdown('<div class="section-title">Fixed Income: Credit Risk & Real Yield Engine</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="risk-box">
    <strong>⚠️ Institutional Risk & Real Yield Mechanics:</strong>
    Fixed Deposits are not entirely "Risk-Free". This engine quantitatively adjusts your expected returns based on two parameters:
    <ul>
        <li><strong>Credit Default Risk:</strong> Sovereign Banks (e.g., SBI) have effectively 0% risk. Top Private Banks (e.g., HDFC) have negligible risk. NBFCs (e.g., Bajaj) offer higher nominal yields strictly to compensate for higher default probability.</li>
        <li><strong>Inflation Risk (Fisher Equation):</strong> Uses the formula <code>Real Rate = [(1 + Nominal) / (1 + Inflation)] - 1</code> to display actual purchasing power growth.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('### 🏛️ 1. Asset & Macroeconomic Profile')

    rc1, rc2 = st.columns([2, 1])
    institution_type = rc1.selectbox("Select Institution Credit Profile (Quantifies Default Risk)", [
        "Sovereign / PSU Bank (e.g., SBI) - 0.00% Annual Default Risk",
        "Tier-1 Private Bank (e.g., HDFC, ICICI) - 0.05% Annual Default Risk",
        "AAA-Rated NBFC (e.g., Bajaj Finance) - 0.25% Annual Default Risk",
        "A-Rated Corporate Deposit - 1.50% Annual Default Risk"
    ])
    
    if "0.00%" in institution_type: default_prob = 0.0000
    elif "0.05%" in institution_type: default_prob = 0.0005
    elif "0.25%" in institution_type: default_prob = 0.0025
    else: default_prob = 0.0150
        
    c1, c2, c3 = st.columns(3)
    principal = c1.number_input("Principal (₹)", min_value=1000, value=investment_amount, step=10000)
    rate = c2.number_input("Nominal Yield (%)", min_value=1.0, max_value=15.0, value=6.5 if "0.05%" in institution_type else (6.4 if "0.00%" in institution_type else 6.95), step=0.05)
    tenure = c3.slider("Tenure (Years)", min_value=1, max_value=20, value=3)
    
    compounding_freq = st.radio("Compounding Frequency", ["Quarterly (Standard)", "Annually", "Monthly"], horizontal=True)
    n = 4 if compounding_freq == "Quarterly (Standard)" else (1 if compounding_freq == "Annually" else 12)
    
    nominal_maturity = principal * (1 + (rate/100)/n)**(n * tenure)
    survival_prob = (1 - default_prob) ** tenure
    expected_payoff = (nominal_maturity * survival_prob) + (principal * 0.5 * (1 - survival_prob))
    risk_adjusted_cagr = ((expected_payoff / principal) ** (1 / tenure) - 1) * 100
    
    real_rate = (((1 + risk_adjusted_cagr/100) / (1 + default_inflation/100)) - 1) * 100
    real_maturity_amount = principal * (1 + real_rate/100)**tenure
    
    st.divider()
    st.markdown("### 📊 2. Risk-Adjusted Outcomes")
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(color_metric("Total Invested", f"₹{principal:,.0f}", "", "cobalt"), unsafe_allow_html=True)
    with m2: st.markdown(color_metric("Expected Payoff (Risk-Adj)", f"₹{expected_payoff:,.0f}", "", "green"), unsafe_allow_html=True)
    with m3: st.markdown(color_metric("Real Maturity (Purchasing Power)", f"₹{real_maturity_amount:,.0f}", "", "orange"), unsafe_allow_html=True)
    with m4: st.markdown(color_metric("True Real Yield", f"{real_rate:.2f}", "%", "dark"), unsafe_allow_html=True)
    
    years = np.arange(0, tenure + 1)
    nom_values = principal * (1 + (rate/100)/n)**(n * years)
    adj_values = principal * (1 + risk_adjusted_cagr/100)**years
    real_values = principal * (1 + real_rate/100)**years
    
    df_fd = pd.DataFrame({
        'Year': np.concatenate([years, years, years]),
        'Value': np.concatenate([nom_values, adj_values, real_values]),
        'Metric': ['1. Nominal (Paper Growth)'] * len(years) + ['2. Risk-Adjusted (Expected)'] * len(years) + ['3. Real Growth (Purchasing Power)'] * len(years)
    })
    
    fig = px.line(df_fd, x='Year', y='Value', color='Metric', title=f"Yield Trajectories: Nominal vs. Risk-Adjusted vs. Real (Inflation: {default_inflation}%)", color_discrete_map={"1. Nominal (Paper Growth)": "#36D1DC", "2. Risk-Adjusted (Expected)": "#00b09b", "3. Real Growth (Purchasing Power)": "#f12711"})
    fig.update_layout(height=450, hovermode="x unified")
    fig.add_hrect(y=principal, line_dash="dash", line_color="gray", annotation_text="Initial Principal")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown('<div style="text-align:center; color:var(--text-color); opacity: 0.6; font-size:0.85rem;">Wealth Portfolio Analyser · Enterprise Edition</div>', unsafe_allow_html=True)