import streamlit as st
import os
import pandas as pd
import re
from streamlit_authenticator.utilities.validator import Validator
from streamlit_authenticator.utilities.exceptions import RegisterError


import browser
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


# Monkey patch to override name validation
def custom_validate_name(self, name_entry: str) -> bool:
    pattern = r"^[A-Za-z0-9 ]+$"
    return 1 <= len(name_entry) <= 100 and bool(re.match(pattern, name_entry))

Validator.validate_name = custom_validate_name

st.markdown("""
<style>
.version-font {
    font-size: 32px !important;
    color: #424242 !important;
}
""", unsafe_allow_html=True)

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    display_name = "Zenzi"
else:
    display_name = st.session_state.name
st.title(f":blue[{display_name}'s] KeyTracker")

# authenticator = users.get_authenticator()
# name, auth_status, username = authenticator.login(location="main")

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:

    st.write('')
    st.write('')

    if st.session_state.authentication_status is False:
        st.error("Incorrect username/password")

    reg_username, reg_email, reg_name = None, None, None
    try:
        reg_email, reg_username, reg_name, = authenticator.register_user(pre_authorization=False)
    except RegisterError as e:
        st.error(f"{e}")
    user_dict = authenticator.authentication_handler.credentials['usernames']
    if reg_username:
        st.write(user_dict)
        # register_status, message = users.new_user(reg_username, user_dict[reg_username]['password'], reg_email, reg_name)

        # if register_status == "Error":
        #     st.error(message)
        # else:
        #     st.success(message)

elif st.session_state.authentication_status:

    if 'playing' not in st.session_state:
        st.session_state.playing = None
    if 'game_obj' not in st.session_state:
        st.session_state.game_obj = None
    if 'game_log' not in st.session_state:
        # st.session_state.game_log = database.pull_user_games(st.session_state.name)
        st.session_state.game_log = None
    if 'game_analysis_id' not in st.session_state:
        st.session_state.game_analysis_id = None

    version = "0.3.0"
    st.markdown(f'<p class="version-font">v{version}</p>', unsafe_allow_html=True)
    st.divider()
    st.subheader("Launch The Crucible Online")
    st.write('')
    launch = st.button("Play")
    if launch and not st.session_state.playing:
        st.session_state.playing = True
        st.session_state.game_obj = browser.play(st.session_state.name, None)
    if launch and st.session_state.playing:
        st.error("The Crucible is already running")
    if st.session_state.game_obj:
        st.session_state.playing = False
        st.session_state.game_obj = None

    st.divider()
    st.subheader("Analyze Game")
    with st.expander("Select Game"):
        game_choice = st.dataframe(st.session_state.game_log[['Date', 'Deck', 'Opponent Deck', 'Opponent', 'Winner']],
                                   on_select='rerun', selection_mode='single-row', hide_index=True)
    analyze_games = st.button("Analyze", key='analyze_games')
    if analyze_games:
        selected_game = game_choice['selection']['rows']
        if len(selected_game) == 0:
            st.error("No game selected")
        else:
            st.session_state.game_id = st.session_state.game_log.iloc[selected_game[0]]['ID']
            st.switch_page("pages/1_Game_Analysis.py")

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
    authenticator.logout()
