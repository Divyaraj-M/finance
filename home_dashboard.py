import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
            <h1 style="margin-bottom: 0.5rem;">📊 Financial Dashboard</h1>
            <p style="color: #666; margin-bottom: 0;">Comprehensive overview of your financial health</p>
        </div>
        """, unsafe_allow_html=True)

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"

    # --- Load Data ---
    def safe_get_df(sheet_name):
        try:
            ws = get_worksheet(SHEET_URL, sheet_name)
            df = pd.DataFrame(ws.get_all_records())
            if df.empty:
                st.warning(f"⚠️ No data found in `{sheet_name}` sheet.")
            return df
        except Exception as e:
            st.error(f"❌ Failed to load `{sheet_name}`: {e}")
            return pd.DataFrame()

    bank_df = safe_get_df("bank_transactions")
    credit_df = safe_get_df("credit_card")
    budget_df = safe_get_df("budget")

    # --- Validation ---
    if "txn_timestamp" not in bank_df.columns or "txn_timestamp" not in credit_df.columns:
        st.error("Missing `txn_timestamp` in bank or credit sheet. Please ensure correct headers.")
        return

    # --- Clean & Transform ---
    bank_df["txn_timestamp"] = pd.to_datetime(bank_df["txn_timestamp"], errors="coerce")
    bank_df["amount"] = pd.to_numeric(bank_df["amount"], errors="coerce")
    bank_df["current_balance"] = pd.to_numeric(bank_df["current_balance"], errors="coerce")

    credit_df["txn_timestamp"] = pd.to_datetime(credit_df["txn_timestamp"], errors="coerce")
    credit_df["amount"] = pd.to_numeric(credit_df["amount"], errors="coerce")
    credit_df["type"] = credit_df["type"].str.upper()

    budget_df["budgeted"] = pd.to_numeric(budget_df["budgeted"], errors="coerce")
    budget_df["month_year"] = pd.to_datetime(budget_df["month_year"], errors="coerce").dt.to_period("M")

    # --- KPI Cards ---
    if not bank_df.empty and "current_balance" in bank_df.columns:
        latest_balances = bank_df.dropna(subset=["current_balance"]).groupby("account_number")["current_balance"].last()
        net_worth = latest_balances.sum()
        latest_balance = bank_df["current_balance"].dropna().iloc[-1] if not bank_df["current_balance"].dropna().empty else 0
    else:
        net_worth, latest_balance = 0, 0

    debits = bank_df[bank_df["type"].str.upper() == "DEBIT"] if not bank_df.empty else pd.DataFrame()
    if not debits.empty:
        debits["month"] = debits["txn_timestamp"].dt.to_period("M")
        avg_monthly_expense = debits.groupby("month")["amount"].sum().mean()
    else:
        avg_monthly_expense = 0

    cc_expense_total = credit_df[credit_df["type"] == "DEBIT"]["amount"].sum() if not credit_df.empty else 0

    # Enhanced KPI Cards
    st.markdown("### 📈 Key Financial Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Net Worth</div>
            <div class="metric-value">₹{net_worth:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📉 Avg Monthly Expenses</div>
            <div class="metric-value">₹{avg_monthly_expense:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏦 Current Bank Balance</div>
            <div class="metric-value">₹{latest_balance:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💳 Credit Card Expenses</div>
            <div class="metric-value">₹{cc_expense_total:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Filters Section ---
    st.markdown("### 📊 Budget vs Actual Analysis")
    
    filter_col1, filter_col2 = st.columns(2)
    selected_person = filter_col1.selectbox("👤 Select Person", ["All", "Divyaraj", "Nithya"])
    
    if budget_df.empty or "month_year" not in budget_df.columns:
        st.warning("⏳ No budget data available.")
        return
    
    selected_month = filter_col2.selectbox(
        "📅 Select Month",
        sorted(budget_df["month_year"].astype(str).unique())[::-1]
    )

    # --- Budget vs Actual Table ---
    filtered_budget = budget_df.copy()
    if selected_person != "All":
        filtered_budget = filtered_budget[filtered_budget["person"] == selected_person]
    filtered_budget = filtered_budget[filtered_budget["month_year"].astype(str) == selected_month]

    # Filter bank transactions for selected person, month, and DEBIT type
    filtered_bank = bank_df.copy()
    if selected_person != "All":
        filtered_bank = filtered_bank[filtered_bank["person"] == selected_person]
    filtered_bank = filtered_bank[(filtered_bank["txn_timestamp"].dt.to_period("M").astype(str) == selected_month) & (filtered_bank["type"].str.upper() == "DEBIT")]

    # Group by my_category and sum amount
    actuals_per_cat = filtered_bank.groupby("my_category")["amount"].sum().reset_index()
    actuals_per_cat.columns = ["Category", "Spent"]

    # Group budget by category
    budget_per_cat = filtered_budget.groupby("category")["budgeted"].sum().reset_index()
    budget_per_cat.columns = ["Category", "Budgeted"]

    # Merge on Category
    merged = pd.merge(budget_per_cat, actuals_per_cat, on="Category", how="outer").fillna(0)
    merged["% Used"] = (merged["Spent"] / merged["Budgeted"] * 100).round(2)
    merged["% Used"] = merged["% Used"].replace([float("inf"), -float("inf")], 0)

    # Format columns to two decimal places
    merged["Budgeted"] = merged["Budgeted"].map(lambda x: f"{x:,.2f}")
    merged["Spent"] = merged["Spent"].map(lambda x: f"{x:,.2f}")
    merged["% Used"] = merged["% Used"].map(lambda x: f"{x:.2f}")

    st.markdown("#### 📋 Budget vs Actual Comparison")
    st.dataframe(merged, use_container_width=True)

    # --- Charts Section ---
    col1, col2 = st.columns(2)
    
    with col1:
        if not actuals_per_cat.empty:
            # Enhanced Pie Chart
            fig_pie = px.pie(
                actuals_per_cat, 
                names="Category", 
                values="Spent", 
                title="🧁 Category-wise Spending Breakdown",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                title_x=0.5,
                title_font_size=16,
                showlegend=True,
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        if not actuals_per_cat.empty:
            # Enhanced Bar Chart for Top Categories
            top_categories = actuals_per_cat.nlargest(8, 'Spent')
            fig_bar = px.bar(
                top_categories,
                x='Spent',
                y='Category',
                orientation='h',
                title="📊 Top Spending Categories",
                color='Spent',
                color_continuous_scale='viridis'
            )
            fig_bar.update_layout(
                title_x=0.5,
                title_font_size=16,
                height=400,
                xaxis_title="Amount (₹)",
                yaxis_title="Category"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- Monthly Trend Chart ---
    if not actuals_per_cat.empty:
        st.markdown("#### 📈 Monthly Spending Trend")
        trend_data = actuals_per_cat.copy()
        trend_data["month"] = trend_data["Category"].str.split('-').str[1]
        trend_data["year"] = trend_data["Category"].str.split('-').str[0]
        trend_data["month"] = pd.to_datetime(trend_data["month"], format='%m').dt.strftime('%b')
        trend_data["year"] = trend_data["year"].astype(int)
        trend_data["month_year"] = trend_data["year"] + '-' + trend_data["month"]
        trend_data["month_year"] = pd.to_datetime(trend_data["month_year"], format='%Y-%b')
        trend_chart = trend_data.groupby("month_year")["Spent"].sum().reset_index()
        
        fig_line = px.line(
            trend_chart, 
            x="month_year", 
            y="Spent", 
            title="📈 Monthly Spending Trend",
            markers=True
        )
        fig_line.update_layout(
            title_x=0.5,
            title_font_size=16,
            height=400,
            xaxis_title="Month",
            yaxis_title="Total Amount (₹)"
        )
        fig_line.update_traces(line_color='#667eea', marker_color='#667eea')
        st.plotly_chart(fig_line, use_container_width=True)

    # --- Summary Cards ---
    if not merged.empty:
        st.markdown("#### 📊 Budget Summary")
        # Convert columns back to float for calculations
        total_budgeted = merged["Budgeted"].replace(',', '', regex=True).astype(float).sum()
        total_spent = merged["Spent"].replace(',', '', regex=True).astype(float).sum()
        overall_usage = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📋 Total Budgeted</div>
                <div class="metric-value">₹{total_budgeted:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💸 Total Spent</div>
                <div class="metric-value">₹{total_spent:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            usage_color = "#e74c3c" if overall_usage > 100 else "#27ae60" if overall_usage <= 80 else "#f39c12"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📊 Budget Usage</div>
                <div class="metric-value" style="color: {usage_color};">{overall_usage:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
