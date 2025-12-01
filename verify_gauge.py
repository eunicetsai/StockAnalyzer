import pandas as pd
import plotly.graph_objects as go

def verify_gauge_logic():
    print("Verifying Gauge Chart Logic...")
    
    # Mock data
    cheap = 100.0
    fair = 150.0
    expensive = 200.0
    close = 145.5
    
    print(f"Inputs: Cheap={cheap}, Fair={fair}, Expensive={expensive}, Close={close}")
    
    # Logic from app.py
    max_val = max(cheap, fair, expensive, close) * 1.2
    print(f"Calculated Max Value: {max_val}")
    
    try:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = close,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Closing Price vs Valuation"},
            delta = {'reference': fair, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            gauge = {
                'axis': {'range': [0, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "black", 'thickness': 0.05},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, cheap], 'color': "#55efc4"},       # Green
                    {'range': [cheap, fair], 'color': "#ffeaa7"},    # Yellow
                    {'range': [fair, expensive], 'color': "#fab1a0"}, # Orange
                    {'range': [expensive, max_val], 'color': "#ff7675"} # Red
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': close
                }
            }
        ))
        print("Figure created successfully.")
        # fig.show() # Cannot show in headless, but creation proves logic is valid
    except Exception as e:
        print(f"Error creating figure: {e}")
        raise e

if __name__ == "__main__":
    verify_gauge_logic()
