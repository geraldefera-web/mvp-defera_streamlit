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

        /* Inputs */
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

        /* dropdown aberto */
        div[role="listbox"],
        ul[role="listbox"] {{
            background: #f2f2f2 !important;
        }}

        li[role="option"], li[role="option"] * {{
            color: black !important;
        }}

        /* Botões */
        .stButton > button {{
            width: 100%;
            border-radius: 10px;
            border: 1px solid {DEFERA_RED};
            background-color: {DEFERA_RED};
            color: white !important;
            font-weight: 700;
            min-height: 2.7rem;
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
            min-height: 2.7rem;
        }}

        /* Métricas */
        div[data-testid="stMetric"] {{
            background: {DEFERA_PANEL};
            border: 1px solid {DEFERA_GREY};
            border-radius: 12px;
            padding: 10px 12px;
        }}

        /* Caixas utilitárias */
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

        /* Grelhas compactas */
        .compact-grid .stButton > button {{
            min-height: 2.15rem !important;
            padding: 0.20rem 0.35rem !important;
            font-size: 0.82rem !important;
            line-height: 1.05 !important;
            border-radius: 8px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}

        .action-grid .stButton > button {{
            min-height: 2.2rem !important;
            padding: 0.25rem 0.35rem !important;
            font-size: 0.84rem !important;
            border-radius: 8px !important;
            white-space: nowrap !important;
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
                font-size: 2.1rem !important;
            }}

            .compact-grid .stButton > button {{
                min-height: 2.05rem !important;
                font-size: 0.78rem !important;
                padding: 0.18rem 0.28rem !important;
            }}

            .action-grid .stButton > button {{
                min-height: 2.1rem !important;
                font-size: 0.80rem !important;
                padding: 0.20rem 0.28rem !important;
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
        {"numero": 1, "nome": "Nuno Pinheiro", "gr": False},
        {"numero": 2, "nome": "Armando Araujo", "gr": False},
        {"numero": 3, "nome": "João Leite", "gr": False},
        {"numero": 4, "nome": "César Gonçalves", "gr": False},
        {"numero": 5, "nome": "Roberto Ferreira", "gr": False},
        {"numero": 6, "nome": "Pedro Freitas", "gr": False},
        {"numero": 7, "nome": "Gabriel Guimarães", "gr": False},
        {"numero": 8, "nome": "Raphael Neto", "gr": False},
        {"numero": 9, "nome": "José Magalhães", "gr": False},
        {"numero": 10, "nome": "José Martins", "gr": True},
        {"numero": 11, "nome": "João Martins", "gr": False},
        {"numero": 12, "nome": "André Silva", "gr": False},
        {"numero": 13, "nome": "Leonardo Pereira", "gr": True},
        {"numero": 14, "nome": "Alexandr Tchikoulaev", "gr": False},
        {"numero": 15, "nome": "José Araújo", "gr": False},
        {"numero": 16, "nome": "Diogo Martins", "gr": False},
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

CAMPOS_EVENTOS = {
    "Golo": "golos",
    "Assistência": "assistencias",
    "Remate Falhado": "remates_falhados",
    "Perda de Bola": "perdas_bola",
    "Recuperação de Bola": "recuperacoes_bola",
    "Exclusão 2 min": "exclusoes_2min",
    "Cartão Amarelo": "cartoes_amarelos",
    "Cartão Vermelho": "cartoes_vermelhos",
    "Defesa GR": "defesas_gr",
    "7m Golo": "livres_7m_golo",
    "7m Falhado": "livres_7m_falhados",
}

EVENTOS_JOGADOR = [
    "Golo",
    "Assistência",
    "Remate Falhado",
    "Perda de Bola",
    "Recuperação de Bola",
    "Exclusão 2 min",
    "Cartão Amarelo",
    "Cartão Vermelho",
    "7m Golo",
    "7m Falhado",
]

EVENTOS_GR = EVENTOS_JOGADOR + ["Defesa GR"]


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
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_jogo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


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


def short_name(nome):
    partes = nome.split()
    if len(partes) <= 2:
        return nome
    return f"{partes[0]} {partes[-1]}"


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
            "golos": 0,
            "assistencias": 0,
            "remates_falhados": 0,
            "perdas_bola": 0,
            "recuperacoes_bola": 0,
            "exclusoes_2min": 0,
            "cartoes_amarelos": 0,
            "cartoes_vermelhos": 0,
            "defesas_gr": 0,
            "livres_7m_golo": 0,
            "livres_7m_falhados": 0,
            "golos_1p": 0,
            "golos_2p": 0,
        }


def registar_evento(numero, evento):
    jogador = get_player_by_num(numero)
    if not jogador:
        return

    ensure_player_stats(jogador)
    campo = CAMPOS_EVENTOS[evento]
    st.session_state.stats[numero][campo] += 1

    if evento in ["Golo", "7m Golo"]:
        if st.session_state.parte == "1.ª Parte":
            st.session_state.stats[numero]["golos_1p"] += 1
        else:
            st.session_state.stats[numero]["golos_2p"] += 1

    st.session_state.eventos_log.append(
        {
            "parte": st.session_state.parte,
            "numero_camisola": jogador["numero"],
            "atleta": jogador["nome"],
            "evento": evento,
        }
    )
    st.session_state.selecionado_id = numero
    st.session_state.ultima_acao_registada = f"{jogador['numero']} · {jogador['nome']} → {evento}"
    st.session_state.ultima_acao_anulada = ""


def anular_ultima_acao():
    if not st.session_state.eventos_log:
        st.session_state.ultima_acao_anulada = "Não existiam ações para anular."
        return

    ultimo = st.session_state.eventos_log.pop()
    numero = ultimo["numero_camisola"]
    evento = ultimo["evento"]
    campo = CAMPOS_EVENTOS[evento]

    if numero in st.session_state.stats and st.session_state.stats[numero][campo] > 0:
        st.session_state.stats[numero][campo] -= 1

        if evento in ["Golo", "7m Golo"]:
            if ultimo["parte"] == "1.ª Parte" and st.session_state.stats[numero]["golos_1p"] > 0:
                st.session_state.stats[numero]["golos_1p"] -= 1
            if ultimo["parte"] == "2.ª Parte" and st.session_state.stats[numero]["golos_2p"] > 0:
                st.session_state.stats[numero]["golos_2p"] -= 1

    st.session_state.ultima_acao_anulada = (
        f"Ação anulada: {ultimo['numero_camisola']} · {ultimo['atleta']} → {evento} ({ultimo['parte']})"
    )
    st.session_state.ultima_acao_registada = ""


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
                    st.rerun()


def render_grelha_acoes(eventos, jogador_numero, n_cols=2):
    for i in range(0, len(eventos), n_cols):
        cols = st.columns(n_cols)
        bloco = eventos[i:i + n_cols]

        for idx, evento in enumerate(bloco):
            with cols[idx]:
                if st.button(evento, key=f"evento_{jogador_numero}_{evento}", use_container_width=True):
                    registar_evento(jogador_numero, evento)
                    st.rerun()


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
        "golos",
        "assistencias",
        "remates_falhados",
        "perdas_bola",
        "recuperacoes_bola",
        "exclusoes_2min",
        "cartoes_amarelos",
        "cartoes_vermelhos",
        "livres_7m_golo",
        "livres_7m_falhados",
        "defesas_gr",
        "golos_1p",
        "golos_2p",
    ]].sort_values(["numero_camisola", "atleta"])


