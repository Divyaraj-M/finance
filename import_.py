import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet
from datetime import datetime

# === Constants ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BANK_SHEET = "bank_transactions"
CC_SHEET = "credit_card"
PEOPLE = ["Divyaraj", "Nithya"]

# === Column Expectations ===
BANK_COLS = [
    'account_number', 'txn_timestamp', 'amount', 'current_balance', 'type',
    'reference', 'merchant', 'category_icon_name', 'category', 'bank_name', 'notes'
]
CC_COLS = [
    'card_number', 'card_name', 'txn_timestamp', 'amount', 'type',
    'merchant', 'category_icon_name', 'category', 'notes'
]

# === Validation Helper ===
def validate_columns(df: pd.DataFrame, expected_cols: list) -> bool:
    df_cols = [col.strip().lower() for col in df.columns]
    expected = [col.strip().lower() for col in expected_cols]
    return df_cols == expected

def enrich_with_person_date_time(df: pd.DataFrame, person: str) -> pd.DataFrame:
    df["person"] = person
    df["txn_timestamp"] = pd.to_datetime(df["txn_timestamp"], errors="coerce")
    df["date"] = df["txn_timestamp"].dt.date
    df["time"] = df["txn_timestamp"].dt.time
    return df

def convert_row(row):
    return [str(val) if pd.notna(val) else "" for val in row]

def show():
    st.title("📥 Import Transactions")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    st.subheader("🧑 Select Person")
    selected_person = st.selectbox("Whose transactions are these?", PEOPLE)

    # === BANK UPLOAD ===
    st.header("🏦 Upload Bank Statement CSV")
    bank_file = st.file_uploader("Upload your bank statement CSV", type=["csv"], key="bank")

    if bank_file:
        df = pd.read_csv(bank_file)
        if not validate_columns(df, BANK_COLS):
            st.error("❌ Uploaded Bank CSV must match expected column schema.")
            st.markdown(f"**Expected columns:** `{', '.join(BANK_COLS)}`")
            st.markdown(f"**Uploaded columns:** `{', '.join(df.columns)}`")
        else:
            df = enrich_with_person_date_time(df, selected_person)
            worksheet = get_worksheet(SHEET_URL, BANK_SHEET)
            data_to_append = df.values.tolist()
            for row in data_to_append:
                worksheet.append_row(convert_row(row), value_input_option="USER_ENTERED")
            st.success(f"✅ Appended {len(data_to_append)} bank transactions.")

    # === CREDIT CARD UPLOAD ===
    st.header("💳 Upload Credit Card Statement CSV")
    cc_file = st.file_uploader("Upload your credit card CSV", type=["csv"], key="credit_card")

    if cc_file:
        df = pd.read_csv(cc_file)
        if not validate_columns(df, CC_COLS):
            st.error("❌ Uploaded Credit Card CSV must match expected column schema.")
            st.markdown(f"**Expected columns:** `{', '.join(CC_COLS)}`")
            st.markdown(f"**Uploaded columns:** `{', '.join(df.columns)}`")
        else:
            df = enrich_with_person_date_time(df, selected_person)
            worksheet = get_worksheet(SHEET_URL, CC_SHEET)
            data_to_append = df.values.tolist()
            for row in data_to_append:
                worksheet.append_row(convert_row(row), value_input_option="USER_ENTERED")
            st.success(f"✅ Appended {len(data_to_append)} credit card transactions.")
