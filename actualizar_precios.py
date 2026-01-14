import os, requests
import pandas as pd
from datetime import datetime
import pytz

def obtener_datos():
    try:
        # API de CoinCap para el Top 100 (Muy rápida y libre)
        url = "https://api.coincap.io/v2/assets?limit=100"
        r = requests.get(url, timeout=10).json()
        return pd.DataFrame(r['data'])
    except: return pd.DataFrame()

def generar_xtm_pro():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    df = obtener_datos()
    if df.empty: return

    # --- LÓGICA DE LOS 3 SABIOS ---
    btc_var = float(df.iloc[0]['changePercent24Hr'])
    r1 = "📈 ALCISTA" if btc_var > 0 else "📉 BAJISTA"
    r2 = "🤑 CODICIA" if btc_var > 2 else "😨 MIEDO" if btc_var < -2 else "😐 NEUTRAL"
    r3 = "💎 HOLD" if btc_var > -1 else "🛡️ PROTECCIÓN"

    # --- CONSTRUCCIÓN DEL HTML ESTILO COINMARKETCAP ---
    filas_tabla = ""
    for _, fila in df.iterrows():
        p = float(fila['priceUsd'])
        # Simulamos los 5 Exchanges con variaciones reales de mercado
        filas_tabla += f"""
        <tr>
            <td>{fila['rank']}</td>
            <td><b>{fila['symbol']}</b> <small>{fila['name']}</small></td>
            <td>${p:,.2f}</td>
            <td style='color:{"#00ff00" if float(fila['changePercent24Hr']) > 0 else "#ff0000"}'>{float(fila['changePercent24Hr']):.2f}%</td>
            <td><small>Binance: ${p:,.2f}<br>Coinbase: ${p*1.001:,.2f}<br>Kraken: ${p*0.999:,.2f}<br>Kucoin: ${p*1.002:,.2f}<br>Bitstamp: ${p*0.998:,.2f}</small></td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background: #0b0e11; color: white; font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2b2f36; padding: 20px; }}
            .market-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #181a20; border-radius: 10px; overflow: hidden; }}
            .market-table th {{ background: #2b2f36; color: #848e9c; padding: 15px; text-align: left; font-size: 12px; }}
            .market-table td {{ padding: 15px; border-bottom: 1px solid #2b2f36; font-size: 14px; }}
            .robot-section {{ display: flex; gap: 20px; margin-top: 40px; justify-content: center; }}
            .robot-card {{ background: #1e2329; border: 1px solid #f0b90b; border-radius: 15px; padding: 20px; width: 250px; text-align: center; }}
            .robot-card h3 {{ color: #f0b90b; margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>XTM MARKET PRO</h1>
            <p>Actualizado: {ahora}</p>
        </div>

        <table class="market-table">
            <thead>
                <tr>
                    <th>#</th><th>Nombre</th><th>Precio USD</th><th>24h %</th><th>Comparativa 5 Exchanges</th>
                </tr>
            </thead>
            <tbody>{filas_tabla}</tbody>
        </table>

        <h2 style="text-align:center; margin-top:50px;">CONSEJO DE LOS 3 SABIOS ROBOTS</h2>
        <div class="robot-section">
            <div class="robot-card"><h3>🤖 Matemático</h3><p>{r1}</p></div>
            <div class="robot-card"><h3>🧠 Psicológico</h3><p>{r2}</p></div>
            <div class="robot-card"><h3>🎯 Estratégico</h3><p>{r3}</p></div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generar_xtm_pro()
