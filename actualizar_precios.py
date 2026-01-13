import os
import requests
from datetime import datetime
import pytz
from supabase import create_client, Client

# --- CONEXIÓN SEGURA A TU BASE DE DATOS ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def obtener_datos():
    try:
        # Usamos Binance porque es muy estable para el Robot Matemático
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

    # --- LÓGICA DE LOS 3 SABIOS ROBOTS ---
    r1 = "✅ PRECIO BAJO" if var < -2 else "⚠️ PRECIO ALTO" if var > 2 else "⚖️ ESTABLE"
    r2 = "😨 MIEDO (Oportunidad)" if var < -4 else "😐 MERCADO TRANQUILO"
    r3 = "💎 VISIÓN LARGO PLAZO" if precio < 95000 else "🛡️ PROTECCIÓN"
    
    consejo_final = f"R1: {r1} | R2: {r2} | R3: {r3}"

    # --- GUARDAR EN TU TABLA DE SUPABASE ---
    if precio > 0:
        try:
            supabase.table("historial_precios").insert({
                "moneda": "BTC",
                "precio": precio,
                "fuente": "Binance",
                "consejo_robot": consejo_final
            }).execute()
            print("¡Éxito! Datos guardados en la memoria del Sabio.")
        except Exception as e:
            print(f"Error al guardar en Supabase: {e}")

    # --- CREAR LA WEB ---
    html = f"""
    <body style="background:#0b0e11; color:white; font-family:sans-serif; text-align:center; padding:50px;">
        <div style="border:1px solid #2b2f36; padding:30px; border-radius:20px; display:inline-block;">
            <h1 style="color:#f0b90b;">XTM CONSEJO DE SABIOS</h1>
            <h2 style="font-size:3em;">${precio:,.2f}</h2>
            <p style="background:#1e2329; padding:15px; border-radius:10px;">{consejo_final}</p>
            <small style="color:#848e9c;">Sincronizado con Supabase • {ahora}</small>
        </div>
    </body>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(html)

if __name__ == "__main__":
    generar_dashboard()
