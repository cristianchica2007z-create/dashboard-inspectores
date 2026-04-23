import streamlit as st
import pandas as pd
import os
import plotly.express as px
import json
import datetime
from zoneinfo import ZoneInfo
import base64
import requests
import io



# -------------------------------------------------
# ZONA HORARIA COLOMBIA
# -------------------------------------------------

import datetime

TZ_CO = ZoneInfo("America/Bogota")

info = {
    "ultima_actualizacion": datetime.datetime.now(TZ_CO).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
}



if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.rol = None

def cargar_usuarios():
    if os.path.exists("USUARIOS.json"):
        with open("USUARIOS.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

if st.session_state.usuario is None:

    st.markdown("""
        <style>
        .login-card {
            max-width: 420px;
            margin: 4rem auto;
            padding: 2.5rem;
            border-radius: 18px;
            background-color: #ffffff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .login-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 2rem;
            color: #0d3b66;
        }
        </style>
    """, unsafe_allow_html=True)

    st.image("logo.png", width=420)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">INICIAR SESIÓN</div>', unsafe_allow_html=True)

    usuarios = cargar_usuarios()

    usuario = st.text_input("Usuario")
    pin = st.text_input("PIN (4 dígitos)", type="password", max_chars=4)

    if st.button("🔐 INICIAR SESIÓN", use_container_width=True):
        if usuario in usuarios and pin == usuarios[usuario]["pin"]:
            st.session_state.usuario = usuario
            st.session_state.rol = usuarios[usuario]["rol"]
            st.rerun()
        else:
            st.error("❌ Usuario o PIN incorrectos")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -------------------------------------------------
# BOTÓN CERRAR SESIÓN
# -------------------------------------------------
col_vacio, col_logout = st.columns([8, 1])

with col_logout:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.usuario = None
        st.session_state.rol = None
        st.rerun()

    
# ---------------------------------------------------
# ✅ LISTA MAESTRA DE INSPECTORES
# ---------------------------------------------------
inspectores_lista = sorted([
  
    "ARIZA MARIN SERGIO",
    "ANDRES ARROYAVE",
    "BEDOYA DIEGO ALEJANDRO",
    "DANNY DE LA CRUZ",
    "CARVAJAL RESTREPO JUAN DAVID",
    "JANIER MARIN",
    "CHAVARRIAGA JUAN MANUEL",
    "CRISTIAN CHICA",
    "ECHEVERRY CARDONA JHON STIVEN",
    "GALLEGO CADAVID NORBEY",
    "GIRALDO GARCIA SIGIFREDO",
    "LOPEZ PINEDA CESAR AUGUSTO",
    "NOREÑA GIRALDO GEOVANNY",
    "OSPINA CASTELLANOS ANDERSON",
    "OSPINA RODRIGUEZ DANIEL ALBERTO",
    "RUIZ DILON MARLON ANDREY",
    "LARGO OSORIO JOSE OMAR",
    "PULGARIN QUINTERO JULIAN ANDRES",
    "TAYACK TRUJILLO DEIVER EVELIO",
    "RUIZ ARENAS JUAN CAMILO",
    "PATIÑO CIFUENTES RICARDO",
    "VARGAS FRANCO JHON EDISON",
    "CARDONA CANO NELSON",
    "CARDONA OROZCO JULIAN ANDRES",
    "GRISALES CUERVO JUAN DAVID",
    "LEON MARIN LEONARDO FABIO",
    "VELASQUEZ TAPASCO JHON DIEGO",
    "CARDONA CASTANO DIDIER ORLANDO",
    "TORRES HERNANDEZ JOHN JAMES",
    "COBO HOYOS JUAN MANUEL",
    "OSPINA NARANJO BERNARDO",
    "COGOLLO FIGUEROA RANDY",
    "ARIAS TORO YEISON",
    "MIRANDA FRANCO EFRAIN",
    "ARDILA MORA GUSTAVO ADOLFO",
    "LOPEZ VELEZ ESTEBAN",
    "GALEANO GRISALEZ RICARDO",
    "CAICEDO ESCOBAR JUNIOR SANTIAGO",
    "OTERO CAICEDO ANYEMBER",
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
    page_title="DASHBOARD INSPECTORES e&c",
       layout="wide"
)

# -------------------------------------------------
# HEADER CON LOGO A LA DERECHA (CORRECTO)
# -------------------------------------------------
col_titulo, col_logo = st.columns([8, 2])

with col_titulo:
    st.markdown(
        "<h1 style='margin-bottom: 0;'>📊 DASHBOARD INSPECTORES E&C</h1>",
        unsafe_allow_html=True
    )

with col_logo:
    st.image(
        "logo.png",
        use_container_width=True,
        caption=""
    )
# ---------------------------------------------------
# ✅ CREAR PESTAÑAS
# ---------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Inventario Papelería",
    "🕒 Seguimiento Diario",
    "📈 Subir Archivos",
     "📅 Seguimiento agendas",
    "📌 Órdenes Asignadas"

    
])

