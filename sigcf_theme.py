"""Tema visual SIGCF v5 — Lovable + Segoe UI (compartilhado entre apps Streamlit)."""
from __future__ import annotations

import streamlit as st

KICKER_DEFAULT = "Santa Virgínia Agropecuária e Florestal LTDA"

SIGCF_THEME_CSS = """
:root{
 --sigcf-bg:#0a1409;--sigcf-card:#0f1f12;--sigcf-border:#2a4030;
 --sigcf-text:#e8edd0;--sigcf-label:#8aab80;--sigcf-green:#6fcf60;
 --sigcf-gold:#ffd966;--sigcf-ouro:#c9a227;
 --sigcf-navy-a:#0a1628;--sigcf-navy-b:#0d2040;
 --sigcf-font:'Segoe UI','Segoe UI Variable',system-ui,-apple-system,sans-serif;
}
html,body,[class*="css"]{font-family:var(--sigcf-font)!important;}
[data-testid="stAppViewContainer"]{background:var(--sigcf-bg);padding-top:0!important;}
[data-testid="stSidebar"]{background:#111c10;border-right:1px solid var(--sigcf-border);}
header[data-testid="stHeader"]{
 height:0!important;min-height:0!important;max-height:0!important;
 padding:0!important;margin:0!important;overflow:hidden!important;
 visibility:hidden!important;display:none!important;background:transparent!important;}
section[data-testid="stMain"] > div{padding-top:0!important;}
[data-testid="stMainBlockContainer"]{padding-top:0.4rem!important;}
h1,h2,h3,h4,p,span,label{color:var(--sigcf-text);}
h1,h2,h3,h4{
 font-family:var(--sigcf-font)!important;font-weight:700;
 letter-spacing:0.08em;text-transform:uppercase;}
.stCaption,[data-testid="stCaptionContainer"] p{
 color:var(--sigcf-ouro)!important;font-family:var(--sigcf-font)!important;
 letter-spacing:0.1em;text-transform:uppercase!important;font-size:12px!important;}
.sigcf-header-band{
 background:linear-gradient(145deg,var(--sigcf-navy-a) 0%,var(--sigcf-navy-b) 100%);
 border:1px solid rgba(201,162,39,.35);border-bottom:2px solid var(--sigcf-green);
 border-radius:12px;padding:16px 20px;margin:0 0 24px;
 box-shadow:0 6px 24px rgba(0,0,0,.35);}
.sigcf-header-inner{display:flex;align-items:center;gap:18px;flex-wrap:wrap;}
.sigcf-header-text{flex:1;min-width:220px;}
.sigcf-kicker{
 font-size:11px;color:var(--sigcf-label);letter-spacing:0.16em;
 text-transform:uppercase;margin:0 0 6px;font-weight:600;}
.sigcf-title{
 font-size:1.75rem;color:var(--sigcf-text)!important;font-weight:700;
 letter-spacing:0.08em;text-transform:uppercase;margin:0;line-height:1.15;}
.sigcf-sub{
 font-size:11px;color:var(--sigcf-label)!important;letter-spacing:0.1em;
 text-transform:uppercase;margin:6px 0 0;font-weight:600;line-height:1.45;}
.logo-frame{background:transparent;border:2px solid var(--sigcf-ouro);
 border-radius:12px;padding:5px;display:inline-block;box-shadow:none;}
.logo-frame img{display:block;border-radius:8px;}
.sec{
 font-family:var(--sigcf-font)!important;font-size:12px;font-weight:700;
 letter-spacing:0.14em;text-transform:uppercase;color:var(--sigcf-gold);
 border-left:4px solid var(--sigcf-green);padding-left:10px;margin:8px 0 12px;}
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stWidgetLabel"] span,
.stTextInput label p,.stNumberInput label p,.stSelectbox label p,
.stDateInput label p,.stTextArea label p{
 color:var(--sigcf-label)!important;font-family:var(--sigcf-font)!important;
 font-size:11px!important;font-weight:600!important;
 letter-spacing:0.1em!important;text-transform:uppercase!important;}
.stMarkdown p strong,
[data-testid="stMarkdownContainer"] p strong{
 color:var(--sigcf-gold)!important;font-family:var(--sigcf-font)!important;
 font-weight:700!important;letter-spacing:0.12em!important;
 text-transform:uppercase!important;font-size:13px!important;}
.stTextInput input,.stNumberInput input,.stTextArea textarea,
[data-testid="stDateInput"] input,[data-testid="stTimeInput"] input{
 background:#dce6d2!important;color:#1a2818!important;
 border:1px solid var(--sigcf-border)!important;border-radius:8px!important;
 font-family:var(--sigcf-font)!important;}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus,
[data-testid="stDateInput"] input:focus,[data-testid="stTimeInput"] input:focus{
 border-color:var(--sigcf-green)!important;box-shadow:0 0 0 2px rgba(111,207,96,.45)!important;}
div[data-baseweb="select"] > div{
 background:#dce6d2!important;border:1px solid var(--sigcf-border)!important;
 color:#1a2818!important;border-radius:8px!important;
 font-family:var(--sigcf-font)!important;}
div[data-baseweb="select"] div{color:#1a2818!important;}
div[data-baseweb="select"] svg{fill:#4a6644!important;}
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"] ul{background:#e8edd0!important;}
div[data-baseweb="popover"] li{color:#1a2818!important;font-family:var(--sigcf-font)!important;}
[data-testid="stNumberInput"] button{
 background:#cdd9c4!important;border-color:var(--sigcf-border)!important;color:#1a2818!important;}
[data-testid="stForm"]{
 background:var(--sigcf-card)!important;border:1px solid var(--sigcf-border)!important;
 border-radius:12px;padding:12px 16px;}
[data-testid="stVerticalBlockBorderWrapper"]{
 background:var(--sigcf-card)!important;border-color:var(--sigcf-border)!important;}
div[data-testid="stMetric"]{
 background:var(--sigcf-card);border:1px solid var(--sigcf-green);
 border-left:4px solid var(--sigcf-green);border-radius:8px;padding:12px 16px;}
div[data-testid="stMetric"] label{
 color:var(--sigcf-label)!important;font-family:var(--sigcf-font)!important;
 font-size:11px!important;letter-spacing:0.12em!important;text-transform:uppercase!important;}
div[data-testid="stMetricValue"]{
 color:var(--sigcf-gold)!important;font-family:var(--sigcf-font)!important;
 font-weight:700!important;font-size:1.6rem!important;}
.stTabs [data-baseweb="tab-list"]{
 background:linear-gradient(180deg,var(--sigcf-navy-b) 0%,var(--sigcf-card) 100%);
 border-bottom:2px solid var(--sigcf-green)!important;gap:4px;
 padding:8px 10px 0;border-radius:0 0 10px 10px;margin-top:0;}
.stTabs [data-baseweb="tab"],.stTabs button[data-baseweb="tab"]{
 color:var(--sigcf-label)!important;font-family:var(--sigcf-font)!important;
 font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
 font-size:12px!important;border-bottom:3px solid transparent!important;
 padding-bottom:10px!important;background:transparent!important;}
.stTabs [data-baseweb="tab"]:hover,.stTabs button[data-baseweb="tab"]:hover{color:var(--sigcf-gold)!important;}
.stTabs button[data-baseweb="tab"][aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"]{
 color:var(--sigcf-gold)!important;border-bottom:3px solid var(--sigcf-green)!important;}
.stTabs [data-baseweb="tab-highlight"]{
 background-color:var(--sigcf-green)!important;height:3px!important;bottom:0!important;}
.stTabs [data-baseweb="tab-border"]{background-color:var(--sigcf-border)!important;height:1px!important;}
.stTabs button[data-baseweb="tab"] p,.stTabs [data-baseweb="tab"] p{
 color:inherit!important;font-size:12px!important;letter-spacing:0.12em!important;text-transform:uppercase!important;}
[data-testid="stTabs"]{margin-top:8px;margin-bottom:14px;}
[data-testid="stExpander"]{
 background:var(--sigcf-card)!important;border:1px solid var(--sigcf-border)!important;border-radius:10px;}
[data-testid="stExpander"] summary{
 color:var(--sigcf-gold)!important;font-family:var(--sigcf-font)!important;
 text-transform:uppercase;letter-spacing:0.08em;font-weight:600;}
div[data-testid="stCheckbox"] label span{color:var(--sigcf-text)!important;}
.stButton button,[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button,
.stTextInput input,.stNumberInput input,[data-testid="stDateInput"] input,
div[data-baseweb="select"] > div{
 transition:border-color .18s ease,background .18s ease,box-shadow .18s ease,color .18s ease;}
.main .stButton > button{
 background:rgba(15,31,18,.88)!important;color:var(--sigcf-text)!important;
 border:1px solid var(--sigcf-green)!important;
 font-family:var(--sigcf-font)!important;font-weight:700;letter-spacing:0.12em;
 text-transform:uppercase;border-radius:8px;font-size:0.76rem!important;
 padding:0.45rem 0.85rem!important;min-height:2.25rem!important;}
.main .stButton > button:hover{
 background:rgba(111,207,96,.14)!important;border-color:var(--sigcf-ouro)!important;}
.main .stButton > button p{color:var(--sigcf-text)!important;
 font-size:0.76rem!important;letter-spacing:0.12em!important;}
[data-testid="stFormSubmitButton"] button,[data-testid="stDownloadButton"] button{
 background:linear-gradient(180deg,#5aad4f,#4a9e3f)!important;color:#fff!important;
 border:2px solid var(--sigcf-ouro)!important;
 font-family:var(--sigcf-font)!important;font-weight:700;letter-spacing:0.12em;
 text-transform:uppercase;border-radius:8px;font-size:0.82rem!important;
 padding:0.55rem 1rem!important;min-height:2.5rem!important;
 box-shadow:0 2px 14px rgba(0,0,0,.28)!important;}
[data-testid="stFormSubmitButton"] button:hover,[data-testid="stDownloadButton"] button:hover{
 background:linear-gradient(180deg,#4a9e3f,#3d8534)!important;
 border-color:var(--sigcf-gold)!important;
 box-shadow:0 4px 18px rgba(111,207,96,.18)!important;}
[data-testid="stFormSubmitButton"] button p,[data-testid="stDownloadButton"] button p{
 color:#ffffff!important;font-size:0.82rem!important;letter-spacing:0.12em!important;}
hr,.sigcf-op-sep{
 border:none!important;height:1px!important;margin:20px 0!important;
 background:linear-gradient(90deg,transparent,var(--sigcf-border) 20%,var(--sigcf-green) 50%,var(--sigcf-border) 80%,transparent)!important;}
.sigcf-op-sep{display:block;width:100%;}
.sigcf-footer{
 text-align:center;color:var(--sigcf-label)!important;font-size:10px!important;
 letter-spacing:0.16em;text-transform:uppercase;padding:18px 0 6px;
 border-top:1px solid var(--sigcf-border);margin-top:28px;}
[data-testid="stAlert"]{
 border-radius:10px!important;font-family:var(--sigcf-font)!important;
 background:var(--sigcf-card)!important;border:1px solid var(--sigcf-border)!important;}
[data-testid="stAlert"] p,[data-testid="stAlert"] span{color:var(--sigcf-text)!important;
 font-size:12px!important;letter-spacing:0.04em;}
[data-testid="stMetric"]{transition:box-shadow .18s ease;}
div[data-testid="stMetric"]:hover{box-shadow:0 0 0 1px rgba(111,207,96,.35);}
.main .block-container{padding-top:0.4rem!important;padding-bottom:2.5rem;max-width:1180px;}
.sigcf-table-wrap{border:1px solid var(--sigcf-border)!important;border-radius:10px;}
.sigcf-table-wrap::-webkit-scrollbar{height:6px;width:6px;}
.sigcf-table-wrap::-webkit-scrollbar-thumb{background:var(--sigcf-green);border-radius:4px;}
.sigcf-table-wrap::-webkit-scrollbar-track{background:var(--sigcf-card);}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
[data-testid="stToolbar"]{visibility:hidden;}
[data-testid="stDecoration"]{display:none;}
.stTabs [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{
 background-color:var(--sigcf-green)!important;background:var(--sigcf-green)!important;}
.stTabs [data-baseweb="tab-list"] [role="tab"][aria-selected="true"]{
 box-shadow:inset 0 -3px 0 0 var(--sigcf-green)!important;}
.ctx-box{background:var(--sigcf-card);border:1px solid var(--sigcf-border);border-radius:12px;padding:14px 16px;margin-bottom:12px;}
"""


