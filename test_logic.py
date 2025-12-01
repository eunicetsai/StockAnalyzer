import pandas as pd
import re

def clean_currency(x):
    if isinstance(x, str):
        clean_str = re.sub(r'[^\d\.-]', '', x)
        try:
            return float(clean_str)
        except ValueError:
            return None
    return x

def test_logic():
    print("Loading test data...")
    df = pd.read_csv('/Users/eunicetsai/.gemini/antigravity/scratch/financial_analysis/test_data.csv')
    
    columns = df.columns.tolist()
    print(f"Columns: {columns}")
    
    col_map = {
        "Year": "Year",
        "Symbol": "Stock Symbol",
        "Cheap": "Cheap Price",
        "Fair": "Fair Price",
        "Expensive": "Expensive Price",
        "Close": "Closing Price"
    }
    
    # Clean
    price_cols = [col_map["Cheap"], col_map["Fair"], col_map["Expensive"], col_map["Close"]]
    for col in price_cols:
        df[col] = df[col].apply(clean_currency)
        
    print("Data after cleaning:")
    print(df)
    
    # Check values
    assert df.loc[0, "Cheap Price"] == 100.0
    assert df.loc[0, "Closing Price"] == 145.5
    assert df.loc[1, "Cheap Price"] == 80.0
    
    print("Verification successful!")

if __name__ == "__main__":
    test_logic()
