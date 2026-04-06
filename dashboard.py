import streamlit as st
import pandas as pd
import os
import plotly.express as px



# ---------------------------------------------------
# ✅ LISTA MAESTRA DE INSPECTORES
# ---------------------------------------------------
inspectores_lista = sorted([
    "ARIZA MARIN SERGIO",
    "ANDRES ARROYAVE",
    "BEDOYA DIEGO ALEJANDRO",
    "CHAVARRIAGA JUAN MANUEL",
    "OSPINA RODRIGUEZ DANIEL ALBERTO",
    "OSPINA CASTELLANOS ANDERSON",
    "RUIZ DILON MARLON ANDREY",
    "RUIZ ARENAS JUAN CAMILO",
    "PATIÑO CIFUENTES RICARDO",
    "VARGAS FRANCO JHON EDISON",
    "CARDONA CANO NELSON",
    "GRISALES CUERVO JUAN DAVID",
    "LEON MARIN LEONARDO FABIO",
    "VELASQUEZ TAPASCO JHON DIEGO",
    "COBO HOYOS JUAN MANUEL",
    "NOREÑA GIRALDO GEOVANNY",
    "GALLEGO CADAVID NORBEY",
    "COGOLLO FIGUEROA RANDY",
    "ARIAS TORO YEISON",
    "MIRANDA FRANCO EFRAIN",
    "ARDILA MORA GUSTAVO ADOLFO",
    "BUITRAGO RAMIREZ LEONARD",
    "BORJAS WILLY ALEXANDER",
    "MARIN LEON JAISSON JOAQUIN",
    "AMAYA HINCAPIE JUAN CARLOS",
    "BEDOYA SANCHEZ CRISTIAN DAVID",
    "RAMIREZ WILSON ENRIQUE",
    "CANO MORALES JIMY ALFREDO",
    "CASTRO CASTAÑO JUAN DAVID",
    "LOAIZA GAMBA JHON ALEXANDER",
    "VILLA LOAIZA JHEISON ESTIBEN",
    "CÁRDENAS GALIANO HAROLD MAURICIO",
    "VARGAS CORREA VICTOR ALFONSO",
    "VILLA MERA CHRISTIAN DAVID",
    "AVENDAÑO GARCIA JUAN NEPOMUCENO",
    "PELAEZ TATIS GABRIEL ESTEBAN",
])
# ---------------------------------------------------
# ✅ CONFIGURACIÓN GENERAL DEL DASHBOARD
# ---------------------------------------------------
st.set_page_config(
    page_title="Dashboard Inspectores",
    layout="wide"
)

st.title("📊 Dashboard Inspectores")

# ---------------------------------------------------
# ✅ CREAR PESTAÑAS
# ---------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📦 Inventario Papelería",
    "🕒 Seguimiento Diario",
    "📈 Gráficas Generales"
])



