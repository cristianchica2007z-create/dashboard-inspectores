import pandas as pd
import os
import datetime
import json

# Mapeo maestro de inspectores a supervisores (Centralizado)
SUPERVISORES_DICT = {
    "ARIZA MARIN SERGIO": "ANDRES ARROYAVE", "ANDRES ARROYAVE": "ANDRES ARROYAVE",
    "BEDOYA DIEGO ALEJANDRO": "DANNY DE LA CRUZ", "DANNY DE LA CRUZ": "DANNY DE LA CRUZ",
    "CARVAJAL RESTREPO JUAN DAVID": "JANIER MARIN", "JANIER MARIN": "JANIER MARIN",
    "ECHEVERRY CARDONA JHON STIVEN": "JANIER MARIN", "GALLEGO CADAVID NORBEY": "DANNY DE LA CRUZ",
    "GIRALDO GARCIA SIGIFREDO": "ANDRES ARROYAVE", "LOPEZ PINEDA CESAR AUGUSTO": "JANIER MARIN",
    "NOREÑA GIRALDO GEOVANNY": "ANDRES ARROYAVE", "OSPINA CASTELLANOS ANDERSON": "CRISTIAN CHICA",
    "OSPINA RODRIGUEZ DANIEL ALBERTO": "ANDRES ARROYAVE", "RUIZ DILON MARLON ANDREY": "ANDRES ARROYAVE",
    "LARGO OSORIO JOSE OMAR": "ANDRES ARROYAVE", "PULGARIN QUINTERO JULIAN ANDRES": "DANNY DE LA CRUZ",
    "TAYACK TRUJILLO DEIVER EVELIO": "ANDRES ARROYAVE", "PATIÑO CIFUENTES RICARDO": "JANIER MARIN", "VARGAS FRANCO JHON EDISON": "CRISTIAN CHICA",
    "CARDONA CANO NELSON": "CRISTIAN CHICA", "CARDONA OROZCO JULIAN ANDRES": "ANDRES ARROYAVE",
    "GRISALES CUERVO JUAN DAVID": "JANIER MARIN", "LEON MARIN LEONARDO FABIO": "JANIER MARIN",
    "CARDONA CASTANO DIDIER ORLANDO": "CRISTIAN CHICA",
    "TORRES HERNANDEZ JOHN JAMES": "ANDRES ARROYAVE", "COBO HOYOS JUAN MANUEL": "CRISTIAN CHICA",
    "OSPINA NARANJO BERNARDO": "CRISTIAN CHICA", "COGOLLO FIGUEROA RANDY": "DANNY DE LA CRUZ",
    "ARIAS TORO YEISON": "DANNY DE LA CRUZ", "MIRANDA FRANCO EFRAIN": "DANNY DE LA CRUZ",
    "ARDILA MORA GUSTAVO ADOLFO": "DANNY DE LA CRUZ", "LOPEZ VELEZ ESTEBAN": "JANIER MARIN",
    "GALEANO GRISALEZ RICARDO": "DANNY DE LA CRUZ", "CAICEDO ESCOBAR JUNIOR SANTIAGO": "JANIER MARIN",
    "BUITRAGO RAMIREZ LEONARD": "CRISTIAN CHICA",
    "BORJAS WILLY ALEXANDER": "ANDRES ARROYAVE", "MARIN LEON JAISSON JOAQUIN": "CRISTIAN CHICA",
    "AMAYA HINCAPIE JUAN CARLOS": "CRISTIAN CHICA", "BEDOYA SANCHEZ CRISTIAN DAVID": "ANDRES ARROYAVE",
    "RAMIREZ WILSON ENRIQUE": "CRISTIAN CHICA", "CANO MORALES JIMY ALFREDO": "ANDRES ARROYAVE",
    "CASTRO CASTAÑO JUAN DAVID": "CRISTIAN CHICA",   "VILLA LOAIZA JHEISON ESTIBEN": "CRISTIAN CHICA", "CÁRDENAS GALIANO HAROLD MAURICIO": "JANIER MARIN",
    "VARGAS CORREA VICTOR ALFONSO": "DANNY DE LA CRUZ", "VILLA MERA CHRISTIAN DAVID": "JANIER MARIN",
    "AVENDAÑO GARCIA JUAN NEPOMUCENO": "ANDRES ARROYAVE", "PELAEZ TATIS GABRIEL ESTEBAN": "CRISTIAN CHICA",
    "CHICA RAMIREZ CRISTIAN ALBERTO": "CRISTIAN CHICA"
}

