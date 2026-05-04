"""
ÁGORA TECH — Plataforma Comercial v3
Diseño corporativo premium · Gemini IA · Gestión de usuarios
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import json, os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ═══════════════════════════════════════════
# DATOS — cargados desde JSON externos
# ═══════════════════════════════════════════
@st.cache_data
def cargar_proyectos():
    base = os.path.dirname(os.path.abspath(__file__))
    for nombre in ["proyectos.json", "proyectos_v2.json"]:
        ruta = os.path.join(base, nombre)
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

PROYECTOS_BASE = cargar_proyectos()

# ═══════════════════════════════════════════
# GESTIÓN DE USUARIOS (en session_state)
# ═══════════════════════════════════════════
USUARIOS_DEFAULT = {
    "luisa":    {"pass":"luisa2026",    "nombre":"Luisa Olivares",     "rol":"gerente",   "comercial":"LUISA OLIVARES",     "activo":True},
    "gerente":  {"pass":"gerente2026",  "nombre":"Luisa Olivares",     "rol":"gerente",   "comercial":"LUISA OLIVARES",     "activo":True},
    "rafael":   {"pass":"rafael2026",   "nombre":"Rafael Torres",      "rol":"comercial", "comercial":"RAFAEL TORRES",      "activo":True},
    "sonia":    {"pass":"sonia2026",    "nombre":"Sonia Castro",       "rol":"comercial", "comercial":"SONIA CASTRO",       "activo":True},
    "lina":     {"pass":"lina2026",     "nombre":"Lina Calle",         "rol":"comercial", "comercial":"LINA CALLE",         "activo":True},
    "alberto":  {"pass":"alberto2026",  "nombre":"Alberto Ferrer",     "rol":"comercial", "comercial":"ALBERTO FERRER",     "activo":True},
    "santiago": {"pass":"santiago2026", "nombre":"Santiago Bohórquez", "rol":"comercial", "comercial":"SANTIAGO BOHORQUEZ", "activo":True},
}

def get_usuarios():
    if "usuarios_db" not in st.session_state:
        st.session_state.usuarios_db = dict(USUARIOS_DEFAULT)
    return st.session_state.usuarios_db

# ═══════════════════════════════════════════
# CONFIG STREAMLIT
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="Ágora Tech",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# DISEÑO CORPORATIVO PREMIUM
# ═══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Lato:wght@300;400;700&display=swap');

:root {
  --ink:    #04111E;
  --ink2:   #0A1E30;
  --ink3:   #0E2D47;
  --sea:    #00C896;
  --sea2:   #00A87E;
  --sky:    #1A9FCC;
  --gold:   #D97706;
  --rose:   #E84040;
  --border: #E3EAF3;
  --bg:     #F6F9FC;
  --white:  #FFFFFF;
  --t1:     #04111E;
  --t2:     #4A6580;
  --t3:     #8BA3BD;
}

html, body, [class*="css"] {
  font-family: 'Lato', sans-serif !important;
  background: var(--bg) !important;
  color: var(--t1) !important;
}
h1,h2,h3,h4,h5 { font-family: 'Sora', sans-serif !important; color: var(--ink) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--ink) !important;
  border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.75) !important; }
[data-testid="stSidebar"] .stTextInput input {
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.15) !important;
  color: white !important; border-radius: 8px !important;
}

/* ── Botones principales ── */
.stButton > button {
  background: linear-gradient(135deg, var(--sea), var(--sky)) !important;
  color: var(--ink) !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 8px 18px !important;
  letter-spacing: 0.3px !important;
  transition: all 0.18s ease !important;
  box-shadow: 0 2px 8px rgba(0,200,150,0.25) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(0,200,150,0.4) !important;
}
.stButton > button[kind="secondary"] {
  background: white !important;
  color: var(--ink) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: var(--sea) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  border-radius: 8px !important;
  border: 1.5px solid var(--border) !important;
  font-family: 'Lato', sans-serif !important;
  transition: border-color 0.18s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--sea) !important;
  box-shadow: 0 0 0 3px rgba(0,200,150,0.1) !important;
}

/* ── Cards ── */
.card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 6px rgba(4,17,30,0.05);
  margin-bottom: 16px;
}
.card-sm { padding: 14px 16px; border-radius: 10px; }

/* ── KPI Cards ── */
.kpi {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 6px rgba(4,17,30,0.05);
  position: relative;
  overflow: hidden;
}
.kpi::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--sea), var(--sky));
}
.kpi-label { font-size: 10px; font-weight: 700; color: var(--t3); text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 8px; }
.kpi-val { font-family: 'Sora', sans-serif; font-size: 24px; font-weight: 800; color: var(--ink); line-height: 1; }
.kpi-val.g { color: #05875D; }
.kpi-val.r { color: var(--rose); }
.kpi-val.o { color: var(--gold); }
.kpi-sub { font-size: 11px; color: var(--t3); margin-top: 5px; }

/* ── Badges ── */
.b-g { background: #D1FAF0; color: #065F46; padding: 3px 10px; border-radius: 20px; font-size: 10.5px; font-weight: 700; display: inline-block; }
.b-y { background: #FEF3C7; color: #92400E; padding: 3px 10px; border-radius: 20px; font-size: 10.5px; font-weight: 700; display: inline-block; }
.b-b { background: #DBEAFE; color: #1E3A8A; padding: 3px 10px; border-radius: 20px; font-size: 10.5px; font-weight: 700; display: inline-block; }
.b-r { background: #FEE2E2; color: #991B1B; padding: 3px 10px; border-radius: 20px; font-size: 10.5px; font-weight: 700; display: inline-block; }
.b-p { background: #EDE9FE; color: #5B21B6; padding: 3px 10px; border-radius: 20px; font-size: 10.5px; font-weight: 700; display: inline-block; }
.b-gray { background: #F1F5F9; color: #64748B; padding: 3px 10px; border-radius: 20px; font-size: 10.5px; font-weight: 700; display: inline-block; }

/* ── Alertas ── */
.al-r { background: #FEF2F2; border-left: 3px solid var(--rose); padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 13px; margin-bottom: 8px; }
.al-y { background: #FFFBEB; border-left: 3px solid var(--gold); padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 13px; margin-bottom: 8px; }
.al-g { background: #F0FDF9; border-left: 3px solid var(--sea); padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 13px; margin-bottom: 8px; }
.al-b { background: #EFF6FF; border-left: 3px solid var(--sky); padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 13px; margin-bottom: 8px; }

/* ── Header de página ── */
.page-header {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 24px; padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.page-icon {
  width: 42px; height: 42px; border-radius: 10px;
  background: linear-gradient(135deg, var(--sea), var(--sky));
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.page-title { font-family: 'Sora',sans-serif; font-size: 20px; font-weight: 700; color: var(--ink); margin: 0; }
.page-sub { font-size: 12px; color: var(--t3); margin: 2px 0 0; }

/* ── Chat ── */
.chat-u {
  background: linear-gradient(135deg, var(--sea), var(--sky));
  color: var(--ink); padding: 12px 16px;
  border-radius: 16px 16px 3px 16px;
  margin: 8px 0; font-weight: 600;
  max-width: 78%; margin-left: auto; display: block;
  font-size: 13.5px; line-height: 1.5;
}
.chat-a {
  background: white; border: 1px solid var(--border);
  padding: 14px 18px; border-radius: 16px 16px 16px 3px;
  margin: 8px 0; max-width: 88%;
  box-shadow: 0 1px 6px rgba(4,17,30,0.06);
  line-height: 1.75; display: block; font-size: 13.5px;
}

/* ── Tabla de edificios ── */
.bld-card {
  background: white; border: 1px solid var(--border);
  border-radius: 12px; padding: 16px;
  box-shadow: 0 1px 6px rgba(4,17,30,0.05);
  transition: all 0.18s; cursor: pointer;
  margin-bottom: 12px;
}
.bld-card:hover { border-color: var(--sea); box-shadow: 0 4px 16px rgba(0,200,150,0.15); transform: translateY(-2px); }

/* ── Formulario sin borde ── */
div[data-testid="stForm"] { border: none !important; padding: 0 !important; }

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: rgba(255,255,255,0.65) !important;
  font-weight: 500 !important;
  border: none !important;
  text-align: left !important;
  box-shadow: none !important;
  border-radius: 8px !important;
  padding: 9px 14px !important;
  font-size: 13px !important;
  letter-spacing: 0 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.08) !important;
  color: white !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── Métricas ── */
[data-testid="metric-container"] {
  background: white; border: 1px solid var(--border);
  border-radius: 12px; padding: 16px !important;
  box-shadow: 0 1px 6px rgba(4,17,30,0.05);
}

/* ── Tags de estado ── */
.tag-nomad { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:700; font-family:'IBM Plex Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════
def init():
    defaults = {
        "logged_in": False, "user": None, "page": "Dashboard",
        "messages": [], "gemini_model": None,
        "crm": None, "correo": "", "editing": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ═══════════════════════════════════════════
# GEMINI — cargado de secrets de Streamlit
# ═══════════════════════════════════════════
def init_gemini_auto():
    """Intenta inicializar Gemini desde st.secrets automáticamente."""
    if st.session_state.gemini_model:
        return True
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            genai.configure(api_key=key)
            m = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                system_instruction="""Eres el asistente comercial de Ágora Tech Colombia.
