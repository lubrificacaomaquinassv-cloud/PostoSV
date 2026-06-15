import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from supabase import create_client

# ═══════════════════════════════════════════════════════════════════════
# PAINEL POSTO SV — somente leitura (views consolidadas). Sem lançamentos.
# Entradas NF e saídas comboio → app Financeiro (combustivel_controle).
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Posto SV - SIGCF",
    layout="wide",
    page_icon="⛽",
    initial_sidebar_state="collapsed",
)

LOGO_URL = "https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg"

CAP_S500 = 15000
CAP_S10 = 5000
CAP_GAS = 5000

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

VW_SALDO_S500 = "vw_saldo_posto_v2"
VW_SALDO_S10 = "vw_saldo_s10_posto"
VW_SALDO_GAS = "vw_saldo_gasolina_posto"
VW_ABAST = "vw_painel_posto_abastecimento"
VW_ENTRADAS = "vw_painel_entradas_posto"
VW_SAIDAS = "vw_painel_saidas_comboio"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');
[data-testid="stAppViewContainer"]{background:#0a1409;}
[data-testid="stSidebar"]{background:#111c10;border-right:1px solid #1e2e1c;}
[data-testid="stHeader"]{background:#0a1409;}
h1,h2,h3,h4,p,span,label{color:#e8edd0;}
h1{font-family:'Barlow Condensed',sans-serif;letter-spacing:1px;}
.stCaption,[data-testid="stCaptionContainer"] p{color:#8aab80!important;}
div[data-testid="stSelectbox"] label{color:#8aab80!important;font-family:'Barlow Condensed',sans-serif;
 text-transform:uppercase;letter-spacing:1px;font-size:12px!important;}
div[data-baseweb="select"] > div{background:#0d180c!important;border:1px solid #1e2e1c!important;color:#e8edd0!important;}
div[data-baseweb="select"] div{color:#e8edd0!important;}
div[data-baseweb="select"] svg{fill:#8aab80;}
ul[data-testid="stSelectboxVirtualDropdown"],div[data-baseweb="popover"] ul{background:#111c10!important;}
div[data-baseweb="popover"] li{color:#e8edd0!important;}
div[data-testid="metric-container"],div[data-testid="stMetric"]{
 background:#0d180c;border:1px solid #4a9e3f;border-radius:10px;padding:12px 18px;}
div[data-testid="stMetric"] label,div[data-testid="metric-container"] label{color:#8aab80!important;}
div[data-testid="stMetricValue"]{color:#6fcf60!important;font-family:'Barlow Condensed',sans-serif;}
.logo-box{background:#ffffff;border-radius:10px;padding:8px 12px;display:inline-block;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#8aab80;
 border-left:4px solid #4a9e3f;padding-left:10px;margin:4px 0 10px;}
.tank-row{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px;}
.tank-card{background:#111c10;border:1px solid #1e2e1c;border-radius:12px;padding:18px 14px;
 flex:1;min-width:200px;display:flex;flex-direction:column;align-items:center;gap:6px;}
.tank-label{font-family:'Barlow Condensed',sans-serif;font-size:11px;font-weight:700;
 letter-spacing:1px;text-transform:uppercase;color:#8aab80;text-align:center;}
.tank-outer{width:78px;height:140px;background:#0d180c;border:2px solid #1e2e1c;border-radius:10px;
 position:relative;overflow:hidden;margin:4px 0;}
.tank-liquid{position:absolute;bottom:0;left:0;right:0;border-radius:0 0 8px 8px;}
.tank-pct{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
 font-family:'Barlow Condensed',sans-serif;font-size:22px;font-weight:700;color:#e8edd0;
 text-shadow:0 1px 4px rgba(0,0,0,.8);z-index:2;}
.tank-vol{font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:700;}
.tank-cap{font-size:11px;color:#8aab80;font-family:'Barlow Condensed',sans-serif;}
.tank-badge{font-family:'Barlow Condensed',sans-serif;font-size:10px;font-weight:700;
 letter-spacing:1px;padding:4px 12px;border-radius:6px;margin-top:4px;}
</style>
""", unsafe_allow_html=True)


def fmt_l(v):
    try:
        return f"{float(v):,.1f} L".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "0,0 L"


def norm_fuel(ft):
    return str(ft or "").strip().upper()


def fuel_family(ft):
    f = norm_fuel(ft)
    if "S-500" in f or "S500" in f:
        return "s500"
    if ("S-10" in f or "S10" in f) and "S-500" not in f:
        return "s10"
    if "GASOLINA" in f:
        return "gas"
    return "outro"


def tank_status(pct, accent):
    if pct <= 20:
        return "NÍVEL CRÍTICO", "#e74c3c", "#2a1010"
    if pct <= 40:
        return "NÍVEL BAIXO", "#d4a017", "#2a2200"
    return "NÍVEL OK", accent, "#101820"


def tank_card_html(pct, saldo, cap, title, accent):
    pct = min(100.0, max(0.0, float(pct)))
    badge, badge_col, badge_bg = tank_status(pct, accent)
    liquid = accent if pct > 40 else "#d4a017" if pct > 20 else "#e74c3c"
    return f"""
<div class="tank-card">
  <div class="tank-label">{title}<br><span class="tank-cap">Tanque {fmt_l(cap)}</span></div>
  <div class="tank-outer">
    <div class="tank-liquid" style="height:{pct:.1f}%;background:{liquid};"></div>
    <div class="tank-pct">{pct:.1f}%</div>
  </div>
  <div class="tank-vol" style="color:{accent}">{fmt_l(saldo)}</div>
  <div class="tank-badge" style="color:{badge_col};background:{badge_bg}">{badge}</div>
</div>"""


def dark_table(df, height=380):
    if df.empty:
        st.info("Nenhum registro no período.")
        return
    rows = "".join(
        "<tr>" + "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #1e2e1c;color:#e8edd0;font-size:12px;">{v}</td>'
            for v in row) + "</tr>"
        for _, row in df.iterrows())
    headers = "".join(
        f'<th style="padding:7px 10px;background:#111c10;color:#8aab80;font-size:10px;'
        f'font-weight:700;text-transform:uppercase;letter-spacing:1px;border-bottom:2px solid #1e2e1c;">{c}</th>'
        for c in df.columns)
    st.markdown(
        f'<div style="max-height:{height}px;overflow-y:auto;overflow-x:auto;border:1px solid #1e2e1c;border-radius:10px;">'
        f'<table style="width:100%;border-collapse:collapse;background:#0d180c;font-family:Barlow Condensed,sans-serif;">'
        f'<thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def parse_ts(series):
    raw = series.astype(str).str.strip()
    has_tz = raw.str.contains(r"[+-]\d{2}:\d{2}|Z$", regex=True, na=False)
    out = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    if has_tz.any():
        out.loc[has_tz] = (
            pd.to_datetime(raw[has_tz], errors="coerce", utc=True)
            .dt.tz_convert("America/Sao_Paulo")
            .dt.tz_localize(None)
        )
    if (~has_tz).any():
        out.loc[~has_tz] = pd.to_datetime(raw[~has_tz], errors="coerce")
    return out


def periodo_opcoes():
    hoje = date.today()
    first = hoje.replace(day=1)
    last_prev = first - timedelta(days=1)
    return ["Hoje", "Este mês", f"{MESES_PT[last_prev.month - 1]}/{last_prev.year}"]


def periodo_bounds(label):
    hoje = date.today()
    if label == "Hoje":
        return hoje, hoje, 1
    if label == "Este mês":
        ini = hoje.replace(day=1)
        dias = max(1, (hoje - ini).days + 1)
        return ini, hoje, dias
    first = hoje.replace(day=1)
    last_prev = first - timedelta(days=1)
    ini = last_prev.replace(day=1)
    dias = calendar.monthrange(last_prev.year, last_prev.month)[1]
    return ini, last_prev, dias


def saldo_from_view(row, cap):
    if not row:
        return 0.0, 0.0
    saldo = float(row.get("saldo_litros") or row.get("saldo_estimado") or 0)
    pct = float(row.get("pct_restante") or row.get("pct_tanque") or 0)
    if pct == 0 and cap > 0:
        pct = min(100.0, (saldo / cap) * 100)
    return saldo, pct


supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=60)
def load_view_row(name):
    try:
        res = supabase.table(name).select("*").limit(1).execute()
        return (res.data or [{}])[0]
    except Exception:
        return {}


@st.cache_data(ttl=30)
def load_view_df(name, order_col="created_at", limit=5000):
    try:
        res = (
            supabase.table(name)
            .select("*")
            .order(order_col, desc=True)
            .limit(limit)
            .execute()
        )
        return pd.DataFrame(res.data or [])
    except Exception:
        return pd.DataFrame()


col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.markdown(f'<div class="logo-box"><img src="{LOGO_URL}" width="100"></div>', unsafe_allow_html=True)
with col_titulo:
    st.title("⛽ Posto de Abastecimento — SV")
    st.caption("SIGCF | Controladoria Bataguassu-MS · Sede · somente consulta (views consolidadas)")

st.divider()

st.caption(
    "Dados do PWA e do banco via views. Lançamento de NF e saída comboio → app Financeiro."
)

s500_row = load_view_row(VW_SALDO_S500)
s10_row = load_view_row(VW_SALDO_S10)
gas_row = load_view_row(VW_SALDO_GAS)

saldo_s500, pct_s500 = saldo_from_view(s500_row, CAP_S500)
saldo_s10, pct_s10 = saldo_from_view(s10_row, CAP_S10)
saldo_gas, pct_gas = saldo_from_view(gas_row, CAP_GAS)

st.markdown('<div class="sec">Relógio de estoque — tanques do posto</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="tank-row">'
    + tank_card_html(pct_s500, saldo_s500, CAP_S500, "Diesel S-500 Aditivado", "#3498db")
    + tank_card_html(pct_s10, saldo_s10, CAP_S10, "Diesel S-10", "#7ab0d4")
    + tank_card_html(pct_gas, saldo_gas, CAP_GAS, "Gasolina Comum", "#e67e22")
    + "</div>",
    unsafe_allow_html=True,
)

opcoes_periodo = periodo_opcoes()
idx_default = 0
filtro = st.selectbox(
    "Selecionar período:",
    options=opcoes_periodo,
    index=idx_default,
    key="sel_periodo_posto",
)
ini, fim, dias_ref = periodo_bounds(filtro)

df_ab = load_view_df(VW_ABAST)
if not df_ab.empty:
    df_ab["dt"] = parse_ts(df_ab["created_at"])
    df_ab["data_ref"] = df_ab["dt"].dt.date
    col_comb = "combustivel" if "combustivel" in df_ab.columns else "fuel_type"
    col_lit = "litros" if "litros" in df_ab.columns else "liters"
    df_ab["familia"] = df_ab[col_comb].map(fuel_family)
    df_ab["liters"] = pd.to_numeric(df_ab[col_lit], errors="coerce").fillna(0)
    mask = (df_ab["data_ref"] >= ini) & (df_ab["data_ref"] <= fim)
    df_per = df_ab.loc[mask].copy()
else:
    df_per = pd.DataFrame()


def litros_familia(df, fam):
    if df.empty:
        return 0.0
    return float(df.loc[df["familia"] == fam, "liters"].sum())


tot_s500 = litros_familia(df_per, "s500")
tot_s10 = litros_familia(df_per, "s10")
tot_gas = litros_familia(df_per, "gas")

st.markdown(f'<div class="sec">Consumo · {filtro} · litros/dia (média)</div>', unsafe_allow_html=True)
k1, k2, k3 = st.columns(3)
k1.metric("Diesel S-500", fmt_l(tot_s500 / dias_ref), f"{fmt_l(tot_s500)} no período")
k2.metric("Diesel S-10", fmt_l(tot_s10 / dias_ref), f"{fmt_l(tot_s10)} no período")
k3.metric("Gasolina", fmt_l(tot_gas / dias_ref), f"{fmt_l(tot_gas)} no período")

st.markdown('<div class="sec">Frotas abastecidas no posto</div>', unsafe_allow_html=True)
if df_per.empty:
    st.info(f"Nenhum abastecimento em {filtro}.")
else:
    show = df_per.sort_values("dt", ascending=False).copy()
    show["Data/Hora"] = show["dt"].dt.strftime("%d/%m/%Y %H:%M")
    show["Litros"] = show["liters"].apply(
        lambda v: f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col_frota = "frota" if "frota" in show.columns else "vehicle"
    col_comb = "combustivel" if "combustivel" in show.columns else "fuel_type"
    col_h = "horimetro" if "horimetro" in show.columns else "hourmeter"
    col_op = "operador" if "operador" in show.columns else "operator_driver"
    tbl = show.rename(columns={
        col_frota: "Frota",
        col_comb: "Combustível",
        col_h: "Horím./Odôm.",
        col_op: "Operador",
    })[["Data/Hora", "Frota", "Combustível", "Litros", "Horím./Odôm.", "Operador"]]
    dark_table(tbl, height=420)

st.divider()
c_ent, c_trf = st.columns(2)
with c_ent:
    st.markdown('<div class="sec">Últimas entradas (NF)</div>', unsafe_allow_html=True)
    df_ent = load_view_df(VW_ENTRADAS, order_col="data").head(8)
    if df_ent.empty:
        st.caption("Nenhuma entrada registrada.")
    else:
        de = df_ent.copy()
        de["Data"] = pd.to_datetime(de["data"], errors="coerce").dt.strftime("%d/%m/%Y")
        de["Litros"] = de["quantidade_l"].apply(fmt_l)
        dark_table(
            de.rename(columns={
                "combustivel": "Combustível",
                "nota_fiscal": "NF",
                "fornecedor": "Fornecedor",
            })[["Data", "Combustível", "NF", "Litros", "Fornecedor"]],
            height=220,
        )
with c_trf:
    st.markdown('<div class="sec">Últimas saídas para comboio</div>', unsafe_allow_html=True)
    df_tr = load_view_df(VW_SAIDAS, order_col="data").head(8)
    if df_tr.empty:
        st.caption("Nenhuma transferência registrada.")
    else:
        dt = df_tr.copy()
        dt["Data"] = pd.to_datetime(dt["data"], errors="coerce").dt.strftime("%d/%m/%Y")
        dt["Litros"] = dt["quantidade_l"].apply(fmt_l)
        dark_table(
            dt.rename(columns={
                "combustivel": "Combustível",
                "destino": "Destino",
                "observacao": "Obs",
            })[["Data", "Combustível", "Litros", "Destino", "Obs"]],
            height=220,
        )

st.divider()
st.caption("SIGCF | Posto SV | Somente consulta · Lançamentos no Financeiro")
