import io
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="DEFERA Stats Live", layout="wide")

# =========================
# ESTILO
# =========================
DEFERA_RED = "#D40000"
DEFERA_BLACK = "#000000"
DEFERA_DARK = "#111111"
DEFERA_GREY = "#2A2A2A"
DEFERA_LIGHT = "#F5F5F5"

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

        h1, h2, h3, h4, h5, h6, p, div, span, label {{
            color: white !important;
        }}

        .block-container {{
            padding-top: 0.8rem;
            padding-bottom: 1rem;
            max-width: 1450px;
        }}

        div[data-testid="stMetric"] {{
            background-color: {DEFERA_DARK};
            border: 1px solid {DEFERA_GREY};
            border-radius: 12px;
            padding: 8px 12px;
        }}

        div[data-testid="stDataFrame"] {{
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
        }}

        .section-box {{
            background: {DEFERA_DARK};
            border: 1px solid {DEFERA_GREY};
            border-radius: 14px;
            padding: 12px;
            margin-bottom: 12px;
        }}

        .defera-note {{
            background: rgba(212,0,0,0.12);
            border-left: 4px solid {DEFERA_RED};
            padding: 10px 12px;
            border-radius: 8px;
            margin-bottom: 10px;
        }}

        .danger-box {{
            background: rgba(255,0,0,0.14);
            border: 1px solid rgba(255,0,0,0.35);
            padding: 10px 12px;
            border-radius: 10px;
            margin-top: 4px;
            margin-bottom: 10px;
        }}

        /* Inputs base */
        input, textarea {{
            color: white !important;
            -webkit-text-fill-color: white !important;
        }}

        /* Text input / select / multiselect */
        div[data-baseweb="input"] input {{
            color: white !important;
            -webkit-text-fill-color: white !important;
        }}

        div[data-baseweb="select"] > div {{
            background-color: #101010 !important;
            color: white !important;
            border: 1px solid #444 !important;
        }}

        div[data-baseweb="select"] span {{
            color: white !important;
        }}

        div[data-baseweb="tag"] {{
            background-color: {DEFERA_RED} !important;
            color: white !important;
        }}

        div[data-baseweb="popover"] * {{
            color: black !important;
        }}

        ul[role="listbox"] * {{
            color: black !important;
        }}

        li[role="option"] * {{
            color: black !important;
        }}

        /* Botões gerais */
        .stButton > button {{
            width: 100%;
            border-radius: 10px;
            border: 1px solid {DEFERA_RED};
            background-color: {DEFERA_RED};
            color: white;
            font-weight: 700;
            min-height: 2.8rem;
            font-size: 1rem;
        }}

        .stButton > button:hover {{
            background-color: #A90000;
            border-color: #A90000;
            color: white;
        }}

        /* Download button */
        .stDownloadButton > button {{
            width: 100%;
            border-radius: 10px;
            border: 1px solid {DEFERA_RED};
            background-color: {DEFERA_RED};
            color: white;
            font-weight: 700;
            min-height: 2.8rem;
            font-size: 0.95rem;
        }}

        /* Botões dos atletas compactos */
        .player-btn .stButton > button {{
            min-height: 2.1rem !important;
            padding: 0.25rem 0.45rem !important;
            font-size: 0.82rem !important;
            border-radius: 8px !important;
        }}

        /* Botões das ações um pouco mais compactos */
        .action-btn .stButton > button {{
            min-height: 2.4rem !important;
            padding: 0.3rem 0.5rem !important;
            font-size: 0.90rem !important;
            border-radius: 8px !important;
        }}

        /* Forçar colunas lado a lado também em mobile */
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 0.6rem !important;
            align-items: flex-start !important;
        }}

        div[data-testid="column"] {{
            min-width: 0 !important;
        }}

        /* Para a zona principal atletas + ações */
        .mobile-dual-col {{
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }}

        .mobile-panel {{
            background: transparent;
        }}

        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 0.6rem;
                padding-right: 0.6rem;
            }}

            h1 {{
                font-size: 2.2rem !important;
            }}

            h2 {{
                font-size: 1.9rem !important;
            }}

            h3 {{
                font-size: 1.35rem !important;
            }}

            /* Mantém colunas lado a lado em mobile */
            div[data-testid="stHorizontalBlock"] {{
                flex-wrap: nowrap !important;
            }}

            div[data-testid="column"]:first-child {{
                flex: 0.95 1 0% !important;
            }}

            div[data-testid="column"]:last-child {{
                flex: 1.05 1 0% !important;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# DADOS
# =========================
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


# =========================
# FUNÇÕES DE ESTADO
# =========================
def init_state():
    defaults = {
        "jogo_iniciado": False,
        "parte": "1.ª Parte",
        "equipa": None,
        "adversario": "",
        "competicao": "",
        "local_jogo": "",
        "data_jogo": date.today().strftime("%Y-%m-%d"),
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


# =========================
# DATAFRAMES / EXPORTAÇÃO
# =========================
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
        ficha_jogo_df(momento_exportacao=momento_exportacao).to_excel(
            writer, sheet_name="Ficha do Jogo", index=False
        )
        dataframe_resumo().to_excel(writer, sheet_name="Resumo por Atleta", index=False)
        dataframe_eventos().to_excel(writer, sheet_name="Log de Eventos", index=False)
    output.seek(0)
    return output.getvalue()


# =========================
# INÍCIO
# =========================
init_state()

st.title("DEFERA Stats Live")
st.caption("Seleciona o atleta à esquerda e regista a ação à direita.")

# =========================
# CONFIGURAÇÃO DO JOGO
# =========================
if not st.session_state.jogo_iniciado:
    st.subheader("Configuração do jogo")

    c1, c2 = st.columns(2)
    with c1:
        equipa = st.selectbox("Equipa", list(EQUIPAS.keys()))
        adversario = st.text_input("Adversário")
        competicao = st.text_input("Competição")
    with c2:
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

# =========================
# TOPO
# =========================
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
        unsafe_allow_html=True
    )
elif st.session_state.ultima_acao_registada:
    st.markdown(
        f"<div class='defera-note'><strong>Última ação registada:</strong> {st.session_state.ultima_acao_registada}</div>",
        unsafe_allow_html=True
    )

# =========================
# CONTROLOS
# =========================
c1, c2, c3, c4 = st.columns([1, 1.2, 1.25, 1])
with c1:
    if st.button(
        "Passar para 2.ª Parte",
        use_container_width=True,
        disabled=st.session_state.parte == "2.ª Parte"
    ):
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

# =========================
# LADO A LADO: ATLETAS / AÇÕES
# =========================
left, right = st.columns([1, 1], gap="small")

convocados = get_convocados()
campo = [j for j in convocados if not j["gr"]]
grs = [j for j in convocados if j["gr"]]


def render_grid(jogadores, prefix):
    for jogador in jogadores:
        selecionado = st.session_state.selecionado_id == jogador["numero"]
        label = f"{jogador['numero']} · {short_name(jogador['nome'])}"
        if jogador["gr"]:
            label += " 🧤"
        if selecionado:
            label = f"✅ {label}"

        st.markdown("<div class='player-btn'>", unsafe_allow_html=True)
        if st.button(
            label,
            key=f"{prefix}_{jogador['numero']}",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.selecionado_id = jogador["numero"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


with left:
    st.markdown("### Atletas")
    if campo:
        st.markdown("#### Campo")
        render_grid(campo, "campo")
    if grs:
        st.markdown("#### GR")
        render_grid(grs, "gr")

with right:
    st.markdown("### Ações")
    selecionado = get_player_by_num(st.session_state.selecionado_id)

    if selecionado:
        st.markdown(
            f"""
            <div class="section-box">
                <h3 style="margin:0;">
                    Camisola {selecionado['numero']} · {selecionado['nome']}
                    {" · GR" if selecionado['gr'] else ""}
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        eventos = EVENTOS_GR if selecionado["gr"] else EVENTOS_JOGADOR
        for evento in eventos:
            st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
            if st.button(
                evento,
                key=f"evento_{selecionado['numero']}_{evento}",
                use_container_width=True
            ):
                registar_evento(selecionado["numero"], evento)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Seleciona um atleta.")

# =========================
# FECHO
# =========================
st.divider()
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

st.session_state.observacoes = st.text_area(
    "Observações finais",
    value=st.session_state.observacoes
)

# =========================
# RESUMO
# =========================
st.divider()
st.markdown("### Resumo estatístico")
st.dataframe(dataframe_resumo(), use_container_width=True, hide_index=True)

if not dataframe_eventos().empty:
    with st.expander("Ver últimas ações"):
        st.dataframe(
            dataframe_eventos().tail(20).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

st.download_button(
    "Exportar Excel do jogo",
    data=exportar_excel_bytes("Final"),
    file_name=f"defera_stats_{st.session_state.equipa}_{st.session_state.adversario}.xlsx".replace(" ", "_"),
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)
