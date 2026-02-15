"""
Main Application
Login system and dashboard router for Army Drill Evaluation System
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auth_utils import initialize_session, login, logout, is_authenticated, get_current_user
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
# GLOBAL STYLES
# ==========================================================

st.markdown("""
<style>
    /* Login container - improved for dark/light mode */
    .login-container {
        background: rgba(255, 255, 255, 0.98);
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        max-width: 500px;
        margin: 0 auto;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .login-title {
        font-size: 52px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    .login-subtitle {
        font-size: 20px;
        color: #6b7280;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 80px 20px;
        color: white;
    }
    
    .hero-title {
        font-size: 76px;
        font-weight: 700;
        margin-bottom: 20px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    .hero-subtitle {
        font-size: 26px;
        margin-bottom: 40px;
        opacity: 0.95;
        font-family: 'Segoe UI', Arial, sans-serif;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    
    .hero-icon {
        font-size: 130px;
        margin-bottom: 30px;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(3px 3px 6px rgba(0,0,0,0.3));
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-20px);
        }
    }
    
    /* Feature cards - improved contrast */
    .feature-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 35px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 10px 0;
        text-align: center;
    }
    
    .feature-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-size: 22px;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 10px;
    }
    
    .feature-desc {
        font-size: 15px;
        color: #6b7280;
        line-height: 1.6;
    }
    
    /* Navbar */
    .navbar {
        background: white;
        padding: 20px 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .navbar-title {
        font-size: 24px;
        font-weight: 700;
        color: #1f2937;
    }
    
    .navbar-user {
        font-size: 16px;
        color: #6b7280;
    }
    
    /* Stbutton overrides */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
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
    """Display login page"""
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-icon">🎖️</div>
        <div class="hero-title">Army Drill Evaluation</div>
        <div class="hero-subtitle">AI-Powered Pose Analysis & Training System</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='login-header'>
            <div class='login-title'>🔐 Login</div>
            <div class='login-subtitle'>Select your role and sign in</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Role selection
        role = st.radio(
            "I am a:",
            ["👨‍🎓 Student", "👨‍🏫 Teacher"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        role_value = "student" if "Student" in role else "teacher"
        
        st.markdown("---")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    if login(username, password, role_value):
                        st.success(f"✅ Welcome back!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
        
        st.markdown("---")
        
        # Demo credentials
        with st.expander("📝 Demo Credentials"):
            st.markdown("""
            **Student Accounts:**
            - Username: `student1` | Password: `pass123`
            - Username: `student2` | Password: `pass123`
            
            **Teacher Account:**
            - Username: `teacher1` | Password: `admin123`
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Features section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        {
            "icon": "🎯",
            "title": "Real-Time Analysis",
            "desc": "Get instant feedback on your drill postures with AI-powered detection"
        },
        {
            "icon": "📊",
            "title": "Progress Tracking",
            "desc": "Monitor your improvement over time with detailed statistics"
        },
        {
            "icon": "👥",
            "title": "Class Management",
            "desc": "Teachers can track all students' performance in one place"
        },
        {
            "icon": "📈",
            "title": "Analytics Dashboard",
            "desc": "Comprehensive analytics and insights for better training"
        }
    ]
    
    for col, feature in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class='feature-card'>
                <div class='feature-icon'>{feature['icon']}</div>
                <div class='feature-title'>{feature['title']}</div>
                <div class='feature-desc'>{feature['desc']}</div>
            </div>
            """, unsafe_allow_html=True)


# ==========================================================
# MAIN APP ROUTER
# ==========================================================

def main():
    """Main application router"""
    
    if not is_authenticated():
        show_login_page()
    else:
        user = get_current_user()
        
        # Navigation bar
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
                <span style='font-size: 24px; font-weight: 700; color: #1f2937;'>
                    🎖️ Army Drill Evaluation System
                </span>
                <span style='font-size: 16px; color: #6b7280; margin-left: 20px;'>
                    👤 {user['full_name']} ({user['role'].title()})
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                logout()
        
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
