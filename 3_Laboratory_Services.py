# --- File: pages/3_Laboratory_Services.py ---

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
f_df = apply_filters(DATA['lab'], start_date, end_date, selected_department)
# ----------------------------------------------------

# === REUSABLE HEADER & SUBTITLE ===
custom_header("🧪 Laboratory Services & Ancillary Efficiency")


# =================================================================
# === 5 KPIs (NOW 4x1 Grid) - Avg. Cost per Test REMOVED ===
# =================================================================
st.markdown("### Core Laboratory Performance Metrics")
kpi_cols = st.columns(4) # Changed from 5 to 4 columns

total_tests = f_df['tests_conducted'].sum()
rejected_rate = f_df['rejected_tests'].sum() / total_tests * 100 if total_tests else 0
avg_tat = f_df['avg_tat'].mean()
total_cost = f_df['total_cost'].sum()
avg_instrument_utilization = f_df['instrument_utilization'].mean()

# --- KPI DISPLAY (4 metrics now fit perfectly in 4 columns) ---
kpi_cols[0].metric("Average TAT (Mins)", f"{avg_tat:.1f}", 
                   delta=f"{-1.5} mins", delta_color="inverse") # Lower is better
kpi_cols[1].metric("Test Rejection Rate", f"{rejected_rate:.2f}%", 
                   delta=f"{+0.1}%", delta_color="inverse") # Lower is better
kpi_cols[2].metric("Total Lab Cost (INR)", f"₹{total_cost:,.0f}")
kpi_cols[3].metric("Avg. Instrument Utilization", f"{avg_instrument_utilization:.1f}%")

st.markdown("---")
st.header("6 Infographics: Laboratory Deep Dive")

# === 6 Infographics (2 Rows of 3 Columns) ===
info_row1 = st.columns(3)

# 1. Tests Conducted Volume (Time-Series Chart - Green Theme)
with info_row1[0]:
    st.subheader("1. Test Volume Trend")
    volume_trend = f_df.groupby('month')['tests_conducted'].sum().reset_index()
    volume_trend['month'] = volume_trend['month'].astype(str)
    fig = px.line(volume_trend, x='month', y='tests_conducted', 
                  title='Diagnostic Demand Over Time',
                  color_discrete_sequence=['#1abc9c'], markers=True) 
    st.plotly_chart(fig, use_container_width=True)

# 2. Rejection Causes (Bar Chart - Red/Alarm Colors for Quality Issue)
with info_row1[1]:
    st.subheader("2. Top Rejection Reasons")
    # Split rejection reasons, explode, and count
    rejection_data = f_df['rejection_reasons'].str.split(',', expand=True).stack().str.strip()
    rejection_counts = rejection_data[rejection_data != 'Unknown'].value_counts().nlargest(5).reset_index()
    rejection_counts.columns = ['Reason', 'Count']
    fig = px.bar(rejection_counts, x='Count', y='Reason', orientation='h',
                 title='Root Causes of Quality Failure',
                 color='Count', color_continuous_scale=px.colors.sequential.Reds)
    st.plotly_chart(fig, use_container_width=True)

# 3. TAT vs. Cost per Test (Scatter Plot by Test Type)
with info_row1[2]:
    st.subheader("3. TAT vs. Cost per Test")
    # This chart remains meaningful for granular analysis
    tat_cost = f_df.groupby('test_type')[['avg_tat', 'cost_per_test']].mean().reset_index()
    fig = px.scatter(tat_cost, x='avg_tat', y='cost_per_test', color='test_type',
                     title='Efficiency vs. Expense',
                     labels={'avg_tat': 'Avg. TAT (Mins)', 'cost_per_test': 'Cost (INR)'})
    st.plotly_chart(fig, use_container_width=True)

# Row 2 (Infographs 4, 5, 6)
info_row2 = st.columns(3)

# 4. Instrument Utilization (Bar Chart - Green/Mint Theme)
with info_row2[0]:
    st.subheader("4. Instrument Utilization")
    inst_agg = f_df.groupby('instrument_name')['instrument_utilization'].mean().reset_index()
    fig = px.bar(inst_agg, x='instrument_name', y='instrument_utilization', 
                 title='Utilization of Key Equipment',
                 color='instrument_utilization', color_continuous_scale=px.colors.sequential.Mint)
    st.plotly_chart(fig, use_container_width=True)
    
# 5. Volume by Department (Stacked Bar Chart)
with info_row2[1]:
    st.subheader("5. Test Volume by Department")
    dept_volume = f_df.groupby('department')['tests_conducted'].sum().reset_index()
    fig = px.bar(dept_volume, x='department', y='tests_conducted', 
                 title='Demand Origin',
                 color_discrete_sequence=['#3498db'])
    st.plotly_chart(fig, use_container_width=True)

# 6. Patient Satisfaction (Gauge/Card)
with info_row2[2]:
    st.subheader("6. Lab Patient Satisfaction")
    avg_sat = f_df['patient_satisfaction'].mean()
    st.metric("Average Lab Satisfaction Score (Out of 5)", f"{avg_sat:.2f}", 
             delta=f"{avg_sat - 4.0:.2f}", delta_color="normal")
    st.info("Goal: Score above 4.0. Monitor for dips.")

# === REUSABLE FOOTER ===
custom_footer()