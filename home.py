import streamlit as st
import pandas as pd
from budgeting import show as show_budgeting
from import_ import show as show_import
from home_dashboard import show as show_dashboard
from data import show as show_data
from utils.gsheet import get_worksheet

# --- App Configuration ---
st.set_page_config(
    page_title="CoFi | Personal Finance Tracker", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Load Custom CSS ---
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Session State Setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()

# --- Top Bar with Enhanced Branding ---
st.markdown("""
<div class="top-bar">
    <div class="app-title">💰 CoFi</div>
    <div style="margin-left: auto; font-size: 0.9rem; color: #bdc3c7;">
        Personal Finance Tracker
    </div>
</div>
""", unsafe_allow_html=True)

# --- Enhanced Navigation ---
st.markdown("""
<div style="margin-bottom: 2rem;">
    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Dashboard", key="dash", help="View your financial overview and analytics"):
        navigate_to("dashboard")
with col2:
    if st.button("📝 Budgeting", key="budget", help="Plan and manage your monthly budget"):
        navigate_to("budgeting")
with col3:
    if st.button("📥 Import", key="import", help="Upload bank and credit card statements"):
        navigate_to("import")
with col4:
    if st.button("📊 Data", key="data", help="Categorize and manage transaction data"):
        navigate_to("data")
with col5:
    if st.button("💰 Savings", key="savings", help="Categorize and track your savings goals"):
        navigate_to("savings")

st.markdown("</div></div>", unsafe_allow_html=True)

# --- Page Renderer ---
if st.session_state.page == "home":
    # Welcome Section
    st.markdown("""
    <div class="custom-card">
        <h1 style="margin-bottom: 0.5rem;">👋 Welcome, Divyaraj & Nithya</h1>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 0;">
            Your financial cockpit is ready. Choose a section to begin tracking your finances.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats Section
    st.markdown("### 📊 Quick Overview")
    
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
    try:
        bank_df = pd.DataFrame(get_worksheet(SHEET_URL, "bank_transactions").get_all_records())
        credit_df = pd.DataFrame(get_worksheet(SHEET_URL, "credit_card").get_all_records())

        if not bank_df.empty:
            bank_df["txn_timestamp"] = pd.to_datetime(bank_df["txn_timestamp"], errors="coerce")
            bank_df["amount"] = pd.to_numeric(bank_df["amount"], errors="coerce")
            latest_balance = bank_df["current_balance"].dropna().iloc[-1] if "current_balance" in bank_df.columns else 0
            monthly_expenses = bank_df[
                (bank_df["type"].str.upper() == "DEBIT") & 
                (bank_df["txn_timestamp"].dt.month == pd.Timestamp.now().month)
            ]["amount"].sum()
        else:
            latest_balance = 0
            monthly_expenses = 0

        if not credit_df.empty:
            credit_df["amount"] = pd.to_numeric(credit_df["amount"], errors="coerce")
            credit_expenses = credit_df[credit_df["type"] == "DEBIT"]["amount"].sum()
        else:
            credit_expenses = 0

        # Quick Stats Cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🏦 Current Balance</div>
                <div class="metric-value">₹{latest_balance:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💸 This Month's Expenses</div>
                <div class="metric-value">₹{monthly_expenses:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💳 Credit Card Expenses</div>
                <div class="metric-value">₹{credit_expenses:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"Could not load financial data: {e}")

    # Recent Transactions Section
    st.markdown("### 🧾 Recent Transactions")
    
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

        if not recent_txns.empty:
            for _, row in recent_txns.iterrows():
                amount = float(row.get("amount", 0))
                amount_color = "#e74c3c" if amount < 0 else "#27ae60"
                
                st.markdown(
                    f"""
                    <div class="txn-row">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="font-size: 1.1rem;">{row.get("description", "Unnamed Transaction")}</strong>
                                <span class="txn-tag">{row.get("category", "Uncategorized")}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-weight: bold; font-size: 1.2rem; color: {amount_color};">
                                    ₹{abs(amount):,.2f}
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem; color: #666; font-size: 0.9rem;">
                            🗓 {row["txn_timestamp"].strftime('%b %d, %Y')} &nbsp;&nbsp;&nbsp;&nbsp; {row['source']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No recent transactions found. Import some data to get started!")
            
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
elif st.session_state.page == "savings":
    from pages.savings import show as show_savings
    show_savings()
