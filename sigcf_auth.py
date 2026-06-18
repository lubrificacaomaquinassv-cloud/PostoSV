"""PIN opcional SIGCF / SIGRH - logo Santa Virginia premium."""
import base64
from pathlib import Path

LOGO_URL = "https://i.postimg.cc/Y9X7ddnb/LOGO-BP.jpg"
LOGO_FILE = Path(__file__).resolve().parent / "assets" / "logo_santa_verginia.png"
BG_URL = "https://media.bio.site/sites/32a25c2c-d6fa-4dfc-bdc2-27e4d35d7ea2/AhS9mKiQxFRXAyMBdXDzEG.jpg"
INSTAGRAM_URL = "https://www.instagram.com/fazendasantaverginia"
SESSION_KEY = "sigcf_auth"

LOGO_FRAME_CSS = (
    ".logo-frame{background:linear-gradient(145deg,#0a1628,#0d2040);border:2px solid #c9a227;"
    "border-radius:12px;padding:5px;display:inline-block;box-shadow:0 4px 18px rgba(0,0,0,.45);}"
    ".logo-frame img{display:block;border-radius:8px;}"
)

INSTA_ICON = (
    '<img class="insta-ico" src="https://cdn.simpleicons.org/instagram/8ec486" '
    'width="17" height="17" alt="" loading="lazy">'
)


def logo_html(width: int = 118) -> str:
    if LOGO_FILE.is_file():
        b64 = base64.b64encode(LOGO_FILE.read_bytes()).decode()
        src = f"data:image/png;base64,{b64}"
    else:
        src = LOGO_URL
    return f'<div class="logo-frame"><img src="{src}" width="{width}" alt="Santa Virginia"></div>'


def link_instagram(text: str = "@fazendasantaverginia") -> str:
    return (
        f'<a class="insta-link" href="{INSTAGRAM_URL}" target="_blank" rel="noopener">'
        f"{INSTA_ICON}{text}</a>"
    )


def exigir_acesso(titulo: str, subtitulo: str = "Acesso restrito - SIGCF Santa Virginia"):
    import streamlit as st

    pin_cfg = str(st.secrets.get("APP_PIN", "") or "").strip()
    if not pin_cfg:
        return
    if st.session_state.get(SESSION_KEY):
        return

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&display=swap');
        .stApp{
         background:linear-gradient(rgba(10,20,9,0.82),rgba(10,20,9,0.92)),
         url('__BG__') center center/cover no-repeat fixed!important;}
        [data-testid="stAppViewContainer"]{background:transparent!important;}
        h1,h2,p,label{color:#e8edd0;}
        h1{font-family:'Barlow Condensed',sans-serif;}
        __LOGO_CSS__
        .insta-link{display:inline-flex;align-items:center;gap:6px;color:#8ec486!important;
         text-decoration:none;font-weight:600;}
        .insta-ico{width:17px;height:17px;flex-shrink:0;}
        </style>
        """
        .replace("__BG__", BG_URL)
        .replace("__LOGO_CSS__", LOGO_FRAME_CSS),
        unsafe_allow_html=True,
    )
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        st.markdown(logo_html(), unsafe_allow_html=True)
    with col_titulo:
        st.title(titulo)
        st.caption(subtitulo)

    pin = st.text_input("PIN de acesso", type="password", key="sigcf_login_pin")
    if st.button("Entrar", type="primary", key="sigcf_login_btn"):
        if pin == pin_cfg:
            st.session_state[SESSION_KEY] = True
            st.rerun()
        else:
            st.error("PIN incorreto.")
    st.stop()
