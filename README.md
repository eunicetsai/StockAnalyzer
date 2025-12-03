# Stock Analyzer

A Streamlit application for analyzing and visualizing financial data with comprehensive data validation, supporting both English and Chinese column names.

## Features

- 📊 **Interactive Visualizations**: Single stock analysis and category comparison charts
- ✅ **Comprehensive Validation**: Detailed error messages for missing columns and data quality issues
- 🌐 **Multi-language Support**: Works with both English and Chinese column names (年度, 代號, 合理價, etc.)
- 🧪 **Well-tested**: 52 test cases with high code coverage
- 📈 **Price Analysis**: Compare cheap, fair, and expensive prices with closing prices

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stock-analyzer
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

1. Change directory to the application source code
```bash
cd src/stock_analyzer
```

2. Start the Streamlit application
```bash
python3 -m streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### CSV File Format

Your CSV file should contain the following columns (English or Chinese names):

| English | Chinese | Required |
|---------|---------|----------|
| Year | 年度 | ✅ |
| Symbol | 代號/股票 | ✅ |
| Cheap | 便宜價 | ✅ |
| Fair | 合理價 | ✅ |
| Expensive | 昂貴價 | ✅ |
| Close | 收盤價 | ✅ |
| Category | 分類/類別/產業 | ❌ |

**Example CSV:**
```csv
Year,Symbol,Category,Cheap,Fair,Expensive,Close
2023,AAPL,Technology,120.50,150.00,180.25,145.30
2023,GOOGL,Technology,90.00,110.50,130.00,108.75
```

## Running Tests

Run all tests:
```bash
pytest tests/ -v
```
Run with coverage report:
```bash
pytest tests/ --cov=src/stock_analyzer --cov-report=term-missing
```
Run a specific test file:
```bash
pytest tests/test_validators.py -v
```

## Project Structure

```
stock-analyzer/
├── src/
│   └── stock_analyzer/          # Main package
│       ├── __init__.py          # Package initialization
│       ├── app.py               # Streamlit application
│       ├── validators.py        # Data validation module
│       ├── data_processor.py    # Data loading and processing
│       ├── ui_components.py     # UI components
│       └── visualizations.py    # Chart generation
├── tests/
│   ├── __init__.py
│   ├── fixtures/                # Test data files
│   ├── test_validators.py       # Validator tests
│   └── test_data_processor.py   # Data processor tests
├── .gitignore                   # Git ignore rules
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Python dependencies
├── __main__.py                  # Application entry point
└── README.md                    # This file
```

## Data Validation

The application provides comprehensive validation with detailed error messages.

### Missing Column Example
```
❌ Validation Errors Found

Error 1: Fair
  Issue: Required column 'Fair Price (合理價)' is missing from the CSV file.
  Solution: Please ensure your CSV file contains a column with one of these names: Fair, 合理
```

### Data Quality Warnings
- Null values detection with percentage thresholds
- Invalid data type detection
- Duplicate entry warnings

## Development

### Adding New Features
1. Add code to the appropriate module in `src/stock_analyzer/`
2. Write tests in `tests/`
3. Run tests to ensure nothing breaks
4. Update documentation

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
