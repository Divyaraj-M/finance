import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet

# === Constants ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BANK_SHEET = "bank_transactions"
CC_SHEET = "credit_card"
PEOPLE = ["Divyaraj", "Nithya"]

# === Validation Helper ===
def validate_columns(df: pd.DataFrame, expected_cols: list) -> bool:
    df_cols = [col.strip().lower() for col in df.columns]
    expected = [col.strip().lower() for col in expected_cols]
    return df_cols == expected

def show():
    st.title("📥 Import Transactions")

    # --- Home Navigation ---
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    # --- Person Selection ---
    selected_person = st.selectbox("👤 Who's data are you importing?", PEOPLE)

    # === Bank Statement Upload ===
    st.header("🏦 Upload Bank Statement")

    bank_file = st.file_uploader("Upload bank statement CSV", type=["csv"], key="bank")
    bank_cols = [
        'account_number', 'txn_timestamp', 'amount', 'current_balance', 'type',
        'reference', 'merchant', 'category_icon_name', 'category', 'bank_name', 'notes'
    ]

    if bank_file:
        df = pd.read_csv(bank_file)
        df.columns = df.columns.str.strip()

        if not validate_columns(df, bank_cols):
            st.error("❌ Uploaded Bank CSV must match expected column schema.")
            st.markdown(f"**Expected columns:** `{', '.join(bank_cols)}`")
            st.markdown(f"**Uploaded columns:** `{', '.join(df.columns)}`")
        else:
            df["person"] = selected_person
            df["txn_timestamp"] = pd.to_datetime(df["txn_timestamp"], errors="coerce")
            df["date"] = df["txn_timestamp"].dt.date.astype(str)
            df["time"] = df["txn_timestamp"].dt.time.astype(str)

            worksheet = get_worksheet(SHEET_URL, BANK_SHEET)
            data_to_append = df.iloc[1:].values.tolist()
            for row in data_to_append:
                worksheet.append_row(row, value_input_option="USER_ENTERED")
            st.success(f"✅ Appended {len(data_to_append)} bank rows to '{BANK_SHEET}'.")

    # === Credit Card Upload ===
    st.header("💳 Upload Credit Card Statement")

    cc_file = st.file_uploader("Upload credit card CSV", type=["csv"], key="credit_card")
    cc_cols = [
        'card_number', 'card_name', 'txn_timestamp', 'amount', 'type',
        'merchant', 'category_icon_name', 'category', 'notes'
    ]

    if cc_file:
        df = pd.read_csv(cc_file)
        df.columns = df.columns.str.strip()

        if not validate_columns(df, cc_cols):
            st.error("❌ Uploaded Credit Card CSV must match expected column schema.")
            st.markdown(f"**Expected columns:** `{', '.join(cc_cols)}`")
            st.markdown(f"**Uploaded columns:** `{', '.join(df.columns)}`")
        else:
            df["person"] = selected_person
            df["txn_timestamp"] = pd.to_datetime(df["txn_timestamp"], errors="coerce")
            df["date"] = df["txn_timestamp"].dt.date.astype(str)
            df["time"] = df["txn_timestamp"].dt.time.astype(str)

            worksheet = get_worksheet(SHEET_URL, CC_SHEET)
            data_to_append = df.iloc[1:].values.tolist()
            for row in data_to_append:
                worksheet.append_row(row, value_input_option="USER_ENTERED")
            st.success(f"✅ Appended {len(data_to_append)} credit card rows to '{CC_SHEET}'.")
