"""
Financial Analysis & Valuation Visualization
Main Streamlit application.
"""
import streamlit as st
from data_processor import load_and_process_data
from visualizations import create_single_stock_chart, create_category_comparison_chart
from ui_components import (
    render_header,
    render_file_uploader,
    render_filters,
    render_stock_selector,
    render_category_selector,
    render_chart,
    render_data_table,
    show_error,
    show_warning,
    show_column_detection_error
)

# Page configuration
st.set_page_config(page_title="Financial Analysis Tool", layout="wide")

# Render header
render_header()

# File upload
uploaded_file = render_file_uploader()

if uploaded_file is not None:
    try:
        # Load and process data
        df, col_map, missing_cols = load_and_process_data(uploaded_file)
        
        if missing_cols:
            show_column_detection_error(missing_cols, df.columns.tolist())
            st.stop()
        
        # Render filters
        selected_year, mode = render_filters(df, col_map)
        
        # Filter by year
        year_df = df[df[col_map["Year"]] == selected_year]
        
        # Single Stock Mode
        if mode == "Single Stock":
            selected_stock = render_stock_selector(year_df, col_map)
            
            if not selected_stock:
                show_warning("Please select a stock.")
            else:
                stock_df = year_df[year_df[col_map["Symbol"]] == selected_stock]
                
                if stock_df.empty:
                    show_error(f"No data found for {selected_stock} in {selected_year}.")
                else:
                    stock_data = stock_df.iloc[0]
                    
                    # Visualization
                    st.subheader(f"Price Analysis for {selected_stock} ({selected_year})")
                    fig = create_single_stock_chart(stock_data, col_map, selected_stock, selected_year)
                    render_chart(fig)
                    
                    # Data table
                    render_data_table(stock_data.to_frame().T)
        
        # Category Comparison Mode
        elif mode == "Category Comparison":
            if col_map["Category"] is None:
                show_error("No 'Category' column detected in the CSV. Please ensure your file has a column named 'Category', 'Sector', 'Industry', or '分類'.")
            else:
                selected_category = render_category_selector(year_df, col_map)
                cat_df = year_df[year_df[col_map["Category"]] == selected_category]
                
                if cat_df.empty:
                    show_warning(f"No stocks found in category '{selected_category}'.")
                else:
                    # Visualization
                    st.subheader(f"Category Comparison: {selected_category} ({selected_year})")
                    fig = create_category_comparison_chart(cat_df, col_map, selected_category, selected_year)
                    render_chart(fig)
                    
                    # Data table
                    render_data_table(cat_df)
    
    except Exception as e:
        show_error(f"An error occurred while processing the file: {e}")
