import streamlit as st
import pandas as pd

from collections import defaultdict

import database
import dok_api
import graphing
import formatting
import calcs

try:
    st.set_page_config(
        page_title="Meta Snapshot - KeyTracker",
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
.VM25-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.amber-font {
    font-size: 26px !important;
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
        recent_games = database.get_all_recent_games(games=500)
        recent_games = recent_games[recent_games['Format'].apply(lambda x: 'Archon' in x)]
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
        set_win_dict = {k: {'wins': 0, 'losses': 0} for k in [ls[0] for ls in database.set_conversion_dict.values()]}
        set_key_diff_dict = {k: {'key_diff': 0, 'games': 0} for k in [ls[0] for ls in database.set_conversion_dict.values()]}
        set_vs_set_dict = {k: {ik: {'wins': 0, 'losses': 0} for ik in [ils[0] for ils in database.set_conversion_dict.values()] if ik != k} for k in [ls[0] for ls in database.set_conversion_dict.values()]}
        house_data_dict = {k.title() if k != 'staralliance' else 'StarAlliance': 0 for k in graphing.house_colors.keys()}
        house_win_dict = {k.title() if k != 'staralliance' else 'StarAlliance': 0 for k in graphing.house_colors.keys()}
        house_key_diff_dict = {k.title() if k != 'staralliance' else 'StarAlliance': {'key_diff': 0, 'games': 0} for k in graphing.house_colors.keys()}
        cards_played_dict = defaultdict(int)
        card_win_dict = defaultdict(int)
        copies_played_dict = defaultdict(int)
        amber_gained_dict = defaultdict(int)
        played_with_dict = defaultdict(lambda: defaultdict(int))
        played_with_win_dict = defaultdict(lambda: defaultdict(int))

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
                    cards_played_dict[card] += 1
                    copies_played_dict[card] += opponent_cards_played[-1][card]
                    if opponent_won:
                        card_win_dict[card] += 1
                        for c in opponent_cards_played[-1].keys():
                            if c != card:
                                played_with_win_dict[card][c] += 1

                    for c in opponent_cards_played[-1].keys():
                        if c != card:
                            played_with_dict[card][c] += 1

            player_cards_played = player_data['individual_cards_played']
            if player_cards_played:
                for card in player_cards_played[-1].keys():
                    cards_played_dict[card] += 1
                    copies_played_dict[card] += player_cards_played[-1][card]
                    if not opponent_won:
                        card_win_dict[card] += 1
                        for c in player_cards_played[-1].keys():
                            if c != card:
                                played_with_win_dict[card][c] += 1

                    for c in player_cards_played[-1].keys():
                        if c != card:
                            played_with_dict[card][c] += 1

            for amber_type in ['individual_amber_icons', 'individual_amber_reaped', 'individual_amber_effect', 'individual_steal']:
                opponent_card_amber = opponent_data[amber_type]
                if opponent_card_amber:
                    for card in opponent_card_amber[-1].keys():
                        amber_gained_dict[card] += opponent_card_amber[-1][card]

                player_card_amber = player_data[amber_type]
                if player_card_amber:
                    for card in player_card_amber[-1].keys():
                        amber_gained_dict[card] += player_card_amber[-1][card]

            player_set, opponent_set = None, None
            for i, deck_id in enumerate([row['Opponent Deck Link'][0].split('/')[-1], row['Deck Link'][0].split('/')[-1]]):
                game_log = row['Game Log'][0]
                opponent_data = game_log[row['Opponent'][0]]
                player_data = game_log[row['Player'][0]]
                try:
                    player_keys = player_data['keys'][-1]
                    opponent_keys = opponent_data['keys'][-1]
                except:
                    print(player_data)
                    print(opponent_data)
                    player_keys = None
                    opponent_keys = None

                dok_data = None
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
                    if i == 0:
                        opponent_set = converted_expansion
                    else:
                        player_set = converted_expansion
                    if converted_expansion in set_data_dict:
                        set_data_dict[converted_expansion] += 1
                    else:
                        set_data_dict[converted_expansion] = 1

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

                        if player_keys is not None and opponent_keys is not None:
                            house_key_diff_dict[house]['games'] += 1
                            house_key_diff_dict[house]['key_diff'] += opponent_keys - player_keys

            if player_set != opponent_set:
                if opponent_set:
                    result = 'wins' if opponent_won else 'losses'
                    set_win_dict.setdefault(opponent_set, {'wins': 0, 'losses': 0})[result] += 1
                    set_vs_set_dict[opponent_set].setdefault(player_set, {'wins': 0, 'losses': 0})[result] += 1
                    if player_keys is not None and opponent_keys is not None:
                        set_key_diff_dict[opponent_set]['games'] += 1
                        set_key_diff_dict[opponent_set]['key_diff'] += opponent_keys - player_keys

                if player_set:
                    result = 'losses' if opponent_won else 'wins'
                    set_win_dict.setdefault(player_set, {'wins': 0, 'losses': 0})[result] += 1
                    set_vs_set_dict[player_set].setdefault(opponent_set, {'wins': 0, 'losses': 0})[result] += 1
                    if player_keys is not None and opponent_keys is not None:
                        set_key_diff_dict[player_set]['games'] += 1
                        set_key_diff_dict[player_set]['key_diff'] += player_keys - opponent_keys

        cards_played_df = pd.DataFrame(list(cards_played_dict.items()), columns=['Card', 'Played'])
        cards_played_df['Copies'] = cards_played_df['Card'].map(copies_played_dict)
        cards_played_df['Amber'] = cards_played_df['Card'].map(amber_gained_dict)
        rarity_val_dict = {
            'Common': 1,
            'Uncommon': 1.35,
            'Rare': 3.5,
            'Special': 3.5,
        }
        for idx, row in cards_played_df.iterrows():
            rarity = dok_api.get_card_rarity(row['Card'])
            if not rarity:
                print(row['Card'])
        cards_played_df['Rarity Adjustment'] = cards_played_df.apply(lambda r: rarity_val_dict[dok_api.get_card_rarity(r['Card'])], axis=1)
        cards_played_df['Played Adjusted'] = cards_played_df['Played'] * cards_played_df['Rarity Adjustment']
        cards_played_df = cards_played_df.sort_values(by='Played', ascending=False)

        st.session_state.meta_snapshot['games_played_day'] = games_played_day
        st.session_state.meta_snapshot['games_played'] = games_played
        st.session_state.meta_snapshot['set_data_dict'] = set_data_dict
        st.session_state.meta_snapshot['set_win_dict'] = set_win_dict
        st.session_state.meta_snapshot['set_vs_set_dict'] = set_vs_set_dict
        st.session_state.meta_snapshot['set_key_diff_dict'] = set_key_diff_dict
        st.session_state.meta_snapshot['house_data_dict'] = house_data_dict
        st.session_state.meta_snapshot['house_win_dict'] = house_win_dict
        st.session_state.meta_snapshot['house_key_diff_dict'] = house_key_diff_dict
        st.session_state.meta_snapshot['cards_played_df'] = cards_played_df
        st.session_state.meta_snapshot['card_win_dict'] = card_win_dict
        st.session_state.meta_snapshot['played_with_dict'] = played_with_dict
        st.session_state.meta_snapshot['played_with_win_dict'] = played_with_win_dict

        database.log_meta_sets(set_data_dict)


c1, c2, c3, c4 = st.columns([22, 1, 1, 1], vertical_alignment='bottom')
c1.title('Meta Snapshot')

refresh_data = c2.button("⟳")

home = c3.button("🏠")
if home:
    st.switch_page("Home.py")

if refresh_data:
    get_meta_games()
    process_meta_games()

if 'recent_games' not in st.session_state:
    get_meta_games()

if 'meta_snapshot' not in st.session_state:
    process_meta_games()

games_played_day = st.session_state.meta_snapshot['games_played_day']
games_played = st.session_state.meta_snapshot['games_played']
set_data_dict = st.session_state.meta_snapshot['set_data_dict']
set_win_dict = st.session_state.meta_snapshot['set_win_dict']
set_vs_set_dict = st.session_state.meta_snapshot['set_vs_set_dict']
set_key_diff_dict = st.session_state.meta_snapshot['set_key_diff_dict']
house_data_dict = st.session_state.meta_snapshot['house_data_dict']
house_win_dict = st.session_state.meta_snapshot['house_win_dict']
house_key_diff_dict = st.session_state.meta_snapshot['house_key_diff_dict']
cards_played_df = st.session_state.meta_snapshot['cards_played_df']
card_win_dict = st.session_state.meta_snapshot['card_win_dict']
played_with_dict = st.session_state.meta_snapshot['played_with_dict']
played_with_win_dict = st.session_state.meta_snapshot['played_with_win_dict']

st.write('')

activity_graph = graphing.activity_graph(games_played_day)
st.subheader('Games Logged')
with st.container(border=True):
    st.plotly_chart(activity_graph, use_container_width=True)

# Make Set Graph
set_play_graph_dict = {k: round(calcs.calculate_winrate(v, games_played, exception=0) / 2) for k, v in set_data_dict.items()}
set_play_graph = graphing.set_meta_graph(set_play_graph_dict)
set_wr_graph_dict = {h: calcs.calculate_winrate(set_win_dict[h]['wins'], set_win_dict[h]['wins'] + set_win_dict[h]['losses'], exception=0, p1smooth=True) for h in set_data_dict}
set_wr_graph = graphing.set_meta_graph(set_wr_graph_dict, winrate=True)
set_key_diff_graph_dict = {h: set_key_diff_dict[h]['key_diff'] / (set_key_diff_dict[h]['games'] + 1) for h in set_data_dict}
set_key_diff_graph = graphing.set_meta_graph(set_key_diff_graph_dict)

st.subheader('Sets Played')
with st.container(border=True):
    tab_1, tab_2, tab_3 = st.tabs(['Play Rate', 'Win Rate', 'Key Diff'])
    with tab_1:
        st.plotly_chart(set_play_graph, use_container_width=True)
    with tab_2:
        st.plotly_chart(set_wr_graph, use_container_width=True)
    with tab_3:
        st.plotly_chart(set_key_diff_graph, use_container_width=True)


# Make House Graph
house_play_graph_dict = {k: round(calcs.calculate_winrate(v, games_played, exception=0) / 2) for k, v in house_data_dict.items()}
house_play_graph = graphing.house_meta_graph(house_play_graph_dict)
house_wr_graph_dict = {h: calcs.calculate_winrate(house_win_dict[h], v, exception=0, p1smooth=True) for h, v in house_data_dict.items()}
house_wr_graph = graphing.house_meta_graph(house_wr_graph_dict, winrate=True)
house_key_diff_graph_dict = {h: house_key_diff_dict[h]['key_diff'] / (house_key_diff_dict[h]['games'] + 1) for h in house_data_dict}
house_key_diff_graph = graphing.house_meta_graph(house_key_diff_graph_dict)

st.subheader('Houses Played')
with st.container(border=True):
    tab_1, tab_2, tab_3 = st.tabs(['Play Rate', 'Win Rate', 'Key Diff'])
    with tab_1:
        st.plotly_chart(house_play_graph, use_container_width=True)
    with tab_2:
        st.plotly_chart(house_wr_graph, use_container_width=True)
    with tab_3:
        st.plotly_chart(house_key_diff_graph, use_container_width=True)

mc = st.columns([4.5, 1])
mc[0].subheader('Cards Played')

cards_played_df = cards_played_df.sort_values(by='Played', ascending=False)

trimmed_card_df = cards_played_df.head(50)

for i, (idx, row) in enumerate(trimmed_card_df.iterrows()):
    with st.container(border=True):
        container_cols = st.columns([2, 3])
        with container_cols[0].container():
            st.subheader(f"{i + 1}. {row['Card']}")
            card_cols = st.columns([0.75, 1.5] + [0.1, 1.5, 1, 0.1], vertical_alignment='top')
            card_cols[1].image(dok_api.get_card_image(row['Card']))

            frequency = round((100 * row['Played'] / games_played) / 2)

            card_cols[3].markdown(f'<b class="plain-font">% Games: </b>', unsafe_allow_html=True)
            card_cols[4].markdown(f'<b class="plain-italic-font">{formatting.transform_pct_string(frequency, extra_padding=2)}</b>', unsafe_allow_html=True)

            copies = round((row['Copies'] / row['Played']), 1)

            card_cols[3].markdown(f'<b class="plain-font"># Played: </b>', unsafe_allow_html=True)
            card_cols[4].markdown(f'<b class="plain-italic-font">   {copies}</b>', unsafe_allow_html=True)

            wins = card_win_dict[row['Card']]
            games = row['Played']
            winrate, font_style = calcs.calculate_winrate(wins, games, include_font=True)

            card_cols[3].markdown(f'<b class="plain-font">Winrate: </b>', unsafe_allow_html=True)
            card_cols[4].markdown(f'<b class="{font_style}">{formatting.transform_pct_string(winrate, extra_padding=2)}</b>', unsafe_allow_html=True)

            card_amber = round(row['Amber'] / row['Copies'], 1) if row['Copies'] != 0 else 0

            card_cols[3].markdown(f'<b class="plain-font">Amber: </b>', unsafe_allow_html=True)
            card_cols[4].markdown(f'<b class="amber-font">   {card_amber}</b>', unsafe_allow_html=True)

        with container_cols[1].container():
            card_cols = st.columns([1.25] + [0.75 for _ in range(2)])
            played_with_card = played_with_dict[row['Card']]
            played_with_card_win = played_with_win_dict[row['Card']]

            combo_score_dict = defaultdict(float)
            for k, v in played_with_card.items():
                if k in played_with_card_win:
                    combo_winrate, _ = calcs.calculate_winrate(played_with_card_win[k], v, include_font=True)
                    combo_play_rate = v / row['Played']
                    combo_score = combo_winrate * combo_play_rate**2
                    combo_score_dict[k] = combo_score

            combo_cards_shown = 7

            most_played_with = sorted(combo_score_dict, key=combo_score_dict.get, reverse=True)
            most_played_with = most_played_with[:combo_cards_shown]
            most_played_with = sorted(most_played_with, key=played_with_card.get, reverse=True)

            card_cols[0].markdown(f'<b class="plain-font">Played With</b>', unsafe_allow_html=True)

            card_cols = st.columns([0.75 for _ in range(combo_cards_shown)], vertical_alignment='bottom')

            for col_idx in range(combo_cards_shown):
                card_name = most_played_with[col_idx]

                appearance_rate = round(100 * played_with_dict[row['Card']][card_name] / row['Played'])
                card_cols[col_idx].image(dok_api.get_card_image(card_name))
                card_cols[col_idx].markdown(f'<b class="plain-italic-font">{formatting.transform_pct_string(appearance_rate, extra_padding=1)}</b>', unsafe_allow_html=True)

                wins = played_with_win_dict[row['Card']][card_name]
                games = played_with_dict[row['Card']][card_name]
                winrate, font_style = calcs.calculate_winrate(wins, games, include_font=True)

                card_cols[col_idx].markdown(f'<b class="{font_style}">{formatting.transform_pct_string(winrate, extra_padding=1)}</b>', unsafe_allow_html=True)










