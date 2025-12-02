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
    
    fig = go.Figure()
    
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
    stocks = cat_df[col_map["Symbol"]].tolist()
    cheaps = cat_df[col_map["Cheap"]].tolist()
    fairs = cat_df[col_map["Fair"]].tolist()
    expensives = cat_df[col_map["Expensive"]].tolist()
    closes = cat_df[col_map["Close"]].tolist()
    
    fig = go.Figure()
    
    # Draw horizontal lines for each stock
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
