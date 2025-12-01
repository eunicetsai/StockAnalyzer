"""
UI components module for financial analysis.
Handles Streamlit UI elements and user interactions.
"""
import streamlit as st


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


def show_column_detection_error(missing_cols, detected_cols):
    """Display column detection error with details."""
    st.error(f"Could not identify the following columns: {', '.join(missing_cols)}")
    st.write("Detected columns:", detected_cols)
