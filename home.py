import streamlit as st

# ✅ Set page config
st.set_page_config(page_title="💸 Home", layout="wide")

# ✅ Import page modules
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
    st.markdown("<h1 style='text-align: center;'>🔐 Personal Finance Tracker v1</h1>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center;'>👤 Welcome, <b>Divyaraj</b> & <b>Nithya</b></h5>", unsafe_allow_html=True)
    st.markdown("---")

    # Styled buttons using HTML + CSS injection
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <style>
        .dashboard-btn {
            background-color: #2D6A4F;
            color: white;
            padding: 0.75rem;
            border-radius: 0.5rem;
            text-align: center;
            display: block;
            font-size: 1.1rem;
            font-weight: bold;
            text-decoration: none;
        }
        .dashboard-btn:hover {
            background-color: #40916C;
            color: white;
        }
        </style>
        <a class="dashboard-btn" href="javascript:window.location.reload();">🏠 Dashboard</a>
        """, unsafe_allow_html=True)

        if st.button("Open Dashboard", key="dash"):
            navigate_to("dashboard")

    with col2:
        st.markdown("""
        <style>
        .budget-btn {
            background-color: #6A4C93;
            color: white;
            padding: 0.75rem;
            border-radius: 0.5rem;
            text-align: center;
            display: block;
            font-size: 1.1rem;
            font-weight: bold;
            text-decoration: none;
        }
        .budget-btn:hover {
            background-color: #8561C5;
            color: white;
        }
        </style>
        <a class="budget-btn" href="javascript:window.location.reload();">📝 Budgeting</a>
        """, unsafe_allow_html=True)

        if st.button("Open Budgeting", key="budget"):
            navigate_to("budgeting")

    with col3:
        st.markdown("""
        <style>
        .import-btn {
            background-color: #D00000;
            color: white;
            padding: 0.75rem;
            border-radius: 0.5rem;
            text-align: center;
            display: block;
            font-size: 1.1rem;
            font-weight: bold;
            text-decoration: none;
        }
        .import-btn:hover {
            background-color: #FF595E;
            color: white;
        }
        </style>
        <a class="import-btn" href="javascript:window.location.reload();">📥 Import</a>
        """, unsafe_allow_html=True)

        if st.button("Open Import", key="import"):
            navigate_to("import")

    with col4:
        st.markdown("""
        <style>
        .data-btn {
            background-color: #1D3557;
            color: white;
            padding: 0.75rem;
            border-radius: 0.5rem;
            text-align: center;
            display: block;
            font-size: 1.1rem;
            font-weight: bold;
            text-decoration: none;
        }
        .data-btn:hover {
            background-color: #457B9D;
            color: white;
        }
        </style>
        <a class="data-btn" href="javascript:window.location.reload();">📊 Data</a>
        """, unsafe_allow_html=True)

        if st.button("Open Data", key="data"):
            navigate_to("data")

# --- Delegate other pages ---
elif st.session_state.page == "dashboard":
    show_dashboard()

elif st.session_state.page == "budgeting":
    show_budgeting()

elif st.session_state.page == "import":
    show_import()

elif st.session_state.page == "data":
    show_data()
