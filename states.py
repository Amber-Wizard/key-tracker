import streamlit as st


def clear_state(session_state):
    for key in session_state.keys():
        del session_state[key]

    return session_state


def get_user_aliases(session_state):
    if 'user_info' in session_state:
        if 'aliases' in session_state['user_info']:
            return session_state['user_info']['aliases']
    return []


def get_player_icon(player_info):
    default_icon = 'https://i.imgur.com/ib66iB9.png'
    if player_info and isinstance(player_info, dict) and 'icon_link' in player_info:
        return player_info['icon_link']
    return default_icon


def update_settings(session_state, user_settings=None):
    default_settings = {
        'icon_link': 'https://i.imgur.com/ib66iB9.png',
        'game_data_use': True,
        'show_decks': False,
        'show_player': False,
        'show_player_page': False,
        'color_coding': True,
        'board_layout': 'tco',
        'high_contrast': False,  # deprecated, may have references that need deleting
        'achievements': [],
    }

    session_state.settings = default_settings

    if not user_settings:
        return session_state

    for setting in default_settings.keys():
        if setting in user_settings:
            session_state.settings[setting] = user_settings[setting]

    return session_state


def get_setting(session_state, setting):
    if 'settings' in session_state:
        if setting in session_state['settings']:
            return session_state['settings'][setting]
    return None

