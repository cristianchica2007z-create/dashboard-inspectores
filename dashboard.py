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

# ---------------------------------------------------
# ✅ CABECERA CON LOGO (ARRIBA A LA DERECHA)
# ---------------------------------------------------
col1, col2 = st.columns([6, 2])

with col2:
    st.image("logo.png", width=180)


st.title("📊 Dashboard Inspectores eyc")
st.title("⏰ Control Operación")

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

import requests
import base64

def subir_a_github(ruta_archivo):
    """Sube el archivo inventario.xlsx al repositorio GitHub automáticamente."""
    try:
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        path = st.secrets["github"]["path"]

        # Leer archivo y convertir a Base64
        with open(ruta_archivo, "rb") as f:
            contenido_b64 = base64.b64encode(f.read()).decode()

        # URL para subir archivo
        url = f"https://api.github.com/repos/{repo}/contents/{path}"

        # Verificar si ya existe un archivo previo para obtener SHA
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            sha = r.json()["sha"]  # archivo existente
        else:
            sha = None  # archivo nuevo

        data = {
            "message": "Actualización automática del inventario",
            "content": contenido_b64,
            "branch": "main"
        }

        if sha:
            data["sha"] = sha  # actualizar archivo existente

        # Subir archivo
        r = requests.put(url, headers=headers, json=data)

        if r.status_code in [200, 201]:
            st.success("✅ Inventario subido a GitHub correctamente")
        else:
            st.error(f"❌ Error subiendo archivo: {r.text}")

    except Exception as e:
        st.error(f"❌ Error inesperado al subir a GitHub: {e}")

# ---------------------------------------------------
# ✅ LISTA GLOBAL DE INSPECTORES
# ---------------------------------------------------
inspectores_lista = [
    "ARIZA MARIN SERGIO","ANDRES ARROYAVE","BEDOYA DIEGO ALEJANDRO",
    "DANNY DE LA CRUZ","CARVAJAL RESTREPO JUAN DAVID","JANIER MARIN",
    "CHAVARRIAGA JUAN MANUEL","CRISTIAN CHICA","ECHEVERRY CARDONA JHON STIVEN",
    "GALLEGO CADAVID NORBEY","GIRALDO GARCIA SIGIFREDO","LOPEZ PINEDA CESAR AUGUSTO",
    "NOREÑA GIRALDO GEOVANNY","OSPINA CASTELLANOS ANDERSON",
    "OSPINA RODRIGUEZ DANIEL ALBERTO","RUIZ DILON MARLON ANDREY",
    "LARGO OSORIO JOSE OMAR","PULGARIN QUINTERO JULIAN ANDRES",
    "TAYACK TRUJILLO DEIVER EVELIO","RUIZ ARENAS JUAN CAMILO",
    "PATIÑO CIFUENTES RICARDO","VARGAS FRANCO JHON EDISON",
    "CARDONA CANO NELSON","CARDONA OROZCO JULIAN ANDRES",
    "GRISALES CUERVO JUAN DAVID","LEON MARIN LEONARDO FABIO",
    "VELASQUEZ TAPASCO JHON DIEGO","CARDONA CASTANO DIDIER ORLANDO",
    "TORRES HERNANDEZ JOHN JAMES","COBO HOYOS JUAN MANUEL",
    "OSPINA NARANJO BERNARDO","COGOLLO FIGUEROA RANDY",
    "ARIAS TORO YEISON","MIRANDA FRANCO EFRAIN",
    "ARDILA MORA GUSTAVO ADOLFO","LOPEZ VELEZ ESTEBAN",
    "GALEANO GRISALEZ RICARDO","CAICEDO ESCOBAR JUNIOR SANTIAGO",
    "OTERO CAICEDO ANYEMBER","BUITRAGO RAMIREZ LEONARD",
    "BORJAS WILLY ALEXANDER","MARIN LEON JAISSON JOAQUIN",
    "AMAYA HINCAPIE JUAN CARLOS","BEDOYA SANCHEZ CRISTIAN DAVID",
    "RAMIREZ WILSON ENRIQUE","CANO MORALES JIMY ALFREDO",
    "CASTRO CASTAÑO JUAN DAVID","LOAIZA GAMBA JHON ALEXANDER",
    "VILLA LOAIZA JHEISON ESTIBEN","CÁRDENAS GALIANO HAROLD MAURICIO",
    "VARGAS CORREA VICTOR ALFONSO","VILLA MERA CHRISTIAN DAVID",
    "AVENDAÑO GARCIA JUAN NEPOMUCENO","PELAEZ TATIS GABRIEL ESTEBAN"
]


