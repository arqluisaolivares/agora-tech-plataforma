"""
ÁGORA TECH — Plataforma Comercial v5
Gemini AI · Formulario real · Historial · Etapas de ejecución
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import json, os
from datetime import datetime, timedelta
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

# ══════════════════════════════════════════
# GOOGLE SHEETS + PERSISTENCIA SEGURA (JSON como respaldo)
# ══════════════════════════════════════════
@st.cache_resource
def get_worksheet():
    """DIAGNÓSTICO DEFINITIVO - muestra exactamente dónde falla"""
    st.error("🔍 DEBUG: Iniciando conexión a Google Sheets...")

    try:
        # Paso 1: Verificar que el secreto existe
        if "gcp_service_account" not in st.secrets:
            st.error("❌ No existe el secreto 'gcp_service_account'")
            return None
        st.success("✅ Secreto 'gcp_service_account' encontrado")

        creds_info = st.secrets["gcp_service_account"]
        st.success(f"✅ Credenciales cargadas. Claves: {list(creds_info.keys())}")

        # Paso 2: Verificar private_key
        if "private_key" not in creds_info:
            st.error("❌ No hay 'private_key' en el secreto")
            return None
        pk = creds_info["private_key"]
        st.success(f"✅ private_key encontrado (empieza con: {pk[:50]}...)")

        # Paso 3: Crear credenciales
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
        st.success("✅ Credenciales creadas correctamente")

        # Paso 4: Conectar
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1GyvYB7__4XKZicXAUU-nSHIFRVCJNs8oMgNWVpYEaTE"
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet("Hoja 1")
        st.success("✅ ¡CONEXIÓN A GOOGLE SHEETS EXITOSA!")
        return worksheet

    except Exception as e:
        st.error(f"❌ Error real: {type(e).__name__}: {str(e)}")
        import traceback
        st.code(traceback.format_exc(), language="python")
        return None
def cargar_proyectos():
    """Carga desde Google Sheets o fallback a JSON"""
    worksheet = get_worksheet()
    if worksheet is not None:
        try:
            data = worksheet.get_all_records()
            if data:
                df = pd.DataFrame(data)
                for col in ['totalNum', 'c24Num', 'c36Num']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                return df.to_dict('records')
        except:
            pass

    # FALLBACK: JSON local
    base = os.path.dirname(os.path.abspath(__file__))
    for n in ["proyectos.json", "proyectos_v2.json"]:
        ruta = os.path.join(base, n)
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                # Aseguramos que existan las columnas nuevas
                for col in ['historial', 'encuesta', 'contrato', 'financiacion_info', 'obra_inicio', 'obra_fin']:
                    if col not in df.columns:
                        df[col] = ""
                return df.to_dict('records')
    return []

def guardar_crm(df):
    """Versión simple y fuerte - fuerza escribir en Google Sheets"""
    worksheet = get_worksheet()

    if worksheet is None:
        st.error("❌ No se pudo conectar a Google Sheets")
        # fallback local
        try:
            base = os.path.dirname(os.path.abspath(__file__))
            ruta = os.path.join(base, "proyectos.json")
            df.to_json(ruta, orient="records", force_ascii=False, indent=2)
            st.toast("💾 Guardado solo en archivo local", icon="📁")
        except Exception as e:
            st.error(f"❌ Error local: {e}")
        return

    # Intento directo: agregar solo la nueva fila
    try:
        ultima_fila = df.iloc[-1].fillna("").tolist()
        worksheet.append_row(ultima_fila, value_input_option="RAW")
        st.toast("✅ Nueva fila creada correctamente en Google Sheets", icon="✅")
        return
    except Exception as e:
        st.error(f"❌ Error al agregar fila: {str(e)}")

    # Si falla, intenta reemplazar toda la hoja
    try:
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.fillna("").values.tolist())
        st.toast("✅ Guardado correctamente en Google Sheets (reemplazo completo)", icon="✅")
        return
    except Exception as e2:
        st.error(f"❌ Error al reemplazar hoja: {str(e2)}")

    # Último recurso: guardar local
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(base, "proyectos.json")
        df.to_json(ruta, orient="records", force_ascii=False, indent=2)
        st.toast("💾 Guardado en archivo local como respaldo", icon="📁")
    except Exception as e:
        st.error(f"❌ No se pudo guardar: {e}")

# ══════════════════════════════════════════
# USUARIOS PERSISTENTES (JSON)
# ══════════════════════════════════════════
def cargar_usuarios():
    """Carga usuarios desde JSON o usa los default"""
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, "usuarios.json")
    if os.path.exists(ruta):
        try:
            with open(ruta, encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Si no existe, devuelve los default
    return dict(USUARIOS_DEFAULT)

def guardar_usuarios():
    """Guarda los usuarios en JSON"""
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(base, "usuarios.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(st.session_state.usuarios_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error al guardar usuarios: {e}")

# ══════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════
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
        st.session_state.usuarios_db = cargar_usuarios()
    return st.session_state.usuarios_db

# ══════════════════════════════════════════
# ETAPAS DEL PIPELINE — COMPLETO
# ══════════════════════════════════════════
ETAPAS = {
    # Comercial
    "lead":           {"label":"🔵 Lead",            "grupo":"Comercial",  "color":"#DBEAFE"},
    "cotizado":       {"label":"🟡 Cotización",       "grupo":"Comercial",  "color":"#FEF9C3"},
    "negociacion":    {"label":"🟠 Negociando",       "grupo":"Comercial",  "color":"#FED7AA"},
    "aprobado":       {"label":"🟣 Aprobado",         "grupo":"Comercial",  "color":"#EDE9FE"},
    "perdido":        {"label":"🔴 Perdido",          "grupo":"Comercial",  "color":"#FEE2E2"},
    # Cierre y ejecución
    "creacion_contrato": {"label":"📝 Creación Contrato", "grupo":"Ejecución", "color":"#F0FDF9"},
    "financiacion":   {"label":"💰 Financiación",    "grupo":"Ejecución",  "color":"#F0FDF9"},
    "obra":           {"label":"🔨 En Obra",          "grupo":"Ejecución",  "color":"#ECFDF5"},
    "novedades_obra": {"label":"⚠️ Novedades Obra",   "grupo":"Ejecución",  "color":"#FFFBEB"},
    "entrega":        {"label":"🎉 Entrega",          "grupo":"Ejecución",  "color":"#D1FAF0"},
    "mantenimiento":  {"label":"🔧 Mantenimiento",   "grupo":"Posventa",   "color":"#EFF6FF"},
    "cerrado":        {"label":"✅ Cerrado",          "grupo":"Posventa",   "color":"#D1FAF0"},
}
ESTADOS_LISTA = list(ETAPAS.keys())

def badge(estado):
    e = ETAPAS.get(estado, {"label":estado,"color":"#F1F5F9"})
    return f'<span style="background:{e["color"]};padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:700;display:inline-block">{e["label"]}</span>'

COMS = ["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"]

# ══════════════════════════════════════════
# CONFIG STREAMLIT
# ══════════════════════════════════════════
st.set_page_config(page_title="Ágora Tech", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Lato:wght@300;400;700&display=swap');
html,body,[class*="css"]{font-family:'Lato',sans-serif!important}
h1,h2,h3{font-family:'Sora',sans-serif!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#04111E 0%,#0A2540 100%)!important}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.85)!important}
.stButton>button{background:linear-gradient(135deg,#00C896,#1A9FCC)!important;color:#04111E!important;
  font-family:'Sora',sans-serif!important;font-weight:700!important;border:none!important;border-radius:8px!important;transition:all .18s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,200,150,.4)!important}
.stButton>button[kind="secondary"]{background:white!important;color:#04111E!important;border:1px solid #E3EAF3!important;box-shadow:none!important;transform:none!important}
.kpi{background:white;border:1px solid #E3EAF3;border-radius:12px;padding:18px 20px;box-shadow:0 1px 6px rgba(4,17,30,.05);position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#00C896,#1A9FCC)}
.kpi-label{font-size:10px;font-weight:700;color:#8BA3BD;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px}
.kpi-val{font-family:'Sora',sans-serif;font-size:24px;font-weight:800;color:#04111E;line-height:1}
.kpi-val.g{color:#05875D}.kpi-val.r{color:#E84040}.kpi-val.o{color:#D97706}
.kpi-sub{font-size:11px;color:#8BA3BD;margin-top:5px}
.al-r{background:#FEF2F2;border-left:3px solid #E84040;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.al-y{background:#FFFBEB;border-left:3px solid #D97706;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.al-g{background:#F0FDF9;border-left:3px solid #00C896;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.al-b{background:#EFF6FF;border-left:3px solid #1A9FCC;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.chat-u{background:linear-gradient(135deg,#00C896,#1A9FCC);color:#04111E;padding:12px 16px;border-radius:16px 16px 3px 16px;margin:8px 0;font-weight:600;max-width:80%;margin-left:auto;display:block}
.chat-a{background:white;border:1px solid #E3EAF3;padding:14px 18px;border-radius:16px 16px 16px 3px;margin:8px 0;max-width:90%;box-shadow:0 1px 6px rgba(4,17,30,.06);line-height:1.75;display:block}
.hist-item{background:#F6F9FC;border-left:3px solid #00C896;border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:8px;font-size:13px}
.hist-date{font-size:10px;color:#8BA3BD;margin-bottom:4px;font-weight:700}
.grupo-tag{font-size:9px;font-weight:700;color:#8BA3BD;text-transform:uppercase;letter-spacing:1.5px;margin:16px 0 6px;display:block}
div[data-testid="stForm"]{border:none!important;padding:0!important}
[data-testid="stSidebar"] .stButton>button{background:transparent!important;color:rgba(255,255,255,.6)!important;font-weight:500!important;border:none!important;box-shadow:none!important;border-radius:8px!important;text-align:left!important;font-size:13px!important;transform:none!important}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.08)!important;color:white!important}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# IA — GROQ (más rápida y estable)
# ══════════════════════════════════════════
def get_ai_key():
    return st.secrets.get("GROQ_API_KEY", st.session_state.get("groq_key", ""))

def ai_activa():
    return bool(get_ai_key())

def activar_ia(key):
    key = key.strip()
    if not key:
        st.error("Pega tu API Key de Groq")
        return False
    st.session_state["groq_key"] = key
    st.success("✅ ¡Groq activado correctamente!")
    return True

def ask_ai(q, ctx=""):
    key = get_ai_key()
    if not key:
        return "⚠️ IA no configurada. Ve a ⚙️ Configuración y pega tu clave de Groq."
    try:
        from groq import Groq
        client = Groq(api_key=key)
        
        full_prompt = f"""Eres el asistente comercial experto de Ágora Tech Colombia.

