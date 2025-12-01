"""
Test suite for data_processor module.
Tests data loading, column mapping, cleaning, and processing functions.
"""
import pytest
import pandas as pd
import os
from io import StringIO
from financial_analysis.data_processor import (
    clean_currency,
    find_column,
    map_columns,
    clean_data,
    load_and_process_data
)


class TestCleanCurrency:
    """Test clean_currency function."""
    
    def test_clean_dollar_sign(self):
        """Test cleaning dollar sign from currency."""
        assert clean_currency("$150.50") == 150.50
    
    def test_clean_comma(self):
        """Test cleaning comma from currency."""
        assert clean_currency("1,234.56") == 1234.56
    
    def test_clean_multiple_symbols(self):
        """Test cleaning multiple symbols."""
        assert clean_currency("$1,234.56") == 1234.56
    
    def test_negative_value(self):
        """Test cleaning negative value."""
        assert clean_currency("-150.50") == -150.50
    
    def test_numeric_input(self):
        """Test with numeric input (should pass through)."""
        assert clean_currency(150.50) == 150.50
    
    def test_invalid_string(self):
        """Test with invalid string."""
        result = clean_currency("invalid")
        assert result is None
    
    def test_empty_string(self):
        """Test with empty string."""
        result = clean_currency("")
        assert result is None


class TestFindColumn:
    """Test find_column function."""
    
    def test_exact_match(self):
        """Test exact keyword match."""
        columns = ["Year", "Symbol", "Close"]
        result = find_column(["Year"], columns)
        assert result == "Year"
    
    def test_partial_match(self):
        """Test partial keyword match."""
        columns = ["Year", "Symbol", "Closing Price"]
        result = find_column(["Closing"], columns)
        assert result == "Closing Price"
    
    def test_chinese_match(self):
        """Test Chinese keyword match."""
        columns = ["年度", "代號", "收盤價"]
        result = find_column(["年度"], columns)
        assert result == "年度"
    
    def test_multiple_keywords(self):
        """Test with multiple keywords."""
        columns = ["Year", "Symbol", "Close"]
        result = find_column(["Fair", "合理", "Year"], columns)
        assert result == "Year"
    
    def test_no_match(self):
        """Test when no match found."""
        columns = ["Year", "Symbol", "Close"]
        result = find_column(["Fair", "合理"], columns)
        assert result is None
    
    def test_exclude_pattern(self):
        """Test with exclude pattern."""
        columns = ["Close Date", "Closing Price"]
        result = find_column(["Closing"], columns, exclude=["Date"])
        assert result == "Closing Price"
    
    def test_first_match_returned(self):
        """Test that first match is returned."""
        columns = ["Fair Price", "Fair Value", "Symbol"]
        result = find_column(["Fair"], columns)
        assert result == "Fair Price"


class TestMapColumns:
    """Test map_columns function."""
    
    def test_english_columns(self):
        """Test mapping with English column names."""
        df = pd.DataFrame(columns=["Year", "Symbol", "Cheap", "Fair", "Expensive", "Close", "Category"])
        col_map = map_columns(df)
        
        assert col_map["Year"] == "Year"
        assert col_map["Symbol"] == "Symbol"
        assert col_map["Cheap"] == "Cheap"
        assert col_map["Fair"] == "Fair"
        assert col_map["Expensive"] == "Expensive"
        assert col_map["Close"] == "Close"
        assert col_map["Category"] == "Category"
    
    def test_chinese_columns(self):
        """Test mapping with Chinese column names."""
        df = pd.DataFrame(columns=["年度", "代號", "便宜價", "合理價", "昂貴價", "收盤價", "分類"])
        col_map = map_columns(df)
        
        assert col_map["Year"] == "年度"
        assert col_map["Symbol"] == "代號"
        assert col_map["Cheap"] == "便宜價"
        assert col_map["Fair"] == "合理價"
        assert col_map["Expensive"] == "昂貴價"
        assert col_map["Close"] == "收盤價"
        assert col_map["Category"] == "分類"
    
    def test_mixed_columns(self):
        """Test mapping with mixed English/Chinese names."""
        df = pd.DataFrame(columns=["Year", "代號", "Cheap", "合理價", "Expensive", "收盤價"])
        col_map = map_columns(df)
        
        assert col_map["Year"] == "Year"
        assert col_map["Symbol"] == "代號"
        assert col_map["Cheap"] == "Cheap"
        assert col_map["Fair"] == "合理價"
        assert col_map["Expensive"] == "Expensive"
        assert col_map["Close"] == "收盤價"
    
    def test_missing_columns(self):
        """Test mapping with missing columns."""
        df = pd.DataFrame(columns=["Year", "Symbol"])
        col_map = map_columns(df)
        
        assert col_map["Year"] == "Year"
        assert col_map["Symbol"] == "Symbol"
        assert col_map["Cheap"] is None
        assert col_map["Fair"] is None
        assert col_map["Expensive"] is None
        assert col_map["Close"] is None
    
    def test_alternative_names(self):
        """Test mapping with alternative column names."""
        df = pd.DataFrame(columns=["Year", "Stock", "Cheap", "Fair", "Expensive", "Closing Price", "Sector"])
        col_map = map_columns(df)
        
        assert col_map["Symbol"] == "Stock"
        assert col_map["Close"] == "Closing Price"
        assert col_map["Category"] == "Sector"


