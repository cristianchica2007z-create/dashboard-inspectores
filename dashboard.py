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
    "CHICA RAMIREZ CRISTIAN ALBERTO",
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

# ===================================================
# CARGA ÚNICA DE BITÁCORA (BASE GLOBAL)
# ===================================================
archivo_bitacora = "BITACORA.xlsx"

if not os.path.exists(archivo_bitacora):
    st.error(
        "❌ No se encontró el archivo BITACORA.xlsx.\n"
        "Debe cargarse antes de usar el dashboard."
    )
    st.stop()

df_bitacora = pd.read_excel(archivo_bitacora)
df_bitacora.columns = df_bitacora.columns.str.strip().str.lower()

# ✅ COPIA BASE INMUTABLE (NO SE FILTRA)
df_bitacora_base = df_bitacora.copy()


# ✅ CREAR PESTAÑAS
# ---------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab_inv = st.tabs([
    "📦 Inventario Papelería",
    "🕒 Seguimiento Diario",
    "📈 Subir Archivos",
     "📅 Seguimiento agendas",
    "📌 Órdenes Asignadas",
    "## 🦺 SST",
    "🏭 Inventario V2"
    

    
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
with tab2:
    st.subheader("🕒 Control Operativo e&c")
    st.subheader("Eje Cafetero")

    # ===================================================
    # USAR COPIA PARA TAB 2 (NO TOCAR LA BASE)
    # ===================================================
    df_tab2 = df_bitacora_base.copy()
    # (SIN MODIFICAR EL ARCHIVO)
    # -------------------------------------------------
    from openpyxl import load_workbook

    wb = load_workbook(archivo_bitacora, data_only=True)
    ws = wb.active

 # Encabezados normalizados (igual que en pandas)
    headers_raw = [cell.value for cell in ws[1]]
    headers = [
        str(h).strip().lower() if h is not None else ""
        for h in headers_raw
    ]

    # Buscar posiciones de columnas de forma segura
    try:
        col_inspector = headers.index("inspector") + 1
        col_fachada = headers.index("foto de fachada") + 1
        col_vp = headers.index("foto de vp") + 1
    except ValueError as e:
        st.error(
            "❌ No se encontraron columnas requeridas en el Excel.\n\n"
            f"Columnas encontradas:\n{headers_raw}"
        )
        st.stop()

    links_fotos = []

    for row in ws.iter_rows(min_row=2):
        inspector = row[col_inspector - 1].value

        cell_fachada = row[col_fachada - 1]
        cell_vp = row[col_vp - 1]

        link_fachada = (
            cell_fachada.hyperlink.target
            if cell_fachada.hyperlink else None
        )

        link_vp = (
            cell_vp.hyperlink.target
            if cell_vp.hyperlink else None
        )

        links_fotos.append({
            "inspector": inspector,
            "link_fachada": link_fachada,
            "link_vp": link_vp
        })

    df_links = pd.DataFrame(links_fotos)
    # -------------------------------------------------
    # ✅ EXCLUIR GRUPOS NO OPERATIVOS
    # -------------------------------------------------
    if "grupo" in df_bitacora.columns:
        df_bitacora["grupo"] = (
            df_bitacora["grupo"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        grupos_no_operativos = ["SST-NAL", "SUPERVISIONES", "SUSP-ANT"]

        df_bitacora = df_bitacora[
            ~df_bitacora["grupo"].isin(grupos_no_operativos)
        ]

    if df_bitacora.empty:
        st.warning(
            "⚠️ No hay datos disponibles después del filtro por GRUPO.\n"
            "Esto indica que el archivo solo contiene grupos no operativos."
        )
        st.stop()

    # -------------------------------------------------
    # FECHA Y USUARIO DE ÚLTIMA ACTUALIZACIÓN
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
        pass

    st.caption(
        f"🕓 Última actualización: {ultima_actualizacion} "
        f"| 👤 Actualizó: {usuario_actualizo}"
    )

    # -------------------------------------------------
    # FUNCIONES UTILITARIAS DE TIEMPO
    # -------------------------------------------------
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
    columnas_necesarias = [
        "fecha de ejecucion", "hora inicio", "hora final",
        "inspector", "localidad", "cierre", "tiempo de tarea"
    ]

    for col in columnas_necesarias:
        if col not in df_bitacora.columns:
            st.error(f"❌ Falta la columna requerida: {col}")
            st.stop()

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

    df_bitacora["fecha"] = pd.to_datetime(
        df_bitacora["fecha de ejecucion"], errors="coerce"
    ).dt.date

    df_bitacora["hora_inicio"] = df_bitacora["hora inicio"].apply(parse_hora)
    df_bitacora["hora_final"] = df_bitacora["hora final"].apply(parse_hora)

    df_bitacora["tiempo_tarea_td"] = (
        df_bitacora["tiempo de tarea"].apply(parse_tiempo_tarea)
    )

    df_bitacora["hora_inicio"] = df_bitacora["hora_inicio"].apply(
        lambda x: x if pd.notna(x) else "SIN HORA"
    )
# ===================================================
    # ✅ TAB 2 — PARTE 3 / 5
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
    # ✅ TAB 2 — PARTE 4 / 5
    # Agrupación diaria, puntualidad y estado
    # ===================================================

    # ---------------------------------------------------
    # AGRUPACIÓN DIARIA POR INSPECTOR (ESTABLE)
    # ---------------------------------------------------
    primeras = (
        df2.sort_values("hora_inicio")
        .groupby("inspector", as_index=False)
        .first()[["inspector", "hora_inicio", "localidad", "supervisor"]]
    )

    ultimas = (
        df2.sort_values("hora_final")
        .groupby("inspector", as_index=False)
        .last()[["inspector", "hora_final"]]
    )

    df_agrupado = primeras.merge(
        ultimas,
        on="inspector",
        how="left"
    )

    # ---------------------------------------------------
    # PUNTUALIDAD (usa SOLO la primera hora del día)
    # ---------------------------------------------------
    hora_oficial = datetime.time(7, 30)

    def mins_tarde(h):
        if h is None or pd.isna(h):
            return None
        if not isinstance(h, datetime.time):
            return None

        h1 = datetime.datetime.combine(datetime.date.today(), h)
        h2 = datetime.datetime.combine(datetime.date.today(), hora_oficial)
        return int((h1 - h2).total_seconds() / 60)

    df_agrupado["minutos_tarde"] = df_agrupado["hora_inicio"].apply(mins_tarde)

    # ---------------------------------------------------
    # ESTADO DE PUNTUALIDAD (ORIGINAL)
    # ---------------------------------------------------
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

# ===================================================
  # ===================================================
    # ✅ TAB 2 — PARTE 5 / 5
    # Estilos y tabla final
    # ===================================================

    # ---------------------------------------------------
    # 🎨 ESTILO SOLO PARA LA COLUMNA hora_inicio
    # (FORMA ESTABLE – NO SE ROMPE)
    # ---------------------------------------------------
    def color_hora_inicio(col):
        estilos = []
        for valor, estado in zip(col, df_tabla["estado"]):
            if estado == "Muy tarde":
                estilos.append("background-color: #f8d7da; color: #721c24")
            elif estado == "Tarde":
                estilos.append("background-color: #fff3cd; color: #856404")
            elif estado == "Puntual":
                estilos.append("background-color: #d4edda; color: #155724")
            else:
                estilos.append("")
        return estilos

    # ---------------------------------------------------
    # 📋 Tabla de inspecciones del día
    # ---------------------------------------------------
    st.markdown("### 📋 Tabla de inspecciones del día")

    # ---------------------------------------------------
    # 📋 Tabla de inspecciones del día (SEGURA)
    # ---------------------------------------------------
    columnas_tabla = [
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

    columnas_disponibles = [
        c for c in columnas_tabla if c in df_tabla.columns
    ]

    tabla_mostrar = df_tabla[columnas_disponibles]

    styled_tabla = (
        tabla_mostrar
        .style
        .apply(color_hora_inicio, subset=["hora_inicio"])
    )

    st.dataframe(styled_tabla, use_container_width=True)

    # ===================================================
 # 🚨 INSPECTORES SIN ACTIVIDAD EN LA FECHA
    # ===================================================
    st.markdown("### 🚨 Inspectores sin actividad registrada")

    inspectores_con_actividad = set(df2["inspector"].str.upper().str.strip().unique())

    inspectores_del_filtro = [
        insp for insp in inspectores_lista
        if supervisores_dict.get(insp.upper(), "SIN SUPERVISOR") in supervisores_sel
    ]

    inspectores_sin_actividad = [
        insp for insp in inspectores_del_filtro
        if insp.upper().strip() not in inspectores_con_actividad
    ]

    if inspectores_sin_actividad:
        df_sin_actividad = pd.DataFrame({
            "Inspector": inspectores_sin_actividad
        })
        df_sin_actividad["Supervisor"] = df_sin_actividad["Inspector"].apply(
            lambda x: supervisores_dict.get(x.upper(), "SIN SUPERVISOR")
        )
        df_sin_actividad = df_sin_actividad.sort_values("Supervisor")

        st.error(f"🚨 {len(inspectores_sin_actividad)} inspector(es) sin actividad registrada para {fecha_sel}")
        st.dataframe(df_sin_actividad, use_container_width=True)
    else:
        st.success("✅ Todos los inspectores tienen actividad registrada para esta fecha.")

    # ===================================================
    # 📊 Producción por inspector (órdenes efectivas)
  
    # ===================================================
    st.markdown("## 📊 Producción por inspector (órdenes efectivas)")

    df_prod = (
        df2[df2["efectiva"] == True]
        .groupby("inspector")
        .size()
        .reset_index(name="Órdenes efectivas")
        .sort_values("Órdenes efectivas", ascending=True)
    )

    if df_prod.empty:
        st.info("⚠️ No hay órdenes efectivas para esta fecha.")
    else:
        # Colores según producción
        def color_por_produccion(valor):
            if valor <= 3:
                return "#dc3545"      # rojo
            elif valor <= 6:
                return "#f5b7b1"      # rosado
            elif valor <= 8:
                return "#f7dc6f"      # amarillo
            else:
                return "#28a745"      # verde

        df_prod["color"] = df_prod["Órdenes efectivas"].apply(color_por_produccion)

        fig_prod = px.bar(
            df_prod,
            y="inspector",
            x="Órdenes efectivas",
            orientation="h",
            text="Órdenes efectivas",
            title="Órdenes efectivas por inspector"
        )

        # Colores y barras más gruesas
        fig_prod.update_traces(
            marker_color=df_prod["color"],
            textposition="outside",
            textfont_size=28,
            cliponaxis=False
        )

        fig_prod.update_layout(
            bargap=0.15,              # barras más gruesas
            xaxis_title="Órdenes efectivas",
            yaxis_title="Inspector",
            font=dict(size=18),
            height=650
        )

        st.plotly_chart(fig_prod, use_container_width=True)


  

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
 #    clave_ingresada = st.text_input(
  #       "Contraseña de administrador",
#         type="password",
#         placeholder="Ingresa la clave para administrar la bitácora"
#     )
# 
#     clave_real = st.secrets["admin"]["password"]

 #    if clave_ingresada != clave_real:
#         st.warning(
#             "⛔ Acceso restringido.\n\n"
#             "Solo personal autorizado puede cargar o actualizar la bitácora."
#         )
 #        st.stop()

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
    # CARGAR BITÁCORA DESDE GITHUB (FORMA CORRECTA)
    # ======================================================
    archivo_bitacora = "BITACORA.xlsx"
    token = st.secrets["github"]["token"]
    repo = st.secrets["github"]["repo"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Cache-Control": "no-cache"
    }

    url_metadata = f"https://api.github.com/repos/{repo}/contents/{archivo_bitacora}"
    r_meta = requests.get(url_metadata, headers=headers)

    if r_meta.status_code != 200:
        st.error("❌ No se pudo obtener la información del archivo desde GitHub.")
        st.stop()

    download_url = r_meta.json().get("download_url")

    if not download_url:
        st.error("❌ No se pudo obtener la URL de descarga del archivo.")
        st.stop()

    r_file = requests.get(download_url, headers=headers)

    if r_file.status_code != 200:
        st.error("❌ No se pudo descargar el archivo desde GitHub.")
        st.stop()

    buffer = io.BytesIO(r_file.content)
    df = pd.read_excel(buffer)
    df.columns = df.columns.str.strip().str.lower()


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

    # ===================================================
    # VALIDAR Y CARGAR BITÁCORA LOCAL
    # ===================================================
    archivo_bitacora = "BITACORA.xlsx"

    if not os.path.exists(archivo_bitacora):
        st.warning("⚠️ No hay una bitácora cargada.")
        st.stop()

    df = pd.read_excel(archivo_bitacora)
    df.columns = df.columns.str.strip().str.lower()

    # ===================================================
    # ✅ EXCLUIR GRUPOS NO OPERATIVOS (MISMA REGLA QUE TAB 2)
    # ===================================================
    if "grupo" in df.columns:
        df["grupo"] = (
            df["grupo"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        grupos_no_operativos = [
            "SST-NAL",
            "SUPERVISIONES",
            "SUSP-ANT"
        ]

        df = df[~df["grupo"].isin(grupos_no_operativos)]

    if df.empty:
        st.warning("⚠️ No hay datos operativos después del filtro de grupos.")
        st.stop()

    # ===================================================
    # VALIDAR COLUMNAS NECESARIAS
    # ===================================================
    columnas_requeridas = ["inspector", "estado", "prioridad", "grupo"]
    for col in columnas_requeridas:
        if col not in df.columns:
            st.error(f"❌ Falta la columna requerida: {col}")
            st.stop()

    # ===================================================
    # FILTRAR SOLO ÓRDENES ASIGNADAS
    # ===================================================
    df_asignadas = df[
        df["estado"]
        .astype(str)
        .str.contains("Asignad", case=False, na=False)
    ].copy()

    if df_asignadas.empty:
        st.info("✅ No hay órdenes ASIGNADAS en la bitácora.")
        st.stop()

    # ===================================================
    # ================= FILTROS =================
    # ===================================================
    st.markdown("### 🔎 Filtros")

    # -------- FILTRO POR GRUPO --------
    grupos_disponibles = sorted(df_asignadas["grupo"].dropna().unique())
    grupos_sel = []

    with st.expander("Seleccionar Grupo", expanded=True):
        for g in grupos_disponibles:
            if st.checkbox(g, value=True, key=f"tab5_grupo_{g}"):
                grupos_sel.append(g)

    if grupos_sel:
        df_asignadas = df_asignadas[df_asignadas["grupo"].isin(grupos_sel)]

    # -------- FILTRO POR PRIORIDAD --------
    prioridades_disponibles = sorted(df_asignadas["prioridad"].dropna().unique())
    prioridades_sel = []

    with st.expander("Seleccionar Prioridad", expanded=True):
        for p in prioridades_disponibles:
            if st.checkbox(p, value=True, key=f"tab5_prio_{p}"):
                prioridades_sel.append(p)

    if prioridades_sel:
        df_asignadas = df_asignadas[df_asignadas["prioridad"].isin(prioridades_sel)]

    if df_asignadas.empty:
        st.warning("⚠️ No hay datos con los filtros seleccionados.")
        st.stop()

    # ===================================================
    # AGRUPAR POR INSPECTOR Y PRIORIDAD (DATOS REALES)
    # ===================================================
    df_prio = (
        df_asignadas
        .groupby(["inspector", "prioridad"])
        .size()
        .reset_index(name="cantidad")
    )

    # Ordenar inspectores por carga total
    orden_inspectores = (
        df_prio.groupby("inspector")["cantidad"]
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    # ===================================================
    # MAPA DE COLORES POR PRIORIDAD
    # ===================================================
    color_prioridad = {
        "Alta": "#dc3545",        # 🔴 rojo
        "Media": "#ffc107",       # 🟡 amarillo
        "Baja": "#7cd992",        # 🟢 verde claro
        "Critica": "#fd7e14",     # 🟠 naranja
        "Prioridad": "#6f4e37",    # 🟤 café
        
        "60 Meses": "#6f42c1",        # 🟣 morado
        "Segunda visita": "#ff8c00"   # 🟠 naranja

    }

    # ===================================================
    # GRÁFICA ACUMULADA
    # ===================================================
    fig = px.bar(
        df_prio,
        y="inspector",
        x="cantidad",
        color="prioridad",
        orientation="h",
        category_orders={"inspector": orden_inspectores},
        color_discrete_map=color_prioridad,
        text="cantidad",
        title="Órdenes ASIGNADAS por inspector (según filtros)"
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


    # ===================================================
    df_sst = df_bitacora_base.copy()


with tab6:
    st.markdown("## 🦺 SST")

    # ===================================================
    # BASE SST
    # ===================================================
    df_sst = df_bitacora_base.copy()

    # Normalizar columnas base
    for col in ["inspector", "tipo de trabajo"]:
        if col in df_sst.columns:
            df_sst[col] = df_sst[col].astype(str).str.upper().str.strip()

    # ===================================================
    # ASIGNAR SUPERVISOR (MISMO MAPEO QUE TAB 2)
    # ===================================================
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
        "CHICA RAMIREZ CRISTIAN ALBERTO": "CRISTIAN CHICA",
    }.items()}

    df_sst["supervisor"] = (
        df_sst["inspector"]
        .map(supervisores_dict)
        .fillna("SIN SUPERVISOR")
    )

    # ===================================================
    # FILTRO POR SUPERVISOR (ESTILO TAB 2)
    # ===================================================
    st.markdown("### 👤 Filtro por Supervisor")

    supervisores_disp = sorted(df_sst["supervisor"].unique().tolist())
    supervisores_sel = []

    with st.expander("Seleccionar supervisores", expanded=True):
        for sup in supervisores_disp:
            if st.checkbox(sup, value=True, key=f"sst_sup_{sup}"):
                supervisores_sel.append(sup)

    if supervisores_sel:
        df_sst = df_sst[df_sst["supervisor"].isin(supervisores_sel)]

    # ===================================================
    # SUBPESTAÑAS SST
    # ===================================================
    sub_preop, sub_final, sub_aus = st.tabs(
        ["✅ PREOPERACIONAL", "🏁 OPERACIONAL FINAL", "🚫 AUSENTISMO"]
    )

    # ===================================================
    # ✅ PREOPERACIONAL – 2025 – EJE
    # ===================================================
    with sub_preop:
        st.subheader("✅ PREOPERACIONAL – 2025 – EJE")

        df_preop = df_sst[
            df_sst["tipo de trabajo"].str.contains("PREOPERACIONAL - 2025 - EJE", na=False)
        ].copy()

        df_preop["fecha_ejecucion_solo"] = pd.to_datetime(
            df_preop["fecha de ejecucion"], errors="coerce"
        ).dt.date

        if "hora inicio" in df_preop.columns:
            df_preop["hora_inicio"] = df_preop["hora inicio"]

        if "hora final" in df_preop.columns:
            df_preop["hora_final"] = df_preop["hora final"]

        if "cierre" in df_preop.columns:
            df_preop["cierre"] = df_preop["cierre"].astype(str).str.upper().str.strip()

        def estilo_preop(row):
            if pd.isna(row["hora_inicio"]):
                return ["background-color:#f8d7da"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_preop[
                ["fecha_ejecucion_solo", "inspector", "hora_inicio", "hora_final", "cierre"]
            ].style.apply(estilo_preop, axis=1),
            use_container_width=True
        )

    # ===================================================
    # 🏁 OPERACIONAL FINAL – 2025 – EJE
    # ===================================================
    with sub_final:
        st.subheader("🏁 OPERACIONAL FINAL – 2025 – EJE")

        df_final = df_sst[
            df_sst["tipo de trabajo"].str.contains("OPERACIONAL FINAL - 2025 - EJE", na=False)
        ].copy()

        df_final["fecha_ejecucion_solo"] = pd.to_datetime(
            df_final["fecha de ejecucion"], errors="coerce"
        ).dt.date

        if "hora inicio" in df_final.columns:
            df_final["hora_inicio"] = df_final["hora inicio"]

        if "hora final" in df_final.columns:
            df_final["hora_final"] = df_final["hora final"]

        if "cierre" in df_final.columns:
            df_final["cierre"] = df_final["cierre"].astype(str).str.upper().str.strip()

        df_final["estado_jornada"] = df_final["hora_final"].apply(
            lambda x: "SIN FINALIZAR JORNADA" if pd.isna(x) else "JORNADA FINALIZADA"
        )

        def estilo_final(row):
            if row["estado_jornada"] == "SIN FINALIZAR JORNADA":
                return ["background-color:#f8d7da"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_final[
                ["fecha_ejecucion_solo", "inspector", "hora_inicio", "hora_final", "estado_jornada", "cierre"]
            ].style.apply(estilo_final, axis=1),
            use_container_width=True
        )

    # ===================================================
    # ===================================================
# 🚫 AUSENTISMO – EJE
# ===================================================
with sub_aus:
    st.subheader("🚫 AUSENTISMO – EJE")

    # ---------------------------------------------
    # Filtrar AUSENTISMO
    # ---------------------------------------------
    df_aus = df_sst[
        df_sst["tipo de trabajo"].str.contains("AUSENTISMO", na=False)
    ].copy()

    # ✅ FILTRO CLAVE POR CONTRATO
    if "contrato" in df_aus.columns:
        df_aus = df_aus[
            df_aus["contrato"]
            .astype(str)
            .str.upper()
            .str.strip()
            == "OFM-2025-014, EJE"
        ]

    # ---------------------------------------------
    # Fecha solo fecha
    # ---------------------------------------------
    if "fecha de ejecucion" in df_aus.columns:
        df_aus["fecha_ejecucion_solo"] = pd.to_datetime(
            df_aus["fecha de ejecucion"], errors="coerce"
        ).dt.date

    # ---------------------------------------------
    # Normalizar horas
    # ---------------------------------------------
    if "hora inicio" in df_aus.columns:
        df_aus["hora_inicio"] = df_aus["hora inicio"]

    if "hora final" in df_aus.columns:
        df_aus["hora_final"] = df_aus["hora final"]

    # ---------------------------------------------
    # Normalizar CIERRE
    # ---------------------------------------------
    if "cierre" in df_aus.columns:
        df_aus["cierre"] = (
            df_aus["cierre"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    # ---------------------------------------------
    # ✅ Cálculo CORRECTO del tiempo (sin apply)
    # ---------------------------------------------
    df_aus["hora_inicio_dt"] = pd.to_datetime(
        df_aus["hora_inicio"], errors="coerce"
    )
    df_aus["hora_final_dt"] = pd.to_datetime(
        df_aus["hora_final"], errors="coerce"
    )

    df_aus["tiempo_ausentismo_min"] = (
        (df_aus["hora_final_dt"] - df_aus["hora_inicio_dt"])
        .dt.total_seconds() / 60
    )

    # Eliminar valores negativos o inválidos
    df_aus.loc[
        df_aus["tiempo_ausentismo_min"] < 0,
        "tiempo_ausentismo_min"
    ] = None

    # ---------------------------------------------
    # Estilo: rojo si > 60 minutos
    # ---------------------------------------------
    def estilo_aus(row):
        if (
            pd.notna(row["tiempo_ausentismo_min"])
            and row["tiempo_ausentismo_min"] > 60
        ):
            return ["background-color:#f8d7da"] * len(row)
        return [""] * len(row)

    # ---------------------------------------------
    # Mostrar tabla
    # ---------------------------------------------
    if not df_aus.empty:
        st.dataframe(
            df_aus[
                [
                    "fecha_ejecucion_solo",
                    "inspector",
                    "hora_inicio",
                    "hora_final",
                    "tiempo_ausentismo_min",
                    "cierre"
                ]
            ]
            .style
            .apply(estilo_aus, axis=1),
            use_container_width=True
        )
    else:
        st.info("No hay registros de AUSENTISMO – EJE para mostrar.")




# ===================================================
# TAB INVENTARIO E&C — Estilo corporativo rojo
# Menú lateral dinámico con submenús colapsables
# ===================================================
# INSTRUCCIONES:
# 1. En tu lista de tabs agrega tab_inv:
#    tab1, tab2, ..., tab6, tab_inv = st.tabs([..., "🏭 Inventario E&C"])
# 2. Pega este bloque completo AL FINAL de tu dashboard.py
# ===================================================

def gh_get_inv(filename, gh_headers, repo, branch="main"):
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    r = requests.get(url, headers=gh_headers)
    if r.status_code == 200:
        raw = base64.b64decode(r.json()["content"]).decode("utf-8")
        return json.loads(raw), r.json().get("sha")
    return None, None

def gh_put_inv(filename, data, gh_headers, repo, sha=None, branch="main", mensaje="Actualización"):
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    contenido = base64.b64encode(
        json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("utf-8")
    payload = {"message": mensaje, "content": contenido, "branch": branch}
    if sha:
        payload["sha"] = sha
    return requests.put(url, headers=gh_headers, json=payload)

with tab_inv:

    CATALOGO_DEFAULT = {
        "EPPs": {
            "Monogafas":  {"tallas": False},
            "Guantes":    {"tallas": False},
            "Piernera":   {"tallas": False},
            "Botas":      {"tallas": True, "opciones_talla": ["36","37","38","39","40","41","42","43","44","45","46"]},
        },
        "Dotación": {
            "Camisa":   {"tallas": True, "opciones_talla": ["XS","S","M","L","XL","XXL"]},
            "Pantalón": {"tallas": True, "opciones_talla": ["28","30","32","34","36","38","40"]},
            "Chaleco":  {"tallas": True, "opciones_talla": ["XS","S","M","L","XL","XXL"]},
        },
        "Papelería": {
            "Isométricos (paquete x200)": {"tallas": False},
            "Stickers":                   {"tallas": False},
            "Papelería general":          {"tallas": False},
        },
        "Herramientas": {
            "Cepo":           {"tallas": False},
            "Llaves de cepo": {"tallas": False},
        },
    }

    SEDES_INV       = ["CALDAS", "RISARALDA"]
    RESPONSABLES_INV = [
        "ANDRES ARROYAVE", "CRISTIAN CHICA", "DANNY DE LA CRUZ",
        "JANIER MARIN", "CAMILA (RESIDENTE)", "ANDRES CARMONA (SST)", "JENNY (DOTACIÓN)",
    ]
    CATEGORIAS = ["EPPs", "Dotación", "Papelería", "Herramientas"]
    COLORES_CAT = {"EPPs": "#c0392b", "Dotación": "#c0392b", "Papelería": "#c0392b", "Herramientas": "#c0392b"}

    inv_token   = st.secrets["github"]["token"]
    inv_repo    = st.secrets["github"]["repo"]
    inv_branch  = st.secrets["github"].get("branch", "main")
    inv_headers = {"Authorization": f"Bearer {inv_token}", "Accept": "application/vnd.github+json"}

    catalogo_raw, catalogo_sha = gh_get_inv("CATALOGO.json", inv_headers, inv_repo, inv_branch)
    catalogo = catalogo_raw if catalogo_raw is not None else CATALOGO_DEFAULT

    mov_raw, mov_sha_raw = gh_get_inv("INVENTARIO_V2.json", inv_headers, inv_repo, inv_branch)
    movimientos = mov_raw if mov_raw is not None else []

    if "inv_seccion"        not in st.session_state: st.session_state.inv_seccion        = "entrada_EPPs"
    if "inv_sede"           not in st.session_state: st.session_state.inv_sede           = SEDES_INV[0]
    if "inv_resp"           not in st.session_state: st.session_state.inv_resp           = RESPONSABLES_INV[0]
    if "inv_mov_sha"        not in st.session_state: st.session_state.inv_mov_sha        = mov_sha_raw
    if "inv_cat_sha"        not in st.session_state: st.session_state.inv_cat_sha        = catalogo_sha
    if "inv_menu_entradas"  not in st.session_state: st.session_state.inv_menu_entradas  = True
    if "inv_menu_salidas"   not in st.session_state: st.session_state.inv_menu_salidas   = False
    if "inv_menu_consultas" not in st.session_state: st.session_state.inv_menu_consultas = True
    if "inv_menu_config"    not in st.session_state: st.session_state.inv_menu_config    = True

    # ── CSS corporativo rojo ─────────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] .inv-sidebar-btn button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        text-align: left !important;
        width: 100% !important;
        justify-content: flex-start !important;
        color: rgba(255,255,255,0.6) !important;
        font-size: 11px !important;
        font-weight: 400 !important;
    }
    [data-testid="stVerticalBlock"] .inv-sidebar-btn button:hover {
        background: rgba(255,255,255,0.05) !important;
        color: #fff !important;
    }
    .inv-header-box {
        background: #fff;
        border-bottom: 1px solid #e0e0e0;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
        border-radius: 6px;
        border-left: 4px solid #c0392b;
    }
    .inv-breadcrumb { font-size: 10px; color: #999; margin-bottom: 2px; }
    .inv-page-title { font-size: 17px; font-weight: 700; color: #1a2332; text-transform: uppercase; letter-spacing: 0.03em; }
    .inv-badge { background: #c0392b; color: #fff; font-size: 10px; font-weight: 700; padding: 4px 14px; border-radius: 4px; letter-spacing: 0.05em; }
    .inv-card { background: #fff; border-radius: 6px; border: 1px solid #e0e0e0; margin-bottom: 14px; overflow: hidden; }
    .inv-card-header { padding: 9px 16px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 8px; background: #fafafa; }
    .inv-card-bar { width: 4px; height: 16px; border-radius: 2px; background: #c0392b; }
    .inv-card-title { font-size: 11px; font-weight: 700; color: #1a2332; text-transform: uppercase; letter-spacing: 0.05em; }
    .inv-card-body { padding: 14px 16px; }
    .inv-section-label {
        font-size: 9px; font-weight: 700; color: #c0392b;
        text-transform: uppercase; letter-spacing: 0.07em;
        margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
    }
    .inv-section-label::after { content: ''; flex: 1; height: 1px; background: #f0f0f0; }
    .inv-item-card {
        border: 1px solid #e8e8e8; border-radius: 6px;
        padding: 10px 12px; background: #fafafa;
    }
    .inv-item-card:hover { border-color: #c0392b; background: #fff; }
    .inv-item-name { font-size: 12px; font-weight: 600; color: #1a2332; margin-bottom: 6px; }
    .inv-talla-row { display: flex; gap: 3px; flex-wrap: wrap; margin-bottom: 6px; }
    .inv-talla-chip { font-size: 9px; font-weight: 600; padding: 2px 7px; border: 1px solid #d0d0d0; border-radius: 3px; color: #555; background: #fff; display: inline-block; }
    .inv-talla-sel { background: #c0392b !important; color: #fff !important; border-color: #c0392b !important; }
    .inv-footer { background: #fff; border-top: 1px solid #e0e0e0; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; border-radius: 0 0 6px 6px; margin-top: 4px; }
    .inv-footer-info { font-size: 11px; color: #999; }
    .sidebar-group-lbl {
        font-size: 9px; font-weight: 700; color: rgba(255,255,255,0.3);
        text-transform: uppercase; letter-spacing: 0.08em;
        padding: 10px 12px 3px; display: block;
    }
    .sidebar-nav-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 8px 12px; font-size: 12px; font-weight: 600;
        color: rgba(255,255,255,0.8); cursor: pointer;
        border-left: 3px solid transparent;
    }
    .sidebar-nav-header:hover { background: rgba(255,255,255,0.05); color: #fff; }
    .sidebar-nav-header.active { color: #fff; background: rgba(192,57,43,0.2); border-left: 3px solid #c0392b; }
    .sidebar-sub-item {
        padding: 6px 12px 6px 32px; font-size: 11px;
        color: rgba(255,255,255,0.5); cursor: pointer;
        border-left: 3px solid transparent; display: flex; align-items: center; gap: 5px;
    }
    .sidebar-sub-item:hover { color: rgba(255,255,255,0.85); background: rgba(255,255,255,0.04); }
    .sidebar-sub-item.active { color: #fff; background: rgba(192,57,43,0.25); border-left: 3px solid #c0392b; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    # ── Layout: sidebar + contenido ──────────────────────────────────────
    col_side, col_main = st.columns([1, 3.8], gap="small")

    # ════════════════════════════════════════════════════════════════════
    # SIDEBAR dinámico
    # ════════════════════════════════════════════════════════════════════
    with col_side:
        st.markdown("""
        <div style="background:#1a2332;border-radius:8px;padding:14px 12px 8px;margin-bottom:0;">
            <div style="font-size:13px;font-weight:700;color:#fff;line-height:1.4;">E&C INGENIERÍA</div>
            <div style="font-size:10px;color:#c0392b;font-weight:700;letter-spacing:0.05em;margin-top:2px;">INVENTARIO</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div style="background:#1a2332;border-radius:0 0 8px 8px;padding:6px 0 10px;">', unsafe_allow_html=True)

            # ── ENTRADAS
            st.markdown('<span class="sidebar-group-lbl">MOVIMIENTOS</span>', unsafe_allow_html=True)
            ent_open = st.session_state.inv_menu_entradas
            ent_active = st.session_state.inv_seccion.startswith("entrada_")
            if st.button(
                f"{'▾' if ent_open else '▸'}  ↓  Entradas",
                key="toggle_entradas",
                use_container_width=True,
            ):
                st.session_state.inv_menu_entradas = not st.session_state.inv_menu_entradas
                st.rerun()

            if st.session_state.inv_menu_entradas:
                for cat in CATEGORIAS:
                    key = f"entrada_{cat}"
                    activo = st.session_state.inv_seccion == key
                    label = f"{'●' if activo else '·'}  {cat}"
                    if st.button(label, key=f"nav_{key}", use_container_width=True):
                        st.session_state.inv_seccion = key
                        st.rerun()

            # ── SALIDAS
            sal_open = st.session_state.inv_menu_salidas
            if st.button(
                f"{'▾' if sal_open else '▸'}  ↑  Salidas",
                key="toggle_salidas",
                use_container_width=True,
            ):
                st.session_state.inv_menu_salidas = not st.session_state.inv_menu_salidas
                st.rerun()

            if st.session_state.inv_menu_salidas:
                for cat in CATEGORIAS:
                    key = f"salida_{cat}"
                    activo = st.session_state.inv_seccion == key
                    label = f"{'●' if activo else '·'}  {cat}"
                    if st.button(label, key=f"nav_{key}", use_container_width=True):
                        st.session_state.inv_seccion = key
                        st.rerun()

            # ── CONSULTAS
            st.markdown('<span class="sidebar-group-lbl">CONSULTAS</span>', unsafe_allow_html=True)
            cons_open = st.session_state.inv_menu_consultas
            if st.button(
                f"{'▾' if cons_open else '▸'}  Consultas",
                key="toggle_consultas",
                use_container_width=True,
            ):
                st.session_state.inv_menu_consultas = not st.session_state.inv_menu_consultas
                st.rerun()

            if st.session_state.inv_menu_consultas:
                for label, key in [("·  Stock actual", "stock"), ("·  Historial", "historial")]:
                    activo = st.session_state.inv_seccion == key
                    btn_label = label.replace("·", "●") if activo else label
                    if st.button(btn_label, key=f"nav_{key}", use_container_width=True):
                        st.session_state.inv_seccion = key
                        st.rerun()

            # ── CONFIGURACIÓN
            st.markdown('<span class="sidebar-group-lbl">CONFIGURACIÓN</span>', unsafe_allow_html=True)
            cfg_open = st.session_state.inv_menu_config
            if st.button(
                f"{'▾' if cfg_open else '▸'}  Configuración",
                key="toggle_config",
                use_container_width=True,
            ):
                st.session_state.inv_menu_config = not st.session_state.inv_menu_config
                st.rerun()

            if st.session_state.inv_menu_config:
                activo = st.session_state.inv_seccion == "catalogo"
                if st.button("●  Catálogo" if activo else "·  Catálogo", key="nav_catalogo", use_container_width=True):
                    st.session_state.inv_seccion = "catalogo"
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # CONTENIDO PRINCIPAL
    # ════════════════════════════════════════════════════════════════════
    with col_main:
        seccion  = st.session_state.inv_seccion
        es_mov   = seccion.startswith("entrada_") or seccion.startswith("salida_")
        tipo_mov = "ENTRADA" if seccion.startswith("entrada_") else "SALIDA"
        cat_activa = seccion.split("_", 1)[1] if "_" in seccion and es_mov else ""

        # ── ENTRADAS y SALIDAS
        if es_mov:
            seccion_label = "Entradas" if tipo_mov == "ENTRADA" else "Salidas"
            st.markdown(f"""
            <div class="inv-header-box">
                <div>
                    <div class="inv-breadcrumb">Inventario E&C / {seccion_label}</div>
                    <div class="inv-page-title">{seccion_label} — {cat_activa}</div>
                </div>
                <span class="inv-badge">{st.session_state.inv_sede}</span>
            </div>
            """, unsafe_allow_html=True)

            # Tarjeta info general
            st.markdown('<div class="inv-card"><div class="inv-card-header"><div class="inv-card-bar"></div><div class="inv-card-title">Información general</div></div><div class="inv-card-body">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            st.session_state.inv_sede = c1.selectbox("Sede", SEDES_INV, key=f"sede_{seccion}", index=SEDES_INV.index(st.session_state.inv_sede))
            st.session_state.inv_resp = c2.selectbox("Responsable", RESPONSABLES_INV, key=f"resp_{seccion}", index=RESPONSABLES_INV.index(st.session_state.inv_resp))
            fecha_mov = c3.date_input("Fecha", key=f"fecha_{seccion}")
            if tipo_mov == "SALIDA":
                inspector_sel = st.selectbox("Inspector", inspectores_lista, key=f"insp_{seccion}")
            obs_mov = st.text_input("Observación (opcional)", key=f"obs_{seccion}", placeholder="Ej: Pedido mensual")
            st.markdown('</div></div>', unsafe_allow_html=True)

            # Tarjeta ítems
            items_cat = catalogo.get(cat_activa, {})
            sin_talla = {k: v for k, v in items_cat.items() if not v["tallas"]}
            con_talla = {k: v for k, v in items_cat.items() if v["tallas"]}
            cantidades = {}
            tallas_sel = {}

            st.markdown(f'<div class="inv-card"><div class="inv-card-header"><div class="inv-card-bar"></div><div class="inv-card-title">{cat_activa}</div></div><div class="inv-card-body">', unsafe_allow_html=True)

            if sin_talla:
                st.markdown('<div class="inv-section-label">Sin talla</div>', unsafe_allow_html=True)
                cols_st = st.columns(min(len(sin_talla), 3))
                for idx, (item, _) in enumerate(sin_talla.items()):
                    with cols_st[idx % 3]:
                        st.markdown(f'<div class="inv-item-card"><div class="inv-item-name">{item}</div>', unsafe_allow_html=True)
                        cantidades[item] = st.number_input("Cantidad", min_value=0, step=1, key=f"{seccion}_{item}", label_visibility="collapsed")
                        st.markdown('</div>', unsafe_allow_html=True)

            if con_talla:
                st.markdown('<div class="inv-section-label" style="margin-top:12px;">Con talla</div>', unsafe_allow_html=True)
                for item, cfg in con_talla.items():
                    st.markdown(f'<div class="inv-item-card" style="margin-bottom:8px;"><div class="inv-item-name">{item}</div>', unsafe_allow_html=True)
                    ca, cb = st.columns([2, 1])
                    tallas_sel[item] = ca.selectbox(f"Talla", cfg["opciones_talla"], key=f"{seccion}_talla_{item}", label_visibility="visible")
                    cantidades[item] = cb.number_input("Cantidad", min_value=0, step=1, key=f"{seccion}_qty_{item}", label_visibility="visible")
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div></div>', unsafe_allow_html=True)

            # Footer con botón
            items_a_guardar = [
                {"categoria": cat_activa, "item": item, "talla": tallas_sel.get(item), "cantidad": int(cant)}
                for item, cant in cantidades.items() if cant > 0
            ]
            resumen = f"{len(items_a_guardar)} ítem(s) seleccionado(s)" if items_a_guardar else "Ningún ítem seleccionado"

            col_info, col_btn_c, col_btn_g = st.columns([3, 1, 1])
            col_info.caption(resumen)
            if col_btn_g.button(
                f"✅ Registrar {'entrada' if tipo_mov=='ENTRADA' else 'salida'}",
                key=f"btn_{seccion}",
                use_container_width=True,
                type="primary",
            ):
                if not items_a_guardar:
                    st.warning("⚠️ Debes ingresar al menos un ítem con cantidad mayor a 0.")
                else:
                    errores = []
                    if tipo_mov == "SALIDA":
                        for it in items_a_guardar:
                            ent = sum(m["cantidad"] for m in movimientos if m["tipo"]=="ENTRADA" and m["sede"]==st.session_state.inv_sede and m["categoria"]==it["categoria"] and m["item"]==it["item"] and m["talla"]==it["talla"])
                            sal = sum(m["cantidad"] for m in movimientos if m["tipo"]=="SALIDA" and m["sede"]==st.session_state.inv_sede and m["categoria"]==it["categoria"] and m["item"]==it["item"] and m["talla"]==it["talla"])
                            if it["cantidad"] > (ent - sal):
                                nombre = it["item"] + (f" T{it['talla']}" if it["talla"] else "")
                                errores.append(f"❌ **{nombre}**: disponible {ent-sal}, solicitado {it['cantidad']}")
                    if errores:
                        st.error("Stock insuficiente:")
                        for e in errores: st.markdown(e)
                    else:
                        ts = datetime.datetime.now(TZ_CO).strftime("%Y-%m-%d %H:%M:%S")
                        for it in items_a_guardar:
                            movimientos.append({
                                "tipo": tipo_mov, "fecha": str(fecha_mov), "timestamp": ts,
                                "sede": st.session_state.inv_sede, "responsable": st.session_state.inv_resp,
                                "categoria": it["categoria"], "item": it["item"], "talla": it["talla"],
                                "cantidad": it["cantidad"], "observacion": obs_mov,
                                "inspector": inspector_sel if tipo_mov=="SALIDA" else None,
                            })
                        r = gh_put_inv("INVENTARIO_V2.json", movimientos, inv_headers, inv_repo, sha=st.session_state.inv_mov_sha, branch=inv_branch, mensaje=f"{tipo_mov} {cat_activa}")
                        if r.status_code in (200, 201):
                            st.session_state.inv_mov_sha = r.json().get("content", {}).get("sha")
                            st.success(f"✅ {tipo_mov.capitalize()} registrada — {len(items_a_guardar)} ítem(s)")
                        else:
                            st.error("❌ Error al guardar en GitHub")

        # ════════════════════════════════════════════════════════════════
        # STOCK ACTUAL
        # ════════════════════════════════════════════════════════════════
        elif seccion == "stock":
            st.markdown("""
            <div class="inv-header-box">
                <div>
                    <div class="inv-breadcrumb">Inventario E&C / Consultas</div>
                    <div class="inv-page-title">Stock Actual</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            sede_st = st.selectbox("Sede", SEDES_INV, key="stock_sede")

            if not movimientos:
                st.info("📭 No hay movimientos registrados aún.")
            else:
                stock_dict = {}
                for m in movimientos:
                    if m["sede"] != sede_st: continue
                    k = (m["categoria"], m["item"], m["talla"])
                    stock_dict.setdefault(k, {"entradas": 0, "salidas": 0})
                    if m["tipo"] == "ENTRADA": stock_dict[k]["entradas"] += m["cantidad"]
                    elif m["tipo"] == "SALIDA": stock_dict[k]["salidas"] += m["cantidad"]

                if not stock_dict:
                    st.info(f"📭 No hay movimientos para {sede_st}.")
                else:
                    filas = [{"Categoría": cat, "Ítem": item + (f" (T{talla})" if talla else ""), "Entradas": v["entradas"], "Salidas": v["salidas"], "Stock actual": v["entradas"]-v["salidas"]} for (cat, item, talla), v in stock_dict.items()]
                    df_st = pd.DataFrame(filas).sort_values(["Categoría", "Ítem"])

                    def color_stock(row):
                        if row["Stock actual"] == 0: return ["background-color:#f8d7da;color:#721c24"]*len(row)
                        elif row["Stock actual"] <= 3: return ["background-color:#fff3cd;color:#856404"]*len(row)
                        return [""]*len(row)

                    st.dataframe(df_st.style.apply(color_stock, axis=1), use_container_width=True, hide_index=True)

                    sin_st   = df_st[df_st["Stock actual"] == 0]
                    bajo_st  = df_st[(df_st["Stock actual"] > 0) & (df_st["Stock actual"] <= 3)]
                    if not sin_st.empty:  st.error(f"🚨 {len(sin_st)} ítem(s) SIN STOCK en {sede_st}")
                    if not bajo_st.empty: st.warning(f"⚠️ {len(bajo_st)} ítem(s) con stock BAJO (≤ 3) en {sede_st}")

                    df_cat = df_st.groupby("Categoría")["Stock actual"].sum().reset_index()
                    fig_st = px.bar(df_cat, x="Categoría", y="Stock actual", color="Categoría",
                                    text="Stock actual", title=f"Stock por categoría — {sede_st}",
                                    color_discrete_sequence=["#c0392b"])
                    fig_st.update_traces(textposition="outside")
                    fig_st.update_layout(showlegend=False, height=320, margin=dict(t=40,b=0))
                    st.plotly_chart(fig_st, use_container_width=True)

        # ════════════════════════════════════════════════════════════════
        # HISTORIAL
        # ════════════════════════════════════════════════════════════════
        elif seccion == "historial":
            st.markdown("""
            <div class="inv-header-box">
                <div>
                    <div class="inv-breadcrumb">Inventario E&C / Consultas</div>
                    <div class="inv-page-title">Historial de Movimientos</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if not movimientos:
                st.info("📭 No hay movimientos registrados aún.")
            else:
                df_h = pd.DataFrame(movimientos)
                c1, c2, c3 = st.columns(3)
                sede_h = c1.selectbox("Sede",      ["TODAS"] + SEDES_INV,            key="h_sede")
                tipo_h = c2.selectbox("Tipo",      ["TODOS","ENTRADA","SALIDA"],      key="h_tipo")
                cat_h  = c3.selectbox("Categoría", ["TODAS"] + CATEGORIAS,           key="h_cat")

                if sede_h != "TODAS":  df_h = df_h[df_h["sede"] == sede_h]
                if tipo_h != "TODOS":  df_h = df_h[df_h["tipo"] == tipo_h]
                if cat_h  != "TODAS":  df_h = df_h[df_h["categoria"] == cat_h]

                df_h["talla"]     = df_h["talla"].fillna("—")
                df_h["inspector"] = df_h["inspector"].fillna("—")
                cols_h = ["fecha","tipo","sede","categoria","item","talla","cantidad","inspector","responsable","observacion"]
                cols_d = [c for c in cols_h if c in df_h.columns]

                def color_tipo_h(row):
                    if row["tipo"] == "ENTRADA": return ["background-color:#d4edda;color:#155724"]*len(row)
                    return ["background-color:#f8d7da;color:#721c24"]*len(row)

                st.dataframe(df_h[cols_d].sort_values("fecha", ascending=False).style.apply(color_tipo_h, axis=1), use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(df_h)} movimiento(s)")

        # ════════════════════════════════════════════════════════════════
        # CATÁLOGO
        # ════════════════════════════════════════════════════════════════
        elif seccion == "catalogo":
            st.markdown("""
            <div class="inv-header-box">
                <div>
                    <div class="inv-breadcrumb">Inventario E&C / Configuración</div>
                    <div class="inv-page-title">Catálogo de Ítems</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for cat, items in catalogo.items():
                with st.expander(f"**{cat}** — {len(items)} ítem(s)"):
                    for item, cfg in items.items():
                        if cfg["tallas"]:
                            st.markdown(f"- **{item}** | Tallas: {', '.join(cfg.get('opciones_talla', []))}")
                        else:
                            st.markdown(f"- **{item}** | Sin tallas")

            st.divider()
            st.markdown("#### ➕ Agregar nuevo ítem")
            with st.form("form_nuevo_item_v3", clear_on_submit=True):
                c1, c2 = st.columns(2)
                cat_n    = c1.selectbox("Categoría", CATEGORIAS)
                nombre_n = c2.text_input("Nombre del ítem")
                usa_t    = st.checkbox("¿Maneja tallas?")
                tallas_t = st.text_input("Tallas separadas por coma (ej: S,M,L)", disabled=not usa_t)
                if st.form_submit_button("➕ Agregar ítem", type="primary"):
                    if not nombre_n.strip():
                        st.warning("⚠️ Ingresa un nombre.")
                    elif nombre_n.strip() in catalogo[cat_n]:
                        st.warning("⚠️ Ya existe ese ítem.")
                    else:
                        nuevo = {"tallas": usa_t}
                        if usa_t and tallas_t.strip():
                            nuevo["opciones_talla"] = [t.strip() for t in tallas_t.split(",") if t.strip()]
                        catalogo[cat_n][nombre_n.strip()] = nuevo
                        r = gh_put_inv("CATALOGO.json", catalogo, inv_headers, inv_repo, sha=st.session_state.inv_cat_sha, branch=inv_branch, mensaje=f"Nuevo ítem: {nombre_n}")
                        if r.status_code in (200, 201):
                            st.session_state.inv_cat_sha = r.json().get("content", {}).get("sha")
                            st.success(f"✅ Ítem '{nombre_n}' agregado a {cat_n}")
                        else:
                            st.error("❌ Error al guardar en GitHub")

            st.divider()
            st.markdown("#### 📐 Agregar talla a ítem existente")
            items_t = [(c, i) for c, its in catalogo.items() for i, cfg in its.items() if cfg["tallas"]]
            if items_t:
                with st.form("form_nueva_talla_v3", clear_on_submit=True):
                    opciones = [f"{c} → {i}" for c, i in items_t]
                    sel_str  = st.selectbox("Ítem", opciones)
                    t_nueva  = st.text_input("Nueva talla")
                    if st.form_submit_button("➕ Agregar talla", type="primary"):
                        if not t_nueva.strip():
                            st.warning("⚠️ Ingresa una talla.")
                        else:
                            idx = opciones.index(sel_str)
                            cs, its2 = items_t[idx]
                            if t_nueva.strip() in catalogo[cs][its2].get("opciones_talla", []):
                                st.warning("⚠️ Esa talla ya existe.")
                            else:
                                catalogo[cs][its2]["opciones_talla"].append(t_nueva.strip())
                                r = gh_put_inv("CATALOGO.json", catalogo, inv_headers, inv_repo, sha=st.session_state.inv_cat_sha, branch=inv_branch, mensaje=f"Nueva talla {t_nueva} en {its2}")
                                if r.status_code in (200, 201):
                                    st.session_state.inv_cat_sha = r.json().get("content", {}).get("sha")
                                    st.success(f"✅ Talla '{t_nueva}' agregada")
                                else:
                                    st.error("❌ Error al guardar en GitHub")
