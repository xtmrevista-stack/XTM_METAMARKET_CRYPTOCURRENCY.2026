import os
import requests
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- CONEXIÓN ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def obtener_datos():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        return float(r['lastPrice']), float(r['priceChangePercent'])
    except:
        return 0.0, 0.0

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    precio, var = obtener_datos()

    r1 = "✅ COMPRA" if var < -1 else "⚠️ ESPERA"
    r2 = "😐 CALMA" if var > -3 else "😨 MIEDO"
    consejo = f"R1:{r1} | R2:{r2}"

    # --- EL CAMBIO CRUCIAL ---
    if precio > 0:
        data = {
            "moneda": "BTC",
            "precio": precio,
            "fuente": "Binance",
            "consejo_robot": consejo
        }
        try:
            # Asegúrate de que el nombre sea 'historial_precios' como en tu imagen
            supabase.table("historial_precios").insert(data).execute()
            print(">>> EXITO: Fila insertada en Supabase <<<")
        except Exception as e:
            print(f"Error de inserción: {e}")

    # --- WEB ---
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"<h1>BTC: ${precio:,.2f}</h1><p>{consejo}</p><small>{ahora}</small>")

if __name__ == "__main__":
    generar_dashboard()
