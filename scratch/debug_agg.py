import pandas as pd
import datetime
import sys
import os
import io
import requests

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.logic import process_bitacora, td_to_str

TOKEN = "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"
REPO = "cristianchica2007z-create/dashboard-inspectores"

def debug():
    print("Descargando datos...")
    headers = {"Authorization": f"Bearer {TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/BITACORA.xlsx"
    r = requests.get(url, headers=headers)
    data = r.json()
    resp = requests.get(data['download_url'], headers=headers)
    df_raw = pd.read_excel(io.BytesIO(resp.content))
    
    print("Procesando...")
    df = process_bitacora(df_raw)
    
    fecha = df["fecha"].max()
    print(f"Fecha: {fecha}")
    df_f = df[df["fecha"] == fecha].copy()
    
    print(f"Total filas: {len(df_f)}")
    
    # Simular agregación
    print("Agregando...")
    try:
        # Normalización extra antes de agrupar
        df_f["inspector"] = df_f["inspector"].astype(str).str.strip().str.upper()

        agg = df_f.groupby("inspector").agg(
            supervisor=("supervisor", "first"),
            hora_inicio=("hora inicio_parsed", "min"),
            hora_final=("hora final_parsed", "max"),
            localidad=("localidad", lambda x: x.mode()[0] if not x.mode().empty else "—"),
            estado=("estado_puntualidad", "first"),
            total_ordenes=("inspector", "count"),
            ordenes_efectivas=("efectiva", "sum"),
            tiempo_tarea_avg=("tiempo_tarea_td", "mean"),
            tiempo_recorrido_avg=("tiempo_recorrido_td", "mean")
        ).reset_index()
        
        print("Agregación exitosa.")
        
        agg["ordenes_sin_recorrido"] = agg["total_ordenes"] - agg["ordenes_efectivas"]
        agg["efectividad_pct"] = (agg["ordenes_efectivas"] / agg["total_ordenes"] * 100).round(1)
        
        print("Formateando tiempos...")
        agg["hora_inicio"] = agg["hora_inicio"].apply(lambda x: x.strftime("%H:%M:%S") if pd.notna(x) else "—")
        agg["hora_final"] = agg["hora_final"].apply(lambda x: x.strftime("%H:%M:%S") if pd.notna(x) else "—")
        agg["promedio_tiempo_tarea"] = agg["tiempo_tarea_avg"].apply(td_to_str)
        agg["promedio_tiempo_recorrido"] = agg["tiempo_recorrido_avg"].apply(td_to_str)
        
        final_data = agg.drop(columns=["tiempo_tarea_avg", "tiempo_recorrido_avg"]).to_dict(orient="records")
        print("Conversión a dict exitosa.")
        # print(final_data[0])
        
    except Exception as e:
        print(f"ERROR EN AGREGACION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug()