class TestCleanData:
    """Test clean_data function."""
    
    def test_clean_year(self):
        """Test cleaning year column."""
        df = pd.DataFrame({
            "Year": [2023.0, 2024.0],
            "Symbol": ["AAPL", "GOOGL"],
            "Cheap": [120.0, 90.0],
            "Fair": [150.0, 110.0],
            "Expensive": [180.0, 130.0],
            "Close": [145.0, 108.0]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close"
        }
        
        cleaned_df = clean_data(df, col_map)
        assert cleaned_df["Year"].dtype == object
        assert cleaned_df["Year"].iloc[0] == "2023"
        assert cleaned_df["Year"].iloc[1] == "2024"
    
    def test_clean_symbol(self):
        """Test cleaning symbol column."""
        df = pd.DataFrame({
            "Year": ["2023"],
            "Symbol": [" AAPL "],  # With spaces
            "Cheap": [120.0],
            "Fair": [150.0],
            "Expensive": [180.0],
            "Close": [145.0]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close"
        }
        
        cleaned_df = clean_data(df, col_map)
        assert cleaned_df["Symbol"].iloc[0] == "AAPL"
    
    def test_clean_prices(self):
        """Test cleaning price columns."""
        df = pd.DataFrame({
            "Year": ["2023"],
            "Symbol": ["AAPL"],
            "Cheap": ["$120.50"],
            "Fair": ["$150.00"],
            "Expensive": ["$180.25"],
            "Close": ["$145.30"]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close"
        }
        
        cleaned_df = clean_data(df, col_map)
        assert cleaned_df["Cheap"].iloc[0] == 120.50
        assert cleaned_df["Fair"].iloc[0] == 150.00
        assert cleaned_df["Expensive"].iloc[0] == 180.25
        assert cleaned_df["Close"].iloc[0] == 145.30


class TestLoadAndProcessData:
    """Test load_and_process_data function."""
    
    @pytest.fixture
    def fixture_path(self):
        """Get path to test fixtures directory."""
        return os.path.join(os.path.dirname(__file__), "fixtures")
    
    def test_load_valid_data(self, fixture_path):
        """Test loading valid CSV data."""
        file_path = os.path.join(fixture_path, "valid_data.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        assert df is not None
        assert col_map is not None
        assert validation_result.is_valid()
        assert len(df) == 8  # 8 rows in valid_data.csv
    
    def test_load_missing_fair_column(self, fixture_path):
        """Test loading CSV with missing Fair column."""
        file_path = os.path.join(fixture_path, "missing_fair_column.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        assert df is None
        assert not validation_result.is_valid()
        assert any(e.field == "Fair" for e in validation_result.errors)
    
    def test_load_missing_multiple_columns(self, fixture_path):
        """Test loading CSV with multiple missing columns."""
        file_path = os.path.join(fixture_path, "missing_multiple_columns.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        assert df is None
        assert not validation_result.is_valid()
        assert len(validation_result.errors) > 1
    
    def test_load_null_values(self, fixture_path):
        """Test loading CSV with null values."""
        file_path = os.path.join(fixture_path, "null_values.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        # Should load successfully but with warnings
        assert df is not None
        assert validation_result.is_valid()
        assert validation_result.has_warnings()
    
    def test_load_duplicate_entries(self, fixture_path):
        """Test loading CSV with duplicate entries."""
        file_path = os.path.join(fixture_path, "duplicate_entries.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        # Should load successfully but with warnings
        assert df is not None
        assert validation_result.is_valid()
        assert validation_result.has_warnings()
        assert any(w.field == "Symbol" for w in validation_result.warnings)
    
    def test_load_chinese_columns(self, fixture_path):
        """Test loading CSV with Chinese column names."""
        file_path = os.path.join(fixture_path, "chinese_columns.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        assert df is not None
        assert validation_result.is_valid()
        assert col_map["Year"] == "年度"
        assert col_map["Symbol"] == "代號"
        assert col_map["Fair"] == "合理價"
    
    def test_load_invalid_file(self):
        """Test loading invalid file."""
        invalid_csv = StringIO("not,a,valid\ncsv,file")
        
        df, col_map, validation_result = load_and_process_data(invalid_csv)
        
        # Should fail validation due to missing required columns
        assert df is None
        assert not validation_result.is_valid()
    
    def test_column_mapping_returned(self, fixture_path):
        """Test that column mapping is returned correctly."""
        file_path = os.path.join(fixture_path, "valid_data.csv")
        
        with open(file_path, 'rb') as f:
            df, col_map, validation_result = load_and_process_data(f)
        
        assert "Year" in col_map
        assert "Symbol" in col_map
        assert "Fair" in col_map
        assert col_map["Year"] is not None
        assert col_map["Symbol"] is not None
        assert col_map["Fair"] is not None
