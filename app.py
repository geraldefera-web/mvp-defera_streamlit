import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# -------------------------
# PLANTÉIS
# -------------------------

plantel_senior = [
    "Nuno Pinheiro","Armando Araujo","João Leite","César Gonçalves",
    "Roberto Ferreira","Pedro Freitas","Gabriel Guimarães","Raphael Neto",
    "José Magalhães","José Martins (GR)","João Martins","André Silva",
    "Leonardo Pereira (GR)","Alexandr Tchikoulaev","José Araújo","Diogo Martins"
]

plantel_sub14 = [
    "Fernando Abreu","David Ramalho","Duarte Silva","Francisco Fonseca",
    "Fábio Faria","João Edu Oliveira","José Lameiras","Lourenço Pinto",
    "Afonso Eusébio","Afonso Sousa","Alexandre Teixeira","Duarte Oliveira",
    "Gabriel Oliveira","Francisco Pedro","Francisco Soares","Tomás Marinho",
    "Francisco Costa","Pedro Martins","José Fernandes (GR)",
    "Diogo Sousa (GR)","Gabriel Silva","Rodrigo Castro",
    "Afonso Cunha (GR)","Salvador Correia","Rodrigo Sanchez"
]

# -------------------------
# SESSION STATE
# -------------------------

if "jogo_iniciado" not in st.session_state:
    st.session_state.jogo_iniciado = False
    st.session_state.parte = None
    st.session_state.eventos = []
    st.session_state.stats = {}
    st.session_state.atleta_atual = None
    st.session_state.ultimos = []

# -------------------------
# SETUP JOGO
# -------------------------

st.title("DEFERA Stats Live")

if not st.session_state.jogo_iniciado:

    equipa = st.selectbox("Equipa", ["Sénior","Sub-14"])
    adversario = st.text_input("Adversário")
    competicao = st.text_input("Competição")

    plantel = plantel_senior if equipa == "Sénior" else plantel_sub14

    convocados = st.multiselect("Convocados", plantel)

    if st.button("Iniciar Jogo"):
        st.session_state.jogo_iniciado = True
        st.session_state.equipa = equipa
        st.session_state.convocados = convocados
        st.session_state.parte = "1ª Parte"

        for jogador in convocados:
            st.session_state.stats[jogador] = {
                "golos":0,"assist":0,"remates":0,"perdas":0,
                "recuperacoes":0,"exclusoes":0,"amarelos":0,
                "vermelhos":0,"defesas":0
            }

        st.session_state.atleta_atual = convocados[0] if convocados else None

    st.stop()

# -------------------------
# NAVEGAÇÃO ATLETA
# -------------------------

st.subheader(f"{st.session_state.parte}")

col1, col2, col3 = st.columns([1,2,1])

with col1:
    if st.button("⬅️"):
        idx = st.session_state.convocados.index(st.session_state.atleta_atual)
        st.session_state.atleta_atual = st.session_state.convocados[max(0, idx-1)]

with col3:
    if st.button("➡️"):
        idx = st.session_state.convocados.index(st.session_state.atleta_atual)
        st.session_state.atleta_atual = st.session_state.convocados[min(len(st.session_state.convocados)-1, idx+1)]

with col2:
    atleta = st.selectbox("Atleta", st.session_state.convocados, index=st.session_state.convocados.index(st.session_state.atleta_atual))
    st.session_state.atleta_atual = atleta

# -------------------------
# FUNÇÃO REGISTO
# -------------------------

def registar(evento):
    atleta = st.session_state.atleta_atual

    if evento == "golo":
        st.session_state.stats[atleta]["golos"] += 1
    elif evento == "assist":
        st.session_state.stats[atleta]["assist"] += 1
    elif evento == "remate":
        st.session_state.stats[atleta]["remates"] += 1
    elif evento == "perda":
        st.session_state.stats[atleta]["perdas"] += 1
    elif evento == "rec":
        st.session_state.stats[atleta]["recuperacoes"] += 1
    elif evento == "2min":
        st.session_state.stats[atleta]["exclusoes"] += 1
    elif evento == "am":
        st.session_state.stats[atleta]["amarelos"] += 1
    elif evento == "vm":
        st.session_state.stats[atleta]["vermelhos"] += 1
    elif evento == "def":
        st.session_state.stats[atleta]["defesas"] += 1

    st.session_state.ultimos.insert(0, atleta)
    st.session_state.ultimos = st.session_state.ultimos[:5]

# -------------------------
# BOTÕES RÁPIDOS
# -------------------------

st.markdown("### Ações")

colA, colB = st.columns(2)

with colA:
    st.button("⚽ Golo", on_click=registar, args=("golo",))
    st.button("🎯 Assistência", on_click=registar, args=("assist",))
    st.button("❌ Remate Falhado", on_click=registar, args=("remate",))
    st.button("🔴 Perda", on_click=registar, args=("perda",))

with colB:
    st.button("🟢 Recuperação", on_click=registar, args=("rec",))
    st.button("⏱ 2min", on_click=registar, args=("2min",))
    st.button("🟨 Amarelo", on_click=registar, args=("am",))
    st.button("🟥 Vermelho", on_click=registar, args=("vm",))

if "(GR)" in atleta:
    st.button("🧤 Defesa GR", on_click=registar, args=("def",))

# -------------------------
# ATALHOS RÁPIDOS
# -------------------------

if st.session_state.ultimos:
    st.markdown("### Atalhos")
    for nome in st.session_state.ultimos:
        if st.button(nome):
            st.session_state.atleta_atual = nome

# -------------------------
# TROCA DE PARTE
# -------------------------

if st.button("➡️ Ir para 2ª Parte"):
    st.session_state.parte = "2ª Parte"

# -------------------------
# RESUMO
# -------------------------

df = pd.DataFrame(st.session_state.stats).T
st.dataframe(df)

# -------------------------
# FINAL DO JOGO
# -------------------------

st.markdown("### Final do Jogo")

res_cdx = st.number_input("CD Xico", step=1)
res_adv = st.number_input("Adversário", step=1)

if st.button("Exportar Excel"):
    df.to_excel("jogo.xlsx")
    with open("jogo.xlsx","rb") as f:
        st.download_button("Download", f, file_name="jogo.xlsx")
        
        st.markdown("</div>", unsafe_allow_html=True)
