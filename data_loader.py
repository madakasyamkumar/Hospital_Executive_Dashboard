# --- File: data_loader.py ---

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# --- 1. Data Loading and Caching ---

@st.cache_data
def load_and_transform_data():
    """
    Loads all four CSV files, converts the 'date' column, and ensures data 
    is prepared for use across the multi-page application.
    """
    
    # CRITICAL PATHING FIX: Determine the project's root path reliably.
    try:
        # Check if running in a multipage context (like dashboard_app.py)
        # If so, the files are relative to the directory where this script resides.
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_folder = os.path.join(base_path, 'data')
    except NameError:
        # Fallback for complex environments
        data_folder = 'data'
    
    # 1. Load Data (using the simplified names)
    try:
        clinical_df = pd.read_csv(os.path.join(data_folder, "clinical_data.csv"))
        hr_df = pd.read_csv(os.path.join(data_folder, "hr_data.csv"))
        lab_df = pd.read_csv(os.path.join(data_folder, "laboratory_data.csv"))
        pharmacy_df = pd.read_csv(os.path.join(data_folder, "pharmacy_data.csv"))
    except FileNotFoundError as e:
        st.error(f"Error: Required file not found. Ensure all four CSVs are in the 'data/' folder. Missing: {e.filename.split(os.sep)[-1]}")
        return None

    # 2. Critical Data Transformation
    date_format = '%d-%b-%Y'
    dataframes = {
        'clinical': clinical_df, 
        'hr': hr_df, 
        'lab': lab_df, 
        'pharmacy': pharmacy_df
    }

    for key, df in dataframes.items():
        df['date'] = pd.to_datetime(df['date'], format=date_format)
        df['month'] = df['date'].dt.to_period('M')
        if 'department' in df.columns:
            df['department'] = df['department'].str.strip()

    return dataframes

DATA = load_and_transform_data()

# --- 2. Utility Function for Global Filtering ---

def apply_filters(df, start_date, end_date, selected_department):
    """Applies global date and department filters."""
    filtered_df = df[
        (df['date'] >= start_date) & 
        (df['date'] <= end_date)
    ].copy()
    
    if selected_department != 'ALL DEPARTMENTS':
        filtered_df = filtered_df[filtered_df['department'] == selected_department]
        
    return filtered_df