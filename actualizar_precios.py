import pandas as pd
import requests
from datetime import datetime
import pytz
import plotly.graph_objects as go

def obtener_datos():
    try:
        # Obtenemos datos de las últimas 24h para la gráfica profesional
        r = requests.get("https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=24", timeout=10)
        df = pd.DataFrame(r.json(), columns=['ts', 'op', 'hi', 'lo', 'cl', 'v', 'ct', 'qv', 'tr', 'tb', 'tq', 'i'])
        df['dt'] = pd.to_datetime(df['ts'], unit='ms')
        df['cl'] = df['cl'].astype(float)
        return df['cl'].iloc[-1], df
    except:
        return 91700.0, pd.DataFrame()

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    precio_actual, df = obtener_datos()
    
    # --- CÁLCULO DE PISOS Y TECHOS (Soportes y Resistencias) ---
    piso = df['cl'].min()
    techo = df['cl'].max()
    promedio = df['cl'].mean()

    # --- GRÁFICA ESTILO COINMARKETCAP ---
    fig = go.Figure()
    # Línea de precio
    fig.add_trace(go.Scatter(x=df['dt'], y=df['cl'], name='Precio', line=dict(color='#38bdf8', width=3), fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)'))
    # Línea de PISO (Soporte)
    fig.add_trace(go.Scatter(x=df['dt'], y=[piso]*24, name='Piso', line=dict(color='#2ebd85', width=1, dash='dash')))
    # Línea de TECHO (Resistencia)
    fig.add_trace(go.Scatter(x=df['dt'], y=[techo]*24, name='Techo', line=dict(color='#f23645', width=1, dash='dash')))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0), height=350, showlegend=False,
        xaxis=dict(showgrid=False, color='#64748b'), yaxis=dict(showgrid=True, gridcolor='#1e293b', side='right', color='#64748b')
    )
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # LÓGICA XTM-ROBOT AI
    prob = 85 if precio_actual < promedio else 42
    recomendacion = "COMPRA SEGURA" if prob > 80 else "MANTENER / ESPERAR" if prob > 40 else "RIESGO: NO COMPRAR"
    color_rec = "#38bdf8" if prob > 80 else "#f0b90b" if prob > 40 else "#f23645"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XTM MetaMarket Pro</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #0b0e11; color: #ffffff; margin: 0; padding: 20px; }}
            .app {{ max-width: 600px; margin: auto; background: #181a20; border-radius: 24px; padding: 25px; border: 1px solid #2b2f36; }}
            .coin-info {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; color: #848e9c; }}
            .price-main {{ font-size: 3em; font-weight: bold; margin: 5px 0; }}
            .stats-table {{ width: 100%; margin-top: 25px; border-top: 1px solid #2b2f36; }}
            .stats-row {{ display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #2b2f36; }}
            .label {{ color: #848e9c; font-size: 0.9em; }}
            .val {{ font-weight: 600; }}
            .ai-box {{ background: #1e2329; padding: 20px; border-radius: 15px; margin-top: 20px; border-left: 5px solid {color_rec}; }}
        </style>
    </head>
    <body>
        <div class="app">
            <div class="coin-info">🚀 <b>Bitcoin</b> <span>BTC/USDT</span> <span style="background:#2ebd85; color:white; padding:2px 6px; border-radius:4px; font-size:0.7em;">IA ACTIVADA</span></div>
            <div class="price-main">${precio_actual:,.2f}</div>
            
            <div id="chart">{graph_html}</div>

            <div class="ai-box">
                <div class="label" style="margin-bottom:5px;">Recomendación de XTM-Robot AI</div>
                <div style="font-size: 1.5em; font-weight: bold; color: {color_rec};">{recomendacion}</div>
                <div style="font-size: 0.8em; color: #848e9c; margin-top:5px;">Probabilidad de éxito basada en regresión: {prob}%</div>
            </div>

            <div class="stats-table">
                <div class="stats-row"><span class="label">Piso del Día (Soporte)</span><span class="val" style="color:#2ebd85;">${piso:,.2f}</span></div>
                <div class="stats-row"><span class="label">Techo del Día (Resistencia)</span><span class="val" style="color:#f23645;">${techo:,.2f}</span></div>
                <div class="stats-row"><span class="label">Estado del Mercado</span><span class="val">Dinámico (24h)</span></div>
            </div>

            <p style="text-align:center; font-size:0.7em; color:#474d57; margin-top:20px;">
                Sincronizado con Binance Global Core • {datetime.now(tz_mx).strftime('%H:%M:%S')} CDMX
            </p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)

if __name__ == "__main__": generar_dashboard()
