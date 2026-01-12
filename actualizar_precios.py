import pandas as pd
import requests
from datetime import datetime
import pytz
import plotly.graph_objects as go

def obtener_datos():
    try:
        # Precios de 3 exchanges para arbitraje
        p_bin = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()['price'])
        p_coin = float(requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot").json()['data']['amount'])
        p_kra = float(requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSDT").json()['result']['XBTUSDT']['c'][0])
        p_usdt = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTDAI").json()['price'])
        return p_bin, p_coin, p_kra, p_usdt
    except: return 0, 0, 0, 1.0

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    p_bin, p_coin, p_kra, p_usdt = obtener_datos()
    
    # Datos históricos (24h en intervalos de 15min)
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=96"
    df = pd.DataFrame(requests.get(url).json(), columns=['ts','op','hi','lo','cl','v','ct','qv','tr','tb','tq','i'])
    df['cl'] = df['cl'].astype(float)
    df['v'] = df['v'].astype(float)
    df['dt_mx'] = pd.to_datetime(df['ts'], unit='ms', utc=True).dt.tz_convert(tz_mx)
    
    # --- LÓGICA DE PROBABILIDAD (ESTILO DEEPSEEK) ---
    promedio_24h = df['cl'].mean()
    desviacion = ((p_bin - promedio_24h) / promedio_24h) * 100
    
    # Volumen Relativo de 2 horas (últimos 8 periodos de 15 min)
    vol_2h = df['v'].tail(8).mean()
    fuerza_volumen = df['v'].iloc[-1] / vol_2h

    # Cálculo Probabilístico
    prob = 50 
    if desviacion < -1.5: prob += 20 # Precio barato
    if fuerza_volumen > 1.1: prob += 15 # Volumen activo
    if p_bin > df['cl'].iloc[-2]: prob += 10 # Impulso inmediato
    prob = min(prob, 98)

    # Gráfica Visual
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['dt_mx'], y=df['cl'], fill='tozeroy', line=dict(color='#38bdf8', width=2)))
    fig.update_layout(template='plotly_dark', height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_showgrid=False, yaxis_showgrid=False)

    # --- DISEÑO DE LA PÁGINA WEB ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XTM Predictive Engine</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: white; margin: 0; padding: 15px; display: flex; justify-content: center; }}
            .app {{ max-width: 500px; width: 100%; background: #1e293b; padding: 20px; border-radius: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            .header {{ text-align: center; border-bottom: 1px solid #334155; padding-bottom: 15px; margin-bottom: 15px; }}
            .prob-card {{ text-align: center; padding: 20px; border-radius: 20px; background: #334155; transition: 0.5s; }}
            .panico {{ background: #7f1d1d !important; border: 2px solid #ef4444; animation: pulse 1.5s infinite; }}
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
            .val {{ font-size: 3.5em; font-weight: bold; color: #38bdf8; margin: 10px 0; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 15px 0; }}
            .box {{ background: #0f172a; padding: 12px; border-radius: 15px; text-align: center; font-size: 0.9em; }}
            .label {{ font-size: 0.7em; color: #94a3b8; text-transform: uppercase; display: block; }}
        </style>
    </head>
    <body>
        <div class="app">
            <div class="header"><b>XTM</b> PREDICTIVE ENGINE <span style="font-size:0.7em; color:#38bdf8;">v2.0</span></div>
            
            <div class="prob-card {'panico' if prob < 40 else ''}">
                <span class="label">Probabilidad de Alza (1h)</span>
                <div class="val">{prob}%</div>
                <div style="font-weight:bold;">{'🎯 OPORTUNIDAD' if prob > 70 else '⚖️ ESTABLE' if prob > 45 else '🛑 RIESGO ALTO'}</div>
            </div>

            <div class="grid">
                <div class="box"><span class="label">Precio Actual</span><b>${p_bin:,.2f}</b></div>
                <div class="box"><span class="label">Volumen (2h)</span><b>x{fuerza_volumen:.2f}</b></div>
                <div class="box"><span class="label">Desviación</span><b>{desviacion:.2f}%</b></div>
                <div class="box"><span class="label">Refugio USDT</span><b>${p_usdt:.4f}</b></div>
            </div>

            <div id="chart">{fig.to_html(full_html=False, include_plotlyjs='cdn')}</div>
            
            <p style="text-align:center; font-size:0.65em; color:#64748b; margin-top:15px;">
                Análisis matemático basado en modelos de arbitraje chino.<br>
                Ult. Actualización: {datetime.now(tz_mx).strftime('%H:%M:%S')} CDMX
            </p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generar_dashboard()
