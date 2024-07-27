import streamlit as st

import database
import graphing

try:
    st.set_page_config(
        page_title="Analysis - KeyTracker",
        page_icon="🔑",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except:
    pass

st.markdown("""
<style>
.deck-font {
    font-size: 32px !important;
}
.game-data-font {
    font-size: 28px !important;
    color: #424242 !important;
}
.hero-font {
    font-size: 24px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 24px !important;
    color: #ff4b4b !important;
}
</style>
""", unsafe_allow_html=True)

game_id = None
if 'game' in st.query_params:
    game_id = st.query_params.get_all(key='game')[0]


if 'game_id' in st.session_state:
    game_id = st.session_state.game_id
    st.query_params['game'] = game_id


def pull_game_data(gid):
    st.session_state.game_data = database.pull_game(gid)

if game_id:
    pull_game_data(game_id)

if 'game_data' not in st.session_state:
    st.error("No game selected")
else:
    c1, c2 = st.columns([7, 1])
    c1.markdown(f'<b class="deck-font">{st.session_state.game_data["Deck"]}</b>', unsafe_allow_html=True)
    c2.link_button("Deck Info", st.session_state.game_data["Deck Link"])
    st.write('vs')
    c1, c2 = st.columns([7, 1])
    c1.markdown(f'<b class="deck-font">{st.session_state.game_data["Opponent Deck"]}</b>', unsafe_allow_html=True)
    c2.link_button("Deck Info", st.session_state.game_data["Opponent Deck Link"])
    st.markdown(f'<b class="game-data-font">{st.session_state.game_data["Date"]}</b>', unsafe_allow_html=True)
    st.divider()
    c1, c2, c3 = st.columns(3)

    c1.subheader("Opponent")
    c2.subheader("First Player")
    c3.subheader("Winner")
    opponent = st.session_state.game_data['Opponent']
    starting_player = st.session_state.game_data['Starting Player']
    winner = st.session_state.game_data['Winner']
    username = st.session_state.name
    c1.markdown(f'<b class="villain-font">{opponent}</b>', unsafe_allow_html=True)
    if starting_player == username:
        c2.markdown(f'<b class="hero-font">{starting_player}</b>', unsafe_allow_html=True)
    else:
        c2.markdown(f'<b class="villain-font">{starting_player}</b>', unsafe_allow_html=True)
    if winner == username:
        c3.markdown(f'<b class="hero-font">{winner}</b>', unsafe_allow_html=True)
    else:
        c3.markdown(f'<b class="villain-font">{winner}</b>', unsafe_allow_html=True)
    st.write(' ')
    st.write(' ')
    st.write(' ')

    game_df, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, player_card_data, opponent_card_data = graphing.analyze_game(st.session_state.name, st.session_state.game_data)
    c1, c2 = st.columns(2)
    c1.subheader("Total Amber Value")
    c1.line_chart(
        game_df,
        x=None,
        y=['Player Amber', 'Opponent Amber'],
        x_label='Turn',
        y_label='Amber Value',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Total Cards Played")
    c2.line_chart(
        game_df,
        x=None,
        y=['Player Cards', 'Opponent Cards'],
        x_label='Turn',
        y_label='Cards Played',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Prediction")
    c1.line_chart(
        game_df,
        x=None,
        y=['Player Prediction', 'Opponent Prediction'],
        x_label='Turn',
        y_label='Turns to Win',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Creatures")
    c2.line_chart(
        game_df,
        x=None,
        y=['Player Creatures', 'Opponent Creatures'],
        x_label='Turn',
        y_label='Creatures',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Amber Delta")
    c1.line_chart(
        game_df,
        x=None,
        y=['Player Delta', 'Opponent Delta'],
        x_label='Turn',
        y_label='Delta',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Reap Rate")
    c2.line_chart(
        game_df,
        x=None,
        y=['Player Reap Rate', 'Opponent Reap Rate'],
        x_label='Turn',
        y_label='Reap Rate',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Player Amber Sources")
    c1.plotly_chart(player_amber_sources, use_container_width=True)
    c2.subheader("Opponent Amber Sources")
    c2.plotly_chart(opponent_amber_sources, use_container_width=True)

    c1.subheader("Player House Calls")
    c1.plotly_chart(player_house_calls, use_container_width=True)
    c2.subheader("Opponent House Calls")
    c2.plotly_chart(opponent_house_calls, use_container_width=True)

    st.subheader("Card Data")
    with st.expander("Player Card Data"):
        st.dataframe(player_card_data, hide_index=True)

    with st.expander("Opponent Card Data"):
        st.dataframe(opponent_card_data, hide_index=True)


