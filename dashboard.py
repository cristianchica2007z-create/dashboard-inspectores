import streamlit as st
import pandas as pd
import os
import plotly.express as px


# ---------------------------------------------------
# ✅ CONFIGURACIÓN GENERAL DEL DASHBOARD
# ---------------------------------------------------
st.set_page_config(
    page_title="Dashboard Inspectores",
    layout="wide"
)
st.title("📊 Dashboard Inspectores eyc")
st.title("⏰ Contro Operación")
# ---------------------------------------------------
# ✅ CREAR PESTAÑAS
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📦 Inventario Papelería",
    "🕒 Seguimiento Diario",
    "📈 Gráficas Generales"
])

# ---------------------------------------------------
# ✅ PESTAÑA 1: INVENTARIO DE PAPELERÍA
# ---------------------------------------------------

# ---------------------------------------------------
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA (FINAL ESTABLE)
# ---------------------------------------------------
with tab1:
    st.subheader("📦 Control de entrega de papelería e inventario")
    archivo_inventario = "inventario.xlsx"
    # Crear archivo si no existe
    if not os.path.exists(archivo_inventario):
        df_init = pd.DataFrame(columns=[
            "Fecha", "Sede", "Inspector",
            "Responsable", "Observación", "Ítems"
        ])
        df_init.to_excel(archivo_inventario, index=False, engine="openpyxl")
    df_inv = pd.read_excel(archivo_inventario, engine="openpyxl")
    # =================================================
    # ✅ FORMULARIO (SE LIMPIA AL GUARDAR)
    # =================================================
    with st.form("form_entrega", clear_on_submit=True):
        # -------- DATOS GENERALES --------
        col1, col2, col3 = st.columns(3)
        with col1:
            sede = st.selectbox("Sede", ["CALDAS", "RISARALDA"], key="form_sede")
        with col2:
            inspector = st.selectbox(
                "Inspector", inspectores_lista, key="form_inspector"
            )
        with col3:
            fecha = st.date_input("Fecha", key="form_fecha")
        col4, col5 = st.columns([1, 2])
        with col4:
            responsable = st.selectbox(
                "Responsable",
                [
                    "JUAN DIEGO SANCHEZ",
                    "CRISTIAN CHICA",
                    "ANDRES ARROYAVE",
                    "MARIA CAMILA",
                    "JANIER",
                    "DANNY DE LA CRUZ"
                ],
                key="form_responsable"
            )
        with col5:
            observacion = st.text_input(
                "Observación (opcional)", key="form_obs"
            )
        # -------- ÍTEMS --------
        st.markdown("### Ítems entregados")
        items_def = [
            "Stickers 🔵", "Cepo 🔒", "Guantes 🧤", "Piernera 🦿",
            "Monogafas 🥽", "Llaves de cepo 🗝️", "Formatos 📄",
            "Sellos 🕹️", "Papelería general 📦"
        ]
        items_seleccionados = []
        filas = [items_def[i:i+4] for i in range(0, len(items_def), 4)]
        for f_idx, fila in enumerate(filas):
            cols = st.columns(4)
            for c_idx, item in enumerate(fila):
                with colsmarcar = st.checkbox(
                        item, key=f"chk_{f_idx}_{c_idx}"
                    )
                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=0,
                        step=1,
                        label_visibility="collapsed",
                        key=f"qty_{f_idx}_{c_idx}"
                    )
                    if marcar and cantidad > 0:
                        items_seleccionados.append(f"{item} x{cantidad}")
        submitted = st.form_submit_button("✅ Guardar entrega")
    # =================================================
    # ✅ GUARDAR ENTREGA
    # =================================================
    if submitted:
        if not items_seleccionados:
            st.warning("⚠️ Debes seleccionar al menos un ítem con cantidad.")
        else:
            nueva_fila = pd.DataFrame({
                "Fecha": [fecha.strftime("%Y-%m-%d")],
                "Sede": [sede],
                "Inspector": [inspector],
                "Responsable": [responsable],
                "Observación": [observacion],
                "Ítems": [", ".join(items_seleccionados)]
            })
            df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)
            df_inv.to_excel(archivo_inventario, index=False, engine="openpyxl")
            subir_a_github(archivo_inventario)
            st.success("✅ Entrega registrada y formulario limpio")
    # =================================================
    # ✅ HISTORIAL + FILTRO + EDICIÓN
    # =================================================
    st.markdown("### 📋 Historial de entregas")
    filtro_inspector = st.selectbox(
        "Filtrar por inspector",
        ["TODOS"] + inspectores_lista,
        key="filtro_hist"
    )
    df_hist = df_inv.copy()
    if filtro_inspector != "TODOS":
        df_hist = df_hist[df_hist["Inspector"] == filtro_inspector]
    df_editado = st.data_editor(
        df_hist,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_hist"
    )
    if st.button("💾 Guardar cambios del historial", key="btn_hist"):
        df_editado.to_excel(archivo_inventario, index=False, engine="openpyxl")
        subir_a_github(archivo_inventario)
        st.success("✅ Cambios del historial guardados")
    # =================================================
    # ✅ RESUMEN MENSUAL CONSOLIDADO
    # =================================================
    st.markdown("## 📊 Consumo mensual consolidado por ítem")
    df_cons = df_inv.copy()
    df_cons["Fecha"] = pd.to_datetime(df_cons["Fecha"], errors="coerce")
    df_cons["Mes"] = df_cons["Fecha"].dt.to_period("M").astype(str)
    registros = []
    for _, row in df_cons.iterrows():
        if pd.isna(row["Ítems"]):
            continue
        for it in row["Ítems"].split(","):
            it = it.strip()
            if " x" in it:
                nom, cant = it.rsplit(" x", 1)
                cant = int(cant)
            else:
                nom = it
                cant = 1
            registros.append({
                "Mes": row["Mes"],
                "Ítem": nom,
                "Cantidad": cant
            })
    df_plot = pd.DataFrame(registros)
    if not df_plot.empty:
        df_plot = df_plot.groupby(
            ["Mes", "Ítem"], as_index=False
        ).sum()
        fig = px.bar(
            df_plot,
            x="Mes",
            y="Cantidad",
            color="Ítem",
            barmode="group",
            text="Cantidad",
            title="Consumo mensual consolidado por ítem"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis=dict(type="category"),
            xaxis_title="Mes",
            yaxis_title="Cantidad entregada",
            legend_title="Ítem"
        )
        st.plotly_chart(fig, use_container_width=True)



