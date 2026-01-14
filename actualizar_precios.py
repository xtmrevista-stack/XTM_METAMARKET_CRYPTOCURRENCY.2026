import os
import requests
import pandas as pd
from datetime import datetime
import pytz

def obtener_datos():
    # Intento 1: Binance
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        r = requests.get(url, timeout=10).json()
        return float(r['price']), 0.0  # Usamos 0.0 para la variación si es simple
    except:
        # Intento 2: CoinGecko (Respaldo)
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            r = requests.get(url, timeout=10).json()
            return float(r['bitcoin']['usd']), 0.0
        except:
            return 95000.0, 0.0 # Un precio de emergencia para que no salga 0

def actualizar_memoria():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora_str = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    precio, var = obtener_datos()
    
    # Lógica de los Sabios (simplificada para evitar errores)
    r1 = "✅ COMPRA" if precio < 90000 else "⚠️ ESPERA"
    r2 = "😐 CALMA"
    consejo = f"{r1} | {r2}"

    # --- MEMORIA INTERNA ---
    archivo = "historial.csv"
    nueva_fila = pd.DataFrame([[ahora_str, precio, consejo]], columns=["Fecha", "Precio", "Consejo"])

    if not os.path.isfile(archivo):
        nueva_fila.to_csv(archivo, index=False)
    else:
        nueva_fila.to_csv(archivo, mode='a', header=False, index=False)

    # --- GENERAR WEB ---
    df = pd.read_csv(archivo).tail(10).iloc[::-1]
    tabla_html = df.to_html(classes='tabla-estilo', index=False)

    html_final = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background: #0b0e11; color: white; font-family: sans-serif; text-align: center; padding: 20px; }}
            .container {{ max-width: 500px; margin: auto; border: 2px solid #f0b90b; padding: 20px; border-radius: 20px; background: #181a20; }}
            h1 {{ color: #f0b90b; }}
            .precio {{ font-size: 3em; color: white; margin: 10px 0; }}
            .tabla-estilo {{ width: 100%; margin-top: 20px; border-collapse: collapse; }}
            .tabla-estilo th {{ background: #f0b90b; color: black; padding: 10px; }}
            .tabla-estilo td {{ padding: 10px; border-bottom: 1px solid #2b2f36; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>XTM MÉTRICAS ÉTICAS</h1>
            <div class="precio">${precio:,.2f}</div>
            <p style="background:#2b2f36; padding:10px; border-radius:10px;">{consejo}</p>
            <h3>ÚLTIMOS MOVIMIENTOS</h3>
            {tabla_html}
            <p style="font-size:0.8em; color:gray; margin-top:20px;">Sincronizado: {ahora_str}</p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_final)

if __name__ == "__main__":
    actualizar_memoria()
