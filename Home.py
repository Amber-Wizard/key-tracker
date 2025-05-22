import streamlit as st
import os
import pandas as pd
import re


import analysis
import database
import users


ALLIANCE_SCAN_THRESHOLD = 0.90

default_settings = {
    'icon_link': 'https://i.imgur.com/ib66iB9.png',
    'game_data_use': True,
    'show_decks': False,
    'show_player': False,
    'show_player_page': False,
    'board_layout': 'tco',
    'high_contrast': False,
    'achievements': [],
}


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


def get_user_info():
    st.session_state.user_info = database.get_user(st.session_state.name)
    if 'aliases' not in st.session_state.user_info:
        st.session_state.user_info['aliases'] = []
    for setting in ['board_layout', 'game_data_use', 'high_contrast', 'show_decks', 'show_player', 'icon_link', 'achievements']:
        if setting in st.session_state.user_info:
            st.session_state.settings[setting] = st.session_state.user_info[setting]
    if 'aliases' in st.session_state.user_info:
        st.session_state.aliases = st.session_state.user_info['aliases']
    else:
        st.session_state.aliases = []


if 'login_type' not in st.session_state:
    st.session_state.login_type = 'normal'
if 'auto_login_check' not in st.session_state:
    st.session_state.auto_login_check = False

if 'settings' not in st.session_state:
    st.session_state.settings = default_settings
if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    display_name = "Zenzi"
    if not st.session_state.auto_login_check:
        st.session_state.login_type = 'special'
        st.switch_page('pages/9_Login.py')
else:
    display_name = st.session_state.name

c1, c2 = st.columns([8, 1], vertical_alignment='bottom')
c1.title(f":blue[{display_name}'s] KeyTracker")

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    login = c2.button("Login")
    if login:
        st.switch_page("pages/9_Login.py")
else:
    if 'user_info' not in st.session_state:
        with st.spinner("Getting user info..."):
            get_user_info()

    c2.image(st.session_state.settings['icon_link'])

versions = ["0.4.1", "0.5.0", "0.5.1", "0.6.0", "0.6.1", "0.7.0", "0.8.0", "0.9.0", "0.10.0", "0.10.1", "0.10.2", "0.10.3"]

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
]

with st.expander(fr"$\texttt{{\color{{gray}}\Large v{versions[-1]}}}$"):
    st.divider()
    for c in changes[-1]:
        if c[0] == ' ':
            st.write(c)
        else:
            st.write(f"-{c}")
    for i in range(len(versions)-1):
        st.divider()
        v = versions[-2-i]
        st.write(fr"$\texttt{{\color{{gray}}\Large v{v}}}$")
        v_changes = changes[-2-i]
        for c in v_changes:
            if c[0] == ' ':
                st.write(c)
            else:
                st.write(f"-{c}")

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    pass
else:
    if 'game_log' not in st.session_state:
        with st.spinner('Getting games...'):
            if st.session_state.name == 'master':
                st.session_state.game_log = database.get_all_games(trim_lists=False)
            else:
                if 'aliases' not in st.session_state:
                    get_user_info()
                st.session_state.game_log = database.get_user_games(st.session_state.name, st.session_state.aliases, trim_lists=False)

    # if 'decks_elo' not in st.session_state:
    #     with st.spinner('Getting ELO...'):
    #         st.session_state.decks_elo = database.get_decks_elo(st.session_state.name)

    if 'deck_log' not in st.session_state:
        with st.spinner('Getting decks...'):
            deck_log = database.get_user_decks(st.session_state.name, st.session_state.aliases, st.session_state.game_log)
            # deck_log['ELO'] = 1500
            # for idx, row in deck_log.iterrows():
            #     deck_dict = [d for d in st.session_state.decks_elo if d['deck'] == row['Deck'][0]]
            #     if len(deck_dict) > 0:
            #         deck_log.loc[idx, 'ELO'] = deck_dict[0]['score']

            st.session_state.deck_log = deck_log

if 'featured_game_log' not in st.session_state:
    with st.spinner('Getting featured games...'):
        st.session_state.featured_game_log = database.get_featured_game_log()
        display_log = st.session_state.featured_game_log
        # display_log['Set'] = display_log['Set'].apply(lambda x: [x])
        # display_log['Op. Set'] = display_log['Op. Set'].apply(lambda x: [x])

if 'game_analysis_id' not in st.session_state:
    st.session_state.game_analysis_id = None

st.write('')

