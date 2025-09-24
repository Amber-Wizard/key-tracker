import collections

import streamlit as st
import os
import pandas as pd
import re


import analysis
import database
import dok_api
import users
import formatting
import states
import graphing


try:
    st.set_page_config(
        page_title="KeyTracker",
        page_icon="🔑",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except:
    pass

st.markdown("""
<style>
.version-font {
    font-size: 32px !important;
    color: #424242 !important;
}
.dark-font {
    font-size: 12px !important;
    color: #424242 !important;
}
""", unsafe_allow_html=True)


# Load User Data
@st.cache_data
def get_user_info():
    st.session_state.user_info = database.get_user(st.session_state.name)
    st.session_state = states.update_settings(st.session_state, user_settings=st.session_state.user_info)
    if 'aliases' not in st.session_state.user_info:
        st.session_state.user_info['aliases'] = []


# Initialize States
if 'login_type' not in st.session_state:
    st.session_state.login_type = 'normal'
if 'auto_login_check' not in st.session_state:
    st.session_state.auto_login_check = False

if 'settings' not in st.session_state:
    st.session_state = states.update_settings(st.session_state)

if 'authentication_status' not in st.session_state or not st.session_state.authentication_status:
    display_name = "Zenzi"
    # Try to automatically log the user in
    if not st.session_state.auto_login_check:
        st.session_state.login_type = 'special'
        st.switch_page('pages/9_Login.py')
else:
    display_name = st.session_state.name

c1, c2 = st.columns([8, 1], vertical_alignment='bottom')
c1.title(f":blue[{display_name}'s] KeyTracker")

if 'authentication_status' not in st.session_state or not st.session_state.authentication_status:
    login = c2.button("Login")
    if login:
        st.switch_page("pages/9_Login.py")
else:
    if 'user_info' not in st.session_state:
        with st.spinner("Getting user info..."):
            get_user_info()

    c2.image(st.session_state.settings['icon_link'])

versions = ["0.4.1", "0.5.0", "0.5.1", "0.6.0", "0.6.1", "0.7.0", "0.8.0", "0.9.0", "0.10.0", "0.10.1", "0.10.2", "0.10.3", "0.10.4", "0.10.5"]


changes = [
    [
        'Added changelog',
        'Added actual turns to win vs prediction',
        'Changed default sorting for My Games to date (descending)',
        'Added expand all turns button',
        'Removed creature count from turn recap (redundant)',
        'Added artifacts to turn recap',
        'Restructured turn recap',
        'Removed winner column from featured games selection',
        'Moved like button',
        'Added back button to Game Analysis'
    ],
    [
        'Added Deck Analysis',
        'Added DoK integration',
        'Added Game Messages in Turn Recap',
        'Added Creature Survival Rate',
        'Added Amber Defense Score',
        'Added ELO'
    ],
    [
        'Fixed Turn Logs'
    ],
    [
        'Added Tide Tracker',
        'Added Token Tracker',
        'Added Sealed Compatibility',
        'Added Deck Error Fix',
        'Improved Prediction Accuracy',
        'Improved Reap Rate Accuracy',
        'Improved Card Info Accuracy (Deck Analysis)',
        'Adjusted Amber Sources & House Calls (Deck Analysis)',
    ],
    [
        'Added Chains, Deck, Discard, Archives, and Purge counts',
        'Fixed ELO Error'
    ],
    [
        'Added Amber Skies & Skyborn',
        'Added Cards Played by Turn % **(Deck Analysis)**',
        'Added Deck Comparison **(Deck Analysis)**',
        'Added House Winrates **(Deck Analysis)**',
        'Added Individual Card Winrates **(Deck Analysis)**',
        'Changed Game Length to % of Games **(Deck Analysis)**',
        'Improved Site Performance **(Deck Analysis)**',
        'Added Individual Survival Rate **(Game Analysis)**',
        'Improved Survival Rate Accuracy',
        'Improved Database Connection Handling',
        "Changed 'Name' Field to 'TCO Username'",
        'Fixed Various Bugs',
    ],
    [
        'Added Tokens of Change & Redemption',
        'Added Achievements',
        'Added Player Icons',
        'Added Leaderboard',
        'Added Player Page',
        'Added Settings:',
        ' - Board Layout',
        ' - High Contrast Amber Charts',
        ' - Show Decks in Leaderboard',
        ' - Show Player Stats in Leaderboard',
        ' - Share Aggregate Data',
    ],
    [
        'Added Meta Snapshot',
        'Added Card Trainer (BETA)',
        'Added Multiple TCO Names',
        'Added More Mutation',
        'Reformatted Pages',
        'Added Advantage Charts',
        'Updated Amber Charts',
        'Updated House Charts',
        'Added House Stats (Deck Analysis)',
        'Added Winrate to Cards Played by Turn (Deck Analysis)',
    ],
    [
        'Added Discovery',
        'Added Formats',
        'Added Auto-Scan (Alliance)',
        'Added Pod Search (Alliance)',
        'Added Forge Through Rate',
        'Added Legacy Winrate',
        'Added Meta Winrate',
        'Added Flex Graph',
        'Added Tokens Graph (Deck Analysis)',
    ],
    [
        'Added Tooltips',
        'Added Card Image Column (Cards Data)',
    ],
    ['Added VM25'],
    ['Added Turn Score', 'Various Bug Fixes'],
    ['Added PV', 'Added CC'],
    [
        'Reworked Meta Snapshot',
        'Color Coding! (Can be disabled in Player Page > Settings > Display)',
        'Added Deck Stats (Deck Analysis)',
        'Added Winrate to Game Length Graph (Deck Analysis)',
        'Added Amber Sources to House Info (Deck Analysis)',
        'Added Amber % Bars in Card Data (Deck/Game Analysis)',
        'Added Deck Game Select (Deck Analysis)',
        'Added Download/Info Button (Home)',
        'Updated House & Set Winrates (Deck Analysis)',
        'Updated Register User Widget (Login)',
        'Removed Favorites (Player Page)',
        'Fixed Calculation Issue (Deck Analysis)',
        'Various Restructuring & Improvements',
    ]
]
with st.expander(fr"$\texttt{{\color{{gray}}\Large v{versions[-1]}}}$"):
    st.divider()
    for c in changes[-1]:
        st.write(c if c[0] == ' ' else f"-{c}")
    for i in range(len(versions)-1):
        st.divider()
        v = versions[-2-i]
        st.write(fr"$\texttt{{\color{{gray}}\Large v{v}}}$")
        v_changes = changes[-2-i]
        for c in v_changes:
            st.write(c if c[0] == ' ' else f"-{c}")

if 'authentication_status' not in st.session_state or not st.session_state.authentication_status:
    pass
else:
    if 'game_log' not in st.session_state:
        with st.spinner('Getting games...'):
            if 'user_info' not in st.session_state:
                with st.spinner("Getting user info..."):
                    get_user_info()

            st.session_state.game_log = database.get_user_games(st.session_state.name, st.session_state.user_info.get('aliases', []), trim_lists=True)

    if 'deck_log' not in st.session_state:
        with st.spinner('Getting decks...'):
            deck_log = database.get_user_decks(st.session_state.name, st.session_state.user_info.get('aliases', []), st.session_state.game_log)

            st.session_state.deck_log = deck_log

if 'featured_game_log' not in st.session_state:
    with st.spinner('Getting featured games...'):
        st.session_state.featured_game_log = database.get_featured_game_log()
        display_log = st.session_state.featured_game_log

if 'game_analysis_id' not in st.session_state:
    st.session_state.game_analysis_id = None

st.write('')

cols = st.columns([1, 1, 1, 1, 1, 1])

if cols[1].button('Leaderboard'):
    st.switch_page("pages/4_Leaderboard.py")

pp_disabled = not bool(st.session_state.get('name'))

if cols[0].button('Player Page', disabled=pp_disabled):
    st.switch_page("pages/3_Player_Page.py")

if cols[2].button('Meta Snapshot'):
    st.switch_page("pages/5_Meta_Snapshot.py")

if cols[3].button('Card Trainer'):
    st.switch_page("pages/6_Card_Trainer.py")

cols[-1].link_button('Download / Info', url="https://drive.google.com/drive/folders/1YvmBXaMBgnGWVQMKbYAUwZRMeS-ulxv2?usp=sharing")

st.divider()

st.subheader("Featured Games")
with st.expander("Select Game"):
    if len(st.session_state.featured_game_log) > 0:
        featured_game_choice = st.dataframe(st.session_state.featured_game_log[['Date', 'Player', 'Opponent', 'Deck', 'Opponent Deck', 'Likes']], on_select='rerun', selection_mode='single-row', hide_index=True)
    else:
        featured_game_choice = None
        st.write("No featured games.")

if st.button("Analyze", key='analyze_featured_games') and featured_game_choice:
    selected_featured_game = featured_game_choice['selection']['rows']
    if len(selected_featured_game) == 0:
        st.error("No game selected")
    else:
        st.session_state.game_analysis_id = st.session_state.featured_game_log.iloc[selected_featured_game[0]]['ID']
        st.switch_page("pages/1_Game_Analysis.py")

if 'authentication_status' not in st.session_state or not st.session_state.authentication_status:
    pass
else:
    st.divider()
    st.subheader("My Games")
    with st.container(border=True):
        game_choice = None
        if st.session_state.game_log is not None and len(st.session_state.game_log) > 0:
            archon_games, alliance_games, sealed_games = st.tabs(['Archon', 'Alliance', 'Sealed'])
            for form, tab in zip(['archon', 'alliance', 'sealed'], [archon_games, alliance_games, sealed_games]):
                with tab:
                    if form != 'sealed':
                        c1, _ = st.columns([99, 1])
                        df_cols = ['Date', 'Deck', 'Opponent Deck', 'Opponent', 'Winner', 'Turns']
                    else:
                        c1, _ = st.columns([6, 4])
                        df_cols = ['Date', 'Opponent', 'Winner', 'Turns']

                    game_df = st.session_state.game_log[form][df_cols]

                    stylized_df, deck_colors = formatting.format_game_df(game_df, st.session_state.user_info.get('aliases', []) + [st.session_state.name], deck_colors=st.session_state.get('deck_colors', None), color_coding=st.session_state.settings.get('color_coding', True))
                    st.session_state.deck_colors = deck_colors
                    game_choice = c1.dataframe(stylized_df, on_select='rerun', selection_mode='single-row', hide_index=True)

                    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 5])

                    if c1.button("Analyze", key=f'analyze_games_{form}') and game_choice:
                        selected_game = game_choice['selection']['rows']
                        if len(selected_game) == 0:
                            st.error("No game selected")
                        else:
                            st.session_state.game_analysis_id = st.session_state.game_log[form].iloc[selected_game[0]]['ID']
                            st.switch_page("pages/1_Game_Analysis.py")

                    if c2.button("Feature", key=f'feature_games_{form}') and game_choice:
                        selected_game = game_choice['selection']['rows']
                        if len(selected_game) == 0:
                            st.error("No game selected")
                        else:
                            game_analysis_id = st.session_state.game_log[form].iloc[selected_game[0]]['ID']
                            if database.feature_game(game_analysis_id):
                                st.success("Game featured!")
                            else:
                                st.error("Game has already been featured.")

                    if c3.button("Delete", key=f'delete_games_{form}', type='primary') and game_choice:
                        selected_game = game_choice['selection']['rows']
                        if len(selected_game) == 0:
                            st.error("No game selected")
                        else:
                            game_analysis_id = st.session_state.game_log[form].iloc[selected_game[0]]['ID']
                            database.delete_game(game_analysis_id)
                            st.success("Game deleted")

                    if form == 'alliance':
                        if c4.button("Auto-Scan", key=f'auto_scan_{form}'):
                            with st.spinner('Scanning games...'):
                                st.session_state, alliances_updated = database.auto_scan_alliance_games(st.session_state)

                                st.toast(f"({alliances_updated}) Alliances Updated", icon=':material/done_all:')

        else:
            st.write("No games played. Download the KeyTracker client above to start tracking your games!")

    st.divider()
    st.subheader("Analyze Deck")
    with st.container(border=True):
        deck_choice = None

        if st.session_state.deck_log is not None and len(st.session_state.game_log) > 0:
            archon_games, alliance_games, sealed_games = st.tabs(['Archon', 'Alliance', 'Sealed'])
            for form, tab in zip(['archon', 'alliance', 'sealed'], [archon_games, alliance_games, sealed_games]):
                with tab:
                    if form != 'sealed':
                        c1, _ = st.columns([6, 4])
                        df_cols = ['Deck', 'Games', 'Win-Loss', 'Winrate']
                    else:
                        c1, _ = st.columns([1, 2])
                        df_cols = ['Games', 'Win-Loss', 'Winrate']

                    df_col_config = {
                        "Deck": st.column_config.TextColumn(width='large'),
                        "Winrate": st.column_config.NumberColumn(format='percent', width='small'),
                        "Win-Loss": st.column_config.TextColumn(width='small')
                    }

                    deck_df = st.session_state.deck_log[form][df_cols]
                    stylized_df, deck_colors = formatting.format_deck_df(deck_df, deck_colors=st.session_state.get('deck_colors', None), color_coding=st.session_state.settings.get('color_coding', True))

                    deck_choice = c1.dataframe(stylized_df, on_select='rerun', selection_mode='single-row', hide_index=True, column_config=df_col_config)

                    if st.button("Analyze", key=f'analyze_deck_{form}') and deck_choice:
                        selected_deck = deck_choice['selection']['rows']
                        if len(selected_deck) == 0:
                            st.error("No deck selected")
                        else:
                            if 'elo_data' in st.session_state:
                                del st.session_state['elo_data']
                            if 'deck_games' in st.session_state:
                                del st.session_state['deck_games']
                            if 'deck_data' in st.session_state:
                                del st.session_state['deck_data']
                            if 'share_id' in st.session_state:
                                del st.session_state['share_id']
                            # if sas_min:
                            #     st.session_state.sas_min = sas_min
                            # else:
                            #     if 'sas_min' in st.session_state:
                            #         del st.session_state['sas_min']
                            # if sas_max:
                            #     st.session_state.sas_max = sas_max
                            # else:
                            #     if 'sas_max' in st.session_state:
                            #         del st.session_state['sas_max']

                            st.session_state.deck_selection = st.session_state.deck_log[form].iloc[selected_deck]
                            deck = st.session_state.deck_selection['Deck'].iat[0]
                            elo_data = database.get_elo(st.session_state.name, deck, form)
                            st.session_state.elo_data = elo_data
                            st.session_state.deck = deck
                            st.session_state.deck_data_compare = None
                            share_id = elo_data['_id']
                            st.session_state.share_id = share_id
                            st.switch_page("pages/2_Deck_Analysis.py")
        else:
            st.write("Not enough games played (Min. 5 games)")

    st.write('')
    st.write('')
    st.write('')
    authenticator, name_conversion_dict = users.get_authenticator()

    if 'name_conversion_dict' not in st.session_state:
        st.session_state.name_conversion_dict = name_conversion_dict

    def clear_session_state(*args):
        st.session_state = states.clear_state(st.session_state)

    authenticator.logout(callback=clear_session_state)
