"""
Main Application
Login system and dashboard router for Army Drill Evaluation System
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth_utils import initialize_session, login, logout, is_authenticated, get_current_user, register, check_username_exists
from student_app import show_student_dashboard
from teacher_app import show_teacher_dashboard


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Army Drill Evaluation System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# GLOBAL STYLES - Clean & Minimal
# ==========================================================

st.markdown("""
<style>
    /* Clean minimal design */
    .main-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 40px 30px;
    }
    
    .app-header {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .app-logo {
        font-size: 60px;
        margin-bottom: 10px;
    }
    
    .app-title {
        font-size: 28px;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 5px;
    }
    
    .app-subtitle {
        font-size: 14px;
        color: #6b7280;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #e5e7eb;
        padding: 12px 14px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        font-size: 15px;
        padding: 12px 20px;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Radio button styling */
    .stRadio > div {
        justify-content: center;
        gap: 20px;
    }
    
    /* Divider */
    hr {
        margin: 20px 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Navbar - minimal */
    .navbar-minimal {
        background: #ffffff;
        padding: 16px 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid #e5e7eb;
</style>
""", unsafe_allow_html=True)


# ==========================================================
# SESSION INITIALIZATION
# ==========================================================

initialize_session()


# ==========================================================
# LOGIN PAGE
# ==========================================================

def show_login_page():
    """Display clean login/register page"""
    
    # Centered container
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Header
        st.markdown("""
        <div class="app-header">
            <div class="app-logo">🎖️</div>
            <div class="app-title">Army Drill Evaluation</div>
            <div class="app-subtitle">AI-Powered Pose Analysis System</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs for Login/Register
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        # ============ LOGIN TAB ============
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Role selection
            role = st.radio(
                "Select Role",
                ["Student", "Teacher"],
                horizontal=True,
                key="login_role"
            )
            role_value = role.lower()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Login form
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", placeholder="Enter username", key="login_user")
                password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
                
                if submit:
                    if not username or not password:
                        st.error("Please fill in all fields")
                    else:
                        if login(username.lower(), password, role_value):
                            st.success("Welcome back!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
            
            # Demo credentials
            with st.expander("Demo Accounts", expanded=False):
                st.caption("**Students:** student1 / pass123")
                st.caption("**Teacher:** teacher1 / admin123")
        
        # ============ REGISTER TAB ============
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Role selection for registration
            reg_role = st.radio(
                "I am a",
                ["Student", "Teacher"],
                horizontal=True,
                key="reg_role"
            )
            reg_role_value = reg_role.lower()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Registration form
            with st.form("register_form", clear_on_submit=True):
                full_name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
                reg_username = st.text_input("Username", placeholder="Choose a unique username", key="reg_user")
                reg_password = st.text_input("Password", type="password", placeholder="Create password (min 4 chars)", key="reg_pass")
                reg_password2 = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_pass2")
                
                st.markdown("<br>", unsafe_allow_html=True)
                register_btn = st.form_submit_button("Create Account", use_container_width=True, type="primary")
                
                if register_btn:
                    # Validation
                    if not full_name or not reg_username or not reg_password:
                        st.error("Please fill in all fields")
                    elif len(reg_username) < 3:
                        st.error("Username must be at least 3 characters")
                    elif reg_password != reg_password2:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 4:
                        st.error("Password must be at least 4 characters")
                    elif check_username_exists(reg_username.lower()):
                        st.error("Username already taken. Please choose another.")
                    else:
                        success, message = register(reg_username.lower(), reg_password, full_name, reg_role_value)
                        if success:
                            st.success("Account created! Please sign in.")
                        else:
                            st.error(message)


# ==========================================================
# MAIN APP ROUTER
# ==========================================================

def main():
    """Main application router"""
    
    if not is_authenticated():
        show_login_page()
    else:
        user = get_current_user()
        
        # Clean minimal navigation bar
        col1, col2, col3 = st.columns([0.5, 3, 1])
        
        with col1:
            st.markdown("<div style='font-size: 32px; padding-top: 8px;'>🎖️</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='padding-top: 12px;'>
                <span style='font-size: 18px; font-weight: 600; color: #1f2937;'>Army Drill Evaluation</span>
                <span style='font-size: 14px; color: #6b7280; margin-left: 16px;'>
                    {user['full_name']} • {user['role'].title()}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("Sign Out", use_container_width=True, type="secondary"):
                logout()
                st.rerun()
        
        st.markdown("<hr style='margin: 10px 0 20px 0; border: none; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
        
        # Route to appropriate dashboard
        if user['role'] == 'student':
            show_student_dashboard(user['username'], user['full_name'])
        elif user['role'] == 'teacher':
            show_teacher_dashboard(user['username'], user['full_name'])


# ==========================================================
# RUN APP
# ==========================================================

if __name__ == "__main__":
    main()
