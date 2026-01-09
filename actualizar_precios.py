import pandas as pd
import requests
import time
from datetime import datetime
import pytz
import os

def generar_excel_automatizado():
    tz_mexico = pytz.timezone('America/Mexico_City')
    # Configuramos inicio desde el 1 de enero 2026
    start_date = datetime(2026, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
    end_date = datetime.now(pytz.utc)

    symbol = "BTCUSDT"
    all_klines = []
    current_ts = int(start_date.timestamp() * 1000)
    end_ts = int(end_date.timestamp() * 1000)

    # Descarga de datos
    while current_ts < end_ts:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&startTime={current_ts}&limit=1000"
        data = requests.get(url).json()
        if not data or len(data) == 0: break
        all_klines.extend(data)
        current_ts = data[-1][0] + 60000 
        time.sleep(0.1)

    df = pd.DataFrame(all_klines, columns=['ts', 'op', 'hi', 'lo', 'cl', 'v', 'ct', 'qv', 'tr', 'tb', 'tq', 'i'])
    df['dt_utc'] = pd.to_datetime(df['ts'], unit='ms', utc=True)
    df['dt_mx'] = df['dt_utc'].dt.tz_convert(tz_mexico)
    
    meses = {1:"ENERO", 2:"FEBRERO", 3:"MARZO", 4:"ABRIL", 5:"MAYO", 6:"JUNIO", 7:"JULIO", 8:"AGOSTO", 9:"SEPTIEMBRE", 10:"OCTUBRE", 11:"NOVIEMBRE", 12:"DICIEMBRE"}
    
    res = pd.DataFrame()
    res['FECHA'] = df['dt_mx'].apply(lambda x: f"{x.year}/{meses[x.month]}/{x.day:02d}")
    res['HORA CDMX'] = df['dt_mx'].dt.strftime('%H:%M:%S')
    res['BINANCE'] = df['cl'].astype(float)
    res['EE.UU (NY)'] = df['dt_utc'].dt.tz_convert('America/New_York').dt.strftime('%H:%M:%S')
    res['EUROPA (LONDRES)'] = df['dt_utc'].dt.tz_convert('Europe/London').dt.strftime('%H:%M:%S')
    res['ASIA (HONG KONG)'] = df['dt_utc'].dt.tz_convert('Asia/Hong_Kong').dt.strftime('%H:%M:%S')
    res['grupo_hora'] = df['dt_mx'].dt.strftime('%Y%m%d%H')

    def styler_completo(x):
        styles = pd.DataFrame('', index=x.index, columns=x.columns)
        for g in x['grupo_hora'].unique():
            idx = x[x['grupo_hora'] == g].index
            hora_num = int(g[-2:])
            bg_row = 'background-color: #F2F2F2;' if hora_num % 2 == 0 else 'background-color: #FFFFFF;'
            for col in x.columns: styles.loc[idx, col] = bg_row
            
            precios = x.loc[idx, 'BINANCE']
            # AZUL: Máximo
            styles.loc[precios[precios == precios.max()].index, 'BINANCE'] = 'background-color: #0070C0; color: white; font-weight: bold;'
            # ROJO: Mínimo
            styles.loc[precios[precios == precios.min()].index, 'BINANCE'] = 'background-color: #FF0000; color: white; font-weight: bold;'
            # VERDE: Promedio
            idx_avg = (precios - precios.mean()).abs().idxmin()
            styles.loc[idx_avg, 'BINANCE'] = 'background-color: #00B050; color: white; font-weight: bold;'
        return styles

    final_styled = res.style.apply(styler_completo, axis=None)
    final_styled.to_excel('BITCOIN_REPORTE_DIARIO.xlsx', engine='openpyxl', index=False)

if __name__ == "__main__":
    generar_excel_automatizado()
