from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
import base64
import io
import os
import sys
from typing import Optional

# Añadir directorio raíz al path para importar shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.logic import process_bitacora, td_to_str, clean_contract

app = FastAPI(title="Dashboard Inspectores API")

# Configurar CORS para que React pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper para descargar de GitHub
def fetch_github_excel(repo: str, path: str, token: str):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()
        download_url = data.get("download_url")
        if download_url:
            resp = requests.get(download_url, headers=headers)
            return pd.read_excel(io.BytesIO(resp.content))
    return pd.DataFrame()

@app.get("/")
def read_root():
    return {"message": "API Dashboard Inspectores V2 está corriendo"}

@app.get("/summary")
def get_summary(repo: str, token: str):
    df_raw = fetch_github_excel(repo, "BITACORA.xlsx", token)
    if df_raw.empty:
        raise HTTPException(status_code=404, detail="No se pudo cargar la bitácora")
    
    df = process_bitacora(df_raw)
    
    # Filtrar solo hoy (simplificado para demo)
    hoy = df["fecha"].max() # O usar fecha actual
    df_hoy = df[df["fecha"] == hoy].copy()
    
    total_inspecciones = len(df_hoy)
    efectivas = df_hoy["efectiva"].sum()
    pct_efectividad = round((efectivas / total_inspecciones * 100), 1) if total_inspecciones > 0 else 0
    
    # Promedio recorrido
    prom_rec = td_to_str(df_hoy["tiempo_recorrido_td"].mean())
    
    return {
        "fecha": str(hoy),
        "total_inspecciones": total_inspecciones,
        "efectivas": int(efectivas),
        "pct_efectividad": pct_efectividad,
        "promedio_recorrido": prom_rec
    }

@app.get("/inspections")
def get_inspections(repo: str, token: str):
    df_raw = fetch_github_excel(repo, "BITACORA.xlsx", token)
    if df_raw.empty:
        return []
    
    df = process_bitacora(df_raw)
    hoy = df["fecha"].max()
    df_hoy = df[df["fecha"] == hoy].copy()
    
    # Formatear para JSON
    df_hoy["hora inicio"] = df_hoy["hora inicio_parsed"].apply(lambda x: x.strftime("%I:%M %p") if pd.notna(x) else "")
    df_hoy["hora final"] = df_hoy["hora final_parsed"].apply(lambda x: x.strftime("%I:%M %p") if pd.notna(x) else "")
    
    cols = ["inspector", "contrato", "hora inicio", "hora final", "estado", "cierre", "estado_puntualidad"]
    return df_hoy[cols].fillna("").to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