CONTEXTO COMPLETO DEL CRM (proyectos, estados, notas, pipeline):
{ctx if ctx else "No hay datos de proyectos disponibles."}

SOLICITUD DEL USUARIO:
{q}

Responde en español colombiano, sé concreto, accionable y usa los datos reales del contexto (estados, notas, comerciales, valores, etc.)."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error temporal con Groq: {str(e)}\n\nPuedes seguir usando la app normalmente."
        
# ══════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════
def init():
    defaults = {"logged_in":False,"user":None,"page":"Dashboard","messages":[],"crm":None,"correo":"","editing":"","encuesta_resultado":{}}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init()

# Cargar key de secrets al inicio
if not st.session_state.get("gemini_key"):
    try:
        k = st.secrets.get("GEMINI_API_KEY","") or st.secrets.get("GOOGLE_API_KEY","")
        if k: st.session_state["gemini_key"] = k
    except: pass

# ══════════════════════════════════════════
# CRM CON HISTORIAL
# ══════════════════════════════════════════
def get_crm():
    if st.session_state.crm is None:
        rows = cargar_proyectos()                    # ← Ahora lee de Google Sheets
        st.session_state.crm = pd.DataFrame(rows)
    return st.session_state.crm

def mis_proyectos():
    df = get_crm()
    u = st.session_state.user
    if not u: return df.iloc[0:0]
    if u["rol"]=="gerente": return df
    return df[df["comercial"].str.upper()==u["comercial"].upper()]

def update_proy(nombre, campos):
    df = get_crm()
    mask = df["nombre"] == nombre
    if mask.any():
        for k, v in campos.items():
            df.loc[mask, k] = v
        st.session_state.crm = df
        guardar_crm(st.session_state.crm)   # ← GUARDA EN LA NUBE

def agregar_historial(nombre, estado, nota, usuario):
    """Agrega un evento al historial del proyecto."""
    df = get_crm()
    mask = df["nombre"] == nombre
    if not mask.any():
        return
    hist_raw = str(df.loc[mask, "historial"].iloc[0] or "[]")
    try:
        hist = json.loads(hist_raw)
    except:
        hist = []
    hist.append({
        "fecha": datetime.now().strftime("%d %b %Y %H:%M"),
        "estado": estado,
        "nota": nota,
        "usuario": usuario
    })
    df.loc[mask, "historial"] = json.dumps(hist, ensure_ascii=False)
    df.loc[mask, "lastNote"] = nota
    df.loc[mask, "lastUpdate"] = datetime.now().isoformat()
    df.loc[mask, "estado"] = estado
    st.session_state.crm = df
    guardar_crm(st.session_state.crm)   # ← GUARDA EN LA NUBE

def add_proy(datos):
    df = get_crm()
    st.session_state.crm = pd.concat([pd.DataFrame([datos]), df], ignore_index=True)
    guardar_crm(st.session_state.crm)   # ← GUARDA EN LA NUBE

def fc(n):
    try:
        n=int(float(n or 0))
        return "$0" if n==0 else "$"+f"{n:,}".replace(",",".")
    except: return "$0"

