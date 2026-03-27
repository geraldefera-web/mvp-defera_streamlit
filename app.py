import io
from datetime import date, datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="DEFERA Stats Live | CD Xico Andebol",
    page_icon="🤾",
    layout="wide",
)

# ======================================================================
# CONFIGURAÇÃO BASE
# Substituir estes nomes pelos plantéis reais do CD Xico Andebol.
# ======================================================================
SENIOR_ROSTER = [
    "Atleta Sénior 1", "Atleta Sénior 2", "Atleta Sénior 3", "Atleta Sénior 4",
    "Atleta Sénior 5", "Atleta Sénior 6", "Atleta Sénior 7", "Atleta Sénior 8",
    "Atleta Sénior 9", "Atleta Sénior 10", "Atleta Sénior 11", "Atleta Sénior 12",
    "Atleta Sénior 13", "Atleta Sénior 14", "GR Sénior 1", "GR Sénior 2",
]

SUB14_ROSTER = [
    "Atleta Sub14 1", "Atleta Sub14 2", "Atleta Sub14 3", "Atleta Sub14 4",
    "Atleta Sub14 5", "Atleta Sub14 6", "Atleta Sub14 7", "Atleta Sub14 8",
    "Atleta Sub14 9", "Atleta Sub14 10", "Atleta Sub14 11", "Atleta Sub14 12",
    "Atleta Sub14 13", "Atleta Sub14 14", "GR Sub14 1", "GR Sub14 2",
]

ROSTERS = {
    "Sénior": SENIOR_ROSTER,
    "Sub-14": SUB14_ROSTER,
}

EVENT_LABELS = {
    "golos": "Golo",
    "assistencias": "Assistência",
    "remates_falhados": "Remate falhado",
    "perdas_bola": "Perda de bola",
    "recuperacoes_bola": "Recuperação de bola",
    "exclusoes_2min": "Exclusão 2 min",
    "amarelos": "Cartão amarelo",
    "vermelhos": "Cartão vermelho",
    "defesas_gr": "Defesa GR",
}

EVENT_ORDER = list(EVENT_LABELS.keys())