Sistema SALTO HomeLok (nube, Bluetooth, PIN, QR, app iOS/Android).
Financiación 100% a 24/36 meses sin intereses. Llave en mano 40 días.
Pipeline: 84 proyectos activos, $8.6B en cotizaciones.
Proyectos clave: Nomad 53 (David Conde) — cierre más cercano; Bosque San Vicente — única con financiamiento, asamblea 2 mayo; Tiara — pasó primer filtro.
Patrones de rechazo: adultos mayores (Inzar VI), seguridad percibida (El Bosque), precios (70A, Hotel Mendoza).
Responde en español colombiano. Sé específico y accionable."""
            )
            st.session_state.gemini_model = m
            return True
    except:
        pass
    return False

def init_gemini_key(key: str):
    """Inicializar Gemini con una key manual."""
    try:
        genai.configure(api_key=key)
        m = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction="""Eres el asistente comercial de Ágora Tech Colombia.
Sistema SALTO HomeLok. Financiación 100% a 24/36 meses sin intereses.
Responde en español colombiano. Sé específico y accionable."""
        )
        st.session_state.gemini_model = m
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def ask_gemini(q, ctx=""):
    m = st.session_state.gemini_model
    if not m:
        return "⚠️ La IA no está configurada. Pide a Luisa que configure la API Key de Gemini en la plataforma."
    try:
        p = f"DATOS CRM:\n{ctx[:22000]}\n\nSOLICITUD:\n{q}" if ctx else q
        return m.generate_content(p).text
    except Exception as e:
        return f"Error Gemini: {e}"

# ═══════════════════════════════════════════
# CRM EN MEMORIA
# ═══════════════════════════════════════════
def get_crm() -> pd.DataFrame:
    if st.session_state.crm is None:
        rows = []
        for p in PROYECTOS_BASE:
            rows.append({
                "id":        p.get("id",""),
                "nombre":    p.get("nombre",""),
                "comercial": p.get("comercial",""),
                "contacto":  p.get("contacto",""),
                "email":     p.get("email",""),
                "total":     p.get("total","$0"),
                "totalNum":  int(float(p.get("totalNum",0) or 0)),
                "cuota24":   p.get("cuota24","$0"),
                "cuota36":   p.get("cuota36","$0"),
                "c24Num":    int(float(p.get("c24Num",0) or 0)),
                "c36Num":    int(float(p.get("c36Num",0) or 0)),
                "vig":       p.get("vig",""),
                "vigH":      p.get("vigH",""),
                "estado":    p.get("estado","nuevo"),
                "etapaOrig": p.get("etapaOrig",""),
                "version":   p.get("version","v1"),
                "notas":     p.get("notas",""),
                "lastUpdate": p.get("lastUpdate",""),
                "lastNote":  p.get("lastNote",""),
                "fecha":     p.get("fecha",""),
                "drive":     p.get("drive",""),
            })
        st.session_state.crm = pd.DataFrame(rows)
    return st.session_state.crm

def mis_proyectos() -> pd.DataFrame:
    df = get_crm()
    u = st.session_state.user
    if not u: return df.iloc[0:0]
    if u["rol"] == "gerente": return df
    return df[df["comercial"].str.upper() == u["comercial"].upper()]

def update_proy(nombre, campos):
    df = get_crm()
    mask = df["nombre"] == nombre
    if mask.any():
        for k, v in campos.items(): df.loc[mask, k] = v
        st.session_state.crm = df

def add_proy(datos):
    df = get_crm()
    st.session_state.crm = pd.concat([pd.DataFrame([datos]), df], ignore_index=True)

# ═══════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════
def fc(n):
    try:
        n = int(float(n or 0))
        return "$0" if n == 0 else "$" + f"{n:,}".replace(",",".")
    except: return "$0"

ESTADOS = ["nuevo","cotizado","negociacion","cerrado","perdido"]
ESTADO_LABEL = {"nuevo":"🔵 Lead","cotizado":"🟡 Enviado","negociacion":"🟠 Negociando","cerrado":"🟢 Cerrado","perdido":"🔴 Perdido"}
ESTADO_CLS   = {"nuevo":"b-b","cotizado":"b-y","negociacion":"b-p","cerrado":"b-g","perdido":"b-r"}
COMS_LISTA   = ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"]

def badge(estado):
    cls = ESTADO_CLS.get(estado,"b-gray")
    lbl = ESTADO_LABEL.get(estado,estado)
    return f'<span class="{cls}">{lbl}</span>'

def header(icon, title, sub=""):
    st.markdown(f"""
    <div class="page-header">
      <div class="page-icon">{icon}</div>
      <div><div class="page-title">{title}</div>
        {'<div class="page-sub">'+sub+'</div>' if sub else ''}</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════
