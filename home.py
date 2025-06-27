import streamlit as st
from budgeting import show as show_budgeting
from import_ import show as show_import
from home_dashboard import show as show_dashboard
from data import show as show_data

# --- App Config ---
st.set_page_config(page_title="💸 CoFi | Personal Finance Tracker", layout="wide")

# --- Session State Setup ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_to(target):
    st.session_state.page = target
    st.rerun()

# --- NAVIGATION BAR STYLES ---
st.markdown("""
    <style>
        .nav-container {
            background-color: #1C1C1C;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 0.5rem;
        }

        .app-title {
            color: #FFEDA8;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }

        .nav-links button {
            background-color: transparent !important;
            border: none !important;
            color: #FFEDA8 !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            margin-left: 1rem !important;
        }

        .welcome {
            font-size: 1.4rem;
            color: #FFEDA8;
            padding-top: 1rem;
        }

        hr {
            border: 1px solid #444;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- NAVIGATION BAR HTML ---
st.markdown(f"""
    <div class="nav-container">
        <div class="app-title">💸 CoFi</div>
        <div class="nav-links">
            <form action="" method="post">
                <button type="submit" name="page" value="dashboard">🏠 Dashboard</button>
                <button type="submit" name="page" value="budgeting">📝 Budgeting</button>
                <button type="submit" name="page" value="import">📥 Import</button>
                <button type="submit" name="page" value="data">📊 Data</button>
            </form>
        </div>
    </div>
""", unsafe_allow_html=True)

# Handle button clicks from the HTML form
if st.session_state.get('page') is None and st.query_params.get("page"):
    st.session_state.page = st.query_params["page"]
elif st.session_state.get('page') is None:
    st.session_state.page = "home"

# --- MAIN BODY ---
if st.session_state.page == "home":
    st.markdown('<div class="welcome">👋 Welcome, Divyaraj & Nithya</div><hr>', unsafe_allow_html=True)
    st.markdown("#### Start by choosing an option from the navigation bar above.")

elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "budgeting":
    show_budgeting()
elif st.session_state.page == "import":
    show_import()
elif st.session_state.page == "data":
    show_data()
