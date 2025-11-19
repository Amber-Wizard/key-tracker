import streamlit as st
import pandas as pd
import random


def get_random_color():
    high_bound = 255 * 3 - 30
    low_bound = 160 * 3
    req_diff = 40
    r_lims = [80, 240]
    g_lims = [80, 255]
    b_lims = [100, 255]

    r_val, g_val, b_val = 0, 0, 0
    satisfied = False
    while not satisfied:
        r_val = random.randint(r_lims[0], r_lims[1])
        g_val = random.randint(g_lims[0], g_lims[1])
        b_val = random.randint(b_lims[0], b_lims[1])

        avg_val = (r_val + g_val + b_val) / 3
        max_diff = max(abs(r_val - avg_val), abs(g_val - avg_val), abs(b_val - avg_val))

        if (high_bound > r_val + g_val + b_val > low_bound) and max_diff > req_diff and r_val != max(r_val, g_val, b_val):
            satisfied = True

    return f'color: rgb({r_val}, {g_val}, {b_val})'


def format_game_df(game_df, player_names, deck_colors=None, color_coding=False):
    if not isinstance(game_df, pd.DataFrame):
        return None

    def highlight_player_names(val):
        if val in player_names:
            return 'color: #60b4ff'
        elif val == " has won the game ":
            return 'color: rgb(200, 0, 0)'
        else:
            return 'color: #ff4b4b'

    def highlight_deck_names(val):
        return deck_colors.get(val, 'color: pink')

    def highlight_opponent_deck_names(val):
        return 'color: pink'

    styled_df = (
        game_df
            .style
            .format({'Date': lambda dt: dt.strftime('%m/%d/%y') if pd.notnull(dt) else ''})
    )

    if color_coding:
        if 'Deck' in game_df.columns:
            if deck_colors is None:
                deck_names = game_df['Deck'].unique()
                deck_colors = {d: get_random_color() for d in deck_names}
            else:
                for deck_name in game_df['Deck'].unique():
                    if deck_name not in deck_colors:
                        deck_colors[deck_name] = get_random_color()

            styled_df = (
                styled_df
                    .map(highlight_player_names, subset=['Opponent', 'Winner'])
                    .map(highlight_deck_names, subset=['Deck'])
                    .map(highlight_opponent_deck_names, subset=['Opponent Deck'])
            )
        else:
            styled_df = styled_df.map(highlight_player_names, subset=['Opponent', 'Winner'])

    return styled_df, deck_colors


def format_deck_df(deck_df, deck_colors=None, color_coding=False):
    if not isinstance(deck_df, pd.DataFrame):
        return None

    def highlight_deck_names(val):
        return deck_colors.get(val, 'color: pink')

    def highlight_winrate(val):
        if val >= 0.5:
            return 'color: #60b4ff'
        else:
            return 'color: #ff4b4b'

    def highlight_games(val):
        if val >= 100:
            return 'color: #60b4ff'
        if val < 25:
            return 'color: #ff4b4b'
        return None

    def highlight_streak(val):
        if val == '' or val is None:
            return None
        # Define buckets
        if val < 5:
            return 'color: #ff4b4b'
        elif 5 <= val < 10:
            return 'color: #ff804b'
        elif 10 <= val < 25:
            return 'color: #ffb84b'
        elif 25 <= val < 52:
            return 'color: #ffe34b'
        elif 52 <= val < 100:
            return 'color: #fff04b'
        else:  # 100+
            return 'color: #fff64b'

    # Start with the base style (no coloring)
    styled_df = deck_df.style

    if color_coding:
        # Only generate deck colors if color coding is enabled
        if 'Deck' in deck_df.columns:
            if deck_colors is None:
                deck_names = deck_df['Deck'].unique()
                deck_colors = {d: get_random_color() for d in deck_names}
            else:
                for deck_name in deck_df['Deck'].unique():
                    if deck_name not in deck_colors:
                        deck_colors[deck_name] = get_random_color()

            styled_df = (
                styled_df
                    .map(highlight_deck_names, subset=['Deck'])
                    .map(highlight_games, subset=['Games'])
                    .map(highlight_winrate, subset=['Winrate'])
            )
        else:
            # No Deck column; just apply games and winrate highlights
            styled_df = (
                styled_df
                    .map(highlight_games, subset=['Games'])
                    .map(highlight_winrate, subset=['Winrate'])
            )

        # Apply streak coloring if the column exists
        if 'Streak' in deck_df.columns:
            styled_df = styled_df.map(highlight_streak, subset=['Streak'])

    return styled_df, deck_colors


