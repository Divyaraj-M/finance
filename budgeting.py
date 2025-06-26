import streamlit as st
import pandas as pd
from datetime import datetime
from utils.gsheet import get_worksheet

# --- Constants ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BUDGET_SHEET = "budget"
INCOME_SHEET = "income"

PEOPLE = ["Divyaraj", "Nithya"]
EXPENSE_CATEGORIES = [
    "Rent", "Food", "Transport - Internal", "Transport - External",
    "Home Expenses", "EMI", "Personal Care", "Savings",
    "Shopping", "Leisure","Subscritions"
]
INCOME_CATEGORIES = ["Freelancing", "Salary"]

# --- Load previous month's values ---
def load_previous_data(sheet_name, key_col):
    ws = get_worksheet(SHEET_URL, sheet_name)
    df = pd.DataFrame(ws.get_all_records())
    if df.empty:
        return {}
    df["month_year"] = pd.to_datetime(df["month_year"], errors="coerce").dt.strftime("%Y-%m")
    last_month = df["month_year"].max()
    filtered = df[df["month_year"] == last_month]
    preload = {}
    for _, row in filtered.iterrows():
        person = row["person"]
        category = row["category"]
        amount = row[key_col]
        if person not in preload:
            preload[person] = {}
        preload[person][category] = amount
    return preload

# --- MAIN ---
def show():
    st.title("📝 Monthly Budget Planner")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.subheader("📅 Select Month")
    selected_month = st.date_input("Choose a date in the month", datetime.today())
    month_year = selected_month.strftime("%Y-%m")

    # Load previous data
    preload_income = load_previous_data(INCOME_SHEET, "income")
    preload_budget = load_previous_data(BUDGET_SHEET, "budgeted")

    # --- Income Input Section ---
    st.markdown("## 💰 Expected Income")
    income_inputs = []
    total_income = {}

    col1, col2 = st.columns(2)

    for person, col in zip(PEOPLE, [col1, col2]):
        with col:
            st.subheader(f"👤 {person}")
            person_total = 0
            cols = st.columns(2)
            for i, cat in enumerate(INCOME_CATEGORIES):
                default = preload_income.get(person, {}).get(cat, 0)
                with cols[i % 2]:
                    val = st.number_input(
                        f"{cat} Income ({person})",
                        min_value=0,
                        step=500,
                        value=default,
                        key=f"{person}_income_{cat}"
                    )
                    income_inputs.append({
                        "month_year": month_year,
                        "person": person,
                        "category": cat,
                        "income": val
                    })
                    person_total += val
            total_income[person] = person_total
            st.metric("💼 Total Income", f"₹{person_total:,.0f}")

    if st.button("📤 Submit Income Data"):
        income_ws = get_worksheet(SHEET_URL, INCOME_SHEET)
        df_income = pd.DataFrame(income_inputs)
        for row in df_income.values.tolist():
            income_ws.append_row(row, value_input_option="USER_ENTERED")
        st.success("✅ Income submitted.")
        st.dataframe(df_income)

    st.markdown("---")

    # --- Budget Input Section ---
    st.markdown("## 💸 Budget Allocations")

    col_left, col_right = st.columns(2)
    budget_inputs = []
    over_budget_flags = {}

    for person, col in zip(PEOPLE, [col_left, col_right]):
        with col:
            st.subheader(f"👤 {person}")
            total_budget = 0
            for cat in EXPENSE_CATEGORIES:
                default = preload_budget.get(person, {}).get(cat, 0)
                input_val = st.number_input(
                    f"{cat}",
                    min_value=0,
                    step=100,
                    value=default,
                    key=f"{person}_{cat}"
                )
                percent = (input_val / total_income.get(person, 1)) * 100 if total_income.get(person, 0) else 0
                st.markdown(
                    f"<span style='color:{'red' if percent > 100 else 'green'}'>({percent:.1f}%)</span>",
                    unsafe_allow_html=True
                )
                total_budget += input_val
                budget_inputs.append({
                    "month_year": month_year,
                    "person": person,
                    "category": cat,
                    "budgeted": input_val
                })

            remaining = total_income.get(person, 0) - total_budget
            st.metric("📊 Total Budgeted", f"₹{total_budget:,.0f}")
            st.metric("💵 Remaining Budget", f"₹{remaining:,.0f}", delta_color="inverse")
            over_budget_flags[person] = total_budget > total_income.get(person, 0)

    if st.button("📤 Submit Budget Data"):
        budget_ws = get_worksheet(SHEET_URL, BUDGET_SHEET)
        df_budget = pd.DataFrame(budget_inputs)
        for row in df_budget.values.tolist():
            budget_ws.append_row(row, value_input_option="USER_ENTERED")
        st.success("✅ Budget submitted.")
        st.dataframe(df_budget)

    for person, flag in over_budget_flags.items():
        if flag:
            st.error(f"🚨 {person} has exceeded their income allocation for this month!")
