import streamlit as st

# ✅ Set up page
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

    # Styled HTML buttons
    st.markdown("""
        <style>
        .btn-grid {
            display: flex;
            gap: 1.5rem;
            margin-top: 2rem;
        }
        .btn {
            padding: 1.2rem 2rem;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 0.6rem;
            text-align: center;
            color: white;
            text-decoration: none;
            flex: 1;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .btn:hover {
            opacity: 0.9;
        }
        .dashboard { background-color: #2E86C1; }
        .budgeting { background-color: #27AE60; }
        .import { background-color: #D35400; }
        .data { background-color: #8E44AD; }
        </style>

        <div class="btn-grid">
            <a href="?page=dashboard" class="btn dashboard">🏠 Dashboard</a>
            <a href="?page=budgeting" class="btn budgeting">📝 Budgeting</a>
            <a href="?page=import" class="btn import">📥 Import</a>
            <a href="?page=data" class="btn data">📊 Data</a>
        </div>
    """, unsafe_allow_html=True)

    # Handle navigation via query parameter
    if st.query_params.get("page") == "dashboard":
        navigate_to("dashboard")
    elif st.query_params.get("page") == "budgeting":
        navigate_to("budgeting")
    elif st.query_params.get("page") == "import":
        navigate_to("import")
    elif st.query_params.get("page") == "data":
        navigate_to("data")

elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "budgeting":
    show_budgeting()
elif st.session_state.page == "import":
    show_import()
elif st.session_state.page == "data":
    show_data()