def transform_pct_string(percent: float, extra_padding=0, return_color=False):
    if isinstance(percent, str):
        frequency_string = f"    {percent}%"
        if return_color:
            return frequency_string, 'plain'
        return frequency_string

    if percent == 100:
        frequency_string = f"{percent}%"
    elif percent < 10:
        frequency_string = f"  {percent}%"
    else:
        frequency_string = f" {percent}%"

    for _ in range(extra_padding):
        frequency_string = " " + frequency_string

    if return_color:
        color = 'hero' if percent >= 50 else 'villain'
        return frequency_string, color
    return frequency_string


@st.dialog("Add Alliance", width='large')
def add_alliance_modal(player_deck=True):
    alliances = database.get_user_alliances(st.session_state.name)
    st.markdown(f'<p class="deck-font">New</p>', unsafe_allow_html=True)
    p_cols = st.columns([4, 3, 1], vertical_alignment='bottom')
    alliance_name = p_cols[0].text_input('Name')
    alliance_deck_link = p_cols[1].text_input('DoK Link')
    if p_cols[2].button("➤", key='submit_new_alliance_player'):
        success, message = database.add_alliance_deck(st.session_state.game_id, alliance={'name': alliance_name, 'link': alliance_deck_link}, player=st.session_state.name, player_deck=player_deck)
        icon = ':material/check:' if success else '❌'
        st.toast(message, icon=icon)
        st.rerun()

    st.divider()
    st.markdown(f'<p class="deck-font">Existing</p>', unsafe_allow_html=True)
    p_cols = st.columns([7, 1], vertical_alignment='bottom')
    alliance_name = p_cols[0].selectbox('Alliance', options=alliances['alliance'], index=None, placeholder='Select Alliance')
    if p_cols[1].button("➤", key='submit_old_alliance_player'):
        alliance_deck_link = alliances.loc[alliances['alliance'] == alliance_name, 'link'].iat[0]
        success, message = database.update_alliance_deck(st.session_state.game_id, alliance=alliance_name, alliance_link=alliance_deck_link, player_deck=player_deck)
        if success:
            st.toast(message, icon='✔')
            st.rerun()
        else:
            st.toast(message, icon='❌')

    st.divider()
    st.markdown(f'<p class="deck-font">Identify</p>', unsafe_allow_html=True)
    b_cols = st.columns(4)
    if b_cols[0].button("Find Pods"):
        g_log = st.session_state.game_data['Game Log'][0]
        if player_deck:
            c_played = g_log[st.session_state.game_data['Player'][0]]['individual_cards_played'][-1].keys()
        else:
            c_played = g_log[st.session_state.game_data['Opponent'][0]]['individual_cards_played'][-1].keys()
        houses_played = {}
        house_cards = {}
        for c in c_played:
            house = dok_api.get_card_house(c)
            if house in houses_played:
                houses_played[house] += 1
                house_cards[house].append(c)
            elif house != 'Special':
                houses_played[house] = 1
                house_cards[house] = [c]

        top_houses = [k for k, _ in sorted(houses_played.items(), key=lambda item: item[1], reverse=True)[:3]]
        for i, h in enumerate(top_houses):
            base_link = "https://decksofkeyforge.com/decks?"
            for c in house_cards[h]:
                base_link += f"cards={c.replace(' ', '%20')}-1&"
            base_link = base_link[:-1]
            b_cols[i + 1].link_button(h, url=base_link)

    st.write('')
