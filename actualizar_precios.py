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
        # Usamos la API de Binance que es la más estable para el Robot Matemático
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=10).json()
        precio = float(r['lastPrice'])
        variacion = float(r['priceChangePercent'])
        return precio, variacion
    except Exception as e:
        print(f"Error al obtener precios: {e}")
        return 0.0, 0.0

def generar_dashboard():
    tz_mx = pytz.timezone('America/Mexico_City')
    ahora = datetime.now(tz_mx).strftime('%Y-%m-%d %H:%M:%S')
    precio, var = obtener_datos()

    # --- LÓGICA DE LOS 3 SABIOS ROBOTS ---
    # Robot 1: Matemático
    r1 = "✅ PRECIO BAJO" if var < -2 else "⚠️ PRECIO ALTO" if var > 2 else "⚖️ ESTABLE"
    # Robot 2: Psicológico
    r2 = "😨 MIEDO (Oportunidad)" if var < -4 else "😐 MERCADO TRANQUILO"
    # Robot 3: Estratégico
    r3 = "💎 VISIÓN LARGO PLAZO" if precio < 95000 else "🛡️ PROTECCIÓN"
    
    consejo_final = f"R1: {r1} | R2: {r2} | R3: {r3}"

    # --- GUARDAR EN TU TABLA DE SUPABASE ---
    if precio > 0:
        try:
            # Aquí escribimos directamente en la tabla de tu imagen image_1eca86.png
            supabase.table("historial_precios").insert({
                "moneda": "BTC",
                "precio": precio,
                "fuente": "Binance",
                "consejo_robot": consejo_final
            }).execute()
            print("¡Éxito! Datos guardados en Supabase.")
        except Exception as e:
            print(f"Error al guardar en Supabase: {e}")

    # --- CREAR LA PÁGINA WEB ---
    html = f"""
    <body style="background:#0b0e11; color:white; font-family:sans-serif; text-align:center; padding:50px;">
        <div style="border:1px solid #2b2f36; padding:30px; border-radius:20px; display:inline-block; max-width:400px;">
            <h1 style="color:#f0b90b;">XTM CONSEJO DE SABIOS</h1>
            <h2 style="font-size:3em; margin:10px 0;">${precio:,.2f}</h2>
            <div style="background:#1e2329; padding:15px; border-radius:10px; text-align:left;">
                <p><b>Estado del Mercado:</b></p>
                <p style="color:#f0b90b;">{consejo_final}</p>
            </div>
            <p style="color:#848e9c; font-size:0.8em; margin-top:20px;">Memoria Activa en Supabase • {ahora}</p>
        </div>
    </body>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generar_dashboard()
