import streamlit as st
import pandas as pd
import numpy as np

import database
import dok_api
import graphing
import calcs
import states
import formatting

try:
    st.set_page_config(
        page_title="Game Analysis - KeyTracker",
        page_icon="🔑",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except:
    pass

st.markdown("""
<style>
.deck-font {
    font-size: 28px !important;
}
.game-data-font {
    font-size: 28px !important;
    color: #424242 !important;
}
.plain-font {
    font-size: 22px !important;
}
.small-font {
    font-size: 12px !important;
}
.hero-font {
    font-size: 22px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 22px !important;
    color: #ff4b4b !important;
}
.hero-title-font {
    font-size: 32px !important;
    color: #60b4ff !important;
}
.villain-title-font {
    font-size: 32px !important;
    color: #ff4b4b !important;
}
.amber-font {
    font-size: 22px !important;
    color: #f8df65 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """, unsafe_allow_html=True)


def pull_game_data(gid):
    with st.spinner('Pulling game data...'):
        st.session_state.game_analysis['game_data'] = database.get_game(gid)
        # === FIX ===
        if 'player_info' in st.session_state.game_analysis:
            del st.session_state['player_info']
        if 'opponent_info' in st.session_state.game_analysis:
            del st.session_state['opponent_info']

if 'user_info' not in st.session_state:
    st.session_state.user_info = {'aliases': []}

game_id = None
if 'game' in st.query_params:
    game_id = st.query_params.get_all(key='game')[0]


if 'game_analysis_id' in st.session_state:
    game_id = st.session_state.game_analysis_id
    st.query_params['game'] = game_id

if 'game_analysis' not in st.session_state or st.session_state.get('game_analysis', {}).get('game_id', None) != game_id:
    st.session_state.game_analysis = {'game_id': game_id}

if 'game_data' not in st.session_state.game_analysis:
    pull_game_data(game_id)
    
game_analysis_dict = st.session_state.game_analysis
game_data = game_analysis_dict['game_data']

if 'game_data' not in game_analysis_dict:
    st.error("No game selected")
elif not game_data:
    st.error("No game data found")
else:
    player = game_data['Player'][0].strip()
    if 'player_info' not in game_analysis_dict:
        game_analysis_dict['player_info'] = database.get_user(player)
    player_icon = states.get_player_icon(game_analysis_dict['player_info'])

    opponent = game_data['Opponent'][0].strip()
    if 'opponent_info' not in game_analysis_dict:
        game_analysis_dict['opponent_info'] = database.get_user(opponent)
    opponent_icon = states.get_player_icon(game_analysis_dict['opponent_info'])

    starting_player = game_data['Starting Player'][0].strip()
    deck = game_data["Deck"][0].strip()

    c1, c2, c3, c4 = st.columns([22, 1, 1, 1])
    c1.markdown(f'<b class="game-data-font">{game_analysis_dict["game_data"]["Date"]}</b>', unsafe_allow_html=True)

    featured = database.check_featured(game_id)
    if 'name' in st.session_state and st.session_state.name and featured:
        if c2.button("💙"):
            status, message = database.like_game(game_id, st.session_state.name)
            if status:
                st.success(message)
            else:
                st.error(message)

    if c3.button("🏠"):
        st.switch_page("Home.py")

    st.write('')
    tab_1, tab_2, tab_3, tab_4 = st.tabs(['Info', 'Summary', 'Advantage', 'Replay'])

    with tab_1:
        c1, c2, c3 = st.columns([1, 11.25, 1.75], vertical_alignment='center')
        c1.image(player_icon)
        c2.markdown(f'<b class="hero-title-font">{player}</b>', unsafe_allow_html=True)
        st.write('')

        format_is_archon = game_data['Format'][0] == 'Archon'
        deck_link = game_data["Deck Link"][0]
        is_current_user = ('name' in st.session_state and st.session_state.name == player) or ('aliases' in states.get_user_aliases(st.session_state) and player in st.session_state['user_info']['aliases'])

        c1, c2 = st.columns([7, 1])
        c1.markdown(f'<b class="deck-font">{deck}</b>', unsafe_allow_html=True)

        if deck_link and deck_link != "https://decksofkeyforge.com/":
            c2.link_button("Deck Info", deck_link)
        elif is_current_user:
            if not format_is_archon:
                if c2.button("Add Alliance", key='p_add_alliance'):
                    formatting.add_alliance_modal()
            else:
                with c2.popover("Add Deck"):
                    st.write("Paste Deck Link")
                    p_cols = st.columns([3, 1])
                    p_deck_link = p_cols[0].text_input("", key='p_deck_link', label_visibility='collapsed')
                    if p_cols[1].button("➤", key='submit_p_deck'):
                        deck_code = p_deck_link.split('/')[-1]
                        if len(deck_code) == 36 and all(deck_code[i] == '-' for i in [8, 13, 18, 23]):
                            dok_data = database.get_dok_cache_deck_id(deck_code)
                            if database.update_game_decks(st.session_state.game_analysis_id, dok_data['Deck'], "https://decksofkeyforge.com/decks/" + dok_data['ID']):
                                st.success(f"Deck Updated: {dok_data['Deck']}")
                                st.rerun()
                            else:
                                st.error(f"Error Updating Deck Info")
                        else:
                            st.error(f"Invalid Deck Code: {deck_code}")

        st.write('vs')
        c1, c2 = st.columns([7, 1])
        c1.markdown(f'<b class="deck-font">{game_data["Opponent Deck"][0]}</b>', unsafe_allow_html=True)

        deck_link = game_data["Opponent Deck Link"][0]

        if deck_link and deck_link != "https://decksofkeyforge.com/":
            c2.link_button("Deck Info", deck_link)
        elif is_current_user:
            if not format_is_archon:
                if c2.button("Add Alliance", key='op_add_alliance'):
                    formatting.add_alliance_modal(player_deck=False)
            else:
                with c2.popover("Add Deck"):
                    st.write("Paste Deck Link")
                    p_cols = st.columns([3, 1])
                    p_deck_link = p_cols[0].text_input("", key='op_deck_link', label_visibility='collapsed')
                    if p_cols[1].button("➤", key='submit_op_deck'):
                        deck_code = p_deck_link.split('/')[-1]
                        if len(deck_code) == 36 and all(deck_code[i] == '-' for i in [8, 13, 18, 23]):
                            dok_data = database.get_dok_cache_deck_id(deck_code)
                            if database.update_game_decks(st.session_state.game_analysis_id, dok_data['Deck'], "https://decksofkeyforge.com/decks/" + dok_data['ID'], player=False):
                                st.success(f"Deck Updated: {dok_data['Deck']}")
                                st.rerun()
                            else:
                                st.error(f"Error Updating Deck Info")
                        else:
                            st.error(f"Invalid Deck Code: {deck_code}")

        st.write('')
        c1, c2 = st.columns([1, 13], vertical_alignment='center')
        c1.image(opponent_icon)
        c2.markdown(f'<b class="villain-title-font">{opponent}</b>', unsafe_allow_html=True)
        st.divider()
        c1, c2, c3 = st.columns(3)

        c1.subheader("First Player")
        c2.subheader("Keys")
        c3.subheader("Winner")
        second_player = player if starting_player == opponent else opponent

        game_log = game_data['Game Log'][0]

        winner = game_data['Winner'][0]

        if starting_player == player:
            c1.markdown(f'<b class="hero-font">{starting_player}</b>', unsafe_allow_html=True)
        else:
            c1.markdown(f'<b class="villain-font">{starting_player}</b>', unsafe_allow_html=True)

        c2.markdown(f'<b class="hero-font">{game_log[player]["keys"][-1]}</b><b class="plain-font">-</b><b class="villain-font">{game_log[opponent]["keys"][-1]}</b>', unsafe_allow_html=True)

        if winner != player and winner != opponent:
            if 'name' in st.session_state and (st.session_state.name == game_data['Player'][0]) or ('aliases' in st.session_state['user_info'] and game_data['Player'][0] in st.session_state['user_info']['aliases']):
                with c3.popover('Add Winner'):
                    st.write("Select Winner")
                    p_cols = st.columns([3, 1])
                    new_winner = p_cols[0].selectbox("", [player, opponent], label_visibility='collapsed')
                    if p_cols[1].button("➤", key='submit_winner'):
                        if database.update_game_winner(st.session_state.game_analysis_id, new_winner):
                            st.success(f"Winner Updated: {new_winner}")
                            game_data['Winner'][0] = new_winner
                            winner = new_winner
                            st.rerun()
                        else:
                            st.error(f"Error Updating Winner Info")

        elif winner == player:
            c3.markdown(f'<b class="hero-font">{winner}</b>', unsafe_allow_html=True)
        elif winner == opponent:
            c3.markdown(f'<b class="villain-font">{winner}</b>', unsafe_allow_html=True)

    st.write(' ')
    st.write(' ')
    st.write(' ')
    game_df, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, advantage_charts, player_card_data, opponent_card_data = graphing.analyze_game(player, game_data)
    if not game_df.empty:
        length = len(game_df) - 1
        game_df['Actual'] = (length - pd.Series(game_df.index)) / 2
        game_df['Amber Advantage'] = game_df['Player Amber'] - game_df['Opponent Amber']
        game_df['Player Amber Advantage'] = game_df['Amber Advantage'].apply(lambda x: max(0, x))
        game_df['Opponent Amber Advantage'] = game_df['Amber Advantage'].apply(lambda x: max(0, x))
        game_df['Player Prediction'].replace(to_replace=25, value=pd.NA, inplace=True)
        game_df['Opponent Prediction'].replace(to_replace=25, value=pd.NA, inplace=True)

    with tab_2:
        c1, c2 = st.columns(2)

        actual_color = (96, 180, 255, 0.5) if winner == player else (255, 75, 75, 0.5) if winner == opponent else (248, 223, 101, 0.5)

        base_colors = [(255, 75, 75), (96, 180, 255)]
        prediction_colors = [actual_color] + base_colors

        chart_dict = {
            "Total Amber Value": {
                'y_values': ['Player Amber', 'Opponent Amber'],
                'y_label': 'Amber Value',
                'color': base_colors,
                'tooltip': "**Total Amber Value** is a representation of a player's total progress in the game. It is calculated using the following formula:\n\n*Amber Value = Keys * 6 + Amber*",
            },
            "Total Cards Played": {
                'y_values': ['Player Cards', 'Opponent Cards'],
                'y_label': 'Cards Played',
                'color': base_colors,
                'tooltip': "The total number of cards played by each player.",
            },
            "Prediction": {
                'y_values': ['Actual', 'Player Prediction', 'Opponent Prediction'],
                'y_label': 'Turns to Win',
                'color': prediction_colors,
                'tooltip': "**Predictions** are made by using a combination of **Amber Value**, **Amber Delta**, and **Reap Rate** to estimate each player's **Turns to Win**. It is calculated using the following formula:\n\n*Amber Remaining = Keys Remaining * Key Cost - Amber*\n\n*Amber Generation = Amber Delta + Creatures * Reap Rate*\n\n*Turns to Win = Amber Remaining / Amber Generation*",
            },
            "Creatures": {
                'y_values': ['Player Creatures', 'Opponent Creatures'],
                'y_label': 'Creatures',
                'color': base_colors,
                'tooltip': "The total number of creatures on the board for each player.",
            },
            "Amber Delta": {
                'y_values': ['Player Delta', 'Opponent Delta'],
                'y_label': 'Delta',
                'color': base_colors,
                'tooltip': "**Amber Delta** is the average amount of Amber gained per turn **NOT from reaping**. It is calculated using the following formula:\n\n*Amber Delta = (Amber Gained - Amber Reaped) / Turns*",
            },
            "Reap Rate": {
                'y_values': ['Player Reap Rate', 'Opponent Reap Rate'],
                'y_label': 'Reap Rate (%)',
                'color': base_colors,
                'tooltip': "**Reap Rate** is the average rate at which a player reaps with creatures they have on the board. It is calculated using the following formula:\n\n*Reap Rate = Average reaps per turn / Average creatures per turn*",
            },
            "Amber Defense": {
                'y_values': ['Player Amber Defense', 'Opponent Amber Defense'],
                'y_label': 'Amber Defense (%)',
                'color': base_colors,
                'tooltip': "**Amber Defense** is the average amount of Amber ‘removed’ from your opponent, or the inverse of how much Amber your opponent retains. An Amber Defense of 30 implies that 30% of the Amber that your opponent generates is lost. It is calculated using the following formula:\n\n*Amber Defense = 1 - Opponent Amber Value / Opponent Amber Gained*",
            },
            "Creature Survival Rate": {
                'y_values': ['Player Survival Rate', 'Opponent Survival Rate'],
                'y_label': 'Survival Rate (%)',
                'color': base_colors,
                'tooltip': "**Survival Rate** is the average rate at which a player’s creatures stay on the field. A Survival Rate of 80 suggests that a creature on the board has an 80% chance of surviving until the next turn. It is calculated using the following formula:\n\n*Survival Rate = Turns Survived / (Turns Survived + Turns Killed)*",
            },
            "Forge Through Rate": {
                'y_values': ['Player Forge Rate', 'Opponent Forge Rate'],
                'y_label': 'Forge Through Rate %',
                'color': base_colors,
                'tooltip': "**Forge Through Rate** is the average rate at which a player’s checks resolve as forged keys. A Forge Through Rate of 80 suggests that 80% of the time when the player checks, they will successfully forge on their next turn. It is calculated using the following formula:\n\n*Forge Through Rate = Keys Forged / Keys Checked*",
            }
        }

        if 'Player Tokens' in game_df.columns and 'Opponent Tokens' in game_df.columns and (game_df['Player Tokens'].gt(0).any() or game_df['Opponent Tokens'].gt(0).any()):
            chart_dict["Tokens Generated"] = {
                'y_values': ['Player Tokens', 'Opponent Tokens'],
                'y_label': 'Tokens',
                'color': base_colors,
                'tooltip': "The number of token creatures generated by each player.",
            }
        elif 'Player Tokens' in game_df.columns and game_df['Player Tokens'].gt(0).any():
            chart_dict["Tokens Generated"] = {
                'y_values': ['Player Tokens'],
                'y_label': 'Tokens',
                'color': base_colors,
                'tooltip': "The number of token creatures generated by each player.",
            }
        elif 'Opponent Tokens' in game_df.columns and game_df['Opponent Tokens'].gt(0).any():
            chart_dict["Tokens Generated"] = {
                'y_values': ['Opponent Tokens'],
                'y_label': 'Tokens',
                'color': base_colors,
                'tooltip': "The number of token creatures generated by each player.",
            }
        elif 'Tide' in game_df.columns:
            chart_dict["Tide"] = {
                'y_values': ['Tide'],
                'y_label': 'Tide',
                'color': [(96, 180, 255)],
                'tooltip': "The tide value (1 is high for the player, -1 is low for the player, 0 is neutral).",
            }
        elif 'Player Archives' in game_df.columns and 'Opponent Archives' in game_df.columns and (game_df['Player Archives'].gt(0).any() or game_df['Opponent Archives'].gt(0).any()):
            chart_dict["Archives"] = {
                'y_values': ['Player Archives', 'Opponent Archives'],
                'y_label': 'Archives',
                'color': base_colors,
                'tooltip': "The number of cards in each players archives."
            }
        elif 'Player Discard' in game_df.columns and 'Opponent Discard' in game_df.columns and (game_df['Player Discard'].gt(0).any() or game_df['Opponent Discard'].gt(0).any()):
            chart_dict["Discard Pile"] = {
                'y_values': ['Player Discard', 'Opponent Discard'],
                'y_label': 'Discard Pile',
                'color': base_colors,
                'tooltip': "The number of cards in each players discard."
            }

        game_df = game_df.replace({None: np.nan})

        for i, chart in enumerate(chart_dict.keys()):
            col = c1 if i % 2 == 0 else c2

            tooltip = chart_dict[chart].get('tooltip', "")

            col.subheader(chart, help=tooltip)
            try:
                col.line_chart(
                    game_df,
                    x=None,
                    y=chart_dict[chart]['y_values'],
                    x_label='Turn',
                    y_label=chart_dict[chart]['y_label'],
                    color=chart_dict[chart]['color']
                )
            except:
                col.error(f"Error plotting chart: {chart}")

        c1, c2 = st.columns(2)
        c1.subheader("Player Amber Sources")
        c1.plotly_chart(player_amber_sources, use_container_width=True)
        c2.subheader("Opponent Amber Sources")
        c2.plotly_chart(opponent_amber_sources, use_container_width=True)

        c1.subheader("Player House Calls")
        c1.image(player_house_calls)
        c2.subheader("Opponent House Calls")
        c2.image(opponent_house_calls)

        for card_data in [player_card_data, opponent_card_data]:
            for stat in ['Discarded %', 'Amber %', 'Survival %']:
                card_data[stat] = card_data[stat].apply(lambda x: x / 100 if isinstance(x, (int, float)) else x)
            card_data['Image'] = card_data['Card'].apply(lambda x: dok_api.get_card_image(x))

        df_col_config = {
            "Image": st.column_config.ImageColumn(pinned=True, width='small'),
            "Turn": st.column_config.Column(help="The turn a card was first played"),
            "Played": st.column_config.Column(help="The number of times a card was played"),
            # "Discarded": st.column_config.Column(help="The number of times a card was discarded"),
            # "Discarded %": st.column_config.NumberColumn(help="The percentage of times a card was discarded vs played", format='percent'),
            "Amber": st.column_config.Column(help="The amount of amber gained from a card"),
            "Amber %": st.column_config.ProgressColumn(help="The percentage of total amber gained from a card", format='percent', width='medium'),
            "Reaps": st.column_config.Column(help="The number of times a card reaped"),
            "Icons": st.column_config.Column(help="The amount of amber icons gained from a card"),
            "Steal": st.column_config.Column(help="The amount of amber stolen with a card"),
            "Effects": st.column_config.Column(help="The amount of amber gained from a card's effects"),
            "Survival %": st.column_config.NumberColumn(help="The likelihood a creature survives on the board until the next turn", format='percent'),
        }

        card_data_cols = ['Image', 'Card', 'Turn', 'Played', 'Amber', 'Reaps', 'Icons', 'Steal', 'Effects', 'Amber %']

        st.subheader("Card Data")
        with st.expander(r"$\textsf{\large Player Card Data}$"):
            st.dataframe(player_card_data[card_data_cols], hide_index=True, column_config=df_col_config)

        with st.expander(r"$\textsf{\large Opponent Card Data}$"):
            st.dataframe(opponent_card_data[card_data_cols], hide_index=True, column_config=df_col_config)

    with tab_3:
        c1, c2 = st.columns(2)

        advantage_stats = ['Amber', 'Cards', 'Prediction', 'Creatures', 'Delta', 'Reap Rate', 'Amber Defense', 'Survival Rate']
        advantage_chart_list = [f'{s} Advantage' for s in advantage_stats]

        for i, advantage in enumerate(advantage_chart_list):
            if i % 2 == 0:
                col = c1
            else:
                col = c2

            col.subheader(advantage)
            col.plotly_chart(advantage_charts[i])

    with tab_4:
        if 'expand_all' not in st.session_state.game_analysis:
            st.session_state.game_analysis['expand_all'] = False

        def expand_turns():
            st.session_state.game_analysis['expand_all'] = not st.session_state.game_analysis['expand_all']

        st.write('')
        c1, c2 = st.columns([6, 1])
        c1.subheader("Turns")
        exp_button_string = "Collapse All" if st.session_state.game_analysis['expand_all'] else "Expand All"
        c2.button(exp_button_string, on_click=expand_turns)

        if ["Key ", " phase -  ", opponent] in game_data['Player Frags'][0]:
            opponent_messages = game_data['Player Frags'][0]
            player_messages = game_data['Opponent Frags'][0]
        else:
            player_messages = game_data['Player Frags'][0]
            opponent_messages = game_data['Opponent Frags'][0]

        card_name_list = dok_api.card_df['cardTitle'].tolist()
        card_image_dict = dok_api.card_df.set_index('cardTitle')['cardTitleUrl'].to_dict()
        card_image_dict = {key.replace("'", "").replace("’", ""): value for key, value in card_image_dict.items()}

        for t in range(len(game_log[starting_player]['cards_played'])):
            p = starting_player if t % 2 == 0 else second_player
            turn_num = round((t + 1.1) / 2)
            turn_opponent_prediction = game_df.loc[t, 'Opponent Prediction']
            turn_player_prediction = game_df.loc[t, 'Player Prediction']
            this_turn_advantage = turn_opponent_prediction - turn_player_prediction
            if t > 0:
                last_turn_opponent_prediction = game_df.loc[t-1, 'Opponent Prediction']
                last_turn_player_prediction = game_df.loc[t-1, 'Player Prediction']
                last_turn_advantage = last_turn_opponent_prediction - last_turn_player_prediction
            else:
                last_turn_opponent_prediction = 25
                last_turn_player_prediction = 25
                last_turn_advantage = 0

            unreliable_turn_advantage = False
            if any(pd.isna(val) for val in [turn_opponent_prediction, turn_player_prediction, last_turn_opponent_prediction, last_turn_player_prediction]):
                unreliable_turn_advantage = True

            turn_score = this_turn_advantage - last_turn_advantage
            if p != player:
                turn_score *= -1
            if t > 0:
                # turn_string = f"{t}: Turn {turn_num} - {p} ({'+' if turn_score > 0 else ''}{round(turn_score, 1)}) ({round(game_df.loc[t, 'Opponent Prediction'], 1)} - {round(game_df.loc[t, 'Player Prediction'], 1)}) - ({round(game_df.loc[t - 1, 'Opponent Prediction'], 1)} - {round(game_df.loc[t - 1, 'Player Prediction'], 1)})"
                if unreliable_turn_advantage:
                    turn_string = f"{t}: Turn {turn_num} - {p}"
                else:
                    turn_string = f"{t}: Turn {turn_num} - {p} ({'+' if turn_score > 0 else ''}{round(turn_score, 1)})" #[{round(game_df.loc[t, 'Opponent Prediction'] - game_df.loc[t, 'Player Prediction'], 1)}]"
            else:
                turn_string = f"{t}: Turn {turn_num} - {p}"

            if player_messages is not None:
                p_messages = player_messages if p == player else opponent_messages if p == opponent else None

                search_frags = [f"Turn {turn_num} -  ", p]

                try:
                    m_start_index = p_messages.index(search_frags)
                except:
                    m_start_index = None

                if t == 0:
                    m_start_index = 0

                if m_start_index is not None:
                    search_frags = [f"Turn {turn_num+1} -  ", p]
                    try:
                        m_finish_index = p_messages.index(search_frags)-2
                    except:
                        m_finish_index = -1
                else:
                    m_finish_index = None

            else:
                m_start_index = None

            with st.expander(fr"$\texttt{{\large {turn_string.replace('_', ' ')}}}$", expanded=st.session_state.game_analysis['expand_all']):
                cols = st.columns([1.1, 1.1, 0.9, 0.8, 1, 1, 1])
                keys = game_log[p]['keys'][t]
                new_keys = max(keys - game_log[p]['keys'][t-1], 0)

                if p == player:
                    cols[0].markdown(f'<b class="hero-font">Keys: {keys} (+{new_keys})</b>', unsafe_allow_html=True)
                else:
                    cols[0].markdown(f'<b class="villain-font">Keys: {keys} (+{new_keys})</b>', unsafe_allow_html=True)

                total_amber_gained = game_log[p]['amber_icons'][t] + game_log[p]['amber_reaped'][t] + game_log[p]['steal'][t] + game_log[p]['amber_effect'][t]

                if t < 2:
                    amber_gained_turn = total_amber_gained
                else:
                    last_amber_gained = game_log[p]['amber_icons'][t-1] + game_log[p]['amber_reaped'][t-1] + game_log[p]['steal'][t-1] + game_log[p]['amber_effect'][t-1]
                    amber_gained_turn = total_amber_gained - last_amber_gained

                cols[1].markdown(f'<b class="amber-font">Amber: {game_log[p]["amber"][t]} (+{amber_gained_turn})</b>', unsafe_allow_html=True)

                if 'chains' in game_log[p] and game_log[p]['chains'][t] != 0:
                    cols[2].markdown(f'<b class="plain-font">Chains: {game_log[p]["chains"][t]}</b>', unsafe_allow_html=True)

                if 'deck_count' in game_log[p]:
                    cols[3].markdown(f'<b class="plain-font">Deck: {game_log[p]["deck_count"][t]}</b>', unsafe_allow_html=True)

                if 'discard_count' in game_log[p]:
                    cols[4].markdown(f'<b class="plain-font">Discard: {game_log[p]["discard_count"][t]}</b>', unsafe_allow_html=True)

                if 'archives_count' in game_log[p] and game_log[p]['archives_count'][t] != 0:
                    cols[5].markdown(f'<b class="plain-font">Archives: {game_log[p]["archives_count"][t]}</b>', unsafe_allow_html=True)
                    next_col = 6
                else:
                    next_col = 5

                if 'purged_count' in game_log[p] and game_log[p]['purged_count'][t] != 0:
                    cols[next_col].markdown(f'<b class="plain-font">Purge: {game_log[p]["purged_count"][t]}</b>', unsafe_allow_html=True)

                if 'player_hand' in game_data['Game Log'][0]:
                    hands = [[x for x in ls if len(x) != 0] for ls in game_data['Game Log'][0]['player_hand']]
                else:
                    hands = None
                player_boards = [[x for x in ls if len(x) != 0] for ls in game_data['Game Log'][0][player]['board']]
                opponent_boards = [[x for x in ls if len(x) != 0] for ls in game_data['Game Log'][0][opponent]['board']]
                if 'artifacts' in game_data['Game Log'][0][player]:
                    player_artifacts = [[x for x in ls if len(x) != 0] for ls in game_data['Game Log'][0][player]['artifacts']]
                    opponent_artifacts = [[x for x in ls if len(x) != 0] for ls in game_data['Game Log'][0][opponent]['artifacts']]
                else:
                    player_artifacts = [[] for _ in range(len(player_boards))]
                    opponent_artifacts = [[] for _ in range(len(opponent_boards))]

                cards_played = game_data['Game Log'][0][p]['individual_cards_played']
                cards_played_turn = cards_played[t]
                if t < 2:
                    new_cards_played = cards_played_turn
                else:
                    new_cards_played = calcs.subtract_dicts(cards_played[t-1], cards_played_turn)

                cards_discarded = game_data['Game Log'][0][p]['individual_cards_discarded']
                cards_discarded_turn = cards_discarded[t]
                if t < 2:
                    new_cards_discarded = cards_discarded_turn
                else:
                    new_cards_discarded = calcs.subtract_dicts(cards_discarded[t - 1], cards_discarded_turn)

                remove_chars = "[]æ””“*!,.-…’'éĕŏăŭĭ\""

                if p == player and hands:
                    st.markdown(f'<b class="plain-font">Player Hand</b>', unsafe_allow_html=True)
                    cols = st.columns(max(11, len(hands[max(t-1, 0)])))

                    for i, card in enumerate(hands[max(t-1, 0)]):
                        card_title = card.replace("'", "").replace("’", "")
                        if card_title not in card_image_dict:
                            st.toast(f"Card image not found: {card_title}")
                            image_link = None
                        else:
                            image_link = card_image_dict[card_title]
                            try:
                                cols[i].image(image_link)
                            except:
                                st.toast(f"Error getting card image: {image_link}")

                    st.divider()

                if sum(new_cards_played.values()) > 0 and sum(new_cards_discarded.values()) > 0 and sum(new_cards_played.values()) + sum(new_cards_discarded.values()) <= 10:
                    if sum(new_cards_played.values()) <= 5 and sum(new_cards_discarded.values()) <= 5:
                        card_split_ratio = 6
                    elif sum(new_cards_played.values()) > 5:
                        card_split_ratio = sum(new_cards_played.values()) + 1
                    else:
                        card_split_ratio = 11-sum(new_cards_discarded.values())

                    c1, c2 = st.columns([card_split_ratio, 11-card_split_ratio])
                    c1.markdown(f'<b class="plain-font">Cards Played</b>', unsafe_allow_html=True)
                    c2.markdown(f'<b class="plain-font">Discards</b>', unsafe_allow_html=True)

                    cols = st.columns(11)
                    last_column = 0
                    for card, copies in new_cards_played.items():
                        for _ in range(copies):
                            card_title = card.replace("'", "").replace("’", "")
                            if card_title not in card_image_dict:
                                st.toast(f"Card image not found: {card_title}")
                                image_link = None
                            else:
                                image_link = card_image_dict[card_title]
                                try:
                                    cols[last_column].image(image_link)
                                except:
                                    st.toast(f"Error getting card image: {image_link}")
                            if last_column < card_split_ratio-1:
                                last_column += 1
                            else:
                                last_column = 0
                    last_column = card_split_ratio
                    for card, copies in new_cards_discarded.items():
                        for _ in range(copies):
                            card_title = card.replace("'", "").replace("’", "")
                            if card_title not in card_image_dict:
                                st.toast(f"Card image not found: {card_title}")
                                image_link = None
                            else:
                                image_link = card_image_dict[card_title]
                                try:
                                    cols[last_column].image(image_link)
                                except:
                                    st.toast(f"Error getting card image: {image_link}")
                            if last_column < 10:
                                last_column += 1
                            else:
                                last_column = card_split_ratio
                if sum(new_cards_played.values()) > 0 and (sum(new_cards_played.values()) + sum(new_cards_discarded.values()) > 10 or sum(new_cards_discarded.values()) == 0):
                    st.markdown(f'<b class="plain-font">Cards Played</b>', unsafe_allow_html=True)

                    cols = st.columns(11)
                    last_column = 0
                    for card, copies in new_cards_played.items():
                        for _ in range(copies):
                            card_title = card.replace("'", "").replace("’", "")
                            if card_title not in card_image_dict:
                                st.toast(f"Card image not found: {card_title}")
                                image_link = None
                            else:
                                image_link = card_image_dict[card_title]
                                try:
                                    cols[last_column].image(image_link)
                                except:
                                    st.toast(f"Error getting card image: {image_link}")
                            if last_column < 10:
                                last_column += 1
                            else:
                                last_column = 0

                if sum(new_cards_discarded.values()) > 0 and (sum(new_cards_played.values()) + sum(new_cards_discarded.values()) > 10 or sum(new_cards_played.values()) == 0):
                    st.markdown(f'<b class="plain-font">Discards</b>', unsafe_allow_html=True)

                    cols = st.columns(11)
                    last_column = 0
                    for card, copies in new_cards_discarded.items():
                        for _ in range(copies):
                            card_title = card.replace("'", "").replace("’", "")
                            if card_title not in card_image_dict:
                                st.toast(f"Card image not found: {card_title}")
                                image_link = None
                            else:
                                image_link = card_image_dict[card_title]
                                try:
                                    cols[last_column].image(image_link)
                                except:
                                    st.toast(f"Error getting card image: {image_link}")
                            if last_column < 10:
                                last_column += 1
                            else:
                                last_column = 0
                st.divider()

                if p == player:
                    first_board = player_boards[t]
                    second_board = opponent_boards[t]
                    first_artifact = player_artifacts[t]
                    second_artifact = opponent_artifacts[t]
                    fb_name = "Player Board"
                    sb_name = "Opponent Board"
                else:
                    first_board = opponent_boards[t]
                    second_board = player_boards[t]
                    first_artifact = opponent_artifacts[t]
                    second_artifact = player_artifacts[t]
                    fb_name = "Opponent Board"
                    sb_name = "Player Board"

                if 'settings' not in st.session_state or st.session_state.settings['board_layout'] == 'tco':
                    if len(opponent_artifacts[t]) + len(opponent_boards[t]) > 0:
                        st.markdown(f'<b class="plain-font">Opponent Board</b>', unsafe_allow_html=True)
                    with st.container(border=True):
                        c_number = max(11, len(opponent_boards[t]), len(opponent_artifacts[t]))

                        if len(opponent_artifacts[t]) > 0:
                            cols = st.columns(c_number)

                            for i, card in enumerate(opponent_artifacts[t]):
                                card_title = card.replace("'", "").replace("’", "")
                                if card_title not in card_image_dict:
                                    st.toast(f"Card image not found: {card_title}")
                                    image_link = None
                                else:
                                    image_link = card_image_dict[card_title]
                                    cols[i].image(image_link)

                        if len(opponent_boards[t]) > 0:
                            if len(opponent_boards[t]) % 2 == 1:
                                cols = st.columns(c_number)
                                if len(opponent_boards[t]) < c_number:
                                    starting_col = 6 - (len(opponent_boards[t]) + 1) / 2
                                else:
                                    starting_col = 0
                            else:
                                if len(opponent_boards[t]) < c_number:
                                    col_vals = [0.5] + [1 for _ in range(c_number-1)] + [0.5]
                                    cols = st.columns(col_vals)
                                    starting_col = 6 - (len(opponent_boards[t])) / 2
                                else:
                                    col_vals = [0.5] + [1 for _ in range(c_number)] + [0.5]
                                    cols = st.columns(col_vals)
                                    starting_col = 1

                            for i, card in enumerate(opponent_boards[t]):
                                card_title = card.replace("'", "").replace("’", "")
                                if card_title not in card_image_dict:
                                    st.toast(f"Card image not found: {card_title}")
                                    image_link = None
                                else:
                                    image_link = card_image_dict[card_title]
                                    cols[round(i+starting_col)].image(image_link)

                    if len(opponent_artifacts[t]) + len(opponent_boards[t]) == 0 and len(player_artifacts[t]) + len(player_boards[t]) > 0:
                        st.markdown(f'<b class="plain-font">Player Board</b>', unsafe_allow_html=True)

                    with st.container(border=True):
                        c_number = max(11, len(player_boards[t]), len(player_artifacts[t]))

                        if len(player_boards[t]) > 0:
                            c_number = max(11, len(player_boards[t]))
                            if len(player_boards[t]) % 2 == 1:
                                cols = st.columns(c_number)
                                if len(player_boards[t]) < c_number:
                                    starting_col = 6 - (len(player_boards[t]) + 1) / 2
                                else:
                                    starting_col = 0
                            else:
                                if len(player_boards[t]) < c_number:
                                    col_vals = [0.5] + [1 for _ in range(c_number-1)] + [0.5]
                                    cols = st.columns(col_vals)
                                    starting_col = 6 - (len(player_boards[t])) / 2
                                else:
                                    col_vals = [0.5] + [1 for _ in range(c_number)] + [0.5]
                                    cols = st.columns(col_vals)
                                    starting_col = 1

                            for i, card in enumerate(player_boards[t]):
                                card_title = card.replace("'", "").replace("’", "")
                                if card_title not in card_image_dict:
                                    st.toast(f"Card image not found: {card_title}")
                                    image_link = None
                                else:
                                    image_link = card_image_dict[card_title]
                                    cols[round(i+starting_col)].image(image_link)

                        if len(player_artifacts[t]) > 0:
                            c_number = max(11, len(player_artifacts[t]))
                            cols = st.columns(c_number)

                            for i, card in enumerate(player_artifacts[t]):
                                card_title = card.replace("'", "").replace("’", "")
                                if card_title not in card_image_dict:
                                    st.toast(f"Card image not found: {card_title}")
                                    image_link = None
                                else:
                                    image_link = card_image_dict[card_title]
                                    cols[i].image(image_link)

                    if len(opponent_artifacts[t]) + len(opponent_boards[t]) > 0 and len(player_artifacts[t]) + len(player_boards[t]) > 0:
                        st.markdown(f'<b class="plain-font">Player Board</b>', unsafe_allow_html=True)
                else:
                    if len(first_artifact) > 0 or len(second_artifact) > 0:
                        c_number = max(11, max(len(first_board), 2) + max(len(first_artifact), 2) + 1, max(len(second_board), 2) + max(len(second_artifact), 2) + 1)
                    else:
                        c_number = max(11, len(first_board), len(second_board))

                    for board, artifact, b_name in zip([first_board, second_board], [first_artifact, second_artifact], [fb_name, sb_name]):
                        c1, c2 = st.columns([c_number - max(len(artifact), 2), max(len(artifact), 2)])
                        if len(board) > 0 or len(artifact) > 0:
                            c1.markdown(f'<b class="plain-font">{b_name}</b>', unsafe_allow_html=True)
                        if len(artifact) > 0:
                            c2.markdown(f'<b class="plain-font">Artifacts</b>', unsafe_allow_html=True)

                        cols = st.columns(c_number)

                        for i, card in enumerate(board):
                            card_title = card.replace("'", "").replace("’", "")
                            if card_title not in card_image_dict:
                                st.toast(f"Card image not found: {card_title}")
                                image_link = None
                            else:
                                image_link = card_image_dict[card_title]
                                cols[i].image(image_link)

                        for j, card in enumerate(artifact):
                            card_title = card.replace("'", "").replace("’", "")
                            if card_title not in card_image_dict:
                                st.toast(f"Card image not found: {card_title}")
                                image_link = None
                            else:
                                image_link = card_image_dict[card_title]
                                if len(artifact) == 1:
                                    cols[c_number-2].image(image_link)
                                else:
                                    cols[c_number-len(artifact)+j].image(image_link)

                if m_start_index is not None:
                    st.divider()
                    show_messages = st.button("Turn Log", key=f"turn_log_{t}")
                    if show_messages:
                        replacements = {
                            player: f':blue[{player}]',
                            opponent: f':red[{opponent}]',
                            'Æmber': ':orange[Æmber]',
                            'amber': ':orange[amber]',
                        }
                        turn_messages = p_messages[m_start_index:m_finish_index]
                        for msg in turn_messages:
                            if " has reconnected " in msg:
                                pass
                            elif " has connected to the game server " in msg:
                                pass
                            elif " has disconnected.  The game will wait up to 30 seconds for them to reconnect " in msg:
                                pass
                            else:
                                for i in range(len(msg)):
                                    fragment = msg[i]
                                    for old_word, new_word in replacements.items():
                                        if old_word in fragment:
                                            msg[i] = fragment.replace(old_word, new_word)
                                    if fragment.strip() in card_name_list:
                                        msg[i] = f":violet[{fragment}]"
                                joined_message = ''.join(msg)
                                st.write(joined_message)
