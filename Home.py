# --- File: Home.py (FINAL, CORRECTED CODE) ---

import streamlit as st
import pandas as pd
import plotly.express as px

# --- CRITICAL PATH FIX: Import utilities directly ---
# This ensures Python finds these files when executed via dashboard_app.py
import sys
import os

# Add the project's root directory to the Python path if running in a complex environment
try:
    if 'pages' in os.path.dirname(os.path.abspath(__file__)):
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    pass

from data_loader import DATA, apply_filters
# Ensure page_utils.py is imported successfully
try:
    from page_utils import custom_header, custom_footer 
except ImportError:
    st.error("Error: Could not import page_utils.py. Please ensure the file exists in the root directory.")
    st.stop()
# ----------------------------------------


# --- PAGE SWITCHING UTILITY FUNCTION (KEY TO THE FIX) ---
def navigate_to(target_page_name):
    """Sets the target page in session state and forces a minimal rerun."""
    st.session_state.target_page = target_page_name
    st.rerun() 
# ----------------------------------------


# --- CONFIGURATION & SETUP ---

st.set_page_config(
    page_title="Syam's Hospital Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Custom CSS Injection
def local_css(file_name):
    """Loads a local CSS file for custom styling."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Warning: Could not find '{file_name}'. Running without custom styles.")

local_css("style.css") 

if DATA is None: st.stop()

# Set session state defaults for filters
if 'global_department' not in st.session_state:
    st.session_state['global_department'] = 'ALL DEPARTMENTS'
if 'global_date_range' not in st.session_state:
    min_date = DATA['clinical']['date'].min()
    max_date = DATA['clinical']['date'].max()
    st.session_state['global_date_range'] = (min_date.date(), max_date.date())

# --- 2. Reusable Header ---
custom_header("Executive Operational Summary") 

# --- 3. Global Filters (Expandable Section) ---
all_departments = sorted(DATA['clinical']['department'].unique().tolist())
all_departments.insert(0, 'ALL DEPARTMENTS')

with st.expander("🔍 Filter Data Range and Department"):
    
    col_date, col_dept = st.columns(2)

    min_date = DATA['clinical']['date'].min()
    max_date = DATA['clinical']['date'].max()
    
    col_date.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
        key='global_date_range'
    )
    
    col_dept.selectbox(
        "Filter by Department", 
        all_departments,
        key='global_department'
    )

# Extract filter variables
start_date = pd.to_datetime(st.session_state['global_date_range'][0])
end_date = pd.to_datetime(st.session_state['global_date_range'][1])
selected_department = st.session_state['global_department']


# --- 4. Apply Filters ---
f_clinical_df = apply_filters(DATA['clinical'], start_date, end_date, selected_department)
f_hr_df = apply_filters(DATA['hr'], start_date, end_date, selected_department)
f_lab_df = apply_filters(DATA['lab'], start_date, end_date, selected_department)
f_pharmacy_df = apply_filters(DATA['pharmacy'], start_date, end_date, selected_department)


# --- 5. Navigation Buttons (FIXED IMPLEMENTATION) ---
st.header("Departmental Deep-Dives")
nav_cols = st.columns(4)

# The arguments must be the exact page name keys defined in dashboard_app.py's PAGES dict
nav_cols[0].button("1. Clinical Operations 🏥", type="primary", 
                   on_click=navigate_to, args=("1_Clinical_Operations",))
nav_cols[1].button("2. HR & Workforce 🧑‍⚕️", type="primary", 
                   on_click=navigate_to, args=("2_HR_Workforce",))
nav_cols[2].button("3. Laboratory Services 🧪", type="primary", 
                   on_click=navigate_to, args=("3_Laboratory_Services",))
nav_cols[3].button("4. Pharmacy Services 💊", type="primary", 
                   on_click=navigate_to, args=("4_Pharmacy_Services",))
st.markdown("---")


# =================================================================
# === 6. KPI GRID (4x1) ===
# =================================================================

st.subheader("Key Financial and Patient Volume Indicators")
kpi_cols = st.columns(4)

# 1. Total Patients
total_patients = f_clinical_df['new_inpatient_admissions'].sum() + f_clinical_df['new_outpatients'].sum() + f_clinical_df['new_icu_admissions'].sum()
kpi_cols[0].metric("Total Patients Served", f"{total_patients:,.0f}")

# 2. Total Revenue (Clinical)
total_clinical_cost = f_clinical_df['diagnosis_cost'].sum()
kpi_cols[1].metric("Total Clinical Cost (INR)", f"₹{total_clinical_cost:,.0f}")

# 3. Total Revenue (Pharmacy)
total_pharmacy_revenue = f_pharmacy_df['pharmacy_revenue'].sum()
kpi_cols[2].metric("Total Pharmacy Revenue (INR)", f"₹{total_pharmacy_revenue:,.0f}")

# 4. Total Revenue (Lab)
total_lab_cost = f_lab_df['total_cost'].sum()
kpi_cols[3].metric("Total Laboratory Cost (INR)", f"₹{total_lab_cost:,.0f}")


# =================================================================
# === 7. INFOGRAPH GRID (2x1) ===
# =================================================================

st.markdown("---")
st.header("Cross-Functional Insights")

info_row = st.columns(2)

# --- 1. Patient Satisfaction Composite Trend ---
with info_row[0]:
    st.subheader("1. Patient Satisfaction Composite Trend")
    
    sat_data_list = []
    if not f_clinical_df.empty:
        sat_data_list.append(f_clinical_df[['date', 'patient_satisfaction_score']].rename(columns={'patient_satisfaction_score': 'Clinical_Sat'}))
    if not f_lab_df.empty:
        sat_data_list.append(f_lab_df[['date', 'patient_satisfaction']].rename(columns={'patient_satisfaction': 'Laboratory_Sat'}))
    if not f_pharmacy_df.empty:
        sat_data_list.append(f_pharmacy_df[['date', 'patient_satisfaction_score']].rename(columns={'patient_satisfaction_score': 'Pharmacy_Sat'}))

    if sat_data_list:
        df_merged = pd.concat(sat_data_list, ignore_index=True)
        df_merged['month'] = df_merged['date'].dt.to_period('M').astype(str)
        
        df_plot = df_merged.groupby('month').mean(numeric_only=True).reset_index()

        df_plot_melt = df_plot.melt(
            id_vars=['month'], 
            var_name='Department', 
            value_name='Satisfaction Score'
        )
        
        df_plot_melt['Department'] = df_plot_melt['Department'].str.replace('_Sat', '')

        fig_sat = px.line(
            df_plot_melt, 
            x='month', 
            y='Satisfaction Score', 
            color='Department',
            title='Avg. Patient Satisfaction Score Over Time',
            markers=True,
            color_discrete_sequence=['#0077B6', '#f39c12', '#2ecc71'] 
        )
        fig_sat.update_layout(yaxis_range=[3.0, 5.0])
        st.plotly_chart(fig_sat, use_container_width=True)
    else:
        st.info("No data available to calculate Patient Satisfaction Composite.")


# --- 2. Department vs. Revenue Graph ---
with info_row[1]:
    st.subheader("2. Department vs. Total Financial Contribution")
    
    df_clinical_agg = f_clinical_df.groupby('department')['diagnosis_cost'].sum().rename("Clinical Cost (INR)")
    df_pharmacy_agg = f_pharmacy_df.groupby('department')['pharmacy_revenue'].sum().rename("Pharmacy Revenue (INR)")
    df_lab_agg = f_lab_df.groupby('department')['total_cost'].sum().rename("Laboratory Cost (INR)")
    
    df_finance = pd.concat([df_clinical_agg, df_pharmacy_agg, df_lab_agg], axis=1).fillna(0)
    df_finance['Total Financial Contribution'] = df_finance.sum(axis=1)

    df_finance_plot = df_finance.sort_values(by='Total Financial Contribution', ascending=False).reset_index()

    fig_bar = px.bar(
        df_finance_plot.head(10), 
        x='department',
        y=['Clinical Cost (INR)', 'Pharmacy Revenue (INR)', 'Laboratory Cost (INR)'],
        title='Financial Contribution by Department (Top 10)',
        labels={'value': 'Total Value (₹)', 'department': 'Department'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# =================================================================
# === 8. AVAILABLE SERVICES (VISUAL CARDS) ===
# =================================================================

st.markdown("---")
st.header("Available Services and Specialties")

services = [
    ("Cardiology", "❤️"), ("General Medicine", "💊"), ("Orthopedics", "🦴"), 
    ("Neurology", "🧠"), ("Gynecology & OBG", "🤰"), ("Pediatrics", "👶"), 
    ("Pulmonology", "😷"), ("Nephrology", "💧"), ("General Surgery", "🔪")
]

dept_cols = st.columns(3)
st.markdown("""<style>.service-card {border: 1px solid #0077B6; border-radius: 10px; padding: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.15); background-color: #f0f8ff; transition: transform 0.2s;} .service-card:hover {transform: translateY(-5px); box-shadow: 0 6px 12px rgba(0,0,0,0.3);} .service-icon {font-size: 3em; display: block; margin-bottom: 5px;}</style>""", unsafe_allow_html=True)

for i, (name, icon) in enumerate(services):
    with dept_cols[i % 3]:
        st.markdown(
            f"""
            <div class='service-card'>
                <span class='service-icon'>{icon}</span>
                <p style='font-weight: bold; margin: 0; color: #004d66;'>{name}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


# =================================================================
# === 9. Reusable Footer ===
# =================================================================
custom_footer()