import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet
import plotly.express as px

def show():
    st.title("🏠 Dashboard")

    if st.button("🔙 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"

    # --- Load Data ---
    bank_df = pd.DataFrame(get_worksheet(SHEET_URL, "bank_transactions").get_all_records())
    credit_df = pd.DataFrame(get_worksheet(SHEET_URL, "credit_card").get_all_records())
    budget_df = pd.DataFrame(get_worksheet(SHEET_URL, "budget").get_all_records())

    # --- Clean ---
    bank_df["txn_timestamp"] = pd.to_datetime(bank_df["txn_timestamp"], errors="coerce")
    bank_df["amount"] = pd.to_numeric(bank_df["amount"], errors="coerce")
    bank_df["current_balance"] = pd.to_numeric(bank_df["current_balance"], errors="coerce")

    credit_df["txn_timestamp"] = pd.to_datetime(credit_df["txn_timestamp"], errors="coerce")
    credit_df["amount"] = pd.to_numeric(credit_df["amount"], errors="coerce")
    credit_df["type"] = credit_df["type"].str.upper()

    budget_df["budgeted"] = pd.to_numeric(budget_df["budgeted"], errors="coerce")
    budget_df["month_year"] = pd.to_datetime(budget_df["month_year"], errors="coerce").dt.to_period("M")

    # --- KPI Cards ---
    latest_balances = bank_df.dropna(subset=["current_balance"]).groupby("account_number")["current_balance"].last()
    net_worth = latest_balances.sum()

    debits = bank_df[bank_df["type"].str.upper() == "DEBIT"]
    debits["month"] = debits["txn_timestamp"].dt.to_period("M")
    avg_monthly_expense = debits.groupby("month")["amount"].sum().mean()

    latest_balance = bank_df["current_balance"].dropna().iloc[-1] if not bank_df["current_balance"].dropna().empty else 0
    cc_expense_total = credit_df[credit_df["type"] == "DEBIT"]["amount"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Net Worth", f"₹{net_worth:,.2f}")
    col2.metric("📉 Avg Monthly Expenses", f"₹{avg_monthly_expense:,.0f}")
    col3.metric("🏦 Current Bank Balance", f"₹{latest_balance:,.2f}")
    col4.metric("💳 Credit Card Expenses", f"₹{cc_expense_total:,.0f}")

    # --- Analysis Filters ---
    st.markdown("## 📊 Budget vs Actual Analysis")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_person = st.selectbox("Select Person", ["All", "Divyaraj", "Nithya"])

    with filter_col2:
        selected_month = st.selectbox(
            "Select Month",
            sorted(budget_df["month_year"].astype(str).unique())[::-1]
        )

    # --- Filter Data ---
    filtered_budget = budget_df.copy()
    if selected_person != "All":
        filtered_budget = filtered_budget[filtered_budget["person"] == selected_person]
    filtered_budget = filtered_budget[filtered_budget["month_year"].astype(str) == selected_month]

    actual_df = pd.concat([bank_df[["txn_timestamp", "amount", "category"]],
                           credit_df[["txn_timestamp", "amount", "category"]]], ignore_index=True)

    actual_df["txn_timestamp"] = pd.to_datetime(actual_df["txn_timestamp"])
    actual_df["month_year"] = actual_df["txn_timestamp"].dt.to_period("M").astype(str)
    actual_df = actual_df[actual_df["month_year"] == selected_month]

    # --- Summary Table ---
    spent_per_cat = actual_df.groupby("category")["amount"].sum().reset_index()
    budget_per_cat = filtered_budget.groupby("category")["budgeted"].sum().reset_index()

    merged = pd.merge(budget_per_cat, spent_per_cat, on="category", how="outer").fillna(0)
    merged.columns = ["Category", "Budgeted", "Spent"]
    merged["% Used"] = (merged["Spent"] / merged["Budgeted"] * 100).round(1)
    merged["% Used"] = merged["% Used"].replace([float("inf"), -float("inf")], 0)

    st.dataframe(merged, use_container_width=True)

    # --- Pie Chart ---
    pie = px.pie(spent_per_cat, names="category", values="amount", title="Category-wise Spending Breakdown")
    st.plotly_chart(pie, use_container_width=True)

    # --- Monthly Trend ---
    trend_data = actual_df.copy()
    trend_data["month"] = trend_data["txn_timestamp"].dt.to_period("M").astype(str)
    trend_chart = trend_data.groupby("month")["amount"].sum().reset_index()

    line = px.line(trend_chart, x="month", y="amount", title="📈 Monthly Spending Trend")
    st.plotly_chart(line, use_container_width=True)
