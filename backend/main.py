from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
import base64
import io
import os
import sys
from typing import Optional, List
import time
import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# Añadir directorio raíz al path para importar shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shared.logic import process_bitacora, td_to_str, clean_contract
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dashboard Inspectores API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sistema de Caché en Memoria
cache_db = {}
CACHE_EXPIRATION = 600 # 10 minutos

def fetch_github_excel(repo: str, path: str, token: str):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data_json = r.json()
            download_url = data_json.get("download_url")
            if download_url:
                resp = requests.get(download_url, headers=headers, timeout=60)
                return pd.read_excel(io.BytesIO(resp.content))
    except Exception as e:
        logger.error(f"Error descargando {path}: {e}")
    return pd.DataFrame()

def get_data(repo: str, token: str):
    cache_key = f"{repo}_processed"
    now = time.time()
    
    if cache_key in cache_db:
        df, timestamp = cache_db[cache_key]
        if now - timestamp < CACHE_EXPIRATION:
            return df
            
    df_raw = fetch_github_excel(repo, "BITACORA.xlsx", token)
    if df_raw.empty: return pd.DataFrame()
    
    df = process_bitacora(df_raw)
    cache_db[cache_key] = (df, now)
    return df

def avg_time_v2(series):
    if series.empty: return "—"
    total_secs = []
    for t in series:
        if pd.notna(t):
            if hasattr(t, 'hour'):
                total_secs.append(t.hour * 3600 + t.minute * 60 + t.second)
            else:
                total_secs.append(t.seconds)
    if not total_secs: return "—"
    avg_s = sum(total_secs) / len(total_secs)
    h, m = int(avg_s // 3600), int((avg_s % 3600) // 60)
    suffix = "AM" if h < 12 else "PM"
    if h > 12: h -= 12
    if h == 0: h = 12
    return f"{h:02d}:{m:02d} {suffix}"

@app.get("/")
def read_root():
    return {"message": "API Dashboard Inspectores V2 está activo"}

@app.get("/summary")
def get_summary(repo: str, token: str, fecha: Optional[str] = None, supervisor: Optional[str] = None):
    df = get_data(repo, token)
    if df.empty: return {"total_inspecciones": 0, "efectivas": 0, "pct_efectividad": 0, "promedio_recorrido": "—"}
    
    if fecha:
        fechas_list = [f.strip() for f in fecha.split(',')]
        df_f = df[df["fecha"].astype(str).isin(fechas_list)].copy()
    else:
        df_f = df[df["fecha"] == df["fecha"].max()].copy()
    
    if supervisor and str(supervisor).upper() != "TODOS":
        sups_list = [s.strip().upper() for s in supervisor.split(',')]
        df_f = df_f[df_f["supervisor"].astype(str).str.strip().str.upper().isin(sups_list)]
        
    total = len(df_f)
    efectivas = df_f["efectiva"].sum()
    pct = round((efectivas / total * 100), 1) if total > 0 else 0
    
    df_ini = df_f.dropna(subset=["hora inicio_parsed"]).groupby(["inspector", "fecha"])["hora inicio_parsed"].min()
    df_fin = df_f.dropna(subset=["hora final_parsed"]).groupby(["inspector", "fecha"])["hora final_parsed"].max()
    
    prom_tarea_td = df_f[df_f["efectiva"] == True]["tiempo_tarea_td"].mean()
    prom_rec = td_to_str(df_f["tiempo_recorrido_td"].mean())
    
    return {
        "total_inspecciones": total,
        "efectivas": int(efectivas),
        "pct_efectividad": pct,
        "promedio_recorrido": prom_rec,
        "promedio_tarea": td_to_str(prom_tarea_td),
        "inicio_promedio": avg_time_v2(df_ini),
        "fin_promedio": avg_time_v2(df_fin)
    }

@app.get("/inspections_agregada")
def get_inspections_agregada(repo: str, token: str, fecha: Optional[str] = None, supervisor: Optional[str] = None):
    df = get_data(repo, token)
    if df.empty: return []
    
    if fecha:
        fechas_list = [f.strip() for f in fecha.split(',')]
        df_f = df[df["fecha"].astype(str).isin(fechas_list)].copy()
    else:
        df_f = df[df["fecha"] == df["fecha"].max()].copy()
        
    if supervisor and str(supervisor).upper() != "TODOS":
        sups_list = [s.strip().upper() for s in supervisor.split(',')]
        df_f = df_f[df_f["supervisor"].astype(str).str.strip().str.upper().isin(sups_list)]
    
    if df_f.empty: return []

    df_f["inspector"] = df_f["inspector"].astype(str).str.strip().str.upper()

    daily_starts = df_f.dropna(subset=["hora inicio_parsed"]).groupby(["inspector", "fecha"])["hora inicio_parsed"].min().reset_index()
    daily_ends = df_f.dropna(subset=["hora final_parsed"]).groupby(["inspector", "fecha"])["hora final_parsed"].max().reset_index()
    
    def time_to_seconds(t):
        return t.hour * 3600 + t.minute * 60 + t.second

    daily_starts["secs"] = daily_starts["hora inicio_parsed"].apply(time_to_seconds)
    daily_ends["secs"] = daily_ends["hora final_parsed"].apply(time_to_seconds)
    
    agg_times = daily_starts.groupby("inspector")["secs"].mean().reset_index()
    agg_ends = daily_ends.groupby("inspector")["secs"].mean().reset_index()

    agg = df_f.groupby("inspector").agg(
        supervisor=("supervisor", "first"),
        localidad=("localidad", lambda x: x.mode()[0] if not x.mode().empty else "—"),
        total_ordenes=("inspector", "count"),
        ordenes_efectivas=("efectiva", "sum"),
        tiempo_tarea_avg=("tiempo_tarea_td", "mean"),
        tiempo_recorrido_avg=("tiempo_recorrido_td", "mean")
    ).reset_index()

    agg = agg.merge(agg_times.rename(columns={"secs": "ini_secs"}), on="inspector", how="left")
    agg = agg.merge(agg_ends.rename(columns={"secs": "fin_secs"}), on="inspector", how="left")

    def secs_to_time_str(s):
        if pd.isna(s): return "—"
        h, m = int(s // 3600), int((s % 3600) // 60)
        return f"{h:02d}:{m:02d}:00"

    agg["hora_inicio"] = agg["ini_secs"].apply(secs_to_time_str)
    agg["hora_final"] = agg["fin_secs"].apply(secs_to_time_str)
    
    hora_oficial_secs = 7 * 3600 + 30 * 60
    def calc_estado_secs(s):
        if pd.isna(s): return "SIN INICIO"
        diff = (s - hora_oficial_secs) / 60
        if diff <= 0: return "Puntual"
        if diff <= 15: return "Tarde"
        return "Muy tarde"

    agg["estado"] = agg["ini_secs"].apply(calc_estado_secs)
    agg["ordenes_sin_recorrido"] = agg["total_ordenes"] - agg["ordenes_efectivas"]
    agg["efectividad_pct"] = (agg["ordenes_efectivas"] / agg["total_ordenes"] * 100).round(1)
    agg["promedio_tiempo_tarea"] = agg["tiempo_tarea_avg"].apply(td_to_str)
    agg["promedio_tiempo_recorrido"] = agg["tiempo_recorrido_avg"].apply(td_to_str)
    
    return agg.drop(columns=["tiempo_tarea_avg", "tiempo_recorrido_avg", "ini_secs", "fin_secs"]).to_dict(orient="records")

@app.get("/config")
def get_config(repo: str, token: str):
    df = get_data(repo, token)
    if df.empty: return {"fechas": [], "supervisores": []}
    fechas = sorted(df["fecha"].unique().astype(str).tolist(), reverse=True)
    supervisores = sorted(df["supervisor"].unique().tolist())
    return {"fechas": fechas, "supervisores": ["TODOS"] + supervisores}

@app.get("/agendas")
def get_agendas(repo: str, token: str, zona: Optional[str] = None):
    logger.info("Fetching agendas...")
    # Cargar bitácora raw para agendas (necesitamos estados originales)
    df_raw = fetch_github_excel(repo, "BITACORA.xlsx", token)
    if df_raw.empty: 
        logger.warning("Bitácora vacía.")
        return {"agendas": [], "kpis": {"alerta": 0, "proximas": 0, "finalizadas": 0}, "zonas": []}
    
    df = df_raw.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    # Filtro de grupos flexible (como en shared/logic.py)
    if "grupo" in df.columns:
        df["grupo"] = df["grupo"].astype(str).str.upper().str.strip()
        df = df[df["grupo"].str.startswith("INSP", na=False)].copy()
    
    # Zonas disponibles ANTES del filtro de zona
    zonas_disponibles = sorted(df["grupo"].unique().tolist()) if "grupo" in df.columns else []
    
    # Aplicar filtro de zona si se especificó
    if zona and zona.upper() != "TODAS":
        df = df[df["grupo"] == zona.upper()].copy()
    
    logger.info(f"Filas tras filtro de grupo/zona: {len(df)}")
    if df.empty:
        return {"agendas": [], "kpis": {"alerta": 0, "proximas": 0, "finalizadas": 0}}

    # Fechas
    df["fecha de visita"] = pd.to_datetime(df["fecha de visita"], errors="coerce")
    df["fecha de ejecucion"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce")
    
    # Cargar programación para hora agenda
    df_prog = fetch_github_excel(repo, "PROGRAMACION.xlsx", token)
    if not df_prog.empty:
        logger.info("Merging with PROGRAMACION.xlsx")
        df_prog.columns = [str(c).strip().lower() for c in df_prog.columns]
        if "contrato" in df_prog.columns and "hora agenda" in df_prog.columns:
            df["contrato"] = df["contrato"].astype(str).str.strip()
            df_prog["contrato"] = df_prog["contrato"].astype(str).str.strip()
            df_prog = df_prog.drop_duplicates(subset=["contrato"])
            df = df.merge(df_prog[["contrato", "hora agenda"]], on="contrato", how="left")
            
    ahora = datetime.datetime.now()
    
    def calc_alerta(row):
        visita = row["fecha de visita"]
        if pd.isna(visita): return "OK"
        # Si la fecha de visita es futura, no es alerta
        if visita.date() > ahora.date(): return "OK"
        
        ha = str(row.get("hora agenda", "")).upper()
        keywords = ["TRANSCURSO DE LA MAÑANA", "TRANSCURSO DE LA TARDE", "TRANSCURSO DEL DIA", "TRANSCURSO DEL DÍA", "JORNADA MAÑANA", "JORNADA TARDE", "JORNADA DE MAÑANA"]
        if any(txt in ha for txt in keywords): return "OK"
        
        # Si es para hoy o pasado y no tiene keywords de "transcurso", es alerta
        return "ALERTA"
        
    df["estado_alerta"] = df.apply(calc_alerta, axis=1)
    df["estado_str"] = df["estado"].astype(str).str.upper()
    df["prioridad_str"] = df["prioridad"].astype(str).str.upper()
    
    # KPIs
    finalizadas = df[df["estado_str"].str.contains("FINALIZAD", na=False)]
    # Próximas: Asignadas sin fecha de ejecución (pendientes)
    proximas = df[(df["estado_str"].str.contains("ASIGNAD", na=False)) & (df["fecha de ejecucion"].isna())]
    # Alertas: Asignadas, prioridad ALTA (incluye ALTA VALLE, etc.), estado alerta
    alertas = df[(df["estado_str"].str.contains("ASIGNAD", na=False)) & (df["prioridad_str"].str.startswith("ALTA")) & (df["estado_alerta"] == "ALERTA")]
    

    
    logger.info(f"KPIs: Alertas={len(alertas)}, Proximas={len(proximas)}, Finalizadas={len(finalizadas)}")

    # Seleccionar columnas a enviar, incluyendo prioridad para filtro interno
    res_df = df[["inspector", "contrato", "direccion", "estado", "fecha de visita", "localidad", "detalle de tarea", "estado_alerta", "grupo", "fecha de ejecucion", "prioridad"]].copy()
    
    # Renombrar para evitar espacios y coincidir con el frontend
    res_df = res_df.rename(columns={
        "fecha de visita": "fecha_de_visita",
        "detalle de tarea": "detalle_de_tarea",
        "fecha de ejecucion": "fecha_de_ejecucion"
    })
    
    # Limpiar NaN en campos de texto (causa error JSON)
    for col in ["inspector", "contrato", "direccion", "estado", "localidad", "detalle_de_tarea", "estado_alerta", "grupo"]:
        if col in res_df.columns:
            res_df[col] = res_df[col].fillna("").astype(str)
    
    res_df["fecha_visita_str"] = pd.to_datetime(res_df["fecha_de_visita"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("")
    # Convertir Timestamps a strings para JSON
    res_df["fecha_de_visita"] = res_df["fecha_de_visita"].astype(str).replace("NaT", "")
    res_df["fecha_de_ejecucion"] = res_df["fecha_de_ejecucion"].astype(str).replace("NaT", "")
    
    # Reemplazar todos los NaN/inf restantes
    res_df = res_df.fillna("").replace([float("inf"), float("-inf")], "")
    
    return {
        "agendas": res_df.to_dict(orient="records"),
        "kpis": {
            "alerta": int(len(alertas)),
            "proximas": int(len(proximas)),
            "finalizadas": int(len(finalizadas))
        },
        "zonas": zonas_disponibles
    }

@app.get("/performance_report")
def get_performance_report(repo: str, token: str, fecha: str, supervisor: Optional[str] = None):
    df = get_data(repo, token)
    if df.empty: return {"report": {}}
    fechas_list = [f.strip() for f in fecha.split(',')]
    df_f = df[df["fecha"].astype(str).isin(fechas_list)].copy()
    if supervisor and str(supervisor).upper() != "TODOS":
        sups_list = [s.strip().upper() for s in supervisor.split(',')]
        df_f = df_f[df_f["supervisor"].astype(str).str.strip().str.upper().isin(sups_list)]
    if df_f.empty: return {"report": {}}
    insp_agg = df_f.groupby("inspector").agg(efectivas=("efectiva", "sum"), total=("inspector", "count"), t_recorrido=("tiempo_recorrido_td", "mean"), t_tarea=("tiempo_tarea_td", "mean"))
    daily_starts = df_f.dropna(subset=["hora inicio_parsed"]).groupby(["inspector", "fecha"])["hora inicio_parsed"].min().reset_index()
    def time_to_seconds(t): return t.hour * 3600 + t.minute * 60 + t.second
    daily_starts["secs"] = daily_starts["hora inicio_parsed"].apply(time_to_seconds)
    avg_starts = daily_starts.groupby("inspector")["secs"].mean()
    insp_agg["sin_recorrido"] = insp_agg["total"] - insp_agg["efectivas"]
    insp_agg["avg_start_secs"] = avg_starts
    def secs_to_str(s):
        if pd.isna(s): return "—"
        h, m = int(s // 3600), int((s % 3600) // 60)
        suffix = "AM" if h < 12 else "PM"
        if h > 12: h -= 12
        if h == 0: h = 12
        return f"{h:02d}:{m:02d} {suffix}"
    report = {
        "mas_efectivas": {"val": int(insp_agg["efectivas"].max()), "name": insp_agg["efectivas"].idxmax()},
        "menos_efectivas": {"val": int(insp_agg["efectivas"].min()), "name": insp_agg["efectivas"].idxmin()},
        "mas_sin_recorrido": {"val": int(insp_agg["sin_recorrido"].max()), "name": insp_agg["sin_recorrido"].idxmax()},
        "inicio_mas_tarde": {"val": secs_to_str(insp_agg["avg_start_secs"].max()), "name": insp_agg["avg_start_secs"].idxmax()},
        "recorrido_mas_extenso": {"val": td_to_str(insp_agg["t_recorrido"].max()), "name": insp_agg["t_recorrido"].idxmax()},
        "mas_tiempo_tarea": {"val": td_to_str(insp_agg["t_tarea"].max()), "name": insp_agg["t_tarea"].idxmax()}
    }
    return {"report": report}

@app.get("/inactive_inspectors")
def get_inactive_inspectors(repo: str, token: str, fecha: str, supervisor: Optional[str] = None):
    df = get_data(repo, token)
    if df.empty: return []
    last_date = df["fecha"].max()
    universo_df = df[df["fecha"] >= (last_date - pd.Timedelta(days=30))].copy()
    if supervisor and str(supervisor).upper() != "TODOS":
        sups_list = [s.strip().upper() for s in supervisor.split(',')]
        universo_df = universo_df[universo_df["supervisor"].astype(str).str.strip().str.upper().isin(sups_list)]
    universo = set(universo_df["inspector"].unique())
    activos_hoy = set(df[df["fecha"].astype(str) == fecha]["inspector"].unique())
    inactivos = sorted(list(universo - activos_hoy))
    res = []
    for name in inactivos:
        sup_mode = universo_df[universo_df["inspector"] == name]["supervisor"].mode()
        sup = sup_mode.iloc[0] if not sup_mode.empty else "SIN SUPERVISOR"
        res.append({"inspector": name, "supervisor": sup})
    return res

@app.post("/upload")
async def upload_file(repo: str, token: str, file: UploadFile = File(...)):
    try:
        content = await file.read()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        url = f"https://api.github.com/repos/{repo}/contents/BITACORA.xlsx"
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        payload = {"message": f"Upload via Dashboard - {datetime.datetime.now()}", "content": base64.b64encode(content).decode("utf-8"), "branch": "main"}
        if sha: payload["sha"] = sha
        r_put = requests.put(url, headers=headers, json=payload)
        if r_put.status_code in [200, 201]:
            if f"{repo}_processed" in cache_db: del cache_db[f"{repo}_processed"]
            
            # Actualizar metadata para que el dashboard muestre la hora de actualización
            info_url = f"https://api.github.com/repos/{repo}/contents/BITACORA_INFO.json"
            r_info = requests.get(info_url, headers=headers)
            sha_info = r_info.json().get("sha") if r_info.status_code == 200 else None
            
            info_data = {
                "ultima_actualizacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "usuario_actualizo": "Dashboard V2"
            }
            info_payload = {
                "message": "Update BITACORA_INFO.json via V2",
                "content": base64.b64encode(json.dumps(info_data).encode()).decode(),
                "branch": "main"
            }
            if sha_info: info_payload["sha"] = sha_info
            requests.put(info_url, headers=headers, json=info_payload)
            
            return {"message": "Éxito"}
        raise HTTPException(status_code=r_put.status_code, detail=r_put.text)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
