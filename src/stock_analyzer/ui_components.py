"""
UI components module for financial analysis.
Handles Streamlit UI elements and user interactions.
"""
import streamlit as st
from validators import ValidationResult


def render_header():
    """Render app header and description."""
    st.title("Financial Analysis & Valuation Visualization")
    st.markdown("""
    Upload your CSV file containing financial data. 
    The app expects columns for **Year**, **Stock Symbol**, **Cheap Price**, **Fair Price**, **Expensive Price**, and **Closing Price**.
    """)


def render_file_uploader():
    """Render file upload widget."""
    return st.file_uploader("Upload CSV File", type=["csv"])


def render_filters(df, col_map):
    """Render sidebar filters and return selections."""
    st.sidebar.header("Filters")
    
    # Year Filter
    years = sorted(df[col_map["Year"]].unique())
    selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
    
    # Analysis Mode
    mode = st.sidebar.radio("Analysis Mode", ["Single Stock", "Category Comparison"])
    
    return selected_year, mode


def render_stock_selector(year_df, col_map):
    """Render stock selection dropdown."""
    all_stocks = sorted(year_df[col_map["Symbol"]].unique())
    return st.sidebar.selectbox("Select Stock", all_stocks)


def render_category_selector(year_df, col_map):
    """Render category selection dropdown."""
    categories = sorted(year_df[col_map["Category"]].astype(str).unique())
    return st.sidebar.selectbox("Select Category", categories)


def render_chart(fig):
    """Render Plotly chart."""
    st.plotly_chart(fig, use_container_width=True)


def render_data_table(data, title="Detailed Data"):
    """Render data table."""
    st.subheader(title)
    st.dataframe(data)


def show_error(message):
    """Display error message."""
    st.error(message)


def show_warning(message):
    """Display warning message."""
    st.warning(message)


def show_info(message):
    """Display info message."""
    st.info(message)


def show_validation_errors(validation_result: ValidationResult, detected_columns=None):
    """
    Display detailed validation errors and warnings.
    
    Args:
        validation_result: ValidationResult object containing errors and warnings
        detected_columns: Optional list of detected column names from the CSV
    """
    # Display errors
    if validation_result.errors:
        st.error("❌ **Validation Errors Found**")
        st.markdown("The following issues must be fixed before proceeding:")
        
        for i, error in enumerate(validation_result.errors, 1):
            with st.expander(f"Error {i}: {error.field}", expanded=True):
                st.markdown(f"**Issue:** {error.message}")
                if error.suggestion:
                    st.markdown(f"**Solution:** {error.suggestion}")
        
        # Show detected columns if available
        if detected_columns:
            st.markdown("---")
            st.markdown("**Columns found in your CSV file:**")
            st.code(", ".join(detected_columns))
    
    # Display warnings
    if validation_result.warnings:
        st.warning("⚠️ **Validation Warnings**")
        st.markdown("The following issues were detected but won't prevent analysis:")
        
        for i, warning in enumerate(validation_result.warnings, 1):
            with st.expander(f"Warning {i}: {warning.field}", expanded=False):
                st.markdown(f"**Issue:** {warning.message}")
                if warning.suggestion:
                    st.markdown(f"**Note:** {warning.suggestion}")


# Deprecated - keeping for backward compatibility
def show_column_detection_error(missing_cols, detected_cols):
    """
    Display column detection error with details.
    DEPRECATED: Use show_validation_errors instead.
    """
    st.error(f"Could not identify the following columns: {', '.join(missing_cols)}")
    st.write("Detected columns:", detected_cols)
