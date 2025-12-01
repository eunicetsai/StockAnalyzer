import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

st.set_page_config(page_title="Financial Analysis Tool", layout="wide")

st.title("Financial Analysis & Valuation Visualization")
st.markdown("""
Upload your CSV file containing financial data. 
The app expects columns for **Year**, **Stock Symbol**, **Cheap Price**, **Fair Price**, **Expensive Price**, and **Closing Price**.
""")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

def clean_currency(x):
    if isinstance(x, str):
        # Remove currency symbols and commas
        clean_str = re.sub(r'[^\d\.-]', '', x)
        try:
            return float(clean_str)
        except ValueError:
            return None
    return x

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # --- Column Mapping ---
        columns = df.columns.tolist()
        
        def find_col(keywords, cols, exclude=None):
            for col in cols:
                # Check exclusions
                if exclude:
                    if any(ex in col for ex in exclude):
                        continue
                
                for kw in keywords:
                    if kw in col:
                        return col
            return None

        # Auto-Mapping with stricter rules
        # We prioritize exact matches or "Price"/"價" to avoid "Date"/"日期"
        col_map = {
            "Year": find_col(["Year", "年度"], columns),
            "Category": find_col(["Category", "Sector", "Industry", "分類", "類別", "產業"], columns),
            "Symbol": find_col(["Symbol", "Stock", "代號", "股票"], columns),
            "Cheap": find_col(["Cheap", "便宜"], columns),
            "Fair": find_col(["Fair", "合理"], columns),
            "Expensive": find_col(["Expensive", "昂貴"], columns),
            # Exclude "Date" and "日期" for Closing Price
            "Close": find_col(["Closing Price", "Close Price", "收盤價", "Close", "Closing", "收盤"], columns, exclude=["Date", "日期"])
        }
        
        missing_cols = [k for k, v in col_map.items() if v is None and k != "Category"] # Category is optional-ish but needed for this feature
        
        if missing_cols:
            st.error(f"Could not identify the following columns: {', '.join(missing_cols)}")
            st.write("Detected columns:", columns)
            st.stop()

        # --- Data Cleaning ---
        # Ensure Year is treated appropriately (int or str)
        df[col_map["Year"]] = df[col_map["Year"]].astype(str).str.replace(r'\.0$', '', regex=True)
        
        # Ensure Symbol is string and stripped of whitespace
        df[col_map["Symbol"]] = df[col_map["Symbol"]].astype(str).str.strip()
        
        # Clean numeric columns
        price_cols = [col_map["Cheap"], col_map["Fair"], col_map["Expensive"], col_map["Close"]]
        for col in price_cols:
            df[col] = df[col].apply(clean_currency)
            
        # --- Filters ---
        st.sidebar.header("Filters")
        
        # Year Filter
        years = sorted(df[col_map["Year"]].unique())
        selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
        
        # Filter by Year
        year_df = df[df[col_map["Year"]] == selected_year]
        
        # Analysis Mode
        mode = st.sidebar.radio("Analysis Mode", ["Single Stock", "Category Comparison"])
        
        if mode == "Single Stock":
            # Stock Filter (Single Select)
            all_stocks = sorted(year_df[col_map["Symbol"]].unique())
            selected_stock = st.sidebar.selectbox("Select Stock", all_stocks)
            
            if not selected_stock:
                st.warning("Please select a stock.")
            else:
                # Safe filtering
                stock_df = year_df[year_df[col_map["Symbol"]] == selected_stock]
                
                if stock_df.empty:
                    st.error(f"No data found for {selected_stock} in {selected_year}.")
                else:
                    stock_data = stock_df.iloc[0]
                    
                    # Extract values
                    cheap = stock_data[col_map["Cheap"]]
                    fair = stock_data[col_map["Fair"]]
                    expensive = stock_data[col_map["Expensive"]]
                    close = stock_data[col_map["Close"]]
                    
                    # --- Visualization (Price Levels) ---
                    st.subheader(f"Price Analysis for {selected_stock} ({selected_year})")
                    
                    fig = go.Figure()
                    
                    # Use a dummy X-axis range [-0.5, 0.5] to draw lines
                    # Cheap (Green Line)
                    fig.add_trace(go.Scatter(
                        x=[-0.3, 0.3], y=[cheap, cheap],
                        mode='lines+text',
                        name='Cheap (便宜)',
                        line=dict(color='green', width=4),
                        text=[f"Cheap: {cheap}", ""],
                        textposition="middle left"
                    ))
                    
                    # Fair (Blue Line)
                    fig.add_trace(go.Scatter(
                        x=[-0.3, 0.3], y=[fair, fair],
                        mode='lines+text',
                        name='Fair (合理)',
                        line=dict(color='blue', width=4),
                        text=[f"Fair: {fair}", ""],
                        textposition="middle left"
                    ))
                    
                    # Expensive (Red Line)
                    fig.add_trace(go.Scatter(
                        x=[-0.3, 0.3], y=[expensive, expensive],
                        mode='lines+text',
                        name='Expensive (昂貴)',
                        line=dict(color='red', width=4),
                        text=[f"Expensive: {expensive}", ""],
                        textposition="middle left"
                    ))
                    
                    # Closing Price (Diamond)
                    fig.add_trace(go.Scatter(
                        x=[0], y=[close],
                        mode='markers+text',
                        name='Close (收盤)',
                        marker=dict(symbol='diamond', color='#f1c40f', size=25, line=dict(color='white', width=1)),
                        text=[f"Close: {close}"],
                        textposition="middle right"
                    ))
                    
                    # Determine Y-axis range
                    all_vals = [v for v in [cheap, fair, expensive, close] if pd.notnull(v)]
                    if all_vals:
                        min_y = min(all_vals) * 0.9
                        max_y = max(all_vals) * 1.1
                        fig.update_yaxes(range=[min_y, max_y])

                    fig.update_layout(
                        title=f"{selected_stock} Price Levels",
                        yaxis_title="Price",
                        xaxis=dict(showticklabels=False, range=[-0.5, 0.5], title=""),
                        showlegend=True,
                        height=600,
                        hovermode="y unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # --- Data Table ---
                    st.subheader("Detailed Data")
                    st.dataframe(stock_data.to_frame().T)
                    
        elif mode == "Category Comparison":
            if col_map["Category"] is None:
                st.error("No 'Category' column detected in the CSV. Please ensure your file has a column named 'Category', 'Sector', 'Industry', or '分類'.")
            else:
                # Category Filter
                categories = sorted(year_df[col_map["Category"]].astype(str).unique())
                selected_category = st.sidebar.selectbox("Select Category", categories)
                
                # Filter by Category
                cat_df = year_df[year_df[col_map["Category"]] == selected_category]
                
                if cat_df.empty:
                    st.warning(f"No stocks found in category '{selected_category}'.")
                else:
                    st.subheader(f"Category Comparison: {selected_category} ({selected_year})")
                    
                    fig = go.Figure()
                    
                    # For each stock, we add the traces
                    # To make it performant and clean, we can use arrays if possible, but 'line-ew' works per point.
                    # Let's iterate for now, or use a clever mapping.
                    
                    stocks = cat_df[col_map["Symbol"]].tolist()
                    cheaps = cat_df[col_map["Cheap"]].tolist()
                    fairs = cat_df[col_map["Fair"]].tolist()
                    expensives = cat_df[col_map["Expensive"]].tolist()
                    closes = cat_df[col_map["Close"]].tolist()
                    
                    # For each stock, draw horizontal lines
                    # We'll use shapes or individual line traces for each stock
                    for i, stock in enumerate(stocks):
                        # Cheap Level (Green Line)
                        fig.add_trace(go.Scatter(
                            x=[i-0.3, i+0.3], y=[cheaps[i], cheaps[i]],
                            mode='lines',
                            name='Cheap (便宜)' if i == 0 else None,
                            line=dict(color='green', width=4),
                            showlegend=(i == 0),
                            legendgroup='cheap',
                            hovertemplate=f'{stock}<br>Cheap: {cheaps[i]}<extra></extra>'
                        ))
                        
                        # Fair Level (Blue Line)
                        fig.add_trace(go.Scatter(
                            x=[i-0.3, i+0.3], y=[fairs[i], fairs[i]],
                            mode='lines',
                            name='Fair (合理)' if i == 0 else None,
                            line=dict(color='blue', width=4),
                            showlegend=(i == 0),
                            legendgroup='fair',
                            hovertemplate=f'{stock}<br>Fair: {fairs[i]}<extra></extra>'
                        ))
                        
                        # Expensive Level (Red Line)
                        fig.add_trace(go.Scatter(
                            x=[i-0.3, i+0.3], y=[expensives[i], expensives[i]],
                            mode='lines',
                            name='Expensive (昂貴)' if i == 0 else None,
                            line=dict(color='red', width=4),
                            showlegend=(i == 0),
                            legendgroup='expensive',
                            hovertemplate=f'{stock}<br>Expensive: {expensives[i]}<extra></extra>'
                        ))
                    
                    # Closing Prices (all at once)
                    fig.add_trace(go.Scatter(
                        x=list(range(len(stocks))), y=closes,
                        mode='markers+text',
                        name='Close (收盤)',
                        marker=dict(symbol='diamond', color='#f1c40f', size=15, line=dict(color='white', width=1)),
                        text=closes,
                        textposition="top center"
                    ))
                    
                    fig.update_layout(
                        title=f"{selected_category} Stocks Overview",
                        xaxis=dict(
                            tickmode='array',
                            tickvals=list(range(len(stocks))),
                            ticktext=stocks,
                            title="Stock Symbol"
                        ),
                        yaxis_title="Price",
                        showlegend=True,
                        height=700,
                        hovermode="closest"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("Detailed Data")
                    st.dataframe(cat_df)


    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
