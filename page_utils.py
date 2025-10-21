# --- File: page_utils.py ---

import streamlit as st
from datetime import datetime

# --- Reusable Header Function ---
def custom_header(subtitle=""):
    """
    Renders the hospital banner with a dynamic subtitle for each department page.
    """
    # 1. Hospital Title Banner (Matches Home.py design)
    st.markdown(
        """
        <div class='custom-banner' style='text-align: center;'>
            <h1 style='margin: 0; font-size: 3.5em; font-weight: 900; color: white;'>SYAM MULTISPECIALITY HOSPITAL</h1>
            <p style='margin: 0; font-size: 1.8em; font-weight: 600; color: #f0f8ff;'>BHIMAVARAM</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 2. Page Subtitle (e.g., Clinical Services)
    if subtitle:
        st.markdown(f"<h2 style='text-align: center; color: #0077B6; margin-top: 20px; font-weight: 700;'>{subtitle}</h2>", unsafe_allow_html=True)
    
    st.markdown("---")


# --- Reusable Footer Function ---
def custom_footer():
    """
    Renders the standardized footer message at the bottom of the page.
    """
    current_year = datetime.now().year
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; font-size: 0.9em; color: #6c757d; padding: 10px;'>
            Dashboard Conceptualized and Developed by <span style='font-weight: bold;'>Dr.M.P.V.N.S.S.P SYAM KUMAR (Pharm.D)</span><br>
            <span style='font-style: italic;'>Role: Healthcare Informatics Lead</span><br>
            &copy; {current_year} Syam Multispeciality Hospital. All Rights Reserved.
        </div>
        """,
        unsafe_allow_html=True
    )