VALORES_EFECTIVOS = [
    "INSPECCIONADA",
    "INSPECCIONADA CON DEFECTO NO CRITICO",
    "INSPECCIONADA CON DEFECTO CRITICO",
    "CERTIFICADA",
    "CERTIFICADA CON NOVEDAD"
]

def clean_contract(c):
    if pd.isna(c): return ""
    s = str(c).strip()
    if s.endswith('.0'): s = s[:-2]
    return s

def td_to_str(td):
    if pd.isna(td) or td is None: return "—"
    s = int(td.total_seconds())
    h = s // 3600
    m = (s % 3600) // 60
    s2 = s % 60
    return f"{h}h {m}m {s2}s" if h > 0 else f"{m}m {s2}s"

def process_bitacora(df):
    """Procesa el dataframe de bitácora con toda la lógica compartida."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "contrato" in df.columns:
        df["contrato"] = df["contrato"].apply(clean_contract)
        
    if "prioridad" in df.columns:
        df["prioridad"] = df["prioridad"].astype(str).str.strip().str.capitalize()
        
    if "inspector" in df.columns:
        df["inspector"] = df["inspector"].astype(str).str.upper().str.strip().str.replace(r"\s+", " ", regex=True)
        
    df["supervisor"] = df["inspector"].map(SUPERVISORES_DICT).fillna("SIN SUPERVISOR")
    
    if "fecha de ejecucion" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce").dt.date
        
    for col in ["hora inicio", "hora inicio de recorrido", "hora final"]:
        if col in df.columns:
            df[col + "_parsed"] = pd.to_datetime(df[col].astype(str), errors='coerce').dt.time

    if "tiempo de tarea" in df.columns:
        df["tiempo_tarea_td"] = pd.to_timedelta(df["tiempo de tarea"].astype(str), errors="coerce")

    # 1. Marcación de Efectiva
    if "cierre" in df.columns:
        df["efectiva"] = df["cierre"].isin(VALORES_EFECTIVOS)
    else:
        df["efectiva"] = False
        
    # 2. Tiempo de Recorrido
    if "hora inicio_parsed" in df.columns and "hora inicio de recorrido_parsed" in df.columns:
        def calc_recorrido(row):
            hi = row.get("hora inicio_parsed")
            hr = row.get("hora inicio de recorrido_parsed")
            if not isinstance(hi, datetime.time) or not isinstance(hr, datetime.time):
                return pd.NaT
            dt_hi = datetime.datetime.combine(datetime.date.today(), hi)
            dt_hr = datetime.datetime.combine(datetime.date.today(), hr)
            return dt_hi - dt_hr if dt_hi >= dt_hr else pd.NaT
        df["tiempo_recorrido_td"] = df.apply(calc_recorrido, axis=1)
    else:
        df["tiempo_recorrido_td"] = pd.NaT
        
    # 3. Puntualidad
    hora_oficial = datetime.time(7, 30)
    def calc_estado(h):
        if not isinstance(h, datetime.time): return "SIN INICIO"
        h1 = datetime.datetime.combine(datetime.date.today(), h)
        h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
        m = int((h1 - h2).total_seconds() / 60)
        if m <= 0: return "Puntual"
        if m <= 15: return "Tarde"
        return "Muy tarde"
        
    if "hora inicio_parsed" in df.columns:
        df["estado_puntualidad"] = df["hora inicio_parsed"].apply(calc_estado)

    return df
