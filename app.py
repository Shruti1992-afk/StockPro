import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION & FULL DARK THEME ---
st.set_page_config(page_title="StockPro Journey", layout="wide")

# CSS for UI/UX: High Contrast, Dark Theme, and Button Styling
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, label, .stMarkdown { color: #ffffff !important; }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3b82f6;
    }
    [data-testid="stMetricValue"] { color: #00ffcc !important; }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #3b82f6, #2563eb);
        color: white !important;
        height: 3em;
        font-weight: bold;
        border-radius: 10px;
    }
    
    /* Progress Bar Color */
    .stProgress > div > div > div > div { background-color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1: Welcome, 2: Capital, 3: Inputs, 4: Analyzing, 5: Output, 6: Journal
if 'journal' not in st.session_state:
    st.session_state.journal = pd.DataFrame(columns=["Date", "Stock", "Entry", "SL", "Target", "Shares", "Investment", "Checks"])

# --- HELPER FUNCTIONS ---
def move_to(step_num):
    st.session_state.step = step_num
    st.rerun()

# --- SCREEN 1: WELCOME ---
if st.session_state.step == 1:
    st.markdown("<div class='welcome-box'>", unsafe_allow_html=True)
    st.title("🚀 StockPro Analysis")
    st.subheader("High-Precision Trading Journal & Position Sizer")
    st.write("Welcome! This system will guide you through your trade setup step-by-step.")
    st.divider()
    if st.button("Start New Analysis"):
        move_to(2)
    st.markdown("</div>", unsafe_allow_html=True)

# --- SCREEN 2: CAPITAL ENTRY ---
elif st.session_state.step == 2:
    st.title("💰 Capital Management")
    st.write("Step 1: Define your total trading capital.")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        capital = st.number_input("Enter Total Investment Value (INR)", value=100000, step=5000)
        st.session_state.total_inv = capital
        st.divider()
        if st.button("Next: Enter Trade Details →"):
            move_to(3)
        if st.button("← Back to Welcome", type="secondary"):
            move_to(1)

# --- SCREEN 3: TRADE ENTRY ---
elif st.session_state.step == 3:
    st.title("📝 Trade Setup")
    st.write("Step 2: Enter stock details and technical checkpoints.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.stock = st.text_input("Stock Ticker", "RELIANCE").upper()
        st.session_state.entry_price = st.number_input("Entry Price", min_value=1.0, value=2500.0)
        st.session_state.trade_date = st.date_input("Trade Date", datetime.now())
    with col2:
        st.session_state.stop_loss_orig = st.number_input("Original Stop Loss", min_value=0.0, value=2450.0)
        st.write("**Technical SMA Checks (50-Day)**")
        c1 = st.checkbox("Nifty 50 Trend")
        c2 = st.checkbox("Sensex Trend")
        c3 = st.checkbox("Industry Trend")
        c4 = st.checkbox("Stock Trend")
        st.session_state.checks = all([c1, c2, c3, c4])

    st.divider()
    if st.button("Run Strategy Analysis ⚡"):
        move_to(4)
    if st.button("← Back"):
        move_to(2)

# --- SCREEN 4: ANALYZING (LOADING) ---
elif st.session_state.step == 4:
    st.title("🔍 Analyzing Stock Strategy...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
        if percent_complete < 30: status_text.text("Checking Position Sizing...")
        elif percent_complete < 60: status_text.text("Calculating Scale-Out Targets...")
        else: status_text.text("Finalizing Trailing Stop Loss SL1...")
    
    move_to(5)

# --- SCREEN 5: FINAL OUTPUT ---
elif st.session_state.step == 5:
    st.title("📊 Analysis Results")
    
    # CALCULATIONS
    risk_amt = 0.01 * st.session_state.total_inv
    gap = st.session_state.entry_price - st.session_state.stop_loss_orig
    
    if gap > 0:
        shares = round(risk_amt / gap)
        invested = shares * st.session_state.entry_price
        target = st.session_state.entry_price + (2 * gap)
        half_s = shares / 2
        
        if half_s > 0:
            profit_50 = (target - st.session_state.entry_price) * half_s
            trans_val = (shares * st.session_state.entry_price) + (half_s * target)
            sl1 = ((profit_50 - 50 + (0.0001 * trans_val)) / half_s) + st.session_state.stop_loss_orig
        else: sl1 = 0
        
        # DISPLAY METRICS
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Quantity", shares)
        col2.metric("Investment", f"₹{invested:,.2f}")
        col3.metric("Sell 50% Target", f"₹{target:,.2f}")
        col4.metric("Trailing SL1", f"₹{sl1:,.2f}")

        st.divider()
        if st.session_state.checks:
            st.success("✅ Market Conditions: BUY ALIGNMENT PASSED")
        else:
            st.warning("⚠️ Market Conditions: ONE OR MORE SMA CHECKS FAILED")

        # Session data for Journal
        st.session_state.current_target = target
        st.session_state.current_shares = shares
        st.session_state.current_invested = invested

        if st.button("Save Entry & View Journal →"):
            new_entry = {
                "Date": st.session_state.trade_date.strftime("%Y-%m-%d"),
                "Stock": st.session_state.stock,
                "Entry": st.session_state.entry_price,
                "SL": st.session_state.stop_loss_orig,
                "Target": target,
                "Shares": int(shares),
                "Investment": invested,
                "Checks": "Passed" if st.session_state.checks else "Failed"
            }
            st.session_state.journal = pd.concat([st.session_state.journal, pd.DataFrame([new_entry])], ignore_index=True)
            move_to(6)
    else:
        st.error("Invalid Entry: Stop loss must be lower than Entry Price.")
        if st.button("Fix Input"): move_to(3)

# --- SCREEN 6: JOURNAL ---
elif st.session_state.step == 6:
    st.title("📁 Trade Vault")
    
    # Filter functionality
    search = st.selectbox("Search Records by Stock", ["Show All"] + sorted(st.session_state.journal["Stock"].unique().tolist()))
    df_to_show = st.session_state.journal if search == "Show All" else st.session_state.journal[st.session_state.journal["Stock"] == search]
    
    st.dataframe(df_to_show, use_container_width=True, hide_index=True)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Another Trade"): move_to(2)
    with col2:
        csv = st.session_state.journal.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Master Journal (CSV)", data=csv, file_name="trade_history.csv", mime="text/csv")