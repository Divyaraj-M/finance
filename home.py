import streamlit as st

# ✅ Set page
st.set_page_config(page_title="💸 Home", layout="wide")

from budgeting import show as show_budgeting
from import_ import show as show_import
from home_dashboard import show as show_dashboard
from data import show as show_data

# --- Session state routing ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_to(target):
    st.session_state.page = target
    st.rerun()

# --- Styling ---
st.markdown("""
    <style>
    .button-row {
        display: flex;
        gap: 1.5rem;
        margin-top: 2rem;
    }
    .button-col button {
        background-color: #1B2631;
        color: #FFEDA8 !important;
        padding: 1.2rem;
        font-size: 1.1rem;
        border: none;
        border-radius: 0.6rem;
        width: 100%;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: all 0.2s ease-in-out;
    }
    .button-col button:hover {
        background-color: #34495E;
        transform: scale(1.03);
    }
    </style>
""", unsafe_allow_html=True)

# --- Render Pages ---
if st.session_state.page == "home":
    st.title("🔐 Personal Finance Tracker v1")
    st.markdown("##### 👤 <span style='color:#FFEDA8'>Welcome, Divyaraj & Nithya</span>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 Dashboard"):
            navigate_to("dashboard")
    with col2:
        if st.button("📝 Budgeting"):
            navigate_to("budgeting")
    with col3:
        if st.button("📥 Import"):
            navigate_to("import")
    with col4:
        if st.button("📊 Data"):
            navigate_to("data")

elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "budgeting":
    show_budgeting()
elif st.session_state.page == "import":
    show_import()
elif st.session_state.page == "data":
    show_data()
