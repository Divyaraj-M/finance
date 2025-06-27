import streamlit as st
import pandas as pd
from budgeting import show as show_budgeting
from import_ import show as show_import
from home_dashboard import show as show_dashboard
from data import show as show_data
from utils.gsheet import get_worksheet

# --- App Configuration ---
st.set_page_config(page_title="CoFi | Personal Finance Tracker", layout="wide")

# --- Session State Setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()

# --- Custom CSS ---
st.markdown("""
    <style>
        .top-bar {
            background-color: #1C1C1C;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .app-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #FFEDA8;
        }
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        .stButton > button {
            background-color: #333 !important;
            color: #FFEDA8 !important;
            border: none;
            padding: 0.5rem 1.2rem;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 0.4rem;
        }
        .stButton > button:hover {
            background-color: #444 !important;
        }
        .txn-tag {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            background-color: #FFEDA8;
            color: #333;
            font-size: 0.75rem;
            font-weight: bold;
            border-radius: 0.3rem;
            margin-left: 0.5rem;
        }
        .txn-row {
            padding: 0.6rem 0;
            border-bottom: 1px solid #333;
        }
    </style>
""", unsafe_allow_html=True)

# --- Top Bar with Navigation ---
st.markdown("""
<div class="top-bar">
    <div class="app-title">CoFi</div>
    <div class="nav-buttons">
        <form action="#" onsubmit="return false;">
            <button onclick="window.location.reload();" class="nav-btn">🏠 Dashboard</button>
        </form>
        <form action="#" onsubmit="return false;">
            <button onclick="window.location.reload();" class="nav-btn">📝 Budgeting</button>
        </form>
        <form action="#" onsubmit="return false;">
            <button onclick="window.location.reload();" class="nav-btn">📥 Import</button>
        </form>
        <form action="#" onsubmit="return false;">
            <button onclick="window.location.reload();" class="nav-btn">📊 Data</button>
        </form>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Navigation with Streamlit Buttons ---
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("🏠 Dashboard", key="dash"):
        navigate_to("dashboard")
with nav_col2:
    if st.button("📝 Budgeting", key="budget"):
        navigate_to("budgeting")
with nav_col3:
    if st.button("📥 Import", key="import"):
        navigate_to("import")
with nav_col4:
    if st.button("📊 Data", key="data"):
        navigate_to("data")

# --- Page Renderer ---
if st.session_state.page == "home":
    st.title("👋 Welcome, Divyaraj & Nithya")
    st.markdown("Your financial cockpit is ready. Choose a section to begin tracking.")

    # --- Show Last 7 Transactions (Bank + Credit) ---
    st.markdown("### 🧾 Recent Transactions")

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
    try:
        bank_df = pd.DataFrame(get_worksheet(SHEET_URL, "bank_transactions").get_all_records())
        credit_df = pd.DataFrame(get_worksheet(SHEET_URL, "credit_card").get_all_records())

        bank_df["txn_timestamp"] = pd.to_datetime(bank_df["txn_timestamp"], errors="coerce")
        credit_df["txn_timestamp"] = pd.to_datetime(credit_df["txn_timestamp"], errors="coerce")

        bank_df["source"] = "🏦 Bank"
        credit_df["source"] = "💳 Credit"

        combined_df = pd.concat([bank_df, credit_df], ignore_index=True)
        combined_df = combined_df.sort_values(by="txn_timestamp", ascending=False).dropna(subset=["txn_timestamp"])
        recent_txns = combined_df.head(7)

        for _, row in recent_txns.iterrows():
            st.markdown(
                f"""
                <div class="txn-row">
                    <strong>{row.get("description", "Unnamed Transaction")}</strong>  
                    <span class="txn-tag">{row.get("category", "Uncategorized")}</span><br/>
                    <span style='font-size:0.85rem;'>🗓 {row["txn_timestamp"].strftime('%b %d, %Y')} &nbsp;&nbsp;&nbsp;&nbsp; {row['source']}</span><br/>
                    <span style='font-weight:bold; color:#FFEDA8;'>₹{float(row.get("amount", 0)):,.2f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        st.error(f"Could not load recent transactions: {e}")

elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "budgeting":
    show_budgeting()
elif st.session_state.page == "import":
    show_import()
elif st.session_state.page == "data":
    show_data()