def inject_theme(extra_css: str = "") -> None:
    st.markdown(f"<style>{SIGCF_THEME_CSS}{extra_css or ''}</style>", unsafe_allow_html=True)


def render_header(
    logo_html_fn,
    title: str,
    subtitle: str,
    kicker: str = KICKER_DEFAULT,
    logo_width: int = 118,
    extra_html: str = "",
) -> None:
    st.markdown(
        f'<div class="sigcf-header-band">'
        f'<div class="sigcf-header-inner">'
        f"{logo_html_fn(logo_width)}"
        f'<div class="sigcf-header-text">'
        f'<div class="sigcf-kicker">{kicker}</div>'
        f'<h1 class="sigcf-title">{title}</h1>'
        f'<p class="sigcf-sub">{subtitle}</p>'
        f"{extra_html or ''}"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )


def render_footer(text: str) -> None:
    st.markdown(f'<div class="sigcf-footer">{text}</div>', unsafe_allow_html=True)


def dark_table(df, height: int = 320) -> None:
    if df.empty:
        st.info("Nenhum registro.")
        return
    rows = "".join(
        "<tr>"
        + "".join(
            f'<td style="padding:6px 10px;border-bottom:1px solid #2a4030;'
            f'color:#e8edd0;font-size:12px;white-space:nowrap;">{v}</td>'
            for v in row
        )
        + "</tr>"
        for _, row in df.iterrows()
    )
    headers = "".join(
        f'<th style="padding:7px 10px;background:#1a2818;color:#ffd966;font-size:10px;'
        f"font-weight:700;text-transform:uppercase;letter-spacing:1px;"
        f'border-bottom:2px solid #2a4030;white-space:nowrap;">{c}</th>'
        for c in df.columns
    )
    st.markdown(
        f'<div class="sigcf-table-wrap" style="overflow-x:auto;">'
        f'<div style="max-height:{height}px;overflow-y:auto;">'
        f'<table style="width:100%;border-collapse:collapse;background:#0f1f12;'
        f'font-family:Segoe UI,sans-serif;"><thead><tr>{headers}</tr></thead>'
        f"<tbody>{rows}</tbody></table></div></div>",
        unsafe_allow_html=True,
    )
