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



# ===================================================
# ===================================================
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA (FINAL ESTABLE)
# ===================================================
with tab1:
    st.subheader("📦 Control de entrega de papelería e inventario")

    archivo_inventario = "inventario.xlsx"

    # -------------------------------------------------
    # CREAR / LEER INVENTARIO
    # -------------------------------------------------
    if not os.path.exists(archivo_inventario):
        df_inv = pd.DataFrame(columns=[
            "Fecha", "Sede", "Inspector",
            "Responsable", "Observación", "Ítems"
        ])
        df_inv.to_excel(archivo_inventario, index=False, engine="openpyxl")
    else:
        df_inv = pd.read_excel(archivo_inventario, engine="openpyxl")

    df_inv.columns = df_inv.columns.str.strip()

    # =================================================
    # ✅ FORMULARIO DE ENTREGA
    # =================================================
    with st.form("form_entrega", clear_on_submit=True):
        st.markdown("### Registrar entrega")

        col1, col2, col3 = st.columns(3)
        with col1:
            sede = st.selectbox("Sede", ["CALDAS", "RISARALDA"], key="inv_sede")
        with col2:
            inspector = st.selectbox("Inspector", inspectores_lista, key="inv_inspector")
        with col3:
            fecha = st.date_input("Fecha", key="inv_fecha")

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
                key="inv_responsable"
            )
        with col5:
            observacion = st.text_input("Observación (opcional)", key="inv_obs")

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
                marcar = cols[c_idx].checkbox(item, key=f"item_chk_{f_idx}_{c_idx}")
                cantidad = cols[c_idx].number_input(
                    "Cantidad",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                    key=f"item_qty_{f_idx}_{c_idx}"
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
            nueva_fila = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Sede": sede,
                "Inspector": inspector,
                "Responsable": responsable,
                "Observación": observacion,
                "Ítems": ", ".join(items_seleccionados)
            }])
            df_inv = pd.concat([df_inv, nueva_fila], ignore_index=True)
            df_inv.to_excel(archivo_inventario, index=False, engine="openpyxl")
            st.success("✅ Entrega registrada correctamente")

    # =================================================
    # ✅ HISTORIAL DE ENTREGAS
    # =================================================
    st.markdown("### 📋 Historial de entregas")

    filtro_inspector = st.selectbox(
        "Filtrar por inspector",
        ["TODOS"] + inspectores_lista,
        key="inv_filtro_inspector"
    )

    df_hist = df_inv.copy()
    if filtro_inspector != "TODOS":
        df_hist = df_hist[df_hist["Inspector"] == filtro_inspector]

    st.dataframe(df_hist, use_container_width=True)

    if st.button("💾 Guardar cambios del historial", key="inv_guardar_hist"):
        df_inv.to_excel(archivo_inventario, index=False, engine="openpyxl")
        st.success("✅ Cambios del historial guardados")

    # =================================================
    # ✅ CONSUMO MENSUAL CONSOLIDADO POR ÍTEM
    # ✅ (ESTE BLOQUE DEBE ESTAR DENTRO DE TAB 1)
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
                nombre, cantidad = it.rsplit(" x", 1)
                cantidad = int(cantidad)
            else:
                nombre = it
                cantidad = 1
            registros.append({
                "Mes": row["Mes"],
                "Ítem": nombre,
                "Cantidad": cantidad
            })

    df_plot = pd.DataFrame(registros)

    if not df_plot.empty:
        df_plot = df_plot.groupby(["Mes", "Ítem"], as_index=False).sum()
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
            xaxis_title="Mes",
            yaxis_title="Cantidad entregada",
            legend_title="Ítem"
        )

        st.plotly_chart(fig, use_container_width=True)

