import io
import json
import os
from datetime import date, datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="DEFERA Stats Live", layout="wide")

# =========================================================
# ESTILO
# =========================================================
DEFERA_RED = "#D40000"
DEFERA_BLACK = "#070707"
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

        /* Campos de texto e selects */
        div[data-baseweb="input"] input,
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] span,
        textarea,
        input {{
            background-color: #111111 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            border: 1px solid #404040 !important;
            border-radius: 10px !important;
        }}

        /* Dropdown aberto */
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        ul[role="listbox"],
        li[role="option"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
        }}

        li[role="option"] div,
        li[role="option"] span {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}

        div[data-baseweb="tag"] {{
            background-color: {DEFERA_RED} !important;
            color: white !important;
        }}

        .stButton > button {{
            width: 100%;
            border-radius: 13px;
            border: 1px solid {DEFERA_RED};
            background: linear-gradient(180deg, {DEFERA_RED} 0%, #b30000 100%);
            color: white !important;
            font-weight: 800;
            min-height: 2.6rem;
            box-shadow: none !important;
        }}

        .stButton > button:hover {{
            background: linear-gradient(180deg, #b30000 0%, #980000 100%);
            border-color: #b30000;
        }}

        .stDownloadButton > button {{
            width: 100%;
            border-radius: 13px;
            border: 1px solid {DEFERA_RED};
            background: linear-gradient(180deg, {DEFERA_RED} 0%, #b30000 100%);
            color: white !important;
            font-weight: 800;
            min-height: 2.6rem;
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
            font-weight: 800;
        }}

        .section-card {{
            background: linear-gradient(180deg, {DEFERA_PANEL} 0%, {DEFERA_PANEL_2} 100%);
            border: 1px solid {DEFERA_BORDER};
            border-radius: 16px;
            padding: 10px;
            margin-bottom: 12px;
        }}

        .athlete-grid .stButton > button {{
            min-height: 2.15rem !important;
            padding: 0.10rem 0.12rem !important;
            font-size: 0.78rem !important;
            border-radius: 11px !important;
            line-height: 1.05 !important;
            white-space: normal !important;
        }}

        .action-grid .stButton > button {{
            min-height: 2.65rem !important;
            padding: 0.16rem 0.18rem !important;
            font-size: 0.82rem !important;
            border-radius: 12px !important;
            line-height: 1.05 !important;
            white-space: normal !important;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 0.38rem;
                padding-right: 0.38rem;
            }}

            .athlete-grid .stButton > button {{
                min-height: 2.05rem !important;
                font-size: 0.70rem !important;
                padding: 0.08rem !important;
            }}

            .action-grid .stButton > button {{
                min-height: 2.25rem !important;
                font-size: 0.70rem !important;
                padding: 0.12rem 0.10rem !important;
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

MAX_CONVOCADOS = 16
BACKUP_FILE = "/tmp/defera_stats_live_backup.json"

CAMPO_ACOES = {
    "Assistência": ["Ponta", "Pivot"],
    "Disciplina": ["Amarelo", "Vermelho", "2 min", "Azul"],
    "Defesa": ["Interceção", "Bloco", "Desarme"],
    "Falta Técnica": ["Passos", "Dribles", "Receção", "Passe", "Atacante"],
    "7 Metros Ganho": ["Registar"],
    "Remate": ["6m", "9m", "7m", "Ponta", "Contra-ataque", "Transição", "Sem GR"],
}

RESULTADOS_REMATE_CAMPO = ["Golo", "Fora", "Defesa GR", "Poste", "Bloco"]

GR_ACOES = {
    "Defesa": ["6m", "9m", "7m", "Ponta", "Pivô", "Contra-ataque", "Transição"],
    "Golo Sofrido": ["6m", "9m", "7m", "Ponta", "Pivô", "Contra-ataque", "Transição"],
    "Remate": ["Golo", "Poste", "Falhado", "Defesa GR"],
    "Assistência": ["Contra-ataque"],
    "Falta Técnica": ["Passe"],
    "Disciplina": ["Amarelo", "Vermelho", "2 min", "Azul"],
}

ZONAS_BALIZA = {
    1: "Superior Esquerdo",
    2: "Superior Centro",
    3: "Superior Direito",
    4: "Médio Esquerdo",
    5: "Médio Centro",
    6: "Médio Direito",
    7: "Inferior Esquerdo",
    8: "Inferior Centro",
    9: "Inferior Direito",
}

STAT_KEYS = [
    "assist_ponta", "assist_pivot", "assist_golo", "assist_contra_ataque",
    "cartoes_amarelos", "cartoes_vermelhos", "suspensoes_2min", "cartoes_azuis",
    "defesas_intercecao", "defesas_bloco", "defesas_desarme", "defesas_gr",
    "faltas_passos", "faltas_dribles", "faltas_rececao", "faltas_passe", "faltas_atacante", "faltas_tecnicas",
    "ganhou_7m",
    "remates_total", "remates_6m", "remates_9m", "remates_7m", "remates_ponta",
    "remates_pivot", "remates_contra_ataque", "remates_transicao", "remates_sem_gr",
    "remates_golo", "remates_fora", "remates_defesa_gr", "remates_poste", "remates_bloco",
    "golos_marcados", "golos_sofridos", "golos_sofridos_baliza_aberta",
]

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
        "eventos_log": [],
        "stats": {},
        "resultado_cd_xico": 0,
        "resultado_adversario": 0,
        "resultado_intervalo_cd_xico": 0,
        "resultado_intervalo_adversario": 0,
        "observacoes": "",
        "ultima_acao_anulada": "",
        "ultima_acao_registada": "",
        "modal_jogador_num": None,
        "modal_acao": None,
        "modal_detalhe": None,
        "modal_zona": None,
        "modal_resultado": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def snapshot_state():
    keys = [
        "jogo_iniciado", "parte", "equipa", "adversario", "competicao", "local_jogo",
        "data_jogo", "convocados_ids", "eventos_log", "stats",
        "resultado_cd_xico", "resultado_adversario",
        "resultado_intervalo_cd_xico", "resultado_intervalo_adversario",
        "observacoes", "ultima_acao_anulada", "ultima_acao_registada",
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


def reset_modal():
    st.session_state.modal_jogador_num = None
    st.session_state.modal_acao = None
    st.session_state.modal_detalhe = None
    st.session_state.modal_zona = None
    st.session_state.modal_resultado = None


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


def ensure_player_stats(jogador):
    pid = jogador["numero"]
    if pid not in st.session_state.stats:
        st.session_state.stats[pid] = {
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "gr": jogador["gr"],
        }
        for key in STAT_KEYS:
            st.session_state.stats[pid][key] = 0


def apply_stats_delta(jogador, delta):
    if not jogador or not delta:
        return
    ensure_player_stats(jogador)
    for key, value in delta.items():
        st.session_state.stats[jogador["numero"]][key] += value
        if st.session_state.stats[jogador["numero"]][key] < 0:
            st.session_state.stats[jogador["numero"]][key] = 0


def criar_delta(categoria, detalhe="", zona="", resultado=""):
    delta = {}

    def inc(key):
        delta[key] = delta.get(key, 0) + 1

    if categoria == "Assistência":
        if detalhe == "Ponta":
            inc("assist_ponta")
        elif detalhe == "Pivot":
            inc("assist_pivot")
        elif detalhe == "Contra-ataque":
            inc("assist_contra_ataque")
        inc("assist_golo")

    elif categoria == "Disciplina":
        if detalhe == "Amarelo":
            inc("cartoes_amarelos")
        elif detalhe == "Vermelho":
            inc("cartoes_vermelhos")
        elif detalhe == "2 min":
            inc("suspensoes_2min")
        elif detalhe == "Azul":
            inc("cartoes_azuis")

    elif categoria == "Defesa":
        if detalhe == "Interceção":
            inc("defesas_intercecao")
        elif detalhe == "Bloco":
            inc("defesas_bloco")
        elif detalhe == "Desarme":
            inc("defesas_desarme")

    elif categoria == "Falta Técnica":
        inc("faltas_tecnicas")
        if detalhe == "Passos":
            inc("faltas_passos")
        elif detalhe == "Dribles":
            inc("faltas_dribles")
        elif detalhe == "Receção":
            inc("faltas_rececao")
        elif detalhe == "Passe":
            inc("faltas_passe")
        elif detalhe == "Atacante":
            inc("faltas_atacante")

    elif categoria == "7 Metros Ganho":
        inc("ganhou_7m")

    elif categoria in ["Remate", "Remate GR"]:
        inc("remates_total")
        zona_map = {
            "6m": "remates_6m",
            "9m": "remates_9m",
            "7m": "remates_7m",
            "Ponta": "remates_ponta",
            "Pivô": "remates_pivot",
            "Pivot": "remates_pivot",
            "Contra-ataque": "remates_contra_ataque",
            "Transição": "remates_transicao",
            "Sem GR": "remates_sem_gr",
        }
        if zona in zona_map:
            inc(zona_map[zona])

        if resultado == "Golo":
            inc("remates_golo")
            inc("golos_marcados")
        elif resultado in ["Fora", "Falhado"]:
            inc("remates_fora")
        elif resultado == "Defesa GR":
            inc("remates_defesa_gr")
        elif resultado == "Poste":
            inc("remates_poste")
        elif resultado == "Bloco":
            inc("remates_bloco")

    elif categoria == "Defesa GR":
        inc("defesas_gr")

    elif categoria == "Golo Sofrido":
        inc("golos_sofridos")

    elif categoria == "Golo Sofrido Baliza Aberta":
        inc("golos_sofridos_baliza_aberta")

    return delta


def registar_evento(jogador, categoria, detalhe="", zona="", resultado="", posicao_baliza=""):
    score_home_delta = 0
    score_away_delta = 0

    if categoria in ["Remate", "Remate GR"] and resultado == "Golo":
        score_home_delta = 1

    if categoria in ["Golo Sofrido", "Golo Sofrido Baliza Aberta"]:
        score_away_delta = 1

    stats_delta = criar_delta(categoria, detalhe, zona, resultado)

    if jogador:
        ensure_player_stats(jogador)
        apply_stats_delta(jogador, stats_delta)

    st.session_state.resultado_cd_xico += score_home_delta
    st.session_state.resultado_adversario += score_away_delta

    evento = {
        "hora": datetime.now().strftime("%H:%M:%S"),
        "parte": st.session_state.parte,
        "numero_camisola": jogador["numero"] if jogador else "",
        "atleta": jogador["nome"] if jogador else "Sem atleta",
        "gr": jogador["gr"] if jogador else "",
        "categoria": categoria,
        "detalhe": detalhe,
        "zona": zona,
        "resultado": resultado,
        "posicao_baliza": posicao_baliza,
        "score_home_delta": score_home_delta,
        "score_away_delta": score_away_delta,
        "stats_delta": stats_delta,
    }

    st.session_state.eventos_log.append(evento)

    nome = f"{jogador['numero']} · {jogador['nome']}" if jogador else "Sem atleta"
    extra = " / ".join([x for x in [categoria, detalhe, zona, resultado, posicao_baliza] if x])
    st.session_state.ultima_acao_registada = f"{nome} → {extra}"
    st.session_state.ultima_acao_anulada = ""

    reset_modal()
    save_backup()
    st.rerun()


def anular_ultima_acao():
    if not st.session_state.eventos_log:
        st.session_state.ultima_acao_anulada = "Não existiam ações para anular."
        return

    ultimo = st.session_state.eventos_log.pop()
    numero = ultimo.get("numero_camisola")
    jogador = get_player_by_num(numero) if numero != "" else None

    if jogador:
        delta = ultimo.get("stats_delta", {})
        reverse_delta = {k: -v for k, v in delta.items()}
        apply_stats_delta(jogador, reverse_delta)

    st.session_state.resultado_cd_xico = max(0, st.session_state.resultado_cd_xico - int(ultimo.get("score_home_delta", 0)))
    st.session_state.resultado_adversario = max(0, st.session_state.resultado_adversario - int(ultimo.get("score_away_delta", 0)))

    st.session_state.ultima_acao_anulada = f"Ação anulada: {ultimo.get('atleta')} → {ultimo.get('categoria')}"
    st.session_state.ultima_acao_registada = ""

    reset_modal()
    save_backup()
    st.rerun()


# =========================================================
# DATAFRAMES / EXPORTAÇÃO
# =========================================================
def dataframe_resumo():
    rows = []
    for jogador in get_convocados():
        ensure_player_stats(jogador)
        rows.append(st.session_state.stats[jogador["numero"]])

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    base = ["numero_camisola", "atleta", "gr"]
    cols = base + STAT_KEYS
    return df[cols].sort_values(["numero_camisola", "atleta"])


def dataframe_eventos():
    if not st.session_state.eventos_log:
        return pd.DataFrame(columns=[
            "hora", "parte", "numero_camisola", "atleta", "gr", "categoria",
            "detalhe", "zona", "resultado", "posicao_baliza",
            "score_home_delta", "score_away_delta"
        ])

    df = pd.DataFrame(st.session_state.eventos_log)
    return df.drop(columns=["stats_delta"], errors="ignore")


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
# MODAL DE REGISTO
# =========================================================
def render_buttons(options, prefix, n_cols=2, on_pick=None):
    st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
    for i in range(0, len(options), n_cols):
        cols = st.columns(n_cols)
        for idx, option in enumerate(options[i:i+n_cols]):
            with cols[idx]:
                if st.button(option, key=f"{prefix}_{option}", use_container_width=True):
                    if on_pick:
                        on_pick(option)
    st.markdown("</div>", unsafe_allow_html=True)


def render_goal_positions(jogador, categoria, zona):
    st.markdown("#### Posição na baliza")
    zonas = list(ZONAS_BALIZA.items())

    for i in range(0, len(zonas), 3):
        cols = st.columns(3)
        for idx, (num, label) in enumerate(zonas[i:i+3]):
            with cols[idx]:
                if st.button(f"{num}\n{label}", key=f"baliza_{categoria}_{zona}_{num}", use_container_width=True):
                    resultado = "Golo" if categoria == "Golo Sofrido" else "Defesa GR"
                    registar_evento(
                        jogador=jogador,
                        categoria=categoria,
                        zona=zona,
                        resultado=resultado,
                        posicao_baliza=f"{num} - {label}",
                    )


@st.dialog("Registo rápido")
def modal_registo():
    jogador = get_player_by_num(st.session_state.modal_jogador_num)

    if not jogador:
        st.warning("Atleta não encontrado.")
        if st.button("Fechar"):
            reset_modal()
            st.rerun()
        return

    st.markdown(f"### {jogador['numero']} · {jogador['nome']} {'🧤' if jogador['gr'] else ''}")

    if st.button("Fechar janela", use_container_width=True):
        reset_modal()
        st.rerun()

    st.markdown("---")

    acoes = GR_ACOES if jogador["gr"] else CAMPO_ACOES

    if st.session_state.modal_acao is None:
        st.markdown("#### Escolher ação")
        render_buttons(
            list(acoes.keys()),
            prefix=f"acao_{jogador['numero']}",
            n_cols=2,
            on_pick=lambda acao: (
                setattr(st.session_state, "modal_acao", acao),
                setattr(st.session_state, "modal_detalhe", None),
                setattr(st.session_state, "modal_zona", None),
                setattr(st.session_state, "modal_resultado", None),
                st.rerun()
            )
        )
        return

    acao = st.session_state.modal_acao
    st.markdown(f"#### {acao}")

    if st.button("Voltar às ações", use_container_width=True):
        st.session_state.modal_acao = None
        st.session_state.modal_detalhe = None
        st.session_state.modal_zona = None
        st.session_state.modal_resultado = None
        st.rerun()

    if not jogador["gr"]:
        if acao == "Remate":
            if st.session_state.modal_zona is None:
                st.markdown("Escolher zona de remate")
                render_buttons(
                    CAMPO_ACOES["Remate"],
                    prefix=f"zona_remate_{jogador['numero']}",
                    n_cols=2,
                    on_pick=lambda zona: (
                        setattr(st.session_state, "modal_zona", zona),
                        st.rerun()
                    )
                )
                return

            st.markdown(f"Zona: **{st.session_state.modal_zona}**")
            st.markdown("Escolher resultado")
            render_buttons(
                RESULTADOS_REMATE_CAMPO,
                prefix=f"res_remate_{jogador['numero']}_{st.session_state.modal_zona}",
                n_cols=2,
                on_pick=lambda resultado: registar_evento(
                    jogador=jogador,
                    categoria="Remate",
                    zona=st.session_state.modal_zona,
                    resultado=resultado,
                )
            )
            return

        if acao == "7 Metros Ganho":
            registar_evento(jogador=jogador, categoria="7 Metros Ganho", detalhe="7 Metros Ganho")
            return

        render_buttons(
            CAMPO_ACOES[acao],
            prefix=f"campo_{jogador['numero']}_{acao}",
            n_cols=2,
            on_pick=lambda detalhe: registar_evento(
                jogador=jogador,
                categoria=acao,
                detalhe=detalhe,
            )
        )
        return

    if jogador["gr"]:
        if acao in ["Defesa", "Golo Sofrido"]:
            if st.session_state.modal_zona is None:
                st.markdown("Escolher zona de origem")
                render_buttons(
                    GR_ACOES[acao],
                    prefix=f"gr_zona_{jogador['numero']}_{acao}",
                    n_cols=2,
                    on_pick=lambda zona: (
                        setattr(st.session_state, "modal_zona", zona),
                        st.rerun()
                    )
                )
                return

            st.markdown(f"Origem: **{st.session_state.modal_zona}**")
            render_goal_positions(jogador, "Defesa GR" if acao == "Defesa" else "Golo Sofrido", st.session_state.modal_zona)
            return

        if acao == "Remate":
            render_buttons(
                GR_ACOES["Remate"],
                prefix=f"gr_remate_{jogador['numero']}",
                n_cols=2,
                on_pick=lambda resultado: registar_evento(
                    jogador=jogador,
                    categoria="Remate GR",
                    resultado=resultado,
                    zona="GR",
                )
            )
            return

        if acao == "Assistência":
            registar_evento(jogador=jogador, categoria="Assistência", detalhe="Contra-ataque")
            return

        render_buttons(
            GR_ACOES[acao],
            prefix=f"gr_{jogador['numero']}_{acao}",
            n_cols=2,
            on_pick=lambda detalhe: registar_evento(
                jogador=jogador,
                categoria=acao,
                detalhe=detalhe,
            )
        )


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
st.caption("Modo rápido — tocar no atleta, escolher ação e registar.")

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
            save_backup()
            reset_modal()
            st.rerun()
    st.stop()

# =========================================================
# TOPO DO JOGO
# =========================================================
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

# =========================================================
# AÇÃO GLOBAL
# =========================================================
st.markdown("---")
g1, g2 = st.columns([1, 3])
with g1:
    if st.button("Golo sofrido baliza aberta", use_container_width=True):
        registar_evento(
            jogador=None,
            categoria="Golo Sofrido Baliza Aberta",
            detalhe="Sem GR",
            zona="Baliza aberta",
            resultado="Golo",
        )

# =========================================================
# PLANTEL
# =========================================================
convocados = get_convocados()

st.markdown("### Atletas")
st.markdown("<div class='athlete-grid'>", unsafe_allow_html=True)

grs = [j for j in convocados if j["gr"]]
campo = [j for j in convocados if not j["gr"]]

if grs:
    st.markdown("#### Guarda-redes")
    cols_gr = st.columns(2)
    for idx, jogador in enumerate(grs):
        with cols_gr[idx % 2]:
            if st.button(f"🧤 {jogador['numero']} · {jogador['nome']}", key=f"gr_{jogador['numero']}", use_container_width=True):
                st.session_state.modal_jogador_num = jogador["numero"]
                st.session_state.modal_acao = None
                st.session_state.modal_zona = None
                st.rerun()

st.markdown("#### Jogadores de campo")
cols = st.columns(2)
for idx, jogador in enumerate(campo):
    with cols[idx % 2]:
        if st.button(f"{jogador['numero']} · {jogador['nome']}", key=f"campo_{jogador['numero']}", use_container_width=True):
            st.session_state.modal_jogador_num = jogador["numero"]
            st.session_state.modal_acao = None
            st.session_state.modal_zona = None
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.modal_jogador_num is not None:
    modal_registo()

# =========================================================
# FECHO / RESUMO
# =========================================================
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

with st.expander("Últimos registos"):
    df_eventos = dataframe_eventos()
    if not df_eventos.empty:
        st.dataframe(df_eventos.tail(30).iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Ainda não existem ações registadas.")