# ---------------------------------------------------
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA (FINAL DEFINITIVO)
# ---------------------------------------------------
# ---------------------------------------------------
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA (FINAL)
# ---------------------------------------------------
# ---------------------------------------------------
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA (FINAL ESTABLE)
# ---------------------------------------------------
with tab1:
    st.subheader("📦 Control de entrega de inventario")

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
                with cols[c_idx]:
                    marcar = st.checkbox(
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
# -----------------------------------------------------
# ✅ PESTAÑA 2: SEGUIMIENTO DIARIO — ARCHIVO COMPARTIDO
# -----------------------------------------------------
with tab2:
    st.subheader("🕒 Control de horario de inspectores")

    ARCHIVO_BITACORA = "BITACORA.xlsx"

    st.info(
        "El archivo de bitácora es compartido. "
        "Cuando un usuario lo actualiza, todos los demás verán la nueva información."
    )

    # -----------------------------------------------------
    # ✅ CARGA Y REEMPLAZO DEL ARCHIVO COMPARTIDO
    # -----------------------------------------------------
    archivo = st.file_uploader(
        "Cargar archivo de bitácora diaria (reemplaza el anterior)",
        type=["xls", "xlsx"],
        key="bitacora_tab2"
    )

    # Si alguien sube archivo → guardar y subir a GitHub
    if archivo is not None:
        with open(ARCHIVO_BITACORA, "wb") as f:
            f.write(archivo.read())

        subir_a_github(ARCHIVO_BITACORA)

        st.success("✅ Archivo BITACORA.xlsx actualizado y compartido correctamente")

    # -----------------------------------------------------
    # ✅ LEER SIEMPRE DESDE EL ARCHIVO COMPARTIDO
    # -----------------------------------------------------
    if not os.path.exists(ARCHIVO_BITACORA):
        st.warning("⚠️ Aún no se ha cargado ningún archivo de bitácora.")
        st.stop()

    df = pd.read_excel(ARCHIVO_BITACORA)
    st.caption("📁 Usando archivo compartido actual: BITACORA.xlsx")

    # -----------------------------------------------------
    # A PARTIR DE AQUÍ, TU CÓDIGO ORIGINAL SIGUE IGUAL
    # -----------------------------------------------------
    import numpy as np
    import datetime

    # Funciones utilitarias
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
    # NORMALIZAR COLUMNAS
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
    # NORMALIZAR NOMBRES
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
    # CONVERTIR FECHAS Y HORAS
    # -----------------------------------------------------
    df["fecha"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce").dt.date
    df["hora_inicio"] = df["hora inicio"].apply(parse_hora)
    df["hora_final"] = df["hora final"].apply(parse_hora)
    df["tiempo_tarea_td"] = df["tiempo de tarea"].apply(parse_tiempo_tarea)

    df["hora_inicio"] = df["hora_inicio"].apply(
        lambda x: x if pd.notna(x) else "SIN HORA"
    )

    # -----------------------------------------------------
    # ⏱️ AQUÍ CONTINÚA TODO TU TAB2 ORIGINAL
    # (filtros, KPIs, tablas, gráficas… sin cambios)
    # -----------------------------------------------------

# ---------------------------------------------------
# ✅ PESTAÑA 3: GRÁFICAS GENERALES
# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------
# ---------------------------------------------------
# ✅ TAB 3 — SEGUIMIENTO MENSUAL (MULTI‑DÍA)
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