# -----------------------------------------------------
# ✅ PESTAÑA 2: SEGUIMIENTO DIARIO — VERSIÓN FINAL
# -----------------------------------------------------
with tab2:
    st.subheader("Control de horario de inspectores")
    st.write("### Cargar archivo de bitácora (formato XLSX recomendado)")
    archivo = st.file_uploader("Sube el archivo de bitácora", type=["xls", "xlsx"])
    if archivo:
        import numpy as np
        import datetime
        # -----------------------------------------------------
        # Funciones utilitarias
        # -----------------------------------------------------
        def hora_to_decimal(hora):
            if hora == "SIN HORA" or hora is None:
                return None
            return hora.hour + hora.minute/60 + hora.second/3600
        def decimal_to_hora(decimal):
            if decimal is None or pd.isna(decimal):
                return None
            h = int(decimal)
            m = int((decimal - h) * 60)
            s = int((((decimal - h) * 60) - m) * 60)
            return datetime.time(h, m, s)
        def hora_to_string(hora):
            if hora is None:
                return "—"
            return hora.strftime("%I:%M %p")
        def parse_hora(valor):
            try:
                return pd.to_datetime(valor, format="%H:%M").time()
            except:
                try:
                    return pd.to_datetime(str(valor)).time()
                except:
                    return None
        def parse_tiempo_tarea(valor):
            try:
                return pd.to_timedelta(str(valor))
            except:
                return pd.NaT
        def td_to_str(td):
            if pd.isna(td):
                return "—"
            s = int(td.total_seconds())
            h = s // 3600
            m = (s % 3600) // 60
            s2 = s % 60
            return f"{h}h {m}m {s2}s" if h > 0 else f"{m}m {s2}s"
        # -----------------------------------------------------
        # 1. Cargar archivo
        # -----------------------------------------------------
        df = pd.read_excel(archivo)
        # -----------------------------------------------------
        # 2. Normalizar columnas
        # -----------------------------------------------------
        df.columns = df.columns.str.strip().str.lower()
        columnas = [
            "fecha de ejecucion","hora inicio","hora final",
            "inspector","localidad","cierre","tiempo de tarea"
        ]
        for col in columnas:
            if col not in df.columns:
                st.error(f"❌ Falta la columna: {col}")
                st.stop()
        # -----------------------------------------------------
        # NORMALIZAR NOMBRES (alto nivel)
        # -----------------------------------------------------
        df["inspector"] = (
            df["inspector"]
            .astype(str)
            .str.upper()
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
        df["localidad"] = (
            df["localidad"]
            .astype(str)
            .str.upper()
            .str.strip()
        )
        # -----------------------------------------------------
        # Convertir horas y fechas
        # -----------------------------------------------------
        df["fecha"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce").dt.date
        df["hora_inicio"] = df["hora inicio"].apply(parse_hora)
        df["hora_final"] = df["hora final"].apply(parse_hora)
        df["tiempo_tarea_td"] = df["tiempo de tarea"].apply(parse_tiempo_tarea)
        # ✅ NO eliminar filas sin hora — asignar SIN HORA
        df["hora_inicio"] = df["hora_inicio"].apply(lambda x: x if pd.notna(x) else "SIN HORA")
        # -----------------------------------------------------
        # Mapeo de supervisores (normalizado)
        # -----------------------------------------------------
        supervisores_dict = {
            "ARIZA MARIN SERGIO": "ANDRES ARROYAVE",
            "ANDRES ARROYAVE": "ANDRES ARROYAVE",
            "BEDOYA DIEGO ALEJANDRO": "DANNY DE LA CRUZ",
            "DANNY DE LA CRUZ": "DANNY DE LA CRUZ",
            "CARVAJAL RESTREPO JUAN DAVID": "JANIER MARIN",
            "JANIER MARIN": "JANIER MARIN",
            "CHAVARRIAGA JUAN MANUEL": "CRISTIAN CHICA",
            "CRISTIAN CHICA": "CRISTIAN CHICA",
            "ECHEVERRY CARDONA JHON STIVEN": "JANIER MARIN",
            "GALLEGO CADAVID NORBEY": "DANNY DE LA CRUZ",
            "GIRALDO GARCIA SIGIFREDO": "ANDRES ARROYAVE",
            "LOPEZ PINEDA CESAR AUGUSTO": "JANIER MARIN",
            "NOREÑA GIRALDO GEOVANNY": "ANDRES ARROYAVE",
            "OSPINA CASTELLANOS ANDERSON": "CRISTIAN CHICA",
            "OSPINA RODRIGUEZ DANIEL ALBERTO": "ANDRES ARROYAVE",
            "RUIZ DILON MARLON ANDREY": "ANDRES ARROYAVE",
            "LARGO OSORIO JOSE OMAR": "ANDRES ARROYAVE",
            "PULGARIN QUINTERO JULIAN ANDRES": "DANNY DE LA CRUZ",
            "TAYACK TRUJILLO DEIVER EVELIO": "ANDRES ARROYAVE",
            "RUIZ ARENAS JUAN CAMILO": "CRISTIAN CHICA",
            "PATIÑO CIFUENTES RICARDO": "JANIER MARIN",
            "VARGAS FRANCO JHON EDISON": "CRISTIAN CHICA",
            "CARDONA CANO NELSON": "CRISTIAN CHICA",
            "CARDONA OROZCO JULIAN ANDRES": "ANDRES ARROYAVE",
            "GRISALES CUERVO JUAN DAVID": "JANIER MARIN",
            "LEON MARIN LEONARDO FABIO": "JANIER MARIN",
            "VELASQUEZ TAPASCO JHON DIEGO": "ANDRES ARROYAVE",
            "CARDONA CASTANO DIDIER ORLANDO": "CRISTIAN CHICA",
            "TORRES HERNANDEZ JOHN JAMES": "ANDRES ARROYAVE",
            "COBO HOYOS JUAN MANUEL": "CRISTIAN CHICA",
            "OSPINA NARANJO BERNARDO": "CRISTIAN CHICA",
            "COGOLLO FIGUEROA RANDY": "DANNY DE LA CRUZ",
            "ARIAS TORO YEISON": "DANNY DE LA CRUZ",
            "MIRANDA FRANCO EFRAIN": "DANNY DE LA CRUZ",
            "ARDILA MORA GUSTAVO ADOLFO": "DANNY DE LA CRUZ",
            "LOPEZ VELEZ ESTEBAN": "JANIER MARIN",
            "GALEANO GRISALEZ RICARDO": "DANNY DE LA CRUZ",
            "CAICEDO ESCOBAR JUNIOR SANTIAGO": "JANIER MARIN",
            "OTERO CAICEDO ANYEMBER": "DANNY DE LA CRUZ",
            "BUITRAGO RAMIREZ LEONARD": "CRISTIAN CHICA",
            "BORJAS WILLY ALEXANDER": "ANDRES ARROYAVE",
            "MARIN LEON JAISSON JOAQUIN": "CRISTIAN CHICA",
            "AMAYA HINCAPIE JUAN CARLOS": "CRISTIAN CHICA",
            "BEDOYA SANCHEZ CRISTIAN DAVID": "ANDRES ARROYAVE",
            "RAMIREZ WILSON ENRIQUE": "CRISTIAN CHICA",
            "CANO MORALES JIMY ALFREDO": "ANDRES ARROYAVE",
            "CASTRO CASTAÑO JUAN DAVID": "CRISTIAN CHICA",
            "LOAIZA GAMBA JHON ALEXANDER": "ANDRES ARROYAVE",
            "VILLA LOAIZA JHEISON ESTIBEN": "CRISTIAN CHICA",
            "CÁRDENAS GALIANO HAROLD MAURICIO": "JANIER MARIN",
            "VARGAS CORREA VICTOR ALFONSO": "DANNY DE LA CRUZ",
            "VILLA MERA CHRISTIAN DAVID": "JANIER MARIN",
            "AVENDAÑO GARCIA JUAN NEPOMUCENO": "ANDRES ARROYAVE",
            "PELAEZ TATIS GABRIEL ESTEBAN": "CRISTIAN CHICA",
        }
        supervisores_dict = {k.upper(): v for k,v in supervisores_dict.items()}
        df["supervisor"] = df["inspector"].map(supervisores_dict).fillna("SIN SUPERVISOR")
        # -----------------------------------------------------
        # FILTRO FECHA
        # -----------------------------------------------------
        fechas_validas = sorted(df["fecha"].dropna().unique())
        fecha_sel = st.selectbox("Selecciona fecha:", fechas_validas)
        df2 = df[df["fecha"] == fecha_sel]
        # -----------------------------------------------------
        # FILTRO SUPERVISOR
        # -----------------------------------------------------
        supervisor_sel = st.selectbox("Selecciona supervisor:", sorted(df2["supervisor"].unique()))
        df2 = df2[df2["supervisor"] == supervisor_sel]
        # -----------------------------------------------------
        # ✅ LISTA COMPLETA DE INSPECTORES DEL EXCEL
        # -----------------------------------------------------
        inspectores_todos = sorted(df["inspector"].unique())
        inspectores_supervisor = [
            i for i in inspectores_todos
            if supervisores_dict.get(i, "") == supervisor_sel
        ]
        insp_sel = st.multiselect(
            "Selecciona inspectores:",
            inspectores_supervisor,
            default=inspectores_supervisor
        )
        inspectores_filtrados = insp_sel
        # -----------------------------------------------------
        # PRIMERA Y ÚLTIMA HORA
        # -----------------------------------------------------
        primeras = (
            df2.sort_values("hora_inicio")
               .groupby(["inspector","fecha"], as_index=False)
               .first()[["inspector","supervisor","fecha","hora_inicio","localidad"]]
        )
        ultimas = (
            df2.sort_values("hora_final")
               .groupby(["inspector","fecha"], as_index=False)
               .last()[["inspector","fecha","hora_final"]]
        )
        df_agrupado = primeras.merge(ultimas, on=["inspector","fecha"], how="left")
        # -----------------------------------------------------
        # PUNTUALIDAD
        # -----------------------------------------------------
        hora_oficial = datetime.time(7,30)
        def mins_tarde(h):
            h1 = datetime.datetime.combine(datetime.date.today(), h)
            h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
            return int((h1 - h2).total_seconds() / 60)
        def safe_mins_tarde(h):
            if h == "SIN HORA" or h is None:
                return None
            return mins_tarde(h)
        df_agrupado["minutos_tarde"] = df_agrupado["hora_inicio"].apply(safe_mins_tarde)
        def estado(m):
            if m is None:
                return "SIN INICIO"
            if m <= 0:
                return "Puntual"
            if m <= 15:
                return "Tarde"
            return "Muy tarde"
        df_agrupado["estado"] = df_agrupado["minutos_tarde"].apply(estado)
        # -----------------------------------------------------
        # PRODUCCIÓN
        # -----------------------------------------------------
        valores_efectivos = [
            "INSPECCIONADA",
            "INSPECCIONADA CON DEFECTO NO CRITICO",
            "INSPECCIONADA CON DEFECTO CRITICO",
            "CERTIFICADA",
            "CERTIFICADA CON NOVEDAD"
        ]
        df2["efectiva"] = df2["cierre"].isin(valores_efectivos)
        df_agrupado["efectiva"] = df2["efectiva"]
        total_ordenes = df2.shape[0]
        total_efectivas = df2[df2["efectiva"]].shape[0]
        porcentaje_efectividad = round((total_efectivas / total_ordenes) * 100, 1) if total_ordenes else 0
        # -----------------------------------------------------
        # TIEMPO PROM. EFECTIVAS
        # -----------------------------------------------------
        df_eff = df2[(df2["efectiva"] == True) & (df2["tiempo_tarea_td"].notna())]
        if df_eff.shape[0] > 0:
            tiempo_promedio_tarea_str = td_to_str(df_eff["tiempo_tarea_td"].mean())
        else:
            tiempo_promedio_tarea_str = "—"
        # -----------------------------------------------------
        # KPIs
        # -----------------------------------------------------
        st.markdown("## ⭐ KPIs del día")
        df_agrupado["ini_dec"] = df_agrupado["hora_inicio"].apply(
            lambda x: hora_to_decimal(x) if x != "SIN HORA" else None
        )
        df_agrupado["fin_dec"] = df_agrupado["hora_final"].apply(
            lambda x: hora_to_decimal(x) if pd.notna(x) else None
        )
        df_agrupado["dur_dec"] = df_agrupado["fin_dec"] - df_agrupado["ini_dec"]
        c1, c2, c3 = st.columns(3)
        c1.metric("⏰ Promedio inicio", hora_to_string(decimal_to_hora(df_agrupado["ini_dec"].mean())))
        c2.metric("🕒 Promedio fin", hora_to_string(decimal_to_hora(df_agrupado["fin_dec"].mean())))
        dur_prom = df_agrupado["dur_dec"].mean()
        c3.metric("💼 Duración prom.", f"{round(dur_prom,2)}h" if pd.notna(dur_prom) else "—")
        c4, c5, c6, c7 = st.columns(4)
        c4.metric("📋 Tareas", total_ordenes)
        c5.metric("✅ Efectivas", total_efectivas)
        c6.metric("📈 % Efectividad", f"{porcentaje_efectividad}%")
        c7.metric("🕓 Prom. tarea efectiva", tiempo_promedio_tarea_str)
        # -----------------------------------------------------
        # RESUMEN POR INSPECTOR
        # -----------------------------------------------------
        resumen = (
            df2.groupby("inspector")
                .apply(lambda x: pd.Series({
                    "total_ordenes": x.shape[0],
                    "ordenes_efectivas": x["efectiva"].sum(),
                    "porcentaje_efectividad":
                        round((x["efectiva"].sum() / x.shape[0]) * 100, 1) if x.shape[0] else 0,
                    "promedio_tiempo_tarea":
                        td_to_str(x.loc[x["efectiva"] == True, "tiempo_tarea_td"].mean())
                }))
                .reset_index()
        )
        # -----------------------------------------------------
        # ARMAR TABLA COMPLETA
        # -----------------------------------------------------
        inspectores_completos = pd.DataFrame({"inspector": inspectores_supervisor})
        df_tabla = inspectores_completos.merge(df_agrupado, on="inspector", how="left")
        df_tabla = df_tabla.merge(resumen, on="inspector", how="left")
        df_tabla = df_tabla.fillna({
            "hora_inicio": "—",
            "hora_final": "—",
            "localidad": "—",
            "estado": "SIN ACTIVIDAD",
            "total_ordenes": 0,
            "ordenes_efectivas": 0,
            "porcentaje_efectividad": 0,
            "promedio_tiempo_tarea": "—"
        })
        df_tabla = df_tabla[df_tabla["inspector"].isin(inspectores_filtrados)]
        st.write("### Tabla de inspecciones del día")
        st.dataframe(
            df_tabla[[
                "inspector","supervisor","fecha",
                "hora_inicio","hora_final","localidad",
                "estado","total_ordenes","ordenes_efectivas",
                "porcentaje_efectividad","promedio_tiempo_tarea"
            ]],
            use_container_width=True
        )
        # -----------------------------------------------------
        # PRODUCCIÓN
        # -----------------------------------------------------
        df_prod = (
            df2.groupby("inspector")
               .apply(lambda x: pd.Series({
                   "efectivas": x["efectiva"].sum(),
                   "no_efectivas": (~x["efectiva"]).sum()
               }))
               .reset_index()
        )
        st.write("## Producción por inspector")
        fig_prod = px.bar(
            df_prod,
            y="inspector",
            x=["efectivas","no_efectivas"],
            orientation="h",
            barmode="group",
            color_discrete_map={"efectivas":"green","no_efectivas":"red"}
        )
        fig_prod.update_traces(texttemplate='%{x}', textposition='outside')
        st.plotly_chart(fig_prod, use_container_width=True)
        # -----------------------------------------------------
        # TOP 5
        # -----------------------------------------------------
        df_rank = (
            df2.groupby("inspector")
               .apply(lambda x: pd.Series({
                   "efectivas": x["efectiva"].sum(),
                   "total": x.shape[0],
                   "efectividad": round((x["efectiva"].sum()/x.shape[0])*100,2) if x.shape[0] else 0
               }))
               .reset_index()
        )
        df_rank = df_rank.sort_values("efectividad", ascending=False).head(5)
        st.write("## 🏆 TOP 5 Efectividad")
        fig_rank = px.bar(
            df_rank,
            x="efectividad",
            y="inspector",
            orientation="h",
            text="efectividad",
            color="efectividad",
            color_continuous_scale="Blues"
        )
        fig_rank.update_traces(texttemplate='%{x}%', textposition='outside')
        st.plotly_chart(fig_rank,use_container_width=True)
        # -----------------------------------------------------
        # PRODUCTIVIDAD POR HORA
        # -----------------------------------------------------
        st.write("## Productividad por hora (efectivas)")
        df_horas = df2[df2["efectiva"] == True]
        if df_horas.shape[0] == 0:
            st.info("⚠️ No hay tareas efectivas para esta fecha.")
        else:
            df_horas["hora_bloque"] = df_horas["hora_inicio"].apply(
                lambda x: x if isinstance(x, datetime.time) else datetime.time(0, 0)
            )
            df_horas["hora_str"] = df_horas["hora_bloque"].astype(str)
            horas_prod = (
                df_horas.groupby("hora_str")
                        .size()
                        .reset_index(name="cantidad")
            )
            fig_horas = px.bar(
                horas_prod,
                x="hora_str",
                y="cantidad",
                text="cantidad",
                color="cantidad",
                color_continuous_scale="blues"
            )
            fig_horas.update_traces(textposition="outside")
            st.plotly_chart(fig_horas, use_container_width=True)
# ---------------------------------------------------

# ---------------------------------------------------
# ✅ TAB 3 — SEGUIMIENTO MENSUAL (MULTI‑DÍA)
# ---------------------------------------------------
with tab3:
    st.subheader("📅 Seguimiento mensual")
    st.info(
        "Este módulo permite analizar el desempeño de los inspectores "
        "en un rango de fechas, consolidando y promediando la información diaria."
    )
    # ---------------------------------------------------
    # 1️⃣ CARGA DEL ARCHIVO
    # ---------------------------------------------------
    archivo = st.file_uploader(
        "Cargar archivo de bitácora (Excel)",
        type=["xls", "xlsx"],
        key="archivo_tab3"
    )
    if archivo:
        import datetime
        # ---------------------------------------------------
        # 2️⃣ CARGA Y NORMALIZACIÓN
        # ---------------------------------------------------
        df = pd.read_excel(archivo)
        df.columns = df.columns.str.strip().str.lower()
        columnas_req = [
            "fecha de ejecucion", "hora inicio", "hora final",
            "inspector", "localidad", "cierre", "tiempo de tarea"
        ]
        for col in columnas_req:
            if col not in df.columns:
                st.error(f"❌ Falta la columna obligatoria: {col}")
                st.stop()
        df["inspector"] = (
            df["inspector"].astype(str)
            .str.upper().str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
        df["fecha"] = pd.to_datetime(
            df["fecha de ejecucion"], errors="coerce"
        ).dt.date
        def parse_hora(x):
            try:
                return pd.to_datetime(x).time()
            except:
                return None
        df["hora_inicio"] = df["hora inicio"].apply(parse_hora)
        df["hora_final"] = df["hora final"].apply(parse_hora)
        df["tiempo_td"] = pd.to_timedelta(
            df["tiempo de tarea"], errors="coerce"
        )
        # ---------------------------------------------------
        # 3️⃣ RANGO DE FECHAS
        # ---------------------------------------------------
        fechas = sorted(df["fecha"].dropna().unique())
        fecha_inicio, fecha_fin = st.date_input(
            "Selecciona rango de fechas",
            value=(fechas[0], fechas[-1])
        )
        df = df[(df["fecha"] >= fecha_inicio) & (df["fecha"] <= fecha_fin)]
        if df.empty:
            st.warning("⚠️ No hay datos en el rango seleccionado.")
            st.stop()
        # ---------------------------------------------------
        # 4️⃣ DEFINIR EFECTIVIDAD (REGLA MIXTA)
        # ---------------------------------------------------
        valores_efectivos = [
            "INSPECCIONADA",
            "INSPECCIONADA CON DEFECTO NO CRITICO",
            "INSPECCIONADA CON DEFECTO CRITICO",
            "CERTIFICADA",
            "CERTIFICADA CON NOVEDAD"
        ]
        df["efectiva"] = df.apply(
            lambda r: (
                r["cierre"] == "AGENDAMIENTO 12161"
                if r["inspector"] == "PELAEZ TATIS GABRIEL ESTEBAN"
                else r["cierre"] in valores_efectivos
            ),
            axis=1
        )
        # ---------------------------------------------------
        # 5️⃣ UTILIDADES
        # ---------------------------------------------------
        hora_oficial = datetime.time(7, 30)
        def minutos_tarde(h):
            if h is None:
                return None
            h1 = datetime.datetime.combine(datetime.date.today(), h)
            h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
            return (h1 - h2).total_seconds() / 60
        df["minutos_tarde"] = df["hora_inicio"].apply(minutos_tarde)
        def hora_promedio(serie):
            serie = serie.dropna()
            if serie.empty:
                return None
            segs = [h.hour*3600 + h.minute*60 for h in serie]
            prom = int(sum(segs)/len(segs))
            return datetime.time(prom//3600, (prom%3600)//60)
        def formatear_td(td):
            if pd.isna(td):
                return "—"
            mins = int(td.total_seconds() // 60)
            h = mins // 60
            m = mins % 60
            return f"{h:02d}:{m:02d}"
        # ---------------------------------------------------
        # 6️⃣ FILTRO POR INSPECTOR ✅
        # ---------------------------------------------------
        inspector_sel = st.selectbox(
            "Filtrar por inspector",
            ["TODOS"] + sorted(df["inspector"].unique())
        )
        # ---------------------------------------------------
        # ✅ CASO TODOS: RESUMEN CONSOLIDADO
        # ---------------------------------------------------
        if inspector_sel == "TODOS":
            st.markdown("### 📊 Resumen consolidado por inspector")
            resumen = []
            for insp in df["inspector"].unique():
                dfi = df[df["inspector"] == insp]
                total = len(dfi)
                efectivas = dfi["efectiva"].sum()
                efectividad = round((efectivas / total) * 100, 1) if total else 0
                por_dia = (
                    dfi.groupby("fecha")
                    .agg(
                        inicio=("hora_inicio", "min"),
                        fin=("hora_final", "max")
                    )
                    .reset_index()
                )
                prom_inicio = hora_promedio(por_dia["inicio"])
                prom_fin = hora_promedio(por_dia["fin"])
                dfi_eff = dfi[
                    (dfi["efectiva"] == True) &
                    (dfi["tiempo_td"].notna())
                ]
                prom_tarea = (
                    formatear_td(dfi_eff["tiempo_td"].mean())
                    if not dfi_eff.empty else "—"
                )
                resumen.append({
                    "Inspector": insp,
                    "Órdenes": total,
                    "Órdenes efectivas": int(efectivas),
                    "% Efectividad": efectividad,
                    "Prom. hora inicio": prom_inicio.strftime("%H:%M") if prom_inicio else "—",
                    "Prom. hora fin": prom_fin.strftime("%H:%M") if prom_fin else "—",
                    "Prom. por inspección": prom_tarea
                })
            df_resumen = pd.DataFrame(resumen).sort_values("% Efectividad", ascending=False)
            st.dataframe(df_resumen, use_container_width=True)
        # ---------------------------------------------------
        # ✅ CASO INSPECTOR ÚNICO: DETALLE DIARIO
        # ---------------------------------------------------
        else:
            st.markdown(f"### 👤 Detalle diario — {inspector_sel}")
            dfi = df[df["inspector"] == inspector_sel]
            detalle = (
                dfi.groupby("fecha")
                .agg(
                    inicio=("hora_inicio", "min"),
                    fin=("hora_final", "max"),
                    ordenes=("efectiva", "count"),
                    efectivas=("efectiva", "sum"),
                    minutos_tarde=("minutos_tarde", "mean"),
                    tiempo_eff=("tiempo_td",
                        lambda x: x[dfi.loc[x.index, "efectiva"]].mean())
                )
                .reset_index()
            )
            detalle["Inicio"] = detalle["inicio"].apply(
                lambda x: x.strftime("%H:%M") if pd.notna(x) else "—"
            )
            detalle["Fin"] = detalle["fin"].apply(
                lambda x: x.strftime("%H:%M") if pd.notna(x) else "—"
            )
            detalle["Min. tarde"] = detalle["minutos_tarde"].round(1)
            detalle["Tiempo efectivo"] = detalle["tiempo_eff"].apply(formatear_td)
            detalle_final = detalle[[
                "fecha", "Inicio", "Fin",
                "ordenes", "efectivas",
                "Min. tarde", "Tiempo efectivo"
            ]].rename(columns={
                "fecha": "Fecha",
                "ordenes": "Órdenes",
                "efectivas": "Órdenes efectivas"
            })
            st.dataframe(detalle_final, use_container_width=True)
