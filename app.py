import streamlit as st
import pandas as pd
from datetime import datetime
import time
# IMPORTANT: Missing import added here
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="StockPro Journey", layout="wide")

# Initialize Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# CSS for UI/UX
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, label, .stMarkdown { color: #ffffff !important; }
    [data-testid="stMetric"] {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3b82f6;
    }
    [data-testid="stMetricValue"] { color: #00ffcc !important; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #3b82f6, #2563eb);
        color: white !important;
        height: 3em;
        font-weight: bold;
        border-radius: 10px;
    }
    .stProgress > div > div > div > div { background-color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'journal' not in st.session_state:
    st.session_state.journal = pd.DataFrame(columns=["Email", "Date", "Stock", "Entry Price", "No. of Shares"])

def move_to(step_num):
    st.session_state.step = step_num
    st.rerun()

# --- SCREENS 1-4 (Same as yours) ---
if st.session_state.step == 1:
    st.title("🚀 StockPro Analysis")
    if st.button("Start New Analysis"): move_to(2)

elif st.session_state.step == 2:
    st.title("💰 Capital Management")
    st.session_state.total_inv = st.number_input("Capital", value=100000)
    if st.button("Next →"): move_to(3)

elif st.session_state.step == 3:
    st.title("📝 Trade Setup")
    st.session_state.stock = st.text_input("Stock", "RELIANCE").upper()
    st.session_state.entry_price = st.number_input("Entry", value=2500.0)
    st.session_state.trade_date = st.date_input("Date", datetime.now())
    st.session_state.stop_loss_orig = st.number_input("SL", value=2450.0)
    c1 = st.checkbox("Nifty 50 Trend")
    c2 = st.checkbox("Sensex Trend")
    c3 = st.checkbox("Industry Trend")
    c4 = st.checkbox("Stock Trend")
    st.session_state.checks = all([c1, c2, c3, c4])
    if st.button("Analyze ⚡"): move_to(4)

elif st.session_state.step == 4:
    st.title("🔍 Analyzing...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    move_to(5)

# --- SCREEN 5: FINAL OUTPUT (FIXED INDENTATION) ---
elif st.session_state.step == 5:
    st.title("📊 Analysis Results")
    
    gap = st.session_state.entry_price - st.session_state.stop_loss_orig
    risk = 0.01 * st.session_state.total_inv
    shares = round(risk / gap) if gap > 0 else 0
    target = st.session_state.entry_price + (2 * gap)
    half_s = shares / 2
    sl1 = (( (target-st.session_state.entry_price)*half_s + 50 + (0.0001*((shares*st.session_state.entry_price)+(half_s*target))) ) / half_s) + st.session_state.stop_loss_orig if half_s > 0 else 0
    invested = shares * st.session_state.entry_price

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Quantity", shares)
    col2.metric("Investment", f"₹{invested:,.2f}")
    col3.metric("Target", f"₹{target:,.2f}")
    col4.metric("SL1", f"₹{sl1:,.2f}")

    # EVERYTHING BELOW IS NOW INSIDE THE BUTTON
    if st.button("Save Entry & View Journal →"):
        # 1. Capture Identity
        user_email = st.user.email if st.user else "Local Test User"

        # 2. Prepare Data
        new_entry = {
            "Email": user_email,
            "Date": st.session_state.trade_date.strftime("%Y-%m-%d"),
            "Total_Capital": st.session_state.total_inv,
            "Stock": st.session_state.stock,
            "Entry Price": st.session_state.entry_price,
            "SL_Original": st.session_state.stop_loss_orig,
            "Target_50": target,
            "Trailing_SL1": sl1,
            "No. of Shares": int(shares),
            "Investment_Value": invested,
            "Nifty 50 Trend": "UP" if st.session_state.get('c1', True) else "DOWN",
            "Sensex Trend": "UP" if st.session_state.get('c2', True) else "DOWN",
            "Industry Trend": "UP" if st.session_state.get('c3', True) else "DOWN",
            "Stock Trend": "UP" if st.session_state.get('c4', True) else "DOWN"
        }

        # 3. PUSH TO GOOGLE SHEETS
        try:
            # We fetch existing data to maintain the sheet structure
            existing_data = conn.read(worksheet="Sheet1")
            updated_df = pd.concat([existing_data, pd.DataFrame([new_entry])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            # 4. Save locally and move
            st.session_state.journal = pd.concat([st.session_state.journal, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Saved to Cloud!")
            time.sleep(1)
            move_to(6)
        except Exception as e:
            st.error(f"Error: {e}")

elif st.session_state.step == 6:
    st.title("📁 Trade Vault")
    st.dataframe(st.session_state.journal)
    if st.button("New Trade"): move_to(2)