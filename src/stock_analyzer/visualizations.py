"""
Visualization module for financial analysis.
Creates Plotly charts for single stock and category comparison.
"""
import plotly.graph_objects as go
import pandas as pd


def create_single_stock_chart(stock_data, col_map, stock_name, year):
    """Create price level chart for a single stock."""
    cheap = stock_data[col_map["Cheap"]]
    fair = stock_data[col_map["Fair"]]
    expensive = stock_data[col_map["Expensive"]]
    close = stock_data[col_map["Close"]]
    
    # Get close date if available
    close_date = stock_data.get(col_map.get("CloseDate")) if col_map.get("CloseDate") else None
    
    fig = go.Figure()
    
    # Cheap (Green Line)
    fig.add_trace(go.Scatter(
        x=[-0.3, 0.3], y=[cheap, cheap],
        mode='lines+text',
        name='Cheap (便宜)',
        line=dict(color='green', width=4),
        text=[f"{cheap}", ""],
        textposition="middle left",
        hovertemplate=f'Cheap: {cheap}<extra></extra>'
    ))
    
    # Fair (Blue Line)
    fig.add_trace(go.Scatter(
        x=[-0.3, 0.3], y=[fair, fair],
        mode='lines+text',
        name='Fair (合理)',
        line=dict(color='blue', width=4),
        text=[f"{fair}", ""],
        textposition="middle left",
        hovertemplate=f'Fair: {fair}<extra></extra>'
    ))
    
    # Expensive (Red Line)
    fig.add_trace(go.Scatter(
        x=[-0.3, 0.3], y=[expensive, expensive],
        mode='lines+text',
        name='Expensive (昂貴)',
        line=dict(color='red', width=4),
        text=[f"{expensive}", ""],
        textposition="middle left",
        hovertemplate=f'Expensive: {expensive}<extra></extra>'
    ))
    
    # Closing Price (Diamond)
    # Prepare hover text with date if available
    if close_date and pd.notnull(close_date):
        hover_text = f'Close: {close}<br>Date: {close_date}'
    else:
        hover_text = f'Close: {close}'
    
    fig.add_trace(go.Scatter(
        x=[0], y=[close],
        mode='markers+text',
        name='Close (收盤)',
        marker=dict(symbol='diamond', color='#f1c40f', size=25, line=dict(color='white', width=1)),
        text=[f"{close}"],
        textposition="middle left",
        hovertemplate=hover_text + '<extra></extra>'
    ))
    
    # Set Y-axis range
    all_vals = [v for v in [cheap, fair, expensive, close] if pd.notnull(v)]
    if all_vals:
        min_y = min(all_vals) * 0.9
        max_y = max(all_vals) * 1.1
        fig.update_yaxes(range=[min_y, max_y])

    fig.update_layout(
        title=f"{stock_name} Price Levels",
        yaxis_title="Price",
        xaxis=dict(showticklabels=False, range=[-0.5, 0.5], title=""),
        showlegend=True,
        height=600,
        hovermode="y unified"
    )
    
    return fig


def create_category_comparison_chart(cat_df, col_map, category_name, year):
    """Create comparison chart for multiple stocks in a category."""
    # Sort by stock symbol
    cat_df_sorted = cat_df.sort_values(by=col_map["Symbol"])
    
    stocks = cat_df_sorted[col_map["Symbol"]].tolist()
    cheaps = cat_df_sorted[col_map["Cheap"]].tolist()
    fairs = cat_df_sorted[col_map["Fair"]].tolist()
    expensives = cat_df_sorted[col_map["Expensive"]].tolist()
    closes = cat_df_sorted[col_map["Close"]].tolist()
    
    # Get close dates if available
    close_dates = None
    if col_map.get("CloseDate"):
        close_dates = cat_df_sorted[col_map["CloseDate"]].tolist()
    
    fig = go.Figure()
    
    # Draw horizontal lines for each stock
    for i, stock in enumerate(stocks):
        # Cheap Level (Green Line)
        fig.add_trace(go.Scatter(
            x=[i-0.3, i+0.3], y=[cheaps[i], cheaps[i]],
            mode='lines+text',
            name='Cheap (便宜)' if i == 0 else None,
            line=dict(color='green', width=4),
            text=[f"{cheaps[i]}", ""],
            textposition="middle left",
            showlegend=(i == 0),
            legendgroup='cheap',
            hovertemplate=f'{stock}<br>Cheap: {cheaps[i]}<extra></extra>'
        ))
        
        # Fair Level (Blue Line)
        fig.add_trace(go.Scatter(
            x=[i-0.3, i+0.3], y=[fairs[i], fairs[i]],
            mode='lines+text',
            name='Fair (合理)' if i == 0 else None,
            line=dict(color='blue', width=4),
            text=[f"{fairs[i]}", ""],
            textposition="middle left",
            showlegend=(i == 0),
            legendgroup='fair',
            hovertemplate=f'{stock}<br>Fair: {fairs[i]}<extra></extra>'
        ))
        
        # Expensive Level (Red Line)
        fig.add_trace(go.Scatter(
            x=[i-0.3, i+0.3], y=[expensives[i], expensives[i]],
            mode='lines+text',
            name='Expensive (昂貴)' if i == 0 else None,
            line=dict(color='red', width=4),
            text=[f"{expensives[i]}", ""],
            textposition="middle left",
            showlegend=(i == 0),
            legendgroup='expensive',
            hovertemplate=f'{stock}<br>Expensive: {expensives[i]}<extra></extra>'
        ))
    
    # Closing Prices (all at once)
    # Prepare hover text with dates if available
    hover_texts = []
    for i, (stock, close) in enumerate(zip(stocks, closes)):
        if close_dates and pd.notnull(close_dates[i]):
            hover_texts.append(f"{stock}<br>Close: {close}<br>Date: {close_dates[i]}")
        else:
            hover_texts.append(f"{stock}<br>Close: {close}")
    
    fig.add_trace(go.Scatter(
        x=list(range(len(stocks))), y=closes,
        mode='markers+text',
        name='Close (收盤)',
        marker=dict(symbol='diamond', color='#f1c40f', size=15, line=dict(color='white', width=1)),
        text=[str(c) for c in closes],  # Only show price
        textposition="middle left",
        hovertext=hover_texts,
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title=f"{category_name} Stocks Overview",
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
    
    return fig
