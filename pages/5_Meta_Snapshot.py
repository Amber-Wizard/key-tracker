
import streamlit as st
import pandas as pd

import database
import dok_api
import graphing
from Home import default_settings

try:
    st.set_page_config(
        page_title="Player Page - KeyTracker",
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
.pilot-font {
    font-size: 28px !important;
    color: #6d3fc0 !important;
}
.game-data-font {
    font-size: 28px !important;
    color: #424242 !important;
}
.plain-font {
    font-size: 26px !important;
}
.plain-italic-font {
    font-size: 26px !important;
    font-style: italic !important;  /* Make this font italic */
}
.hero-font {
    font-size: 26px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
}
.hero-italic-font {
    font-size: 26px !important;
    color: #60b4ff !important;
    font-style: italic !important;  /* Make this font italic */

}
.villain-italic-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
    font-style: italic !important;  /* Make this font italic */

}
.big-hero-font {
    font-size: 36px !important;
    color: #60b4ff !important;
}
.big-villain-font {
    font-size: 36px !important;
    color: #ff4b4b !important;
}
.small-hero-font {
    font-size: 20px !important;
    color: #60b4ff !important;
}
.small-villain-font {
    font-size: 20px !important;
    color: #ff4b4b !important;
}
.CotA-font {
    font-size: 28px !important;
    color: #d92b34 !important;
}
.AoA-font {
    font-size: 28px !important;
    color: #259adb !important;
}
.WC-font {
    font-size: 28px !important;
    color: #ad39a5 !important;
}
.MM-font {
    font-size: 28px !important;
    color: #e94e76 !important;
}
.DT-font {
    font-size: 28px !important;
    color: #136697 !important;
}
.WoE-font {
    font-size: 28px !important;
    color: #0c9aa8 !important;
}
.GR-font {
    font-size: 28px !important;
    color: #0c4f7f !important;
}
.VM23-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.VM24-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.amber-font {
    font-size: 22px !important;
    color: #f8df65 !important;
}
</style>
""", unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_meta_games():
    with st.spinner('Getting games...'):
        recent_games = database.get_all_recent_games()
        recent_games = recent_games[recent_games['Opponent Deck'] != '---']
        st.session_state.recent_games = recent_games


def process_meta_games():
    with st.spinner('Processing games...'):
        st.session_state.meta_snapshot = {}

        recent_games = st.session_state.recent_games
        games_played = len(recent_games)

        # Games Logged
        games_played_day = recent_games['Date'].dt.date.value_counts().sort_index()
        games_played_day = games_played_day.reset_index()
        games_played_day.columns = ['Date', 'Games']

        # Get Dok Data
        dok_data_dict = {}
        set_data_dict = {k: 0 for k in [ls[0] for ls in database.set_conversion_dict.values()]}
        set_win_dict = {k: 0 for k in [ls[0] for ls in database.set_conversion_dict.values()]}
        house_data_dict = {k.title() if k != 'staralliance' else 'StarAlliance': 0 for k in graphing.house_colors.keys()}
        house_win_dict = {k.title() if k != 'staralliance' else 'StarAlliance': 0 for k in graphing.house_colors.keys()}
        cards_played_dict = {}
        card_win_dict = {}

        for idx, row in recent_games.iterrows():
            game_log = row['Game Log'][0]
            opponent_data = game_log[row['Opponent'][0]]
            player_data = game_log[row['Player'][0]]
            opponent_won = False
            if row['Winner'][0] == row['Opponent'][0]:
                opponent_won = True

            # Calculated Cards Played
            opponent_cards_played = opponent_data['individual_cards_played']
            if opponent_cards_played:
                for card in opponent_cards_played[-1].keys():
                    if card in cards_played_dict:
                        cards_played_dict[card] += 1
                    else:
                        cards_played_dict[card] = 1
                    if opponent_won:
                        if card in card_win_dict:
                            card_win_dict[card] += 1
                        else:
                            card_win_dict[card] = 1

            player_cards_played = player_data['individual_cards_played']
            if player_cards_played:
                for card in player_cards_played[-1].keys():
                    if card in cards_played_dict:
                        cards_played_dict[card] += 1
                    else:
                        cards_played_dict[card] = 1
                    if not opponent_won:
                        if card in card_win_dict:
                            card_win_dict[card] += 1
                        else:
                            card_win_dict[card] = 1

            for i, deck_id in enumerate([row['Opponent Deck Link'][0].split('/')[-1], row['Deck Link'][0].split('/')[-1]]):
                if deck_id and deck_id not in dok_data_dict:
                    dok_data = database.get_dok_cache_deck_id(deck_id)
                    if dok_data:
                        dok_data_dict[deck_id] = dok_data
                elif deck_id:
                    dok_data = dok_data_dict[deck_id]

                if dok_data:
                    # Calculate Sets Played
                    expansion = dok_data['Data']['deck']['expansion']
                    converted_expansion = database.set_conversion_dict[expansion][0]
                    if converted_expansion in set_data_dict:
                        set_data_dict[converted_expansion] += 1
                    else:
                        set_data_dict[converted_expansion] = 1
                    if opponent_won and i == 0 or not opponent_won and i == 1:
                        converted_expansion = database.set_conversion_dict[expansion][0]
                        if converted_expansion in set_win_dict:
                            set_win_dict[converted_expansion] += 1
                        else:
                            set_win_dict[converted_expansion] = 1

                    # Calculate Houses Played
                    houses_and_cards = dok_data['Data']['deck']['housesAndCards']
                    for h in houses_and_cards:
                        house = h['house']
                        if house in house_data_dict:
                            house_data_dict[house] += 1
                        else:
                            house_data_dict[house] = 1
                        if opponent_won and i == 0 or not opponent_won and i == 1:
                            if house in house_win_dict:
                                house_win_dict[house] += 1
                            else:
                                house_win_dict[house] = 1

        cards_played_df = pd.DataFrame(list(cards_played_dict.items()), columns=['Card', 'Played'])
        cards_played_df = cards_played_df.sort_values(by='Played', ascending=False)

        st.session_state.meta_snapshot['games_played_day'] = games_played_day
        st.session_state.meta_snapshot['games_played'] = games_played
        st.session_state.meta_snapshot['set_data_dict'] = set_data_dict
        st.session_state.meta_snapshot['set_win_dict'] = set_win_dict
        st.session_state.meta_snapshot['house_data_dict'] = house_data_dict
        st.session_state.meta_snapshot['house_win_dict'] = house_win_dict
        st.session_state.meta_snapshot['cards_played_df'] = cards_played_df
        st.session_state.meta_snapshot['card_win_dict'] = card_win_dict

if 'recent_games' not in st.session_state:
    get_meta_games()

if 'meta_snapshot' not in st.session_state:
    process_meta_games()

games_played_day = st.session_state.meta_snapshot['games_played_day']
games_played = st.session_state.meta_snapshot['games_played']
set_data_dict = st.session_state.meta_snapshot['set_data_dict']
set_win_dict = st.session_state.meta_snapshot['set_win_dict']
house_data_dict = st.session_state.meta_snapshot['house_data_dict']
house_win_dict = st.session_state.meta_snapshot['house_win_dict']
cards_played_df = st.session_state.meta_snapshot['cards_played_df']
card_win_dict = st.session_state.meta_snapshot['card_win_dict']


c1, c2, c3, c4 = st.columns([22, 1, 1, 1], vertical_alignment='bottom')
c1.title('Meta Snapshot')

refresh_data = c2.button("⟳")

home = c3.button("🏠")
if home:
    st.switch_page("Home.py")

if refresh_data:
    get_meta_games()
    process_meta_games()

st.write('')

activity_graph = graphing.activity_graph(games_played_day)

st.subheader('Games Logged')
with st.container(border=True):
    st.plotly_chart(activity_graph, use_container_width=True)

# Make Set Graph
set_graph_dict = {k: round((100 * v / games_played) / 2) for k, v in set_data_dict.items()}
set_graph = graphing.set_meta_graph(set_graph_dict)

st.subheader('Sets Played')
with st.container(border=True):
    st.plotly_chart(set_graph, use_container_width=True)

st.subheader('Set Winrates')
with st.container(border=True):
    cols = st.columns(len(set_data_dict))
    for i, h in enumerate(set_data_dict.keys()):
        cols[i].markdown(f'<b class="plain-font">  {h}</b>', unsafe_allow_html=True)
        if set_data_dict[h] != 0:
            winrate = round(100 * set_win_dict[h] / set_data_dict[h])
        else:
            winrate = 0

        if winrate >= 50:
            cols[i].markdown(f'<b class="hero-italic-font">  {winrate}%</b>', unsafe_allow_html=True)
        else:
            cols[i].markdown(f'<b class="villain-italic-font">  {winrate}%</b>', unsafe_allow_html=True)

# Make House Graph
house_graph_dict = {k: round((100 * v / games_played) / 2) for k, v in house_data_dict.items()}
house_graph = graphing.house_meta_graph(house_graph_dict)

st.subheader('Houses Played')
with st.container(border=True):
    st.plotly_chart(house_graph, use_container_width=True)

st.subheader('House Winrates')
with st.container(border=True):
    cols = st.columns(len(house_data_dict))
    for i, h in enumerate(house_data_dict.keys()):
        cols[i].image(graphing.house_dict[h]['Image'])
        if house_data_dict[h] != 0:
            winrate = round(100 * house_win_dict[h] / house_data_dict[h])
        else:
            winrate = 0
        if winrate >= 50:
            cols[i].markdown(f'<b class="hero-italic-font"> {winrate}%</b>', unsafe_allow_html=True)
        else:
            cols[i].markdown(f'<b class="villain-italic-font"> {winrate}%</b>', unsafe_allow_html=True)

st.subheader('Cards Played')
with st.container(border=True):
    trimmed_card_df = cards_played_df.head(20)

    card_cols = st.columns(10)
    for j, (idx, row) in enumerate(trimmed_card_df.iterrows()):
        i = j
        if j > 9:
            i = j-10

        card_cols[i].image(dok_api.card_image_dict[row['Card']])

        frequency = round((100 * row['Played'] / games_played) / 2)
        if frequency == 100:
            frequency_string = f"  {frequency}%"
        elif frequency < 10:
            frequency_string = f"    {frequency}%"
        else:
            frequency_string = f"   {frequency}%"
        card_cols[i].markdown(f'<b class="plain-italic-font">{frequency_string}</b>', unsafe_allow_html=True)

        winrate = round(100 * card_win_dict[row['Card']] / row['Played'])
        if winrate == 100:
            winrate_string = f"  {winrate}%"
        elif winrate < 10:
            winrate_string = f"    {winrate}%"
        else:
            winrate_string = f"   {winrate}%"
        if winrate >= 50:
            card_cols[i].markdown(f'<b class="hero-italic-font">{winrate_string}</b>', unsafe_allow_html=True)
        else:
            card_cols[i].markdown(f'<b class="villain-italic-font">{winrate_string}</b>', unsafe_allow_html=True)









