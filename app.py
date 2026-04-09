import io
import json
import os
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="DEFERA Stats Live", layout="wide")

# =========================================================
# ESTILO
# =========================================================
DEFERA_RED = "#D40000"
DEFERA_BLACK = "#070707"
DEFERA_DARK = "#111111"
DEFERA_GREY = "#2A2A2A"
DEFERA_PANEL = "#151515"
DEFERA_PANEL_2 = "#1D1D1D"
DEFERA_BORDER = "#303030"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, #050505 0%, #0b0b0b 100%);
            color: white;
        }}

        html, body, [class*="css"] {{
            color: white;
        }}

        .block-container {{
            max-width: 1320px;
            padding-top: 0.55rem;
            padding-bottom: 1rem;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: white !important;
        }}

        h1 {{
            font-size: 2rem !important;
            letter-spacing: 0.3px;
            margin-bottom: 0.1rem !important;
        }}

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea,
        input {{
            background: #101010 !important;
            color: white !important;
            border: 1px solid #404040 !important;
            -webkit-text-fill-color: white !important;
            border-radius: 10px !important;
        }}

        div[data-baseweb="select"] span {{
            color: white !important;
        }}

        div[data-baseweb="tag"] {{
            background-color: {DEFERA_RED} !important;
            color: white !important;
        }}

        div[role="listbox"],
        ul[role="listbox"] {{
            background: #f2f2f2 !important;
        }}

        li[role="option"], li[role="option"] * {{
            color: black !important;
        }}

        .stButton > button {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid {DEFERA_RED};
            background: linear-gradient(180deg, {DEFERA_RED} 0%, #b30000 100%);
            color: white !important;
            font-weight: 700;
            min-height: 2.3rem;
            box-shadow: none !important;
        }}

        .stButton > button:hover {{
            background: linear-gradient(180deg, #b30000 0%, #980000 100%);
            border-color: #b30000;
            color: white !important;
        }}

        .stDownloadButton > button {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid {DEFERA_RED};
            background: linear-gradient(180deg, {DEFERA_RED} 0%, #b30000 100%);
            color: white !important;
            font-weight: 700;
            min-height: 2.3rem;
        }}

        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, {DEFERA_PANEL} 0%, {DEFERA_PANEL_2} 100%);
            border: 1px solid {DEFERA_BORDER};
            border-radius: 16px;
            padding: 10px 12px;
        }}

        .note-box {{
            background: rgba(212,0,0,0.12);
            border-left: 4px solid {DEFERA_RED};
            border-radius: 10px;
            padding: 10px 12px;
            margin: 8px 0 14px 0;
        }}

        .danger-box {{
            background: rgba(255,0,0,0.14);
            border: 1px solid rgba(255,0,0,0.35);
            border-radius: 10px;
            padding: 10px 12px;
            margin: 8px 0 14px 0;
        }}

        .selected-box {{
            background: linear-gradient(180deg, rgba(212,0,0,0.18) 0%, rgba(212,0,0,0.08) 100%);
            border: 1px solid rgba(212,0,0,0.35);
            border-radius: 14px;
            padding: 10px 12px;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .section-card {{
            background: linear-gradient(180deg, {DEFERA_PANEL} 0%, {DEFERA_PANEL_2} 100%);
            border: 1px solid {DEFERA_BORDER};
            border-radius: 16px;
            padding: 10px;
            margin-bottom: 12px;
        }}

        .mini-caption {{
            font-size: 0.74rem;
            opacity: 0.78;
            margin-bottom: 6px;
        }}

        .athlete-grid .stButton > button {{
            min-height: 2.5rem !important;
            padding: 0.20rem !important;
            font-size: 0.95rem !important;
            border-radius: 14px !important;
        }}

        .action-grid .stButton > button {{
            min-height: 2.35rem !important;
            padding: 0.16rem 0.18rem !important;
            font-size: 0.72rem !important;
            border-radius: 12px !important;
            line-height: 1.05 !important;
            white-space: normal !important;
        }}

        .zone-grid .stButton > button {{
            min-height: 4.2rem !important;
            padding: 0.18rem 0.10rem !important;
            font-size: 0.53rem !important;
            border-radius: 12px !important;
            line-height: 1.0 !important;
            white-space: pre-line !important;
        }}

        .source-zone-grid .stButton > button {{
            min-height: 2.5rem !important;
            padding: 0.14rem 0.10rem !important;
            font-size: 0.68rem !important;
            border-radius: 12px !important;
            line-height: 1.0 !important;
            white-space: normal !important;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 0.38rem;
                padding-right: 0.38rem;
            }}

            h1 {{
                font-size: 1.75rem !important;
            }}

            .athlete-grid .stButton > button {{
                min-height: 2.2rem !important;
                font-size: 0.86rem !important;
            }}

            .action-grid .stButton > button {{
                min-height: 2.05rem !important;
                font-size: 0.64rem !important;
                padding: 0.12rem 0.12rem !important;
            }}

            .zone-grid .stButton > button {{
                min-height: 4.05rem !important;
                font-size: 0.47rem !important;
                padding: 0.12rem 0.05rem !important;
            }}

            .source-zone-grid .stButton > button {{
                min-height: 2.3rem !important;
                font-size: 0.62rem !important;
                padding: 0.12rem 0.08rem !important;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# DADOS
# =========================================================
EQUIPAS = {
    "Sénior": [
        {"numero": 15, "nome": "Nuno Pinheiro", "gr": False},
        {"numero": 8, "nome": "Armando Araujo", "gr": False},
        {"numero": 10, "nome": "João Leite", "gr": False},
        {"numero": 7, "nome": "César Gonçalves", "gr": False},
        {"numero": 5, "nome": "Roberto Ferreira", "gr": False},
        {"numero": 28, "nome": "Pedro Freitas", "gr": False},
        {"numero": 77, "nome": "Raphael Cancino", "gr": False},
        {"numero": 3, "nome": "José Magalhães", "gr": False},
        {"numero": 99, "nome": "José Martins", "gr": True},
        {"numero": 9, "nome": "João Martins", "gr": False},
        {"numero": 27, "nome": "André Costa", "gr": False},
        {"numero": 22, "nome": "Leo Quim", "gr": True},
        {"numero": 91, "nome": "Alexandr Tchikoulaev", "gr": False},
        {"numero": 68, "nome": "José Araújo", "gr": False},
        {"numero": 18, "nome": "Diogo M.", "gr": False},
        {"numero": 12, "nome": "Tiago G.", "gr": True},
        {"numero": 67, "nome": "Edgar", "gr": False},
        {"numero": 4, "nome": "João Lourenço", "gr": False},
        {"numero": 20, "nome": "Gui", "gr": False},
        {"numero": 44, "nome": "Pacheco", "gr": False},
    ],
    "Sub-14": [
        {"numero": 1, "nome": "Fernando Abreu", "gr": False},
        {"numero": 2, "nome": "David Ramalho", "gr": False},
        {"numero": 3, "nome": "Duarte Silva", "gr": False},
        {"numero": 4, "nome": "Francisco Fonseca", "gr": False},
        {"numero": 5, "nome": "Fábio Faria", "gr": False},
        {"numero": 6, "nome": "João Edu Oliveira", "gr": False},
        {"numero": 7, "nome": "José Lameiras", "gr": False},
        {"numero": 8, "nome": "Lourenço Pinto", "gr": False},
        {"numero": 9, "nome": "Afonso Eusébio", "gr": False},
        {"numero": 10, "nome": "Afonso Sousa", "gr": False},
        {"numero": 11, "nome": "Alexandre Teixeira", "gr": False},
        {"numero": 12, "nome": "Duarte Oliveira", "gr": False},
        {"numero": 13, "nome": "Gabriel Oliveira", "gr": False},
        {"numero": 14, "nome": "Francisco Pedro", "gr": False},
        {"numero": 15, "nome": "Francisco Soares", "gr": False},
        {"numero": 16, "nome": "Tomás Marinho", "gr": False},
        {"numero": 17, "nome": "Francisco Costa", "gr": False},
        {"numero": 18, "nome": "Pedro Martins", "gr": False},
        {"numero": 19, "nome": "José Fernandes", "gr": True},
        {"numero": 20, "nome": "Diogo Sousa", "gr": True},
        {"numero": 21, "nome": "Gabriel Silva", "gr": False},
        {"numero": 22, "nome": "Rodrigo Castro", "gr": False},
        {"numero": 23, "nome": "Afonso Cunha", "gr": True},
        {"numero": 24, "nome": "Salvador Correia", "gr": False},
        {"numero": 25, "nome": "Rodrigo Sanchez", "gr": False},
    ],
}

ACOES_RAPIDAS = [
    "Assistência ao Ponta",
    "Defesa do Guarda redes",
    "Golo Marcado",
    "Assistência para golo",
    "Assistência ao Pivô",
    "Cartão Amarelo",
    "Cartão Vermelho",
    "Suspensão dois minutos",
    "Bola/remate Bloqueado",
    "Desarme",
    "Remate interceptado",
    "Remate",
    "Perda de bola",
    "7 metros ganho",
    "Falta técnica",
    "Golo sofrido",
]

TIPOS_REMATE = [
    "6 metros",
    "9 metros",
    "7 metros",
    "Ponta",
    "Pivô",
    "Contra-ataque",
]

RESULTADOS_REMATE = [
    "Golo",
    "Falhado",
    "Defesa GR",
    "Poste",
]

ZONAS_ORIGEM_REMATE = [
    "6 metros",
    "9 metros",
    "7 metros",
    "Ponta",
    "Pivô",
    "Contra-ataque",
]

ZONAS_BALIZA = {
    1: "Canto Superior Esquerdo",
    2: "Centro Superior",
    3: "Canto Superior Direito",
    4: "Meio Esquerda",
    5: "Meio Centro",
    6: "Meio Direita",
    7: "Canto Inferior Esquerdo",
    8: "Centro Inferior",
    9: "Canto Inferior Direito",
}

MAX_CONVOCADOS = 16
BACKUP_FILE = "/tmp/defera_stats_live_backup.json"

# =========================================================
# ESTADO
# =========================================================
def init_state():
    defaults = {
        "jogo_iniciado": False,
        "parte": "1.ª Parte",
        "equipa": None,
        "adversario": "",
        "competicao": "",
        "local_jogo": "",
        "data_jogo": date.today().strftime("%d/%m/%Y"),
        "convocados_ids": [],
        "selecionado_id": None,
        "eventos_log": [],
        "stats": {},
        "resultado_cd_xico": 0,
        "resultado_adversario": 0,
        "resultado_intervalo_cd_xico": 0,
        "resultado_intervalo_adversario": 0,
        "observacoes": "",
        "ultima_acao_anulada": "",
        "ultima_acao_registada": "",
        "acao_atual": None,
        "resultado_defesa_gr_atual": None,
        "tipo_remate_atual": None,
        "resultado_remate_atual": None,
        "zona_origem_gr_atual": None,
        "zona_baliza_atual": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def snapshot_state():
    keys = [
        "jogo_iniciado",
        "parte",
        "equipa",
        "adversario",
        "competicao",
        "local_jogo",
        "data_jogo",
        "convocados_ids",
        "selecionado_id",
        "eventos_log",
        "stats",
        "resultado_cd_xico",
        "resultado_adversario",
        "resultado_intervalo_cd_xico",
        "resultado_intervalo_adversario",
        "observacoes",
        "ultima_acao_anulada",
        "ultima_acao_registada",
        "acao_atual",
        "resultado_defesa_gr_atual",
        "tipo_remate_atual",
        "resultado_remate_atual",
        "zona_origem_gr_atual",
        "zona_baliza_atual",
    ]
    return {k: st.session_state.get(k) for k in keys}


def save_backup():
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(snapshot_state(), f, ensure_ascii=False)
    except Exception:
        pass


def load_backup():
    try:
        if os.path.exists(BACKUP_FILE):
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def restore_backup(data):
    if not data:
        return
    for k, v in data.items():
        st.session_state[k] = v


def clear_backup():
    try:
        if os.path.exists(BACKUP_FILE):
            os.remove(BACKUP_FILE)
    except Exception:
        pass


def reset_jogo():
    clear_backup()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def limpar_fluxo_acao():
    st.session_state.acao_atual = None
    st.session_state.resultado_defesa_gr_atual = None
    st.session_state.tipo_remate_atual = None
    st.session_state.resultado_remate_atual = None
    st.session_state.zona_origem_gr_atual = None
    st.session_state.zona_baliza_atual = None
    save_backup()


def get_plantel(equipa_nome):
    return EQUIPAS.get(equipa_nome, [])


def get_convocados():
    return sorted(
        [j for j in get_plantel(st.session_state.equipa) if j["numero"] in st.session_state.convocados_ids],
        key=lambda x: x["numero"],
    )


def get_player_by_num(numero):
    for jogador in get_convocados():
        if jogador["numero"] == numero:
            return jogador
    return None


def atleta_selecionado_e_gr():
    jogador = get_player_by_num(st.session_state.selecionado_id)
    return jogador["gr"] if jogador else False


def ensure_player_stats(jogador):
    pid = jogador["numero"]
    if pid not in st.session_state.stats:
        st.session_state.stats[pid] = {
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "gr": jogador["gr"],
            "assist_ponta": 0,
            "defesas_gr": 0,
            "golos_marcados": 0,
            "assist_golo": 0,
            "assist_pivo": 0,
            "cartoes_amarelos": 0,
            "cartoes_vermelhos": 0,
            "suspensoes_2min": 0,
            "bolas_bloqueadas": 0,
            "desarmes": 0,
            "remates_interceptados": 0,
            "perdas_bola": 0,
            "ganhou_7m": 0,
            "faltas_tecnicas": 0,
            "golos_sofridos": 0,
            "remates_total": 0,
            "remates_6m": 0,
            "remates_9m": 0,
            "remates_7m": 0,
            "remates_ponta": 0,
            "remates_pivo": 0,
            "remates_contra_ataque": 0,
            "remates_golo": 0,
            "remates_falhados": 0,
            "remates_defesa_gr": 0,
            "remates_poste": 0,
        }


def registar_acao_simples(acao):
    numero = st.session_state.selecionado_id
    jogador = get_player_by_num(numero)
    if not jogador:
        return

    ensure_player_stats(jogador)
    s = st.session_state.stats[numero]

    mapa = {
        "Assistência ao Ponta": "assist_ponta",
        "Golo Marcado": "golos_marcados",
        "Assistência para golo": "assist_golo",
        "Assistência ao Pivô": "assist_pivo",
        "Cartão Amarelo": "cartoes_amarelos",
        "Cartão Vermelho": "cartoes_vermelhos",
        "Suspensão dois minutos": "suspensoes_2min",
        "Bola/remate Bloqueado": "bolas_bloqueadas",
        "Desarme": "desarmes",
        "Remate interceptado": "remates_interceptados",
        "Perda de bola": "perdas_bola",
        "7 metros ganho": "ganhou_7m",
        "Falta técnica": "faltas_tecnicas",
        "Golo sofrido": "golos_sofridos",
    }

    campo = mapa.get(acao)
    if campo:
        s[campo] += 1

    st.session_state.eventos_log.append(
        {
            "parte": st.session_state.parte,
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "acao_principal": acao,
            "resultado_defesa_gr": "",
            "tipo_remate": "",
            "resultado_remate": "",
            "zona_origem_gr": "",
            "zona_baliza": "",
            "zona_baliza_label": "",
        }
    )

    st.session_state.ultima_acao_registada = f"{jogador['numero']} · {jogador['nome']} → {acao}"
    st.session_state.ultima_acao_anulada = ""
    save_backup()
    limpar_fluxo_acao()


def confirmar_defesa_gr():
    numero = st.session_state.selecionado_id
    jogador = get_player_by_num(numero)
    if not jogador:
        return

    resultado = st.session_state.resultado_defesa_gr_atual
    origem = st.session_state.zona_origem_gr_atual
    zona = st.session_state.zona_baliza_atual

    if resultado is None or origem is None or zona is None:
        return

    ensure_player_stats(jogador)
    s = st.session_state.stats[numero]

    if resultado == "Defendeu":
        s["defesas_gr"] += 1
    else:
        s["golos_sofridos"] += 1

    st.session_state.eventos_log.append(
        {
            "parte": st.session_state.parte,
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "acao_principal": "Defesa do Guarda redes",
            "resultado_defesa_gr": resultado,
            "tipo_remate": "",
            "resultado_remate": "",
            "zona_origem_gr": origem,
            "zona_baliza": zona,
            "zona_baliza_label": ZONAS_BALIZA.get(zona, ""),
        }
    )

    extra = f" / Origem {origem} / Zona {zona} - {ZONAS_BALIZA.get(zona, '')}"
    st.session_state.ultima_acao_registada = (
        f"{jogador['numero']} · {jogador['nome']} → Defesa do Guarda redes / {resultado}{extra}"
    )
    st.session_state.ultima_acao_anulada = ""
    save_backup()
    limpar_fluxo_acao()


def mapear_tipo_remate(tipo):
    mapa = {
        "6 metros": "remates_6m",
        "9 metros": "remates_9m",
        "7 metros": "remates_7m",
        "Ponta": "remates_ponta",
        "Pivô": "remates_pivo",
        "Contra-ataque": "remates_contra_ataque",
    }
    return mapa.get(tipo)


def confirmar_remate():
    numero = st.session_state.selecionado_id
    jogador = get_player_by_num(numero)
    if not jogador:
        return

    tipo = st.session_state.tipo_remate_atual
    resultado = st.session_state.resultado_remate_atual
    zona = st.session_state.zona_baliza_atual

    if not tipo or not resultado:
        return

    if resultado == "Defesa GR" and zona is None:
        return

    if resultado != "Defesa GR":
        zona = None

    ensure_player_stats(jogador)
    s = st.session_state.stats[numero]

    s["remates_total"] += 1

    campo_tipo = mapear_tipo_remate(tipo)
    if campo_tipo:
        s[campo_tipo] += 1

    if resultado == "Golo":
        s["remates_golo"] += 1
    elif resultado == "Falhado":
        s["remates_falhados"] += 1
    elif resultado == "Defesa GR":
        s["remates_defesa_gr"] += 1
    elif resultado == "Poste":
        s["remates_poste"] += 1

    st.session_state.eventos_log.append(
        {
            "parte": st.session_state.parte,
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "acao_principal": "Remate",
            "resultado_defesa_gr": "",
            "tipo_remate": tipo,
            "resultado_remate": resultado,
            "zona_origem_gr": "",
            "zona_baliza": zona if zona is not None else "",
            "zona_baliza_label": ZONAS_BALIZA.get(zona, "") if zona is not None else "",
        }
    )

    extra = f" / Zona {zona} - {ZONAS_BALIZA.get(zona, '')}" if zona is not None else ""
    st.session_state.ultima_acao_registada = (
        f"{jogador['numero']} · {jogador['nome']} → Remate / {tipo} / {resultado}{extra}"
    )
    st.session_state.ultima_acao_anulada = ""
    save_backup()
    limpar_fluxo_acao()


def anular_ultima_acao():
    if not st.session_state.eventos_log:
        st.session_state.ultima_acao_anulada = "Não existiam ações para anular."
        return

    ultimo = st.session_state.eventos_log.pop()
    numero = ultimo["numero_camisola"]
    jogador = get_player_by_num(numero)
    if not jogador:
        st.session_state.ultima_acao_anulada = "Última ação anulada."
        return

    ensure_player_stats(jogador)
    s = st.session_state.stats[numero]

    acao = ultimo["acao_principal"]

    mapa = {
        "Assistência ao Ponta": "assist_ponta",
        "Golo Marcado": "golos_marcados",
        "Assistência para golo": "assist_golo",
        "Assistência ao Pivô": "assist_pivo",
        "Cartão Amarelo": "cartoes_amarelos",
        "Cartão Vermelho": "cartoes_vermelhos",
        "Suspensão dois minutos": "suspensoes_2min",
        "Bola/remate Bloqueado": "bolas_bloqueadas",
        "Desarme": "desarmes",
        "Remate interceptado": "remates_interceptados",
        "Perda de bola": "perdas_bola",
        "7 metros ganho": "ganhou_7m",
        "Falta técnica": "faltas_tecnicas",
        "Golo sofrido": "golos_sofridos",
    }

    if acao == "Defesa do Guarda redes":
        if ultimo["resultado_defesa_gr"] == "Defendeu":
            if s["defesas_gr"] > 0:
                s["defesas_gr"] -= 1
        else:
            if s["golos_sofridos"] > 0:
                s["golos_sofridos"] -= 1

        extra = f" / Origem {ultimo['zona_origem_gr']} / Zona {ultimo['zona_baliza']} - {ultimo['zona_baliza_label']}"
        st.session_state.ultima_acao_anulada = (
            f"Ação anulada: {numero} · {ultimo['atleta']} → Defesa do Guarda redes / "
            f"{ultimo['resultado_defesa_gr']}{extra}"
        )
        st.session_state.ultima_acao_registada = ""
        save_backup()
        limpar_fluxo_acao()
        return

    if acao == "Remate":
        tipo = ultimo["tipo_remate"]
        resultado = ultimo["resultado_remate"]

        if s["remates_total"] > 0:
            s["remates_total"] -= 1

        campo_tipo = mapear_tipo_remate(tipo)
        if campo_tipo and s[campo_tipo] > 0:
            s[campo_tipo] -= 1

        if resultado == "Golo" and s["remates_golo"] > 0:
            s["remates_golo"] -= 1
        elif resultado == "Falhado" and s["remates_falhados"] > 0:
            s["remates_falhados"] -= 1
        elif resultado == "Defesa GR" and s["remates_defesa_gr"] > 0:
            s["remates_defesa_gr"] -= 1
        elif resultado == "Poste" and s["remates_poste"] > 0:
            s["remates_poste"] -= 1

        extra = (
            f" / Zona {ultimo['zona_baliza']} - {ultimo['zona_baliza_label']}"
            if ultimo["zona_baliza"] != ""
            else ""
        )
        st.session_state.ultima_acao_anulada = (
            f"Ação anulada: {numero} · {ultimo['atleta']} → Remate / "
            f"{ultimo['tipo_remate']} / {ultimo['resultado_remate']}{extra}"
        )
        st.session_state.ultima_acao_registada = ""
        save_backup()
        limpar_fluxo_acao()
        return

    campo = mapa.get(acao)
    if campo and s[campo] > 0:
        s[campo] -= 1

    st.session_state.ultima_acao_anulada = f"Ação anulada: {numero} · {ultimo['atleta']} → {acao}"
    st.session_state.ultima_acao_registada = ""
    save_backup()
    limpar_fluxo_acao()


# =========================================================
# RENDER GRELHAS
# =========================================================
def render_grelha_atletas_numeros(jogadores, n_cols=4):
    for i in range(0, len(jogadores), n_cols):
        cols = st.columns(n_cols)
        bloco = jogadores[i:i + n_cols]
        for idx, j in enumerate(bloco):
            selecionado = st.session_state.selecionado_id == j["numero"]
            label = f"✅ {j['numero']}" if selecionado else str(j["numero"])
            with cols[idx]:
                if st.button(label, key=f"atleta_{j['numero']}", use_container_width=True):
                    st.session_state.selecionado_id = j["numero"]
                    save_backup()
                    limpar_fluxo_acao()
                    st.rerun()


def render_grelha_acoes_rapidas(itens, n_cols=2):
    for i in range(0, len(itens), n_cols):
        cols = st.columns(n_cols)
        bloco = itens[i:i + n_cols]
        for idx, item in enumerate(bloco):
            selecionado = st.session_state.acao_atual == item
            label = f"✅ {item}" if selecionado else item
            with cols[idx]:
                if st.button(label, key=f"acao_{item}", use_container_width=True):
                    st.session_state.acao_atual = item
                    st.session_state.resultado_defesa_gr_atual = None
                    st.session_state.tipo_remate_atual = None
                    st.session_state.resultado_remate_atual = None
                    st.session_state.zona_origem_gr_atual = None
                    st.session_state.zona_baliza_atual = None
                    save_backup()

                    if item in ["Defesa do Guarda redes", "Remate"]:
                        st.rerun()
                    else:
                        registar_acao_simples(item)
                        st.rerun()


def render_grelha_lista_botoes(itens, chave_estado, prefixo, n_cols=2):
    for i in range(0, len(itens), n_cols):
        cols = st.columns(n_cols)
        bloco = itens[i:i + n_cols]
        for idx, item in enumerate(bloco):
            selecionado = st.session_state[chave_estado] == item
            label = f"✅ {item}" if selecionado else item
            with cols[idx]:
                if st.button(label, key=f"{prefixo}_{item}", use_container_width=True):
                    st.session_state[chave_estado] = item
                    save_backup()
                    st.rerun()


def render_grelha_zonas():
    zonas = list(ZONAS_BALIZA.keys())
    idx = 0
    for _ in range(3):
        cols = st.columns(3)
        for c in cols:
            zona = zonas[idx]
            selecionado = st.session_state.zona_baliza_atual == zona
            label = f"✅ {zona}\n{ZONAS_BALIZA[zona]}" if selecionado else f"{zona}\n{ZONAS_BALIZA[zona]}"
            with c:
                if st.button(label, key=f"zona_{zona}", use_container_width=True):
                    st.session_state.zona_baliza_atual = zona
                    save_backup()
                    st.rerun()
            idx += 1


# =========================================================
# DATAFRAMES
# =========================================================
def dataframe_resumo():
    rows = []
    for jogador in get_convocados():
        ensure_player_stats(jogador)
        rows.append(st.session_state.stats[jogador["numero"]])

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)[[
        "numero_camisola",
        "atleta",
        "assist_ponta",
        "defesas_gr",
        "golos_marcados",
        "assist_golo",
        "assist_pivo",
        "cartoes_amarelos",
        "cartoes_vermelhos",
        "suspensoes_2min",
        "bolas_bloqueadas",
        "desarmes",
        "remates_interceptados",
        "perdas_bola",
        "ganhou_7m",
        "faltas_tecnicas",
        "golos_sofridos",
        "remates_total",
        "remates_6m",
        "remates_9m",
        "remates_7m",
        "remates_ponta",
        "remates_pivo",
        "remates_contra_ataque",
        "remates_golo",
        "remates_falhados",
        "remates_defesa_gr",
        "remates_poste",
    ]].sort_values(["numero_camisola", "atleta"])


def dataframe_eventos():
    if not st.session_state.eventos_log:
        return pd.DataFrame(
            columns=[
                "parte",
                "numero_camisola",
                "atleta",
                "acao_principal",
                "resultado_defesa_gr",
                "tipo_remate",
                "resultado_remate",
                "zona_origem_gr",
                "zona_baliza",
                "zona_baliza_label",
            ]
        )
    return pd.DataFrame(st.session_state.eventos_log)


def ficha_jogo_df(momento_exportacao="Final"):
    return pd.DataFrame([{
        "momento_exportacao": momento_exportacao,
        "parte_atual": st.session_state.parte,
        "equipa": st.session_state.equipa,
        "adversario": st.session_state.adversario,
        "competicao": st.session_state.competicao,
        "local_jogo": st.session_state.local_jogo,
        "data_jogo": st.session_state.data_jogo,
        "resultado_cd_xico": st.session_state.resultado_cd_xico,
        "resultado_adversario": st.session_state.resultado_adversario,
        "resultado_intervalo_cd_xico": st.session_state.resultado_intervalo_cd_xico,
        "resultado_intervalo_adversario": st.session_state.resultado_intervalo_adversario,
        "observacoes": st.session_state.observacoes,
    }])


def exportar_excel_bytes(momento_exportacao="Final"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        ficha_jogo_df(momento_exportacao=momento_exportacao).to_excel(writer, sheet_name="Ficha do Jogo", index=False)
        dataframe_resumo().to_excel(writer, sheet_name="Resumo por Atleta", index=False)
        dataframe_eventos().to_excel(writer, sheet_name="Log de Ações", index=False)
    output.seek(0)
    return output.getvalue()

# =========================================================
# RENDER PRINCIPAL
# =========================================================
init_state()

if not st.session_state.jogo_iniciado:
    backup = load_backup()
    if backup and backup.get("jogo_iniciado"):
        st.warning("Foi encontrado um jogo em curso guardado automaticamente.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Recuperar último jogo", use_container_width=True):
                restore_backup(backup)
                st.rerun()
        with c2:
            if st.button("Ignorar recuperação", use_container_width=True):
                clear_backup()
                st.rerun()

st.title("DEFERA Stats Live")
st.caption("Modo operacional — números à esquerda e ações à direita.")

if not st.session_state.jogo_iniciado:
    st.subheader("Configuração do jogo")

    equipa = st.selectbox("Equipa", list(EQUIPAS.keys()))
    adversario = st.text_input("Adversário")
    competicao = st.text_input("Competição")
    local_jogo = st.text_input("Local")
    data_jogo = st.text_input("Data do jogo", value=st.session_state.data_jogo)

    plantel = get_plantel(equipa)
    opcoes = {f"{j['numero']} · {j['nome']}{' 🧤' if j['gr'] else ''}": j["numero"] for j in plantel}

    st.markdown(f"#### Convocados (máximo {MAX_CONVOCADOS})")
    labels = st.multiselect("Selecionar atletas", list(opcoes.keys()))
    convocados_ids = [opcoes[label] for label in labels]
    st.caption(f"Selecionados: {len(convocados_ids)}/{MAX_CONVOCADOS}")

    if st.button("Iniciar jogo", use_container_width=True):
        if not adversario.strip():
            st.warning("Preenche o adversário.")
        elif not convocados_ids:
            st.warning("Seleciona os convocados.")
        elif len(convocados_ids) > MAX_CONVOCADOS:
            st.warning(f"No andebol, a convocatória está limitada a {MAX_CONVOCADOS} atletas.")
        else:
            st.session_state.jogo_iniciado = True
            st.session_state.equipa = equipa
            st.session_state.adversario = adversario.strip()
            st.session_state.competicao = competicao.strip()
            st.session_state.local_jogo = local_jogo.strip()
            st.session_state.data_jogo = data_jogo.strip()
            st.session_state.convocados_ids = convocados_ids
            st.session_state.selecionado_id = sorted(convocados_ids)[0]
            save_backup()
            limpar_fluxo_acao()
            st.rerun()
    st.stop()

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Parte", st.session_state.parte)
with m2:
    st.metric("CD Xico", st.session_state.resultado_cd_xico)
with m3:
    st.metric("Adversário", st.session_state.resultado_adversario)
with m4:
    st.metric("Convocados", len(st.session_state.convocados_ids))

if st.session_state.ultima_acao_anulada:
    st.markdown(f"<div class='danger-box'><strong>{st.session_state.ultima_acao_anulada}</strong></div>", unsafe_allow_html=True)
elif st.session_state.ultima_acao_registada:
    st.markdown(f"<div class='note-box'><strong>Última ação registada:</strong> {st.session_state.ultima_acao_registada}</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([1, 1.2, 1.25, 1])
with c1:
    if st.button("Passar para 2.ª Parte", use_container_width=True, disabled=st.session_state.parte == "2.ª Parte"):
        st.session_state.parte = "2.ª Parte"
        save_backup()
        st.rerun()
with c2:
    if st.button("ANULAR ÚLTIMA AÇÃO", use_container_width=True):
        anular_ultima_acao()
        st.rerun()
with c3:
    st.download_button(
        "Exportar Excel ao intervalo",
        data=exportar_excel_bytes("Intervalo"),
        file_name=f"defera_stats_intervalo_{st.session_state.equipa}_{st.session_state.adversario}.xlsx".replace(" ", "_"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with c4:
    if st.button("Novo jogo", use_container_width=True):
        reset_jogo()
        st.rerun()

convocados = get_convocados()
selecionado = get_player_by_num(st.session_state.selecionado_id)

left, right = st.columns([0.82, 1.38], gap="medium")

with left:
    st.markdown("### Atletas")
    st.markdown("<div class='mini-caption'>Seleciona apenas o número do atleta</div>", unsafe_allow_html=True)
    st.markdown("<div class='athlete-grid'>", unsafe_allow_html=True)
    render_grelha_atletas_numeros(convocados, n_cols=4)
    st.markdown("</div>", unsafe_allow_html=True)

    if selecionado:
        gr_txt = " · GR" if selecionado["gr"] else ""
        st.markdown(
            f"<div class='selected-box'>Selecionado — {selecionado['numero']} · {selecionado['nome']}{gr_txt}</div>",
            unsafe_allow_html=True,
        )

with right:
    st.markdown("### Registo")

    if selecionado:
        defesa_txt = st.session_state.resultado_defesa_gr_atual or "—"
        tipo_txt = st.session_state.tipo_remate_atual or "—"
        resultado_txt = st.session_state.resultado_remate_atual or "—"
        origem_gr_txt = st.session_state.zona_origem_gr_atual or "—"
        zona_txt = (
            f"{st.session_state.zona_baliza_atual} - {ZONAS_BALIZA[st.session_state.zona_baliza_atual]}"
            if st.session_state.zona_baliza_atual is not None else "—"
        )

        st.markdown(
            f"""
            <div class='selected-box'>
                Atleta — {selecionado['numero']} · {selecionado['nome']}{' · GR' if selecionado['gr'] else ''}<br>
                Ação — {st.session_state.acao_atual or '—'} &nbsp;&nbsp;|&nbsp;&nbsp;
                Defesa — {defesa_txt} &nbsp;&nbsp;|&nbsp;&nbsp;
                Tipo — {tipo_txt} &nbsp;&nbsp;|&nbsp;&nbsp;
                Resultado — {resultado_txt} &nbsp;&nbsp;|&nbsp;&nbsp;
                Origem — {origem_gr_txt} &nbsp;&nbsp;|&nbsp;&nbsp;
                Baliza — {zona_txt}
            </div>
            """,
            unsafe_allow_html=True,
        )

        acoes_visiveis = ACOES_RAPIDAS if selecionado["gr"] else [a for a in ACOES_RAPIDAS if a != "Defesa do Guarda redes"]

        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("**Ações rápidas**")
        st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
        render_grelha_acoes_rapidas(acoes_visiveis, n_cols=2)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.acao_atual == "Defesa do Guarda redes" and selecionado["gr"]:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("**Defesa do GR**")
            st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
            render_grelha_lista_botoes(["Defendeu", "Não defendeu"], "resultado_defesa_gr_atual", "resultado_defesa", n_cols=2)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.resultado_defesa_gr_atual is not None:
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                st.markdown("**Origem do remate**")
                st.markdown("<div class='source-zone-grid'>", unsafe_allow_html=True)
                render_grelha_lista_botoes(ZONAS_ORIGEM_REMATE, "zona_origem_gr_atual", "origem_gr", n_cols=2)
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                st.markdown("**Posição na baliza**")
                st.markdown("<div class='zone-grid'>", unsafe_allow_html=True)
                render_grelha_zonas()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            pode_confirmar_defesa = all([
                st.session_state.selecionado_id is not None,
                st.session_state.resultado_defesa_gr_atual is not None,
                st.session_state.zona_origem_gr_atual is not None,
                st.session_state.zona_baliza_atual is not None,
            ])

            b1, b2 = st.columns(2)
            with b1:
                if st.button("CONFIRMAR DEFESA", use_container_width=True, disabled=not pode_confirmar_defesa):
                    confirmar_defesa_gr()
                    st.rerun()
            with b2:
                if st.button("LIMPAR SELEÇÃO", use_container_width=True):
                    limpar_fluxo_acao()
                    st.rerun()

        if st.session_state.acao_atual == "Remate":
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("**Tipo de remate**")
            st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
            render_grelha_lista_botoes(TIPOS_REMATE, "tipo_remate_atual", "tipo_remate", n_cols=2)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("**Resultado do remate**")
            st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
            render_grelha_lista_botoes(RESULTADOS_REMATE, "resultado_remate_atual", "resultado_remate", n_cols=2)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.resultado_remate_atual == "Defesa GR":
                st.markdown("<div class='section-card'>", unsafe_allow_html=True)
                st.markdown("**Posição na baliza**")
                st.markdown("<div class='zone-grid'>", unsafe_allow_html=True)
                render_grelha_zonas()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            pode_confirmar_remate = all([
                st.session_state.selecionado_id is not None,
                st.session_state.tipo_remate_atual is not None,
                st.session_state.resultado_remate_atual is not None,
                (st.session_state.zona_baliza_atual is not None if st.session_state.resultado_remate_atual == "Defesa GR" else True),
            ])

            b1, b2 = st.columns(2)
            with b1:
                if st.button("CONFIRMAR REMATE", use_container_width=True, disabled=not pode_confirmar_remate):
                    confirmar_remate()
                    st.rerun()
            with b2:
                if st.button("LIMPAR SELEÇÃO ", use_container_width=True):
                    limpar_fluxo_acao()
                    st.rerun()

with st.expander("Fecho do jogo"):
    r1, r2 = st.columns(2)
    with r1:
        st.session_state.resultado_cd_xico = st.number_input(
            "Resultado final CD Xico",
            min_value=0,
            step=1,
            value=int(st.session_state.resultado_cd_xico),
        )
    with r2:
        st.session_state.resultado_adversario = st.number_input(
            "Resultado final adversário",
            min_value=0,
            step=1,
            value=int(st.session_state.resultado_adversario),
        )

    r3, r4 = st.columns(2)
    with r3:
        st.session_state.resultado_intervalo_cd_xico = st.number_input(
            "Resultado ao intervalo CD Xico",
            min_value=0,
            step=1,
            value=int(st.session_state.resultado_intervalo_cd_xico),
        )
    with r4:
        st.session_state.resultado_intervalo_adversario = st.number_input(
            "Resultado ao intervalo adversário",
            min_value=0,
            step=1,
            value=int(st.session_state.resultado_intervalo_adversario),
        )

    st.session_state.observacoes = st.text_area("Observações finais", value=st.session_state.observacoes)
    save_backup()

    st.download_button(
        "Exportar Excel do jogo",
        data=exportar_excel_bytes("Final"),
        file_name=f"defera_stats_{st.session_state.equipa}_{st.session_state.adversario}.xlsx".replace(" ", "_"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with st.expander("Resumo estatístico"):
    st.dataframe(dataframe_resumo(), use_container_width=True, hide_index=True)

    if not dataframe_eventos().empty:
        with st.expander("Ver últimos registos"):
            st.dataframe(
                dataframe_eventos().tail(30).iloc[::-1],
                use_container_width=True,
                hide_index=True,
            )
