import streamlit as st
from budgeting import show as show_budgeting
from import_ import show as show_import
from home_dashboard import show as show_dashboard
from data import show as show_data

# --- App Configuration ---
st.set_page_config(page_title="💸 CoFi | Personal Finance Tracker", layout="wide")

# --- Session State Setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()

# --- Top Bar Styling ---
st.markdown("""
    <style>
        .top-bar {
            background-color: #1C1C1C;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .app-title {
            flex: 1;
            font-size: 1.6rem;
            font-weight: 700;
            color: #FFEDA8;
        }
        .nav-btn {
            background-color: transparent !important;
            border: none !important;
            color: #FFEDA8 !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            margin-left: 1rem !important;
            cursor: pointer;
        }
        .nav-btn:hover {
            color: #FFF0B3 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Top Bar Content ---
st.markdown(
    f"""
    <div class="top-bar">
        <div class="app-title"> CoFi</div>
    </div>
    """, unsafe_allow_html=True
)

# --- Navigation Buttons ---
col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 6])
with col1:
    if st.button("🏠 Dashboard", key="nav_dash"):
        navigate_to("dashboard")
with col2:
    if st.button("📝 Budgeting", key="nav_budget"):
        navigate_to("budgeting")
with col3:
    if st.button("📥 Import", key="nav_import"):
        navigate_to("import")
with col4:
    if st.button("📊 Data", key="nav_data"):
        navigate_to("data")

# --- Page Rendering Logic ---
if st.session_state.page == "home":
    st.title("👋 Welcome to CoFi")
    st.markdown("Select a section above to get started.")
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "budgeting":
    show_budgeting()
elif st.session_state.page == "import":
    show_import()
elif st.session_state.page == "data":
    show_data()
