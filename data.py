import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet

# === Sheet Config ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
SHEETS = {
    "Bank Transactions": "bank_transactions",
    "Credit Card Transactions": "credit_card"  # Updated name
}

# === Category Options ===
CATEGORY_OPTIONS = [
    "EMI", "Food", "Home Expenses", "Leisure", "Personal Care",
    "Rent", "Savings", "Shopping", "Transport - External",
    "Transport - Internal", "Subscriptions", "Other"
]

# === Load Data ===
def load_data(sheet_name):
    worksheet = get_worksheet(SHEET_URL, sheet_name)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return worksheet, df

# === Update Rows ===
def update_rows(worksheet, df, updated_rows):
    for index, category in updated_rows.items():
        row_number = index + 2  # 1 for 0-index, 1 for header row
        col_index = df.columns.get_loc("my_category") + 1
        worksheet.update_cell(row_number, col_index, category)

# === Render UI for One Sheet ===
def render_sheet_categorizer(label, sheet_key):
    st.subheader(f"🗂️ {label}")

    worksheet, df = load_data(sheet_key)

    if "my_category" not in df.columns:
        df["my_category"] = ""

    df_uncategorized = df[df["my_category"].isna() | (df["my_category"].astype(str).str.strip() == "")]

    if df_uncategorized.empty:
        st.success(f"✅ All {label.lower()} entries are categorized.")
        return

    st.info(f"Found **{len(df_uncategorized)}** uncategorized rows in **{label}**")

    updates = {}

    for idx, row in df_uncategorized.iterrows():
        title = f"{row.get('date', '')} | ₹{row['amount']} | {row.get('merchant', row.get('category', ''))}"
        with st.expander(title):
            st.write(f"**Type:** {row['type']} | **Bank/Card:** {row.get('bank_name', row.get('card_name', 'N/A'))}")
            selected = st.selectbox("Select Category", CATEGORY_OPTIONS, key=f"{sheet_key}_{idx}")
            updates[idx] = selected

    if st.button(f"💾 Save Categories for {label}"):
        update_rows(worksheet, df, updates)
        st.success(f"✅ Updated {len(updates)} rows in **{label}**.")
        st.rerun()

# === Entry Point ===
def show():
    st.title("📋 Categorize Transactions Manually")

    if st.button("🏠 Go Home"):
        st.session_state.page = "home"
        st.rerun()

    for label, key in SHEETS.items():
        render_sheet_categorizer(label, key)
