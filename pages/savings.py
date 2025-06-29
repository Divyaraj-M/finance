import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet, update_worksheet_rows

# Load Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Sheet Config ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BANK_SHEET = "bank_transactions"
SAVINGS_SHEET = "savings"

# --- Savings Allocation Categories ---
GOAL_OPTIONS = [
    "Wedding Plan",
    "Gold Plan",
    "IITM Course",
    "CFA",
    "General Savings",
    "Emergency Fund"
]

def show():
    # Header with back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔙 Back to Home", help="Return to main dashboard"):
            st.session_state.page = "home"
            st.experimental_rerun()
    
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h1 style="margin-bottom: 0.5rem;">💰 Savings Categorization</h1>
            <p style="color: #666; margin-bottom: 0;">Allocate your savings transactions to specific goals</p>
        </div>
        """, unsafe_allow_html=True)

    try:
        # --- Load and clean bank transactions ---
        bank_ws = get_worksheet(SHEET_URL, BANK_SHEET)
        bank_df = pd.DataFrame(bank_ws.get_all_records())

        bank_df["txn_timestamp"] = pd.to_datetime(bank_df["txn_timestamp"], utc=True, errors="coerce").dt.tz_localize(None)
        bank_df["amount"] = pd.to_numeric(bank_df["amount"], errors="coerce")
        bank_df = bank_df[bank_df["my_category"].str.lower() == "savings"]

        # --- Load existing savings records ---
        savings_ws = get_worksheet(SHEET_URL, SAVINGS_SHEET)
        savings_df = pd.DataFrame(savings_ws.get_all_records())

        if not savings_df.empty:
            savings_df["txn_timestamp"] = pd.to_datetime(savings_df["txn_timestamp"], utc=True, errors="coerce").dt.tz_localize(None)
            savings_df["amount"] = pd.to_numeric(savings_df["amount"], errors="coerce")

        # --- KPI Cards ---
        st.markdown("### 📌 Key Metrics")
        total_saved = savings_df["amount"].sum() if not savings_df.empty else 0
        monthly_avg = savings_df.set_index("txn_timestamp").resample("M")["amount"].sum().mean() if not savings_df.empty else 0

        kpi1, kpi2 = st.columns(2)
        with kpi1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Savings</div>
                <div class='metric-value'>₹{total_saved:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Avg Monthly Savings</div>
                <div class='metric-value'>₹{monthly_avg:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        # --- Filter out already categorized transactions ---
        uncategorized_df = bank_df.copy()
        if not savings_df.empty:
            merged = pd.merge(
                bank_df,
                savings_df[["txn_timestamp", "amount"]],
                on=["txn_timestamp", "amount"],
                how="left",
                indicator=True
            )
            uncategorized_df = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])

        st.markdown("### 📝 Uncategorized Savings Transactions")
        st.markdown("Allocate each transaction to a specific goal below:")

        if uncategorized_df.empty:
            st.success("🎉 All savings transactions have been categorized.")
        else:
            for index, row in uncategorized_df.iterrows():
                with st.expander(f"{row['my_category']} - ₹{row['amount']:,.0f} on {row['txn_timestamp'].strftime('%d-%b-%Y')}"):
                    goal = st.selectbox("Allocate to", GOAL_OPTIONS, key=f"goal_{index}")
                    if st.button("✅ Save Allocation", key=f"save_{index}"):
                        new_entry = {
                            "txn_timestamp": row["txn_timestamp"].strftime("%Y-%m-%dT%H:%M:%S"),
                            "description": row["my_category"],
                            "amount": row["amount"],
                            "allocated_to": goal
                        }
                        update_worksheet_rows(SHEET_URL, SAVINGS_SHEET, [new_entry])
                        st.success("✅ Saved!")
                        st.experimental_rerun()

        # --- Summary Table ---
        st.markdown("### 📊 Summary of Categorized Savings")
        savings_df = pd.DataFrame(savings_ws.get_all_records())
        if not savings_df.empty:
            savings_df["amount"] = pd.to_numeric(savings_df["amount"], errors="coerce")
            summary = savings_df.groupby("allocated_to")["amount"].sum().reset_index()
            summary.columns = ["Goal", "Total Saved"]
            summary.index += 1  # Start index from 1
            st.dataframe(summary, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error loading data: {e}") 