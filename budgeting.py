import streamlit as st
import pandas as pd
from datetime import datetime
from utils.gsheet import get_worksheet

# Load Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Constants ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BUDGET_SHEET = "budget"
INCOME_SHEET = "income"

PEOPLE = ["Divyaraj", "Nithya"]
EXPENSE_CATEGORIES = [
    "Rent", "Food", "Transport - Internal", "Transport - External",
    "Home Expenses", "EMI", "Personal Care", "Savings",
    "Shopping", "Leisure","Subscriptions"
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
    # Header with back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔙 Back to Home", help="Return to main dashboard"):
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h1 style="margin-bottom: 0.5rem;">📝 Monthly Budget Planner</h1>
            <p style="color: #666; margin-bottom: 0;">Plan and manage your monthly income and expenses</p>
        </div>
        """, unsafe_allow_html=True)

    # Month Selection
    st.markdown("### 📅 Select Month")
    selected_month = st.date_input("Choose a date in the month", datetime.today(), help="Select any date in the month you want to budget for")
    month_year = selected_month.strftime("%Y-%m")

    # Load previous data
    preload_income = load_previous_data(INCOME_SHEET, "income")
    preload_budget = load_previous_data(BUDGET_SHEET, "budgeted")

    # --- Income Input Section ---
    st.markdown("### 💰 Expected Income")
    
    income_inputs = []
    total_income = {}

    col1, col2 = st.columns(2)

    for person, col in zip(PEOPLE, [col1, col2]):
        with col:
            st.markdown(f"""
            <div class="custom-card">
                <h3 style="margin-bottom: 1rem; color: #667eea;">👤 {person}</h3>
            """, unsafe_allow_html=True)
            
            person_total = 0
            cols = st.columns(2)
            for i, cat in enumerate(INCOME_CATEGORIES):
                default = preload_income.get(person, {}).get(cat, 0)
                with cols[i % 2]:
                    val = st.number_input(
                        f"{cat}",
                        min_value=0,
                        step=500,
                        value=default,
                        key=f"{person}_income_{cat}",
                        help=f"Enter {cat.lower()} income for {person}"
                    )
                    income_inputs.append({
                        "month_year": month_year,
                        "person": person,
                        "category": cat,
                        "income": val
                    })
                    person_total += val
            
            st.markdown(f"""
            <div class="metric-card" style="margin-top: 1rem;">
                <div class="metric-label">💼 Total Income</div>
                <div class="metric-value">₹{person_total:,.0f}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            total_income[person] = person_total

    # Submit Income Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📤 Submit Income Data", help="Save income data to the spreadsheet"):
            try:
                income_ws = get_worksheet(SHEET_URL, INCOME_SHEET)
                df_income = pd.DataFrame(income_inputs)
                for row in df_income.values.tolist():
                    income_ws.append_row(row, value_input_option="USER_ENTERED")
                st.success("✅ Income data submitted successfully!")
                
                # Show summary
                with st.expander("📋 Income Summary"):
                    st.dataframe(df_income, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error submitting income data: {e}")

    st.markdown("---")

    # --- Budget Input Section ---
    st.markdown("### 💸 Budget Allocations")

    col_left, col_right = st.columns(2)
    budget_inputs = []
    over_budget_flags = {}

    for person, col in zip(PEOPLE, [col_left, col_right]):
        with col:
            st.markdown(f"""
            <div class="custom-card">
                <h3 style="margin-bottom: 1rem; color: #667eea;">👤 {person}</h3>
            """, unsafe_allow_html=True)
            
            total_budget = 0
            for cat in EXPENSE_CATEGORIES:
                default = preload_budget.get(person, {}).get(cat, 0)
                input_val = st.number_input(
                    f"{cat}",
                    min_value=0,
                    step=100,
                    value=default,
                    key=f"{person}_{cat}",
                    help=f"Enter budget for {cat.lower()} for {person}"
                )
                
                # Calculate percentage
                percent = (input_val / total_income.get(person, 1)) * 100 if total_income.get(person, 0) else 0
                percent_color = "#e74c3c" if percent > 100 else "#27ae60" if percent <= 80 else "#f39c12"
                
                st.markdown(
                    f"<span style='color: {percent_color}; font-size: 0.9rem;'>({percent:.1f}% of income)</span>",
                    unsafe_allow_html=True
                )
                
                total_budget += input_val
                budget_inputs.append({
                    "month_year": month_year,
                    "person": person,
                    "category": cat,
                    "budgeted": input_val
                })

            # Budget Summary Cards
            remaining = total_income.get(person, 0) - total_budget
            remaining_color = "#e74c3c" if remaining < 0 else "#27ae60"
            
            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div class="metric-card">
                    <div class="metric-label">📊 Total Budgeted</div>
                    <div class="metric-value">₹{total_budget:,.0f}</div>
                </div>
                <div class="metric-card" style="margin-top: 0.5rem;">
                    <div class="metric-label">💵 Remaining Budget</div>
                    <div class="metric-value" style="color: {remaining_color};">₹{remaining:,.0f}</div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            over_budget_flags[person] = total_budget > total_income.get(person, 0)

    # Submit Budget Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📤 Submit Budget Data", help="Save budget data to the spreadsheet"):
            try:
                budget_ws = get_worksheet(SHEET_URL, BUDGET_SHEET)
                df_budget = pd.DataFrame(budget_inputs)
                for row in df_budget.values.tolist():
                    budget_ws.append_row(row, value_input_option="USER_ENTERED")
                st.success("✅ Budget data submitted successfully!")
                
                # Show summary
                with st.expander("📋 Budget Summary"):
                    st.dataframe(df_budget, use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error submitting budget data: {e}")

    # Warning Messages
    for person, flag in over_budget_flags.items():
        if flag:
            st.markdown(f"""
            <div class="custom-card" style="border-left: 4px solid #e74c3c; background: rgba(231, 76, 60, 0.1);">
                <h4 style="color: #e74c3c; margin-bottom: 0.5rem;">🚨 Budget Warning</h4>
                <p style="margin-bottom: 0; color: #c0392b;">
                    {person} has exceeded their income allocation for this month! 
                    Consider adjusting your budget categories.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Budget Tips
    st.markdown("### 💡 Budgeting Tips")
    st.markdown("""
    <div class="custom-card">
        <ul style="margin-bottom: 0;">
            <li><strong>50/30/20 Rule:</strong> 50% for needs, 30% for wants, 20% for savings</li>
            <li><strong>Emergency Fund:</strong> Aim to save 3-6 months of expenses</li>
            <li><strong>Track Regularly:</strong> Review your budget weekly to stay on track</li>
            <li><strong>Be Realistic:</strong> Set achievable goals based on your actual spending patterns</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
