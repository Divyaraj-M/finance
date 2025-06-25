import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet

SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BANK_SHEET = "bank_transactions"
CC_SHEET = "credit_card"

def show():
    st.title("📥 Import Transactions")

    # --- Home Button ---
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    # ===========================
    # 📁 1. Upload Bank Statement
    # ===========================
    st.header("🏦 Upload Bank Statement CSV")

    bank_file = st.file_uploader("Upload your bank transaction CSV", type=["csv"], key="bank")

    if bank_file:
        df = pd.read_csv(bank_file)

        required_cols = [
            'account_number', 'txn_timestamp', 'amount', 'current_balance', 'type',
            'reference', 'merchant', 'category_icon_name', 'category', 'bank_name', 'notes'
        ]
        if not all(col in df.columns for col in required_cols):
            st.error("❌ CSV columns do not match the required bank schema.")
        else:
            worksheet = get_worksheet(SHEET_URL, BANK_SHEET)
            data_to_append = df.iloc[1:].values.tolist()
            for row in data_to_append:
                worksheet.append_row(row, value_input_option="USER_ENTERED")
            st.success(f"✅ Appended {len(data_to_append)} rows to '{BANK_SHEET}'.")

    # =================================
    # 💳 2. Upload Credit Card Statement
    # =================================
    st.header("💳 Upload Credit Card Statement CSV")

    cc_file = st.file_uploader("Upload your credit card CSV", type=["csv"], key="credit_card")

    if cc_file:
        df = pd.read_csv(cc_file)

        required_cols = [
            'card_number', 'card_name', 'txn_timestamp', 'amount', 'type',
            'merchant', 'category_icon_name', 'category', 'notes'
        ]
        if not all(col in df.columns for col in required_cols):
            st.error("❌ CSV columns do not match the required credit card schema.")
        else:
            worksheet = get_worksheet(SHEET_URL, CC_SHEET)
            data_to_append = df.iloc[1:].values.tolist()
            for row in data_to_append:
                worksheet.append_row(row, value_input_option="USER_ENTERED")
            st.success(f"✅ Appended {len(data_to_append)} rows to '{CC_SHEET}'.")
