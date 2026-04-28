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
# ✅ TAB - INVENTARIO NUEVO (REEMPLAZA TAB 1)


with tab_inv:
    
    # ✅ TAB - INVENTARIO NUEVO (REEMPLAZA TAB 1)
    # Categorías: EPPs, Dotación (con tallas), Papelería, Herramientas
    # Lógica: Entradas / Salidas / Stock actual / Historial
    
    # ===================================================
    # HELPERS GITHUB
    # ===================================================
    
    def gh_get(filename, headers, repo, branch="main"):
    """Lee un archivo JSON desde GitHub. Retorna (data, sha)."""
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
    raw = base64.b64decode(r.json()["content"]).decode("utf-8")
    return json.loads(raw), r.json().get("sha")
    return None, None
    
    
    def gh_put(filename, data, headers, repo, sha=None, branch="main", mensaje="Actualización"):
    """Guarda un archivo JSON en GitHub."""
    url = f"https://api.github.com/repos/{repo}/contents/{filename}"
    contenido = base64.b64encode(
    json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("utf-8")
    payload = {"message": mensaje, "content": contenido, "branch": branch}
    if sha:
    payload["sha"] = sha
    return requests.put(url, headers=headers, json=payload)
    
    
    # ===================================================
    # CATÁLOGO POR DEFECTO
    # ===================================================
    
    CATALOGO_DEFAULT = {
    "EPPs": {
    "Monogafas":  {"tallas": False},
    "Guantes":    {"tallas": False},
    "Piernera":   {"tallas": False},
    "Botas":      {"tallas": True,  "opciones_talla": ["36","37","38","39","40","41","42","43","44","45","46"]},
    },
    "Dotación": {
    "Camisa":     {"tallas": True,  "opciones_talla": ["XS","S","M","L","XL","XXL"]},
    "Pantalón":   {"tallas": True,  "opciones_talla": ["28","30","32","34","36","38","40"]},
    "Chaleco":    {"tallas": True,  "opciones_talla": ["XS","S","M","L","XL","XXL"]},
    },
    "Papelería": {
    "Isométricos (paquete x200)": {"tallas": False},
    "Stickers":                   {"tallas": False},
    "Papelería general":          {"tallas": False},
    },
    "Herramientas": {
    "Cepo":         {"tallas": False},
    "Llaves de cepo": {"tallas": False},
    },
    }
    
    SEDES = ["CALDAS", "RISARALDA"]
    
    RESPONSABLES = [
    "ANDRES ARROYAVE",
    "CRISTIAN CHICA",
    "DANNY DE LA CRUZ",
    "JANIER MARIN",
    "CAMILA (RESIDENTE)",
    "ANDRES CARMONA (SST)",
    "JENNY (DOTACIÓN)",
    ]
    
    TZ_CO = ZoneInfo("America/Bogota")
    
    
    # ===================================================
    # INICIO DEL TAB
    # ===================================================
    
    st.markdown("## 🏭 Inventario E&C")
    
    # Credenciales GitHub
    token  = st.secrets["github"]["token"]
    repo   = st.secrets["github"]["repo"]
    branch = st.secrets["github"].get("branch", "main")
    
    gh_headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    }
    
    # -------------------------------------------------
    # CARGAR CATÁLOGO
    # -------------------------------------------------
    catalogo_raw, catalogo_sha = gh_get("CATALOGO.json", gh_headers, repo, branch)
    if catalogo_raw is None:
    catalogo = CATALOGO_DEFAULT
    catalogo_sha = None
    else:
    catalogo = catalogo_raw
    
    # -------------------------------------------------
    # CARGAR MOVIMIENTOS
    # -------------------------------------------------
    movimientos_raw, mov_sha = gh_get("INVENTARIO_V2.json", gh_headers, repo, branch)
    if movimientos_raw is None:
    movimientos = []
    mov_sha = None
    else:
    movimientos = movimientos_raw
    
    
    # ===================================================
    # SUBPESTAÑAS
    # ===================================================
    sub_entradas, sub_salidas, sub_stock, sub_historial, sub_catalogo = st.tabs([
    "📥 Entradas",
    "📤 Salidas",
    "📊 Stock Actual",
    "📋 Historial",
    "⚙️ Catálogo",
    ])
    
    
    # ===================================================
    # 📥 ENTRADAS
    # ===================================================
    with sub_entradas:
    st.markdown("### 📥 Registrar entrada de mercancía")
    st.info("Usa este formulario cuando llegue mercancía nueva a la sede.")
    
    with st.form("form_entrada", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    sede_e      = col1.selectbox("Sede", SEDES, key="sede_entrada")
    resp_e      = col2.selectbox("Responsable", RESPONSABLES, key="resp_entrada")
    fecha_e     = col3.date_input("Fecha", key="fecha_entrada")
    obs_e       = st.text_input("Observación (opcional)", key="obs_entrada")
    
    st.markdown("#### Ítems recibidos")
    
    items_entrada = []
    for cat, items in catalogo.items():
        st.markdown(f"**{cat}**")
        cols_cat = st.columns(3)
        for idx, (item, cfg) in enumerate(items.items()):
            col = cols_cat[idx % 3]
            with col:
                cantidad_e = st.number_input(
                    item, min_value=0, step=1, key=f"ent_{cat}_{item}"
                )
                if cfg["tallas"]:
                    talla_e = st.selectbox(
                        f"Talla ({item})",
                        cfg["opciones_talla"],
                        key=f"ent_talla_{cat}_{item}"
                    )
                else:
                    talla_e = None
    
                if cantidad_e > 0:
                    items_entrada.append({
                        "categoria": cat,
                        "item": item,
                        "talla": talla_e,
                        "cantidad": int(cantidad_e),
                    })
    
    submitted_e = st.form_submit_button("✅ Registrar entrada", use_container_width=True)
    
    if submitted_e:
    if not items_entrada:
        st.warning("⚠️ Debes ingresar al menos un ítem con cantidad mayor a 0.")
    else:
        ts = datetime.datetime.now(TZ_CO).strftime("%Y-%m-%d %H:%M:%S")
        for it in items_entrada:
            movimientos.append({
                "tipo":        "ENTRADA",
                "fecha":       str(fecha_e),
                "timestamp":   ts,
                "sede":        sede_e,
                "responsable": resp_e,
                "categoria":   it["categoria"],
                "item":        it["item"],
                "talla":       it["talla"],
                "cantidad":    it["cantidad"],
                "observacion": obs_e,
                "inspector":   None,
            })
    
        r_put = gh_put(
            "INVENTARIO_V2.json", movimientos,
            gh_headers, repo, sha=mov_sha, branch=branch,
            mensaje="Entrada de inventario"
        )
        if r_put.status_code in (200, 201):
            st.success(f"✅ Entrada registrada correctamente ({len(items_entrada)} ítem(s))")
            mov_sha = r_put.json().get("content", {}).get("sha", mov_sha)
        else:
            st.error("❌ Error al guardar en GitHub")
            st.json(r_put.json())
    
    
    # ===================================================
    # 📤 SALIDAS
    # ===================================================
    with sub_salidas:
    st.markdown("### 📤 Registrar entrega a inspector")
    st.info("Usa este formulario cuando entregues ítems a un inspector.")
    
    with st.form("form_salida", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    sede_s      = col1.selectbox("Sede", SEDES, key="sede_salida")
    resp_s      = col2.selectbox("Responsable", RESPONSABLES, key="resp_salida")
    fecha_s     = col3.date_input("Fecha", key="fecha_salida")
    
    inspector_s = st.selectbox("Inspector", inspectores_lista, key="insp_salida")
    obs_s       = st.text_input("Observación (opcional)", key="obs_salida")
    
    st.markdown("#### Ítems entregados")
    
    items_salida = []
    for cat, items in catalogo.items():
        st.markdown(f"**{cat}**")
        cols_cat = st.columns(3)
        for idx, (item, cfg) in enumerate(items.items()):
            col = cols_cat[idx % 3]
            with col:
                cantidad_s = st.number_input(
                    item, min_value=0, step=1, key=f"sal_{cat}_{item}"
                )
                if cfg["tallas"]:
                    talla_s = st.selectbox(
                        f"Talla ({item})",
                        cfg["opciones_talla"],
                        key=f"sal_talla_{cat}_{item}"
                    )
                else:
                    talla_s = None
    
                if cantidad_s > 0:
                    items_salida.append({
                        "categoria": cat,
                        "item":      item,
                        "talla":     talla_s,
                        "cantidad":  int(cantidad_s),
                    })
    
    submitted_s = st.form_submit_button("✅ Registrar salida", use_container_width=True)
    
    if submitted_s:
    if not items_salida:
        st.warning("⚠️ Debes ingresar al menos un ítem con cantidad mayor a 0.")
    else:
        # Verificar stock suficiente
        errores_stock = []
        for it in items_salida:
            key_item = (sede_s, it["categoria"], it["item"], it["talla"])
            total_ent = sum(
                m["cantidad"] for m in movimientos
                if m["tipo"] == "ENTRADA"
                and m["sede"] == sede_s
                and m["categoria"] == it["categoria"]
                and m["item"] == it["item"]
                and m["talla"] == it["talla"]
            )
            total_sal = sum(
                m["cantidad"] for m in movimientos
                if m["tipo"] == "SALIDA"
                and m["sede"] == sede_s
                and m["categoria"] == it["categoria"]
                and m["item"] == it["item"]
                and m["talla"] == it["talla"]
            )
            stock_disp = total_ent - total_sal
            if it["cantidad"] > stock_disp:
                nombre_item = f"{it['item']}" + (f" T{it['talla']}" if it["talla"] else "")
                errores_stock.append(
                    f"❌ **{nombre_item}**: stock disponible {stock_disp}, solicitado {it['cantidad']}"
                )
    
        if errores_stock:
            st.error("⚠️ Stock insuficiente para los siguientes ítems:")
            for e in errores_stock:
                st.markdown(e)
        else:
            ts = datetime.datetime.now(TZ_CO).strftime("%Y-%m-%d %H:%M:%S")
            for it in items_salida:
                movimientos.append({
                    "tipo":        "SALIDA",
                    "fecha":       str(fecha_s),
                    "timestamp":   ts,
                    "sede":        sede_s,
                    "responsable": resp_s,
                    "categoria":   it["categoria"],
                    "item":        it["item"],
                    "talla":       it["talla"],
                    "cantidad":    it["cantidad"],
                    "observacion": obs_s,
                    "inspector":   inspector_s,
                })
    
            r_put = gh_put(
                "INVENTARIO_V2.json", movimientos,
                gh_headers, repo, sha=mov_sha, branch=branch,
                mensaje="Salida de inventario"
            )
            if r_put.status_code in (200, 201):
                st.success(f"✅ Salida registrada correctamente ({len(items_salida)} ítem(s))")
                mov_sha = r_put.json().get("content", {}).get("sha", mov_sha)
            else:
                st.error("❌ Error al guardar en GitHub")
    
    
    # ===================================================
    # 📊 STOCK ACTUAL
    # ===================================================
    with sub_stock:
    st.markdown("### 📊 Stock actual por sede")
    
    if not movimientos:
    st.info("📭 Aún no hay movimientos registrados. Comienza registrando una entrada.")
    else:
    sede_stock = st.selectbox("Selecciona sede", SEDES, key="sede_stock")
    
    # Calcular stock
    stock_dict = {}
    for m in movimientos:
        if m["sede"] != sede_stock:
            continue
        key = (m["categoria"], m["item"], m["talla"])
        if key not in stock_dict:
            stock_dict[key] = {"entradas": 0, "salidas": 0}
        if m["tipo"] == "ENTRADA":
            stock_dict[key]["entradas"] += m["cantidad"]
        elif m["tipo"] == "SALIDA":
            stock_dict[key]["salidas"] += m["cantidad"]
    
    if not stock_dict:
        st.info(f"📭 No hay movimientos para la sede {sede_stock}.")
    else:
        filas = []
        for (cat, item, talla), vals in stock_dict.items():
            stock_actual = vals["entradas"] - vals["salidas"]
            nombre_item = item + (f" (T{talla})" if talla else "")
            filas.append({
                "Categoría":   cat,
                "Ítem":        nombre_item,
                "Entradas":    vals["entradas"],
                "Salidas":     vals["salidas"],
                "Stock actual": stock_actual,
            })
    
        df_stock = pd.DataFrame(filas).sort_values(["Categoría", "Ítem"])
    
        # Estilo: rojo si stock = 0, amarillo si stock <= 3
        def color_stock(row):
            if row["Stock actual"] == 0:
                return ["background-color:#f8d7da; color:#721c24"] * len(row)
            elif row["Stock actual"] <= 3:
                return ["background-color:#fff3cd; color:#856404"] * len(row)
            return [""] * len(row)
    
        st.dataframe(
            df_stock.style.apply(color_stock, axis=1),
            use_container_width=True,
            hide_index=True
        )
    
        # Alertas
        sin_stock = df_stock[df_stock["Stock actual"] == 0]
        stock_bajo = df_stock[(df_stock["Stock actual"] > 0) & (df_stock["Stock actual"] <= 3)]
    
        if not sin_stock.empty:
            st.error(f"🚨 {len(sin_stock)} ítem(s) SIN STOCK en {sede_stock}")
        if not stock_bajo.empty:
            st.warning(f"⚠️ {len(stock_bajo)} ítem(s) con stock BAJO (≤ 3) en {sede_stock}")
    
        # Gráfica por categoría
        st.markdown("#### 📊 Stock por categoría")
        df_cat = df_stock.groupby("Categoría")["Stock actual"].sum().reset_index()
        fig_stock = px.bar(
            df_cat,
            x="Categoría",
            y="Stock actual",
            color="Categoría",
            text="Stock actual",
            title=f"Stock total por categoría — {sede_stock}"
        )
        fig_stock.update_traces(textposition="outside")
        fig_stock.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_stock, use_container_width=True)
    
    
    # ===================================================
    # 📋 HISTORIAL
    # ===================================================
    with sub_historial:
    st.markdown("### 📋 Historial de movimientos")
    
    if not movimientos:
    st.info("📭 Aún no hay movimientos registrados.")
    else:
    df_hist = pd.DataFrame(movimientos)
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    sede_h  = col1.selectbox("Sede", ["TODAS"] + SEDES, key="hist_sede")
    tipo_h  = col2.selectbox("Tipo", ["TODOS", "ENTRADA", "SALIDA"], key="hist_tipo")
    cat_h   = col3.selectbox(
        "Categoría",
        ["TODAS"] + list(catalogo.keys()),
        key="hist_cat"
    )
    
    if sede_h != "TODAS":
        df_hist = df_hist[df_hist["sede"] == sede_h]
    if tipo_h != "TODOS":
        df_hist = df_hist[df_hist["tipo"] == tipo_h]
    if cat_h != "TODAS":
        df_hist = df_hist[df_hist["categoria"] == cat_h]
    
    df_hist["talla"] = df_hist["talla"].fillna("—")
    df_hist["inspector"] = df_hist["inspector"].fillna("—")
    
    columnas_hist = [
        "fecha", "tipo", "sede", "categoria",
        "item", "talla", "cantidad",
        "inspector", "responsable", "observacion"
    ]
    columnas_disp = [c for c in columnas_hist if c in df_hist.columns]
    
    def color_tipo(row):
        if row["tipo"] == "ENTRADA":
            return ["background-color:#d4edda; color:#155724"] * len(row)
        return ["background-color:#f8d7da; color:#721c24"] * len(row)
    
    st.dataframe(
        df_hist[columnas_disp]
        .sort_values("fecha", ascending=False)
        .style.apply(color_tipo, axis=1),
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Total de movimientos: {len(df_hist)}")
    
    
    # ===================================================
    # ⚙️ CATÁLOGO (AGREGAR ÍTEMS Y TALLAS)
    # ===================================================
    with sub_catalogo:
    st.markdown("### ⚙️ Gestión del catálogo de ítems")
    st.info("Aquí puedes agregar nuevos ítems o tallas sin tocar el código.")
    
    # --- Ver catálogo actual ---
    st.markdown("#### 📋 Catálogo actual")
    for cat, items in catalogo.items():
    with st.expander(f"**{cat}** — {len(items)} ítem(s)"):
        for item, cfg in items.items():
            if cfg["tallas"]:
                tallas_str = ", ".join(cfg.get("opciones_talla", []))
                st.markdown(f"- **{item}** | Tallas: {tallas_str}")
            else:
                st.markdown(f"- **{item}** | Sin tallas")
    
    st.divider()
    
    # --- Agregar nuevo ítem ---
    st.markdown("#### ➕ Agregar nuevo ítem")
    with st.form("form_nuevo_item", clear_on_submit=True):
    col1, col2 = st.columns(2)
    cat_nueva   = col1.selectbox("Categoría", list(catalogo.keys()), key="cat_nuevo")
    nombre_item = col2.text_input("Nombre del ítem", key="nombre_nuevo")
    maneja_tallas = st.checkbox("¿Maneja tallas?", key="tallas_nuevo")
    tallas_texto  = st.text_input(
        "Tallas separadas por coma (ej: S,M,L,XL)",
        key="tallas_texto_nuevo",
        disabled=not maneja_tallas
    )
    submitted_ni = st.form_submit_button("➕ Agregar ítem")
    
    if submitted_ni:
    if not nombre_item.strip():
        st.warning("⚠️ Debes ingresar un nombre para el ítem.")
    elif nombre_item.strip() in catalogo[cat_nueva]:
        st.warning(f"⚠️ El ítem '{nombre_item}' ya existe en {cat_nueva}.")
    else:
        nuevo_cfg = {"tallas": maneja_tallas}
        if maneja_tallas and tallas_texto.strip():
            nuevo_cfg["opciones_talla"] = [
                t.strip() for t in tallas_texto.split(",") if t.strip()
            ]
        catalogo[cat_nueva][nombre_item.strip()] = nuevo_cfg
    
        r_cat = gh_put(
            "CATALOGO.json", catalogo,
            gh_headers, repo, sha=catalogo_sha, branch=branch,
            mensaje=f"Nuevo ítem: {nombre_item}"
        )
        if r_cat.status_code in (200, 201):
            st.success(f"✅ Ítem '{nombre_item}' agregado a {cat_nueva}")
            catalogo_sha = r_cat.json().get("content", {}).get("sha", catalogo_sha)
        else:
            st.error("❌ Error al guardar el catálogo en GitHub")
    
    st.divider()
    
    # --- Agregar talla a ítem existente ---
    st.markdown("#### 📐 Agregar talla a ítem existente")
    items_con_talla = [
    (cat, item)
    for cat, items in catalogo.items()
    for item, cfg in items.items()
    if cfg["tallas"]
    ]
    
    if not items_con_talla:
    st.info("No hay ítems con tallas en el catálogo.")
    else:
    with st.form("form_nueva_talla", clear_on_submit=True):
        opciones_items = [f"{cat} → {item}" for cat, item in items_con_talla]
        item_sel_str   = st.selectbox("Ítem", opciones_items, key="item_talla_sel")
        nueva_talla    = st.text_input("Nueva talla", key="nueva_talla_input")
        submitted_nt   = st.form_submit_button("➕ Agregar talla")
    
    if submitted_nt:
        if not nueva_talla.strip():
            st.warning("⚠️ Debes ingresar una talla.")
        else:
            idx_sel  = opciones_items.index(item_sel_str)
            cat_sel, item_sel = items_con_talla[idx_sel]
            tallas_act = catalogo[cat_sel][item_sel].get("opciones_talla", [])
            if nueva_talla.strip() in tallas_act:
                st.warning(f"⚠️ La talla '{nueva_talla}' ya existe en {item_sel}.")
            else:
                catalogo[cat_sel][item_sel]["opciones_talla"].append(nueva_talla.strip())
                r_cat = gh_put(
                    "CATALOGO.json", catalogo,
                    gh_headers, repo, sha=catalogo_sha, branch=branch,
                    mensaje=f"Nueva talla {nueva_talla} en {item_sel}"
                )
                if r_cat.status_code in (200, 201):
                    st.success(f"✅ Talla '{nueva_talla}' agregada a {item_sel}")
                    catalogo_sha = r_cat.json().get("content", {}).get("sha", catalogo_sha)
                else:
                    st.error("❌ Error al guardar el catálogo en GitHub")
    
    
