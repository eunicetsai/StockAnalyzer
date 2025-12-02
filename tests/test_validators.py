"""
Test suite for validators module.
Tests validation functions for column checking, data quality, and CSV structure.
"""
import pytest
import pandas as pd
from stock_analyzer.validators import (
    COLUMN_NAMES,
    ValidationError,
    ValidationResult,
    validate_required_columns,
    validate_data_quality,
    validate_csv_structure
)


class TestValidationError:
    """Test ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test creating a ValidationError."""
        error = ValidationError("MISSING_COLUMN", "Fair", "Column missing", "Add column")
        assert error.error_type == "MISSING_COLUMN"
        assert error.field == "Fair"
        assert error.message == "Column missing"
        assert error.suggestion == "Add column"
    
    def test_validation_error_repr(self):
        """Test ValidationError string representation."""
        error = ValidationError("MISSING_COLUMN", "Fair", "Column missing")
        assert "MISSING_COLUMN" in repr(error)
        assert "Fair" in repr(error)


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating a ValidationResult."""
        result = ValidationResult()
        assert result.is_valid()
        assert not result.has_warnings()
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult()
        result.add_error("TEST_ERROR", "TestField", "Test message", "Test suggestion")
        
        assert not result.is_valid()
        assert len(result.errors) == 1
        assert result.errors[0].error_type == "TEST_ERROR"
        assert result.errors[0].field == "TestField"
    
    def test_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult()
        result.add_warning("TEST_WARNING", "TestField", "Test message")
        
        assert result.is_valid()  # Warnings don't affect validity
        assert result.has_warnings()
        assert len(result.warnings) == 1
    
    def test_multiple_errors(self):
        """Test multiple errors."""
        result = ValidationResult()
        result.add_error("ERROR1", "Field1", "Message1")
        result.add_error("ERROR2", "Field2", "Message2")
        
        assert not result.is_valid()
        assert len(result.errors) == 2


class TestValidateRequiredColumns:
    """Test validate_required_columns function."""
    
    def test_all_columns_present(self):
        """Test validation with all required columns present."""
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": "Category"
        }
        result = validate_required_columns(col_map)
        assert result.is_valid()
        assert len(result.errors) == 0
    
    def test_missing_fair_column(self):
        """Test validation with missing Fair column (合理價)."""
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": None,  # Missing
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": "Category"
        }
        result = validate_required_columns(col_map)
        
        assert not result.is_valid()
        assert len(result.errors) == 1
        assert result.errors[0].field == "Fair"
        assert "Fair Price (合理價)" in result.errors[0].message
        assert "Fair" in result.errors[0].suggestion or "合理" in result.errors[0].suggestion
    
    def test_missing_multiple_columns(self):
        """Test validation with multiple missing columns."""
        col_map = {
            "Year": "Year",
            "Symbol": None,  # Missing
            "Cheap": None,   # Missing
            "Fair": "Fair",
            "Expensive": None,  # Missing
            "Close": "Close",
            "Category": "Category"
        }
        result = validate_required_columns(col_map)
        
        assert not result.is_valid()
        assert len(result.errors) == 3
        fields = [e.field for e in result.errors]
        assert "Symbol" in fields
        assert "Cheap" in fields
        assert "Expensive" in fields
    
    def test_category_optional(self):
        """Test that Category column is optional."""
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": None  # Optional
        }
        result = validate_required_columns(col_map)
        assert result.is_valid()


class TestValidateDataQuality:
    """Test validate_data_quality function."""
    
    def test_valid_data(self):
        """Test validation with valid data."""
        df = pd.DataFrame({
            "Year": ["2023", "2023", "2024"],
            "Symbol": ["AAPL", "GOOGL", "MSFT"],
            "Cheap": [120.0, 90.0, 250.0],
            "Fair": [150.0, 110.0, 300.0],
            "Expensive": [180.0, 130.0, 350.0],
            "Close": [145.0, 108.0, 295.0]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": None
        }
        result = validate_data_quality(df, col_map)
        assert result.is_valid()
    
    def test_null_values_warning(self):
        """Test validation with null values."""
        df = pd.DataFrame({
            "Year": ["2023", "2023", "2024"],
            "Symbol": ["AAPL", "GOOGL", "MSFT"],
            "Cheap": [120.0, None, 250.0],
            "Fair": [150.0, 110.0, 300.0],
            "Expensive": [180.0, 130.0, 350.0],
            "Close": [145.0, 108.0, None]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": None
        }
        result = validate_data_quality(df, col_map)
        
        # Should have warnings but still be valid
        assert result.is_valid()
        assert result.has_warnings()
    
    def test_all_null_values_error(self):
        """Test validation with all null values in a column."""
        df = pd.DataFrame({
            "Year": ["2023", "2023", "2024"],
            "Symbol": ["AAPL", "GOOGL", "MSFT"],
            "Cheap": [120.0, 90.0, 250.0],
            "Fair": [None, None, None],  # All null
            "Expensive": [180.0, 130.0, 350.0],
            "Close": [145.0, 108.0, 295.0]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": None
        }
        result = validate_data_quality(df, col_map)
        
        assert not result.is_valid()
        assert any(e.field == "Fair" for e in result.errors)
    
    def test_duplicate_entries_warning(self):
        """Test validation with duplicate stock entries."""
        df = pd.DataFrame({
            "Year": ["2023", "2023", "2023"],
            "Symbol": ["AAPL", "AAPL", "GOOGL"],  # AAPL duplicated in 2023
            "Cheap": [120.0, 125.0, 90.0],
            "Fair": [150.0, 155.0, 110.0],
            "Expensive": [180.0, 185.0, 130.0],
            "Close": [145.0, 150.0, 108.0]
        })
        col_map = {
            "Year": "Year",
            "Symbol": "Symbol",
            "Cheap": "Cheap",
            "Fair": "Fair",
            "Expensive": "Expensive",
            "Close": "Close",
            "Category": None
        }
        result = validate_data_quality(df, col_map)
        
        assert result.is_valid()  # Duplicates are warnings, not errors
        assert result.has_warnings()
        assert any(w.field == "Symbol" for w in result.warnings)


class TestValidateCSVStructure:
    """Test validate_csv_structure function."""
    
    def test_valid_structure(self):
        """Test validation with valid CSV structure."""
        df = pd.DataFrame({
            "Year": ["2023"],
            "Symbol": ["AAPL"],
            "Close": [145.0]
        })
        result = validate_csv_structure(df)
        assert result.is_valid()
    
    def test_empty_dataframe(self):
        """Test validation with empty DataFrame."""
        df = pd.DataFrame()
        result = validate_csv_structure(df)
        
        assert not result.is_valid()
        assert len(result.errors) == 1
        assert result.errors[0].error_type == "EMPTY_FILE"
    
    def test_no_columns(self):
        """Test validation with no columns."""
        df = pd.DataFrame()
        result = validate_csv_structure(df)
        
        assert not result.is_valid()
    
    def test_no_data_rows(self):
        """Test validation with columns but no data."""
        df = pd.DataFrame(columns=["Year", "Symbol", "Close"])
        result = validate_csv_structure(df)
        
        assert not result.is_valid()
        # Empty DataFrame is caught by the empty check
        assert any(e.error_type == "EMPTY_FILE" for e in result.errors)


class TestColumnNames:
    """Test COLUMN_NAMES configuration."""
    
    def test_all_fields_present(self):
        """Test that all expected fields are in COLUMN_NAMES."""
        expected_fields = ["Year", "Symbol", "Cheap", "Fair", "Expensive", "Close", "Category"]
        for field in expected_fields:
            assert field in COLUMN_NAMES
    
    def test_keywords_present(self):
        """Test that each field has keywords."""
        for field, config in COLUMN_NAMES.items():
            assert "keywords" in config
            assert len(config["keywords"]) > 0
    
    def test_display_names_present(self):
        """Test that each field has display name."""
        for field, config in COLUMN_NAMES.items():
            assert "display" in config
            assert len(config["display"]) > 0
    
    def test_chinese_keywords_present(self):
        """Test that Chinese keywords are present."""
        # Check Fair column has 合理
        assert "合理" in COLUMN_NAMES["Fair"]["keywords"]
        # Check Year has 年度
        assert "年度" in COLUMN_NAMES["Year"]["keywords"]