CSS = """
<style>
    .main-header {
        background: linear-gradient(135deg, #111827, #1f2937);
        color: white;
        padding: 1.2rem 1.4rem;
        border-radius: 16px;
        margin-bottom: 1rem;
    }
    .section-box {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
        background: #ffffff;
    }
    .small-note {
        color: #6b7280;
        font-size: 0.9rem;
    }
    .athlete-card {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.8rem;
        background: #fafafa;
    }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    defaults = {
        "match_started": False,
        "current_half": None,
        "halves_started": {"1.ª Parte": False, "2.ª Parte": False},
        "halves_ended": {"1.ª Parte": False, "2.ª Parte": False},
        "match_meta": {},
        "squad_selected": [],
        "goalkeepers_selected": [],
        "stats": {},
        "events": [],
        "result_home": None,
        "result_away": None,
        "halftime_home": None,
        "halftime_away": None,
        "notes": "",
        "setup_complete": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def build_empty_stats(players):
    return {
        player: {
            "1.ª Parte": {event: 0 for event in EVENT_ORDER},
            "2.ª Parte": {event: 0 for event in EVENT_ORDER},
        }
        for player in players
    }


def reset_match():
    for key in [
        "match_started", "current_half", "halves_started", "halves_ended",
        "match_meta", "squad_selected", "goalkeepers_selected", "stats",
        "events", "result_home", "result_away", "halftime_home", "halftime_away",
        "notes", "setup_complete"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


def configure_match(team, opponent, competition, match_date, venue, selected_players, selected_gks):
    st.session_state.match_meta = {
        "equipa": team,
        "adversario": opponent.strip(),
        "competicao": competition.strip(),
        "data": match_date.strftime("%d/%m/%Y"),
        "local": venue.strip(),
    }
    st.session_state.squad_selected = selected_players
    st.session_state.goalkeepers_selected = selected_gks
    st.session_state.stats = build_empty_stats(selected_players)
    st.session_state.events = []
    st.session_state.result_home = None
    st.session_state.result_away = None
    st.session_state.halftime_home = None
    st.session_state.halftime_away = None
    st.session_state.notes = ""
    st.session_state.match_started = False
    st.session_state.current_half = None
    st.session_state.halves_started = {"1.ª Parte": False, "2.ª Parte": False}
    st.session_state.halves_ended = {"1.ª Parte": False, "2.ª Parte": False}
    st.session_state.setup_complete = True


def can_start_half(half):
    if not st.session_state.setup_complete:
        return False
    if half == "1.ª Parte":
        return not st.session_state.halves_started["1.ª Parte"]
    return (
        st.session_state.halves_ended["1.ª Parte"]
        and not st.session_state.halves_started["2.ª Parte"]
    )


def start_half(half):
    if not can_start_half(half):
        return
    st.session_state.match_started = True
    st.session_state.current_half = half
    st.session_state.halves_started[half] = True


def end_current_half():
    half = st.session_state.current_half
    if half is None:
        return
    st.session_state.halves_ended[half] = True
    st.session_state.current_half = None


def add_event(player, event_key):
    half = st.session_state.current_half
    if not half or player not in st.session_state.stats:
        return
    st.session_state.stats[player][half][event_key] += 1
    st.session_state.events.append({
        "timestamp_registo": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "parte": half,
        "atleta": player,
        "evento": EVENT_LABELS[event_key],
        "evento_chave": event_key,
        "quantidade": 1,
    })


def undo_last_event():
    if not st.session_state.events:
        return
    last = st.session_state.events.pop()
    player = last["atleta"]
    half = last["parte"]
    event_key = last["evento_chave"]
    if (
        player in st.session_state.stats
        and half in st.session_state.stats[player]
        and st.session_state.stats[player][half][event_key] > 0
    ):
        st.session_state.stats[player][half][event_key] -= 1


def build_player_summary_df():
    rows = []
    for player, half_data in st.session_state.stats.items():
        for half, metrics in half_data.items():
            row = {"Atleta": player, "Parte": half}
            for key in EVENT_ORDER:
                row[EVENT_LABELS[key]] = metrics[key]
            rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    total_rows = []
    for player, group in df.groupby("Atleta"):
        total = {"Atleta": player, "Parte": "Total"}
        for key in EVENT_ORDER:
            label = EVENT_LABELS[key]
            total[label] = int(group[label].sum())
        total_rows.append(total)

    total_df = pd.DataFrame(total_rows)
    full_df = pd.concat([df, total_df], ignore_index=True)
    return full_df


def build_team_summary_df():
    player_df = build_player_summary_df()
    if player_df.empty:
        return pd.DataFrame()

    metric_cols = [EVENT_LABELS[key] for key in EVENT_ORDER]
    base = player_df[player_df["Parte"].isin(["1.ª Parte", "2.ª Parte"])].copy()
    team_half = base.groupby("Parte", as_index=False)[metric_cols].sum()
    team_half.insert(0, "Âmbito", "Equipa")

    total = pd.DataFrame([{
        "Âmbito": "Equipa",
        "Parte": "Total",
        **{col: int(team_half[col].sum()) for col in metric_cols}
    }])

    return pd.concat([team_half, total], ignore_index=True)


def build_events_df():
    if not st.session_state.events:
        return pd.DataFrame(columns=["timestamp_registo", "parte", "atleta", "evento", "quantidade"])
    return pd.DataFrame(st.session_state.events)[["timestamp_registo", "parte", "atleta", "evento", "quantidade"]]


def build_match_sheet_df():
    meta = st.session_state.match_meta
    return pd.DataFrame([{
        "Equipa": meta.get("equipa", ""),
        "Adversário": meta.get("adversario", ""),
        "Competição": meta.get("competicao", ""),
        "Data": meta.get("data", ""),
        "Local": meta.get("local", ""),
        "Convocados": ", ".join(st.session_state.squad_selected),
        "Guarda-redes": ", ".join(st.session_state.goalkeepers_selected),
        "Resultado CD Xico": st.session_state.result_home if st.session_state.result_home is not None else "",
        "Resultado Adversário": st.session_state.result_away if st.session_state.result_away is not None else "",
        "Resultado Intervalo CD Xico": st.session_state.halftime_home if st.session_state.halftime_home is not None else "",
        "Resultado Intervalo Adversário": st.session_state.halftime_away if st.session_state.halftime_away is not None else "",
        "Observações": st.session_state.notes,
    }])


def export_excel():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        build_match_sheet_df().to_excel(writer, sheet_name="Ficha do Jogo", index=False)
        build_events_df().to_excel(writer, sheet_name="Log de Eventos", index=False)
        build_player_summary_df().to_excel(writer, sheet_name="Resumo por Atleta", index=False)
        build_team_summary_df().to_excel(writer, sheet_name="Resumo Global", index=False)
    output.seek(0)
    return output


def export_summary_txt():
    meta = st.session_state.match_meta
    team_df = build_team_summary_df()
    player_df = build_player_summary_df()

    lines = [
        "DEFERA Stats Live | Resumo do Jogo",
        f"Equipa: {meta.get('equipa', '')}",
        f"Adversário: {meta.get('adversario', '')}",
        f"Competição: {meta.get('competicao', '')}",
        f"Data: {meta.get('data', '')}",
        f"Local: {meta.get('local', '')}",
        f"Resultado Final: {st.session_state.result_home} - {st.session_state.result_away}",
    ]

    if st.session_state.halftime_home is not None and st.session_state.halftime_away is not None:
        lines.append(
            f"Resultado ao Intervalo: {st.session_state.halftime_home} - {st.session_state.halftime_away}"
        )

    lines.append("")
    lines.append("Resumo Global:")
    if not team_df.empty:
        lines.append(team_df.to_string(index=False))
    else:
        lines.append("Sem dados.")

    lines.append("")
    lines.append("Resumo por Atleta:")
    total_players = player_df[player_df["Parte"] == "Total"].copy()
    if not total_players.empty:
        lines.append(total_players.to_string(index=False))
    else:
        lines.append("Sem dados.")

    if st.session_state.notes:
        lines.append("")
        lines.append("Observações:")
        lines.append(st.session_state.notes)

    return "\n".join(lines).encode("utf-8")


init_state()

# ======================================================================
# HEADER
# ======================================================================
st.markdown(
    """
    <div class="main-header">
        <h2 style="margin:0;">DEFERA Stats Live</h2>
        <div style="margin-top:0.35rem;">App MVP de registo estatístico em direto para andebol | CD Xico Andebol</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Controlo")
    if st.button("Novo jogo / Reset total", use_container_width=True):
        reset_match()
        st.rerun()

    st.markdown("---")
    meta = st.session_state.match_meta
    if meta:
        st.markdown("**Jogo atual**")
        st.write(f"**Equipa:** {meta.get('equipa', '-')}")
        st.write(f"**Adversário:** {meta.get('adversario', '-')}")
        st.write(f"**Competição:** {meta.get('competicao', '-')}")
        st.write(f"**Parte ativa:** {st.session_state.current_half or 'Nenhuma'}")
    else:
        st.caption("Sem jogo configurado.")

