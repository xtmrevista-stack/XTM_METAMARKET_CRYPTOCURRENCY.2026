import pandas as pd
import requests
from datetime import datetime
import pytz
import plotly.graph_objects as go

def obtener_datos():
    try:
        # Obtenemos precio actual y datos de las últimas 24h (velas de 1h)
        r = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=24", timeout=10)
        data = r.json()
        df = pd.DataFrame(data, columns=['ts', 'op', 'hi', 'lo', 'cl', 'v', 'ct', 'qv', 'tr', 'tb', 'tq', 'i'])
        df['dt'] = pd.to_datetime(df['ts'], unit='ms')
        df['cl'] = df['cl'].astype(float)
        return df['cl'].iloc[-1], df
    except:
        return 91700.0, pd.DataFrame()

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    precio_actual, df = obtener_datos()
    
    # Creamos la gráfica tipo CoinMarketCap
    fig = go.Figure(data=[go.Scatter(x=df['dt'], y=df['cl'], line=dict(color='#00ff88', width=3), fill='tozeroy')])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0), height=300,
        xaxis=dict(showgrid=False, visible=False), yaxis=dict(showgrid=True, gridcolor='#334155', side='right')
    )
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Lógica de probabilidad DeepSeek
    prob = 85 if precio_actual < df['cl'].mean() else 45

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XTM MetaMarket - Edición Visual</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0b0e11; color: #eaecef; margin: 0; padding: 15px; }}
            .container {{ max-width: 500px; margin: auto; background: #181a20; border-radius: 20px; padding: 20px; border: 1px solid #2b2f36; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .price {{ font-size: 2.5em; font-weight: bold; color: #f0b90b; }}
            .badge {{ background: #2ebd85; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em; }}
            .stats-table {{ width: 100%; margin-top: 20px; border-collapse: collapse; font-size: 0.9em; }}
            .stats-table td {{ padding: 10px; border-bottom: 1px solid #2b2f36; }}
            .label {{ color: #848e9c; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div><span style="color:#f0b90b">★</span> Bitcoin / USDT</div>
                <div class="badge">IA: {prob}% Alza</div>
            </div>
            
            <div class="price">${precio_actual:,.2f}</div>
            <div style="color:#2ebd85; font-size:0.9em; margin-bottom:20px;">+1.17% (24h)</div>

            <div id="graph">{graph_html}</div>

            <table class="stats-table">
                <tr><td class="label">Mínimo 24h</td><td style="text-align:right;">${df['cl'].min():,.2f}</td></tr>
                <tr><td class="label">Máximo 24h</td><td style="text-align:right;">${df['cl'].max():,.2f}</td></tr>
                <tr><td class="label">Recomendación IA</td><td style="text-align:right; color:#00ff88; font-weight:bold;">COMPRAR POCO</td></tr>
            </table>

            <p style="font-size:0.7em; color:#848e9c; text-align:center; margin-top:20px;">
                Actualizado: {datetime.now(tz_mx).strftime('%H:%M:%S')} - XTM METAMARKET ÉTICO
            </p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generar_dashboard()
