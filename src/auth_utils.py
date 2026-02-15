"""
Authentication Utilities
Handles user authentication and session management
"""

import streamlit as st
from data_manager import DataManager


def initialize_session():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'


def login(username, password, role):
    """Attempt to log in a user"""
    data_manager = DataManager()
    success, full_name = data_manager.authenticate_user(username, password, role)
    
    if success:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.full_name = full_name
        st.session_state.role = role
        st.session_state.page = 'dashboard'
        return True
    return False


def logout():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.full_name = None
    st.session_state.role = None
    st.session_state.page = 'login'


def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def get_current_user():
    """Get current user information"""
    return {
        'username': st.session_state.get('username'),
        'full_name': st.session_state.get('full_name'),
        'role': st.session_state.get('role')
    }
