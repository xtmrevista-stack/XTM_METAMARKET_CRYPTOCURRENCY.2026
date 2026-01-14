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
        # Obtenemos precio de Bitcoin
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        return float(r['lastPrice']), float(r['priceChangePercent'])
    except Exception as e:
        print(f"Error API: {e}")
        return 0.0, 0.0

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    precio, var = obtener_datos()

    consejo = "COMPRA" if var < -1 else "ESPERA"

    if precio > 0:
        # Preparamos los datos EXACTAMENTE como tus columnas en Supabase
        datos_para_supabase = {
            "moneda": "BTC",
            "precio": precio,
            "fuente": "Binance",
            "consejo_robot": consejo
        }
        
        try:
            # ENVIAR A SUPABASE (Nombre de tabla: historial_precios)
            resultado = supabase.table("historial_precios").insert(datos_para_supabase).execute()
            print(f"¡DATOS ENVIADOS! Respuesta: {resultado}")
        except Exception as e:
            print(f"ERROR AL ENVIAR A SUPABASE: {e}")

    # Actualizar la web para GitHub Pages
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"<html><body style='background:black;color:gold;text-align:center;'>")
        f.write(f"<h1>BTC: ${precio:,.2f}</h1><p>{consejo}</p><p>{ahora}</p>")
        f.write(f"</body></html>")

if __name__ == "__main__":
    generar_dashboard()
