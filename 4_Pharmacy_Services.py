# --- File: pages/4_Pharmacy_Services.py ---

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
f_df = apply_filters(DATA['pharmacy'], start_date, end_date, selected_department)
# ----------------------------------------------------

# === REUSABLE HEADER & SUBTITLE ===
custom_header("💊 Pharmacy Services & Medication Safety")


# =================================================================
# === 5 KPIs (NOW 4x1 GRID) - Dispensing Error Rate REMOVED ===
# =================================================================
st.markdown("### Core Pharmacy Performance Metrics")
kpi_cols = st.columns(4) # Changed from 5 to 4 columns

total_dispensed = f_df['prescriptions_dispensed'].sum()
med_alerts = f_df['medication_alerts'].sum()

kpi_cols[0].metric("Total Prescriptions", f"{total_dispensed:,.0f}")
kpi_cols[1].metric("Avg. Dispensing Time (Mins)", f"{f_df['avg_dispensing_time'].mean():.1f}", 
                   delta=f"{-0.5} min", delta_color="inverse") # Lower is better
kpi_cols[2].metric("Total Revenue (INR)", f"₹{f_df['pharmacy_revenue'].sum():,.0f}")
kpi_cols[3].metric("Medication Alerts (Count)", f"{med_alerts:,.0f}", 
                   delta=f"{+2}", delta_color="inverse") # Lower is better

st.markdown("---")
st.header("6 Infographics: Pharmacy Deep Dive")

# === 6 Infographics (2 Rows of 3 Columns) ===
info_row1 = st.columns(3)

# 1. Safety Performance (Bar Chart - Includes Dispensing Errors in the graphic)
with info_row1[0]:
    st.subheader("1. Dispensing Safety Events")
    safety_events = pd.DataFrame({
        'Event': ['Dispensing Errors', 'Near Miss Events', 'Medication Alerts'],
        'Count': [f_df['dispensing_errors'].sum(), f_df['near_miss_events'].sum(), f_df['medication_alerts'].sum()]
    })
    fig = px.bar(safety_events, x='Event', y='Count', 
                 title='Safety Failure Points',
                 color='Event', color_discrete_sequence=['#e74c3c', '#f1c40f', '#3498db'])
    st.plotly_chart(fig, use_container_width=True)

# 2. Revenue Trend (Time-Series Chart)
with info_row1[1]:
    st.subheader("2. Revenue & Volume Trend")
    revenue_trend = f_df.groupby('month')[['pharmacy_revenue', 'prescriptions_dispensed']].sum().reset_index()
    revenue_trend['month'] = revenue_trend['month'].astype(str)
    
    fig = px.line(revenue_trend.melt(id_vars='month'), x='month', y='value', color='variable',
                  title='Financial & Volume Trend',
                  color_discrete_sequence=['#2ecc71', '#9b59b6']) 
    st.plotly_chart(fig, use_container_width=True)

# 3. High-Cost Medication Analysis (Treemap)
with info_row1[2]:
    st.subheader("3. High-Cost Drug Utilization")
    high_cost_agg = f_df.groupby('high_cost_drug_name')['high_cost_drug_cost'].sum().reset_index()
    fig = px.treemap(high_cost_agg, path=['high_cost_drug_name'], values='high_cost_drug_cost',
                     title='Cost Contribution by High-Value Drug',
                     color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

# Row 2 (Infographs 4, 5, 6)
info_row2 = st.columns(3)

# 4. Avg Dispensing Time vs TAT (Bar Chart)
with info_row2[0]:
    st.subheader("4. Avg. Dispensing vs. TAT (Mins)")
    avg_dispensing = f_df['avg_dispensing_time'].mean()
    avg_tat = f_df['turnaround_time'].mean()
    time_data = pd.DataFrame({
        'Metric': ['Dispensing Time', 'Turnaround Time'],
        'Time (Mins)': [avg_dispensing, avg_tat]
    })
    fig = px.bar(time_data, x='Metric', y='Time (Mins)', 
                 title='Efficiency Breakdown',
                 color_discrete_sequence=['#34495e', '#f39c12']) 
    st.plotly_chart(fig, use_container_width=True)

# 5. Top Prescribed Drugs (Bar Chart)
with info_row2[1]:
    st.subheader("5. Top Prescribed Drugs (Volume)")
    top_drugs = f_df.groupby('top_drug_name')['top_drug_volume'].sum().nlargest(10).reset_index()
    fig = px.bar(top_drugs, x='top_drug_volume', y='top_drug_name', orientation='h',
                 title='Highest Volume Medications',
                 color='top_drug_volume', color_continuous_scale=px.colors.sequential.Electric)
    st.plotly_chart(fig, use_container_width=True)

# 6. Revenue Per User by Department (Bar Chart)
with info_row2[2]:
    st.subheader("6. Revenue Per User by Dept (INR)")
    rev_user_agg = f_df.groupby('department')['revenue_per_user'].mean().reset_index()
    fig = px.bar(rev_user_agg.sort_values(by='revenue_per_user', ascending=False),
                 x='department', y='revenue_per_user', 
                 title='Revenue Efficiency by Referring Department',
                 color='revenue_per_user', color_continuous_scale=px.colors.sequential.Sunset)
    st.plotly_chart(fig, use_container_width=True)

# === REUSABLE FOOTER ===
custom_footer()