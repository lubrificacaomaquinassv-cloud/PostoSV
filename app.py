import calendar
from datetime import date, timedelta
from io import BytesIO

import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Posto SV - SIGCF",
    layout="wide",
    page_icon="⛽",
    initial_sidebar_state="collapsed",
)

from sigcf_auth import exigir_acesso, logo_html

exigir_acesso("Posto SV — Painel")

CAP_S500 = 10000
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
.logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;
 border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}
.logo-frame img{display:block;border-radius:8px;}
.sec{font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;
 letter-spacing:2px;text-transform:uppercase;color:#8aab80;
 border-left:4px solid #4a9e3f;padding-left:10px;margin:4px 0 10px;}
.pump-row{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:4px;}
.pump-stock{background:#111c10;border:1px solid #1e2e1c;border-radius:12px;padding:18px 14px;
 text-align:center;font-family:'Barlow Condensed',sans-serif;}
.pump-stock-title{font-size:11px;font-weight:700;color:#8aab80;text-transform:uppercase;
 letter-spacing:1.2px;margin-bottom:10px;}
.pump-stock-saldo{font-size:22px;font-weight:700;margin-top:6px;}
.pump-stock-cap{font-size:11px;color:#8aab80;margin-top:2px;}
.pump-stock-badge{display:inline-block;margin-top:8px;font-size:10px;font-weight:700;
 padding:3px 12px;border-radius:12px;text-transform:uppercase;}
.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
.kpi-pump{background:#111c10;border:1px solid #1e2e1c;border-radius:12px;padding:16px 18px;
 font-family:'Barlow Condensed',sans-serif;min-height:130px;}
.kpi-pump-title{font-size:11px;font-weight:700;color:#8aab80;text-transform:uppercase;
 letter-spacing:1.2px;margin-bottom:12px;}
.kpi-pump-body{display:flex;align-items:center;justify-content:space-between;gap:10px;}
.kpi-pump-val{font-size:32px;font-weight:700;color:#e8edd0;line-height:1;}
.kpi-pump-sub{font-size:11px;color:#8aab80;margin-top:10px;}
.stButton button,.stDownloadButton button,[data-testid="stDownloadButton"] button{
 background:#4a9e3f!important;color:#ffffff!important;border:1px solid #6fcf60!important;
 font-family:'Barlow Condensed',sans-serif;font-weight:700;letter-spacing:1px;
 text-transform:uppercase;border-radius:8px;min-height:44px;}
.stButton button:hover,.stDownloadButton button:hover,[data-testid="stDownloadButton"] button:hover{
 background:#3d8534!important;}
.stDownloadButton button p,.stDownloadButton button span{color:#ffffff!important;}
.stTextInput input,[data-testid="stDateInput"] input{
 background:#dce6d2!important;color:#1a2818!important;border:1px solid #4a6644!important;border-radius:8px!important;}
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


def fmt_n(v):
    try:
        return f"{float(v):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "0,0"


def fill_color(pct, accent):
    if pct <= 20:
        return "#e74c3c"
    if pct <= 40:
        return "#d4a017"
    return accent


def level_badge(pct, accent):
    if pct <= 20:
        return "NÍVEL CRÍTICO", "#e74c3c", "#2a1010"
    if pct <= 40:
        return "NÍVEL BAIXO", "#d4a017", "#2a2200"
    return "NÍVEL OK", accent, "#101820"


def fuel_pump_svg(pct, color, uid, width=110, height=150):
    """Bomba de combustível com nível de preenchimento (formato KPI visual)."""
    pct = min(100.0, max(0.0, float(pct)))
    fz_top, fz_h = 82, 56
    fill_h = fz_h * pct / 100.0
    y_fill = fz_top + (fz_h - fill_h)
    pct_txt = f"{pct:.0f}%" if pct >= 10 else f"{pct:.1f}%"
    fs = 17 if width >= 90 else 11
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 110 150" xmlns="http://www.w3.org/2000/svg">
  <defs><clipPath id="pz{uid}"><rect x="27" y="{fz_top}" width="46" height="{fz_h}" rx="4"/></clipPath></defs>
  <rect x="12" y="138" width="86" height="7" rx="3.5" fill="#2c3440"/>
  <rect x="20" y="22" width="56" height="118" rx="9" fill="#4a5568" stroke="#1e2e1c" stroke-width="1.5"/>
  <rect x="28" y="30" width="40" height="20" rx="3" fill="#a8c0d8" opacity="0.45"/>
  <rect x="27" y="{y_fill:.2f}" width="46" height="{fill_h:.2f}" fill="{color}" clip-path="url(#pz{uid})"/>
  <rect x="70" y="55" width="18" height="12" rx="4" fill="#6a7585"/>
  <rect x="84" y="48" width="10" height="26" rx="5" fill="#8a95a5"/>
  <path d="M94 72 Q102 88 94 98" stroke="#1a1a1a" stroke-width="3" fill="none"/>
  <text x="52" y="108" text-anchor="middle" fill="#ffffff"
    font-family="Barlow Condensed,Arial,sans-serif" font-size="{fs}" font-weight="700">{pct_txt}</text>
</svg>"""


def fuel_pump_icon_svg(accent, uid, width=56, height=76):
    """Ícone estático da bomba (KPI) — cor cheia, sem % dinâmico."""
    fz_top, fz_h = 82, 56
    return f"""<svg width="{width}" height="{height}" viewBox="0 0 110 150" xmlns="http://www.w3.org/2000/svg">
  <defs><clipPath id="pi{uid}"><rect x="27" y="{fz_top}" width="46" height="{fz_h}" rx="4"/></clipPath></defs>
  <rect x="12" y="138" width="86" height="7" rx="3.5" fill="#2c3440"/>
  <rect x="20" y="22" width="56" height="118" rx="9" fill="#4a5568" stroke="#1e2e1c" stroke-width="1.5"/>
  <rect x="28" y="30" width="40" height="20" rx="3" fill="#a8c0d8" opacity="0.45"/>
  <rect x="27" y="{fz_top}" width="46" height="{fz_h}" fill="{accent}" clip-path="url(#pi{uid})"/>
  <rect x="70" y="55" width="18" height="12" rx="4" fill="#6a7585"/>
  <rect x="84" y="48" width="10" height="26" rx="5" fill="#8a95a5"/>
  <path d="M94 72 Q102 88 94 98" stroke="#1a1a1a" stroke-width="3" fill="none"/>
</svg>"""


def pump_stock_card(pct, saldo, cap, title, accent, uid):
    color = fill_color(pct, accent)
    badge, badge_col, badge_bg = level_badge(pct, accent)
    svg = fuel_pump_svg(pct, color, f"s{uid}", 110, 150)
    return f"""
<div class="pump-stock">
  <div class="pump-stock-title">{title}</div>
  {svg}
  <div class="pump-stock-saldo" style="color:{accent}">{fmt_l(saldo)}</div>
  <div class="pump-stock-cap">Tanque {fmt_l(cap)}</div>
  <div class="pump-stock-badge" style="color:{badge_col};background:{badge_bg}">{badge}</div>
</div>"""


def kpi_pump_card(title, liters, subtitle, accent, uid):
    """KPI: título, ícone bomba (cor fixa), valor grande."""
    svg = fuel_pump_icon_svg(accent, f"k{uid}", 56, 76)
    return f"""
<div class="kpi-pump">
  <div class="kpi-pump-title">{title}</div>
  <div class="kpi-pump-body">
    <div>{svg}</div>
    <div class="kpi-pump-val" style="color:{accent}">{fmt_n(liters)}</div>
  </div>
  <div class="kpi-pump-sub">{subtitle}</div>
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


def gerar_excel(df: pd.DataFrame) -> bytes:
    buf = BytesIO()
    df.to_excel(buf, index=False, sheet_name="Baixa posto")
    return buf.getvalue()


def df_baixa_posto(show: pd.DataFrame) -> pd.DataFrame:
    """Colunas para baixa no sistema legado (Excel)."""
    col_frota = "frota" if "frota" in show.columns else "vehicle"
    col_comb = "combustivel" if "combustivel" in show.columns else "fuel_type"
    col_h = "horimetro" if "horimetro" in show.columns else "hourmeter"
    col_frente = "frente" if "frente" in show.columns else "work_front"
    for cand in ("operador", "operator", "operator_driver"):
        col_op = cand if cand in show.columns else None
        if col_op:
            break
    else:
        col_op = "operador"

    out = pd.DataFrame({
        "Data/Hora": show["dt"].dt.strftime("%d/%m/%Y %H:%M"),
        "Frota": show[col_frota].fillna(""),
        "Combustível": show[col_comb].fillna(""),
        "Qtde (L)": show["liters"].round(1),
        "Horímetro/Odômetro": show[col_h].fillna("") if col_h in show.columns else "",
        "Frente de trabalho": show[col_frente].fillna("") if col_frente in show.columns else "",
        "Operador": show[col_op].fillna("") if col_op in show.columns else "",
    })
    return out.sort_values("Data/Hora", ascending=False)


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
    return [
        "Hoje",
        "Ontem",
        "Este mês",
        f"{MESES_PT[last_prev.month - 1]}/{last_prev.year}",
        "Escolher datas",
    ]


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
    """Saldo da view; % sempre pelo tamanho real do tanque no posto."""
    if not row:
        return 0.0, 0.0
    saldo = float(row.get("saldo_litros") or row.get("saldo_estimado") or 0)
    pct = min(100.0, (saldo / cap) * 100) if cap > 0 else 0.0
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


col_logo, col_titulo = st.columns([1.1, 5.9])
with col_logo:
    st.markdown(logo_html(118), unsafe_allow_html=True)
with col_titulo:
    st.title("⛽ Posto de Abastecimento — SV")
    st.caption("SIGCF | Controladoria Bataguassu-MS")

st.divider()

s500_row = load_view_row(VW_SALDO_S500)
s10_row = load_view_row(VW_SALDO_S10)
gas_row = load_view_row(VW_SALDO_GAS)

saldo_s500, pct_s500 = saldo_from_view(s500_row, CAP_S500)
saldo_s10, pct_s10 = saldo_from_view(s10_row, CAP_S10)
saldo_gas, pct_gas = saldo_from_view(gas_row, CAP_GAS)

st.markdown('<div class="sec">Relógio de estoque — tanques do posto</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="pump-row">'
    + pump_stock_card(pct_s500, saldo_s500, CAP_S500, "Diesel S-500 Aditivado", "#3498db", "500")
    + pump_stock_card(pct_s10, saldo_s10, CAP_S10, "Diesel S-10", "#7ab0d4", "10")
    + pump_stock_card(pct_gas, saldo_gas, CAP_GAS, "Gasolina Comum", "#e67e22", "gas")
    + "</div>",
    unsafe_allow_html=True,
)

opcoes_periodo = periodo_opcoes()
idx_default = 0
filtro = st.selectbox(
    "Período para tabela e Excel:",
    options=opcoes_periodo,
    index=idx_default,
    key="sel_periodo_posto",
)
if filtro == "Escolher datas":
    fc1, fc2 = st.columns(2)
    with fc1:
        data_ini = st.date_input("De", value=date.today(), key="baixa_de", format="DD/MM/YYYY")
    with fc2:
        data_fim = st.date_input("Até", value=date.today(), key="baixa_ate", format="DD/MM/YYYY")
    ini, fim = data_ini, data_fim
    if ini > fim:
        ini, fim = fim, ini
    dias_ref = max(1, (fim - ini).days + 1)
    filtro_label = f"{ini.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
elif filtro == "Ontem":
    ontem = date.today() - timedelta(days=1)
    ini = fim = ontem
    dias_ref = 1
    filtro_label = f"Ontem ({ontem.strftime('%d/%m/%Y')})"
else:
    ini, fim, dias_ref = periodo_bounds(filtro)
    filtro_label = filtro

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

st.markdown(f'<div class="sec">Consumo · {filtro_label} · litros/dia (média)</div>', unsafe_allow_html=True)
pct_uso_s500 = min(100.0, (tot_s500 / CAP_S500) * 100) if CAP_S500 else 0
pct_uso_s10 = min(100.0, (tot_s10 / CAP_S10) * 100) if CAP_S10 else 0
pct_uso_gas = min(100.0, (tot_gas / CAP_GAS) * 100) if CAP_GAS else 0
st.markdown(
    '<div class="kpi-row">'
    + kpi_pump_card(
        "Diesel S-500 · L/dia",
        tot_s500 / dias_ref,
        f"{fmt_l(tot_s500)} no período · {pct_uso_s500:.1f}% do tanque",
        "#3498db", "500",
    )
    + kpi_pump_card(
        "Diesel S-10 · L/dia",
        tot_s10 / dias_ref,
        f"{fmt_l(tot_s10)} no período · {pct_uso_s10:.1f}% do tanque",
        "#7ab0d4", "10",
    )
    + kpi_pump_card(
        "Gasolina · L/dia",
        tot_gas / dias_ref,
        f"{fmt_l(tot_gas)} no período · {pct_uso_gas:.1f}% do tanque",
        "#e67e22", "gas",
    )
    + "</div>",
    unsafe_allow_html=True,
)

st.markdown('<div class="sec">Frotas abastecidas no posto</div>', unsafe_allow_html=True)
st.caption(
    f"Período: **{filtro_label}** — exporte o Excel para baixa no sistema de controle. "
    "Se não baixou no dia, use **Ontem** ou **Escolher datas**."
)
if df_per.empty:
    st.info(f"Nenhum abastecimento no período ({filtro_label}).")
else:
    show = df_per.sort_values("dt", ascending=False).copy()
    df_xlsx = df_baixa_posto(show)
    show["Data/Hora"] = show["dt"].dt.strftime("%d/%m/%Y %H:%M")
    show["Litros"] = show["liters"].apply(
        lambda v: f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    col_frota = "frota" if "frota" in show.columns else "vehicle"
    col_comb = "combustivel" if "combustivel" in show.columns else "fuel_type"
    col_h = "horimetro" if "horimetro" in show.columns else "hourmeter"
    col_frente = "frente" if "frente" in show.columns else "work_front"
    for cand in ("operador", "operator", "operator_driver"):
        col_op = cand if cand in show.columns else None
        if col_op:
            break
    else:
        col_op = "operador"
    cols_tbl = ["Data/Hora", "Frota", "Combustível", "Litros", "Horím./Odôm.", "Operador"]
    rename = {
        col_frota: "Frota",
        col_comb: "Combustível",
        col_h: "Horím./Odôm.",
        col_op: "Operador",
    }
    if col_frente in show.columns:
        show["Frente"] = show[col_frente].fillna("")
        cols_tbl.insert(5, "Frente")
    tbl = show.rename(columns=rename)[cols_tbl]
    dark_table(tbl, height=420)
    st.download_button(
        "⬇️ Exportar Excel — baixa no sistema",
        data=gerar_excel(df_xlsx),
        file_name=f"posto_baixa_{ini:%Y%m%d}_{fim:%Y%m%d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary",
    )

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
st.caption("SIGCF | Posto SV | Controladoria Bataguassu-MS")
