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
        st.switch_page('pages/2_Login.py')
else:
    display_name = st.session_state.name

c1, c2 = st.columns([9, 1])
c1.title(f":blue[{display_name}'s] KeyTracker")
version = "0.4.0"

changes = [
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
]

with st.expander(fr"$\texttt{{\color{{gray}}\Large v{version}}}$"):
    st.divider()
    for c in changes:
        st.write(f"-{c}")
st.divider()

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    login = c2.button("Login")
    if login:
        st.switch_page("pages/2_Login.py")
if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    pass
else:
    if 'game_log' not in st.session_state:
        if st.session_state.name == 'master':
            st.session_state.game_log = database.get_all_games()
        else:
            st.session_state.game_log = database.get_user_games(st.session_state.name)
if 'featured_game_log' not in st.session_state:
    st.session_state.featured_game_log = database.get_featured_game_log()
if 'game_analysis_id' not in st.session_state:
    st.session_state.game_analysis_id = None

st.subheader("Featured Games")
with st.expander("Select Game"):
    if len(st.session_state.featured_game_log) > 0:
        featured_game_choice = st.dataframe(st.session_state.featured_game_log[['Date', 'Player', 'Opponent', 'Deck', 'Opponent Deck', 'Likes']], on_select='rerun', selection_mode='single-row', hide_index=True)
    else:
        featured_game_choice = None
        st.write("No featured games.")

c1, c2, c3, c4 = st.columns([1, 1, 1, 6])
analyze_games = c1.button("Analyze", key='analyze_featured_games')
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
        st.write("Coming soon!")
    analyze_deck = st.button("Analyze", key='analyze_deck')
    if analyze_deck:
        pass
    st.write('')
    st.write('')
    st.write('')
    authenticator = users.get_authenticator()
    authenticator.logout()
