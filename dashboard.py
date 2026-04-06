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

        # -------- DATOS GENERALES --------
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
                marcar = cols[c_idx].checkbox(
                    item,
                    key=f"item_chk_{f_idx}_{c_idx}"
                )

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

    # =================================================
    # ✅ GUARDAR HISTORIAL
    # =================================================
    if st.button("💾 Guardar cambios del historial", key="inv_guardar_hist"):
        df_inv.to_excel(archivo_inventario, index=False, engine="openpyxl")
        st.success("✅ Cambios del historial guardados")
    # =================================================
# =================================================
# =================================================
# ✅ RESUMEN MENSUAL CONSOLIDADO POR ÍTEM
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
        xaxis_title="Mes",
        yaxis_title="Cantidad entregada",
        legend_title="Ítem"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------

# ===================================================
# ===================================================
# ✅ TAB 2 — SEGUIMIENTO DIARIO (BITÁCORA LIMPIA)
# ===================================================
with tab2:
    st.subheader("🕒 Control de horario de inspectores")

    ARCHIVO_BITACORA = "BITACORA.xlsx"

    # ---------------------------------------------------
    # CARGA DE BITÁCORA
    # ---------------------------------------------------
    st.write("### Cargar archivo de bitácora (formato XLSX recomendado)")
    archivo = st.file_uploader(
        "Sube SOLO el archivo de bitácora diaria",
        type=["xls", "xlsx"]
    )

    if archivo:
        with open(ARCHIVO_BITACORA, "wb") as f:
            f.write(archivo.read())
        st.success("✅ Bitácora actualizada y compartida")

    if not os.path.exists(ARCHIVO_BITACORA):
        st.info("ℹ️ Sube una bitácora para iniciar el análisis.")
        st.stop()

    # ---------------------------------------------------
    # LECTURA Y NORMALIZACIÓN
    # ---------------------------------------------------
    df_bitacora = pd.read_excel(ARCHIVO_BITACORA)
    df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

    st.write("📄 Vista previa de la bitácora")
    st.dataframe(df_bitacora.head(), use_container_width=True)

    # ---------------------------------------------------
    # FUNCIONES
    # ---------------------------------------------------
    def parse_hora(valor):
        try:
            return pd.to_datetime(valor, format="%H:%M").time()
        except:
            return pd.NaT

    # ---------------------------------------------------
    # VALIDAR COLUMNAS NECESARIAS
    # ---------------------------------------------------
    columnas_necesarias = [
        "fecha de ejecucion", "hora inicio", "hora final",
        "inspector", "localidad", "cierre", "tiempo de tarea"
    ]

    for col in columnas_necesarias:
        if col not in df_bitacora.columns:
            st.error(f"❌ Falta la columna: {col}")
            st.stop()

    # ---------------------------------------------------
    # CONVERTIR COLUMNAS
    # ---------------------------------------------------
    df_bitacora["fecha"] = pd.to_datetime(
        df_bitacora["fecha de ejecucion"], errors="coerce"
    ).dt.date

    df_bitacora["hora_inicio"] = df_bitacora["hora inicio"].apply(parse_hora)
    df_bitacora["hora_final"] = df_bitacora["hora final"].apply(parse_hora)
    df_bitacora["inspector"] = df_bitacora["inspector"].astype(str).str.strip()

    df_bitacora = df_bitacora.dropna(
        subset=["hora_inicio", "hora_final"]
    )

    # ---------------------------------------------------
    # SUPERVISORES
    # ---------------------------------------------------
    supervisores_dict = {
        "ARIZA MARIN SERGIO": "ANDRES ARROYAVE",
        "BEDOYA DIEGO ALEJANDRO": "DANNY DE LA CRUZ",
        "CHAVARRIAGA JUAN MANUEL": "CRISTIAN CHICA",
        "PATIÑO CIFUENTES RICARDO": "JANIER MARIN",
        "VARGAS FRANCO JHON EDISON": "CRISTIAN CHICA",
    }

    df_bitacora["supervisor"] = (
        df_bitacora["inspector"]
        .map(supervisores_dict)
        .fillna("SIN SUPERVISOR")
    )

    # ---------------------------------------------------
    # PRIMERA Y ÚLTIMA HORA DEL DÍA
    # ---------------------------------------------------
    primeras = (
        df_bitacora.sort_values("hora_inicio")
        .groupby(["inspector", "fecha"], as_index=False)
        .first()[["inspector", "supervisor", "fecha", "hora_inicio"]]
    )

    ultimas = (
        df_bitacora.sort_values("hora_final")
        .groupby(["inspector", "fecha"], as_index=False)
        .last()[["inspector", "fecha", "hora_final"]]
    )

    df_agrupado = primeras.merge(
        ultimas,
        on=["inspector", "fecha"],
        how="left"
    )

    # ---------------------------------------------------
    # RESULTADO FINAL
    # ---------------------------------------------------
    st.markdown("### 📊 Resumen diario por inspector")
    st.dataframe(df_agrupado, use_container_width=True)

# ---------------------------------------------------
# ✅ PESTAÑA 3: GRÁFICAS GENERALES
# ---------------------------------------------------
with tab3:
    st.subheader("Gráficas de desempeño general")
    st.info("Aquí veremos indicadores, tendencias y análisis más avanzados usando Plotly.")

      
