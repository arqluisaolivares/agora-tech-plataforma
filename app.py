"""
ÁGORA TECH — Plataforma Comercial v4
Configuración de IA disponible para TODOS los usuarios
"""

import streamlit as st
from groq import Groq
import pandas as pd
import json, os
from datetime import datetime, timedelta
import plotly.express as px

# ═══════════════════════════════════════════════════════════════
# DATOS — cargar desde JSON
# ═══════════════════════════════════════════════════════════════
@st.cache_data
def cargar_proyectos():
    base = os.path.dirname(os.path.abspath(__file__))
    for nombre in ["proyectos.json", "proyectos_v2.json"]:
        ruta = os.path.join(base, nombre)
        if os.path.exists(ruta):
            with open(ruta, encoding="utf-8") as f:
                return json.load(f)
    return []

PROYECTOS_BASE = cargar_proyectos()

# ═══════════════════════════════════════════════════════════════
# USUARIOS
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# CONFIG STREAMLIT
# ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="Ágora Tech", page_icon="🔐", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Lato:wght@300;400;700&display=swap');
html,body,[class*="css"]{font-family:'Lato',sans-serif!important}
h1,h2,h3{font-family:'Sora',sans-serif!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#04111E 0%,#0A2540 100%)!important}
[data-testid="stSidebar"] *{color:rgba(255,255,255,.85)!important}
.stButton>button{background:linear-gradient(135deg,#00C896,#1A9FCC)!important;color:#04111E!important;
  font-family:'Sora',sans-serif!important;font-weight:700!important;border:none!important;
  border-radius:8px!important;transition:all .18s!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,200,150,.4)!important}
.stButton>button[kind="secondary"]{background:white!important;color:#04111E!important;
  border:1px solid #E3EAF3!important;box-shadow:none!important}
.kpi{background:white;border:1px solid #E3EAF3;border-radius:12px;padding:18px 20px;
  box-shadow:0 1px 6px rgba(4,17,30,.05);position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#00C896,#1A9FCC)}
.kpi-label{font-size:10px;font-weight:700;color:#8BA3BD;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px}
.kpi-val{font-family:'Sora',sans-serif;font-size:24px;font-weight:800;color:#04111E;line-height:1}
.kpi-val.g{color:#05875D}.kpi-val.r{color:#E84040}.kpi-val.o{color:#D97706}
.kpi-sub{font-size:11px;color:#8BA3BD;margin-top:5px}
.b-g{background:#D1FAF0;color:#065F46;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:700;display:inline-block}
.b-y{background:#FEF9C3;color:#92400E;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:700;display:inline-block}
.b-b{background:#DBEAFE;color:#1E3A8A;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:700;display:inline-block}
.b-r{background:#FEE2E2;color:#991B1B;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:700;display:inline-block}
.b-p{background:#EDE9FE;color:#5B21B6;padding:3px 10px;border-radius:20px;font-size:10.5px;font-weight:700;display:inline-block}
.al-r{background:#FEF2F2;border-left:3px solid #E84040;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.al-y{background:#FFFBEB;border-left:3px solid #D97706;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.al-g{background:#F0FDF9;border-left:3px solid #00C896;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.al-b{background:#EFF6FF;border-left:3px solid #1A9FCC;padding:12px 16px;border-radius:0 8px 8px 0;font-size:13px;margin-bottom:8px}
.chat-u{background:linear-gradient(135deg,#00C896,#1A9FCC);color:#04111E;padding:12px 16px;
  border-radius:16px 16px 3px 16px;margin:8px 0;font-weight:600;max-width:80%;margin-left:auto;display:block}
.chat-a{background:white;border:1px solid #E3EAF3;padding:14px 18px;border-radius:16px 16px 16px 3px;
  margin:8px 0;max-width:90%;box-shadow:0 1px 6px rgba(4,17,30,.06);line-height:1.75;display:block}
div[data-testid="stForm"]{border:none!important;padding:0!important}
[data-testid="stSidebar"] .stButton>button{background:transparent!important;
  color:rgba(255,255,255,.6)!important;font-weight:500!important;border:none!important;
  box-shadow:none!important;border-radius:8px!important;text-align:left!important;font-size:13px!important}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.08)!important;
  color:white!important;transform:none!important;box-shadow:none!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# IA — GROQ
# ═══════════════════════════════════════════════════════════════
AI_SYSTEM = """Eres el asistente comercial de Ágora Tech Colombia.
Sistema SALTO HomeLok (nube, Bluetooth, PIN, QR, app iOS/Android).
Financiación 100% a 24/36 meses sin intereses. Llave en mano 40 días.
Proyectos clave: Nomad 53 (David Conde) cierre cercano; Bosque San Vicente asamblea 2 mayo; Tiara pasó primer filtro.
Responde en español colombiano. Sé específico y accionable."""

GROQ_MODEL = "llama-3.3-70b-versatile"

def get_ai_key():
    """Obtener la API Key de Groq — primero de session_state, luego de secrets."""
    # Prioridad 1: key guardada en esta sesión (puesta por cualquier usuario)
    k = st.session_state.get("groq_api_key", "")
    if k and len(k) > 10:
        return k
    # Prioridad 2: key de Streamlit Cloud Secrets
    try:
        k = st.secrets["GROQ_API_KEY"]
        if k:
            st.session_state["groq_api_key"] = k  # cachear en sesión
            return k
    except Exception:
        pass
    return ""

def ai_activa():
    return len(get_ai_key()) > 10

def activar_ia(key: str):
    """Guardar key en session_state y verificar que funciona."""
    key = key.strip()
    if not key or len(key) < 10:
        st.error("La key debe empezar con gsk_ y tener más de 20 caracteres")
        return False
    try:
        client = Groq(api_key=key)
        r = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role":"user","content":"hola"}],
            max_tokens=5
        )
        if r:
            st.session_state["groq_api_key"] = key
            return True
    except Exception as e:
        st.error(f"❌ Key inválida: {str(e)[:100]}")
        return False

def ask_gemini(q, ctx=""):
    key = get_ai_key()
    if not key:
        return "⚠️ La IA no está configurada. Ve a ⚙️ Configuración en el menú y pega tu API Key de Groq."
    try:
        client = Groq(api_key=key)
        msgs = [{"role":"system","content":AI_SYSTEM}]
        if ctx:
            msgs.append({"role":"user","content":f"DATOS CRM:\n{ctx[:18000]}\n\nSOLICITUD:\n{q}"})
        else:
            msgs.append({"role":"user","content":q})
        r = client.chat.completions.create(model=GROQ_MODEL, messages=msgs, max_tokens=2000, temperature=0.7)
        return r.choices[0].message.content
    except Exception as e:
        return f"Error IA: {e}"

# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
def init():
    defaults = {"logged_in":False,"user":None,"page":"Dashboard","messages":[],"crm":None,"correo":"","editing":""}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init()

# Cargar key de secrets al inicio (para todos)
if not st.session_state.get("groq_api_key"):
    try:
        k = st.secrets["GROQ_API_KEY"]
        if k: st.session_state["groq_api_key"] = k
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
# CRM EN MEMORIA
# ═══════════════════════════════════════════════════════════════
def get_crm():
    if st.session_state.crm is None:
        rows = []
        for p in PROYECTOS_BASE:
            rows.append({
                "id":p.get("id",""),"nombre":p.get("nombre",""),"comercial":p.get("comercial",""),
                "contacto":p.get("contacto",""),"email":p.get("email",""),
                "total":p.get("total","$0"),"totalNum":int(float(p.get("totalNum",0) or 0)),
                "cuota24":p.get("cuota24","$0"),"cuota36":p.get("cuota36","$0"),
                "c24Num":int(float(p.get("c24Num",0) or 0)),"c36Num":int(float(p.get("c36Num",0) or 0)),
                "vig":p.get("vig",""),"vigH":p.get("vigH",""),
                "estado":p.get("estado","nuevo"),"etapaOrig":p.get("etapaOrig",""),
                "version":p.get("version","v1"),"notas":p.get("notas",""),
                "lastUpdate":p.get("lastUpdate",""),"lastNote":p.get("lastNote",""),
                "fecha":p.get("fecha",""),"drive":p.get("drive",""),
            })
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
    mask = df["nombre"]==nombre
    if mask.any():
        for k,v in campos.items(): df.loc[mask,k]=v
        st.session_state.crm=df

def add_proy(datos):
    df = get_crm()
    st.session_state.crm = pd.concat([pd.DataFrame([datos]),df],ignore_index=True)

# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════
def fc(n):
    try:
        n=int(float(n or 0))
        return "$0" if n==0 else "$"+f"{n:,}".replace(",",".")
    except: return "$0"

ESTADOS=["nuevo","cotizado","negociacion","cerrado","perdido"]
ESTADO_LABEL={"nuevo":"🔵 Lead","cotizado":"🟡 Enviado","negociacion":"🟠 Negoc.","cerrado":"🟢 Cerrado","perdido":"🔴 Perdido"}
ESTADO_CLS={"nuevo":"b-b","cotizado":"b-y","negociacion":"b-p","cerrado":"b-g","perdido":"b-r"}
COMS=["RAFAEL TORRES","SONIA CASTRO","LINA CALLE","ALBERTO FERRER","SANTIAGO BOHORQUEZ","LUISA OLIVARES"]

def badge(estado):
    return f'<span class="{ESTADO_CLS.get(estado,"b-b")}">{ESTADO_LABEL.get(estado,estado)}</span>'

def hdr(icon,title,sub=""):
    st.markdown(f"""<div style='display:flex;align-items:center;gap:14px;margin-bottom:24px;
      padding-bottom:16px;border-bottom:1px solid #E3EAF3'>
      <div style='width:42px;height:42px;border-radius:10px;
        background:linear-gradient(135deg,#00C896,#1A9FCC);display:flex;
        align-items:center;justify-content:center;font-size:20px;flex-shrink:0'>{icon}</div>
      <div><div style='font-family:Sora,sans-serif;font-size:20px;font-weight:700;color:#04111E'>{title}</div>
        {'<div style="font-size:12px;color:#8BA3BD;margin-top:2px">'+sub+'</div>' if sub else ''}</div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════
def pg_login():
    col1,col2,col3 = st.columns([1,1.2,1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:48px 0 28px'>
          <div style='font-family:Sora,sans-serif;font-size:11px;font-weight:700;
               color:#8BA3BD;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px'>
               SISTEMA COMERCIAL</div>
          <div style='font-family:Sora,sans-serif;font-size:36px;font-weight:800;
               color:#04111E;letter-spacing:-2px'>ÁGORA TECH</div>
          <div style='width:40px;height:3px;background:linear-gradient(90deg,#00C896,#1A9FCC);
               margin:14px auto;border-radius:2px'></div>
          <div style='font-size:13px;color:#8BA3BD'>Plataforma de Gestión Comercial</div>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            usuario  = st.text_input("Usuario", placeholder="rafael / sonia / lina / luisa...")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            entrar   = st.form_submit_button("Ingresar a la plataforma", use_container_width=True)
            if entrar:
                u = usuario.strip().lower()
                usuarios = get_usuarios()
                if u in usuarios and usuarios[u]["activo"] and usuarios[u]["pass"]==password:
                    st.session_state.logged_in = True
                    st.session_state.user = usuarios[u]
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

        st.markdown("""
        <div style='background:#F6F9FC;border:1px solid #E3EAF3;border-radius:10px;
             padding:12px 16px;margin-top:12px;font-size:11.5px;color:#8BA3BD;text-align:center'>
          luisa / luisa2026 &nbsp;·&nbsp; rafael / rafael2026 &nbsp;·&nbsp; sonia / sonia2026<br>
          lina / lina2026 &nbsp;·&nbsp; alberto / alberto2026 &nbsp;·&nbsp; santiago / santiago2026
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
def sidebar():
    u = st.session_state.user
    es_g = u["rol"]=="gerente"
    ai_ok = ai_activa()

    with st.sidebar:
        st.markdown(f"""
        <div style='padding:18px 16px 12px'>
          <div style='font-family:Sora,sans-serif;font-size:16px;font-weight:800;color:#fff'>ÁGORA TECH</div>
          <div style='font-size:9px;color:rgba(255,255,255,.3);letter-spacing:2px;text-transform:uppercase;margin-top:2px'>Plataforma Comercial</div>
        </div>
        <div style='background:rgba(0,200,150,.1);border:1px solid rgba(0,200,150,.2);
             border-radius:10px;padding:10px 14px;margin:0 12px 14px'>
          <div style='font-size:13px;font-weight:600;color:#fff'>{u["nombre"]}</div>
          <div style='font-size:10px;color:rgba(255,255,255,.4);margin-top:1px'>
            {u["rol"].capitalize()} · {"🟢 IA activa" if ai_ok else "🔴 IA sin configurar — ve a ⚙️"}</div>
        </div>""", unsafe_allow_html=True)

        # MENÚ — Configuración disponible para TODOS
        nav_todos = [
            ("📊","Dashboard"),("📋","Proyectos"),("🧮","Nueva Cotización"),
            ("📝","Actualizar Estado"),("🏢","Edificios"),("📅","Calendario"),
            ("✉️","Correos IA"),("🤖","Asistente IA"),("⚙️","Configuración"),
        ]
        nav_solo_gerente = [
            ("🔍","Auditoría"),("📈","Informes"),("🎯","Pipeline"),("📊","Encuestas"),("👥","Usuarios"),
        ]
        todas_paginas = nav_todos + (nav_solo_gerente if es_g else [])

        for icono,nombre in todas_paginas:
            activo = st.session_state.page==nombre
            if activo:
                st.markdown(f'<div style="background:rgba(0,200,150,.15);border:1px solid rgba(0,200,150,.3);border-radius:8px;margin-bottom:2px">', unsafe_allow_html=True)
            if st.button(f"{icono}  {nombre}", key=f"nav_{nombre}", use_container_width=True):
                st.session_state.page = nombre
                st.rerun()
            if activo:
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("← Cerrar sesión", use_container_width=True, key="logout"):
            for k in ["logged_in","user","messages","page","crm","correo","editing"]:
                st.session_state.pop(k,None)
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# PÁGINAS
# ═══════════════════════════════════════════════════════════════
def pg_dashboard():
    u=st.session_state.user; es_g=u["rol"]=="gerente"; df=mis_proyectos()
    st.markdown(f"""<div style='background:linear-gradient(135deg,#04111E 0%,#0A2540 55%,#0E3D6B 100%);
      border-radius:14px;padding:28px 32px;margin-bottom:24px;color:white;overflow:hidden;position:relative'>
      <div style='position:absolute;top:-60px;right:-60px;width:220px;height:220px;border-radius:50%;
           background:radial-gradient(circle,rgba(0,200,150,.18) 0%,transparent 70%)'></div>
      <div style='font-family:Sora,sans-serif;font-size:11px;font-weight:700;color:rgba(0,200,150,.8);
           letter-spacing:3px;text-transform:uppercase;margin-bottom:10px'>Dashboard · {datetime.now().strftime("%d %B %Y")}</div>
      <div style='font-family:Sora,sans-serif;font-size:24px;font-weight:800;color:#fff;letter-spacing:-1px;margin-bottom:6px'>
        {"Vista General — Ágora Tech" if es_g else f"Hola, {u['nombre'].split()[0]} 👋"}</div>
      <div style='font-size:13px;color:rgba(255,255,255,.45)'>{len(df)} proyectos · Pipeline ${int(df["totalNum"].sum())/1e9:.2f}B</div>
    </div>""", unsafe_allow_html=True)

    total=int(df["totalNum"].sum()); con_v=df[df["totalNum"]>0]
    prom=int(con_v["totalNum"].mean()) if len(con_v) else 0
    negoc=int(df[df["estado"]=="negociacion"].shape[0]); cotiz=int(df[df["estado"]=="cotizado"].shape[0])
    cerr=int(df[df["estado"]=="cerrado"].shape[0])

    c1,c2,c3,c4,c5=st.columns(5)
    c1.markdown(f'<div class="kpi"><div class="kpi-label">Pipeline Total</div><div class="kpi-val g">${total/1e9:.2f}B</div><div class="kpi-sub">{len(df)} proyectos</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="kpi-label">Promedio</div><div class="kpi-val">${prom/1e6:.1f}M</div><div class="kpi-sub">{len(con_v)} con valor</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="kpi-label">Negociando</div><div class="kpi-val o">{negoc}</div><div class="kpi-sub">cierre cercano</div></div>',unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><div class="kpi-label">Cotizaciones Enviadas</div><div class="kpi-val o">{cotiz}</div><div class="kpi-sub">en seguimiento</div></div>',unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi"><div class="kpi-label">Contratos Cerrados</div><div class="kpi-val {"r" if cerr==0 else "g"}">{cerr}</div><div class="kpi-sub">{"⚠ urgente" if cerr==0 else "excelente"}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    lm={"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}
    c1,c2=st.columns(2)
    with c1:
        est=df.groupby("estado").size().reset_index(name="n")
        est["Estado"]=est["estado"].map(lm).fillna(est["estado"])
        fig=px.bar(est,x="Estado",y="n",title="Proyectos por Estado",labels={"n":"Proyectos"},
                   color_discrete_sequence=["#00C896"])
        fig.update_traces(marker_color=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"][:len(est)],marker_line_width=0)
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",font_family="Lato",title_font_family="Sora",margin=dict(t=40,b=10))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        if es_g:
            dc=df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
            dc["M"]=(dc["totalNum"]/1e6).round(1); dc["Com"]=dc["comercial"].str.split().str[0]
            fig2=px.bar(dc.sort_values("M",ascending=True),x="M",y="Com",orientation="h",
                        title="Pipeline por Comercial ($M)",color="M",color_continuous_scale=["#1A9FCC","#00C896"],labels={"M":"$M","Com":""})
            fig2.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40,b=10))
        else:
            pie_d=df.groupby("estado").size().reset_index(name="n")
            pie_d["Estado"]=pie_d["estado"].map(lm).fillna(pie_d["estado"])
            fig2=px.pie(pie_d,values="n",names="Estado",hole=0.48,title="Mis Proyectos",
                        color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"])
            fig2.update_layout(paper_bgcolor="white",margin=dict(t=40,b=10))
        st.plotly_chart(fig2,use_container_width=True)

    st.markdown("### 🚨 Alertas")
    if es_g:
        st.markdown('<div class="al-r">❗ <b>0 contratos cerrados.</b> Con $8.6B en pipeline el cuello de botella está en el cierre.</div>',unsafe_allow_html=True)
    st.markdown('<div class="al-y">⚡ <b>Nomad 53 (David Conde)</b> — reunión 30 abril. Llevar contrato listo.</div>',unsafe_allow_html=True)
    st.markdown('<div class="al-g">✅ <b>Bosque San Vicente</b> — asamblea 2 mayo. Única propuesta con financiamiento.</div>',unsafe_allow_html=True)
    st.markdown('<div class="al-g">✅ <b>Tiara</b> — pasó primer filtro del consejo 24 abril. Agendar asamblea urgente.</div>',unsafe_allow_html=True)
    if not ai_activa():
        st.markdown('<div class="al-b">💡 <b>IA sin configurar.</b> Ve a ⚙️ Configuración en el menú y pega tu API Key de Groq para activar correos y asistente IA.</div>',unsafe_allow_html=True)

def pg_proyectos():
    es_g=st.session_state.user["rol"]=="gerente"; df=mis_proyectos()
    hdr("📋","Proyectos","Pipeline completo")
    c1,c2,c3=st.columns([2,1,1])
    with c1: buscar=st.text_input("🔍 Buscar",placeholder="Nombre del edificio...")
    with c2: filtro_e=st.selectbox("Estado",["Todos"]+ESTADOS)
    with c3:
        if es_g:
            coms=["Todos"]+sorted(df["comercial"].dropna().unique().tolist())
            filtro_c=st.selectbox("Comercial",coms)
        else: filtro_c="Todos"
    dff=df.copy()
    if buscar: dff=dff[dff["nombre"].str.contains(buscar,case=False,na=False)]
    if filtro_e!="Todos": dff=dff[dff["estado"]==filtro_e]
    if filtro_c!="Todos": dff=dff[dff["comercial"]==filtro_c]
    st.markdown(f'<div style="font-size:12px;color:#8BA3BD;margin-bottom:12px">{len(dff)} proyectos</div>',unsafe_allow_html=True)
    for _,r in dff.iterrows():
        tn=int(r.get("totalNum") or 0); total=fc(tn) if tn else r.get("total","$0") or "$0"
        c24=fc(int(r.get("c24Num") or 0)) if tn else "—"; c36=fc(int(r.get("c36Num") or 0)) if tn else "—"
        est=str(r.get("estado","nuevo")); nota=str(r.get("lastNote","") or r.get("notas","") or "")
        drive=str(r.get("drive","") or ""); drv=f'<a href="{drive}" target="_blank" style="font-size:11px;color:#1A73E8;margin-left:8px">📁 Drive</a>' if drive.startswith("http") else ""
        with st.expander(f"🏢  {r['nombre']}   —   {total}   —   {r.get('comercial','')}",expanded=False):
            m1,m2,m3,m4=st.columns(4)
            m1.metric("Valor",total); m2.metric("Cuota 24m",c24); m3.metric("Cuota 36m",c36)
            m4.markdown(f"**Estado:**<br>{badge(est)}{drv}",unsafe_allow_html=True)
            if nota and nota!="nan": st.markdown(f'<div class="al-b" style="font-size:12px">📝 {nota[:300]}</div>',unsafe_allow_html=True)
            b1,b2=st.columns(2)
            if b1.button("📝 Actualizar",key=f"u_{r.get('id',r['nombre'])}"):
                st.session_state.editing=r["nombre"]; st.session_state.page="Actualizar Estado"; st.rerun()
            if b2.button("✉️ Correo IA",key=f"c_{r.get('id',r['nombre'])}"):
                st.session_state.page="Correos IA"; st.rerun()

def pg_nueva_cotizacion():
    hdr("🧮","Nueva Cotización","Registrar en el CRM")
    with st.form("form_cot"):
        c1,c2=st.columns(2)
        with c1:
            nombre=st.text_input("Nombre del edificio *",placeholder="Ej: Edificio Altos del Pino")
            contacto=st.text_input("Contacto *",placeholder="Juan Pérez — Administrador")
            email=st.text_input("Email de contacto")
        with c2:
            direccion=st.text_input("Dirección")
            drive_url=st.text_input("Link carpeta Drive (opcional)")
        st.markdown("---"); c1,c2,c3=st.columns(3)
        with c1: valor=st.number_input("Valor total ($)",min_value=0,value=0,step=1_000_000,format="%d")
        with c2: vig_v=st.number_input("Vigilancia actual ($/mes)",min_value=0,value=0,step=100_000,format="%d")
        with c3: vig_h=st.text_input("Vigilancia vigente hasta",placeholder="Nov 2026")
        c1,c2=st.columns(2)
        with c1: estado=st.selectbox("Estado",ESTADOS)
        with c2: version=st.text_input("Versión",value="v1")
        notas=st.text_area("Observaciones",placeholder="Contexto, acuerdos, próximos pasos...")
        arch=st.file_uploader("Adjuntar archivos",accept_multiple_files=True)
        if st.form_submit_button("💾 Guardar en CRM",use_container_width=True):
            if not nombre: st.error("El nombre es obligatorio")
            else:
                u=st.session_state.user; c24n=valor//24 if valor else 0; c36n=valor//36 if valor else 0
                add_proy({"id":int(datetime.now().timestamp()),"nombre":nombre.upper(),"comercial":u["comercial"],
                    "contacto":contacto,"email":email,"total":fc(valor),"totalNum":valor,
                    "cuota24":fc(c24n),"cuota36":fc(c36n),"c24Num":c24n,"c36Num":c36n,
                    "vig":str(vig_v),"vigH":vig_h,"estado":estado,"etapaOrig":estado,"version":version,
                    "notas":notas,"lastUpdate":datetime.now().isoformat(),"lastNote":notas[:100],
                    "fecha":datetime.now().strftime("%d %b %Y"),"drive":drive_url})
                st.success(f"✅ **{nombre}** guardado — {fc(valor)}")
                if arch: st.info(f"📎 {len(arch)} archivo(s): {', '.join(f.name for f in arch)}")
                st.balloons()

def pg_actualizar():
    hdr("📝","Actualizar Estado","Registro de seguimiento — mínimo cada 7 días")
    df=mis_proyectos()
    presel=st.session_state.get("editing","")
    nombres=["— Selecciona un edificio —"]+sorted(df["nombre"].dropna().unique().tolist())
    idx=nombres.index(presel) if presel in nombres else 0
    sel=st.selectbox("Edificio:",nombres,index=idx)
    if sel!="— Selecciona un edificio —":
        r=df[df["nombre"]==sel].iloc[0]
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Valor",fc(int(r.get("totalNum") or 0))); c2.metric("Comercial",str(r.get("comercial","—")))
        c3.metric("Estado",str(r.get("estado","—"))); c4.metric("Última actualización",str(r.get("lastUpdate","Nunca"))[:10] or "Nunca")
        if r.get("lastNote"): st.markdown(f'<div style="font-size:12px;color:#8BA3BD;margin-top:8px">Última nota: {str(r["lastNote"])[:200]}</div>',unsafe_allow_html=True)
        with st.form("upd_form"):
            nuevo_e=st.selectbox("Nuevo estado *",ESTADOS,index=ESTADOS.index(str(r.get("estado","nuevo"))) if str(r.get("estado","nuevo")) in ESTADOS else 0)
            nota=st.text_area("Nota de seguimiento * (obligatoria)",placeholder="¿Qué pasó? ¿Cuál es el próximo paso?...")
            if st.form_submit_button("✅ Guardar actualización",use_container_width=True):
                if not nota.strip(): st.error("La nota es obligatoria")
                else:
                    update_proy(sel,{"estado":nuevo_e,"lastNote":nota,"lastUpdate":datetime.now().isoformat()})
                    st.success(f"✅ **{sel}** → {nuevo_e}"); st.session_state.editing=""; st.rerun()

def pg_edificios():
    hdr("🏢","Edificios","Carpetas y datos por proyecto")
    df=mis_proyectos(); buscar=st.text_input("🔍 Buscar",placeholder="Nombre...")
    if buscar: df=df[df["nombre"].str.contains(buscar,case=False,na=False)]
    cols=st.columns(3)
    for i,(_,r) in enumerate(df.iterrows()):
        with cols[i%3]:
            tn=int(r.get("totalNum") or 0); total=fc(tn) if tn else "Sin cotización"
            c36=fc(int(r.get("c36Num") or 0)) if tn else "—"; est=str(r.get("estado","nuevo"))
            drive=str(r.get("drive","") or ""); nota=str(r.get("notas","") or r.get("lastNote",""))
            drv_html=f'<a href="{drive}" target="_blank" style="background:#E8F0FE;color:#1A73E8;border-radius:6px;padding:3px 9px;font-size:10px;font-weight:700;text-decoration:none;display:inline-block;margin-top:8px">📁 Ver en Drive</a>' if drive.startswith("http") else ""
            st.markdown(f"""<div style='background:white;border:1px solid #E3EAF3;border-radius:12px;padding:16px;
              margin-bottom:12px;box-shadow:0 1px 6px rgba(4,17,30,.05);transition:all .18s'>
              <div style='font-family:Sora,sans-serif;font-size:13px;font-weight:700;color:#04111E;margin-bottom:4px'>{str(r["nombre"])[:30]}</div>
              <div style='font-size:11px;color:#8BA3BD;margin-bottom:8px'>{str(r.get("comercial","—"))}</div>
              <div style='font-family:Sora,sans-serif;font-size:17px;font-weight:800;color:#05875D;margin-bottom:2px'>{total}</div>
              {'<div style="font-size:10.5px;color:#8BA3BD;margin-bottom:8px">Cuota 36m: '+c36+'/mes</div>' if tn else '<div style="margin-bottom:8px"></div>'}
              <div>{badge(est)}</div>
              {'<div style="font-size:11px;color:#8BA3BD;margin-top:6px">'+nota[:60]+'...</div>' if nota and nota!="nan" and len(nota)>5 else ""}
              {drv_html}
            </div>""",unsafe_allow_html=True)

def pg_calendario():
    hdr("📅","Calendario Comercial","Agenda de actividades")
    es_g=st.session_state.user["rol"]=="gerente"
    col1,col2=st.columns([2,1])
    with col1:
        st.markdown("#### Registrar actividad")
        with st.form("act_form"):
            c1,c2=st.columns(2)
            with c1: edif=st.text_input("Edificio"); tipo=st.selectbox("Tipo",["Reunión presencial","Llamada","Visita técnica","Asamblea","Envío propuesta","Otro"])
            with c2: fecha_a=st.date_input("Fecha",value=datetime.now()); hora_a=st.time_input("Hora")
            titulo_a=st.text_input("Título *",placeholder="Ej: Reunión consejo directivo")
            if es_g: com_r=st.selectbox("Comercial responsable",COMS)
            else: com_r=st.session_state.user["comercial"]
            notas_a=st.text_area("Notas / Agenda")
            if st.form_submit_button("📅 Guardar actividad",use_container_width=True):
                if titulo_a: st.success(f"✅ **{titulo_a}** — {fecha_a.strftime('%d %b')} {hora_a.strftime('%H:%M')}")
                else: st.error("El título es obligatorio")
    with col2:
        st.markdown("#### ⏰ Urgente esta semana")
        urgentes=[("Nomad 53","Reunión David Conde — 30 abr","#FEF3C7","#92400E"),
                  ("Bosque San Vicente","Asamblea 2 mayo","#FEF3C7","#92400E"),
                  ("Tiara","Agendar presentación asamblea","#F0FDF9","#065F46"),
                  ("El Cerro","Presentación consejo mié 29 — 7pm","#EFF6FF","#1E3A8A")]
        for nombre_u,desc,bg,ct in urgentes:
            st.markdown(f'<div style="background:{bg};border-radius:8px;padding:10px 12px;margin-bottom:8px;border-left:3px solid {ct}"><div style="font-size:12px;font-weight:700;color:#04111E">{nombre_u}</div><div style="font-size:10.5px;color:#8BA3BD;margin-top:2px">{desc}</div></div>',unsafe_allow_html=True)

def pg_correos():
    hdr("✉️","Correos IA","Genera correos comerciales personalizados")
    df=mis_proyectos()
    if not ai_activa():
        st.markdown('<div class="al-r">⚠️ <b>IA no configurada.</b> Ve a ⚙️ Configuración en el menú para activarla.</div>',unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        edif_sel=st.selectbox("Edificio / Cotización",["— Seleccionar —"]+sorted(df["nombre"].dropna().unique().tolist()))
        tipo_c=st.selectbox("Tipo de correo",["Primera presentación de propuesta","Seguimiento 5-7 días post-envío","Urgencia — oferta próxima a vencer","Respuesta a objeción: precio alto","Argumentos para asamblea","Adultos mayores / discapacidad","Propuesta de visita presencial"])
        ctx_e=st.text_area("Contexto adicional",height=90,placeholder="Ej: El cliente dice que la cuota es muy alta...")
        if st.button("🤖 Generar correo con IA",use_container_width=True):
            if edif_sel=="— Seleccionar —": st.warning("Selecciona un edificio primero")
            elif not ai_activa(): st.error("Activa la IA en ⚙️ Configuración")
            else:
                r=df[df["nombre"]==edif_sel].iloc[0]; tn=int(r.get("totalNum") or 0)
                prompt=f"""Redacta correo "{tipo_c}" para Ágora Tech Colombia.
EDIFICIO: {edif_sel} | Total: {fc(tn)} | Cuota 24m: {fc(int(r.get("c24Num") or 0))} | Cuota 36m: {fc(int(r.get("c36Num") or 0))}
Contacto: {r.get("contacto","Administrador")} | Comercial: {r.get("comercial","")}
{f"Contexto: {ctx_e}" if ctx_e else ""}
Primera línea: ASUNTO: [asunto específico]. Énfasis en financiamiento sin entrada.
Para adultos mayores: teclado PIN físico, sin smartphone.
Firma: {st.session_state.user["nombre"]} — Ágora Tech | (+57) 315 101 7511 | agoratech.com.co
Texto plano sin markdown."""
                with st.spinner("Generando..."): correo=ask_gemini(prompt)
                st.session_state.correo=correo
    with col2:
        st.markdown("**Vista previa del correo generado:**")
        correo_actual = st.session_state.get("correo", "")
        if correo_actual:
            # Mostrar el correo en un contenedor estilizado
            st.markdown(f"""
            <div style='background:#F6F9FC;border:1.5px solid #E3EAF3;border-radius:10px;
                 padding:20px;font-family:monospace;font-size:12.5px;line-height:1.7;
                 white-space:pre-wrap;color:#04111E;max-height:460px;overflow-y:auto'>
{correo_actual.replace("<","&lt;").replace(">","&gt;")}
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "📋 Descargar correo (.txt)",
                data=correo_actual,
                file_name=f"correo_{edif_sel[:20] if edif_sel!='— Seleccionar —' else 'agora'}.txt",
                mime="text/plain"
            )
        else:
            st.markdown("""
            <div style='background:#F6F9FC;border:1.5px dashed #C8D8E9;border-radius:10px;
                 padding:40px;text-align:center;color:#8BA3BD;font-size:13px'>
              Selecciona un edificio y haz clic en<br>
              <b>"🤖 Generar correo con IA"</b><br>para ver el resultado aquí
            </div>
            """, unsafe_allow_html=True)

def pg_asistente():
    hdr("🤖","Asistente Comercial IA","Consultas estratégicas sobre el pipeline")
    if not ai_activa():
        st.markdown('<div class="al-r">⚠️ <b>IA no configurada.</b> Ve a ⚙️ Configuración y activa la IA.</div>',unsafe_allow_html=True)
        return
    df=mis_proyectos(); ctx=df.to_string(max_rows=84) if not df.empty else ""
    for msg in st.session_state.messages:
        cls="chat-u" if msg["role"]=="user" else "chat-a"
        pre="👤 " if msg["role"]=="user" else "🤖 "
        st.markdown(f'<div class="{cls}">{pre}{msg["content"]}</div>',unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown("**Sugerencias:**")
        sugs=["📊 Resume el pipeline completo","💰 Pipeline total en COP","⚡ Proyectos más urgentes","📈 Estrategia para cerrar Nomad 53","🔍 Patrones de rechazo","👴 Objeción adultos mayores: cómo responder"]
        cols=st.columns(3)
        for i,s in enumerate(sugs):
            if cols[i%3].button(s,key=f"sug_{i}"):
                st.session_state.messages.append({"role":"user","content":s})
                with st.spinner("Analizando..."): r=ask_gemini(s,ctx)
                st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    with st.form("chat_f",clear_on_submit=True):
        c1,c2=st.columns([5,1])
        with c1: ui=st.text_input("Pregunta",label_visibility="collapsed",placeholder="Ej: Estrategia para Bosque San Vicente esta semana...")
        with c2: send=st.form_submit_button("Enviar →")
        if send and ui:
            st.session_state.messages.append({"role":"user","content":ui})
            with st.spinner("Analizando..."): r=ask_gemini(ui,ctx)
            st.session_state.messages.append({"role":"assistant","content":r}); st.rerun()
    if st.session_state.messages:
        if st.button("🗑 Limpiar"): st.session_state.messages=[]; st.rerun()

# ═══════════════════════════════════════════════════════════════
# ⚙️ CONFIGURACIÓN — PARA TODOS LOS USUARIOS
# ═══════════════════════════════════════════════════════════════
def pg_configuracion():
    u = st.session_state.user
    es_g = u["rol"] == "gerente"
    ai_ok = ai_activa()

    hdr("⚙️","Configuración","Activa la IA — disponible para todos los usuarios")

    # Estado actual
    if ai_ok:
        st.markdown('<div class="al-g">✅ <b>IA activa y funcionando</b> — Llama 3.3 · Groq · Gratis</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="al-r">🔴 <b>IA no configurada.</b> Pega la API Key de Groq abajo para activarla.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔑 Activar la IA (API Key de Groq)")
    st.markdown("""
    <div style='background:#F6F9FC;border:1px solid #E3EAF3;border-radius:10px;padding:16px 20px;margin-bottom:16px;font-size:13px;color:#4A6580'>
      <b>Instrucciones para obtener la key gratis:</b><br>
      1. Abre <b>console.groq.com</b> en el navegador<br>
      2. Inicia sesión con Gmail personal<br>
      3. Clic en <b>API Keys</b> → <b>Create API Key</b><br>
      4. Nombre: <code>agora-tech</code> → Submit<br>
      5. Copia la key (empieza con <code>gsk_...</code>) y pégala abajo
    </div>
    """, unsafe_allow_html=True)

    # Mostrar si ya hay una key guardada
    key_actual = get_ai_key()
    if key_actual:
        st.markdown(f'<div class="al-g">✅ <b>Key activa:</b> <code>gsk_...{key_actual[-6:]}</code> — la IA funciona en esta sesión</div>', unsafe_allow_html=True)
    
    with st.form("config_ia_form"):
        st.markdown("**Pega tu API Key de Groq completa** (empieza con `gsk_` y tiene ~56 caracteres):")
        nueva_key = st.text_input(
            "API Key de Groq",
            placeholder="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            help="Copia la key COMPLETA desde console.groq.com → API Keys",
            label_visibility="collapsed"
        )
        
        # Mostrar longitud para verificar que está completa
        if nueva_key:
            n = len(nueva_key.strip())
            if n < 40:
                st.warning(f"⚠️ La key tiene solo {n} caracteres — parece incompleta. Una key válida tiene ~56 caracteres.")
            else:
                st.success(f"✅ Key de {n} caracteres — longitud correcta")
        
        guardar = st.form_submit_button("⚡ Activar IA", use_container_width=True)

        if guardar:
            key_limpia = nueva_key.strip().replace(" ", "").replace("\n", "")
            if not key_limpia or len(key_limpia) < 20:
                st.error("❌ La key parece incompleta. Cópiala completa desde console.groq.com")
            elif not key_limpia.startswith("gsk_"):
                st.error("❌ La key debe empezar con 'gsk_'. Verifica que la copiaste completa.")
            else:
                with st.spinner("Verificando..."):
                    ok = activar_ia(key_limpia)
                if ok:
                    st.success("✅ ¡IA activada! Ahora funciona Correos IA y el Asistente.")
                    st.balloons()
                    st.rerun()

    # Sección adicional solo para gerente
    if es_g:
        st.markdown("---")
        st.markdown("#### 📋 Configuración permanente en Streamlit Cloud (recomendada)")
        st.markdown("""
        Para que la IA quede activa automáticamente para **todos los usuarios** sin que cada uno tenga que activarla:

        1. Ve a tu app en **share.streamlit.io**
        2. Clic en **⋮** (tres puntos) → **Settings** → **Secrets**
        3. Pega exactamente esto:
        """)
        st.code('GROQ_API_KEY = "gsk_tu-key-aqui"', language="toml")
        st.markdown("4. Clic **Save** — la app se reinicia en 1 minuto y todos tienen IA automáticamente.")

        st.markdown("---")
        st.markdown("#### 📊 Estado del sistema")
        df=get_crm(); usuarios=get_usuarios()
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Proyectos en CRM",df.shape[0])
        c2.metric("Con valor",df[df["totalNum"]>0].shape[0])
        c3.metric("Usuarios activos",sum(1 for u in usuarios.values() if u.get("activo",True)))
        c4.metric("IA Groq","🟢 Activa" if ai_ok else "🔴 Inactiva")

def pg_auditoria():
    hdr("🔍","Auditoría Comercial","Análisis del equipo y el pipeline")
    df=get_crm()
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Total Proyectos",df.shape[0]); c2.metric("Pipeline",f"${int(df['totalNum'].sum())/1e9:.2f}B")
    c3.metric("Cotizaciones",df[df["estado"]=="cotizado"].shape[0])
    c4.metric("Rechazados",df[df["estado"]=="perdido"].shape[0]); c5.metric("Contratos",df[df["estado"]=="cerrado"].shape[0])
    st.markdown("---")
    st.markdown('<div class="al-r">❗ <b>0 contratos cerrados.</b> El cuello de botella está en el cierre, no en la prospección.</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        res=df[df["totalNum"]>0].groupby("comercial").agg(cotiz=("totalNum","count"),pipeline=("totalNum","sum")).reset_index()
        res["Pipeline $M"]=(res["pipeline"]/1e6).round(1)
        st.dataframe(res[["comercial","cotiz","Pipeline $M"]].rename(columns={"comercial":"Comercial","cotiz":"Cotiz."}),use_container_width=True,hide_index=True)
    with c2:
        if st.button("🤖 Análisis estratégico IA",use_container_width=True):
            with st.spinner("Analizando..."): r=ask_gemini("Análisis: top 5 proyectos más cercanos al cierre, patrón de rechazos, plan 7 días.",df.to_string(max_rows=84))
            st.markdown(r)

def pg_informes():
    hdr("📈","Informes Gerenciales","Análisis ejecutivo con gráficas")
    df=get_crm(); lm={"nuevo":"Lead","cotizado":"Enviado","negociacion":"Negoc.","cerrado":"Cerrado","perdido":"Perdido"}
    c1,c2,c3=st.columns(3)
    with c1:
        dc=df[df["totalNum"]>0].groupby("comercial")["totalNum"].sum().reset_index()
        dc["M"]=(dc["totalNum"]/1e6).round(1); dc["Com"]=dc["comercial"].str.split().str[0]
        fig=px.bar(dc.sort_values("M",ascending=True),x="M",y="Com",orientation="h",title="Pipeline ($M)",color="M",color_continuous_scale=["#1A9FCC","#00C896"])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(t=40))
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        est=df.groupby("estado").size().reset_index(name="n"); est["Estado"]=est["estado"].map(lm).fillna(est["estado"])
        fig2=px.pie(est,values="n",names="Estado",hole=0.48,color_discrete_sequence=["#1A9FCC","#F2A12E","#8B5CF6","#00C896","#E84040"])
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
    with c1: tipo_i=st.selectbox("Tipo:",["Informe Gerencial Ejecutivo","Reporte Pipeline","Análisis Equipo Comercial","Oportunidades Críticas"])
    with c2: notas_i=st.text_area("Instrucciones:",height=80,placeholder="Ej: Enfatizar en Nomad y Bosque San Vicente...")
    if st.button("🤖 Generar Informe Completo",use_container_width=True):
        prompt=f"Genera {tipo_i} para Ágora Tech. {f'Instrucciones: {notas_i}' if notas_i else ''}\nEstructura: ## RESUMEN EJECUTIVO ## MÉTRICAS ## ANÁLISIS ## ALERTAS ## RECOMENDACIONES ## PRÓXIMOS PASOS\nFecha: {datetime.now().strftime('%d %B %Y')}. Sin ---. Tono ejecutivo."
        with st.spinner("Generando..."): r=ask_gemini(prompt,df.to_string(max_rows=84))
        st.markdown(r)
        c1,c2=st.columns(2)
        c1.download_button("📥 .md",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.md")
        c2.download_button("📥 .txt",data=r,file_name=f"Informe_{datetime.now().strftime('%Y%m%d')}.txt")

def pg_pipeline():
    hdr("🎯","Pipeline Kanban","Vista de embudo por etapas")
    df=mis_proyectos(); etapas=[("nuevo","🔵 Lead"),("cotizado","🟡 Enviado"),("negociacion","🟠 Negoc."),("cerrado","🟢 Cerrado")]
    cols=st.columns(4)
    for i,(k,lbl) in enumerate(etapas):
        items=df[df["estado"]==k]; tot=int(items["totalNum"].sum())
        with cols[i]:
            st.markdown(f"**{lbl}**")
            st.markdown(f'<div style="font-size:11px;color:#8BA3BD;margin-bottom:12px">{len(items)} · ${tot/1e6:.1f}M</div>',unsafe_allow_html=True)
            for _,r in items.iterrows():
                tn=int(r.get("totalNum") or 0); nota=str(r.get("notas","") or "")
                st.markdown(f"""<div style='background:white;border:1px solid #E3EAF3;border-radius:8px;padding:11px;margin-bottom:8px'>
                  <div style='font-family:Sora,sans-serif;font-size:11.5px;font-weight:700;color:#04111E;margin-bottom:2px'>{str(r["nombre"])[:24]}</div>
                  <div style='font-size:10.5px;color:#8BA3BD;margin-bottom:4px'>{str(r.get("comercial","—")).split()[0]}</div>
                  <div style='font-family:Sora,sans-serif;font-size:13px;font-weight:800;color:#05875D'>{fc(tn) if tn else "—"}</div>
                </div>""",unsafe_allow_html=True)

def pg_encuestas():
    hdr("📊","Encuestas de Prospectos","Formulario de información preliminar")
    with st.form("prosp_form"):
        c1,c2=st.columns(2)
        with c1:
            nom_e=st.text_input("Nombre del Edificio *"); cont_e=st.text_input("Contacto *")
        with c2:
            rol_e=st.selectbox("Rol",["Administrador","Propietario","Miembro del Consejo","Presidente"])
            com_e=st.selectbox("Comercial",COMS)
        vig_e=st.radio("¿Tiene vigilancia?",["Sí","No"],horizontal=True)
        c1,c2=st.columns(2)
        with c1: cost_e=st.number_input("Costo vigilancia ($/mes)",min_value=0,value=0,step=100_000,format="%d")
        with c2: vigh_e=st.text_input("Contrato hasta",placeholder="Nov 2026")
        acc_e=st.text_area("Adultos mayores / Discapacidad"); notas_e=st.text_area("Notas del comercial")
        if st.form_submit_button("🤖 Analizar con IA y Guardar",use_container_width=True):
            if not nom_e: st.error("Nombre del edificio obligatorio")
            elif not ai_activa(): st.error("Activa la IA en ⚙️ Configuración")
            else:
                prompt=f"Analiza este prospecto para Ágora Tech:\nEdificio: {nom_e} | Contacto: {cont_e} ({rol_e}) | Vigilancia: {'SÍ $'+f'{int(cost_e):,}'+'/mes hasta '+vigh_e if vig_e=='Sí' and cost_e>0 else 'NO'}\nAdultos mayores: {acc_e or 'No reportado'} | Comercial: {com_e}\n## VIABILIDAD ## AHORRO POTENCIAL ## ESTRATEGIA ## OBJECIONES ## PRÓXIMOS PASOS\nNegrilla para datos clave."
                with st.spinner("Analizando..."): r=ask_gemini(prompt)
                st.markdown(r); st.success(f"✅ Prospecto {nom_e} analizado")

def pg_usuarios():
    hdr("👥","Gestión de Usuarios","Solo gerente — agregar, editar y administrar accesos")
    usuarios=get_usuarios()
    st.markdown("#### Usuarios registrados")
    for ukey,ud in usuarios.items():
        activo=ud.get("activo",True); cols=st.columns([2,2,1.5,1,1,1])
        cols[0].markdown(f"**{ud['nombre']}**"); cols[1].markdown(f"`{ukey}`")
        cols[2].markdown(ud["rol"].capitalize())
        cols[3].markdown(f'<span class="{"b-g" if activo else "b-r"}">{"Activo" if activo else "Inactivo"}</span>',unsafe_allow_html=True)
        if cols[4].button("✏️",key=f"edit_{ukey}"): st.session_state[f"editing_user"]=ukey
        if cols[5].button("🔒" if activo else "🔓",key=f"tog_{ukey}"):
            st.session_state.usuarios_db[ukey]["activo"]=not activo; st.rerun()
        st.markdown('<div style="border-bottom:1px solid #E3EAF3;margin:6px 0"></div>',unsafe_allow_html=True)
    editing=st.session_state.get("editing_user","")
    if editing and editing in usuarios:
        ud_e=usuarios[editing]
        st.markdown(f"#### ✏️ Editando: {ud_e['nombre']}")
        with st.form("edit_user_form"):
            c1,c2=st.columns(2)
            with c1:
                new_n=st.text_input("Nombre",value=ud_e["nombre"])
                new_p=st.text_input("Nueva contraseña (vacío=no cambiar)",type="password")
            with c2:
                new_r=st.selectbox("Rol",["gerente","comercial"],index=0 if ud_e["rol"]=="gerente" else 1)
                new_c=st.selectbox("Comercial",COMS,index=COMS.index(ud_e["comercial"]) if ud_e["comercial"] in COMS else 0)
            if st.form_submit_button("💾 Guardar",use_container_width=True):
                st.session_state.usuarios_db[editing].update({"nombre":new_n,"rol":new_r,"comercial":new_c})
                if new_p: st.session_state.usuarios_db[editing]["pass"]=new_p
                st.success(f"✅ {editing} actualizado"); st.session_state.pop("editing_user",None); st.rerun()
    st.markdown("---")
    st.markdown("#### ➕ Agregar nuevo usuario")
    with st.form("add_user_form"):
        c1,c2=st.columns(2)
        with c1:
            nu_user=st.text_input("Usuario *",placeholder="ej: carlos")
            nu_nombre=st.text_input("Nombre completo *")
            nu_pass=st.text_input("Contraseña *",type="password")
        with c2:
            nu_rol=st.selectbox("Rol",["comercial","gerente"])
            nu_com=st.selectbox("Comercial asignado",COMS)
        if st.form_submit_button("➕ Crear usuario",use_container_width=True):
            if not nu_user or not nu_nombre or not nu_pass: st.error("Todos los campos son obligatorios")
            elif nu_user.lower() in usuarios: st.error(f"'{nu_user}' ya existe")
            else:
                st.session_state.usuarios_db[nu_user.lower()]={"pass":nu_pass,"nombre":nu_nombre,"rol":nu_rol,"comercial":nu_com,"activo":True}
                st.success(f"✅ Usuario **{nu_user}** creado"); st.rerun()

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    pg_login()
else:
    sidebar()
    pg = st.session_state.get("page","Dashboard")

    if   pg=="Dashboard":         pg_dashboard()
    elif pg=="Proyectos":         pg_proyectos()
    elif pg=="Nueva Cotización":  pg_nueva_cotizacion()
    elif pg=="Actualizar Estado": pg_actualizar()
    elif pg=="Edificios":         pg_edificios()
    elif pg=="Calendario":        pg_calendario()
    elif pg=="Correos IA":        pg_correos()
    elif pg=="Asistente IA":      pg_asistente()
    elif pg=="Configuración":     pg_configuracion()
    elif pg=="Auditoría":         pg_auditoria()
    elif pg=="Informes":          pg_informes()
    elif pg=="Pipeline":          pg_pipeline()
    elif pg=="Encuestas":         pg_encuestas()
    elif pg=="Usuarios":          pg_usuarios()
    else:                         pg_dashboard()
