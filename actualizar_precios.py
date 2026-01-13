import os
import requests
import pandas as pd
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- CONEXIÓN SEGURA ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def obtener_datos():
    try:
        # Usamos una fuente muy estable
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        precio = float(r['lastPrice'])
        pct = float(r['priceChangePercent'])
        return precio, pct
    except Exception as e:
        print(f"Error obteniendo datos: {e}")
        return 91000.0, 0.0

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora_dt = datetime.now(tz_mx)
    ahora_str = ahora_dt.strftime('%Y-%m-%d %H:%M:%S')
    
    precio, pct = obtener_datos()

    # --- LÓGICA DE LOS SABIOS ROBOTS ---
    r1 = "✅ OFERTA" if pct < -2 else "⚠️ INFLADO" if pct > 2 else "⚖️ ESTABLE"
    r2 = "😨 MIEDO" if pct < -4 else "😐 CALMA"
    r3 = "💎 LARGO PLAZO" if precio < 95000 else "🛡️ PRECAUCIÓN"
    consejo = f"R1:{r1} | R2:{r2} | R3:{r3}"

    # --- GUARDAR EN SUPABASE ---
    try:
        # Insertar en la tabla que creamos
        supabase.table("historial_precios").insert({
            "moneda": "BTC",
            "precio": precio,
            "fuente": "Binance",
            "consejo_robot": consejo
        }).execute()
        print("¡Datos guardados con éxito en Supabase!")
    except Exception as e:
        print(f"Error guardando en Supabase: {e}")

    # --- HTML SIMPLE ---
    html = f"""
    <html>
    <body style="background:#0b0e11; color:white; font-family:sans-serif; text-align:center;">
        <div style="padding:50px; border:1px solid #2b2f36; border-radius:20px; display:inline-block;">
            <h1>XTM MÉTRICAS ÉTICAS</h1>
            <h2 style="font-size:3em;">${precio:,.2f}</h2>
            <p style="color:#848e9c;">{ahora_str}</p>
            <hr>
            <h3>CONSEJO DE SABIOS:</h3>
            <p style="font-size:1.2em; color:#f0b90b;">{consejo}</p>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generar_dashboard()
