import os
import requests
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- CONEXIÓN SEGURA ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def obtener_datos():
    try:
        # Usamos Binance por su alta estabilidad
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        precio = float(r['lastPrice'])
        variacion = float(r['priceChangePercent'])
        return precio, variacion
    except:
        return 0.0, 0.0

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    precio, var = obtener_datos()

    # --- LÓGICA DE LOS SABIOS ROBOTS ---
    r1 = "✅ COMPRA" if var < -1 else "⚠️ ESPERA" if var > 1 else "⚖️ NEUTRAL"
    r2 = "😨 MIEDO" if var < -3 else "😐 CALMA"
    r3 = "💎 HOLD" if precio < 98000 else "🛡️ TOMA PROFEIT"
    consejo_final = f"R1:{r1} | R2:{r2} | R3:{r3}"

    # --- EL PASO CRUCIAL: GUARDAR EN SUPABASE ---
    if precio > 0:
        data = {
            "moneda": "BTC",
            "precio": precio,
            "fuente": "Binance",
            "consejo_robot": consejo_final
        }
        try:
            # Esta línea es la que llena tu tabla de la imagen image_20366d.png
            supabase.table("historial_precios").insert(data).execute()
            print(">>> ¡MEMORIA ACTUALIZADA EN SUPABASE! <<<")
        except Exception as e:
            print(f"Error al guardar: {e}")

    # --- ACTUALIZAR WEB ---
    html = f"""
    <body style="background:#0b0e11; color:white; font-family:sans-serif; text-align:center; padding:50px;">
        <h1 style="color:#f0b90b;">XTM METAMARKET</h1>
        <h2 style="font-size:3em;">${precio:,.2f}</h2>
        <p style="background:#1e2329; padding:15px; border-radius:10px;">{consejo_final}</p>
        <small style="color:#848e9c;">Base de datos vinculada • {ahora}</small>
    </body>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generar_dashboard()