# ===================================================
# ===================================================
# ✅ TAB 1 — INVENTARIO DE PAPELERÍA
# ===================================================
with tab1:
    st.subheader("📦 Control de entrega de papelería e inventario")

    # ==============================
    # LEER INVENTARIO DESDE GITHUB
    # ==============================
    archivo_inventario = "inventario.xlsx"

    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]
    branch = st.secrets["github"].get("branch", "main")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    url_inv = f"https://api.github.com/repos/{repo}/contents/{archivo_inventario}"
    r = requests.get(url_inv, headers=headers)

    if r.status_code == 200:
        contenido = r.json()["content"]
        binario = base64.b64decode(contenido)
        buffer = io.BytesIO(binario)
        df_inv = pd.read_excel(buffer, engine="openpyxl")
    else:
        df_inv = pd.DataFrame(columns=[
            "Fecha", "Sede", "Inspector",
            "Responsable", "Observación", "Ítems"
        ])

    df_inv.columns = df_inv.columns.str.strip()

    # ===================================================
    # FORMULARIO DE REGISTRO
    # ===================================================
    with st.form("form_entrega", clear_on_submit=True):
        st.markdown("### Registrar entrega")

        col1, col2, col3 = st.columns(3)

        sede = col1.selectbox("Sede", ["CALDAS", "RISARALDA"])
        inspector = col2.selectbox("Inspector", inspectores_lista)
        fecha = col3.date_input("Fecha")

        responsable = st.selectbox(
            "Responsable",
            [
                "JUAN DIEGO SANCHEZ",
                "CRISTIAN CHICA",
                "ANDRES ARROYAVE",
                "MARIA CAMILA",
                "JANIER",
                "DANNY DE LA CRUZ"
            ]
        )

        observacion = st.text_input("Observación (opcional)")

        st.markdown("### Ítems entregados")

        items_def = [
            "Stickers 🔵", "Cepo 🔒", "Guantes 🧤", "Piernera 🦿",
            "Monogafas 🥽", "Llaves de cepo 🗝️","Papelería general 📦"
        ]

        items_seleccionados = []

        filas = [items_def[i:i+4] for i in range(0, len(items_def), 4)]
        for f_idx, fila in enumerate(filas):
            cols = st.columns(4)
            for c_idx, item in enumerate(fila):
                marcar = cols[c_idx].checkbox(item, key=f"item_{f_idx}_{c_idx}")
                cantidad = cols[c_idx].number_input(
                    "Cantidad",
                    min_value=0,
                    step=1,
                    label_visibility="collapsed",
                    key=f"qty_{f_idx}_{c_idx}"
                )
                if marcar and cantidad > 0:
                    items_seleccionados.append(f"{item} x{cantidad}")

        submitted = st.form_submit_button("✅ Guardar entrega")

    # ===================================================
    # GUARDAR ENTREGA (SOLO CUANDO SUBMITTED)
    # ===================================================
    if submitted:
        if not items_seleccionados:
            st.warning("⚠️ Debes seleccionar al menos un ítem con cantidad")
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

            buffer = io.BytesIO()
            df_inv.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            contenido_b64 = base64.b64encode(buffer.read()).decode("utf-8")
            sha = r.json().get("sha") if r.status_code == 200 else None

            payload = {
                "message": "Registro de entrega de papelería",
                "content": contenido_b64,
                "branch": branch
            }

            if sha:
                payload["sha"] = sha

            requests.put(url_inv, headers=headers, json=payload)

            st.success("✅ Entrega registrada y guardada correctamente")

    # ===================================================
    # HISTORIAL (SIEMPRE SE MUESTRA)
    # ===================================================
    st.markdown("### 📋 Historial de entregas")

    filtro_inspector = st.selectbox(
        "Filtrar por inspector",
        ["TODOS"] + inspectores_lista
    )

    df_hist = df_inv.copy()
    if filtro_inspector != "TODOS":
        df_hist = df_hist[df_hist["Inspector"] == filtro_inspector]

    st.dataframe(df_hist, use_container_width=True)

    # ===================================================
    # CONSUMO MENSUAL
    # ===================================================
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
            nombre, cantidad = it.rsplit(" x", 1) if " x" in it else (it, 1)
            registros.append({"Mes": row["Mes"], "Ítem": nombre, "Cantidad": int(cantidad)})

    df_plot = pd.DataFrame(registros)
    if not df_plot.empty:
        df_plot = df_plot.groupby(["Mes", "Ítem"], as_index=False).sum()
        fig = px.bar(df_plot, x="Mes", y="Cantidad", color="Ítem", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

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
            ["Mes", "Ítem"],
            as_index=False
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



# ===================================================
# ===================================================
# ✅ TAB 2 — PARTE 1 / 4
# Carga + funciones + normalización
# LEE BITACORA.xlsx DESDE EL REPOSITORIO
# ===================================================
with tab2:
    st.subheader("🕒 Control Operativo e&c")
    st.subheader("Eje Cafetero")

    # -------------------------------------------------
    # VALIDAR QUE EXISTA BITÁCORA COMPARTIDA
    # -------------------------------------------------
    archivo_bitacora = "BITACORA.xlsx"

    if not os.path.exists(archivo_bitacora):
        st.warning(
            "⚠️ No hay una bitácora cargada.\n\n"
            "Un administrador debe subir el archivo en la pestaña "
            "📂 Administración de Bitácora."
        )
        st.stop()

    # -------------------------------------------------
    # CARGAR BITÁCORA COMPARTIDA
    # -------------------------------------------------
    df_bitacora = pd.read_excel(archivo_bitacora)

    # -------------------------------------------------
    # NORMALIZAR NOMBRES DE COLUMNAS
    # -------------------------------------------------
    df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

    # -------------------------------------------------
    # ✅ EXCLUIR GRUPOS NO OPERATIVOS (REGLA DEFINITIVA)
    # -------------------------------------------------
    if "grupo" in df_bitacora.columns:
        df_bitacora["grupo"] = (
            df_bitacora["grupo"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        grupos_no_operativos = [
            "SST-NAL",
            "SUPERVISIONES",
            "SUSP-ANT"
        ]

        df_bitacora = df_bitacora[
            ~df_bitacora["grupo"].isin(grupos_no_operativos)
        ]

    # -------------------------------------------------
    # PROTECCIÓN: EVITAR PESTAÑA VACÍA
    # -------------------------------------------------
    if df_bitacora.empty:
        st.warning(
            "⚠️ No hay datos disponibles después del filtro por GRUPO.\n"
            "Esto indica que el archivo solo contiene grupos no operativos."
        )
        st.stop()

    # -------------------------------------------------
 # -------------------------------------------------
    # MOSTRAR FECHA, HORA (COLOMBIA) Y USUARIO QUE ACTUALIZÓ
    # -------------------------------------------------
    TZ_UTC = ZoneInfo("UTC")
    TZ_CO = ZoneInfo("America/Bogota")

    info_path = "BITACORA_INFO.json"
    ultima_actualizacion = "—"
    usuario_actualizo = "—"

    try:
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)

                fecha_utc = datetime.datetime.strptime(
                    info.get("ultima_actualizacion"),
                    "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=TZ_UTC)

                fecha_colombia = fecha_utc.astimezone(TZ_CO)

                ultima_actualizacion = fecha_colombia.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                usuario_actualizo = info.get("usuario_actualizo", "—")

    except Exception:
        ultima_actualizacion = "—"
        usuario_actualizo = "—"

    st.caption(
        f"🕓 Última actualización: {ultima_actualizacion} "
        f"| 👤 Actualizó: {usuario_actualizo}"
    )

    # -------------------------------------------------
    # FUNCIONES UTILITARIAS DE TIEMPO
    # -------------------------------------------------
    import datetime

    def parse_hora(valor):
        try:
            return pd.to_datetime(valor, format="%H:%M").time()
        except Exception:
            try:
                return pd.to_datetime(str(valor)).time()
            except Exception:
                return None

    def parse_tiempo_tarea(valor):
        try:
            return pd.to_timedelta(str(valor))
        except Exception:
            return pd.NaT

    def hora_to_decimal(h):
        if h is None or h == "SIN HORA":
            return None
        return h.hour + h.minute / 60 + h.second / 3600

    def decimal_to_hora(d):
        if d is None or pd.isna(d):
            return None
        h = int(d)
        m = int((d - h) * 60)
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

    # -------------------------------------------------
    # NORMALIZAR COLUMNAS
    # -------------------------------------------------
    df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

    columnas_necesarias = [
        "fecha de ejecucion", "hora inicio", "hora final",
        "inspector", "localidad", "cierre", "tiempo de tarea"
    ]

    for col in columnas_necesarias:
        if col not in df_bitacora.columns:
            st.error(f"❌ Falta la columna requerida: {col}")
            st.stop()

    # -------------------------------------------------
    # NORMALIZAR TEXTO
    # -------------------------------------------------
    df_bitacora["inspector"] = (
        df_bitacora["inspector"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    df_bitacora["localidad"] = (
        df_bitacora["localidad"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    # -------------------------------------------------
    # CONVERTIR FECHAS Y HORAS
    # -------------------------------------------------
    df_bitacora["fecha"] = pd.to_datetime(
        df_bitacora["fecha de ejecucion"], errors="coerce"
    ).dt.date

    df_bitacora["hora_inicio"] = df_bitacora["hora inicio"].apply(parse_hora)
    df_bitacora["hora_final"] = df_bitacora["hora final"].apply(parse_hora)

    df_bitacora["tiempo_tarea_td"] = (
        df_bitacora["tiempo de tarea"].apply(parse_tiempo_tarea)
    )

    # Mantener registros sin hora (SIN HORA)
    df_bitacora["hora_inicio"] = df_bitacora["hora_inicio"].apply(
        lambda x: x if pd.notna(x) else "SIN HORA"
    )
    # ===================================================
   # ===================================================
    # ✅ TAB 2 — PARTE 2 / 4
    # Supervisores y filtros
    # ===================================================

    # -------------------------------------------
    # ASIGNAR SUPERVISOR A CADA INSPECTOR
    # -------------------------------------------
    supervisores_dict = {k.upper(): v for k, v in {
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
    }.items()}

    df_bitacora["supervisor"] = (
        df_bitacora["inspector"]
        .map(supervisores_dict)
        .fillna("SIN SUPERVISOR")
    )

    # -------------------------------------------
    # FILTRO DE FECHA
    # -------------------------------------------
    fechas_validas = sorted(df_bitacora["fecha"].dropna().unique())
    fecha_sel = st.selectbox("Selecciona fecha:", fechas_validas)
    df2 = df_bitacora[df_bitacora["fecha"] == fecha_sel]

    # -------------------------------------------
    # FILTRO DE SUPERVISORES (CHECKLIST TIPO EXCEL ✅)
    # -------------------------------------------
    supervisores_disponibles = sorted(df2["supervisor"].unique())

    with st.expander("Seleccionar supervisores", expanded=True):
        supervisores_sel = []
        for sup in supervisores_disponibles:
            if st.checkbox(
                sup,
                value=True,
                key=f"sup_{fecha_sel}_{sup}"
            ):
                supervisores_sel.append(sup)

    if supervisores_sel:
        df2 = df2[df2["supervisor"].isin(supervisores_sel)]
    else:
        st.warning("⚠️ Selecciona al menos un supervisor.")
        st.stop()

    if df2.empty:
        st.warning("⚠️ No hay datos para los supervisores seleccionados.")
        st.stop()

    # -------------------------------------------
   # -------------------------------------------
# -------------------------------------------
# -------------------------------------------
# FILTRO DE INSPECTORES (DEPENDIENTE)
    # -------------------------------------------
    inspectores_disponibles = sorted(df2["inspector"].unique())

    inspectores_sel = st.multiselect(
        "Selecciona inspectores:",
        inspectores_disponibles,
        default=inspectores_disponibles
    )

    if inspectores_sel:
        df2 = df2[df2["inspector"].isin(inspectores_sel)]
    else:
        st.warning("⚠️ Selecciona al menos un inspector.")
        st.stop()
# ===================================================
# ===================================================
    # ✅ TAB 2 — PARTE 3 / 4
    # Agrupación diaria, puntualidad, producción y KPIs
    # ===================================================

    # ---------------------------------------------------
    # AGRUPACIÓN DIARIA (solo para puntualidad y tabla)
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
    # PUNTUALIDAD (usa SOLO la primera hora del día)
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
    # PRODUCCIÓN (MARCAR ÓRDENES EFECTIVAS)
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
    total_efectivas = df2["efectiva"].sum()

    porcentaje = (
        round((total_efectivas / total_ordenes) * 100, 1)
        if total_ordenes > 0 else 0
    )

    # ---------------------------------------------------
    # ÓRDENES EFECTIVAS CON TIEMPO VÁLIDO
    # ---------------------------------------------------
    df_eff = df2[
        (df2["efectiva"] == True) &
        (df2["tiempo_tarea_td"].notna())
    ]

    # ---------------------------------------------------
# ---------------------------------------------------
    # ✅ KPI: PROMEDIO HORA DE INICIO
    # (PRIMERA TAREA DEL DÍA POR INSPECTOR)
    # ---------------------------------------------------
    df_inicio_jornada = (
        df2[
            (df2["hora_inicio"] != "SIN HORA") &
            (df2["hora_inicio"].notna())
        ]
        .groupby("inspector", as_index=False)
        .agg({"hora_inicio": "min"})
    )

    df_inicio_jornada["ini_dec"] = (
        df_inicio_jornada["hora_inicio"]
        .apply(hora_to_decimal)
    )

    prom_ini = df_inicio_jornada["ini_dec"].mean()

    hora_prom_ini = (
        hora_to_string(decimal_to_hora(prom_ini))
        if pd.notna(prom_ini) else "—"
    )

    # ---------------------------------------------------
    # ✅ KPI: PROMEDIO HORA DE FIN
    # (ÚLTIMA TAREA DEL DÍA POR INSPECTOR)
    # ---------------------------------------------------
    df_fin_jornada = (
        df2[
            df2["hora_final"].notna()
        ]
        .groupby("inspector", as_index=False)
        .agg({"hora_final": "max"})
    )

    df_fin_jornada["fin_dec"] = (
        df_fin_jornada["hora_final"]
        .apply(hora_to_decimal)
    )

    prom_fin = df_fin_jornada["fin_dec"].mean()

    hora_prom_fin = (
        hora_to_string(decimal_to_hora(prom_fin))
        if pd.notna(prom_fin) else "—"
    )
    # ---------------------------------------------------
    # ✅ KPI: PROMEDIO TIEMPO POR TAREA (SOLO EFECTIVAS)
    # ---------------------------------------------------
    tiempo_prom_str = (
        td_to_str(df_eff["tiempo_tarea_td"].mean())
        if not df_eff.empty else "—"
    )

    # ---------------------------------------------------
    # KPIs EN PANTALLA (ORDEN ORIGINAL)
    # ---------------------------------------------------
    st.markdown("## ⭐ KPIs del día")

    c1, c2, c3 = st.columns(3)
    c1.metric("⏰ Promedio inicio", hora_prom_ini)
    c2.metric("🕒 Promedio fin", hora_prom_fin)
    c3.metric("🕓 Prom. tiempo por tarea", tiempo_prom_str)

    c4, c5, c6 = st.columns(3)
    c4.metric("📋 Total tareas", total_ordenes)
    c5.metric("✅ Efectivas", total_efectivas)
    c6.metric("📈 % Efectividad", f"{porcentaje}%")

    # ---------------------------------------------------
    # RESUMEN POR INSPECTOR (SOLO PARA CÁLCULO)
    # ---------------------------------------------------
    resumen = (
        df2.groupby("inspector")
           .apply(lambda x: pd.Series({
               "total_ordenes": x.shape[0],
               "ordenes_efectivas": x["efectiva"].sum(),
               "porcentaje_efectividad":
                   round((x["efectiva"].sum() / x.shape[0]) * 100, 1)
                   if x.shape[0] > 0 else 0,
               "promedio_tiempo_tarea":
                   td_to_str(
                       x.loc[x["efectiva"], "tiempo_tarea_td"].mean()
                   )
           }))
           .reset_index()
    )

    # ---------------------------------------------------
    # TABLA CONSOLIDADA DEL DÍA (UNA SOLA)
    # ---------------------------------------------------
    df_tabla = df_agrupado.merge(
        resumen,
        on="inspector",
        how="left"
    )

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


    # ---------------------------------------------------
# 🎨 ESTILO DE PUNTUALIDAD PARA LA TABLA
# ---------------------------------------------------
def estilo_puntualidad(row):
    if row["estado"] == "Muy tarde":
        return ["background-color: #f8d7da; color: #721c24"] * len(row)
    elif row["estado"] == "Tarde":
        return ["background-color: #fff3cd; color: #856404"] * len(row)
    else:
        return [""] * len(row)


    
# ---------------------------------------------------
# 📋 Tabla de inspecciones del día (con colores)
# ---------------------------------------------------
st.dataframe(
    df_tabla[
        [
            "inspector",
            "supervisor",
            "fecha",
            "hora_inicio",
            "hora_final",
            "localidad",
            "estado",
            "total_ordenes",
            "ordenes_efectivas",
            "porcentaje_efectividad",
            "promedio_tiempo_tarea"
        ]
    ]
    .style
    .apply(estilo_puntualidad, axis=1),
    use_container_width=True
)


  # ===================================================
    # ✅ TAB 2 — PARTE 4 / 4
    # Gráficas finales
    # ===================================================

  # ---------------------------------------------------
# ---------------------------------------------------
# ✅ PRODUCCIÓN POR INSPECTOR (SOLO ORDENES EFECTIVAS)
# ---------------------------------------------------
st.markdown("## 📊 Producción por inspector (órdenes efectivas)")

df_prod = (
    df2[df2["efectiva"] == True]
    .groupby("inspector")
    .size()
    .reset_index(name="Órdenes efectivas")
    .sort_values("Órdenes efectivas", ascending=False)
)

if df_prod.empty:
    st.info("⚠️ No hay órdenes efectivas para esta fecha.")
else:
    fig_prod = px.bar(
        df_prod,
        y="inspector",
        x="Órdenes efectivas",
        orientation="h",
        text="Órdenes efectivas",
        title="Órdenes efectivas por inspector",
        color_discrete_sequence=["green"]
    )

    # 🔥 HACER LOS NÚMEROS MUCHO MÁS GRANDES
    fig_prod.update_traces(
        textposition="outside",
        textfont_size=35,        # ⬅️ AQUÍ el tamaño (ajústalo si quieres)
        textfont_color="black",
        cliponaxis=False
    )

    fig_prod.update_layout(
        xaxis_title="Órdenes efectivas",
        yaxis_title="Inspector",
        font=dict(size=18)       # tamaño general del gráfico
    )

    st.plotly_chart(fig_prod, use_container_width=True)




# ---------------------------------------------------
# ===================================================
# ===================================================
# ✅ TAB 3 — ADMINISTRACIÓN DE BITÁCORA (PROTEGIDO)
# Guarda / reemplaza BITACORA.xlsx en GitHub
# Guarda fecha y hora en BITACORA_INFO.json
# ===================================================
with tab3:
    st.subheader("🔐 Administración de Bitácora Compartida")

    # -------------------------------------------------
    # VALIDACIÓN DE ADMINISTRADOR
    # -------------------------------------------------
    clave_ingresada = st.text_input(
        "Contraseña de administrador",
        type="password",
        placeholder="Ingresa la clave para administrar la bitácora"
    )

    clave_real = st.secrets["admin"]["password"]

    if clave_ingresada != clave_real:
        st.warning(
            "⛔ Acceso restringido.\n\n"
            "Solo personal autorizado puede cargar o actualizar la bitácora."
        )
        st.stop()

    # -------------------------------------------------
    # CONTENIDO SOLO PARA ADMIN
    # -------------------------------------------------
    st.success("✅ Acceso autorizado")

    st.info(
        "Desde aquí se sube la bitácora OFICIAL.\n\n"
        "Al cargar un nuevo archivo, este reemplazará el anterior y "
        "todos los usuarios verán la MISMA información en la pestaña "
        "🕒 Seguimiento Diario (TAB 2)."
    )

    archivo = st.file_uploader(
        "Sube el archivo BITACORA.xlsx",
        type=["xls", "xlsx"]
    )

    if archivo is not None:
        import base64
        import requests
        import json
        import datetime
        from zoneinfo import ZoneInfo

        # -----------------------------
        # ZONA HORARIA
        # -----------------------------
        TZ_UTC = ZoneInfo("UTC")

        # -----------------------------
        # LEER SECRETS DE GITHUB
        # -----------------------------
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"].get("branch", "main")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }

        # =================================================
        # 1️⃣ GUARDAR / REEMPLAZAR BITACORA.xlsx
        # =================================================
        contenido_excel = archivo.read()
        contenido_excel_b64 = base64.b64encode(
            contenido_excel
        ).decode("utf-8")

        url_excel = f"https://api.github.com/repos/{repo}/contents/BITACORA.xlsx"

        r_excel = requests.get(url_excel, headers=headers)
        sha_excel = r_excel.json().get("sha") if r_excel.status_code == 200 else None

        payload_excel = {
            "message": "Actualización de BITACORA.xlsx desde Streamlit",
            "content": contenido_excel_b64,
            "branch": branch
        }

        if sha_excel:
            payload_excel["sha"] = sha_excel

        r_put_excel = requests.put(
            url_excel,
            headers=headers,
            json=payload_excel
        )

        if r_put_excel.status_code not in (200, 201):
            st.error("❌ Error al guardar BITACORA.xlsx en GitHub")
            st.json(r_put_excel.json())
            st.stop()

        # =================================================
        # 2️⃣ GUARDAR FECHA, HORA Y USUARIO (BITACORA_INFO.json)
        # =================================================
        info = {
            "ultima_actualizacion": datetime.datetime.now(TZ_UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "usuario_actualizo": st.session_state.usuario
        }

        contenido_info_b64 = base64.b64encode(
            json.dumps(info, indent=2).encode("utf-8")
        ).decode("utf-8")

        url_info = f"https://api.github.com/repos/{repo}/contents/BITACORA_INFO.json"

        r_info = requests.get(url_info, headers=headers)
        sha_info = r_info.json().get("sha") if r_info.status_code == 200 else None

        payload_info = {
            "message": "Actualización de BITACORA_INFO.json",
            "content": contenido_info_b64,
            "branch": branch
        }

        if sha_info:
            payload_info["sha"] = sha_info

        requests.put(
            url_info,
            headers=headers,
            json=payload_info
        )

        # =================================================
        # ✅ CONFIRMACIÓN FINAL
        # =================================================
        st.success("✅ Bitácora actualizada correctamente")
        st.caption(f"🕓 Hora UTC guardada: {info['ultima_actualizacion']}")

  # =================================================
#PESTAÑA 4 SEGUIMIENTO AGENDAS
with tab4:
    # ======================================================
    # TÍTULO PRINCIPAL
    # ======================================================
    st.markdown("## 🗂️ Control agendas")

    # ======================================================
    # CARGAR BITÁCORA DESDE GITHUB
    # ======================================================
    archivo_bitacora = "BITACORA.xlsx"
    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Cache-Control": "no-cache"
    }

    url_bit = f"https://api.github.com/repos/{repo}/contents/{archivo_bitacora}"
    r = requests.get(url_bit, headers=headers)

    if r.status_code != 200:
        st.error("❌ No se pudo cargar la bitácora desde GitHub.")
        st.stop()

    buffer = io.BytesIO(base64.b64decode(r.json()["content"]))
    df = pd.read_excel(buffer, engine="openpyxl")

    # ======================================================
    # NORMALIZAR Y VALIDAR COLUMNAS
    # ======================================================
    df.columns = df.columns.str.strip().str.lower()

    columnas_req = [
        "grupo", "prioridad", "estado",
        "fecha de visita", "fecha de ejecucion",
        "inspector", "contrato", "direccion",
        "localidad", "detalle de tarea"
    ]

    for c in columnas_req:
        if c not in df.columns:
            st.error(f"❌ Falta la columna requerida: {c}")
            st.stop()

    # ======================================================
    # FILTRO FIJO DE GRUPO
    # ======================================================
    df["grupo"] = df["grupo"].astype(str).str.upper().str.strip()
    grupos_validos = ["INSP-CALDAS", "INSP-RIS"]
    df = df[df["grupo"].isin(grupos_validos)].copy()

    # ======================================================
    # FECHAS Y ALERTAS
    # ======================================================
    df["fecha de visita"] = pd.to_datetime(df["fecha de visita"], errors="coerce")
    df["fecha de ejecucion"] = pd.to_datetime(df["fecha de ejecucion"], errors="coerce")

    ahora_colombia = datetime.datetime.now(
        ZoneInfo("America/Bogota")
    ).replace(tzinfo=None)

    df["estado_alerta"] = df["fecha de visita"].apply(
        lambda x: "ALERTA" if pd.notna(x) and x <= ahora_colombia else "OK"
    )

    # ======================================================
    # COLUMNAS BASE A MOSTRAR
    # ======================================================
    columnas_base = [
        "inspector",
        "contrato",
        "direccion",
        "estado",
        "fecha de visita",
        "localidad",
        "detalle de tarea",
        "estado_alerta"
    ]

    # ======================================================
    # SUBPESTAÑAS
    # ======================================================
    t_fin, t_prox, t_pen = st.tabs(
        ["✅ Finalizadas", "⏳ Próximas", "🚨 Pendientes"]
    )

    # ======================================================
    # ✅ FINALIZADAS
    # ======================================================
    with t_fin:
        st.markdown("### ✅ Agendas finalizadas")

        # -------- Filtro Zona (checkbox estilo Tab2)
        zonas_sel = []
        with st.expander("Seleccionar Zona"):
            for z in grupos_validos:
                if st.checkbox(z, value=True, key=f"fin_zona_{z}"):
                    zonas_sel.append(z)

        # -------- Filtro Inicio de tarea
        inicios_sel = []
        with st.expander("Filtrar por inicio de la tarea"):
            for i in ["INICIO TARDE", "INICIO A TIEMPO"]:
                if st.checkbox(i, value=True, key=f"fin_inicio_{i}"):
                    inicios_sel.append(i)

        df_final = df[df["estado"].str.upper() == "FINALIZADA"].copy()

        if zonas_sel:
            df_final = df_final[df_final["grupo"].isin(zonas_sel)]

        def evaluar_inicio_tarde(row):
            if pd.isna(row["fecha de ejecucion"]) or pd.isna(row["fecha de visita"]):
                return "SIN DATO"
            limite = row["fecha de visita"] + pd.Timedelta(minutes=15)
            return "INICIO TARDE" if row["fecha de ejecucion"] > limite else "INICIO A TIEMPO"

        df_final["inicio_tarea"] = df_final.apply(evaluar_inicio_tarde, axis=1)

        if inicios_sel:
            df_final = df_final[df_final["inicio_tarea"].isin(inicios_sel)]

        columnas_fin = columnas_base[:-1] + ["inicio_tarea"]

        if df_final.empty:
            st.info("✅ No hay agendas finalizadas con esos filtros.")
        else:
            st.dataframe(
                df_final[columnas_fin].sort_values("fecha de visita"),
                use_container_width=True
            )

    # ======================================================
    # ⏳ PRÓXIMAS (NO INICIADAS)
    # ======================================================
    with t_prox:
        st.markdown("### ⏳ Agendas próximas (no iniciadas)")

        zonas_sel = []
        with st.expander("Seleccionar Zona"):
            for z in grupos_validos:
                if st.checkbox(z, value=True, key=f"prox_zona_{z}"):
                    zonas_sel.append(z)

        df_prox = df[
            (df["estado"].str.upper() == "ASIGNADA") &
            (df["fecha de ejecucion"].isna()) &
            (df["fecha de visita"] > ahora_colombia)
        ].copy()

        if zonas_sel:
            df_prox = df_prox[df_prox["grupo"].isin(zonas_sel)]

        if df_prox.empty:
            st.info("✅ No hay agendas próximas.")
        else:
            st.dataframe(
                df_prox[columnas_base].sort_values("fecha de visita"),
                use_container_width=True
            )

    # ======================================================
    # 🚨 PENDIENTES (ALERTAS REALES)
    # ======================================================
    with t_pen:
        st.markdown("### 🚨 Agendas en ALERTA")

        zonas_sel = []
        with st.expander("Seleccionar Zona"):
            for z in grupos_validos:
                if st.checkbox(z, value=True, key=f"pen_zona_{z}"):
                    zonas_sel.append(z)

        df_alerta = df[
            (df["estado"].str.upper() == "ASIGNADA") &
            (df["prioridad"].str.upper() == "ALTA") &
            (df["estado_alerta"] == "ALERTA")
        ].copy()

        if zonas_sel:
            df_alerta = df_alerta[df_alerta["grupo"].isin(zonas_sel)]

        if df_alerta.empty:
            st.info("✅ No hay agendas en ALERTA para la zona seleccionada.")
        else:
            st.dataframe(
                df_alerta[columnas_base].sort_values("fecha de visita"),
                use_container_width=True
            )
            st.error(f"🚨 TOTAL ALERTAS: {len(df_alerta)}")




with tab5:
    st.markdown("## 📌 Órdenes ASIGNADAS")

    # ---------------------------------------------------
    # VALIDAR QUE EXISTA LA BITÁCORA
    # ---------------------------------------------------
    archivo_bitacora = "BITACORA.xlsx"

    if not os.path.exists(archivo_bitacora):
        st.warning(
            "⚠️ No hay una bitácora cargada.\n"
            "Un administrador debe subir el archivo en la pestaña de Administración."
        )
        st.stop()

    # ---------------------------------------------------
    # CARGAR BITÁCORA COMPLETA
    # ---------------------------------------------------
    df_bitacora = pd.read_excel(archivo_bitacora)
    df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

    # ---------------------------------------------------
    # VALIDAR COLUMNAS NECESARIAS
    # ---------------------------------------------------
    columnas_req = ["inspector", "estado", "prioridad"]
    for col in columnas_req:
        if col not in df_bitacora.columns:
            st.error(f"❌ Falta la columna requerida: {col}")
            st.stop()

    # ---------------------------------------------------
    # FILTRAR SOLO ÓRDENES ASIGNADAS (TEXTO REAL)
    # ---------------------------------------------------
    df_asignadas = df_bitacora[
        df_bitacora["estado"]
        .astype(str)
        .str.contains("Asignad", case=False, na=False)
    ].copy()

    if df_asignadas.empty:
        st.info("✅ No hay órdenes ASIGNADAS en la bitácora.")
        st.stop()

    # ---------------------------------------------------
    # USAR PRIORIDAD TAL CUAL VIENE DEL EXCEL
    # ---------------------------------------------------
    df_asignadas["prioridad_real"] = (
        df_asignadas["prioridad"]
        .astype(str)
        .str.strip()
    )

    # ---------------------------------------------------
    # AGRUPAR POR INSPECTOR Y PRIORIDAD REAL
    # ---------------------------------------------------
    df_prio = (
        df_asignadas
        .groupby(["inspector", "prioridad_real"])
        .size()
        .reset_index(name="cantidad")
    )

    # Ordenar inspectores por total asignadas
    orden_inspectores = (
        df_prio.groupby("inspector")["cantidad"]
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    # ---------------------------------------------------
    # COLORES SEGÚN PRIORIDAD (TAL COMO PEDISTE)
    # ---------------------------------------------------
    color_prioridad = {
        "Alta": "#dc3545",        # 🔴 rojo
        "Media": "#ffc107",       # 🟡 amarillo
        "Baja": "#7cd992",        # 🟢 verde claro
        "Critica": "#fd7e14",     # 🟠 naranja
        "Prioridad": "#6f4e37"    # 🟤 café
    }

    # ---------------------------------------------------
    # GRÁFICA ACUMULADA
    # ---------------------------------------------------
    fig = px.bar(
        df_prio,
        y="inspector",
        x="cantidad",
        color="prioridad_real",
        orientation="h",
        category_orders={"inspector": orden_inspectores},
        color_discrete_map=color_prioridad,
        text="cantidad",
        title="Órdenes ASIGNADAS por inspector (prioridades reales del Excel)"
    )

    fig.update_traces(
        textposition="inside",
        textfont_size=16
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Cantidad de órdenes ASIGNADAS",
        yaxis_title="Inspector",
        legend_title="Prioridad",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
