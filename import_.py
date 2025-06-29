import streamlit as st
import pandas as pd
from utils.gsheet import get_worksheet
from datetime import datetime

# Load Custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# === Constants ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1C2IwUJSB30tbfu1dbR-_PKRVeSePcGq7fpLxMqtTa1w"
BANK_SHEET = "bank_transactions"
CC_SHEET = "credit_card"

# === Helper ===
def validate_columns(df: pd.DataFrame, expected_cols: list) -> bool:
    df_cols = [col.strip().lower() for col in df.columns]
    expected = [col.strip().lower() for col in expected_cols]
    return df_cols[:len(expected)] == expected

def split_timestamp(ts):
    try:
        dt = pd.to_datetime(ts)
        return dt.date().isoformat(), dt.time().strftime("%H:%M:%S")
    except:
        return "", ""

def convert_row(row):
    return [str(item) if not pd.isna(item) else "" for item in row]

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
            <h1 style="margin-bottom: 0.5rem;">📥 Import Transactions</h1>
            <p style="color: #666; margin-bottom: 0;">Upload your bank and credit card statements</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Bank Statement Upload ---
    st.markdown("### 🏦 Upload Bank Statement")
    person = st.selectbox("Who's Data?", ["Divyaraj", "Nithya"], key="person_upload")
    bank_file = st.file_uploader("Upload bank statement CSV", type=["csv"], key="bank_upload")
    bank_cols = [
        'account_number', 'txn_timestamp', 'amount', 'current_balance', 'type',
        'reference', 'merchant', 'category_icon_name', 'category', 'bank_name', 'notes'
    ]

    if bank_file:
        try:
            df = pd.read_csv(bank_file)
            if not validate_columns(df, bank_cols):
                st.error("❌ Uploaded Bank CSV must match expected column schema.")
                st.markdown(f"**Expected:** `{', '.join(bank_cols)}`")
                st.markdown(f"**Got:** `{', '.join(df.columns)}`")
            else:
                df = df.iloc[1:]  # skip header row if included twice
                df["person"] = person
                df["date"], df["time"] = zip(*df["txn_timestamp"].apply(split_timestamp))
                final_data = df[bank_cols + ["person", "date", "time"]]
                worksheet = get_worksheet(SHEET_URL, BANK_SHEET)
                worksheet.append_rows([convert_row(row) for row in final_data.values.tolist()],
                                      value_input_option="USER_ENTERED")
                st.success(f"✅ Uploaded {len(final_data)} rows to '{BANK_SHEET}'.")
                with st.expander("📋 Uploaded Data Preview"):
                    st.dataframe(final_data, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error uploading bank statement: {e}")
        # Center the upload button (if you want a manual upload button, place it here)
        # col1, col2, col3 = st.columns([1,1,1])
        # with col2:
        #     st.button("Upload Bank Data")

    st.markdown("---")

    # --- Credit Card Statement Upload ---
    st.markdown("### 💳 Upload Credit Card Statement")
    cc_file = st.file_uploader("Upload credit card CSV", type=["csv"], key="cc_upload")
    cc_cols = [
        'card_number', 'card_name', 'txn_timestamp', 'amount', 'type',
        'merchant', 'category_icon_name', 'category', 'notes'
    ]

    if cc_file:
        try:
            df = pd.read_csv(cc_file)
            if not validate_columns(df, cc_cols):
                st.error("❌ Uploaded Credit Card CSV must match expected column schema.")
                st.markdown(f"**Expected:** `{', '.join(cc_cols)}`")
                st.markdown(f"**Got:** `{', '.join(df.columns)}`")
            else:
                df = df.iloc[1:]
                df["person"] = person
                df["date"], df["time"] = zip(*df["txn_timestamp"].apply(split_timestamp))
                final_data = df[cc_cols + ["person", "date", "time"]]
                worksheet = get_worksheet(SHEET_URL, CC_SHEET)
                worksheet.append_rows([convert_row(row) for row in final_data.values.tolist()],
                                      value_input_option="USER_ENTERED")
                st.success(f"✅ Uploaded {len(final_data)} rows to '{CC_SHEET}'.")
                with st.expander("📋 Uploaded Data Preview"):
                    st.dataframe(final_data, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error uploading credit card statement: {e}")
        # Center the upload button (if you want a manual upload button, place it here)
        # col1, col2, col3 = st.columns([1,1,1])
        # with col2:
        #     st.button("Upload Credit Card Data")

    # Tips Section
    st.markdown("### 💡 Import Tips")
    st.markdown("""
    <div class="custom-card">
        <ul style="margin-bottom: 0;">
            <li>Ensure your CSV columns match the required schema exactly.</li>
            <li>Remove any extra header rows from your export before uploading.</li>
            <li>Preview your data before confirming upload.</li>
            <li>Contact support if you face repeated upload errors.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
