import streamlit as st
import pandas as pd

import database
import graphing


def subtract_dicts(old_dict, new_dict):
    # Subtract values from the new dict based on the old dict
    result = {}
    for key, value in new_dict.items():
        if key in old_dict:
            difference = value - old_dict[key]
            if difference > 0:
                result[key] = difference
        else:
            result[key] = value
    return result


try:
    st.set_page_config(
        page_title="Analysis - KeyTracker",
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
.game-data-font {
    font-size: 28px !important;
    color: #424242 !important;
}
.plain-font {
    font-size: 24px !important;
}
.hero-font {
    font-size: 24px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 24px !important;
    color: #ff4b4b !important;
}
.amber-font {
    font-size: 24px !important;
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

game_id = None
if 'game' in st.query_params:
    game_id = st.query_params.get_all(key='game')[0]


if 'game_id' in st.session_state:
    game_id = st.session_state.game_id
    st.query_params['game'] = game_id


def pull_game_data(gid):
    st.session_state.game_data = database.get_game(gid)

if game_id:
    pull_game_data(game_id)

if 'game_data' not in st.session_state:
    st.error("No game selected")
else:
    c1, c2, c3, c4 = st.columns([22, 1, 1, 1])
    c1.markdown(f'<b class="game-data-font">{st.session_state.game_data["Date"][0]}</b>', unsafe_allow_html=True)

    featured = database.check_featured(game_id)
    if 'name' in st.session_state and st.session_state.name and featured:
        like_game = c2.button("💙")
        if like_game:
            status, message = database.like_game(game_id, st.session_state.name)
            if status:
                st.success(message)
            else:
                st.error(message)

    home = c3.button("↩")
    if home:
        st.switch_page("Home.py")
    st.write('')
    c1, c2 = st.columns([7, 1])
    c1.markdown(f'<b class="deck-font">{st.session_state.game_data["Deck"][0]}</b>', unsafe_allow_html=True)
    c2.link_button("Deck Info", st.session_state.game_data["Deck Link"][0])
    st.write('vs')
    c1, c2 = st.columns([7, 1])
    c1.markdown(f'<b class="deck-font">{st.session_state.game_data["Opponent Deck"][0]}</b>', unsafe_allow_html=True)
    c2.link_button("Deck Info", st.session_state.game_data["Opponent Deck Link"][0])
    st.divider()
    c1, c2, c3 = st.columns(3)

    c1.subheader("Opponent")
    c2.subheader("First Player")
    c3.subheader("Winner")
    player = st.session_state.game_data['Player'][0]
    opponent = st.session_state.game_data['Opponent'][0]
    starting_player = st.session_state.game_data['Starting Player'][0]
    if starting_player == opponent:
        second_player = player
    elif starting_player == player:
        second_player = opponent
    else:
        second_player = None
    winner = st.session_state.game_data['Winner'][0]
    c1.markdown(f'<b class="villain-font">{opponent}</b>', unsafe_allow_html=True)
    if starting_player == player:
        c2.markdown(f'<b class="hero-font">{starting_player}</b>', unsafe_allow_html=True)
    else:
        c2.markdown(f'<b class="villain-font">{starting_player}</b>', unsafe_allow_html=True)
    if winner == player:
        c3.markdown(f'<b class="hero-font">{winner}</b>', unsafe_allow_html=True)
    else:
        c3.markdown(f'<b class="villain-font">{winner}</b>', unsafe_allow_html=True)
    st.write(' ')
    st.write(' ')
    st.write(' ')

    game_df, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, player_card_data, opponent_card_data = graphing.analyze_game(player, st.session_state.game_data)
    if not game_df.empty:
        length = len(game_df) - 1
        game_df['Actual'] = (length - pd.Series(game_df.index)) / 2
    c1, c2 = st.columns(2)
    c1.subheader("Total Amber Value")
    c1.line_chart(
        game_df,
        x=None,
        y=['Player Amber', 'Opponent Amber'],
        x_label='Turn',
        y_label='Amber Value',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Total Cards Played")
    c2.line_chart(
        game_df,
        x=None,
        y=['Player Cards', 'Opponent Cards'],
        x_label='Turn',
        y_label='Cards Played',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Prediction")
    if winner == player:
        actual_color = (96, 180, 255, 0.5)
    elif winner == opponent:
        actual_color = (255, 75, 75, 0.5)
    else:
        actual_color = (248, 223, 101, 0.5)

    c1.line_chart(
        game_df,
        x=None,
        y=['Actual', 'Player Prediction', 'Opponent Prediction'],
        x_label='Turn',
        y_label='Turns to Win',
        color=[actual_color, (255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Creatures")
    c2.line_chart(
        game_df,
        x=None,
        y=['Player Creatures', 'Opponent Creatures'],
        x_label='Turn',
        y_label='Creatures',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Amber Delta")
    c1.line_chart(
        game_df,
        x=None,
        y=['Player Delta', 'Opponent Delta'],
        x_label='Turn',
        y_label='Delta',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Reap Rate")
    c2.line_chart(
        game_df,
        x=None,
        y=['Player Reap Rate', 'Opponent Reap Rate'],
        x_label='Turn',
        y_label='Reap Rate',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Player Amber Sources")
    c1.plotly_chart(player_amber_sources, use_container_width=True)
    c2.subheader("Opponent Amber Sources")
    c2.plotly_chart(opponent_amber_sources, use_container_width=True)

    c1.subheader("Player House Calls")
    c1.plotly_chart(player_house_calls, use_container_width=True)
    c2.subheader("Opponent House Calls")
    c2.plotly_chart(opponent_house_calls, use_container_width=True)

    st.subheader("Card Data")
    with st.expander(r"$\textsf{\large Player Card Data}$"):
        st.dataframe(player_card_data, hide_index=True)

    with st.expander(r"$\textsf{\large Opponent Card Data}$"):
        st.dataframe(opponent_card_data, hide_index=True)

    if 'expand_all' not in st.session_state:
        st.session_state.expand_all = False

    def expand_turns():
        if not st.session_state.expand_all:
            st.session_state.expand_all = True
        else:
            st.session_state.expand_all = False

    st.write('')
    c1, c2 = st.columns([9, 1])
    c1.subheader("Turns")
    c2.button("Expand All", on_click=expand_turns)

    link_base = "https://keyforge-card-images.s3-us-west-2.amazonaws.com/card-imgs/"

    game_log = st.session_state.game_data['Game Log'][0]

    for t in range(len(game_log[starting_player]['cards_played'])):
        if t % 2 == 0:
            p = starting_player
        else:
            p = second_player
        turn_string = f"{t}: Turn {round((t+1.1)/2)} - {p}"
        with st.expander(fr"$\texttt{{\large {turn_string}}}$", expanded=st.session_state.expand_all):
            c1, c2, c3 = st.columns(3)
            keys = game_log[p]['keys'][t]
            new_keys = max(keys - game_log[p]['keys'][t-1], 0)

            if p == player:
                c1.markdown(f'<b class="hero-font">Keys: {keys} (+{new_keys})</b>', unsafe_allow_html=True)
            else:
                c1.markdown(f'<b class="villain-font">Keys: {keys} (+{new_keys})</b>', unsafe_allow_html=True)

            total_amber_gained = game_log[p]['amber_icons'][t] + game_log[p]['amber_reaped'][t] + game_log[p]['steal'][t] + game_log[p]['amber_effect'][t]

            if t < 2:
                amber_gained_turn = total_amber_gained
            else:
                last_amber_gained = game_log[p]['amber_icons'][t-1] + game_log[p]['amber_reaped'][t-1] + game_log[p]['steal'][t-1] + game_log[p]['amber_effect'][t-1]
                amber_gained_turn = total_amber_gained - last_amber_gained

            c2.markdown(f'<b class="amber-font">Amber: {game_log[p]["amber"][t]} (+{amber_gained_turn})</b>', unsafe_allow_html=True)

            hands = st.session_state.game_data['Game Log'][0]['player_hand']
            player_boards = st.session_state.game_data['Game Log'][0][player]['board']
            opponent_boards = st.session_state.game_data['Game Log'][0][opponent]['board']
            if 'artifacts' in st.session_state.game_data['Game Log'][0][player]:
                player_artifacts = st.session_state.game_data['Game Log'][0][player]['artifacts']
                opponent_artifacts = st.session_state.game_data['Game Log'][0][opponent]['artifacts']
            else:
                player_artifacts = [[] for _ in range(len(player_boards))]
                opponent_artifacts = [[] for _ in range(len(opponent_boards))]
            cards_played = st.session_state.game_data['Game Log'][0][p]['individual_cards_played']
            cards_played_turn = cards_played[t]
            if t < 2:
                new_cards_played = cards_played_turn
            else:
                new_cards_played = subtract_dicts(cards_played[t-1], cards_played_turn)

            cards_discarded = st.session_state.game_data['Game Log'][0][p]['individual_cards_discarded']
            cards_discarded_turn = cards_discarded[t]
            if t < 2:
                new_cards_discarded = cards_discarded_turn
            else:
                new_cards_discarded = subtract_dicts(cards_discarded[t - 1], cards_discarded_turn)

            remove_chars = "æ””“!,.-…’'éĕŏăŭĭ"

            if p == player:
                st.subheader("Player Hand")
                cols = st.columns(max(11, len(hands[max(t-1, 0)])))

                for i, card in enumerate(hands[max(t-1, 0)]):
                    translation_table = str.maketrans('', '', remove_chars)
                    link_name = card.lower().translate(translation_table).replace(' ', '-')
                    image_link = f"{link_base}{link_name}.png"
                    cols[i].image(image_link)

                st.divider()

            if sum(new_cards_played.values()) > 0 and sum(new_cards_discarded.values()) > 0 and sum(new_cards_played.values()) + sum(new_cards_discarded.values()) <= 10:
                if sum(new_cards_played.values()) <= 5 and sum(new_cards_discarded.values()) <= 5:
                    card_split_ratio = 6
                elif sum(new_cards_played.values()) > 5:
                    card_split_ratio = sum(new_cards_played.values()) + 1
                else:
                    card_split_ratio = 11-sum(new_cards_discarded.values())

                c1, c2 = st.columns([card_split_ratio, 11-card_split_ratio])
                c1.subheader("Cards Played")
                c2.subheader("Discards")

                cols = st.columns(11)
                last_column = 0
                for card, copies in new_cards_played.items():
                    for _ in range(copies):
                        translation_table = str.maketrans('', '', remove_chars)
                        link_name = card.lower().translate(translation_table).replace(' ', '-')
                        image_link = f"{link_base}{link_name}.png"
                        cols[last_column].image(image_link)
                        if last_column < card_split_ratio-1:
                            last_column += 1
                        else:
                            last_column = 0
                last_column = card_split_ratio
                for card, copies in new_cards_discarded.items():
                    for _ in range(copies):
                        translation_table = str.maketrans('', '', remove_chars)
                        link_name = card.lower().translate(translation_table).replace(' ', '-')
                        image_link = f"{link_base}{link_name}.png"
                        cols[last_column].image(image_link)
                        if last_column < 10:
                            last_column += 1
                        else:
                            last_column = card_split_ratio
            if sum(new_cards_played.values()) > 0 and (sum(new_cards_played.values()) + sum(new_cards_discarded.values()) > 10 or sum(new_cards_discarded.values()) == 0):
                st.subheader("Cards Played")

                cols = st.columns(11)
                last_column = 0
                for card, copies in new_cards_played.items():
                    for _ in range(copies):
                        translation_table = str.maketrans('', '', remove_chars)
                        link_name = card.lower().translate(translation_table).replace(' ', '-')
                        image_link = f"{link_base}{link_name}.png"
                        cols[last_column].image(image_link)
                        if last_column < 10:
                            last_column += 1
                        else:
                            last_column = 0

            if sum(new_cards_discarded.values()) > 0 and (sum(new_cards_played.values()) + sum(new_cards_discarded.values()) > 10 or sum(new_cards_played.values()) == 0):
                st.subheader("Discards")

                cols = st.columns(11)
                last_column = 0
                for card, copies in new_cards_discarded.items():
                    for _ in range(copies):
                        translation_table = str.maketrans('', '', remove_chars)
                        link_name = card.lower().translate(translation_table).replace(' ', '-')
                        image_link = f"{link_base}{link_name}.png"
                        cols[last_column].image(image_link)
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

            if len(first_artifact) > 0:
                c_number = max(11, max(len(first_board), 2) + max(len(first_artifact), 2) + 1, max(len(second_board), 2) + max(len(second_artifact), 2) + 1)
            else:
                c_number = max(11, len(first_board), len(second_board))

            for board, artifact, b_name in zip([first_board, second_board], [first_artifact, second_artifact], [fb_name, sb_name]):
                c1, c2 = st.columns([c_number - max(len(artifact), 2), max(len(artifact), 2)])
                if len(board) > 0 or len(artifact) > 0:
                    c1.subheader(b_name)
                if len(artifact) > 0:
                    c2.subheader("Artifacts")
    
                cols = st.columns(c_number)
    
                for i, card in enumerate(board):
                    translation_table = str.maketrans('', '', remove_chars)
                    link_name = card.lower().translate(translation_table).replace(' ', '-')
                    image_link = f"{link_base}{link_name}.png"
                    cols[i].image(image_link)
    
                for j, card in enumerate(artifact):
                    translation_table = str.maketrans('', '', remove_chars)
                    link_name = card.lower().translate(translation_table).replace(' ', '-')
                    image_link = f"{link_base}{link_name}.png"
                    if len(artifact) == 1:
                        cols[c_number-2].image(image_link)
                    else:
                        cols[c_number-len(artifact)+j].image(image_link)