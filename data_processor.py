"""
Data processing module for financial analysis.
Handles CSV loading, column mapping, and data cleaning.
"""
import pandas as pd
import re
from validators import (
    COLUMN_NAMES,
    ValidationResult,
    validate_csv_structure,
    validate_required_columns,
    validate_data_quality
)


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
    
    col_map = {}
    for field, config in COLUMN_NAMES.items():
        keywords = config["keywords"]
        exclude = config.get("exclude", None)
        col_map[field] = find_column(keywords, columns, exclude)
    
    return col_map


def clean_data(df, col_map):
    """Clean and standardize data types."""
    # Year as string
    if col_map["Year"]:
        df[col_map["Year"]] = df[col_map["Year"]].astype(str).str.replace(r'\.0$', '', regex=True)
    
    # Symbol as string, stripped
    if col_map["Symbol"]:
        df[col_map["Symbol"]] = df[col_map["Symbol"]].astype(str).str.strip()
    
    # Clean price columns
    price_fields = ["Cheap", "Fair", "Expensive", "Close"]
    for field in price_fields:
        col_name = col_map.get(field)
        if col_name:
            df[col_name] = df[col_name].apply(clean_currency)
    
    return df


def load_and_process_data(uploaded_file):
    """
    Main function to load and process uploaded CSV file.
    
    Returns:
        Tuple of (df, col_map, validation_result)
        - df: Processed DataFrame (None if validation failed)
        - col_map: Column mapping dictionary
        - validation_result: ValidationResult object with errors/warnings
    """
    # Load CSV
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        result = ValidationResult()
        result.add_error("FILE_READ_ERROR", "CSV", 
                        f"Failed to read CSV file: {str(e)}",
                        "Please ensure the file is a valid CSV format.")
        return None, None, result
    
    # Validate CSV structure
    validation_result = validate_csv_structure(df)
    if not validation_result.is_valid():
        return None, None, validation_result
    
    # Map columns
    col_map = map_columns(df)
    
    # Validate required columns
    column_validation = validate_required_columns(col_map)
    if not column_validation.is_valid():
        return None, col_map, column_validation
    
    # Clean data
    df = clean_data(df, col_map)
    
    # Validate data quality
    quality_validation = validate_data_quality(df, col_map)
    
    # Combine validation results
    validation_result.errors.extend(quality_validation.errors)
    validation_result.warnings.extend(quality_validation.warnings)
    
    # Return data even if there are warnings (but not errors)
    if not validation_result.is_valid():
        return None, col_map, validation_result
    
    return df, col_map, validation_result
