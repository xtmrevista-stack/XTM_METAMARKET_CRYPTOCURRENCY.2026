import os
import requests
import pandas as pd
from datetime import datetime
import pytz

def obtener_datos():
    try:
        # Usamos Binance por su gran estabilidad
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        return float(r['lastPrice']), float(r['priceChangePercent'])
    except:
        return 0.0, 0.0

def actualizar_memoria():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    precio, var = obtener_datos()
    
    # Lógica de los Sabios
    r1 = "✅ COMPRA" if var < -1 else "⚠️ ESPERA"
    r2 = "😐 CALMA" if var > -3 else "😨 MIEDO"
    consejo = f"R1:{r1} | R2:{r2}"

    # --- GESTIÓN DEL ARCHIVO DE MEMORIA (CSV) ---
    archivo = "historial.csv"
    nueva_fila = pd.DataFrame([[ahora, precio, consejo]], columns=["Fecha", "Precio", "Consejo"])

    if not os.path.isfile(archivo):
        nueva_fila.to_csv(archivo, index=False)
    else:
        nueva_fila.to_csv(archivo, mode='a', header=False, index=False)

    # --- GENERAR LA WEB (Leemos el historial para mostrarlo) ---
    df = pd.read_csv(archivo).tail(10) # Tomamos los últimos 10 registros
    tabla_html = df.to_html(classes='tabla-estilo', index=False)

    html_final = f"""
    <html>
    <head>
        <style>
            body {{ background: #0b0e11; color: white; font-family: sans-serif; text-align: center; padding: 20px; }}
            .card {{ border: 1px solid #f0b90b; padding: 20px; border-radius: 15px; display: inline-block; }}
            .tabla-estilo {{ margin-top: 20px; border-collapse: collapse; width: 100%; }}
            .tabla-estilo th, .tabla-estilo td {{ border: 1px solid #2b2f36; padding: 8px; }}
            .tabla-estilo th {{ background: #f0b90b; color: black; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>XTM MÉTRICAS ÉTICAS</h1>
            <h2 style="font-size: 3em; color: #f0b90b;">${precio:,.2f}</h2>
            <p>Última actualización: {ahora}</p>
            <hr>
            <h3>HISTORIAL DE MEMORIA INTERNA</h3>
            {tabla_html}
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_final)

if __name__ == "__main__":
    actualizar_memoria()