cols = st.columns([1, 1, 1, 1, 1, 1])

if cols[1].button('Leaderboard'):
    st.switch_page("pages/4_Leaderboard.py")

if 'name' in st.session_state and st.session_state.name:
    pp_disabled = False
else:
    pp_disabled = True

if cols[0].button('Player Page', disabled=pp_disabled):
    st.switch_page("pages/3_Player_Page.py")

if cols[2].button('Meta Snapshot'):
    st.switch_page("pages/5_Meta_Snapshot.py")

if cols[3].button('Card Trainer'):
    st.switch_page("pages/6_Card_Trainer.py")

st.divider()

st.subheader("Featured Games")
with st.expander("Select Game"):
    if len(st.session_state.featured_game_log) > 0:

        featured_game_choice = st.dataframe(st.session_state.featured_game_log[['Date', 'Player', 'Opponent', 'Deck', 'Opponent Deck', 'Likes']], on_select='rerun', selection_mode='single-row', hide_index=True)
    else:
        featured_game_choice = None
        st.write("No featured games.")

analyze_games = st.button("Analyze", key='analyze_featured_games')
if analyze_games:
    if featured_game_choice:
        selected_featured_game = featured_game_choice['selection']['rows']
        if len(selected_featured_game) == 0:
            st.error("No game selected")
        else:
            st.session_state.game_id = st.session_state.featured_game_log.iloc[selected_featured_game[0]]['ID'][0]
            st.switch_page("pages/1_Game_Analysis.py")

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    pass
else:
    st.divider()
    st.subheader("My Games")
    with st.expander("Select Game"):
        game_choice = None
        if st.session_state.game_log is not None and len(st.session_state.game_log) > 0:
            archon_games, alliance_games, sealed_games = st.tabs(['Archon', 'Alliance', 'Sealed'])
            for form, tab in zip(['archon', 'alliance', 'sealed'], [archon_games, alliance_games, sealed_games]):
                with tab:
                    if form != 'sealed':
                        game_choice = st.dataframe(st.session_state.game_log[form][['Date', 'Deck', 'Opponent Deck', 'Opponent', 'Winner', 'Turns']], on_select='rerun', selection_mode='single-row', hide_index=True)
                    else:
                        c1, _ = st.columns([6, 4])
                        game_choice = c1.dataframe(st.session_state.game_log[form][['Date', 'Opponent', 'Winner', 'Turns']], on_select='rerun', selection_mode='single-row', hide_index=True)

                    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 5])

                    analyze_games = c1.button("Analyze", key=f'analyze_games_{form}')
                    if analyze_games:
                        if game_choice:
                            selected_game = game_choice['selection']['rows']
                            if len(selected_game) == 0:
                                st.error("No game selected")
                            else:
                                st.session_state.game_id = st.session_state.game_log[form].iloc[selected_game[0]]['ID']
                                st.switch_page("pages/1_Game_Analysis.py")

                    feature_games = c2.button("Feature", key=f'feature_games_{form}')
                    if feature_games:
                        if game_choice:
                            selected_game = game_choice['selection']['rows']
                            if len(selected_game) == 0:
                                st.error("No game selected")
                            else:
                                game_id = st.session_state.game_log[form].iloc[selected_game[0]]['ID']
                                if database.feature_game(game_id):
                                    st.success("Game featured!")
                                else:
                                    st.error("Game has already been featured.")

                    delete_games = c3.button("Delete", key=f'delete_games_{form}', type='primary')
                    if delete_games:
                        if game_choice:
                            selected_game = game_choice['selection']['rows']
                            if len(selected_game) == 0:
                                st.error("No game selected")
                            else:
                                game_id = st.session_state.game_log[form].iloc[selected_game[0]]['ID']
                                database.delete_game(game_id)
                                st.success("Game deleted")

                    if form == 'alliance':
                        if c4.button("Auto-Scan", key=f'auto_scan_{form}'):
                            with st.spinner('Scanning games...'):
                                print(f"Initializing Scan Process for {st.session_state.name}")
                                alliances_updated = 0
                                alliances = database.get_user_alliances(st.session_state.name, st.session_state.user_info['aliases'])
                                alliance_card_dict = {}
                                for alliance_idx, alliance in alliances.iterrows():
                                    alliance_card_dict[alliance['alliance']] = [c['cardTitle'] for j in range(3) for c in alliance['data']['deck']['housesAndCards'][j]['cards']]
                                for scan_format in 'alliance', 'sealed':
                                    print(f"Scanning {scan_format} games")
                                    for idx, row in st.session_state.game_log[scan_format].iterrows():
                                        game_id = row['ID'][0]
                                        print(f"Checking game [{game_id}]")
                                        player_name = row['Player'][0]
                                        cards_played = row['Game Log'][0][player_name]['individual_cards_played'][-1]
                                        opponent_name = row['Opponent'][0]
                                        opponent_cards_played = row['Game Log'][0][opponent_name]['individual_cards_played'][-1]
                                        for cp in [cards_played, opponent_cards_played]:
                                            if cp == cards_played and row['Deck'][0] != '---':
                                                print(f"Deck Skipped")
                                                continue
                                            elif cp == opponent_cards_played and row['Opponent Deck'][0] != '---':
                                                print(f"Deck Skipped")
                                                continue
                                            print(f"Cards Played: {cp.keys()}")
                                            possible_alliances = {}
                                            for k, v in alliance_card_dict.items():
                                                accuracy = len([c for c in cp.keys() if c in v]) / len(cp.keys())
                                                possible_alliances[k] = accuracy
                                            most_likely = max(possible_alliances, key=possible_alliances.get)
                                            likelihood = possible_alliances[most_likely]
                                            print(f"Most Likely: [{most_likely}] ({round(100 * likelihood)})")
                                            if likelihood > ALLIANCE_SCAN_THRESHOLD:
                                                link = alliances.loc[alliances['alliance'] == most_likely, 'link'].iloc[0]
                                                success, message = database.update_alliance_deck(game_id, most_likely, link, player_deck=cp == cards_played)
                                                if success:
                                                    alliances_updated += 1
                                                else:
                                                    st.toast(f"{message} [{game_id}]", icon='❌')
                                            # else:
                                            #     database.update_alliance_deck(game_id, '---', 'https://decksofkeyforge.com/', player_deck=cp == cards_played)
                                st.toast(f"({alliances_updated}) Alliances Updated", icon=':material/done_all:')

                                # If the top result is over a certain threshold, assign the alliance

        else:
            st.write("No games played.")

    st.divider()
    st.subheader("Analyze Deck")
    with st.expander("Select Deck"):
        deck_choice = None
        # st.write('Filter Games')
        # c1, c2, c3, c4 = st.columns([1, 1, 1, 1], vertical_alignment='bottom')
        # sas_min = c1.text_input('SAS Min.')
        # if sas_min:
        #     try:
        #         sas_min = int(sas_min)
        #     except:
        #         sas_min = 0
        #
        # sas_max = c2.text_input('SAS Max.')
        # if sas_max:
        #     try:
        #         sas_max = int(sas_max)
        #     except:
        #         sas_max = 1000

        if st.session_state.deck_log is not None and len(st.session_state.game_log) > 0:
            archon_games, alliance_games, sealed_games = st.tabs(['Archon', 'Alliance', 'Sealed'])
            for form, tab in zip(['archon', 'alliance', 'sealed'], [archon_games, alliance_games, sealed_games]):
                with tab:
                    if form != 'sealed':
                        c1, _ = st.columns([6, 4])
                        deck_choice = c1.dataframe(st.session_state.deck_log[form][['Deck', 'Games', 'Win-Loss', 'Winrate']], on_select='rerun', selection_mode='single-row', hide_index=True)
                    else:
                        c1, _ = st.columns([1, 2])
                        deck_choice = c1.dataframe(st.session_state.deck_log[form][['Games', 'Win-Loss', 'Winrate']], on_select='rerun', selection_mode='single-row', hide_index=True)

                    analyze_deck = st.button("Analyze", key=f'analyze_deck_{form}')
                    if analyze_deck:
                        if deck_choice:
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
                                deck = st.session_state.deck_selection['Deck'].iat[0][0]
                                elo_data = database.get_elo(st.session_state.name, deck, form)
                                st.session_state.elo_data = elo_data
                                st.session_state.deck = deck
                                st.session_state.deck_data_compare = None
                                share_id = elo_data['_id']
                                st.session_state.share_id = share_id
                                st.switch_page("pages/2_Deck_Analysis.py")
        else:
            st.write("No games played.")

    st.write('')
    st.write('')
    st.write('')
    authenticator, name_conversion_dict = users.get_authenticator()

    if 'name_conversion_dict' not in st.session_state:
        st.session_state.name_conversion_dict = name_conversion_dict

    authenticator.logout()
