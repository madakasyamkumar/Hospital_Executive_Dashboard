# --- File: pages/1_Clinical_Operations.py ---

import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import DATA, apply_filters
from page_utils import custom_header, custom_footer 
import numpy as np

# --- 1. CSS INJECTION (CRUCIAL FOR VISUAL AESTHETICS) ---
# This ensures the custom background, banner style, and card aesthetics are loaded.
def local_css(file_name):
    """Loads a local CSS file for custom styling."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Allow the page to run even if CSS is not found

st.set_page_config(layout="wide") # Ensure wide layout persists

# Call the CSS injection function immediately after config
local_css("style.css") 


# --- 2. INITIALIZATION & FILTERS (CRITICAL BLOCK) ---
if DATA is None: st.stop()
if 'global_department' not in st.session_state: st.session_state['global_department'] = 'ALL DEPARTMENTS'
if 'global_date_range' not in st.session_state: 
    min_date = DATA['clinical']['date'].min(); max_date = DATA['clinical']['date'].max()
    st.session_state['global_date_range'] = (min_date.date(), max_date.date())
    st.info("Filters initialized with default values. Please set filters on the Home page.")
    
start_date = pd.to_datetime(st.session_state['global_date_range'][0])
end_date = pd.to_datetime(st.session_state['global_date_range'][1])
selected_department = st.session_state['global_department']
f_df = apply_filters(DATA['clinical'], start_date, end_date, selected_department)
# ----------------------------------------------------

# === REUSABLE HEADER & SUBTITLE ===
custom_header("🏥 Clinical Services & Quality Dashboard")
# This renders the bold hospital title and the specific subtitle.


# =================================================================
# === 5 KPIs (4x1 Grid) - CORRECTED OT UTILIZATION ===
# =================================================================

st.markdown("### Core Operational Metrics")
kpi_cols = st.columns(4) # Changed from 5 to 4 columns (Readmission Rate removed)

# Calculate KPIs
avg_los = f_df['avg_length_of_stay'].mean()
ed_wait_time = f_df['ed_wait_time'].mean()
bed_occupancy = f_df['bed_occupancy'].mean()

# --- CORRECTED OT UTILIZATION CALCULATION ---
ot_used_sum = f_df['ot_slots_used'].sum()
ot_avail_sum = f_df['ot_slots_available'].sum()
# This calculation is now correct, yielding a meaningful percentage
ot_utilization_correct = (ot_used_sum / ot_avail_sum) * 100 if ot_avail_sum > 0 else 0

# --- KPI DISPLAY (Consistent Visual Aesthetic) ---
kpi_cols[0].metric("Avg. LOS (Days)", f"{avg_los:.1f}", 
                   delta=f"{-0.1} day", delta_color="inverse") 
kpi_cols[1].metric("ED Wait Time (Mins)", f"{ed_wait_time:.0f}", 
                   delta=f"{-5} mins", delta_color="inverse")
kpi_cols[2].metric("Bed Occupancy (%)", f"{bed_occupancy:.1f}", 
                   delta=f"{+1.0}%")
kpi_cols[3].metric("OT Utilization (%)", f"{ot_utilization_correct:.1f}", 
                   delta=f"{+2.0}%") 

st.markdown("---")
st.header("6 Infographics: Clinical Deep Dive")

# === 6 Infographics (2 Rows of 3 Columns) ===
info_row1 = st.columns(3)

# 1. Admission Volume (Stacked Area Chart)
with info_row1[0]:
    st.subheader("1. Admission Volume Trend")
    admit_trend = f_df.groupby('month')[['new_inpatient_admissions', 'new_outpatients', 'new_icu_admissions']].sum().reset_index()
    admit_trend['month'] = admit_trend['month'].astype(str)
    fig = px.area(admit_trend, x='month', y=['new_inpatient_admissions', 'new_outpatients', 'new_icu_admissions'],
                  title='Demand Over Time',
                  color_discrete_sequence=['#1a73e8', '#34a853', '#fbbc05'])
    st.plotly_chart(fig, use_container_width=True)

# 2. Diagnosis Deep Dive (Top 10 Cost - Teal Theme)
with info_row1[1]:
    st.subheader("2. Top 10 Diagnoses by Cost (₹)")
    diagnosis_cost = f_df.groupby('diagnosis_name')['diagnosis_cost'].sum().nlargest(10).reset_index()
    fig = px.bar(diagnosis_cost, x='diagnosis_name', y='diagnosis_cost',
                 title='Cost Hotspots',
                 color_continuous_scale=px.colors.sequential.Teal, labels={'diagnosis_cost':'Cost (INR)'})
    st.plotly_chart(fig, use_container_width=True)

# 3. Quality Trend (Complications over time - Red/Alarm Theme)
with info_row1[2]:
    st.subheader("3. Complication Rate Trend")
    comp_trend = f_df.groupby('month')[['post_op_complications', 'new_inpatient_admissions']].sum().reset_index()
    comp_trend['Rate'] = (comp_trend['post_op_complications'] / comp_trend['new_inpatient_admissions']) * 100
    comp_trend['month'] = comp_trend['month'].astype(str)
    fig = px.line(comp_trend, x='month', y='Rate', title='Safety Trend',
                  color_discrete_sequence=['#E83333'], markers=True) 
    st.plotly_chart(fig, use_container_width=True)

# Row 2 (Infographs 4, 5, 6)
info_row2 = st.columns(3)

# 4. Efficiency Funnel (OT Utilization - Displaying the correct rate)
with info_row2[0]:
    st.subheader("4. OT Utilization Funnel")
    ot_avail = f_df['ot_slots_available'].sum()
    ot_used = f_df['ot_slots_used'].sum()
    funnel_data = pd.DataFrame({'Stage': ['Used Slots', 'Available Slots'], 'Count': [ot_used, ot_avail]})
    fig = px.funnel(funnel_data, x='Count', y='Stage', 
                    title=f'OT Utilization: {ot_utilization_correct:.1f}%', 
                    color_discrete_sequence=['#34a853', '#0077B6'])
    st.plotly_chart(fig, use_container_width=True)
    
# 5. Patient/Staff Ratio (Visual Metric Cards)
with info_row2[1]:
    st.subheader("5. Key Staff Ratios")
    avg_patients_per_doc = f_df['patients_per_doctor'].mean()
    avg_nurse_to_patient = f_df['nurse_to_patient_ratio'].mean()
    st.markdown(f"**Avg. Patients per Doctor:** <span style='font-size: 2em; color: #1a73e8;'>{avg_patients_per_doc:.1f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Avg. Nurse-to-Patient Ratio:** <span style='font-size: 2em; color: #34a853;'>{avg_nurse_to_patient:.2f}</span>", unsafe_allow_html=True)
    st.info("Monitoring resource adequacy against patient load.")

# 6. LOS vs. Complication Rate (Scatter Plot by Department - Readmission Rate Used)
with info_row2[2]:
    st.subheader("6. Quality & Efficiency Scorecard")
    scatter_data = f_df.groupby('department').agg(
        LOS_Metric=('avg_length_of_stay', 'mean'),
        Readmission_Rate_Metric=('readmission_rate', 'mean'),
        Total_Volume=('new_inpatient_admissions', 'sum')
    ).reset_index()
    
    fig = px.scatter(scatter_data, x='LOS_Metric', y='Readmission_Rate_Metric', color='department',
                     size='Total_Volume', hover_name='department',
                     title='LOS vs. Readmission Rate (Bubble=Volume)')
    st.plotly_chart(fig, use_container_width=True)

# === REUSABLE FOOTER ===
custom_footer()