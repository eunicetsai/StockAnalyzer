"""
Data validation module for financial analysis.
Provides comprehensive validation for CSV data and columns.
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional


# Column name mappings (English/Chinese)
COLUMN_NAMES = {
    "Year": {
        "keywords": ["Year", "年度"],
        "display": "Year (年度)"
    },
    "Category": {
        "keywords": ["Category", "Sector", "Industry", "分類", "類別", "產業"],
        "display": "Category (分類/類別/產業)",
        "required": False
    },
    "Symbol": {
        "keywords": ["Symbol", "Stock", "代號", "股票"],
        "display": "Symbol (代號/股票)"
    },
    "Cheap": {
        "keywords": ["Cheap", "便宜"],
        "display": "Cheap Price (便宜價)"
    },
    "Fair": {
        "keywords": ["Fair", "合理"],
        "display": "Fair Price (合理價)"
    },
    "Expensive": {
        "keywords": ["Expensive", "昂貴"],
        "display": "Expensive Price (昂貴價)"
    },
    "Close": {
        "keywords": ["Closing Price", "Close Price", "收盤價", "Close", "Closing", "收盤"],
        "display": "Closing Price (收盤價)",
        "exclude": ["Date", "日期"]
    },
    "CloseDate": {
        "keywords": ["Close Date", "Closing Date", "收盤日期", "日期", "Date"],
        "display": "Close Date (收盤日期)",
        "required": False
    }
}


class ValidationError:
    """Represents a validation error with detailed information."""
    
    def __init__(self, error_type: str, field: str, message: str, suggestion: str = ""):
        self.error_type = error_type
        self.field = field
        self.message = message
        self.suggestion = suggestion
    
    def __repr__(self):
        return f"ValidationError({self.error_type}, {self.field})"


class ValidationResult:
    """Contains validation results and errors."""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def add_error(self, error_type: str, field: str, message: str, suggestion: str = ""):
        """Add a validation error."""
        self.errors.append(ValidationError(error_type, field, message, suggestion))
    
    def add_warning(self, error_type: str, field: str, message: str, suggestion: str = ""):
        """Add a validation warning."""
        self.warnings.append(ValidationError(error_type, field, message, suggestion))
    
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


def validate_required_columns(col_map: Dict[str, Optional[str]]) -> ValidationResult:
    """
    Validate that all required columns are present.
    
    Args:
        col_map: Dictionary mapping field names to actual column names
        
    Returns:
        ValidationResult with any errors found
    """
    result = ValidationResult()
    
    for field, config in COLUMN_NAMES.items():
        # Check if field is required (default is True unless specified)
        is_required = config.get("required", True)
        
        if is_required and col_map.get(field) is None:
            # Column is missing
            display_name = config["display"]
            keywords = config["keywords"]
            
            message = f"Required column '{display_name}' is missing from the CSV file."
            suggestion = f"Please ensure your CSV file contains a column with one of these names: {', '.join(keywords)}"
            
            result.add_error("MISSING_COLUMN", field, message, suggestion)
    
    return result


def validate_data_quality(df: pd.DataFrame, col_map: Dict[str, Optional[str]]) -> ValidationResult:
    """
    Validate data quality (null values, data types, ranges).
    
    Args:
        df: DataFrame to validate
        col_map: Dictionary mapping field names to actual column names
        
    Returns:
        ValidationResult with any errors or warnings found
    """
    result = ValidationResult()
    
    # Check for null values in required columns
    for field, col_name in col_map.items():
        if col_name is None:
            continue
            
        null_count = df[col_name].isnull().sum()
        total_rows = len(df)
        
        if null_count > 0:
            display_name = COLUMN_NAMES[field]["display"]
            percentage = (null_count / total_rows) * 100
            
            message = f"Column '{display_name}' has {null_count} null values ({percentage:.1f}% of data)."
            
            if null_count == total_rows:
                # All values are null - this is an error
                suggestion = "This column appears to be completely empty. Please check your data file."
                result.add_error("NULL_VALUES", field, message, suggestion)
            elif percentage > 50:
                # More than 50% null - warning
                suggestion = "More than half of the values are missing. This may affect analysis accuracy."
                result.add_warning("NULL_VALUES", field, message, suggestion)
            elif percentage > 10:
                # More than 10% null - warning
                suggestion = "Some values are missing. These rows will be excluded from analysis."
                result.add_warning("NULL_VALUES", field, message, suggestion)
    
    # Validate numeric columns (prices)
    price_fields = ["Cheap", "Fair", "Expensive", "Close"]
    for field in price_fields:
        col_name = col_map.get(field)
        if col_name is None:
            continue
        
        # Check if values can be converted to numeric
        non_null_values = df[col_name].dropna()
        if len(non_null_values) > 0:
            # Try to identify non-numeric values
            try:
                # This will be done after cleaning, so we just check for negative values
                numeric_values = pd.to_numeric(non_null_values, errors='coerce')
                invalid_count = numeric_values.isnull().sum()
                
                if invalid_count > 0:
                    display_name = COLUMN_NAMES[field]["display"]
                    message = f"Column '{display_name}' contains {invalid_count} non-numeric values."
                    suggestion = "Price values should be numeric. Please check for invalid entries."
                    result.add_warning("INVALID_DATA_TYPE", field, message, suggestion)
            except Exception:
                pass
    
    # Check for duplicate stock symbols within the same year
    if col_map.get("Symbol") and col_map.get("Year"):
        duplicates = df.groupby([col_map["Year"], col_map["Symbol"]]).size()
        duplicates = duplicates[duplicates > 1]
        
        if len(duplicates) > 0:
            message = f"Found {len(duplicates)} duplicate stock entries (same symbol and year)."
            suggestion = "Each stock should appear only once per year. Duplicate entries may cause incorrect analysis."
            result.add_warning("DUPLICATE_DATA", "Symbol", message, suggestion)
    
    return result


def validate_csv_structure(df: pd.DataFrame) -> ValidationResult:
    """
    Validate basic CSV structure.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        ValidationResult with any errors found
    """
    result = ValidationResult()
    
    # Check if DataFrame is empty
    if df.empty:
        result.add_error("EMPTY_FILE", "CSV", "The uploaded CSV file is empty.", 
                        "Please upload a file with data.")
        return result
    
    # Check if there are any columns
    if len(df.columns) == 0:
        result.add_error("NO_COLUMNS", "CSV", "The uploaded CSV file has no columns.",
                        "Please ensure the file is properly formatted.")
        return result
    
    # Check for minimum number of rows
    if len(df) < 1:
        result.add_error("INSUFFICIENT_DATA", "CSV", "The uploaded CSV file has no data rows.",
                        "Please ensure the file contains at least one row of data.")
    
    return result