# ---------------------------------------------------
# ---------------------------------------------------
# ✅ PESTAÑA 1: INVENTARIO DE PAPELERÍA
# ---------------------------------------------------
with tab1:
    st.subheader("📦 Control de entrega de papelería e inventario")

    ARCHIVO_INVENTARIO = "inventario.xlsx"

    # ---------------------------------------------------
    # COLUMNAS VÁLIDAS DEL INVENTARIO
    # (coinciden con tu Excel real)
    # ---------------------------------------------------
    columnas_inventario = [
        "fecha",
        "inspector",
        "sede",
        "responsable",
        "ítems",
    ]

    # ---------------------------------------------------
    # CREAR O LEER INVENTARIO (AISLADO)
    # ---------------------------------------------------
    if not os.path.exists(ARCHIVO_INVENTARIO):
        df_inv = pd.DataFrame(columns=columnas_inventario)
        df_inv.to_excel(
            ARCHIVO_INVENTARIO,
            index=False,
            engine="openpyxl"
        )
    else:
        df_inv = pd.read_excel(
            ARCHIVO_INVENTARIO,
            engine="openpyxl"
        )

    # Normalizar columnas (blindaje)
    df_inv.columns = df_inv.columns.str.strip().str.lower()

    # ---------------------------------------------------
    # LISTA DE INSPECTORES (DESDE INVENTARIO)
    # ---------------------------------------------------
    inspectores_inv = sorted(
        df_inv["inspector"].dropna().unique().tolist()
    ) if not df_inv.empty else inspectores_lista

    # ===================================================
    # ✅ FORMULARIO DE ENTREGA
    # ===================================================
    with st.form("form_entrega", clear_on_submit=True):
        st.markdown("### Registrar entrega")

        col1, col2, col3 = st.columns(3)

        with col1:
            fecha = st.date_input("Fecha")

        with col2:
            inspector = st.selectbox(
                "Inspector",
                inspectores_inv
            )

        with col3:
            sede = st.selectbox(
                "Sede",
                ["CALDAS", "RISARALDA"]
            )

        col4, col5 = st.columns([1, 2])

        with col4:
            responsable = st.text_input("Responsable")

        with col5:
            st.markdown(" ")  # separador visual

        # ---------------- ÍTEMS ----------------
        st.markdown("### Ítems entregados")

        items_def = [
            "Stickers",
            "Cepo",
            "Guantes",
            "Piernera",
            "Monogafas",
            "Llaves de cepo",
            "Formatos",
            "Sellos",
            "Papelería general",
        ]

        items_seleccionados = []

        cols_items = st.columns(3)
        for i, item in enumerate(items_def):
            with cols_items[i % 3]:
                marcar = st.checkbox(item, key=f"inv_item_{i}")
                cantidad = st.number_input(
                    "Cantidad",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                    key=f"inv_qty_{i}",
                )
                if marcar and cantidad > 0:
                    items_seleccionados.append(f"{item} x{cantidad}")

        submitted = st.form_submit_button("✅ Guardar entrega")

    # ===================================================
    # ✅ GUARDAR ENTREGA (SOLO INVENTARIO)
    # ===================================================
    if submitted:
        if not items_seleccionados:
            st.warning("⚠️ Debes seleccionar al menos un ítem con cantidad.")
        else:
            nueva_fila = pd.DataFrame({
                "fecha": [fecha],
                "inspector": [inspector],
                "sede": [sede],
                "responsable": [responsable],
                "ítems": [", ".join(items_seleccionados)],
            })

            df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)

            df_inv.to_excel(
                ARCHIVO_INVENTARIO,
                index=False,
                engine="openpyxl"
            )

            st.success("✅ Entrega registrada correctamente")

    # ===================================================
    # ✅ HISTORIAL DE ENTREGAS (INVENTARIO REAL)
    # ===================================================
    st.markdown("### 📋 Historial de entregas")

    filtro_inspector = st.selectbox(
        "Filtrar por inspector",
        ["TODOS"] + inspectores_inv,
        key="filtro_hist_inv"
    )

    df_hist = df_inv.copy()

    if filtro_inspector != "TODOS":
        df_hist = df_hist[
            df_hist["inspector"] == filtro_inspector
        ]

    # RENDER PASIVO (SIN ESTADO, SIN MEZCLAS)
    st.dataframe(
        df_hist,
        use_container_width=True
    )

# ---------------------------------------------------
# ---------------------------------------------------