# ===================================================
# ===================================================
# ✅ TAB 2 — SEGUIMIENTO DIARIO (PARTE 1/4)
# Carga + funciones + normalización
# ===================================================
with tab2:
    st.subheader("🕒 Control de horario de inspectores")
    st.write("### Cargar archivo de bitácora (formato XLSX recomendado)")

    archivo = st.file_uploader(
        "Sube el archivo de bitácora",
        type=["xls", "xlsx"]
    )

    if archivo is None:
        st.info("ℹ️ Carga un archivo de bitácora para iniciar el análisis.")
        st.stop()

    import datetime

    # -----------------------------
    # Funciones utilitarias
    # -----------------------------
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

    def hora_to_decimal(h):
        if h is None or h == "SIN HORA":
            return None
        return h.hour + h.minute/60 + h.second/3600

    def decimal_to_hora(d):
        if d is None or pd.isna(d):
            return None
        h = int(d)
        m = int((d-h)*60)
        return datetime.time(h, m)

    def hora_to_string(h):
        return h.strftime("%I:%M %p") if h else "—"

    def td_to_str(td):
        if pd.isna(td):
            return "—"
        s = int(td.total_seconds())
        h = s // 3600
        m = (s % 3600) // 60
        s2 = s % 60
        return f"{h}h {m}m {s2}s" if h > 0 else f"{m}m {s2}s"

    # -----------------------------
    # Cargar bitácora
    # -----------------------------
    df_bitacora = pd.read_excel(archivo)
    df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

    columnas_necesarias = [
        "fecha de ejecucion","hora inicio","hora final",
        "inspector","localidad","cierre","tiempo de tarea"
    ]

    for col in columnas_necesarias:
        if col not in df_bitacora.columns:
            st.error(f"❌ Falta la columna: {col}")
            st.stop()

    # Normalizar texto
    df_bitacora["inspector"] = (
        df_bitacora["inspector"]
        .astype(str).str.upper().str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df_bitacora["localidad"] = (
        df_bitacora["localidad"]
        .astype(str).str.upper().str.strip()
    )

    # Convertir fechas y horas
    df_bitacora["fecha"] = pd.to_datetime(
        df_bitacora["fecha de ejecucion"], errors="coerce"
    ).dt.date

    df_bitacora["hora_inicio"] = df_bitacora["hora inicio"].apply(parse_hora)
    df_bitacora["hora_final"] = df_bitacora["hora final"].apply(parse_hora)
    df_bitacora["tiempo_tarea_td"] = (
        df_bitacora["tiempo de tarea"].apply(parse_tiempo_tarea)
    )

    df_bitacora["hora_inicio"] = (
        df_bitacora["hora_inicio"].apply(
            lambda x: x if pd.notna(x) else "SIN HORA"
        )
    )

# ===================================================
# ✅ TAB 2 — PARTE 2/4
# Supervisores y filtros
# ===================================================

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

    supervisores_dict = {k.upper(): v for k, v in supervisores_dict.items()}
    df_bitacora["supervisor"] = (
        df_bitacora["inspector"]
        .map(supervisores_dict)
        .fillna("SIN SUPERVISOR")
    )

    # -----------------------------
    # Filtro por fecha
    # -----------------------------
    fechas_validas = sorted(df_bitacora["fecha"].dropna().unique())
    fecha_sel = st.selectbox("Selecciona fecha:", fechas_validas)
    df2 = df_bitacora[df_bitacora["fecha"] == fecha_sel]

    # -----------------------------
    # Filtro por supervisor
    # -----------------------------
    supervisor_sel = st.selectbox(
        "Selecciona supervisor:",
        sorted(df2["supervisor"].unique())
    )
    df2 = df2[df2["supervisor"] == supervisor_sel]

    # -----------------------------
    # Filtro por inspector
    # -----------------------------
    inspectores_disp = sorted(df2["inspector"].unique())
    inspectores_sel = st.multiselect(
        "Selecciona inspectores:",
        inspectores_disp,
        default=inspectores_disp
    )
    df2 = df2[df2["inspector"].isin(inspectores_sel)]

# ===================================================
# ===================================================
# ✅ TAB 2 — PARTE 3 / 4
# Agrupación diaria, puntualidad, producción y KPIs
# ===================================================

# ---------------------------------------------------
# AGRUPACIÓN DIARIA (primera y última hora)
# ---------------------------------------------------
primeras = (
    df2.sort_values("hora_inicio")
       .groupby(["inspector", "fecha"], as_index=False)
       .first()[["inspector", "supervisor", "fecha", "hora_inicio", "localidad"]]
)

ultimas = (
    df2.sort_values("hora_final")
       .groupby(["inspector", "fecha"], as_index=False)
       .last()[["inspector", "fecha", "hora_final"]]
)

df_agrupado = primeras.merge(
    ultimas,
    on=["inspector", "fecha"],
    how="left"
)

# ---------------------------------------------------
# PUNTUALIDAD
# ---------------------------------------------------
hora_oficial = datetime.time(7, 30)

def mins_tarde(h):
    if h == "SIN HORA" or h is None:
        return None
    h1 = datetime.datetime.combine(datetime.date.today(), h)
    h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
    return int((h1 - h2).total_seconds() / 60)

df_agrupado["minutos_tarde"] = df_agrupado["hora_inicio"].apply(mins_tarde)

def estado(m):
    if m is None:
        return "SIN INICIO"
    if m <= 0:
        return "Puntual"
    if m <= 15:
        return "Tarde"
    return "Muy tarde"

df_agrupado["estado"] = df_agrupado["minutos_tarde"].apply(estado)

# ---------------------------------------------------
# PRODUCCIÓN
# ---------------------------------------------------
valores_efectivos = [
    "INSPECCIONADA",
    "INSPECCIONADA CON DEFECTO NO CRITICO",
    "INSPECCIONADA CON DEFECTO CRITICO",
    "CERTIFICADA",
    "CERTIFICADA CON NOVEDAD"
]

df2["efectiva"] = df2["cierre"].isin(valores_efectivos)

total_ordenes = df2.shape[0]
total_efectivas = df2[df2["efectiva"]].shape[0]
porcentaje = round((total_efectivas / total_ordenes) * 100, 1) if total_ordenes else 0

# ---------------------------------------------------
# TIEMPO PROMEDIO TAREAS EFECTIVAS
# ---------------------------------------------------
df_eff = df2[
    (df2["efectiva"]) &
    (df2["tiempo_tarea_td"].notna())
]

tiempo_prom_str = (
    td_to_str(df_eff["tiempo_tarea_td"].mean())
    if not df_eff.empty else "—"
)

# ---------------------------------------------------
# KPI HORAS (PROMEDIOS)
# ---------------------------------------------------
df_agrupado["ini_dec"] = df_agrupado["hora_inicio"].apply(
    lambda x: hora_to_decimal(x) if x != "SIN HORA" else None
)

df_agrupado["fin_dec"] = df_agrupado["hora_final"].apply(
    lambda x: hora_to_decimal(x) if pd.notna(x) else None
)

prom_ini = df_agrupado["ini_dec"].mean()
prom_fin = df_agrupado["fin_dec"].mean()

hora_prom_ini = hora_to_string(decimal_to_hora(prom_ini))
hora_prom_fin = hora_to_string(decimal_to_hora(prom_fin))

dur_prom = (df_agrupado["fin_dec"] - df_agrupado["ini_dec"]).mean()

if pd.notna(dur_prom):
    dur_h = int(dur_prom)
    dur_m = int((dur_prom - dur_h) * 60)
    dur_prom_str = f"{dur_h}h {dur_m}m"
else:
    dur_prom_str = "—"

# ---------------------------------------------------
# KPIs EN PANTALLA
# ---------------------------------------------------
st.markdown("## ⭐ KPIs del día")

c1, c2, c3 = st.columns(3)
c1.metric("⏰ Promedio inicio", hora_prom_ini)
c2.metric("🕒 Promedio fin", hora_prom_fin)
c3.metric("💼 Duración promedio", dur_prom_str)

c4, c5, c6, c7 = st.columns(4)
c4.metric("📋 Tareas", total_ordenes)
c5.metric("✅ Efectivas", total_efectivas)
c6.metric("📈 % Efectividad", f"{porcentaje}%")
c7.metric("🕓 Prom. tarea efectiva", tiempo_prom_str)
# ===================================================
# ===================================================
# ✅ TAB 2 — PARTE 4 / 4
# Tablas finales, producción, TOP 5 y productividad
# ===================================================

# ---------------------------------------------------
# RESUMEN POR INSPECTOR
# ---------------------------------------------------
resumen = (
    df2.groupby("inspector")
       .apply(lambda x: pd.Series({
           "total_ordenes": x.shape[0],
           "ordenes_efectivas": x["efectiva"].sum(),
           "porcentaje_efectividad":
               round((x["efectiva"].sum() / x.shape[0]) * 100, 1)
               if x.shape[0] else 0,
           "promedio_tiempo_tarea":
               td_to_str(
                   x.loc[x["efectiva"] == True, "tiempo_tarea_td"].mean()
               )
       }))
       .reset_index()
)

# ---------------------------------------------------
# ARMAR TABLA COMPLETA DEL DÍA
# ---------------------------------------------------
df_tabla = df_agrupado.merge(resumen, on="inspector", how="left")

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

st.markdown("### 📋 Tabla de inspecciones del día")
st.dataframe(
    df_tabla[
        [
            "inspector", "supervisor", "fecha",
            "hora_inicio", "hora_final", "localidad",
            "estado", "total_ordenes",
            "ordenes_efectivas", "porcentaje_efectividad",
            "promedio_tiempo_tarea"
        ]
    ],
    use_container_width=True
)

# ---------------------------------------------------
# PRODUCCIÓN POR INSPECTOR
# ---------------------------------------------------
st.markdown("## Producción por inspector")

df_prod = (
    df2.groupby("inspector")
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
    color_discrete_map={
        "efectivas": "green",
        "no_efectivas": "red"
    }
)

fig_prod.update_traces(texttemplate="%{x}", textposition="outside")
st.plotly_chart(fig_prod, use_container_width=True)

# ---------------------------------------------------
# TOP 5 EFECTIVIDAD
# ---------------------------------------------------
st.markdown("## 🏆 TOP 5 Efectividad")

df_rank = (
    resumen.sort_values("porcentaje_efectividad", ascending=False)
            .head(5)
)

fig_rank = px.bar(
    df_rank,
    x="porcentaje_efectividad",
    y="inspector",
    orientation="h",
    text="porcentaje_efectividad",
    color="porcentaje_efectividad"
)

fig_rank.update_traces(texttemplate="%{x}%")
st.plotly_chart(fig_rank, use_container_width=True)

# ---------------------------------------------------
# PRODUCTIVIDAD POR HORA
# ---------------------------------------------------
st.markdown("## Productividad por hora (efectivas)")

df_horas = df2[df2["efectiva"] == True]

if df_horas.empty:
    st.info("⚠️ No hay tareas efectivas para esta fecha.")
else:
    df_horas["hora_str"] = df_horas["hora_inicio"].astype(str)

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
        color="cantidad"
    )

    fig_horas.update_traces(textposition="outside")
    st.plotly_chart(fig_horas, use_container_width=True)



# ---------------------------------------------------
# ✅ PESTAÑA 3: GRÁFICAS GENERALES
# ---------------------------------------------------
with tab3:
    st.subheader("Gráficas de desempeño general")
    st.info("Aquí veremos indicadores, tendencias y análisis más avanzados usando Plotly.")

      
