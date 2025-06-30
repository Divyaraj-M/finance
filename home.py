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
        @st.cache_data(ttl=60)
        def get_sheet_data(sheet_url, worksheet_name):
            ws = get_worksheet(sheet_url, worksheet_name)
            return ws.get_all_records()

        bank_df = pd.DataFrame(get_sheet_data(SHEET_URL, "bank_transactions"))
        credit_df = pd.DataFrame(get_sheet_data(SHEET_URL, "credit_card"))

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
        bank_df = pd.DataFrame(get_sheet_data(SHEET_URL, "bank_transactions"))
        credit_df = pd.DataFrame(get_sheet_data(SHEET_URL, "credit_card"))

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

    # --- 3-Year Savings Plan Tracker ---
    st.markdown("### 🎯 3-Year Savings Plan")
    try:
        savings_df = pd.DataFrame(get_sheet_data(SHEET_URL, "savings"))
        savings_df["amount"] = pd.to_numeric(savings_df["amount"], errors="coerce")

        savings_goals = {
            "Wedding Plan": 1000000,
            "Gold Plan": 700000,
            "IITM Course": 350000,
            "CFA": 500000,
            "General Savings": 400000,
            "Emergency Fund": 200000
        }

        summary_df = savings_df.groupby("allocated_to")[["amount"]].sum().reset_index()

        left_col, right_col = st.columns(2)
        for i, (goal, target) in enumerate(savings_goals.items()):
            saved_row = summary_df[summary_df["allocated_to"].str.lower() == goal.lower()]
            saved_amount = saved_row["amount"].values[0] if not saved_row.empty else 0
            progress = saved_amount / target if target else 0

            container = left_col if i % 2 == 0 else right_col
            with container:
                st.markdown(f"**{goal}**")
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: space-between; font-size: 0.9rem;'>
                        <span>Saved: ₹{saved_amount:,.0f}</span>
                        <span>Target: ₹{target:,.0f}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.progress(min(progress, 1.0))
                st.markdown(f"📅 Monthly Goal: ₹{target // 36:,.0f}")
    except Exception as e:
        st.error(f"❌ Could not load savings tracker: {e}")

    # --- Manual Data Entry Button and Form ---
    st.markdown("---")
    with st.expander("➕ Add Transaction (Manual Entry)"):
        entry_type = st.radio("Transaction Type", ["Bank", "Credit Card"], horizontal=True)
        txn_date = st.date_input("Date")
        txn_time = st.time_input("Time")
        amount = st.number_input("Amount", step=1.0, format="%.2f")
        txn_type = st.selectbox("Type", ["DEBIT", "CREDIT"])
        description = st.text_input("Description")
        person = st.selectbox("Person", ["Divyaraj", "Nithya"])
        my_category_options = [
            "Rent",
            "Food",
            "Transport - Internal",
            "Transport - External",
            "Home Expenses",
            "EMI",
            "Personal Care",
            "Savings",
            "Shopping",
            "Leisure",
            "Other"
        ]
        my_category_selected = st.selectbox("My Category (Tag)", my_category_options)
        if my_category_selected == "Other":
            my_category = st.text_input("Custom Category")
        else:
            my_category = my_category_selected
        if entry_type == "Bank":
            account_number = st.text_input("Account Number")
            current_balance = st.number_input("Current Balance", step=1.0, format="%.2f")
            reference = st.text_input("Reference")
            merchant = st.text_input("Merchant")
            category_icon_name = st.text_input("Category Icon Name")
            category = st.text_input("Bank Category (optional)")
            bank_name = st.text_input("Bank Name")
            notes = st.text_area("Notes")
            if st.button("Submit Transaction"):
                import datetime
                dt = datetime.datetime.combine(txn_date, txn_time)
                dt_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                date_str = dt.strftime("%d-%b-%Y")
                time_str = dt.strftime("%H:%M:%S")
                row = [
                    account_number, dt_str, amount, current_balance, txn_type, reference, merchant,
                    category_icon_name, category, bank_name, notes, person, date_str, time_str, my_category
                ]
                ws = get_worksheet(SHEET_URL, "bank_transactions")
                ws.append_row(row, value_input_option="USER_ENTERED")
                st.success("✅ Transaction added successfully!")
        else:
            card_number = st.text_input("Card Number")
            card_name = st.selectbox("Card Name", ["Paytm", "HDFC"])
            merchant = st.text_input("Merchant")
            category_icon_name = st.text_input("Category Icon Name")
            category = st.text_input("CC Category")
            notes = st.text_area("Notes")
            if st.button("Submit Transaction"):
                import datetime
                dt = datetime.datetime.combine(txn_date, txn_time)
                dt_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M:%S")
                row = [
                    card_number, card_name, dt_str, amount, txn_type, merchant,
                    category_icon_name, category, notes, person, date_str, time_str, my_category
                ]
                ws = get_worksheet(SHEET_URL, "credit_card")
                ws.append_row(row, value_input_option="USER_ENTERED")
                st.success("✅ Transaction added successfully!")

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
