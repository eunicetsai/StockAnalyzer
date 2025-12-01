"""
Data processing module for financial analysis.
Handles CSV loading, column mapping, and data cleaning.
"""
import pandas as pd
import re


def clean_currency(x):
    """Remove currency symbols and convert to float."""
    if isinstance(x, str):
        clean_str = re.sub(r'[^\d\.-]', '', x)
        try:
            return float(clean_str)
        except ValueError:
            return None
    return x


def find_column(keywords, columns, exclude=None):
    """Find column by matching keywords, with optional exclusions."""
    for col in columns:
        if exclude and any(ex in col for ex in exclude):
            continue
        for kw in keywords:
            if kw in col:
                return col
    return None


def map_columns(df):
    """Auto-detect and map CSV columns to expected fields."""
    columns = df.columns.tolist()
    
    col_map = {
        "Year": find_column(["Year", "年度"], columns),
        "Category": find_column(["Category", "Sector", "Industry", "分類", "類別", "產業"], columns),
        "Symbol": find_column(["Symbol", "Stock", "代號", "股票"], columns),
        "Cheap": find_column(["Cheap", "便宜"], columns),
        "Fair": find_column(["Fair", "合理"], columns),
        "Expensive": find_column(["Expensive", "昂貴"], columns),
        "Close": find_column(
            ["Closing Price", "Close Price", "收盤價", "Close", "Closing", "收盤"], 
            columns, 
            exclude=["Date", "日期"]
        )
    }
    
    return col_map


def validate_columns(col_map):
    """Check if required columns are present."""
    missing = [k for k, v in col_map.items() if v is None and k != "Category"]
    return missing


def clean_data(df, col_map):
    """Clean and standardize data types."""
    # Year as string
    df[col_map["Year"]] = df[col_map["Year"]].astype(str).str.replace(r'\.0$', '', regex=True)
    
    # Symbol as string, stripped
    df[col_map["Symbol"]] = df[col_map["Symbol"]].astype(str).str.strip()
    
    # Clean price columns
    price_cols = [col_map["Cheap"], col_map["Fair"], col_map["Expensive"], col_map["Close"]]
    for col in price_cols:
        df[col] = df[col].apply(clean_currency)
    
    return df


def load_and_process_data(uploaded_file):
    """Main function to load and process uploaded CSV file."""
    df = pd.read_csv(uploaded_file)
    col_map = map_columns(df)
    missing = validate_columns(col_map)
    
    if missing:
        return None, col_map, missing
    
    df = clean_data(df, col_map)
    return df, col_map, None
