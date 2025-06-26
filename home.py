import streamlit as st

# ✅ FIRST Streamlit call
st.set_page_config(page_title="💸 Home", layout="wide")

from budgeting import show as show_budgeting
from import_ import show as show_import
from home_dashboard import show as show_dashboard
from data import show as show_data


# --- Session state for navigation ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_to(target):
    st.session_state.page = target
    st.rerun()

# --- Render pages ---
if st.session_state.page == "home":
    st.title("🔐 Personal Finance Tracker v1")
    st.markdown("##### 👤 Welcome, Divyaraj & Nithya")

    col1, col2, col3 = st.columns(4)
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            navigate_to("dashboard")
    with col2:
        if st.button("📝 Budgeting", use_container_width=True):
            navigate_to("budgeting")
    with col3:
        if st.button("📥 Import", use_container_width=True):
            navigate_to("import")
    with col4:
        if st.button("📥 Data", use_container_width=True):
            navigate_to("data")
            
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "budgeting":
    show_budgeting()
elif st.session_state.page == "import":
    show_import()
    
elif st.session_state.page == "data":
    show_data()