def dataframe_eventos():
    if not st.session_state.eventos_log:
        return pd.DataFrame(columns=["parte", "numero_camisola", "atleta", "evento"])
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
        dataframe_eventos().to_excel(writer, sheet_name="Log de Eventos", index=False)
    output.seek(0)
    return output.getvalue()


# =========================================================
# RENDER PRINCIPAL
# =========================================================
init_state()

st.title("DEFERA Stats Live")
st.caption("Seleciona o atleta e regista a ação.")

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
            st.rerun()
    st.stop()

# topo
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
        st.markdown(
            f"""
            <div class='selected-athlete-fixed'>
                Atleta selecionado — Camisola {selecionado['numero']} · {selecionado['nome']}{' · GR' if selecionado['gr'] else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Seleciona um atleta.")

    subtab1, subtab2 = st.tabs(["Atletas", "Ações"])

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
        if selecionado:
            eventos = EVENTOS_GR if selecionado["gr"] else EVENTOS_JOGADOR
            st.markdown("<div class='action-grid'>", unsafe_allow_html=True)
            render_grelha_acoes(eventos, selecionado["numero"], n_cols=2)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Seleciona primeiro um atleta na tab Atletas.")

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
        with st.expander("Ver últimas ações"):
            st.dataframe(
                dataframe_eventos().tail(20).iloc[::-1],
                use_container_width=True,
                hide_index=True,
            )