def pg_login():
    # Intentar auto-inicializar Gemini al cargar
    init_gemini_auto()

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:60px 0 32px'>
          <div style='font-family:Sora,sans-serif;font-size:11px;font-weight:700;
               color:#8BA3BD;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px'>
               SISTEMA COMERCIAL</div>
          <div style='font-family:Sora,sans-serif;font-size:36px;font-weight:800;
               color:#04111E;letter-spacing:-2px;line-height:1'>ÁGORA TECH</div>
          <div style='width:40px;height:3px;background:linear-gradient(90deg,#00C896,#1A9FCC);
               margin:16px auto;border-radius:2px'></div>
          <div style='font-size:13px;color:#8BA3BD;font-weight:300'>
               Plataforma de Gestión Comercial</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            with st.form("login_form"):
                usuario  = st.text_input("Usuario", placeholder="Ingresa tu usuario...")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••••")
                entrar   = st.form_submit_button("Ingresar a la plataforma", use_container_width=True)
                if entrar:
                    u = usuario.strip().lower()
                    usuarios = get_usuarios()
                    if u in usuarios and usuarios[u]["activo"] and usuarios[u]["pass"] == password:
                        st.session_state.logged_in = True
                        st.session_state.user = usuarios[u]
                        init_gemini_auto()
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style='background:#F6F9FC;border:1px solid #E3EAF3;border-radius:10px;
             padding:14px 16px;margin-top:12px;font-size:12px;color:#8BA3BD;text-align:center'>
          luisa / luisa2026 · rafael / rafael2026 · sonia / sonia2026<br>
          lina / lina2026 · alberto / alberto2026 · santiago / santiago2026
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
def mostrar_sidebar():
    u = st.session_state.user
    es_g = u["rol"] == "gerente"
    ai_ok = st.session_state.gemini_model is not None

    with st.sidebar:
        st.markdown(f"""
        <div style='padding:20px 16px 12px'>
          <div style='font-family:Sora,sans-serif;font-size:16px;font-weight:800;
               color:#fff;letter-spacing:-0.5px'>ÁGORA TECH</div>
          <div style='font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;
               text-transform:uppercase;margin-top:3px'>Plataforma Comercial</div>
        </div>
        <div style='background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.2);
             border-radius:10px;padding:10px 14px;margin:0 12px 16px'>
          <div style='font-size:13px;font-weight:600;color:#fff'>{u["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:1px'>
            {u["rol"].capitalize()} · Ágora Tech · {'🟢 IA activa' if ai_ok else '🔴 IA sin configurar'}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navegación
        nav_base = [("📊","Dashboard"),("📋","Proyectos"),("🧮","Nueva Cotización"),
                    ("📝","Actualizar Estado"),("🏢","Edificios"),("📅","Calendario"),
                    ("✉️","Correos IA"),("🤖","Asistente IA")]
        nav_gerente = [("🔍","Auditoría"),("📈","Informes"),("🎯","Pipeline Kanban"),
                       ("📊","Encuestas"),("👥","Usuarios"),("⚙️","Configuración")]

        todos = nav_base + (nav_gerente if es_g else [])

        st.markdown('<div style="padding:0 4px">', unsafe_allow_html=True)
        for icono, nombre in todos:
            activo = st.session_state.page == nombre
            bg = "rgba(0,200,150,.15)" if activo else "transparent"
            color = "#00C896" if activo else "rgba(255,255,255,.6)"
            brd = "1px solid rgba(0,200,150,.3)" if activo else "1px solid transparent"
            st.markdown(f"""
            <div style='background:{bg};border:{brd};border-radius:8px;
                 margin-bottom:2px;transition:all .15s'>""", unsafe_allow_html=True)
            if st.button(f"{icono}  {nombre}", key=f"nav_{nombre}", use_container_width=True):
                st.session_state.page = nombre
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Cerrar sesión", use_container_width=True, key="logout"):
            for k in ["logged_in","user","messages","gemini_model","page","crm","correo","editing"]:
                st.session_state.pop(k, None)
            st.rerun()

# ═══════════════════════════════════════════
# PÁGINA: DASHBOARD
# ═══════════════════════════════════════════
def pg_dashboard():
    u = st.session_state.user
    es_g = u["rol"] == "gerente"
    df = mis_proyectos()

    # Hero header
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#04111E 0%,#0A2540 55%,#0E3D6B 100%);
         border-radius:14px;padding:28px 32px;margin-bottom:24px;
         position:relative;overflow:hidden'>
      <div style='position:absolute;top:-60px;right:-60px;width:220px;height:220px;
           border-radius:50%;background:radial-gradient(circle,rgba(0,200,150,.18) 0%,transparent 70%)'></div>
      <div style='position:absolute;bottom:-40px;left:200px;width:160px;height:160px;
           border-radius:50%;background:radial-gradient(circle,rgba(26,159,204,.12) 0%,transparent 70%)'></div>
      <div style='font-family:Sora,sans-serif;font-size:11px;font-weight:700;
           color:rgba(0,200,150,.8);letter-spacing:3px;text-transform:uppercase;margin-bottom:10px'>
           Dashboard · {datetime.now().strftime("%d %B %Y")}</div>
      <div style='font-family:Sora,sans-serif;font-size:24px;font-weight:800;color:#fff;
           letter-spacing:-1px;margin-bottom:6px'>
           {"Vista General del Equipo" if es_g else f"Hola, {u['nombre'].split()[0]}"}</div>
      <div style='font-size:13px;color:rgba(255,255,255,.45)'>
           {len(df)} proyectos activos · Pipeline ${int(df["totalNum"].sum())/1e9:.2f}B</div>
    </div>""", unsafe_allow_html=True)

    # KPIs
    total = int(df["totalNum"].sum())
    con_v = df[df["totalNum"]>0]
    prom  = int(con_v["totalNum"].mean()) if len(con_v) else 0
    negoc = int(df[df["estado"]=="negociacion"].shape[0])
    cotiz = int(df[df["estado"]=="cotizado"].shape[0])
    cerr  = int(df[df["estado"]=="cerrado"].shape[0])

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(f'<div class="kpi"><div class="kpi-label">Pipeline Total</div><div class="kpi-val g">${total/1e9:.2f}B</div><div class="kpi-sub">{len(df)} proyectos</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kpi-label">Promedio / Proyecto</div><div class="kpi-val">${prom/1e6:.1f}M</div><div class="kpi-sub">{len(con_v)} con valor</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kpi-label">Negociando</div><div class="kpi-val o">{negoc}</div><div class="kpi-sub">cierre cercano</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><div class="kpi-label">Cotizaciones Enviadas</div><div class="kpi-val o">{cotiz}</div><div class="kpi-sub">en seguimiento</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi"><div class="kpi-label">Contratos Cerrados</div><div class="kpi-val {"r" if cerr==0 else "g"}">{cerr}</div><div class="kpi-sub">{"⚠ urgente" if cerr==0 else "excelente"}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficas
    lm = {"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}
    c1, c2 = st.columns(2)

    with c1:
        est = df.groupby("estado").size().reset_index(name="n")
        est["Estado"] = est["estado"].map(lm).fillna(est["estado"])
        fig = px.bar(est, x="Estado", y="n",
                     color_discrete_sequence=["#00C896"],
                     title="Proyectos por Estado", labels={"n":"Proyectos"})
        fig.update_traces(marker_color=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"][:len(est)], marker_line_width=0)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          font_family="Lato", title_font_family="Sora",
                          title_font_size=14, margin=dict(t=40,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        if es_g:
            dc = df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
            dc["M"]   = (dc["totalNum"]/1e6).round(1)
            dc["Com"] = dc["comercial"].str.split().str[0]
            fig2 = px.bar(dc.sort_values("M",ascending=True), x="M", y="Com", orientation="h",
                          title="Pipeline por Comercial ($M)", color="M",
                          color_continuous_scale=["#1A9FCC","#00C896"],
                          labels={"M":"$M","Com":""})
            fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",
                               coloraxis_showscale=False,font_family="Lato",
                               title_font_family="Sora",title_font_size=14,margin=dict(t=40,b=10))
        else:
            pie_d = df.groupby("estado").size().reset_index(name="n")
            pie_d["Estado"] = pie_d["estado"].map(lm).fillna(pie_d["estado"])
            fig2 = px.pie(pie_d, values="n", names="Estado", hole=0.48,
                          color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"],
                          title="Mis Proyectos")
            fig2.update_layout(paper_bgcolor="white",font_family="Lato",
                               title_font_family="Sora",title_font_size=14,margin=dict(t=40,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Alertas inteligentes
    st.markdown("### 🚨 Alertas del Sistema")
    if es_g:
        st.markdown('<div class="al-r">❗ <b>0 contratos cerrados en 5 meses.</b> Pipeline de $8.6B sin conversión. El cuello de botella está en el cierre, no en la prospección.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-y">⚡ <b>Nomad 53 (David Conde / Rafael)</b> — único en negociación activa. Reunión agendada 30 de abril. Llevar contrato listo.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-y">🌳 <b>Bosque San Vicente</b> — única propuesta con financiamiento. Asamblea agendada 2 de mayo. Alta probabilidad de cierre.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-g">✅ <b>Tiara</b> — pasó primer filtro del consejo el 24 de abril. Agendar presentación en asamblea urgente.</div>', unsafe_allow_html=True)

    sin_upd = df[df["lastUpdate"].astype(str).str.strip()==""].shape[0]
    if sin_upd > 0:
        st.markdown(f'<div class="al-b">📋 <b>{sin_upd} proyectos</b> sin actualización de estado. Ve a "Actualizar Estado" para registrar el seguimiento.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PÁGINA: PROYECTOS
# ═══════════════════════════════════════════
def pg_proyectos():
    es_g = st.session_state.user["rol"] == "gerente"
    df   = mis_proyectos()
    header("📋","Proyectos","Gestión completa del pipeline comercial")

    c1,c2,c3 = st.columns([2,1,1])
    with c1: buscar = st.text_input("🔍 Buscar edificio", placeholder="Nombre...")
    with c2: filtro_e = st.selectbox("Estado", ["Todos"]+ESTADOS)
    with c3:
        if es_g:
            coms = ["Todos"]+sorted(df["comercial"].dropna().unique().tolist())
            filtro_c = st.selectbox("Comercial", coms)
        else: filtro_c = "Todos"

    dff = df.copy()
    if buscar:        dff = dff[dff["nombre"].str.contains(buscar, case=False, na=False)]
    if filtro_e != "Todos": dff = dff[dff["estado"]==filtro_e]
    if filtro_c != "Todos": dff = dff[dff["comercial"]==filtro_c]

    st.markdown(f'<div style="font-size:12px;color:#8BA3BD;margin-bottom:12px">{len(dff)} proyectos encontrados</div>', unsafe_allow_html=True)

    for _, r in dff.iterrows():
        tn    = int(r.get("totalNum") or 0)
        total = fc(tn) if tn else r.get("total","$0") or "$0"
        c24   = fc(int(r.get("c24Num") or 0)) if tn else r.get("cuota24","—") or "—"
        c36   = fc(int(r.get("c36Num") or 0)) if tn else r.get("cuota36","—") or "—"
        est   = str(r.get("estado","nuevo"))
        nota  = str(r.get("lastNote","") or r.get("notas","") or r.get("etapaOrig",""))
        drive = str(r.get("drive","") or "")
        drv   = f'<a href="{drive}" target="_blank" style="font-size:11px;color:#1A73E8;margin-left:8px">📁 Drive</a>' if drive.startswith("http") else ""

        label = f"🏢  {r['nombre']}   —   {total}   —   {r.get('comercial','')}"
        with st.expander(label, expanded=False):
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("Valor total", total)
            m2.metric("Cuota 24m", c24)
            m3.metric("Cuota 36m", c36)
            m4.markdown(f"**Estado:**<br>{badge(est)}{drv}", unsafe_allow_html=True)

            if nota and nota != "nan":
                st.markdown(f'<div class="al-b" style="font-size:12px">📝 {nota[:300]}</div>', unsafe_allow_html=True)

            bc1,bc2 = st.columns(2)
            if bc1.button("📝 Actualizar estado", key=f"u_{r.get('id',r['nombre'])}"):
                st.session_state.editing = r["nombre"]
                st.session_state.page = "Actualizar Estado"
                st.rerun()
            if bc2.button("✉️ Generar correo IA", key=f"c_{r.get('id',r['nombre'])}"):
                st.session_state.page = "Correos IA"
                st.rerun()


# ═══════════════════════════════════════════
# PÁGINA: NUEVA COTIZACIÓN
# ═══════════════════════════════════════════
def pg_nueva_cotizacion():
    header("🧮","Nueva Cotización","Registrar una cotización en el CRM")
    st.markdown('<div class="card">', unsafe_allow_html=True)

    with st.form("form_cot"):
        st.markdown("**Datos del edificio**")
        c1,c2 = st.columns(2)
        with c1:
            nombre   = st.text_input("Nombre del edificio *", placeholder="Ej: Edificio Altos del Pino")
            contacto = st.text_input("Contacto *", placeholder="Juan Pérez — Administrador")
            email    = st.text_input("Email de contacto")
        with c2:
            direccion = st.text_input("Dirección")
            telefono  = st.text_input("Teléfono")
            drive_url = st.text_input("Link carpeta Drive (opcional)")

        st.markdown("---")
        st.markdown("**Valores**")
        c1,c2,c3 = st.columns(3)
        with c1: valor  = st.number_input("Valor total ($)", min_value=0, value=0, step=1_000_000, format="%d")
        with c2: vig_v  = st.number_input("Vigilancia actual ($/mes)", min_value=0, value=0, step=100_000, format="%d")
        with c3: vig_h  = st.text_input("Vigilancia vigente hasta", placeholder="Nov 2026")

        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1: estado  = st.selectbox("Estado inicial", ESTADOS)
        with c2: version = st.text_input("Versión", value="v1")
        notas = st.text_area("Observaciones", placeholder="Contexto, acuerdos, próximos pasos...")
        arch  = st.file_uploader("Adjuntar archivos (PDF, Excel, imágenes)", accept_multiple_files=True)

        if st.form_submit_button("💾 Guardar en CRM", use_container_width=True):
            if not nombre:
                st.error("El nombre del edificio es obligatorio")
            else:
                u    = st.session_state.user
                c24n = valor//24 if valor else 0
                c36n = valor//36 if valor else 0
                add_proy({
                    "id":int(datetime.now().timestamp()),
                    "nombre":nombre.upper(),"comercial":u["comercial"],
                    "contacto":contacto,"email":email,
                    "total":fc(valor),"totalNum":valor,
                    "cuota24":fc(c24n),"cuota36":fc(c36n),
                    "c24Num":c24n,"c36Num":c36n,
                    "vig":str(vig_v),"vigH":vig_h,
                    "estado":estado,"etapaOrig":estado,"version":version,
                    "notas":notas,"lastUpdate":datetime.now().isoformat(),
                    "lastNote":notas[:100],"fecha":datetime.now().strftime("%d %b %Y"),
                    "drive":drive_url,
                })
                st.success(f"✅ **{nombre}** guardado — {fc(valor)}")
                if arch: st.info(f"📎 {len(arch)} archivo(s): {', '.join(f.name for f in arch)}")
                st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PÁGINA: ACTUALIZAR ESTADO
# ═══════════════════════════════════════════
def pg_actualizar():
    header("📝","Actualizar Estado","Registro obligatorio de seguimiento — mínimo cada 7 días")
    df = mis_proyectos()

    presel = st.session_state.get("editing","")
    nombres = ["— Selecciona un edificio —"] + sorted(df["nombre"].dropna().unique().tolist())
    idx = nombres.index(presel) if presel in nombres else 0
    sel = st.selectbox("Edificio:", nombres, index=idx)

    if sel != "— Selecciona un edificio —":
        r = df[df["nombre"]==sel].iloc[0]
        st.markdown('<div class="card card-sm">', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Valor", fc(int(r.get("totalNum") or 0)))
        c2.metric("Comercial", str(r.get("comercial","—")))
        c3.metric("Estado actual", str(r.get("estado","—")))
        c4.metric("Última actualización", str(r.get("lastUpdate","Nunca"))[:10] or "Nunca")
        if r.get("lastNote"):
            st.markdown(f'<div style="font-size:12px;color:#8BA3BD;margin-top:8px">Última nota: {str(r["lastNote"])[:200]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.form("upd_form"):
            nuevo_e = st.selectbox("Nuevo estado *", ESTADOS,
                index=ESTADOS.index(str(r.get("estado","nuevo"))) if str(r.get("estado","nuevo")) in ESTADOS else 0)
            nota = st.text_area("Nota de seguimiento * (obligatoria)",
                                placeholder="¿Qué pasó? ¿Cuál es el próximo paso? ¿Quién respondió? Sé específico...")
            if st.form_submit_button("✅ Guardar actualización", use_container_width=True):
                if not nota.strip():
                    st.error("La nota de seguimiento es obligatoria")
                else:
                    update_proy(sel, {"estado":nuevo_e,"lastNote":nota,"lastUpdate":datetime.now().isoformat()})
                    st.success(f"✅ **{sel}** → {nuevo_e}")
                    st.session_state.editing = ""
                    st.rerun()


# ═══════════════════════════════════════════
# PÁGINA: EDIFICIOS
# ═══════════════════════════════════════════
def pg_edificios():
    header("🏢","Edificios","Carpetas y archivos por proyecto")
    df = mis_proyectos()
    buscar = st.text_input("🔍 Buscar", placeholder="Nombre del edificio...")
    if buscar: df = df[df["nombre"].str.contains(buscar,case=False,na=False)]

    cols = st.columns(3)
    for i,(_, r) in enumerate(df.iterrows()):
        with cols[i%3]:
            tn    = int(r.get("totalNum") or 0)
            total = fc(tn) if tn else "Sin cotización"
            c36   = fc(int(r.get("c36Num") or 0)) if tn else "—"
            est   = str(r.get("estado","nuevo"))
            drive = str(r.get("drive","") or "")
            nota  = str(r.get("notas","") or r.get("lastNote",""))

            drv_html = ""
            if drive.startswith("http"):
                drv_html = f'<a href="{drive}" target="_blank" style="background:#E8F0FE;color:#1A73E8;border-radius:6px;padding:3px 9px;font-size:10px;font-weight:700;text-decoration:none;display:inline-block;margin-top:8px">📁 Ver en Drive</a>'

            st.markdown(f"""
            <div class="bld-card">
              <div style='font-family:Sora,sans-serif;font-size:13px;font-weight:700;
                   color:#04111E;margin-bottom:4px'>{str(r["nombre"])[:30]}</div>
              <div style='font-size:11px;color:#8BA3BD;margin-bottom:8px'>
                {str(r.get("comercial","—"))}</div>
              <div style='font-family:Sora,sans-serif;font-size:17px;font-weight:800;
                   color:#05875D;margin-bottom:2px'>{total}</div>
              {'<div style="font-size:10.5px;color:#8BA3BD;margin-bottom:8px">Cuota 36m: '+c36+'/mes</div>' if tn else '<div style="margin-bottom:8px"></div>'}
              <div style='margin-bottom:4px'>{badge(est)}</div>
              {'<div style="font-size:11px;color:#8BA3BD;margin-top:6px">'+nota[:80]+'...</div>' if nota and nota!='nan' and len(nota)>5 else ''}
              {drv_html}
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PÁGINA: CALENDARIO
# ═══════════════════════════════════════════
def pg_calendario():
    header("📅","Calendario Comercial","Agenda de actividades y seguimientos")
    es_g = st.session_state.user["rol"] == "gerente"

    col1,col2 = st.columns([2,1])
    with col1:
        st.markdown("#### Registrar actividad")
        with st.form("act_form"):
            c1,c2 = st.columns(2)
            with c1:
                edif = st.text_input("Edificio / Proyecto")
                tipo = st.selectbox("Tipo",["Reunión presencial","Llamada","Visita técnica","Asamblea","Envío de propuesta","Otro"])
            with c2:
                fecha_a = st.date_input("Fecha", value=datetime.now())
                hora_a  = st.time_input("Hora")

            titulo_a = st.text_input("Título *", placeholder="Ej: Reunión consejo directivo")
            if es_g:
                com_r = st.selectbox("Comercial responsable", COMS_LISTA)
            else:
                com_r = st.session_state.user["comercial"]
            notas_a = st.text_area("Notas / Agenda")

            if st.form_submit_button("📅 Guardar actividad", use_container_width=True):
                if titulo_a:
                    st.success(f"✅ Actividad guardada: **{titulo_a}** — {fecha_a.strftime('%d %b')} {hora_a.strftime('%H:%M')}")
                else: st.error("El título es obligatorio")

    with col2:
        st.markdown("#### ⏰ Prioritario esta semana")
        urgentes = [
            ("Nomad 53","Reunión David Conde — 30 abr — Llevar contrato","#FEF3C7","#92400E"),
            ("Bosque San Vicente","Asamblea 2 de mayo — única con financiamiento","#FEF3C7","#92400E"),
            ("Tiara","Agendar presentación en asamblea — pasó primer filtro","#F0FDF9","#065F46"),
            ("Edificio El Cerro","Presentación consejo mié 29 — 7pm","#EFF6FF","#1E3A8A"),
            ("Entorno 109","Enviar cotización ajustada — jueves","#EFF6FF","#1E3A8A"),
            ("Risaralda","Decisión agendada 30 abril — hacer seguimiento","#FEF3C7","#92400E"),
        ]
        for nombre_u,desc,bg,col_t in urgentes:
            st.markdown(f"""
            <div style='background:{bg};border-radius:8px;padding:10px 12px;
                 margin-bottom:8px;border-left:3px solid {col_t}'>
              <div style='font-size:12px;font-weight:700;color:#04111E'>{nombre_u}</div>
              <div style='font-size:10.5px;color:#8BA3BD;margin-top:2px'>{desc}</div>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PÁGINA: CORREOS IA
# ═══════════════════════════════════════════
def pg_correos():
    header("✉️","Correos IA","Genera correos comerciales personalizados con inteligencia artificial")
    if not st.session_state.gemini_model:
        st.markdown('<div class="al-r">⚠️ <b>Gemini no está configurado.</b> Ve a Configuración (menú Luisa) para agregar la API Key, o pídele a la gerente que la configure.</div>', unsafe_allow_html=True)

    df   = mis_proyectos()
    col1,col2 = st.columns(2)

    with col1:
        edif_sel = st.selectbox("Edificio / Cotización",
            ["— Seleccionar —"]+sorted(df["nombre"].dropna().unique().tolist()))
        tipo_c = st.selectbox("Tipo de correo",[
            "Primera presentación de propuesta",
            "Seguimiento 5-7 días post-envío",
            "Urgencia — oferta próxima a vencer",
            "Respuesta a objeción: precio alto",
            "Respuesta técnica a pregunta del cliente",
            "Argumentos para asamblea de propietarios",
            "Adultos mayores / discapacidad — respuesta específica",
            "Propuesta de visita presencial",
        ])
        ctx_e = st.text_area("Contexto adicional", height=100,
            placeholder="Ej: El cliente pregunta por adultos mayores. Le parece cara la cuota...")

        if st.button("🤖 Generar correo con IA", use_container_width=True):
            if edif_sel == "— Seleccionar —":
                st.warning("Selecciona un edificio primero")
            elif not st.session_state.gemini_model:
                st.error("Gemini no está configurado. Pide a Luisa que agregue la API Key en Configuración.")
            else:
                r = df[df["nombre"]==edif_sel].iloc[0]
                tn = int(r.get("totalNum") or 0)
                prompt = f"""Redacta un correo comercial de tipo "{tipo_c}" para Ágora Tech Colombia.

EDIFICIO: {edif_sel}
Valor total: {fc(tn)} | Cuota 24m: {fc(int(r.get("c24Num") or 0))} | Cuota 36m: {fc(int(r.get("c36Num") or 0))}
Contacto: {r.get("contacto","Administrador")} | Comercial: {r.get("comercial",st.session_state.user["comercial"])}
Notas del proyecto: {str(r.get("notas",""))[:200]}
{f"Contexto adicional: {ctx_e}" if ctx_e else ""}

INSTRUCCIONES:
- Primera línea: ASUNTO: [asunto específico y llamativo]
- Argumento central: ahorro económico y único con financiamiento sin entrada sin intereses
- Para adultos mayores: enfatizar teclado PIN físico con relieve, no requiere smartphone ni app
- Mencionar Alto 61 como referencia si aplica
- Tono: cálido, profesional, colombiano
- Firma: {st.session_state.user["nombre"]} — Ágora Tech | (+57) 315 101 7511 | agoratech.com.co
- Solo texto plano, sin markdown ni asteriscos"""

                with st.spinner("Generando correo personalizado..."):
                    correo = ask_gemini(prompt)
                st.session_state.correo = correo

    with col2:
        st.markdown("**Vista previa del correo:**")
        val = st.session_state.get("correo","El correo generado aparecerá aquí...")
        st.text_area("", value=val, height=480, key="prev_correo")
        if val != "El correo generado aparecerá aquí...":
            st.download_button("📋 Descargar correo", data=val,
                file_name=f"correo_{edif_sel[:20] if edif_sel!='— Seleccionar —' else 'agora'}_{datetime.now().strftime('%Y%m%d')}.txt")


# ═══════════════════════════════════════════
# PÁGINA: ASISTENTE IA
# ═══════════════════════════════════════════
def pg_asistente():
    header("🤖","Asistente Comercial IA","Consultas estratégicas sobre el pipeline y el equipo")

    if not st.session_state.gemini_model:
        st.markdown('<div class="al-r">⚠️ <b>Gemini no está configurado.</b> Ve a Configuración para agregar la API Key de Gemini.</div>', unsafe_allow_html=True)
        return

    df  = mis_proyectos()
    ctx = df.to_string(max_rows=84) if not df.empty else ""

    for msg in st.session_state.messages:
        cls = "chat-u" if msg["role"]=="user" else "chat-a"
        pre = "👤 " if msg["role"]=="user" else "🤖 "
        st.markdown(f'<div class="{cls}">{pre}{msg["content"]}</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("**Sugerencias rápidas:**")
        sugs = [
            "📊 Resume el estado del pipeline completo",
            "💰 ¿Cuánto vale el pipeline total?",
            "⚡ ¿Cuáles son los proyectos más urgentes?",
            "📈 Estrategia para cerrar Nomad 53",
            "🔍 Patrones de rechazo y cómo superarlos",
            "👴 Cómo responder objeción de adultos mayores",
        ]
        cols = st.columns(3)
        for i,s in enumerate(sugs):
            if cols[i%3].button(s, key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":s})
                with st.spinner("Analizando..."):
                    r = ask_gemini(s, ctx)
                st.session_state.messages.append({"role":"assistant","content":r})
                st.rerun()

    with st.form("chat_f", clear_on_submit=True):
        c1,c2 = st.columns([5,1])
        with c1: ui = st.text_input("Pregunta", label_visibility="collapsed",
                     placeholder="Ej: Dame la estrategia para Bosque San Vicente esta semana...")
        with c2: send = st.form_submit_button("Enviar →")
        if send and ui:
            st.session_state.messages.append({"role":"user","content":ui})
            with st.spinner("Analizando con Gemini..."):
                r = ask_gemini(ui, ctx)
            st.session_state.messages.append({"role":"assistant","content":r})
            st.rerun()

    if st.session_state.messages:
        if st.button("🗑 Limpiar conversación"):
            st.session_state.messages = []
            st.rerun()


# ═══════════════════════════════════════════
# PÁGINA: AUDITORÍA (gerente)
# ═══════════════════════════════════════════
def pg_auditoria():
    header("🔍","Auditoría Comercial","Análisis profundo del equipo y el pipeline")
    df = get_crm()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Proyectos", df.shape[0])
    c2.metric("Pipeline", f"${int(df['totalNum'].sum())/1e9:.2f}B")
    c3.metric("Cotizaciones", df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Rechazados", df[df["estado"]=="perdido"].shape[0])
    c5.metric("Contratos", df[df["estado"]=="cerrado"].shape[0])

    st.markdown("---")
    st.markdown('<div class="al-r">❗ <b>0 contratos cerrados.</b> Con $8.6B en pipeline el cuello de botella está en el proceso de cierre.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-y">⚡ <b>Patrón de rechazo adultos mayores:</b> Inzar VI, El Bosque, y otros. Preparar respuesta estándar con énfasis en teclado PIN físico.</div>', unsafe_allow_html=True)
    st.markdown('<div class="al-g">✅ <b>Oportunidades inmediatas:</b> Nomad (30 abr), Bosque San Vicente (2 mayo), Tiara (1er filtro ok), Olivar (única con financiamiento).</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        res = df[df["totalNum"]>0].groupby("comercial").agg(
            cotiz=("totalNum","count"), pipeline=("totalNum","sum")
        ).reset_index()
        res["Pipeline $M"] = (res["pipeline"]/1e6).round(1)
        st.dataframe(res[["comercial","cotiz","Pipeline $M"]].rename(
            columns={"comercial":"Comercial","cotiz":"Cotiz."}),
            use_container_width=True, hide_index=True)
    with c2:
        if st.button("🤖 Análisis estratégico con IA", use_container_width=True):
            if not st.session_state.gemini_model:
                st.error("Configura Gemini primero")
            else:
                with st.spinner("Analizando..."):
                    r = ask_gemini(
                        "Análisis estratégico completo: 1)Diagnóstico exacto del cuello de botella en cierres. "
                        "2)Top 5 proyectos más cercanos al cierre con acción específica para cada uno. "
                        "3)Patrón de rechazos y cómo resolverlo. 4)Plan de acción 7 días. "
                        "Sin separadores ---. Negrilla para cifras. Tono ejecutivo.",
                        df.to_string(max_rows=84)
                    )
                st.markdown(r)


# ═══════════════════════════════════════════
# PÁGINA: INFORMES (gerente)
# ═══════════════════════════════════════════
def pg_informes():
    header("📈","Informes Gerenciales","Análisis ejecutivo con gráficas y datos reales")
    df = get_crm()
    lm = {"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}

    c1,c2,c3 = st.columns(3)
    with c1:
        dc = df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
        dc["M"]   = (dc["totalNum"]/1e6).round(1)
        dc["Com"] = dc["comercial"].str.split().str[0]
        fig = px.bar(dc.sort_values("M",ascending=True), x="M", y="Com", orientation="h",
                     title="Pipeline por Comercial ($M)", color="M",
                     color_continuous_scale=["#1A9FCC","#00C896"], labels={"M":"$M","Com":""})
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,
                          font_family="Lato",title_font_family="Sora",title_font_size=13,margin=dict(t=40))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        est = df.groupby("estado").size().reset_index(name="n")
        est["Estado"] = est["estado"].map(lm).fillna(est["estado"])
        fig2 = px.pie(est, values="n", names="Estado", hole=0.48,
                      color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"],
                      title="Distribución del Pipeline")
        fig2.update_layout(paper_bgcolor="white",font_family="Lato",title_font_family="Sora",
                           title_font_size=13,margin=dict(t=40))
        st.plotly_chart(fig2, use_container_width=True)
    with c3:
        cr = pd.DataFrame({"Mes":["Dic 2025","Ene 2026","Feb 2026","Mar 2026","Abr 2026"],"Leads":[3,17,25,32,46]})
        fig3 = px.area(cr, x="Mes", y="Leads", title="Crecimiento de Leads",
                       color_discrete_sequence=["#00C896"], markers=True)
        fig3.update_traces(line_width=3,marker_size=8,fill="tozeroy",fillcolor="rgba(0,200,150,0.08)")
        fig3.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Lato",
                           title_font_family="Sora",title_font_size=13,margin=dict(t=40))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1: tipo_i = st.selectbox("Tipo de informe:",["Informe Gerencial Ejecutivo","Reporte Pipeline Comercial","Análisis del Equipo Comercial","Oportunidades Críticas de Cierre","Auditoría Estratégica"])
    with c2: notas_i = st.text_area("Instrucciones adicionales:", height=80, placeholder="Ej: Enfatizar en Nomad y Bosque San Vicente...")

    if st.button("🤖 Generar Informe Completo con IA", use_container_width=True):
        if not st.session_state.gemini_model:
            st.error("Configura Gemini primero en Configuración")
        else:
            prompt = f"""Genera un {tipo_i} COMPLETO y profesional para Ágora Tech Colombia.
{f"Instrucciones: {notas_i}" if notas_i else ""}
Fecha: {datetime.now().strftime("%d de %B de %Y")}

## 1. RESUMEN EJECUTIVO
## 2. MÉTRICAS CLAVE (tabla con cifras exactas)
## 3. ANÁLISIS DETALLADO POR COMERCIAL
## 4. PROYECTOS PRIORITARIOS (top 5 más cercanos al cierre)
## 5. ALERTAS Y RIESGOS
## 6. RECOMENDACIONES ESTRATÉGICAS
## 7. PLAN DE ACCIÓN — PRÓXIMAS 2 SEMANAS

Sin separadores ---. Negrilla para cifras clave. Tono técnico ejecutivo."""
            with st.spinner("Generando informe completo..."):
                r = ask_gemini(prompt, df.to_string(max_rows=84))
            st.markdown(r)
            c1,c2 = st.columns(2)
            c1.download_button("📥 Descargar .md", data=r, file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.md")
            c2.download_button("📥 Descargar .txt", data=r, file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.txt")


# ═══════════════════════════════════════════
# PÁGINA: PIPELINE KANBAN (gerente)
# ═══════════════════════════════════════════
def pg_pipeline():
    header("🎯","Pipeline — Kanban","Vista de embudo comercial por etapas")
    df = mis_proyectos()
    etapas = [("nuevo","🔵 Lead Nuevo"),("cotizado","🟡 Cotización Enviada"),("negociacion","🟠 Negociando"),("cerrado","🟢 Cerrado")]
    cols   = st.columns(4)
    for i,(k,lbl) in enumerate(etapas):
        items = df[df["estado"]==k]
        tot   = int(items["totalNum"].sum())
        with cols[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:11px;color:#8BA3BD;margin-bottom:12px">{len(items)} proy · ${tot/1e6:.1f}M</div>', unsafe_allow_html=True)
            for _,r in items.iterrows():
                tn = int(r.get("totalNum") or 0)
                nota = str(r.get("notas","") or "")
                st.markdown(f"""
                <div class="card card-sm" style="margin-bottom:8px">
                  <div style='font-family:Sora,sans-serif;font-size:11.5px;font-weight:700;color:#04111E;margin-bottom:2px'>
                    {str(r["nombre"])[:24]}</div>
                  <div style='font-size:10.5px;color:#8BA3BD;margin-bottom:4px'>
                    {str(r.get("comercial","—")).split()[0]}</div>
                  <div style='font-family:Sora,sans-serif;font-size:13px;font-weight:800;color:#05875D'>
                    {fc(tn) if tn else "—"}</div>
                  {f'<div style="font-size:10px;color:#8BA3BD;margin-top:4px">{nota[:60]}...</div>' if nota and nota!="nan" and len(nota)>5 else ""}
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PÁGINA: ENCUESTAS (gerente)
# ═══════════════════════════════════════════
def pg_encuestas():
    header("📊","Encuestas de Prospectos","Formulario de información preliminar con análisis IA")
    with st.form("prosp_form"):
        c1,c2 = st.columns(2)
        with c1:
            nom_e  = st.text_input("Nombre del Edificio *")
            dir_e  = st.text_input("Dirección")
            cont_e = st.text_input("Contacto *")
        with c2:
            rol_e   = st.selectbox("Rol",["Administrador","Propietario","Miembro del Consejo","Presidente del Consejo"])
            etapa_e = st.selectbox("Etapa",["Recibiendo cotizaciones por orden de asamblea","No se ha hablado en asamblea","Explorando opciones"])
            com_e   = st.selectbox("Comercial", COMS_LISTA)

        vig_e   = st.radio("¿Tiene vigilancia actual?",["Sí","No"],horizontal=True)
        c1,c2   = st.columns(2)
        with c1: cost_e = st.number_input("Costo vigilancia ($/mes)", min_value=0, value=0, step=100_000, format="%d")
        with c2: vigh_e = st.text_input("Contrato hasta", placeholder="Nov 2026")

        inc_e  = st.text_area("Incidentes de seguridad recientes")
        acc_e  = st.text_area("Adultos mayores / Personas con discapacidad")
        notas_e = st.text_area("Notas del comercial")

        if st.form_submit_button("🤖 Analizar con IA y Guardar", use_container_width=True):
            if not nom_e:
                st.error("Nombre del edificio obligatorio")
            elif not st.session_state.gemini_model:
                st.error("Gemini no está configurado. Ve a Configuración.")
            else:
                prompt = f"""Analiza este prospecto para Ágora Tech Colombia:
Edificio: {nom_e} | Contacto: {cont_e} ({rol_e}) | Etapa: {etapa_e}
Vigilancia: {"SÍ $"+f"{int(cost_e):,}"+"/mes hasta "+vigh_e if vig_e=="Sí" and cost_e>0 else "NO"}
Incidentes: {inc_e or "Ninguno"} | Adultos mayores: {acc_e or "No reportado"} | Comercial: {com_e}

## VIABILIDAD: [ALTA / MEDIA / BAJA — con justificación]
## AHORRO POTENCIAL (si tiene vigilancia)
## ESTRATEGIA DE VENTA RECOMENDADA
## OBJECIONES PROBABLES Y CÓMO RESPONDERLAS
## PRÓXIMOS PASOS CONCRETOS (3 acciones esta semana)

Sin ---. Negrilla para datos clave."""
                with st.spinner("Analizando..."):
                    r = ask_gemini(prompt)
                st.markdown("---")
                st.markdown(r)
                st.success(f"✅ Prospecto {nom_e} analizado y registrado")


# ═══════════════════════════════════════════
# PÁGINA: GESTIÓN DE USUARIOS (gerente)
# ═══════════════════════════════════════════
def pg_usuarios():
    header("👥","Gestión de Usuarios","Agregar, editar y administrar accesos al sistema")
    usuarios = get_usuarios()

    # Tabla de usuarios
    st.markdown("#### Usuarios registrados")
    for ukey, ud in usuarios.items():
        activo = ud.get("activo", True)
        cols = st.columns([2,2,1.5,1,1,1])
        cols[0].markdown(f"**{ud['nombre']}**")
        cols[1].markdown(f"<code>{ukey}</code>", unsafe_allow_html=True)
        cols[2].markdown(ud["rol"].capitalize())
        cols[3].markdown(f'<span class="{"b-g" if activo else "b-r"}">{"Activo" if activo else "Inactivo"}</span>', unsafe_allow_html=True)
        if cols[4].button("✏️", key=f"edit_{ukey}", help="Editar"):
            st.session_state[f"editing_user"] = ukey
        if cols[5].button("🔒" if activo else "🔓", key=f"tog_{ukey}", help="Activar/Desactivar"):
            st.session_state.usuarios_db[ukey]["activo"] = not activo
            st.rerun()
        st.markdown('<div style="border-bottom:1px solid #E3EAF3;margin:6px 0"></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Editar usuario seleccionado
    editing = st.session_state.get("editing_user","")
    if editing and editing in usuarios:
        ud_e = usuarios[editing]
        st.markdown(f"#### ✏️ Editando: {ud_e['nombre']}")
        with st.form("edit_user_form"):
            c1,c2 = st.columns(2)
            with c1:
                new_nombre = st.text_input("Nombre completo", value=ud_e["nombre"])
                new_pass   = st.text_input("Nueva contraseña (dejar vacío para no cambiar)", type="password")
            with c2:
                new_rol    = st.selectbox("Rol", ["gerente","comercial"], index=0 if ud_e["rol"]=="gerente" else 1)
                new_com    = st.selectbox("Comercial asignado", COMS_LISTA, index=COMS_LISTA.index(ud_e["comercial"]) if ud_e["comercial"] in COMS_LISTA else 0)

            if st.form_submit_button("💾 Guardar cambios", use_container_width=True):
                st.session_state.usuarios_db[editing]["nombre"]    = new_nombre
                st.session_state.usuarios_db[editing]["rol"]       = new_rol
                st.session_state.usuarios_db[editing]["comercial"] = new_com
                if new_pass: st.session_state.usuarios_db[editing]["pass"] = new_pass
                st.success(f"✅ Usuario {editing} actualizado")
                st.session_state.pop("editing_user", None)
                st.rerun()

    st.markdown("---")

    # Agregar nuevo usuario
    st.markdown("#### ➕ Agregar nuevo usuario")
    with st.form("add_user_form"):
        c1,c2 = st.columns(2)
        with c1:
            nu_user  = st.text_input("Nombre de usuario *", placeholder="ej: carlos")
            nu_nombre = st.text_input("Nombre completo *", placeholder="Carlos Rodríguez")
            nu_pass  = st.text_input("Contraseña *", type="password")
        with c2:
            nu_rol   = st.selectbox("Rol", ["comercial","gerente"])
            nu_com   = st.selectbox("Comercial asignado", COMS_LISTA)
            nu_activo = st.checkbox("Usuario activo", value=True)

        if st.form_submit_button("➕ Crear usuario", use_container_width=True):
            if not nu_user or not nu_nombre or not nu_pass:
                st.error("Usuario, nombre y contraseña son obligatorios")
            elif nu_user.lower() in usuarios:
                st.error(f"El usuario '{nu_user}' ya existe")
            else:
                st.session_state.usuarios_db[nu_user.lower()] = {
                    "pass": nu_pass, "nombre": nu_nombre,
                    "rol": nu_rol, "comercial": nu_com, "activo": nu_activo
                }
                st.success(f"✅ Usuario **{nu_user}** creado exitosamente")
                st.rerun()


# ═══════════════════════════════════════════
# PÁGINA: CONFIGURACIÓN (gerente)
# ═══════════════════════════════════════════
def pg_configuracion():
    header("⚙️","Configuración del Sistema","API Keys, IA y ajustes de la plataforma")

    st.markdown("#### 🤖 Configurar Gemini IA")
    st.markdown('<div class="al-b">La API Key de Gemini permite usar la IA para correos, análisis y el asistente. Se recomienda configurarla en Streamlit Cloud → Settings → Secrets para que todos la usen automáticamente.</div>', unsafe_allow_html=True)

    ai_ok = st.session_state.gemini_model is not None
    st.markdown(f"**Estado actual:** {'🟢 Gemini activo y funcionando' if ai_ok else '🔴 Gemini no configurado'}")

    with st.form("gemini_form"):
        gkey = st.text_input("API Key de Gemini", type="password",
                              placeholder="AIzaSy...",
                              help="Obtén tu key gratis en: aistudio.google.com/app/apikey")
        if st.form_submit_button("Activar Gemini", use_container_width=True):
            if gkey:
                if init_gemini_key(gkey):
                    st.success("✅ Gemini activado correctamente. Todos los usuarios ya tienen IA disponible en esta sesión.")
                    st.rerun()

    st.markdown("---")
    st.markdown("#### 📋 Para que Gemini funcione siempre (configuración permanente)")
    st.markdown("""
    1. Ve a tu app en **share.streamlit.io**
    2. Clic en **⋮ (tres puntos)** → **Settings** → **Secrets**
    3. Pega esto exactamente:
    """)
    st.code('GEMINI_API_KEY = "AIzaSy-TU-KEY-AQUI"', language="toml")
    st.markdown("""
    4. Clic **Save** — la app se reinicia en 1 minuto
    5. Desde ese momento **todos los usuarios** tienen IA activa automáticamente sin configurar nada
    """)

    st.markdown("---")
    st.markdown("#### 📊 Estado del sistema")
    df = get_crm()
    usuarios = get_usuarios()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Proyectos en CRM", df.shape[0])
    c2.metric("Con valor cotizado", df[df["totalNum"]>0].shape[0])
    c3.metric("Usuarios activos", sum(1 for u in usuarios.values() if u.get("activo",True)))
    c4.metric("IA Gemini", "🟢 Activa" if ai_ok else "🔴 Inactiva")


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
if not st.session_state.logged_in:
    pg_login()
else:
    mostrar_sidebar()
    pg = st.session_state.get("page","Dashboard")

    if   pg == "Dashboard":         pg_dashboard()
    elif pg == "Proyectos":         pg_proyectos()
    elif pg == "Nueva Cotización":  pg_nueva_cotizacion()
    elif pg == "Actualizar Estado": pg_actualizar()
    elif pg == "Edificios":         pg_edificios()
    elif pg == "Calendario":        pg_calendario()
    elif pg == "Correos IA":        pg_correos()
    elif pg == "Asistente IA":      pg_asistente()
    elif pg == "Auditoría":         pg_auditoria()
    elif pg == "Informes":          pg_informes()
    elif pg == "Pipeline Kanban":   pg_pipeline()
    elif pg == "Encuestas":         pg_encuestas()
    elif pg == "Usuarios":          pg_usuarios()
    elif pg == "Configuración":     pg_configuracion()
    else:                           pg_dashboard()