# ✅ PESTAÑA 2: SEGUIMIENTO DIARIO (BITÁCORA COMPARTIDA)
# ---------------------------------------------------
with tab2:
    st.subheader("Control de horario de inspectores")

    ARCHIVO_BITACORA = "BITACORA.xlsx"

    import numpy as np
    import datetime

    # ---------------------------------------------------
    # CARGA DE BITÁCORA (GUARDADO Y COMPARTIDO)
    # ---------------------------------------------------
    st.write("### Cargar archivo de bitácora (formato XLSX recomendado)")
    archivo = st.file_uploader(
        "Sube SOLO el archivo de bitácora diaria",
        type=["xls", "xlsx"]
    )

    if archivo is not None:
        with open(ARCHIVO_BITACORA, "wb") as f:
            f.write(archivo.read())
        st.success("✅ Bitácora actualizada y compartida")

    if not os.path.exists(ARCHIVO_BITACORA):
        st.info("ℹ️ Carga un archivo de bitácora para iniciar el análisis.")
        st.stop()

    # ---------------------------------------------------
    # LECTURA DEL ARCHIVO DE BITÁCORA
    # ✅ NOMBRE DE DF AISLADO (NO USAR df)
    # ---------------------------------------------------
    df_bitacora = pd.read_excel(ARCHIVO_BITACORA)

    st.write("📄 Vista previa de la bitácora cargada:")
    st.dataframe(df_bitacora.head(), use_container_width=True)

    # ---------------------------------------------------
    # FUNCIONES UTILITARIAS (SOLO BITÁCORA)
    # ---------------------------------------------------
    def hora_to_decimal(hora):
        if hora is None or pd.isna(hora):
            return None
        return hora.hour + hora.minute / 60 + hora.second / 3600

    def decimal_to_hora(decimal):
        if decimal is None or pd.isna(decimal):
            return None
        h = int(decimal)
        m = int((decimal - h) * 60)
        s = int((((decimal - h) * 60) - m) * 60)
        return datetime.time(h, m, s)

    def hora_to_string(hora):
        if hora is None or pd.isna(hora):
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

    def td_to_str(td):
        if pd.isna(td):
            return "—"
        total_sec = int(td.total_seconds())
        h = total_sec // 3600
        m = (total_sec % 3600) // 60
        s = total_sec % 60
        return f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"


    # -----------------------------------------------------
    # NORMALIZAR COLUMNAS
    # -----------------------------------------------------
    df.columns = df.columns.str.strip().str.lower()

    columnas_necesarias = [
        "fecha de ejecucion","hora inicio","hora final",
        "inspector","localidad","cierre","tiempo de tarea"
    ]

    for col in columnas_necesarias:
        if col not in df.columns:
            st.error(f"❌ Falta la columna: {col}")
            st.stop()
    # -----------------------------------------------------
    # CONVERTIR COLUMNAS CLAVE
    # -----------------------------------------------------
    df["fecha"] = pd.to_datetime(
        df["fecha de ejecucion"], errors="coerce"
    ).dt.date

    df["hora_inicio"] = df["hora inicio"].apply(parse_hora)
    df["hora_final"] = df["hora final"].apply(parse_hora)
    df["inspector"] = df["inspector"].astype(str).str.strip()
    df["localidad"] = df["localidad"].astype(str)
    df = df.dropna(subset=["hora_inicio", "hora_final"])


        # -----------------------------------------------------
     # -----------------------------------------------------
    # 4. Mapeo de supervisores actualizado
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

    df["supervisor"] = df["inspector"].map(supervisores_dict).fillna("SIN SUPERVISOR")

        # -----------------------------------------------------
  # -----------------------------------------------------
    # 6. Primera y última hora del día
    # -----------------------------------------------------
    primeras = (
        df.sort_values("hora_inicio")
          .groupby(["inspector", "fecha"], as_index=False)
          .first()[["inspector", "supervisor", "fecha", "hora_inicio", "localidad"]]
    )

    ultimas = (
        df.sort_values("hora_final")
          .groupby(["inspector", "fecha"], as_index=False)
          .last()[["inspector", "fecha", "hora_final"]]
    )

    df_agrupado = primeras.merge(
        ultimas,
        on=["inspector", "fecha"],
        how="left"
    )

    # -----------------------------------------------------
    # 7. Puntualidad
    # -----------------------------------------------------
    hora_oficial = pd.to_datetime("07:30", format="%H:%M").time()

    def mins_tarde(h):
        h1 = pd.to_datetime(str(h))
        h2 = pd.to_datetime(str(hora_oficial))
        return int((h1 - h2).total_seconds() / 60)

    df_agrupado["minutos_tarde"] = df_agrupado["hora_inicio"].apply(mins_tarde)

    def estado(m):
        if m <= 0:
            return "Puntual"
        elif m <= 15:
            return "Tarde"
        else:
            return "Muy Tarde"

    df_agrupado["estado"] = df_agrupado["minutos_tarde"].apply(estado)

    # -----------------------------------------------------
    # 8. Producción
    # -----------------------------------------------------
    valores_efectivos = [
        "INSPECCIONADA",
        "INSPECCIONADA CON DEFECTO NO CRITICO",
        "INSPECCIONADA CON DEFECTO CRITICO",
        "CERTIFICADA",
        "CERTIFICADA CON NOVEDAD"
    ]

    df["efectiva"] = df["cierre"].isin(valores_efectivos)
    df_agrupado["efectiva"] = df["efectiva"]

    total_ordenes = df.shape[0]
    total_efectivas = df[df["efectiva"]].shape[0]
    porcentaje_efectividad = (
        round((total_efectivas / total_ordenes) * 100, 1)
        if total_ordenes > 0 else 0
    )

    # -----------------------------------------------------
    # 8-B. Tiempo promedio por tarea efectiva
    # -----------------------------------------------------
    def parse_tiempo_tarea(valor):
        try:
            return pd.to_timedelta(str(valor))
        except:
            return pd.NaT

    df["tiempo_tarea_td"] = df["tiempo de tarea"].apply(parse_tiempo_tarea)

    df_efectivas = df[
        (df["efectiva"] == True) &
        (df["tiempo_tarea_td"].notna())
    ]

    if df_efectivas.shape[0] > 0:
        promedio_td = df_efectivas["tiempo_tarea_td"].mean()

        prom_seg = int(promedio_td.total_seconds())
        prom_h = prom_seg // 3600
        prom_m = (prom_seg % 3600) // 60
        prom_s = prom_seg % 60

        tiempo_promedio_tarea_str = (
            f"{prom_h}h {prom_m}m {prom_s}s"
            if prom_h > 0 else f"{prom_m}m {prom_s}s"
        )
    else:
        tiempo_promedio_tarea_str = "No disponible"
        # -----------------------------------------------------
     # -----------------------------------------------------
    # 9. KPIs Premium
    # -----------------------------------------------------
    st.markdown("## ⭐ KPIs del Día")

    df_agrupado["ini_dec"] = df_agrupado["hora_inicio"].apply(hora_to_decimal)
    df_agrupado["fin_dec"] = df_agrupado["hora_final"].apply(hora_to_decimal)
    df_agrupado["dur_dec"] = df_agrupado["fin_dec"] - df_agrupado["ini_dec"]

    hora_prom_ini = hora_to_string(decimal_to_hora(df_agrupado["ini_dec"].mean()))
    hora_prom_fin = hora_to_string(decimal_to_hora(df_agrupado["fin_dec"].mean()))

    dur_prom = df_agrupado["dur_dec"].mean()
    dur_h = int(dur_prom)
    dur_m = int((dur_prom - dur_h) * 60)
    dur_prom_str = f"{dur_h}h {dur_m}m"

    c1, c2, c3 = st.columns(3)
    c1.metric("⏰ Promedio inicio", hora_prom_ini)
    c2.metric("🕒 Promedio fin", hora_prom_fin)
    c3.metric("💼 Duración promedio", dur_prom_str)

    c4, c5, c6, c7 = st.columns(4)
    c4.metric("📋 Total tareas", total_ordenes)
    c5.metric("✅ Tareas efectivas", total_efectivas)
    c6.metric("📈 % Efectividad", f"{porcentaje_efectividad}%")
    c7.metric("🕓 Tiempo prom. tarea efectiva", tiempo_promedio_tarea_str)

    # -----------------------------------------------------
    # 10. Resumen por inspector
    # -----------------------------------------------------
    resumen = (
        df.groupby("inspector")
          .apply(lambda x: pd.Series({
              "total_ordenes": x.shape[0],
              "ordenes_efectivas": x[x["efectiva"]].shape[0],
              "porcentaje_efectividad": round(
                  (x[x["efectiva"]].shape[0] / x.shape[0]) * 100, 1
              ) if x.shape[0] > 0 else 0,
              "promedio_tiempo_tarea": x.loc[x["efectiva"], "tiempo_tarea_td"].mean()
          }))
          .reset_index()
    )

    resumen["promedio_tiempo_tarea"] = resumen["promedio_tiempo_tarea"].apply(td_to_str)

    df_tabla = df_agrupado.merge(resumen, on="inspector", how="left")

    st.write("### Tabla de inspecciones del día")
    st.dataframe(
        df_tabla[[
            "inspector","supervisor","fecha",
            "hora_inicio","hora_final","localidad",
            "estado","efectiva",
            "total_ordenes","ordenes_efectivas",
            "porcentaje_efectividad","promedio_tiempo_tarea"
        ]],
        use_container_width=True
    )

    # -----------------------------------------------------
    # 11. Producción
    # -----------------------------------------------------
    df_prod = (
        df.groupby("inspector")
          .apply(lambda x: pd.Series({
              "efectivas": x["efectiva"].sum(),
              "no_efectivas": (~x["efectiva"]).sum()
          }))
          .reset_index()
    )

    fig_prod = px.bar(
        df_prod,
        y="inspector",
        x=["efectivas", "no_efectivas"],
        orientation="h",
        barmode="group",
        color_discrete_map={"efectivas": "green", "no_efectivas": "red"}
    )

    fig_prod.update_traces(texttemplate="%{x}", textposition="outside")
    st.plotly_chart(fig_prod, use_container_width=True)

    # -----------------------------------------------------
    # 12. TOP 5
    # -----------------------------------------------------
    st.markdown("## 🏆 TOP 5 Inspectores con mejor efectividad")

    df_rank = (
        df.groupby("inspector")
          .apply(lambda x: pd.Series({
              "efectivas": x["efectiva"].sum(),
              "total": x.shape[0],
              "efectividad": round((x["efectiva"].sum() / x.shape[0]) * 100, 1)
          }))
          .reset_index()
          .sort_values("efectividad", ascending=False)
          .head(5)
    )

    fig_rank = px.bar(
        df_rank,
        y="inspector",
        x="efectividad",
        orientation="h",
        text="efectividad",
        color="efectividad"
    )

    fig_rank.update_traces(texttemplate="%{x}%", textposition="outside")
    st.plotly_chart(fig_rank, use_container_width=True)

# ---------------------------------------------------
# ✅ PESTAÑA 3: GRÁFICAS GENERALES
# ---------------------------------------------------
with tab3:
    st.subheader("Gráficas de desempeño general")
    st.info("Aquí veremos indicadores, tendencias y análisis más avanzados usando Plotly.")