def hdr(icon, title, sub=""):
    st.markdown(f"""<div style='display:flex;align-items:center;gap:14px;margin-bottom:24px;
      padding-bottom:16px;border-bottom:1px solid #E3EAF3'>
      <div style='width:42px;height:42px;border-radius:10px;
        background:linear-gradient(135deg,#00C896,#1A9FCC);display:flex;
        align-items:center;justify-content:center;font-size:20px;flex-shrink:0'>{icon}</div>
      <div><div style='font-family:Sora,sans-serif;font-size:20px;font-weight:700;color:#04111E'>{title}</div>
        {'<div style="font-size:12px;color:#8BA3BD;margin-top:2px">'+sub+'</div>' if sub else ''}</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# DASHBOARD CON NÚMEROS CLAROS
# ══════════════════════════════════════════
def pg_dashboard():
    u = st.session_state.user
    es_g = u["rol"] == "gerente"
    df = mis_proyectos()

    # Cálculos
    total_edificios = len(df)
    activos = len(df[~df["estado"].isin(["perdido", "cerrado"])])
    cotizados = len(df[df["estado"] == "cotizado"])
    contacto_frio = len(df[df["estado"] == "lead"])
    por_contactar = len(df[df["estado"].isin(["cotizado", "negociacion", "aprobado"])])

    # Header
    st.markdown(f"""<div style='background:linear-gradient(135deg,#04111E 0%,#0A2540 100%);
      border-radius:14px;padding:28px 32px;margin-bottom:24px;color:white'>
      <div style='font-family:Sora,sans-serif;font-size:24px;font-weight:800'>
        Dashboard · {datetime.now().strftime("%d %B %Y")}
      </div>
    </div>""", unsafe_allow_html=True)

    # Resumen General
    st.markdown("### Resumen General")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div style="text-align:center"><div style="font-size:48px;font-weight:800;color:#04111E">{total_edificios}</div><div style="font-size:16px;font-weight:700;color:#8BA3BD">Total Edificios</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div style="text-align:center"><div style="font-size:48px;font-weight:800;color:#04111E">{activos}</div><div style="font-size:16px;font-weight:700;color:#8BA3BD">Activos</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div style="text-align:center"><div style="font-size:48px;font-weight:800;color:#04111E">{cotizados}</div><div style="font-size:16px;font-weight:700;color:#8BA3BD">Cotizados</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div style="text-align:center"><div style="font-size:48px;font-weight:800;color:#04111E">{contacto_frio}</div><div style="font-size:16px;font-weight:700;color:#8BA3BD">Contacto Frío</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div style="text-align:center"><div style="font-size:48px;font-weight:800;color:#04111E">{por_contactar}</div><div style="font-size:16px;font-weight:700;color:#8BA3BD">Por Contactar</div></div>', unsafe_allow_html=True)

    # Gráficas
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        grupos = {"Comercial":["lead","cotizado","negociacion","aprobado","perdido"],
                  "Ejecución":["creacion_contrato","financiacion","obra","novedades_obra","entrega"],
                  "Posventa":["mantenimiento","cerrado"]}
        est_data = [{"Grupo":g, "Cantidad":len(df[df["estado"].isin(e)])} for g,e in grupos.items()]
        fig = px.bar(pd.DataFrame(est_data), x="Grupo", y="Cantidad", title="Proyectos por Etapa", 
                     color="Grupo", color_discrete_map={"Comercial":"#1A9FCC","Ejecución":"#00C896","Posventa":"#8B5CF6"})
        st.plotly_chart(fig, use_container_width=True)

    with col_g2:
        cot_por_com = df[df["estado"] == "cotizado"].groupby("comercial").size().reset_index(name="Cantidad")
        cot_por_com = cot_por_com.sort_values("Cantidad", ascending=False)
        fig2 = px.bar(cot_por_com, x="Cantidad", y="comercial", orientation="h",
                      title="Cotizaciones Entregadas por Comercial", 
                      color="Cantidad", color_continuous_scale=["#00C896","#1A9FCC"])
        st.plotly_chart(fig2, use_container_width=True)

    # Alertas por Comercial
    st.markdown("### 🚨 Alertas por Comercial")
    if es_g:
        for com in sorted(df["comercial"].unique()):
            proy_com = df[df["comercial"] == com]
            alertas = proy_com[proy_com["estado"].isin(["cotizado", "negociacion", "aprobado"])]
            with st.expander(f"**{com}** — {len(proy_com)} proyectos", expanded=True):
                if len(alertas) > 0:
                    for _, r in alertas.head(3).iterrows():
                        st.markdown(f'<div class="al-y">⚡ <strong>{r["nombre"]}</strong> — {ETAPAS.get(r["estado"],{}).get("label","")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="al-g">✅ Sin alertas pendientes</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="al-y">⚡ Revisa tus proyectos pendientes</div>', unsafe_allow_html=True)

    # Top 5 urgentes
    st.markdown("### 🔥 Proyectos que necesitan atención inmediata")
    urgentes = df[df["estado"].isin(["cotizado", "negociacion", "aprobado"])].copy()
    if not urgentes.empty:
        urgentes = urgentes.sort_values("lastUpdate", ascending=True).head(5)
        for _, r in urgentes.iterrows():
            st.markdown(f"""
            <div style="background:#FEF2F2;border-left:5px solid #E84040;padding:14px 18px;border-radius:8px;margin-bottom:10px">
                <strong>{r.get('nombre')}</strong> — {r.get('comercial','')} 
                <span style="color:#E84040">• {ETAPAS.get(r['estado'],{}).get('label','')}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.success("✅ No hay proyectos urgentes en este momento.")
        
# ══════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════
def pg_login():
    c1,c2,c3=st.columns([1,1.2,1])
    with c2:
        st.markdown("""<div style='text-align:center;padding:48px 0 28px'>
          <div style='font-family:Sora,sans-serif;font-size:11px;font-weight:700;color:#8BA3BD;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px'>SISTEMA COMERCIAL</div>
          <div style='font-family:Sora,sans-serif;font-size:36px;font-weight:800;color:#04111E;letter-spacing:-2px'>ÁGORA TECH</div>
          <div style='width:40px;height:3px;background:linear-gradient(90deg,#00C896,#1A9FCC);margin:14px auto;border-radius:2px'></div>
          <div style='font-size:13px;color:#8BA3BD'>Plataforma de Gestión Comercial</div>
        </div>""", unsafe_allow_html=True)
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="rafael / sonia / lina / luisa...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            if st.form_submit_button("Ingresar a la plataforma", use_container_width=True):
                u=usuario.strip().lower(); usuarios=get_usuarios()
                if u in usuarios and usuarios[u]["activo"] and usuarios[u]["pass"]==password:
                    st.session_state.logged_in=True; st.session_state.user=usuarios[u]; st.rerun()
                else: st.error("Usuario o contraseña incorrectos")
        
# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
def sidebar():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; ai_ok=ai_activa()
    with st.sidebar:
        st.markdown(f"""<div style='padding:18px 16px 12px'>
          <div style='font-family:Sora,sans-serif;font-size:16px;font-weight:800;color:#fff'>ÁGORA TECH</div>
          <div style='font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;text-transform:uppercase;margin-top:2px'>Plataforma Comercial</div>
        </div>
        <div style='background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.2);border-radius:10px;padding:10px 14px;margin:0 12px 14px'>
          <div style='font-size:13px;font-weight:600;color:#fff'>{u["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:1px'>{u["rol"].capitalize()} · {"🟢 IA activa" if ai_ok else "🔴 IA — ve a ⚙️"}</div>
        </div>""", unsafe_allow_html=True)

        nav_todos=[("📊","Dashboard"),("📋","Proyectos"),("🧮","Nueva Cotización"),
                   ("📝","Actualizar Estado"),("🏢","Edificios"),("📅","Calendario"),
                   ("✉️","Correos IA"),("🤖","Asistente IA"),("📊","Encuesta Prospecto"),("⚙️","Configuración")]
        nav_gerente=[("🔍","Auditoría"),("📈","Informes"),("🎯","Pipeline"),("👥","Usuarios")]
        todas=nav_todos+(nav_gerente if es_g else [])

        for icono,nombre in todas:
            activo=st.session_state.page==nombre
            if activo: st.markdown('<div style="background:rgba(0,200,150,.15);border:1px solid rgba(0,200,150,.3);border-radius:8px;margin-bottom:2px">',unsafe_allow_html=True)
            if st.button(f"{icono}  {nombre}",key=f"nav_{nombre}",use_container_width=True):
                st.session_state.page=nombre; st.rerun()
            if activo: st.markdown('</div>',unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Cerrar sesión",use_container_width=True,key="logout"):
            for k in ["logged_in","user","messages","page","crm","correo","editing"]:
                st.session_state.pop(k,None)
            st.rerun()

# ══════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════
def ask_ai(q, ctx=""):
    key = get_ai_key()
    if not key:
        return "⚠️ IA no configurada. Ve a ⚙️ Configuración y pega tu clave de Groq."
    try:
        from groq import Groq
        client = Groq(api_key=key)
        
        full_context = f"""CONTEXTO COMPLETO DEL CRM (usa esta información siempre):
{ctx if ctx else "Sin datos de proyectos disponibles."}

SOLICITUD DEL USUARIO: {q}

Responde en español colombiano, sé muy concreto, usa los nombres de los edificios, estados reales, valores y notas recientes cuando sea relevante."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_context}],
            temperature=0.7,
            max_tokens=1600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error temporal con Groq: {str(e)}\n\nPuedes seguir usando la app normalmente."
def pg_proyectos():
    es_g=st.session_state.user["rol"]=="gerente"; df=mis_proyectos()
    hdr("📋","Proyectos","Pipeline comercial y ejecución completo")

    # Filtros
    c1,c2,c3,c4=st.columns([2,1,1,1])
    with c1: buscar=st.text_input("🔍 Buscar",placeholder="Nombre del edificio...")
    with c2:
        grupos_filter=["Todos","Comercial","Ejecución","Posventa"]
        filtro_g=st.selectbox("Grupo",grupos_filter)
    with c3:
        if es_g: filtro_c=st.selectbox("Comercial",["Todos"]+sorted(df["comercial"].dropna().unique().tolist()))
        else: filtro_c="Todos"
    with c4: filtro_e=st.selectbox("Estado",["Todos"]+ESTADOS_LISTA)

    dff=df.copy()
    if buscar: dff=dff[dff["nombre"].str.contains(buscar,case=False,na=False)]
    if filtro_g!="Todos":
        estados_del_grupo=[k for k,v in ETAPAS.items() if v["grupo"]==filtro_g]
        dff=dff[dff["estado"].isin(estados_del_grupo)]
    if filtro_c!="Todos": dff=dff[dff["comercial"]==filtro_c]
    if filtro_e!="Todos": dff=dff[dff["estado"]==filtro_e]

    st.markdown(f'<div style="font-size:12px;color:#8BA3BD;margin-bottom:12px">{len(dff)} proyectos</div>',unsafe_allow_html=True)

    for _,r in dff.iterrows():
        tn=int(r.get("totalNum") or 0); total=fc(tn) if tn else r.get("total","$0") or "$0"
        c24=fc(int(r.get("c24Num") or 0)) if tn else "—"
        c36=fc(int(r.get("c36Num") or 0)) if tn else "—"
        est=str(r.get("estado","lead"))
        nota=str(r.get("lastNote","") or r.get("notas","") or "")
        drive=str(r.get("drive","") or "")

        with st.expander(f"🏢  {r['nombre']}   {badge(est)}   {total}   {r.get('comercial','')}",expanded=False):
            tab_info,tab_hist,tab_ejec=st.tabs(["📋 Información","📜 Historial","🔧 Ejecución"])

            with tab_info:
                m1,m2,m3,m4=st.columns(4)
                m1.metric("Valor",total); m2.metric("Cuota 24m",c24)
                m3.metric("Cuota 36m",c36)
                m4.markdown(f"**Estado:**<br>{badge(est)}",unsafe_allow_html=True)
                if nota and nota!="nan":
                    st.markdown(f'<div class="al-b" style="font-size:12px">📝 {nota[:400]}</div>',unsafe_allow_html=True)
                if drive.startswith("http"):
                    st.markdown(f'📁 <a href="{drive}" target="_blank">Ver en Drive</a>',unsafe_allow_html=True)
                b1,b2,b3=st.columns(3)
                if b1.button("📝 Actualizar",key=f"u_{r.get('id',r['nombre'])}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()
                if b2.button("✉️ Correo IA",key=f"c_{r.get('id',r['nombre'])}"):
                    st.session_state.page="Correos IA"; st.rerun()
                if b3.button("📊 Encuesta",key=f"enc_{r.get('id',r['nombre'])}"):
                    st.session_state.editing=r["nombre"]; st.session_state.page="Encuesta Prospecto"; st.rerun()

            with tab_hist:
                hist_raw=str(r.get("historial","") or "[]")
                try: hist=json.loads(hist_raw)
                except: hist=[]
                if hist:
                    for evento in reversed(hist):
                        st.markdown(f"""<div class="hist-item">
                          <div class="hist-date">{evento.get("fecha","")} · {evento.get("usuario","")} · {ETAPAS.get(evento.get("estado",""),{"label":evento.get("estado","")})["label"]}</div>
                          <div>{evento.get("nota","")}</div>
                        </div>""",unsafe_allow_html=True)
                else:
                    st.info("Sin historial registrado aún.")

                # Ver encuesta si existe
                enc_raw=str(r.get("encuesta","") or "{}")
                try: enc=json.loads(enc_raw)
                except: enc={}
                if enc:
                    st.markdown("**📊 Encuesta de prospecto:**")
                    for campo,valor in enc.items():
                        if valor: st.markdown(f"- **{campo}:** {valor}")

            with tab_ejec:
                grupo_actual=ETAPAS.get(est,{}).get("grupo","Comercial")
                if grupo_actual in ["Ejecución","Posventa"]:
                    cont_raw=str(r.get("contrato","") or "")
                    fin_raw=str(r.get("financiacion_info","") or "")
                    obra_ini=str(r.get("obra_inicio","") or "")
                    obra_fin=str(r.get("obra_fin","") or "")

                    c1,c2=st.columns(2)
                    with c1:
                        st.markdown("**Contrato:**")
                        if cont_raw: st.markdown(cont_raw)
                        else: st.caption("Sin información de contrato")
                        st.markdown("**Financiación:**")
                        if fin_raw: st.markdown(fin_raw)
                        else: st.caption("Sin información de financiación")
                    with c2:
                        st.markdown("**Fechas de obra:**")
                        if obra_ini: st.markdown(f"Inicio: **{obra_ini}**")
                        if obra_fin: st.markdown(f"Fin estimado: **{obra_fin}**")
                        if not obra_ini and not obra_fin: st.caption("Sin fechas de obra")
                else:
                    st.info("Este proyecto aún está en etapa comercial. Las fechas de ejecución se activarán cuando avance a 'Creación Contrato'.")

def pg_actualizar():
    hdr("📝","Actualizar Estado","Registro de seguimiento con historial completo")
    df=mis_proyectos(); u=st.session_state.user
    presel=st.session_state.get("editing","")
    nombres=["— Selecciona un edificio —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx=nombres.index(presel) if presel in nombres else 0
    sel=st.selectbox("Edificio:",nombres,index=idx)

    if sel!="— Selecciona un edificio —":
        r=df[df["nombre"]==sel].iloc[0]
        est_actual=str(r.get("estado","lead"))

        c1,c2,c3,c4=st.columns(4)
        c1.metric("Valor",fc(int(r.get("totalNum") or 0)))
        c2.metric("Comercial",str(r.get("comercial","—")))
        c3.metric("Estado actual",ETAPAS.get(est_actual,{"label":est_actual})["label"])
        c4.metric("Última actualización",str(r.get("lastUpdate","Nunca"))[:10] or "Nunca")

        if r.get("lastNote"):
            st.markdown(f'<div class="al-b" style="font-size:12px">📝 Última nota: {str(r["lastNote"])[:200]}</div>',unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Registrar actualización")

        # Separar etapas por grupo
        col1,col2=st.columns(2)
        with col1:
            st.markdown('<span class="grupo-tag">Etapas Comerciales</span>',unsafe_allow_html=True)
            etapas_com=[e for e,v in ETAPAS.items() if v["grupo"]=="Comercial"]
            est_com_labels=[ETAPAS[e]["label"] for e in etapas_com]
            idx_com=etapas_com.index(est_actual) if est_actual in etapas_com else 0
        with col2:
            st.markdown('<span class="grupo-tag">Etapas de Ejecución y Posventa</span>',unsafe_allow_html=True)
            etapas_ejec=[e for e,v in ETAPAS.items() if v["grupo"] in ["Ejecución","Posventa"]]
            est_ejec_labels=[ETAPAS[e]["label"] for e in etapas_ejec]

        with st.form("upd_form"):
            nuevo_e=st.selectbox("Nuevo estado *",
                options=ESTADOS_LISTA,
                format_func=lambda x: ETAPAS.get(x,{"label":x})["label"],
                index=ESTADOS_LISTA.index(est_actual) if est_actual in ESTADOS_LISTA else 0)
            nota=st.text_area("Nota de seguimiento * (obligatoria)",
                              placeholder="¿Qué pasó? ¿Cuál es el próximo paso? ¿Quién respondió?...")

            # Campos adicionales para etapas de ejecución
            if nuevo_e in ["creacion_contrato","financiacion","obra","novedades_obra","entrega","mantenimiento","cerrado"]:
                st.markdown("**Información de ejecución:**")
                ec1,ec2=st.columns(2)
                with ec1:
                    contrato=st.text_input("Número/referencia del contrato",placeholder="CT-2025-001")
                    financiacion=st.text_area("Detalles de financiación",placeholder="Banco, plazo, cuotas...",height=80)
                with ec2:
                    obra_ini=st.text_input("Fecha inicio de obra",placeholder="15 jun 2025")
                    obra_fin=st.text_input("Fecha fin estimada",placeholder="25 jul 2025 (40 días)")
            else:
                contrato=financiacion=obra_ini=obra_fin=""

            if st.form_submit_button("✅ Guardar y registrar en historial",use_container_width=True):
                if not nota.strip():
                    st.error("La nota de seguimiento es obligatoria")
                else:
                    # Guardar en historial
                    agregar_historial(sel, nuevo_e, nota, u["nombre"])
                    # Campos adicionales
                    extras={}
                    if contrato: extras["contrato"]=contrato
                    if financiacion: extras["financiacion_info"]=financiacion
                    if obra_ini: extras["obra_inicio"]=obra_ini
                    if obra_fin: extras["obra_fin"]=obra_fin
                    if extras: update_proy(sel,extras)
                    st.success(f"✅ **{sel}** → {ETAPAS.get(nuevo_e,{'label':nuevo_e})['label']} — guardado en historial")
                    st.session_state.editing=""; st.rerun()

def pg_nueva_cotizacion():
    hdr("🧮","Nueva Cotización","Registrar en el CRM")

    with st.form("form_cot"):
        st.markdown("**Datos del edificio**")
        c1,c2=st.columns(2)
        with c1:
            nombre=st.text_input("Nombre del edificio *",placeholder="Ej: Edificio Altos del Pino")
            contacto=st.text_input("Contacto *",placeholder="Juan Pérez — Administrador")
            email=st.text_input("Email de contacto")
        with c2:
            direccion=st.text_input("Dirección")
            drive_url=st.text_input("Link carpeta Drive (opcional)")

        st.markdown("---")
        st.markdown("**Cotización**")
        c1,c2,c3,c4=st.columns(4)
        with c1:
            valor=st.number_input("Valor total ($)",min_value=0,value=0,step=1_000_000,format="%d")
        with c2:
            cuota24=st.number_input("Cuota 24 meses ($)",min_value=0,value=0,step=10_000,format="%d")
        with c3:
            cuota36=st.number_input("Cuota 36 meses ($)",min_value=0,value=0,step=10_000,format="%d")
        with c4:
            version=st.text_input("Versión",value="v1")

        notas=st.text_area("Observaciones iniciales",placeholder="Contexto, cómo llegó el lead, próximos pasos...")

        if st.form_submit_button("💾 Guardar en CRM",use_container_width=True):
            if not nombre:
                st.error("El nombre del edificio es obligatorio")
            else:
                u=st.session_state.user
                
                # Guardamos los valores numéricos
                c24n = cuota24
                c36n = cuota36
                
                nuevo_id=int(datetime.now().timestamp())
                hist_inicial=json.dumps([{
                    "fecha":datetime.now().strftime("%d %b %Y %H:%M"),
                    "estado":"cotizado",
                    "nota":notas or "Cotización entregada",
                    "usuario":u["nombre"]
                }],ensure_ascii=False)

                add_proy({
                    "id":nuevo_id,
                    "nombre":nombre.upper(),
                    "comercial":u["comercial"],
                    "contacto":contacto,
                    "email":email,
                    "total":fc(valor),
                    "totalNum":valor,
                    "cuota24":fc(c24n),
                    "cuota36":fc(c36n),
                    "c24Num":c24n,
                    "c36Num":c36n,
                    "estado":"cotizado",          # ← Oferta ya entregada
                    "etapaOrig":"cotizado",
                    "version":version,
                    "notas":notas,
                    "lastUpdate":datetime.now().isoformat(),
                    "lastNote":notas[:100] if notas else "Cotización entregada",
                    "fecha":datetime.now().strftime("%d %b %Y"),
                    "drive":drive_url,
                    "historial":hist_inicial,
                    "encuesta":"",
                    "contrato":"",
                    "financiacion_info":"",
                    "obra_inicio":"",
                    "obra_fin":""
                })
                st.success(f"✅ **{nombre}** guardado como **cotizado** — ${valor/1e6:.1f}M")
                st.balloons()

def pg_edificios():
    hdr("🏢", "Edificios", "Selecciona un edificio para ver detalle completo")

    df = mis_proyectos()
    if df.empty:
        st.info("No hay edificios registrados aún.")
        return

    # Filtros
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1.5, 1.5, 1.5])
    with col_f1:
        buscar = st.text_input("🔍 Buscar por nombre", placeholder="Nombre del edificio...")
    with col_f2:
        comercial_filter = st.selectbox("Comercial", ["Todos"] + sorted(df["comercial"].dropna().unique().tolist()))
    with col_f3:
        estado_filter = st.selectbox("Estado", ["Todos"] + list(ETAPAS.keys()))
    with col_f4:
        df["mes"] = pd.to_datetime(df.get("lastUpdate", pd.NaT), errors='coerce').dt.strftime("%Y-%m")
        mes_filter = st.selectbox("Mes", ["Todos"] + sorted(df["mes"].dropna().unique().tolist()))

    # Aplicar filtros
    dff = df.copy()
    if buscar:
        dff = dff[dff["nombre"].str.contains(buscar, case=False, na=False)]
    if comercial_filter != "Todos":
        dff = dff[dff["comercial"] == comercial_filter]
    if estado_filter != "Todos":
        dff = dff[dff["estado"] == estado_filter]
    if mes_filter != "Todos":
        dff = dff[dff["mes"] == mes_filter]

    col_list, col_detail = st.columns([2, 3])

    with col_list:
        st.markdown(f"**{len(dff)} proyectos**")
        
        for _, r in dff.iterrows():
            nombre = r["nombre"]
            comercial = r.get("comercial", "—")
            valor = fc(int(r.get("totalNum", 0)))
            estado = str(r.get("estado", "lead"))
            estado_label = ETAPAS.get(estado, {}).get("label", estado)

            # Tarjeta limpia y moderna
            if st.button(f"""
                **{nombre}**  
                {comercial}  
                {valor} • {estado_label}
            """, key=f"edif_{r.name}", use_container_width=True):
                st.session_state.edificio_seleccionado = nombre

    # ====================== PANEL DETALLE ======================
    with col_detail:
        seleccionado = st.session_state.get("edificio_seleccionado")

        if seleccionado:
            r = df[df["nombre"] == seleccionado].iloc[0]
            estado = str(r.get("estado", "lead"))

            st.markdown(f"""
            <div style="background:#0F172A; color:white; padding:28px; border-radius:16px; margin-bottom:24px;">
                <h2 style="margin:0; color:white;">{seleccionado}</h2>
                <p style="margin:12px 0 0 0; opacity:0.9;">{r.get('comercial','—')} • {ETAPAS.get(estado,{}).get('label', estado)}</p>
            </div>
            """, unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📋 Información", "📜 Historial", "🤖 Sugerencia IA"])

            with tab1:
                c1, c2, c3 = st.columns(3)
                c1.metric("Valor Total", fc(int(r.get("totalNum", 0))))
                c2.metric("Cuota 24m", fc(int(r.get("c24Num", 0))))
                c3.metric("Cuota 36m", fc(int(r.get("c36Num", 0))))

                st.write(f"**Contacto:** {r.get('contacto','—')}")
                if r.get("email"): st.write(f"**Email:** {r.get('email')}")
                if r.get("drive"):
                    st.markdown(f"[📁 Abrir carpeta en Drive]({r.get('drive')})")

            with tab2:
                hist_raw = str(r.get("historial", "[]"))
                try: hist = json.loads(hist_raw)
                except: hist = []
                if hist:
                    for h in reversed(hist[-8:]):
                        st.markdown(f"""
                        <div style="background:#F8FAFC; padding:16px; border-radius:12px; margin-bottom:12px;">
                            <small>{h.get('fecha')} • {h.get('usuario')}</small><br>
                            <strong>{ETAPAS.get(h.get('estado'),{}).get('label')}</strong><br>
                            {h.get('nota')}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Sin historial registrado.")

            with tab3:
                if ai_activa():
                    with st.spinner("Generando sugerencia..."):
                        prompt = f"Edificio: {seleccionado}\nEstado: {ETAPAS.get(estado,{}).get('label')}\nValor: {fc(int(r.get('totalNum',0)))}\nSugerencia concreta."
                        sug = ask_ai(prompt)
                    st.markdown(sug)
                else:
                    st.warning("Activa la IA en Configuración")

            c1, c2, c3 = st.columns(3)
            if c1.button("📝 Actualizar Estado", use_container_width=True, type="primary"):
                st.session_state.editing = seleccionado
                st.session_state.page = "Actualizar Estado"
                st.rerun()
            if c2.button("✉️ Generar Correo", use_container_width=True):
                st.session_state.page = "Correos IA"
                st.rerun()
            if c3.button("📊 Encuesta", use_container_width=True):
                st.session_state.editing = seleccionado
                st.session_state.page = "Encuesta Prospecto"
                st.rerun()

        else:
            st.info("👈 Selecciona un edificio de la lista para ver su detalle completo.")
            


def pg_correos():
    hdr("✉️","Correos IA","Genera correos comerciales personalizados")

    df = mis_proyectos()
    if not ai_activa():
        st.markdown('<div class="al-r">⚠️ <b>IA no configurada.</b> Ve a ⚙️ Configuración.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        edif_sel = st.selectbox("Edificio", ["— Seleccionar —"] + sorted(df["nombre"].dropna().unique().tolist()))
        tipo_c = st.selectbox("Tipo de correo", [
            "Primera presentación de propuesta",
            "Seguimiento 5-7 días post-envío",
            "Urgencia — oferta próxima a vencer",
            "Respuesta a objeción: precio alto",
            "Argumentos para asamblea de propietarios",
            "Adultos mayores / discapacidad — respuesta específica",
            "Propuesta de visita presencial",
            "Confirmación de contrato y próximos pasos"
        ])
        ctx_e = st.text_area("Contexto adicional", height=90, placeholder="Ej: El cliente pregunta por adultos mayores...")

        if st.button("🤖 Generar correo", use_container_width=True):
            if edif_sel == "— Seleccionar —":
                st.warning("Selecciona un edificio")
            elif not ai_activa():
                st.error("Activa la IA en ⚙️ Configuración")
            else:
                r = df[df["nombre"] == edif_sel].iloc[0]
                tn = int(r.get("totalNum") or 0)

                # PROMPT MUY FUERTE Y CLARO
                prompt = f"""Eres un asistente comercial experto de Ágora Tech Colombia.
Empresa especializada en **automatización de accesos** con sistema SALTO HomeLok.
Ofrecemos instalación de cerraduras electrónicas, control de acceso y financiamiento 100% sin intereses ni entrada.
NO vendemos apartamentos ni inmuebles. Nunca hables de comprar unidades, descuentos en precio de apartamento ni nada relacionado con venta de bienes raíces.

Datos del edificio:
- Nombre: {edif_sel}
- Valor cotizado: {fc(tn)}
- Cuota 24 meses: {fc(int(r.get("c24Num") or 0))}
- Cuota 36 meses: {fc(int(r.get("c36Num") or 0))}
- Contacto: {r.get("contacto", "Administrador")}
- Comercial: {r.get("comercial", "")}
- Estado actual: {ETAPAS.get(str(r.get("estado","lead")), {"label":"Lead"})["label"]}

Tipo de correo solicitado: {tipo_c}
Contexto adicional del cliente: {ctx_e if ctx_e else "Ninguno"}

Redacta un correo profesional, claro y persuasivo en español colombiano.
Énfasis en: seguridad, comodidad para adultos mayores (teclado PIN físico con relieve, sin necesidad de celular), financiamiento 100% sin intereses.
Firma siempre: 
Luisa Olivares — Ágora Tech | (+57) 315 101 7511 | agoratech.com.co

Responde SOLO el texto del correo (incluyendo asunto). Nada más."""
                
                with st.spinner("Generando correo..."):
                    correo = ask_ai(prompt)
                st.session_state.correo = correo

    with col2:
        st.markdown("**Vista previa del correo:**")
        correo_actual = st.session_state.get("correo", "")
        if correo_actual:
            st.markdown(f"""<div style='background:#F6F9FC;border:1.5px solid #E3EAF3;border-radius:10px;
                 padding:20px;font-family:monospace;font-size:12.5px;line-height:1.7;
                 white-space:pre-wrap;color:#04111E;max-height:460px;overflow-y:auto'>{correo_actual.replace("<","&lt;").replace(">","&gt;")}</div>""", unsafe_allow_html=True)
            st.download_button("📋 Descargar correo", data=correo_actual,
                file_name=f"correo_{edif_sel[:20] if edif_sel != '— Seleccionar —' else 'agora'}.txt", mime="text/plain")
        else:
            st.markdown("""<div style='background:#F6F9FC;border:1.5px dashed #C8D8E9;border-radius:10px;
                 padding:40px;text-align:center;color:#8BA3BD;font-size:13px'>
              Selecciona edificio y haz clic en<br><b>"🤖 Generar correo"</b>
            </div>""", unsafe_allow_html=True)

def pg_asistente():
    hdr("🤖","Asistente Comercial IA","Consultas estratégicas — pipeline, cierres, objeciones")
    if not ai_activa():
        st.markdown('<div class="al-r">⚠️ <b>IA no configurada.</b> Ve a ⚙️ Configuración.</div>',unsafe_allow_html=True); return
    df=mis_proyectos(); ctx=df.to_string(max_rows=84) if not df.empty else ""
    for msg in st.session_state.messages:
        cls="chat-u" if msg["role"]=="user" else "chat-a"
        pre="👤 " if msg["role"]=="user" else "🤖 "
        st.markdown(f'<div class="{cls}">{pre}{msg["content"]}</div>',unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown("**Sugerencias:**")
        sugs=["📊 Resume el pipeline completo","⚡ Top 5 proyectos más urgentes","📈 Estrategia para Nomad 53","👴 Cómo responder objeción adultos mayores","🔍 Análisis de rechazos","📋 Plan de acción esta semana"]
        cols=st.columns(3)
        for i,s in enumerate(sugs):
            if cols[i%3].button(s,key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":s})
                with st.spinner("Analizando..."): r=ask_ai(s,ctx)
                st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    with st.form("chat_f",clear_on_submit=True):
        c1,c2=st.columns([5,1])
        with c1: ui=st.text_input("Pregunta",label_visibility="collapsed",placeholder="Ej: Estrategia para Bosque San Vicente esta semana...")
        with c2: send=st.form_submit_button("Enviar →")
        if send and ui:
            st.session_state.messages.append({"role":"user","content":ui})
            with st.spinner("Analizando..."): r=ask_ai(ui,ctx)
            st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    if st.session_state.messages:
        if st.button("🗑 Limpiar"): st.session_state.messages=[]; st.rerun()

# ══════════════════════════════════════════
# ENCUESTA PROSPECTO — Formulario real de Ágora Tech
# ══════════════════════════════════════════
def pg_encuesta():
    hdr("📊","Encuesta de Prospecto","Formulario Información Preliminar — Ágora Tech")

    df=mis_proyectos()
    # Pre-seleccionar edificio si viene de proyectos
    presel=st.session_state.get("editing","")
    nombres=["— Nuevo prospecto (sin edificio aún) —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx=nombres.index(presel) if presel in nombres else 0
    edificio_sel=st.selectbox("Vincular a edificio existente (opcional):",nombres,index=idx)

    st.markdown("---")
    st.markdown("### Formulario Información Preliminar Prospectos")

    with st.form("encuesta_form"):
        st.markdown("**Datos del edificio**")
        c1,c2=st.columns(2)
        with c1:
            nombre_edif=st.text_input("Nombre del Edificio *",
                value=edificio_sel if edificio_sel!="— Nuevo prospecto (sin edificio aún) —" else "",
                placeholder="Ej: Edificio Altos del Pino")
            direccion=st.text_input("Dirección del Edificio",placeholder="Cra 7 No. 45-23, Bogotá")
        with c2:
            contacto=st.text_input("Contacto *",placeholder="Juan Pérez")
            rol=st.selectbox("Rol",["Administrador","Propietario","Propietario y Miembro del Consejo","Presidente del Consejo"])

        st.markdown("---")
        st.markdown("**Etapa y decisión**")
        etapa_decision=st.selectbox("¿En qué etapa de decisión se encuentra la automatización?",
            ["El Consejo está recibiendo cotizaciones por orden de la asamblea",
             "Aún no se ha hablado del tema en asamblea",
             "La copropiedad está apenas explorando la opción de automatizar"])

        impulsor=st.text_input("¿Quién está impulsando la decisión de automatizar?",
            placeholder="Ej: El administrador / Un propietario del consejo...")

        st.markdown("---")
        st.markdown("**Seguridad**")
        incidentes=st.text_area("¿Han ocurrido robos o incidentes de seguridad en la copropiedad? ¿Qué pasó?",
            placeholder="Describir incidentes relevantes...",height=80)

        st.markdown("---")
        st.markdown("**Comunidad**")
        adultos_mayores=st.text_area("¿El edificio cuenta con adultos mayores o personas con discapacidad? Cuéntenos sobre la situación de la comunidad.",
            placeholder="Ej: Hay varios adultos mayores en los pisos altos. Un residente en silla de ruedas...",height=80)

        st.markdown("---")
        st.markdown("**Vigilancia actual**")
        c1,c2=st.columns(2)
        with c1:
            tiene_vigilancia=st.radio("¿El edificio cuenta con vigilancia tradicional?",["Sí","No"],horizontal=True)
        with c2:
            costo_vig=st.number_input("¿Cuál es el costo al mes de este servicio? ($)",min_value=0,value=0,step=100_000,format="%d") if tiene_vigilancia=="Sí" else 0
        vigencia=st.text_input("¿Hasta cuándo está vigente el contrato de vigilancia?",placeholder="Ej: Noviembre 2026")
        servicios_adicionales=st.text_area("¿El servicio de vigilancia presta servicios de jardinería o asistencia en actividades cotidianas a miembros de la comunidad?",
            placeholder="Ej: Sí, el vigilante apoya con paquetes y tareas del edificio...",height=70)

        st.markdown("---")
        st.markdown("**Proceso de selección**")
        terminos=st.text_area("¿Tienen algunos términos de selección para la automatización?",
            placeholder="Ej: Necesitan 3 cotizaciones, requieren presentación en asamblea, tienen presupuesto máximo...",height=70)

        analizar_ia=st.checkbox("🤖 Analizar con IA y generar estrategia de venta al guardar",value=True)

        submitted=st.form_submit_button("💾 Guardar Encuesta",use_container_width=True)

        if submitted:
            if not nombre_edif: st.error("El nombre del edificio es obligatorio"); st.stop()

            datos_encuesta={
                "Nombre del Edificio":nombre_edif,
                "Dirección":direccion,
                "Contacto":contacto,
                "Rol":rol,
                "Etapa de decisión":etapa_decision,
                "Impulsor de la decisión":impulsor,
                "Incidentes de seguridad":incidentes,
                "Adultos mayores / Discapacidad":adultos_mayores,
                "Tiene vigilancia":tiene_vigilancia,
                "Costo vigilancia mensual":fc(costo_vig) if costo_vig else "No aplica",
                "Vigencia contrato vigilancia":vigencia,
                "Servicios adicionales vigilancia":servicios_adicionales,
                "Términos de selección":terminos,
            }

            # Guardar encuesta en el CRM si hay edificio seleccionado
            if edificio_sel!="— Nuevo prospecto (sin edificio aún) —":
                update_proy(edificio_sel, {"encuesta":json.dumps(datos_encuesta,ensure_ascii=False)})
                nota_hist=f"Encuesta de prospecto completada. Contacto: {contacto} ({rol}). Etapa: {etapa_decision}."
                agregar_historial(edificio_sel,"lead",nota_hist,st.session_state.user["nombre"])
                st.success(f"✅ Encuesta guardada en el historial de **{edificio_sel}**")

            # Análisis con IA
            if analizar_ia and ai_activa():
                prompt=f"""Analiza este prospecto para Ágora Tech Colombia y genera una estrategia de venta completa:

EDIFICIO: {nombre_edif} | Contacto: {contacto} ({rol})
Etapa decisión: {etapa_decision}
Impulsor: {impulsor or "No especificado"}
Vigilancia: {"SÍ — "+fc(costo_vig)+"/mes hasta "+vigencia if tiene_vigilancia=="Sí" and costo_vig else "NO"}
Incidentes: {incidentes or "Ninguno reportado"}
Adultos mayores: {adultos_mayores or "No reportado"}
Servicios vigilancia: {servicios_adicionales or "No aplica"}
Términos selección: {terminos or "Sin términos específicos"}

Genera:
## VIABILIDAD: [ALTA/MEDIA/BAJA] — con justificación clara

## PERFIL DEL CLIENTE
Tipo de comprador, motivaciones principales, posibles objeciones.

## ESTRATEGIA DE VENTA RECOMENDADA
Pasos concretos y argumentos específicos para este edificio.

## MANEJO DE OBJECIONES PROBABLES
Incluye respuesta específica si hay adultos mayores o discapacitados.

## ANÁLISIS FINANCIERO
{"Ahorro mensual vs vigilancia: "+fc(costo_vig)+"→ calcular cuota 36m que sea menor" if costo_vig else "Sin comparativo de vigilancia"}

## PRÓXIMOS PASOS CONCRETOS (esta semana)
Lista de acciones específicas con responsable.

Sin separadores ---. Negrilla para datos clave. Tono ejecutivo colombiano."""
                with st.spinner("Analizando con IA..."):
                    analisis=ask_ai(prompt)
                st.markdown("---")
                st.markdown("### 🤖 Análisis Estratégico IA")
                st.markdown(analisis)
                st.download_button("📥 Descargar análisis",data=analisis,
                    file_name=f"analisis_{nombre_edif[:20]}_{datetime.now().strftime('%Y%m%d')}.txt")
                # Guardar análisis en historial
                if edificio_sel!="— Nuevo prospecto (sin edificio aún) —":
                    agregar_historial(edificio_sel,"lead",f"Análisis IA generado: {analisis[:200]}...",st.session_state.user["nombre"])
            elif analizar_ia and not ai_activa():
                st.warning("Encuesta guardada. Para el análisis IA, ve a ⚙️ Configuración y activa Gemini.")

def pg_configuracion():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; ai_ok=ai_activa()
    hdr("⚙️","Configuración","Activa la IA — disponible para todos los usuarios")

    if ai_ok:
        modelo=st.session_state.get("gemini_modelo","gemini-2.0-flash")
        st.markdown(f'<div class="al-g">✅ <b>IA activa</b> — Gemini ({modelo}) · Usando créditos de Google Cloud</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="al-r">🔴 <b>IA no configurada.</b> Pega tu API Key de Gemini abajo.</div>',unsafe_allow_html=True)

    key_actual=get_ai_key()
    if key_actual:
        st.markdown(f'<div style="font-size:12px;color:#8BA3BD">Key activa: AIzaSy...{key_actual[-4:]}</div>',unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔑 Activar IA con Groq (recomendado)")
    st.markdown("""<div style='background:#F6F9FC;border:1px solid #E3EAF3;border-radius:10px;padding:14px 18px;margin-bottom:16px;font-size:13px;color:#4A6580'>
      Pega tu clave de Groq (empieza con gsk_...)<br>
      La puedes crear en: <a href="https://console.groq.com/keys" target="_blank">console.groq.com/keys</a>
    </div>""", unsafe_allow_html=True)

    with st.form("config_ia_form"):
        nueva_key = st.text_input("API Key de Groq *", placeholder="gsk_...")
        if st.form_submit_button("⚡ Activar IA con Groq", use_container_width=True):
            if not nueva_key.strip():
                st.error("Pega la API Key")
            else:
                with st.spinner("Verificando..."):
                    ok = activar_ia(nueva_key)
                if ok:
                    st.balloons()
                    st.rerun()

    if es_g:
        st.markdown("---")
        st.markdown("#### 📋 Configuración permanente en Streamlit Cloud")
        st.markdown("Para que todos tengan IA automáticamente sin configurar nada:")
        st.code('GEMINI_API_KEY = "AIzaSy-tu-key-aqui"',language="toml")
        st.markdown("Ve a tu app → **⋮** → **Settings** → **Secrets** → pega eso → **Save**")
        st.markdown("---")
        st.markdown("#### 📊 Estado del sistema")
        df=get_crm(); usuarios=get_usuarios()
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Proyectos en CRM",df.shape[0])
        c2.metric("Con valor",df[df["totalNum"]>0].shape[0])
        c3.metric("Usuarios",sum(1 for u in usuarios.values() if u.get("activo",True)))
        c4.metric("IA Gemini","🟢 Activa" if ai_ok else "🔴 Inactiva")

import calendar  # Asegúrate de que esté importado al inicio del archivo

import calendar
from datetime import datetime, timedelta

def pg_calendario():
    hdr("📅", "Calendario Comercial", "Agenda mensual con actividades visibles")

    hoy = datetime.now()
    mes = hoy.month
    año = hoy.year

    # ==================== ACTIVIDADES DE EJEMPLO (puedes agregar más) ====================
    actividades = {
        "2026-05-07": ["14:00 - Reunión Nomad 53 con David Conde", "Llevar contrato"],
        "2026-05-09": ["18:00 - Asamblea Bosque San Vicente"],
        "2026-05-13": ["19:00 - Presentación Tiara"],
        "2026-05-14": ["19:00 - Consejo El Cerro"],
        "2026-05-16": ["11:00 - Visita técnica Risaralda"],
        "2026-05-20": ["15:00 - Firma contrato Altos del Pino"],
    }

    # ====================== CALENDARIO REAL CON ACTIVIDADES ======================
    st.markdown(f"### 📆 {calendar.month_name[mes]} {año}")

    cal = calendar.monthcalendar(año, mes)
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    # Cabecera
    cols = st.columns(7)
    for i, dia in enumerate(dias_semana):
        cols[i].markdown(f"**{dia}**", unsafe_allow_html=True)

    # Días del mes
    for semana in cal:
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            if dia == 0:
                cols[i].markdown("")
                continue

            fecha_str = f"{año}-{mes:02d}-{dia:02d}"
            es_hoy = (dia == hoy.day and mes == hoy.month and año == hoy.year)

            # Contenido de la celda
            with cols[i].container():
                # Número del día
                if es_hoy:
                    st.markdown(f"<div style='text-align:center; background:#00C896; color:white; font-weight:700; padding:4px; border-radius:8px;'>{dia}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center; font-weight:600; color:#04111E;'>{dia}</div>", unsafe_allow_html=True)

                # Actividades del día
                if fecha_str in actividades:
                    for act in actividades[fecha_str]:
                        st.markdown(f"""
                        <div style="background:#FFF3E0; padding:6px 8px; margin:4px 0; border-radius:6px; font-size:12px; border-left:3px solid #FF9800;">
                            {act}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#B0B0B0; font-size:11px; text-align:center; margin-top:8px;'>—</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ====================== URGENTES ESTA SEMANA ======================
    st.markdown("### 🔥 Urgentes esta semana")
    col_urg = st.columns(3)
    urg = [
        ("Nomad 53", "Reunión con David Conde - Llevar contrato", "Mié 7 Mayo 14:00"),
        ("Bosque San Vicente", "Asamblea de copropietarios", "Vie 9 Mayo 18:00"),
        ("Tiara", "Presentación en asamblea", "Mar 13 Mayo 19:00"),
    ]
    for i, (edif, desc, fecha) in enumerate(urg):
        with col_urg[i]:
            st.markdown(f"""
            <div style="background:#FEF2F2; padding:14px; border-radius:10px; border-left:5px solid #E84040;">
                <strong>{edif}</strong><br>
                <small>{desc}</small><br>
                <strong style="color:#E84040;">{fecha}</strong>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ====================== AGREGAR NUEVA ACTIVIDAD ======================
    st.markdown("### ➕ Agregar nueva actividad al calendario")
    with st.form("act_form", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        with c1:
            edif = st.text_input("Edificio *")
            titulo = st.text_input("Título de la actividad *")
        with c2:
            fecha_a = st.date_input("Fecha", value=hoy + timedelta(days=3))
            hora_a = st.time_input("Hora", value=datetime.now().time().replace(minute=0))
        
        tipo = st.selectbox("Tipo", ["Reunión presencial", "Llamada", "Visita técnica", "Asamblea", "Firma contrato", "Otro"])
        notas = st.text_area("Notas adicionales", height=70)

        if st.form_submit_button("📅 Guardar en Calendario", use_container_width=True):
            if edif and titulo:
                st.success(f"✅ Actividad guardada: **{titulo}** en {edif} — {fecha_a.strftime('%d %b %Y')} {hora_a.strftime('%H:%M')}")
            else:
                st.error("Edificio y título son obligatorios")


    
def pg_auditoria():
    hdr("🔍","Auditoría Comercial","Análisis del equipo y pipeline completo")
    df=get_crm()
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Total Proyectos",df.shape[0]); c2.metric("Pipeline",f"${int(df['totalNum'].sum())/1e9:.2f}B")
    c3.metric("Cotizaciones",df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Rechazados",df[df["estado"]=="perdido"].shape[0]); c5.metric("Cerrados",df[df["estado"]=="cerrado"].shape[0])
    st.markdown('<div class="al-r">❗ <b>0 contratos cerrados.</b> El cuello de botella está en el cierre.</div>',unsafe_allow_html=True)
    st.markdown('<div class="al-y">⚠️ Patrón: adultos mayores no aprueban. Preparar respuesta con teclado PIN físico.</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        res=df[df["totalNum"]>0].groupby("comercial").agg(cotiz=("totalNum","count"),pipeline=("totalNum","sum")).reset_index()
        res["Pipeline $M"]=(res["pipeline"]/1e6).round(1)
        st.dataframe(res[["comercial","cotiz","Pipeline $M"]].rename(columns={"comercial":"Comercial","cotiz":"Cotiz."}),use_container_width=True,hide_index=True)
    with c2:
        if st.button("🤖 Análisis estratégico profundo",use_container_width=True):
            with st.spinner("Analizando..."): r=ask_ai("Top 5 proyectos más cercanos al cierre con acción específica. Patrón de rechazos. Plan 7 días. Estrategia para el primer contrato.",df.to_string(max_rows=84))
            st.markdown(r)

def pg_informes():
    hdr("📈","Informes Gerenciales","Análisis ejecutivo con gráficas")
    df=get_crm()
    c1,c2,c3=st.columns(3)
    with c1:
        dc=df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
        dc["M"]=(dc["totalNum"]/1e6).round(1); dc["Com"]=dc["comercial"].str.split().str[0]
        fig=px.bar(dc.sort_values("M",ascending=True),x="M",y="Com",orientation="h",title="Pipeline ($M)",color="M",color_continuous_scale=["#1A9FCC","#00C896"])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        grupos={"Comercial":["lead","cotizado","negociacion","aprobado","perdido"],"Ejecución":["creacion_contrato","financiacion","obra","novedades_obra","entrega"],"Posventa":["mantenimiento","cerrado"]}
        est_data=[{"Grupo":g,"n":df[df["estado"].isin(e)].shape[0]} for g,e in grupos.items()]
        fig2=px.pie(pd.DataFrame(est_data),values="n",names="Grupo",hole=0.48,color_discrete_sequence=["#1A9FCC","#00C896","#8B5CF6"])
        fig2.update_layout(paper_bgcolor="white",margin=dict(t=40))
        st.plotly_chart(fig2,use_container_width=True)
    with c3:
        cr=pd.DataFrame({"Mes":["Dic 2025","Ene 2026","Feb 2026","Mar 2026","Abr 2026"],"Leads":[3,17,25,32,46]})
        fig3=px.area(cr,x="Mes",y="Leads",color_discrete_sequence=["#00C896"],markers=True)
        fig3.update_traces(line_width=3,marker_size=8,fill="tozeroy",fillcolor="rgba(0,200,150,0.08)")
        fig3.update_layout(plot_bgcolor="white",paper_bgcolor="white",margin=dict(t=40))
        st.plotly_chart(fig3,use_container_width=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1: tipo_i=st.selectbox("Tipo:",["Informe Gerencial Ejecutivo","Reporte Pipeline","Análisis Equipo","Oportunidades Críticas","Estado de Ejecución y Obra"])
    with c2: notas_i=st.text_area("Instrucciones adicionales:",height=80)
    if st.button("🤖 Generar Informe",use_container_width=True):
        prompt=f"Genera {tipo_i} para Ágora Tech. {f'Instrucciones: {notas_i}' if notas_i else ''}\n## RESUMEN EJECUTIVO\n## MÉTRICAS\n## ANÁLISIS DETALLADO\n## ALERTAS\n## RECOMENDACIONES\n## PRÓXIMOS PASOS\nFecha: {datetime.now().strftime('%d %B %Y')}. Sin ---. Tono ejecutivo."
        with st.spinner("Generando..."): r=ask_ai(prompt,df.to_string(max_rows=84))
        st.markdown(r)
        c1,c2=st.columns(2)
        c1.download_button("📥 .md",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.md")
        c2.download_button("📥 .txt",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.txt")

def pg_pipeline():
    hdr("🎯","Pipeline Kanban","Vista de embudo por etapas")
    df=mis_proyectos()
    # Solo etapas comerciales en el kanban principal
    etapas_k=[("lead","🔵 Lead"),("cotizado","🟡 Cotización"),("negociacion","🟠 Negociando"),("aprobado","🟣 Aprobado"),("cerrado","✅ Cerrado")]
    cols=st.columns(5)
    for i,(k,lbl) in enumerate(etapas_k):
        items=df[df["estado"]==k]; tot=int(items["totalNum"].sum())
        with cols[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:11px;color:#8BA3BD;margin-bottom:12px">{len(items)} · ${tot/1e6:.1f}M</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                tn=int(r.get("totalNum") or 0)
                st.markdown(f"""<div style='background:white;border:1px solid #E3EAF3;border-radius:8px;padding:11px;margin-bottom:8px'>
                  <div style='font-family:Sora,sans-serif;font-size:11.5px;font-weight:700;color:#04111E;margin-bottom:2px'>{str(r["nombre"])[:22]}</div>
                  <div style='font-size:10px;color:#8BA3BD;margin-bottom:4px'>{str(r.get("comercial","—")).split()[0]}</div>
                  <div style='font-family:Sora,sans-serif;font-size:13px;font-weight:800;color:#05875D'>{fc(tn) if tn else "—"}</div>
                </div>""",unsafe_allow_html=True)

    # Pipeline de ejecución separado
    st.markdown("---")
    st.markdown("### 🔨 Proyectos en Ejecución")
    etapas_ejec=[("creacion_contrato","📝 Contrato"),("financiacion","💰 Financiación"),("obra","🔨 En Obra"),("novedades_obra","⚠️ Novedades"),("entrega","🎉 Entrega"),("mantenimiento","🔧 Mantenimiento")]
    cols2=st.columns(6)
    for i,(k,lbl) in enumerate(etapas_ejec):
        items=df[df["estado"]==k]
        with cols2[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:10px;color:#8BA3BD;margin-bottom:8px">{len(items)}</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                st.markdown(f'<div style="background:#F0FDF9;border-radius:6px;padding:8px;margin-bottom:6px;font-size:11px;font-weight:700">{str(r["nombre"])[:20]}</div>',unsafe_allow_html=True)

def pg_usuarios():
    hdr("👥","Gestión de Usuarios","Solo gerente - Cambio de contraseñas inmediato")

    usuarios = get_usuarios()

    # Tabla con contraseñas visibles
    st.markdown("### Usuarios registrados")
    data = []
    for ukey, ud in usuarios.items():
        data.append({
            "Usuario": ukey,
            "Nombre": ud["nombre"],
            "Rol": ud["rol"].capitalize(),
            "Comercial": ud["comercial"],
            "Contraseña": ud.get("pass", "—"),
            "Estado": "✅ Activo" if ud.get("activo", True) else "🔴 Inactivo"
        })
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Cambiar contraseña
    st.markdown("### 🔑 Cambiar contraseña de un usuario")
    col1, col2 = st.columns([1, 2])
    with col1:
        usuario_seleccionado = st.selectbox(
            "Seleccionar usuario", 
            options=list(usuarios.keys()),
            format_func=lambda x: f"{x} — {usuarios[x]['nombre']}"
        )
    with col2:
        nueva_contrasena = st.text_input("Nueva contraseña", type="password", key="nueva_pass_input")

    if st.button("💾 Cambiar contraseña", type="primary", use_container_width=True):
        if nueva_contrasena.strip():
            st.session_state.usuarios_db[usuario_seleccionado]["pass"] = nueva_contrasena.strip()
            guardar_usuarios()   # ← Guarda permanentemente
            nombre = usuarios[usuario_seleccionado]["nombre"]
            st.success(f"✅ Contraseña de **{nombre}** actualizada correctamente.\nEl cambio es inmediato.")
            st.rerun()
        else:
            st.error("Por favor ingresa una nueva contraseña")

    st.markdown("---")

    # Crear nuevo usuario
    st.markdown("### ➕ Crear nuevo usuario")
    with st.form("add_user_form"):
        c1, c2 = st.columns(2)
        with c1:
            nu_user = st.text_input("Usuario *")
            nu_nombre = st.text_input("Nombre completo *")
            nu_pass = st.text_input("Contraseña *", type="password")
        with c2:
            nu_rol = st.selectbox("Rol", ["comercial", "gerente"])
            nu_com = st.text_input("Nombre del Comercial *", placeholder="Ej: Carlos Mendoza")
        if st.form_submit_button("Crear usuario", use_container_width=True):
            if not nu_user or not nu_nombre or not nu_pass or not nu_com:
                st.error("Todos los campos son obligatorios")
            elif nu_user.lower() in usuarios:
                st.error(f"El usuario '{nu_user}' ya existe")
            else:
                st.session_state.usuarios_db[nu_user.lower()] = {
                    "pass": nu_pass,
                    "nombre": nu_nombre,
                    "rol": nu_rol,
                    "comercial": nu_com.upper(),
                    "activo": True
                }
                guardar_usuarios()   # ← Guarda permanentemente
                st.success(f"✅ Usuario **{nu_user}** creado correctamente")
                st.rerun()
                
# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if not st.session_state.logged_in:
    pg_login()
else:
    sidebar()
    pg=st.session_state.get("page","Dashboard")
    if   pg=="Dashboard":           pg_dashboard()
    elif pg=="Proyectos":           pg_proyectos()
    elif pg=="Nueva Cotización":    pg_nueva_cotizacion()
    elif pg=="Actualizar Estado":   pg_actualizar()
    elif pg=="Edificios":           pg_edificios()
    elif pg=="Calendario":          pg_calendario()
    elif pg=="Correos IA":          pg_correos()
    elif pg=="Asistente IA":        pg_asistente()
    elif pg=="Encuesta Prospecto":  pg_encuesta()
    elif pg=="Configuración":       pg_configuracion()
    elif pg=="Auditoría":           pg_auditoria()
    elif pg=="Informes":            pg_informes()
    elif pg=="Pipeline":            pg_pipeline()
    elif pg=="Usuarios":            pg_usuarios()
    else:                           pg_dashboard()
