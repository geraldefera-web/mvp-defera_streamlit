import io
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="DEFERA Stats Live", layout="wide")

# =========================================================
# ESTILO
# =========================================================
DEFERA_RED = "#D40000"
DEFERA_BLACK = "#000000"
DEFERA_DARK = "#111111"
DEFERA_GREY = "#2A2A2A"
DEFERA_PANEL = "#151515"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {DEFERA_BLACK};
            color: white;
        }}

        html, body, [class*="css"] {{
            color: white;
        }}

        .block-container {{
            max-width: 1200px;
            padding-top: 0.8rem;
            padding-bottom: 1rem;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: white !important;
        }}

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        textarea,
        input {{
            background: #111111 !important;
            color: white !important;
            border: 1px solid #444 !important;
            -webkit-text-fill-color: white !important;
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
            border-radius: 10px;
            border: 1px solid {DEFERA_RED};
            background-color: {DEFERA_RED};
            color: white !important;
            font-weight: 700;
            min-height: 2.55rem;
        }}

        .stButton > button:hover {{
            background-color: #a90000;
            border-color: #a90000;
            color: white !important;
        }}

        .stDownloadButton > button {{
            width: 100%;
            border-radius: 10px;
            border: 1px solid {DEFERA_RED};
            background-color: {DEFERA_RED};
            color: white !important;
            font-weight: 700;
            min-height: 2.55rem;
        }}

        div[data-testid="stMetric"] {{
            background: {DEFERA_PANEL};
            border: 1px solid {DEFERA_GREY};
            border-radius: 12px;
            padding: 10px 12px;
        }}

        .note-box {{
            background: rgba(212,0,0,0.12);
            border-left: 4px solid {DEFERA_RED};
            border-radius: 8px;
            padding: 10px 12px;
            margin: 8px 0 14px 0;
        }}

        .danger-box {{
            background: rgba(255,0,0,0.14);
            border: 1px solid rgba(255,0,0,0.35);
            border-radius: 8px;
            padding: 10px 12px;
            margin: 8px 0 14px 0;
        }}

        .compact-grid .stButton > button {{
            min-height: 2.1rem !important;
            padding: 0.20rem 0.35rem !important;
            font-size: 0.82rem !important;
            line-height: 1.05 !important;
            border-radius: 8px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}

        .action-grid .stButton > button {{
            min-height: 2.45rem !important;
            padding: 0.25rem 0.30rem !important;
            font-size: 0.76rem !important;
            border-radius: 8px !important;
            line-height: 1.05 !important;
            white-space: pre-line !important;
        }}

        .zone-grid .stButton > button {{
            min-height: 4.35rem !important;
            padding: 0.28rem 0.22rem !important;
            font-size: 0.66rem !important;
            border-radius: 8px !important;
            line-height: 1.05 !important;
            white-space: pre-line !important;
        }}

        .selected-athlete-fixed {{
            background: rgba(212,0,0,0.16);
            border: 1px solid rgba(212,0,0,0.35);
            border-radius: 10px;
            padding: 8px 10px;
            margin-bottom: 10px;
            font-weight: 700;
            position: sticky;
            top: 0.25rem;
            z-index: 10;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 0.55rem;
                padding-right: 0.55rem;
            }}

            h1 {{
                font-size: 2.0rem !important;
            }}

            .compact-grid .stButton > button {{
                min-height: 2.0rem !important;
                font-size: 0.78rem !important;
                padding: 0.18rem 0.28rem !important;
            }}

            .action-grid .stButton > button {{
                min-height: 2.15rem !important;
                font-size: 0.73rem !important;
                padding: 0.18rem 0.24rem !important;
            }}

            .zone-grid .stButton > button {{
                min-height: 4.55rem !important;
                font-size: 0.60rem !important;
                padding: 0.22rem 0.12rem !important;
                line-height: 1.0 !important;
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

TIPOS_REMATE = [
    "1.ª Linha",
    "2.ª Linha",
    "Ponta",
    "Pivô",
    "Contra-ataque",
    "7 metros",
    "GR",
]

RESULTADOS_REMATE = [
    "Golo",
    "Falhado",
    "Defesa GR",
    "Poste",
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
        "tipo_remate_atual": None,
        "resultado_remate_atual": None,
        "zona_baliza_atual": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_jogo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def limpar_selecao_remate():
    st.session_state.tipo_remate_atual = None
    st.session_state.resultado_remate_atual = None
    st.session_state.zona_baliza_atual = None


def get_plantel(equipa_nome):
    return EQUIPAS.get(equipa_nome, [])


def get_convocados():
    return sorted(
        [j for j in get_plantel(st.session_state.equipa) if j["numero"] in st.session_state.convocados_ids],
        key=lambda x: (x["gr"], x["numero"], x["nome"]),
    )


def get_player_by_num(numero):
    for jogador in get_convocados():
        if jogador["numero"] == numero:
            return jogador
    return None


def atleta_selecionado_e_gr():
    jogador = get_player_by_num(st.session_state.selecionado_id)
    return jogador["gr"] if jogador else False


def nome_compacto(nome, limite=14):
    partes = nome.split()
    if len(partes) == 1:
        base = nome
    elif len(partes) == 2:
        base = nome
    else:
        base = f"{partes[0]} {partes[-1]}"
    return base if len(base) <= limite else base[:limite - 1] + "…"


def ensure_player_stats(jogador):
    pid = jogador["numero"]
    if pid not in st.session_state.stats:
        st.session_state.stats[pid] = {
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "gr": jogador["gr"],
            "remates_total": 0,
            "golos": 0,
            "falhados": 0,
            "defesas_gr_sofridas": 0,
            "postes": 0,
            "remates_1_linha": 0,
            "remates_2_linha": 0,
            "remates_ponta": 0,
            "remates_pivo": 0,
            "remates_contra_ataque": 0,
            "remates_7m": 0,
            "golos_1p": 0,
            "golos_2p": 0,
            "eficacia_percent": 0.0,
        }


def mapear_tipo_remate(tipo):
    mapa = {
        "1.ª Linha": "remates_1_linha",
        "2.ª Linha": "remates_2_linha",
        "Ponta": "remates_ponta",
        "Pivô": "remates_pivo",
        "Contra-ataque": "remates_contra_ataque",
        "7 metros": "remates_7m",
        "GR": None,
    }
    return mapa.get(tipo)


def confirmar_registo_remate():
    numero = st.session_state.selecionado_id
    tipo = st.session_state.tipo_remate_atual
    resultado = st.session_state.resultado_remate_atual
    zona = st.session_state.zona_baliza_atual

    if not numero or not resultado or not zona:
        return

    jogador = get_player_by_num(numero)
    if not jogador:
        return

    if jogador["gr"] and not tipo:
        tipo = "GR"

    if not jogador["gr"] and not tipo:
        return

    ensure_player_stats(jogador)
    pid = jogador["numero"]

    st.session_state.stats[pid]["remates_total"] += 1

    campo_tipo = mapear_tipo_remate(tipo)
    if campo_tipo:
        st.session_state.stats[pid][campo_tipo] += 1

    if resultado == "Golo":
        st.session_state.stats[pid]["golos"] += 1
        if st.session_state.parte == "1.ª Parte":
            st.session_state.stats[pid]["golos_1p"] += 1
        else:
            st.session_state.stats[pid]["golos_2p"] += 1
    elif resultado == "Falhado":
        st.session_state.stats[pid]["falhados"] += 1
    elif resultado == "Defesa GR":
        st.session_state.stats[pid]["defesas_gr_sofridas"] += 1
    elif resultado == "Poste":
        st.session_state.stats[pid]["postes"] += 1

    remates_total = st.session_state.stats[pid]["remates_total"]
    golos = st.session_state.stats[pid]["golos"]
    st.session_state.stats[pid]["eficacia_percent"] = round((golos / remates_total) * 100, 1) if remates_total > 0 else 0.0

    st.session_state.eventos_log.append(
        {
            "parte": st.session_state.parte,
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "tipo_remate": tipo,
            "resultado_remate": resultado,
            "zona_baliza": zona,
            "zona_baliza_label": ZONAS_BALIZA.get(zona, ""),
        }
    )

    st.session_state.ultima_acao_registada = (
        f"{jogador['numero']} · {jogador['nome']} → {tipo} / {resultado} / Zona {zona} - {ZONAS_BALIZA.get(zona, '')}"
    )
    st.session_state.ultima_acao_anulada = ""
    limpar_selecao_remate()


def anular_ultima_acao():
    if not st.session_state.eventos_log:
        st.session_state.ultima_acao_anulada = "Não existiam ações para anular."
        return

    ultimo = st.session_state.eventos_log.pop()
    numero = ultimo["numero_camisola"]
    tipo = ultimo["tipo_remate"]
    resultado = ultimo["resultado_remate"]

    jogador = get_player_by_num(numero)
    if not jogador:
        st.session_state.ultima_acao_anulada = "Última ação anulada."
        return

    ensure_player_stats(jogador)
    s = st.session_state.stats[numero]

    if s["remates_total"] > 0:
        s["remates_total"] -= 1

    campo_tipo = mapear_tipo_remate(tipo)
    if campo_tipo and s[campo_tipo] > 0:
        s[campo_tipo] -= 1

    if resultado == "Golo":
        if s["golos"] > 0:
            s["golos"] -= 1
        if ultimo["parte"] == "1.ª Parte" and s["golos_1p"] > 0:
            s["golos_1p"] -= 1
        if ultimo["parte"] == "2.ª Parte" and s["golos_2p"] > 0:
            s["golos_2p"] -= 1
    elif resultado == "Falhado" and s["falhados"] > 0:
        s["falhados"] -= 1
    elif resultado == "Defesa GR" and s["defesas_gr_sofridas"] > 0:
        s["defesas_gr_sofridas"] -= 1
    elif resultado == "Poste" and s["postes"] > 0:
        s["postes"] -= 1

    remates_total = s["remates_total"]
    golos = s["golos"]
    s["eficacia_percent"] = round((golos / remates_total) * 100, 1) if remates_total > 0 else 0.0

    st.session_state.ultima_acao_anulada = (
        f"Ação anulada: {ultimo['numero_camisola']} · {ultimo['atleta']} → "
        f"{ultimo['tipo_remate']} / {ultimo['resultado_remate']} / Zona {ultimo['zona_baliza']} - {ultimo['zona_baliza_label']}"
    )
    st.session_state.ultima_acao_registada = ""
    limpar_selecao_remate()


# =========================================================
# GRELHAS MOBILE
# =========================================================
def render_grelha_atletas(jogadores, prefix, n_cols=2):
    for i in range(0, len(jogadores), n_cols):
        cols = st.columns(n_cols)
        bloco = jogadores[i:i + n_cols]

        for idx, j in enumerate(bloco):
            selecionado = st.session_state.selecionado_id == j["numero"]
            label = f"{j['numero']} · {nome_compacto(j['nome'])}"
            if j["gr"]:
                label += " 🧤"
            if selecionado:
                label = f"✅ {label}"

            with cols[idx]:
                if st.button(label, key=f"{prefix}_{j['numero']}", use_container_width=True):
                    st.session_state.selecionado_id = j["numero"]
                    limpar_selecao_remate()
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
                    st.rerun()


def render_grelha_zonas():
    zonas = list(ZONAS_BALIZA.keys())
    idx = 0
    for _ in range(3):
        cols = st.columns(3)
        for c in cols:
            zona = zonas[idx]
            selecionado = st.session_state.zona_baliza_atual == zona

            label = f"{zona}\n{ZONAS_BALIZA[zona]}"
            if selecionado:
                label = f"✅ {zona}\n{ZONAS_BALIZA[zona]}"

            with c:
                if st.button(label, key=f"zona_{zona}", use_container_width=True):
                    st.session_state.zona_baliza_atual = zona
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
        "remates_total",
        "golos",
        "falhados",
        "defesas_gr_sofridas",
        "postes",
        "remates_1_linha",
        "remates_2_linha",
        "remates_ponta",
        "remates_pivo",
        "remates_contra_ataque",
        "remates_7m",
        "golos_1p",
        "golos_2p",
        "eficacia_percent",
    ]].sort_values(["numero_camisola", "atleta"])


def dataframe_eventos():
    if not st.session_state.eventos_log:
        return pd.DataFrame(
            columns=[
                "parte",
                "numero_camisola",
                "atleta",
                "tipo_remate",
                "resultado_remate",
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
        ficha_jogo_df(momento_exportacao=momento_exportacao).to_excel(
            writer, sheet_name="Ficha do Jogo", index=False
        )
        dataframe_resumo().to_excel(writer, sheet_name="Resumo por Atleta", index=False)
        dataframe_eventos().to_excel(writer, sheet_name="Log de Remates", index=False)
    output.seek(0)
    return output.getvalue()


# =========================================================
# RENDER PRINCIPAL
# =========================================================
init_state()

st.title("DEFERA Stats Live")
st.caption("Seleciona o atleta e regista o remate.")

if not st.session_state.jogo_iniciado:
    st.subheader("Configuração do jogo")

    equipa = st.selectbox("Equipa", list(EQUIPAS.keys()))
    adversario = st.text_input("Adversário")
    competicao = st.text_input("Competição")
    local_jogo = st.text_input("Local")
    data_jogo = st.text_input("Data do jogo", value=st.session_state.data_jogo)

    plantel = get_plantel(equipa)
    st.markdown("#### Convocados")

    opcoes = {
        f"Camisola {j['numero']} · {j['nome']}{' 🧤' if j['gr'] else ''}": j["numero"]
        for j in plantel
    }
    labels = st.multiselect("Selecionar atletas", list(opcoes.keys()))
    convocados_ids = [opcoes[label] for label in labels]

    if st.button("Iniciar jogo", use_container_width=True):
        if not adversario.strip():
            st.warning("Preenche o adversário.")
        elif not convocados_ids:
            st.warning("Seleciona os convocados.")
        else:
            st.session_state.jogo_iniciado = True
            st.session_state.equipa = equipa
            st.session_state.adversario = adversario.strip()
            st.session_state.competicao = competicao.strip()
            st.session_state.local_jogo = local_jogo.strip()
            st.session_state.data_jogo = data_jogo.strip()
            st.session_state.convocados_ids = convocados_ids
            st.session_state.selecionado_id = sorted(convocados_ids)[0]
            limpar_selecao_remate()
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
    st.metric("Selecionado", st.session_state.selecionado_id if st.session_state.selecionado_id else "-")

if st.session_state.ultima_acao_anulada:
    st.markdown(
        f"<div class='danger-box'><strong>{st.session_state.ultima_acao_anulada}</strong></div>",
        unsafe_allow_html=True,
    )
elif st.session_state.ultima_acao_registada:
    st.markdown(
        f"<div class='note-box'><strong>Última ação registada:</strong> {st.session_state.ultima_acao_registada}</div>",
        unsafe_allow_html=True,
    )

tab1, tab2, tab3 = st.tabs(["Registo rápido", "Fecho do jogo", "Resumo"])

with tab1:
    c1, c2, c3, c4 = st.columns([1, 1.2, 1.25, 1])
    with c1:
        if st.button("Passar para 2.ª Parte", use_container_width=True, disabled=st.session_state.parte == "2.ª Parte"):
            st.session_state.parte = "2.ª Parte"
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
    campo = [j for j in convocados if not j["gr"]]
    grs = [j for j in convocados if j["gr"]]
    selecionado = get_player_by_num(st.session_state.selecionado_id)

    st.markdown("### Registo rápido")

    if selecionado:
        tipo_txt = st.session_state.tipo_remate_atual or ("GR" if selecionado["gr"] else "—")
        resultado_txt = st.session_state.resultado_remate_atual or "—"
        zona_txt = (
            f"{st.session_state.zona_baliza_atual} - {ZONAS_BALIZA[st.session_state.zona_baliza_atual]}"
            if st.session_state.zona_baliza_atual is not None
            else "—"
        )
        st.markdown(
            f"""
            <div class='selected-athlete-fixed'>
                Atleta — Camisola {selecionado['numero']} · {selecionado['nome']}{' · GR' if selecionado['gr'] else ''}<br>
                Tipo — {tipo_txt} &nbsp;&nbsp;|&nbsp;&nbsp; Resultado — {resultado_txt} &nbsp;&nbsp;|&nbsp;&nbsp; Zona — {zona_txt}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Seleciona um atleta.")

    subtab1, subtab2, subtab3, subtab4 = st.tabs(["Atletas", "Tipo", "Resultado", "Baliza"])

    with subtab1:
        st.markdown("<div class='compact-grid'>", unsafe_allow_html=True)
        if campo:
            st.markdown("**Jogadores de campo**")
            render_grelha_atletas(campo, "campo", n_cols=2)
        if grs:
            st.markdown("**Guarda-redes**")
            render_grelha_atletas(grs, "gr", n_cols=2)
        st.markdown("</div>", unsafe_allow_html=True)

    with subtab2:
        if atleta_selecionado_e_gr():
            st.info("Para guarda-redes, o tipo não é obrigatório. A app assume GR automaticamente.")
            if st.button("Assumir tipo GR", key="tipo_gr", use_container_width=True):
                st.session_state.tipo_remate_atual = "GR"
                st.rerun()
        else:
            st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
            render_grelha_lista_botoes(
                [t for t in TIPOS_REMATE if t != "GR"],
                "tipo_remate_atual",
                "tipo",
                n_cols=2,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    with subtab3:
        st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
        render_grelha_lista_botoes(RESULTADOS_REMATE, "resultado_remate_atual", "resultado", n_cols=2)
        st.markdown("</div>", unsafe_allow_html=True)

    with subtab4:
        st.markdown("**Zona da baliza**")
        st.caption("Seleciona a zona correspondente.")
        st.markdown("<div class='zone-grid'>", unsafe_allow_html=True)
        render_grelha_zonas()
        st.markdown("</div>", unsafe_allow_html=True)

        zona_label = (
            f"{st.session_state.zona_baliza_atual} - {ZONAS_BALIZA[st.session_state.zona_baliza_atual]}"
            if st.session_state.zona_baliza_atual is not None
            else "—"
        )
        st.markdown(f"Zona selecionada: **{zona_label}**")

    jogador_atual = get_player_by_num(st.session_state.selecionado_id) if st.session_state.selecionado_id else None
    tipo_obrigatorio = False if (jogador_atual and jogador_atual["gr"]) else True

    pode_confirmar = all([
        st.session_state.selecionado_id is not None,
        (st.session_state.tipo_remate_atual is not None if tipo_obrigatorio else True),
        st.session_state.resultado_remate_atual is not None,
        st.session_state.zona_baliza_atual is not None,
    ])

    b1, b2 = st.columns(2)
    with b1:
        if st.button("CONFIRMAR REMATE", use_container_width=True, disabled=not pode_confirmar):
            confirmar_registo_remate()
            st.rerun()
    with b2:
        if st.button("LIMPAR SELEÇÃO", use_container_width=True):
            limpar_selecao_remate()
            st.rerun()

with tab2:
    st.markdown("### Fecho do jogo")

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

    st.download_button(
        "Exportar Excel do jogo",
        data=exportar_excel_bytes("Final"),
        file_name=f"defera_stats_{st.session_state.equipa}_{st.session_state.adversario}.xlsx".replace(" ", "_"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

with tab3:
    st.markdown("### Resumo estatístico")
    st.dataframe(dataframe_resumo(), use_container_width=True, hide_index=True)

    if not dataframe_eventos().empty:
        with st.expander("Ver últimos registos"):
            st.dataframe(
                dataframe_eventos().tail(30).iloc[::-1],
                use_container_width=True,
                hide_index=True,
            )
