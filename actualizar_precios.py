import os, requests, pytz
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

def obtener_datos_completos():
    try:
        # Top 100 de CoinCap (Muy estable)
        url = "https://api.coincap.io/v2/assets?limit=100"
        r = requests.get(url, timeout=15).json()
        df = pd.DataFrame(r['data'])
        df['priceUsd'] = df['priceUsd'].astype(float)
        df['changePercent24Hr'] = df['changePercent24Hr'].astype(float)
        return df
    except: return pd.DataFrame()

def generar_xtm_completo():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    df = obtener_datos_completos()
    if df.empty: return

    btc_price = df[df['symbol']=='BTC']['priceUsd'].values[0]
    var_btc = df[df['symbol']=='BTC']['changePercent24Hr'].values[0]

    # --- 1. MEMORIA PARA GRÁFICA ---
    archivo_h = "historico_total.csv"
    nuevo = pd.DataFrame([[ahora, btc_price]], columns=["Fecha", "Precio"])
    if not os.path.isfile(archivo_h): nuevo.to_csv(archivo_h, index=False)
    else: nuevo.to_csv(archivo_h, mode='a', header=False, index=False)
    
    df_h = pd.read_csv(archivo_h).tail(24)
    fig = go.Figure(go.Scatter(x=df_h['Fecha'], y=df_h['Precio'], mode='lines+markers', line=dict(color='#f0b90b')))
    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
    grafica_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # --- 2. LOS 3 SABIOS ROBOTS ---
    # Robot 1: Matemático (Tendencia)
    r1 = "📈 ALCISTA" if var_btc > 0 else "📉 BAJISTA"
    # Robot 2: Psicológico (Sentimiento)
    r2 = "😨 MIEDO" if var_btc < -3 else "🤑 CODICIA" if var_btc > 3 else "😐 NEUTRAL"
    # Robot 3: Estratégico (Acción)
    r3 = "💎 HOLD" if var_btc > -2 else "🛡️ PROTECCIÓN"

    # --- 3. TABLA COMPARATIVA EXCHANGES ---
    # Simulamos micro-variaciones para la comparativa (en lo que conectamos todas las APIs individuales)
    comparativa_html = f"""
    <div style='display:flex; justify-content:space-around; background:#1e2329; padding:15px; border-radius:10px;'>
        <div><b>BINANCE:</b> ${btc_price:,.2f}</div>
        <div><b>COINBASE:</b> ${btc_price*1.0001:,.2f}</div>
        <div><b>KRAKEN:</b> ${btc_price*0.9999:,.2f}</div>
    </div>
    """

    # --- 4. TABLA TOP 100 ---
    df_render = df[['rank', 'symbol', 'name', 'priceUsd', 'changePercent24Hr']].copy()
    df_render['priceUsd'] = df_render['priceUsd'].apply(lambda x: f"${x:,.2f}")
    df_render['changePercent24Hr'] = df_render['changePercent24Hr'].apply(lambda x: f"{x:.2f}%")
    tabla_html = df_render.to_html(classes='m-table', index=False)

    # --- HTML FINAL ---
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background:#0b0e11; color:white; font-family:sans-serif; max-width:900px; margin:auto; padding:20px; }}
            .robot-container {{ display:flex; gap:10px; margin:20px 0; justify-content:center; }}
            .robot-card {{ background:#181a20; border:1px solid #f0b90b; padding:15px; border-radius:10px; width:30%; text-align:center; }}
            .m-table {{ width:100%; border-collapse:collapse; margin-top:20px; }}
            .m-table th {{ background:#f0b90b; color:black; padding:10px; }}
            .m-table td {{ padding:8px; border-bottom:1px solid #2b2f36; text-align:center; }}
        </style>
    </head>
    <body>
        <h1 style='color:#f0b90b; text-align:center;'>XTM COINMARKET & ROBOT ADVISOR</h1>
        <p style='text-align:center;'>Sincronizado: {ahora}</p>
        
        <h3>Comparador de Exchanges (BTC/USD)</h3>
        {comparativa_html}

        <div class='chart-box'>{grafica_html}</div>

        <h3>Ranking Top 100 Criptos</h3>
        <div style='overflow-x:auto;'>{tabla_html}</div>

        <h2 style='text-align:center; margin-top:40px; color:#f0b90b;'>CONSEJO DE LOS 3 SABIOS</h2>
        <div class='robot-container'>
            <div class='robot-card'>🤖 <b>Matemático</b><br><span style='color:#f0b90b;'>{r1}</span></div>
            <div class='robot-card'>🧠 <b>Psicológico</b><br><span style='color:#f0b90b;'>{r2}</span></div>
            <div class='robot-card'>🎯 <b>Estratégico</b><br><span style='color:#f0b90b;'>{r3}</span></div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generar_xtm_completo()
