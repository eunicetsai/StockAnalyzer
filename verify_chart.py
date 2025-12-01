import pandas as pd
import plotly.graph_objects as go

def verify_chart_logic():
    print("Verifying Price Level Chart Logic...")
    
    # Mock data
    cheap = 100.0
    fair = 150.0
    expensive = 200.0
    close = 145.5
    stock = "AAPL"
    
    print(f"Inputs: Stock={stock}, Cheap={cheap}, Fair={fair}, Expensive={expensive}, Close={close}")
    
    try:
        fig = go.Figure()
        
        x_val = [stock]
        
        # Cheap
        fig.add_trace(go.Scatter(
            x=x_val, y=[cheap],
            mode='markers+text',
            name='Cheap',
            marker=dict(symbol='line-ew', color='green', size=50, line=dict(width=3)),
            text=[f"Cheap: {cheap}"],
            textposition="middle left"
        ))
        
        # Fair
        fig.add_trace(go.Scatter(
            x=x_val, y=[fair],
            mode='markers+text',
            name='Fair',
            marker=dict(symbol='line-ew', color='blue', size=50, line=dict(width=3)),
            text=[f"Fair: {fair}"],
            textposition="middle left"
        ))
        
        # Expensive
        fig.add_trace(go.Scatter(
            x=x_val, y=[expensive],
            mode='markers+text',
            name='Expensive',
            marker=dict(symbol='line-ew', color='red', size=50, line=dict(width=3)),
            text=[f"Expensive: {expensive}"],
            textposition="middle left"
        ))
        
        # Close
        fig.add_trace(go.Scatter(
            x=x_val, y=[close],
            mode='markers+text',
            name='Close',
            marker=dict(symbol='diamond', color='black', size=20),
            text=[f"Close: {close}"],
            textposition="middle right"
        ))
        
        fig.update_layout(title="Test Chart")
        print("Figure created successfully.")
        
    except Exception as e:
        print(f"Error creating figure: {e}")
        raise e

if __name__ == "__main__":
    verify_chart_logic()
