# --- File: pages/2_HR_Workforce.py ---

import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import DATA, apply_filters
from page_utils import custom_header, custom_footer 
import numpy as np

# --- 1. CSS INJECTION (CRUCIAL FOR VISUAL AESTHETICS) ---
def local_css(file_name):
    """Loads a local CSS file for custom styling."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

st.set_page_config(layout="wide")
local_css("style.css") 

# --- 2. INITIALIZATION & FILTERS ---
if DATA is None: st.stop()
if 'global_department' not in st.session_state: st.session_state['global_department'] = 'ALL DEPARTMENTS'
if 'global_date_range' not in st.session_state: 
    min_date = DATA['clinical']['date'].min(); max_date = DATA['clinical']['date'].max()
    st.session_state['global_date_range'] = (min_date.date(), max_date.date())
    st.info("Filters initialized with default values. Please set filters on the Home page.")

start_date = pd.to_datetime(st.session_state['global_date_range'][0])
end_date = pd.to_datetime(st.session_state['global_date_range'][1])
selected_department = st.session_state['global_department']
f_df = apply_filters(DATA['hr'], start_date, end_date, selected_department)
# ----------------------------------------------------

# === CRITICAL FIX: CREATE UNIQUE EMPLOYEE DATAFRAME FOR DISTRIBUTIONS ===
# This ensures distribution charts (Age, Gender, Satisfaction) count employees only once.
f_unique_employees_df = f_df.sort_values(by='date', ascending=False).drop_duplicates(subset=['employee_id'], keep='first')
# -----------------------------------------------------------------------


# === REUSABLE HEADER & SUBTITLE ===
custom_header("🧑‍⚕️ Human Resources & Workforce Analytics")


# =================================================================
# === 5 KPIs (NOW 4x1 GRID) - Absenteeism Ratio REMOVED ===
# =================================================================
st.markdown("### Core Workforce Metrics")
kpi_cols = st.columns(4) # Changed from 5 to 4 columns

# KPIs calculated using the unique count where appropriate
total_employees = f_df['employee_id'].nunique()
avg_satisfaction = f_unique_employees_df['employee_satisfaction'].mean()
avg_tenure = f_unique_employees_df['tenure_years'].mean()

kpi_cols[0].metric("Total Active Employees", f"{total_employees:,.0f}")
kpi_cols[1].metric("Total Overtime Hours", f"{f_df['overtime_hours'].sum():,.0f}")
kpi_cols[2].metric("Avg. Employee Tenure (Yrs)", f"{avg_tenure:.1f}")
kpi_cols[3].metric("Avg. Employee Satisfaction", f"{avg_satisfaction:.1f}", 
                   delta=f"{+0.1}", delta_color="normal")


st.markdown("---")
st.header("6 Infographics: HR Deep Dive")

# === 6 Infographics (2 Rows of 3 Columns) ===
info_row1 = st.columns(3)

# 1. Overtime Analysis (Stacked Bar Chart - Uses all records for summation)
with info_row1[0]:
    st.subheader("1. Overtime by Department & Shift")
    ot_agg = f_df.groupby(['department', 'shift_type'])['overtime_hours'].sum().reset_index()
    fig = px.bar(ot_agg, x='department', y='overtime_hours', color='shift_type',
                 title='Overtime Hours by Department',
                 color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig, use_container_width=True)

# 2. Staff Category Split (Donut Chart - Uses unique employees for accurate distribution)
with info_row1[1]:
    st.subheader("2. Staff Category Distribution")
    category_counts = f_unique_employees_df['staff_category'].value_counts().reset_index()
    fig = px.pie(category_counts, names='staff_category', values='count', hole=.5,
                 title='FTE vs. Contract vs. Agency',
                 color_discrete_sequence=px.colors.sequential.Agsunset)
    st.plotly_chart(fig, use_container_width=True)

# 3. Satisfaction Drivers (Box Plot by Role - Uses unique employees for accurate distribution)
with info_row1[2]:
    st.subheader("3. Satisfaction by Role")
    fig = px.box(f_unique_employees_df, x='role', y='employee_satisfaction',
                 title='Satisfaction Distribution by Role',
                 color_discrete_sequence=['#FFC300'])
    st.plotly_chart(fig, use_container_width=True)

# Row 2 (Infographs 4, 5, 6)
info_row2 = st.columns(3)

# 4. Pay Equity Comparison (Grouped Bar Chart - Uses unique employees for accurate distribution)
with info_row2[0]:
    st.subheader("4. Average Pay by Role (₹)")
    pay_agg = f_unique_employees_df.groupby('role')['avg_pay'].mean().reset_index()
    fig = px.bar(pay_agg, x='role', y='avg_pay', 
                 title='Average Pay (INR)',
                 labels={'avg_pay': 'Avg. Pay (INR)'},
                 color_discrete_sequence=px.colors.qualitative.Dark2)
    st.plotly_chart(fig, use_container_width=True)
    
# 5. Stability vs. Absences (Scatter Plot - Correctly groups by employee_id)
with info_row2[1]:
    st.subheader("5. Tenure vs. Absenteeism")
    # This correctly aggregates total absent days against average tenure per employee
    stability_data = f_df.groupby('employee_id').agg(
        Avg_Tenure=('tenure_years', 'mean'),
        Total_Absent=('absent_flag', 'sum')
    ).reset_index()
    fig = px.scatter(stability_data, x='Avg_Tenure', y='Total_Absent', 
                     title='Absenteeism by Tenure', color_discrete_sequence=['#E83333'])
    st.plotly_chart(fig, use_container_width=True)

# 6. Workforce Demographics (Age Distribution Histogram - Uses unique employees for accurate count)
with info_row2[2]:
    st.subheader("6. Age Distribution")
    fig = px.histogram(f_unique_employees_df, x='age', color='gender', 
                       title='Age/Gender Distribution (Unique Employees)',
                       color_discrete_sequence=['#f39c12', '#9b59b6'])
    st.plotly_chart(fig, use_container_width=True)

# === REUSABLE FOOTER ===
custom_footer()