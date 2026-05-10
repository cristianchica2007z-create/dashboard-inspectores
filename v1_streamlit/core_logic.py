import pandas as pd
import datetime

def procesar_datos_sst(df_base, fecha_sel, supervisores_sel):
    """
    Procesa los datos de Preoperacional, Operacional y Ausentismo para un contrato específico.
    """
    if df_base is None or df_base.empty:
        return pd.DataFrame()

    # 1. Filtro inicial por fecha y supervisores
    mask = (df_base["fecha"] == fecha_sel) & (df_base["supervisor"].isin(supervisores_sel))
    df_filt = df_base[mask].copy()

    # 2. Filtro por el contrato específico del Eje
    df_eje = df_filt[df_filt["contrato"].astype(str).str.upper().str.strip() == "OFM-2025-014, EJE"].copy()
    
    if df_eje.empty:
        return pd.DataFrame()

    # 3. Agrupaciones por Tipo de Trabajo
    # Preoperacional
    df_pre = df_eje[df_eje["tipo de trabajo"].astype(str).str.upper().str.strip() == "PREOPERACIONAL - 2025 - EJE"].copy()
    agg_pre = df_pre.groupby("inspector").agg(
        HORA_PREOPERACIONAL=("hora final_parsed", lambda x: x.iloc[0] if not x.empty else pd.NaT)
    ).reset_index()

    # Operacional Final
    df_op = df_eje[df_eje["tipo de trabajo"].astype(str).str.upper().str.strip() == "OPERACIONAL FINAL - EJE"].copy()
    agg_op = df_op.groupby("inspector").agg(
        HORA_OPERACIONAL_FINAL=("hora final_parsed", lambda x: x.iloc[0] if not x.empty else pd.NaT)
    ).reset_index()

    # Ausentismo
    df_aus = df_eje[df_eje["tipo de trabajo"].astype(str).str.upper().str.strip() == "AUSENTISMO"].copy()
    agg_aus = df_aus.groupby("inspector").agg(
        TIEMPO_AUSENTISMO=("tiempo de tarea", lambda x: str(x.iloc[0]) if not x.empty else "00:00:00")
    ).reset_index()

    # 4. Consolidación de Resultados
    all_insps = pd.concat([agg_pre["inspector"], agg_op["inspector"], agg_aus["inspector"]]).unique()
    res = pd.DataFrame({"INSPECTOR": all_insps})
    
    res = res.merge(agg_pre, left_on="INSPECTOR", right_on="inspector", how="left").drop(columns="inspector")
    res = res.merge(agg_op, left_on="INSPECTOR", right_on="inspector", how="left").drop(columns="inspector")
    res = res.merge(agg_aus, left_on="INSPECTOR", right_on="inspector", how="left").drop(columns="inspector")

    # 5. Formateo de Texto
    res["HORA PREOPERACIONAL"] = res["HORA_PREOPERACIONAL"].apply(
        lambda x: x.strftime("%H:%M") if pd.notna(x) else "SIN PREOPERACIONAL"
    )
    res["HORA OPERACIONAL FINAL"] = res["HORA_OPERACIONAL_FINAL"].apply(
        lambda x: x.strftime("%H:%M") if pd.notna(x) else "SIN OPERACIONAL FINAL"
    )
    res["AUSENTISMO"] = res["TIEMPO_AUSENTISMO"].fillna("00:00:00").apply(
        lambda x: "SIN AUSENTISMO" if str(x) == "00:00:00" else str(x)
    )

    return res[["INSPECTOR", "HORA PREOPERACIONAL", "HORA OPERACIONAL FINAL", "AUSENTISMO"]]

def calcular_semaforo_sst(valor, tipo):
    """
    Determina si un valor debe estar en rojo basado en las reglas de negocio.
    """
    if tipo == "AUSENTISMO":
        if valor == "SIN AUSENTISMO": return True
        try:
            td = pd.to_timedelta(valor)
            if td < pd.Timedelta(minutes=30) or td > pd.Timedelta(hours=1, minutes=5):
                return True
        except: return False
    elif "SIN" in str(valor):
        return True
    return False