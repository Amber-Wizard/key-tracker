import streamlit as st
import os
import pandas as pd
import re


import analysis
import database
import users


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
""", unsafe_allow_html=True)

if 'login_type' not in st.session_state:
    st.session_state.login_type = 'normal'
if 'auto_login_check' not in st.session_state:
    st.session_state.auto_login_check = False

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    display_name = "Zenzi"
    if not st.session_state.auto_login_check:
        st.session_state.login_type = 'special'
        st.switch_page('pages/3_Login.py')
else:
    display_name = st.session_state.name

c1, c2 = st.columns([9, 1])
c1.title(f":blue[{display_name}'s] KeyTracker")
versions = ["0.4.1", "0.5.0"]

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
    ]
]

with st.expander(fr"$\texttt{{\color{{gray}}\Large v{versions[-1]}}}$"):
    st.divider()
    for c in changes[-1]:
        st.write(f"-{c}")
st.divider()

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    login = c2.button("Login")
    if login:
        st.switch_page("pages/3_Login.py")
if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    pass
else:
    if 'game_log' not in st.session_state:
        with st.spinner('Getting games...'):
            if st.session_state.name == 'master':
                st.session_state.game_log = database.get_all_games(trim_lists=False)
            else:
                st.session_state.game_log = database.get_user_games(st.session_state.name)
    if 'deck_log' not in st.session_state:
        with st.spinner('Getting decks...'):
            st.session_state.deck_log = database.get_user_decks(st.session_state.name)
if 'featured_game_log' not in st.session_state:
    with st.spinner('Getting featured games...'):
        st.session_state.featured_game_log = database.get_featured_game_log()
        display_log = st.session_state.featured_game_log
        display_log['Set'] = display_log['Set'].apply(lambda x: [x])
        display_log['Op. Set'] = display_log['Op. Set'].apply(lambda x: [x])
if 'game_analysis_id' not in st.session_state:
    st.session_state.game_analysis_id = None

st.subheader("Featured Games")
with st.expander("Select Game"):
    if len(st.session_state.featured_game_log) > 0:

        featured_game_choice = st.dataframe(st.session_state.featured_game_log[['Date', 'Player', 'Opponent', 'Deck', 'Set', 'SAS', 'Opponent Deck', 'Op. Set', 'Op. SAS', 'Likes']], on_select='rerun', selection_mode='single-row', hide_index=True)
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
        if not st.session_state.game_log.empty:
            game_choice = st.dataframe(st.session_state.game_log[['Date', 'Deck', 'Opponent Deck', 'Opponent', 'Winner']], on_select='rerun', selection_mode='single-row', hide_index=True)
        else:
            game_choice = None
            st.write("No games played.")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 6])
    analyze_games = c1.button("Analyze", key='analyze_games')
    if analyze_games:
        if game_choice:
            selected_game = game_choice['selection']['rows']
            if len(selected_game) == 0:
                st.error("No game selected")
            else:
                st.session_state.game_id = st.session_state.game_log.iloc[selected_game[0]]['ID']
                st.switch_page("pages/1_Game_Analysis.py")
    feature_games = c2.button("Feature", key='feature_games')
    if feature_games:
        if game_choice:
            selected_game = game_choice['selection']['rows']
            if len(selected_game) == 0:
                st.error("No game selected")
            else:
                game_id = st.session_state.game_log.iloc[selected_game[0]]['ID']
                if database.feature_game(game_id):
                    st.success("Game featured!")
                else:
                    st.error("Game has already been featured.")
    delete_games = c3.button("Delete", key='delete_games', type='primary')
    if delete_games:
        if game_choice:
            selected_game = game_choice['selection']['rows']
            if len(selected_game) == 0:
                st.error("No game selected")
            else:
                game_id = st.session_state.game_log.iloc[selected_game[0]]['ID']
                database.delete_game(game_id)
                st.success("Game deleted")

    st.divider()
    st.subheader("Analyze Deck")
    with st.expander("Select Deck"):
        if not st.session_state.deck_log.empty:
            deck_choice = st.dataframe(st.session_state.deck_log[['Deck', 'Set', 'SAS', 'Games', 'Win-Loss', 'Winrate', 'ELO']], on_select='rerun', selection_mode='single-row', hide_index=True)
        else:
            deck_choice = None
            st.write("No games played.")
    analyze_deck = st.button("Analyze", key='analyze_deck')
    if analyze_deck:
        if deck_choice:
            selected_deck = deck_choice['selection']['rows']
            if len(selected_deck) == 0:
                st.error("No game selected")
            else:
                if 'elo_data' in st.session_state:
                    del st.session_state['elo_data']
                if 'deck_games' in st.session_state:
                    del st.session_state['deck_games']
                if 'deck_data' in st.session_state:
                    del st.session_state['deck_data']
                st.session_state.deck_selection = st.session_state.deck_log.iloc[selected_deck]
                st.switch_page("pages/2_Deck_Analysis.py")
    st.write('')
    st.write('')
    st.write('')
    authenticator = users.get_authenticator()
    authenticator.logout()