tab_setup, tab_live, tab_summary, tab_export = st.tabs(
    ["1. Configuração do Jogo", "2. Registo Live", "3. Resumo", "4. Exportação"]
)

# ======================================================================
# CONFIGURAÇÃO
# ======================================================================
with tab_setup:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Configurar jogo")

    with st.form("setup_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_team = st.selectbox("Equipa", options=list(ROSTERS.keys()))
        with col2:
            opponent = st.text_input("Adversário")
        with col3:
            competition = st.text_input("Competição")

        col4, col5 = st.columns(2)
        with col4:
            match_date = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        with col5:
            venue = st.text_input("Local")

        roster = ROSTERS[selected_team]
        selected_players = st.multiselect(
            "Convocados",
            options=roster,
            default=roster[:14] if len(roster) >= 14 else roster,
            help="Seleciona os atletas presentes no jogo.",
        )
        selected_gks = st.multiselect(
            "Guarda-redes convocados",
            options=selected_players,
            default=[p for p in selected_players if "GR" in p][:2],
        )

        submitted = st.form_submit_button("Guardar configuração do jogo", use_container_width=True)

        if submitted:
            errors = []
            if not opponent.strip():
                errors.append("Indica o adversário.")
            if not competition.strip():
                errors.append("Indica a competição.")
            if not venue.strip():
                errors.append("Indica o local.")
            if not selected_players:
                errors.append("Seleciona pelo menos um convocado.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                configure_match(
                    selected_team,
                    opponent,
                    competition,
                    match_date,
                    venue,
                    selected_players,
                    selected_gks,
                )
                st.success("Jogo configurado com sucesso.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.setup_complete:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Ficha atual")
        st.dataframe(build_match_sheet_df(), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ======================================================================
# REGISTO LIVE
# ======================================================================
with tab_live:
    if not st.session_state.setup_complete:
        st.info("Primeiro configura o jogo no separador anterior.")
    else:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Controlo das partes")
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            if st.button("Iniciar 1.ª Parte", use_container_width=True, disabled=not can_start_half("1.ª Parte")):
                start_half("1.ª Parte")
                st.rerun()

        with c2:
            if st.button(
                "Terminar Parte Ativa",
                use_container_width=True,
                disabled=st.session_state.current_half is None,
            ):
                end_current_half()
                st.rerun()

        with c3:
            if st.button("Iniciar 2.ª Parte", use_container_width=True, disabled=not can_start_half("2.ª Parte")):
                start_half("2.ª Parte")
                st.rerun()

        with c4:
            if st.button("Anular última ação", use_container_width=True, disabled=not st.session_state.events):
                undo_last_event()
                st.rerun()

        with c5:
            if st.button("Fechar jogo", use_container_width=True, disabled=not st.session_state.halves_ended["2.ª Parte"]):
                st.session_state.current_half = None
                st.rerun()

        current_half = st.session_state.current_half or "Nenhuma"
        st.caption(f"Parte ativa: {current_half}")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.current_half is None:
            st.warning("Inicia uma parte para começares o registo live.")
        else:
            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            st.subheader(f"Registo live | {st.session_state.current_half}")

            num_cols = 2 if len(st.session_state.squad_selected) > 10 else 1
            cols = st.columns(num_cols)

            for idx, player in enumerate(st.session_state.squad_selected):
                target_col = cols[idx % num_cols]
                with target_col:
                    st.markdown('<div class="athlete-card">', unsafe_allow_html=True)
                    st.markdown(f"**{player}**")
                    player_stats = st.session_state.stats[player][st.session_state.current_half]
                    stat_line = " | ".join(
                        [f"{EVENT_LABELS[k]}: {player_stats[k]}" for k in EVENT_ORDER]
                    )
                    st.markdown(f'<div class="small-note">{stat_line}</div>', unsafe_allow_html=True)

                    action_cols = st.columns(3)
                    buttons = [
                        ("golos", "➕ Golo"),
                        ("assistencias", "➕ Assist."),
                        ("remates_falhados", "➕ Rem. falhado"),
                        ("perdas_bola", "➕ Perda"),
                        ("recuperacoes_bola", "➕ Recuperação"),
                        ("exclusoes_2min", "➕ 2 min"),
                        ("amarelos", "➕ Amarelo"),
                        ("vermelhos", "➕ Vermelho"),
                        ("defesas_gr", "➕ Defesa GR"),
                    ]

                    for b_idx, (event_key, label) in enumerate(buttons):
                        with action_cols[b_idx % 3]:
                            if st.button(label, key=f"{player}_{st.session_state.current_half}_{event_key}", use_container_width=True):
                                add_event(player, event_key)
                                st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Últimas ações")
        events_df = build_events_df()
        if events_df.empty:
            st.caption("Ainda não existem ações registadas.")
        else:
            st.dataframe(events_df.tail(15).iloc[::-1], use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.halves_ended["2.ª Parte"]:
            st.markdown('<div class="section-box">', unsafe_allow_html=True)
            st.subheader("Fecho do jogo")
            with st.form("close_match_form", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1:
                    result_home = st.number_input("Resultado final CD Xico", min_value=0, step=1, value=0 if st.session_state.result_home is None else st.session_state.result_home)
                with c2:
                    result_away = st.number_input("Resultado final adversário", min_value=0, step=1, value=0 if st.session_state.result_away is None else st.session_state.result_away)

                c3, c4 = st.columns(2)
                with c3:
                    halftime_home = st.number_input("Resultado ao intervalo CD Xico", min_value=0, step=1, value=0 if st.session_state.halftime_home is None else st.session_state.halftime_home)
                with c4:
                    halftime_away = st.number_input("Resultado ao intervalo adversário", min_value=0, step=1, value=0 if st.session_state.halftime_away is None else st.session_state.halftime_away)

                notes = st.text_area("Observações finais", value=st.session_state.notes, height=100)
                close_submitted = st.form_submit_button("Guardar dados finais do jogo", use_container_width=True)

                if close_submitted:
                    st.session_state.result_home = int(result_home)
                    st.session_state.result_away = int(result_away)
                    st.session_state.halftime_home = int(halftime_home)
                    st.session_state.halftime_away = int(halftime_away)
                    st.session_state.notes = notes
                    st.success("Dados finais guardados com sucesso.")
            st.markdown("</div>", unsafe_allow_html=True)

# ======================================================================
# RESUMO
# ======================================================================
with tab_summary:
    if not st.session_state.setup_complete:
        st.info("Primeiro configura o jogo.")
    else:
        meta = st.session_state.match_meta
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Equipa", meta.get("equipa", "-"))
        with c2:
            st.metric("Adversário", meta.get("adversario", "-"))
        with c3:
            st.metric("Competição", meta.get("competicao", "-"))
        with c4:
            score = "-"
            if st.session_state.result_home is not None and st.session_state.result_away is not None:
                score = f"{st.session_state.result_home} - {st.session_state.result_away}"
            st.metric("Resultado Final", score)

        player_df = build_player_summary_df()
        team_df = build_team_summary_df()

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Resumo por atleta")
        if player_df.empty:
            st.caption("Sem dados para apresentar.")
        else:
            view_option = st.radio(
                "Visualização",
                options=["Totais", "Por parte"],
                horizontal=True,
                key="summary_view_option",
            )
            if view_option == "Totais":
                display_df = player_df[player_df["Parte"] == "Total"].copy()
            else:
                display_df = player_df[player_df["Parte"].isin(["1.ª Parte", "2.ª Parte"])].copy()

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            ranking_metric_label = st.selectbox(
                "Ranking rápido por métrica",
                options=[EVENT_LABELS[k] for k in EVENT_ORDER],
                index=0,
            )
            ranking_df = player_df[player_df["Parte"] == "Total"][["Atleta", ranking_metric_label]].sort_values(
                by=ranking_metric_label, ascending=False
            )
            st.bar_chart(ranking_df.set_index("Atleta"))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Resumo global")
        if team_df.empty:
            st.caption("Sem dados para apresentar.")
        else:
            st.dataframe(team_df, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Log completo de eventos")
        st.dataframe(build_events_df(), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================================
# EXPORTAÇÃO
# ======================================================================
with tab_export:
    if not st.session_state.setup_complete:
        st.info("Primeiro configura o jogo.")
    else:
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Exportar jogo")

        missing_final_data = st.session_state.result_home is None or st.session_state.result_away is None
        if missing_final_data:
            st.warning("Para exportar, deves primeiro guardar o resultado final no separador de registo live.")

        excel_data = export_excel()
        txt_data = export_summary_txt()

        file_stub = f"{st.session_state.match_meta.get('equipa', 'equipa')}_{st.session_state.match_meta.get('adversario', 'adversario')}_{datetime.now().strftime('%Y%m%d_%H%M')}"

        st.download_button(
            label="Descarregar Excel do jogo",
            data=excel_data,
            file_name=f"{file_stub}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            disabled=missing_final_data,
        )

        st.download_button(
            label="Descarregar resumo TXT",
            data=txt_data,
            file_name=f"{file_stub}_resumo.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=missing_final_data,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.subheader("Notas de utilização")
        st.markdown(
            """
            - Esta versão foi pensada como MVP para teste com o CD Xico Andebol.
            - Os plantéis estão definidos no próprio código e devem ser substituídos pelos nomes reais.
            - O registo é feito por parte do jogo, sem minuto exato por ação.
            - A exportação gera um ficheiro Excel com a ficha do jogo, log de eventos e resumos estatísticos.
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)
