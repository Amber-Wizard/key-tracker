import streamlit as st
import pandas as pd
import numpy as np

import database
import graphing
import analysis
import dok_api

house_dict = graphing.house_dict


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
        page_title="Deck Analysis - KeyTracker",
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
.compare-deck-font {
    font-size: 32px !important;
    color: #666666 !important;
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
.small-hero-font {
    font-size: 20px !important;
    color: #60b4ff !important;
}
.small-villain-font {
    font-size: 20px !important;
    color: #ff4b4b !important;
}
.CotA-font {
    font-size: 26px !important;
    color: #d92b34 !important;
}
.AoA-font {
    font-size: 26px !important;
    color: #259adb !important;
}
.WC-font {
    font-size: 26px !important;
    color: #ad39a5 !important;
}
.MM-font {
    font-size: 26px !important;
    color: #e94e76 !important;
}
.DT-font {
    font-size: 26px !important;
    color: #136697 !important;
}
.WoE-font {
    font-size: 26px !important;
    color: #0c9aa8 !important;
}
.GR-font {
    font-size: 26px !important;
    color: #0c4f7f !important;
}
.AES-font {
    font-size: 26px !important;
    color: #f1ebd2 !important;
}
.ToC-font {
    font-size: 26px !important;
    color: #ea2e46 !important;
}
.MMM-font {
    font-size: 26px !important;
    color: #e94e76 !important;
}
.VM23-font {
    font-size: 26px !important;
    color: #838383 !important;
}
.VM24-font {
    font-size: 26px !important;
    color: #838383 !important;
}
.amber-font {
    font-size: 22px !important;
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

deck = None
pilot = None
share_id = None
score = None

if 'shareID' not in st.query_params and 'share_id' in st.session_state:
    st.query_params['shareID'] = st.session_state.share_id

if 'shareID' in st.query_params:
    share_id = st.query_params.get_all(key='shareID')[0]
    if 'share_id' in st.session_state and st.session_state.share_id == share_id:
        pass
    else:
        st.session_state.share_id = share_id
        if 'deck_selection' in st.session_state:
            del st.session_state['deck_selection']
        if 'elo_data' in st.session_state:
            del st.session_state['elo_data']
        if 'deck_games' in st.session_state:
            del st.session_state['deck_games']
        if 'deck_data' in st.session_state:
            del st.session_state['deck_data']

if 'share_id' in st.session_state and 'elo_data' not in st.session_state:
    with st.spinner('Getting ELO...'):
        st.session_state.elo_data = database.get_elo_by_id(st.session_state.share_id)
    st.session_state.deck = st.session_state.elo_data['deck']
    st.session_state.pilot = st.session_state.elo_data['player']
    st.session_state.score = st.session_state.elo_data['score']

if 'deck_games' not in st.session_state:
    if 'pilot' not in st.session_state:
        if 'elo_data' in st.session_state:
            st.session_state.pilot = st.session_state.elo_data['player']
        else:
            st.error(f"Error locating deck pilot.")
            st.session_state.pilot = ''
    pilot = st.session_state.pilot
    deck = st.session_state.deck
    with st.spinner('Getting pilot info...'):
        st.session_state.pilot_info = database.get_user(pilot)
        if 'aliases' not in st.session_state.pilot_info:
            st.session_state.pilot_info['aliases'] = []
    with st.spinner('Getting deck games...'):
        deck_games = database.get_deck_games(pilot, deck, aliases=st.session_state.pilot_info['aliases'], trim_lists=True)
    with st.spinner('Processing games...'):
        st.session_state.deck_games = deck_games
        deck_games['Opponent Deck ID'] = deck_games['Opponent Deck Link'].str.split('/').str[-1]

        # Vectorized retrieval of 'Dok Data' and 'Opponent Set'
        deck_games['Dok Data'] = deck_games['Opponent Deck ID'].apply(database.get_dok_cache_deck_id)

        def get_deck_set(dok_data):
            try:
                return database.set_conversion_dict[dok_data['Data']['deck']['expansion']][0]
            except KeyError:
                return 'Unknown Set'  # Or some default value

        deck_games['Opponent Set'] = deck_games['Dok Data'].apply(lambda dok_data: get_deck_set(dok_data))

        # Calculate winrate by 'Opponent Set' in a vectorized way
        set_winrate_df = deck_games.groupby('Opponent Set').size().reset_index(name='Count')

        # Vectorized 'Wins' calculation
        set_winrate_df['Wins'] = deck_games.groupby('Opponent Set').apply(lambda x: (x['Winner'].isin(st.session_state.pilot_info['aliases'] + [pilot])).sum()).reset_index(drop=True)

        # Calculate winrate in a vectorized way
        set_winrate_df['Winrate'] = (100 * set_winrate_df['Wins'] / set_winrate_df['Count']).round(0).astype(int)

        # Save result to session state
        st.session_state.set_winrate_df = set_winrate_df

        deck_games['Opponent Houses'] = deck_games['Dok Data'].apply(lambda dok_data: [hd['house'] for hd in dok_data['Data']['deck']['housesAndCards']])

        # Step 2: Expand the DataFrame so that each game is associated with each house
        expanded_deck_games = deck_games.explode('Opponent Houses')

        # Group by 'Opponent Houses' and count games
        house_winrate_df = expanded_deck_games.groupby('Opponent Houses').size().reset_index(name='Count')

        # Calculate the number of wins for each house
        house_winrate_df['Wins'] = expanded_deck_games.groupby('Opponent Houses').apply(lambda x: (x['Winner'].isin(st.session_state.pilot_info['aliases'] + [pilot])).sum()).reset_index(drop=True)

        # Calculate winrate for each house
        house_winrate_df['Winrate'] = (100 * house_winrate_df['Wins'] / house_winrate_df['Count']).round(0).astype(int)

        st.session_state.house_winrate_df = house_winrate_df


if 'deck_selection' not in st.session_state:
    if 'pilot' not in st.session_state:
        if 'elo_data' in st.session_state:
            st.session_state.pilot = st.session_state.elo_data['player']
        else:
            st.error(f"Error locating deck pilot.")
            st.session_state.pilot = ''
    pilot = st.session_state.pilot
    deck_games = st.session_state.deck_games
    deck_link = st.session_state.deck_games['Deck Link'].iat[0]
    st.session_state.deck_dok_data = database.get_dok_cache_deck_id(deck_link.split('/')[-1])
    wins = (deck_games['Winner'].isin(st.session_state.pilot_info['aliases'] + [pilot])).sum()
    games = len(deck_games)
    firsts = (deck_games['Starting Player'].isin(st.session_state.pilot_info['aliases'] + [pilot])).sum()
    seconds = games - firsts
    losses = games - wins
    winrate = round(100 * wins / games)

    st.session_state.wins = wins
    st.session_state.games = games
    st.session_state.losses = losses
    st.session_state.winrate = winrate
    st.session_state.firsts = firsts
    st.session_state.seconds = seconds


def pull_deck_data(d, p, c=False):
    st.session_state.deck_data_compare = None
    st.session_state.compare_deck = None
    st.session_state.compare_deck_link = None
    print(f"Pulling deck data for deck {d} ({p})")
    if c:
        st.session_state.deck_data_compare = analysis.analyze_deck(d, p, aliases=st.session_state.pilot_info['aliases'])
    else:
        if 'aliases' not in st.session_state.pilot_info:
            st.session_state.pilot_info['aliases'] = []
        st.session_state.deck_data = analysis.analyze_deck(d, p, aliases=st.session_state.pilot_info['aliases'])


if 'deck_data' not in st.session_state:
    print('Pulling deck data', deck, pilot)
    pull_deck_data(deck, pilot)

if 'deck_data' not in st.session_state:
    st.error("No deck selected")
else:
    if 'pilot' not in st.session_state:
        if 'elo_data' in st.session_state:
            st.session_state.pilot = st.session_state.elo_data['player']
        else:
            st.error(f"Error locating deck pilot.")
            st.session_state.pilot = ''
    pilot = st.session_state.pilot
    deck = st.session_state.deck
    score = st.session_state.score
    c1, c2, c3, c4 = st.columns([22, 1, 1, 1])
    if 'name' in st.session_state and (st.session_state.name == pilot or 'aliases' in st.session_state and pilot in st.session_state.aliases):
        pass
    else:
        c1.markdown(f'<b class="pilot-font">{pilot}</b>', unsafe_allow_html=True)
    home = c3.button("🏠")
    if home:
        st.switch_page("Home.py")
    st.write('')
    c1, c2 = st.columns([7, 1])
    c1.markdown(f'<b class="deck-font">{deck}</b>', unsafe_allow_html=True)
    c2.link_button("Deck Info", deck_link)

    if 'name' in st.session_state and st.session_state.name == pilot:
        if 'deck_log' in st.session_state:
            deck_log = st.session_state.deck_log
        else:
            with st.spinner('Getting decks...'):
                if 'game_log' in st.session_state:
                    deck_log = database.get_user_decks(st.session_state.name, aliases=st.session_state.aliases, game_data=st.session_state.game_log)
                else:
                    deck_log = database.get_user_decks(st.session_state.name, aliases=st.session_state.aliases)

                st.session_state.deck_log = deck_log
        deck_log = deck_log[deck_log['Deck'].apply(lambda x: x[0] != deck)]
        if len(deck_log) > 0:
            with st.expander('Compare Deck'):
                compare_choice = st.dataframe(deck_log[['Deck', 'Games', 'Win-Loss', 'Winrate']], on_select='rerun', selection_mode='single-row', hide_index=True)
                c1, c2, c3 = st.columns([1, 1, 7])
                compare_button = c1.button('Compare')
                clear_button = c2.button('Clear')
                if compare_button:
                    if len(compare_choice['selection']['rows']) == 0:
                        st.error("No deck selected")
                    else:
                        st.session_state.deck_data_compare = None
                        st.session_state.compare_deck = None
                        st.session_state.compare_deck_link = None
                        deck_choice = deck_log.iloc[compare_choice['selection']['rows'][0]]
                        compare_deck = deck_choice['Deck'][0]
                        compare_deck_link = deck_choice['Deck Link']
                        pull_deck_data(compare_deck, pilot, True)
                        if 'compare_games' not in st.session_state:
                            st.session_state.compare_games = deck_choice['Games']
                        st.session_state.compare_deck = compare_deck
                        st.session_state.compare_deck_link = compare_deck_link

                if clear_button:
                    st.session_state.deck_data_compare = None
                    st.session_state.compare_deck = None
                    st.session_state.compare_deck_link = None
    if 'compare_deck' in st.session_state and st.session_state.compare_deck:
        st.write('')
        c1, c2 = st.columns([7, 1], vertical_alignment='bottom')
        c1.markdown(f'<b class="compare-deck-font">{st.session_state.compare_deck} (C)</b>', unsafe_allow_html=True)
        c2.link_button("Deck Info", st.session_state.compare_deck_link)

    with st.spinner('Analyzing games...'):
        wins = st.session_state.wins
        losses = st.session_state.losses
        games = st.session_state.games
        winrate = st.session_state.winrate

        deck_df, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, advantage_charts, player_card_data, opponent_card_data, turns = graphing.analyze_deck(pilot, st.session_state.deck_data, games)
        if 'deck_data_compare' in st.session_state and st.session_state.deck_data_compare is not None:
            compare_data = graphing.analyze_deck(pilot, st.session_state.deck_data_compare, st.session_state.compare_games)
            compare_data[0].columns = compare_data[0].columns.map(lambda c: c + ' (C)')
            min_length = min(len(deck_df), len(compare_data[0]))
            chart_df = pd.concat([deck_df, compare_data[0]], axis=1)
            chart_df = chart_df[:min_length]
            turn_df = pd.DataFrame(turns, columns=['Games'])
            turn_list = compare_data[-1]
            if len(turn_list) == len(turn_df):
                turn_df['Games (C)'] = turn_list
            elif len(turn_list) > len(turn_df):
                turn_list = turn_list[:len(turn_df)]
                turn_df['Games (C)'] = turn_list
            elif len(turn_df) > len(turn_list):
                turn_df = turn_df[:len(turn_list)]
                turn_df['Games (C)'] = turn_list
            chart_colors = [(255, 75, 75), (255, 75, 75, 0.6), (96, 180, 255), (96, 180, 255, 0.6)]
            comparison = True
        else:
            chart_df = deck_df
            turn_df = pd.DataFrame(turns, columns=['Games'])
            chart_colors = [(255, 75, 75), (96, 180, 255)]
            comparison = False

    player_card_data['Games %'] = 0
    player_card_data['WR%'] = np.nan
    player_card_data['(-)WR%'] = np.nan
    c_win_dict = st.session_state.deck_data[pilot]['card_wins']
    c_loss_dict = st.session_state.deck_data[pilot]['card_losses']
    for idx, row in player_card_data.iterrows():
        card = row['Card']
        c_wins = c_win_dict.get(card, 0)
        c_losses = c_loss_dict.get(card, 0)

        if c_wins + c_losses > 0:
            c_winrate = round(100*c_wins / (c_wins + c_losses))
            player_card_data.at[idx, 'WR%'] = c_winrate

            try:
                c_winrate_wo = round(
                    100 * (int(wins) - int(c_wins)) / (int(wins) + int(losses) - int(c_wins) - int(c_losses)))
            except:
                c_winrate_wo = np.nan

            player_card_data.at[idx, '(-)WR%'] = c_winrate_wo

            player_card_data.at[idx, 'Games %'] = round(100*(c_wins + c_losses) / games)

    opponent_card_data['Games %'] = 0
    opponent_card_data['WR%'] = np.nan
    opponent_card_data['(-)WR%'] = np.nan
    c_win_dict = st.session_state.deck_data['opponent']['card_wins']
    c_loss_dict = st.session_state.deck_data['opponent']['card_losses']
    for idx, row in opponent_card_data.iterrows():
        card = row['Card']
        c_wins = c_win_dict.get(card, 0)
        c_losses = c_loss_dict.get(card, 0)

        if c_wins + c_losses > 0:
            c_winrate = round(100*c_wins / (c_wins + c_losses))
            opponent_card_data.at[idx, 'WR%'] = c_winrate

            try:
                c_winrate_wo = round(100*(int(wins) - int(c_wins)) / (int(wins) + int(losses) - int(c_wins) - int(c_losses)))
            except:
                c_winrate_wo = np.nan

            opponent_card_data.at[idx, '(-)WR%'] = c_winrate_wo

            opponent_card_data.at[idx, 'Games %'] = round(100*(c_wins + c_losses) / games)

    # player_card_data['Impact'] = round((player_card_data['WR%'] - player_card_data['(-)WR%']) * (50-abs(player_card_data['Games %']-50)) / 50, 1)
    # opponent_card_data['Impact'] = round((opponent_card_data['WR%'] - opponent_card_data['(-)WR%']) * (50-abs(opponent_card_data['Games %']-50)) / 50, 1)

    st.divider()

    tab_1, tab_2, tab_3, tab_4 = st.tabs(['Info', 'Charts', 'Advantage', 'Cards'])

    with tab_1:
        with st.container(border=True):

            wins = st.session_state.wins
            losses = st.session_state.losses
            games = st.session_state.games
            winrate = st.session_state.winrate

            c0, c1, c2, c3, c4 = st.columns([0.6, 1, 1, 1, 1])
            c1.subheader("Games")
            c2.subheader("Win-Loss")
            c3.subheader("Winrate")
            c4.subheader("ELO")
            c1.markdown(f'<b class="plain-font">  {games}</b>', unsafe_allow_html=True)
            c2.markdown(f'<b class="hero-font">  {wins}</b><b class="plain-font">-</b><b class="villain-font">{losses}</b>', unsafe_allow_html=True)
            if winrate >= 50:
                c3.markdown(f'<b class="hero-font">   {winrate}%</b>', unsafe_allow_html=True)
            elif winrate < 50:
                c3.markdown(f'<b class="villain-font">   {winrate}%</b>', unsafe_allow_html=True)
            if score:
                if score >= 1500:
                    c4.markdown(f'<b class="hero-font">{score}</b>', unsafe_allow_html=True)
                elif score < 1500:
                    c4.markdown(f'<b class="villain-font">{score}</b>', unsafe_allow_html=True)

        houses_and_cards = st.session_state.deck_dok_data['Data']['deck']['housesAndCards']

        house_cards = {entry["house"]: [card["cardTitle"] for card in entry["cards"]] for entry in houses_and_cards}

        house_scores = {h: {
            'Rating': {
                'Games': 0,
                'Wins': 0,
            },
            'Dependence': {
                'Games': 0,
                'Wins': 0,
            },
            'Cards Played': 0,
            'Amber Gained': 0,
        } for h in house_cards.keys()}

        games = st.session_state.games
        winrate = st.session_state.winrate

        cols = st.columns(3)

        total_cards_played = player_card_data['Played'].sum()
        total_amber_gained = player_card_data['Amber'].sum()

        cards_checked = []

        for i, house in enumerate(house_cards):
            for card in house_cards[house]:
                c_data = player_card_data.loc[player_card_data['Card'] == card]
                cr_games = round(games * c_data['Games %'].iloc[0] / 100)
                try:
                    cr_wins = round(cr_games * c_data['WR%'].iloc[0] / 100)
                except:
                    cr_wins = 0

                house_scores[house]['Rating']['Games'] += cr_games
                house_scores[house]['Rating']['Wins'] += cr_wins

                cd_games = games - cr_games
                if cd_games > 0:
                    try:
                        cd_wins = round(cd_games * c_data['(-)WR%'].iloc[0] / 100)
                    except:
                        cd_wins = 0
                else:
                    cd_wins = 0

                house_scores[house]['Dependence']['Games'] += cd_games
                house_scores[house]['Dependence']['Wins'] += cd_wins

                if card not in cards_checked:
                    cards_checked.append(card)

                    card_played = c_data['Played'].iloc[0]
                    house_scores[house]['Cards Played'] += card_played

                    amber_gained = c_data['Amber'].iloc[0]
                    house_scores[house]['Amber Gained'] += amber_gained

            h_wr = round(100 * house_scores[house]['Rating']['Wins'] / house_scores[house]['Rating']['Games'])
            h_dp = round(100 * (1 - house_scores[house]['Dependence']['Wins'] / house_scores[house]['Dependence']['Games']))

            with cols[i].container(border=True):
                st.markdown(f'<b class="plain-font">{house} Strength</b>', unsafe_allow_html=True)
                c1, c2, _ = st.columns([2.8, 1, 0.2])
                c1.metric(f'{house} Strength', value=h_wr, delta=round(h_wr - winrate), label_visibility='collapsed')
                c2.image(house_dict[house]['Image'])
                st.divider()
                st.markdown(f'<b class="plain-font">{house} Dependence</b>', unsafe_allow_html=True)
                st.metric(f'{house} Dependence', value=h_dp, delta=round(h_dp - (100 - winrate)), delta_color='inverse', label_visibility='collapsed')
                st.divider()
                st.markdown(f'<p class="plain-font">Cards Played: {round(100*house_scores[house]["Cards Played"]/total_cards_played)}%</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="plain-font">Amber Gained: {round(100*house_scores[house]["Amber Gained"]/total_cards_played)}%</p>', unsafe_allow_html=True)

        with st.container(border=True):
            sets = ['CotA', 'AoA', 'WC', 'MM', 'DT', 'WoE', 'GR', 'AES', 'ToC', 'MMM', 'VM23', 'VM24']
            set_winrate_df = st.session_state.set_winrate_df
            cols = st.columns([0.25] + [1 for i in range(max(len(set_winrate_df), 4))])
            col_num = 1
            for s in sets:
                if s in set_winrate_df['Opponent Set'].values:
                    cols[col_num].markdown(f'<b class ="{s}-font">vs {s}</b>', unsafe_allow_html=True)
                    set_winrate = set_winrate_df.loc[set_winrate_df['Opponent Set'] == s, 'Winrate'].iat[0]
                    set_games = set_winrate_df.loc[set_winrate_df['Opponent Set'] == s, 'Count'].iat[0]
                    if set_winrate >= 50:
                        cols[col_num].markdown(f'<b class="hero-font">{set_winrate}% {set_games}</b>', unsafe_allow_html=True)
                    elif set_winrate < 50:
                        cols[col_num].markdown(f'<b class="villain-font">{set_winrate}% {set_games}</b>', unsafe_allow_html=True)
                    col_num += 1

        with st.container(border=True):
            st.write(' ')
            house_winrate_df = st.session_state.house_winrate_df
            cols = st.columns([0.25, 1, 1, 1, 1, 1, 1, 1])
            col_num = 1
            for h in house_dict:
                if h in house_winrate_df['Opponent Houses'].values:
                    cols[col_num].image(house_dict[h]['Image'])
                    house_winrate = house_winrate_df.loc[house_winrate_df['Opponent Houses'] == h, 'Winrate'].iat[0]
                    house_games = house_winrate_df.loc[house_winrate_df['Opponent Houses'] == h, 'Count'].iat[0]
                    if house_winrate >= 50:
                        cols[col_num].markdown(f'<b class="hero-font"> {house_winrate}% {house_games}</b>', unsafe_allow_html=True)
                    elif house_winrate < 50:
                        cols[col_num].markdown(f'<b class="villain-font"> {house_winrate}% {house_games}</b>', unsafe_allow_html=True)
                    col_num += 1
                    if col_num > 7:
                        col_num = 1

    with tab_2:
        st.subheader("Game Length")
        if comparison:
            y = ['Games', 'Games (C)']
        else:
            y = ['Games']
        st.line_chart(
            turn_df,
            x=None,
            y=y,
            y_label='Games (%)',
        )

        c1, c2 = st.columns(2)

        base_colors = [(255, 75, 75), (96, 180, 255)]

        chart_dict = {
            "Total Amber Value": {
                'y_values': ['Player Amber', 'Opponent Amber'],
                'y_label': 'Amber Value',
                'color': base_colors,
            },
            "Total Cards Played": {
                'y_values': ['Player Cards', 'Opponent Cards'],
                'y_label': 'Cards Played',
                'color': base_colors,
            },
            "Prediction": {
                'y_values': ['Player Prediction', 'Opponent Prediction'],
                'y_label': 'Turns to Win',
                'color': base_colors,
            },
            "Creatures": {
                'y_values': ['Player Creatures', 'Opponent Creatures'],
                'y_label': 'Creatures',
                'color': base_colors,
            },
            "Amber Delta": {
                'y_values': ['Player Delta', 'Opponent Delta'],
                'y_label': 'Delta',
                'color': base_colors,
            },
            "Reap Rate": {
                'y_values': ['Player Reap Rate', 'Opponent Reap Rate'],
                'y_label': 'Reap Rate (%)',
                'color': base_colors,
            },
            "Amber Defense": {
                'y_values': ['Player Amber Defense', 'Opponent Amber Defense'],
                'y_label': 'Amber Defense (%)',
                'color': base_colors,
            },
            "Creature Survival Rate": {
                'y_values': ['Player Survival Rate', 'Opponent Survival Rate'],
                'y_label': 'Survival Rate (%)',
                'color': base_colors,
            },
        }

        for i, chart in enumerate(chart_dict.keys()):
            if i % 2 == 0:
                col = c1
            else:
                col = c2

            col.subheader(chart)
            col.line_chart(
                chart_df,
                x=None,
                y=chart_dict[chart]['y_values'],
                x_label='Turn',
                y_label=chart_dict[chart]['y_label'],
                color=chart_dict[chart]['color']
            )

        # c1.subheader("Reap/Kill Advantage")
        # y = ['Reap/Kill Advantage']
        # c1.line_chart(
        #     chart_df,
        #     x=None,
        #     y=y,
        #     x_label='Turn',
        #     y_label='Reap Advantage',
        #     color=chart_colors[1]
        # )
        #
        # c2.subheader("Reap/Trade Advantage")
        # y = ['Reap/Trade Advantage']
        # c2.line_chart(
        #     chart_df,
        #     x=None,
        #     y=y,
        #     x_label='Turn',
        #     y_label='Reap Advantage',
        #     color=chart_colors[1]
        # )

        c1.subheader("Player Amber Sources")
        c1.plotly_chart(player_amber_sources, use_container_width=True)
        c2.subheader("Opponent Amber Sources")
        c2.plotly_chart(opponent_amber_sources, use_container_width=True)

        if comparison:
            c1.subheader("Player Amber Sources (C)")
            c1.plotly_chart(compare_data[1], use_container_width=True)
            c2.subheader("Opponent Amber Sources (C)")
            c2.plotly_chart(compare_data[2], use_container_width=True)

        c1.subheader("Player House Calls")
        c1.image(player_house_calls)
        c2.subheader("Opponent House Calls")
        c2.image(opponent_house_calls)

        if comparison:
            c1.subheader("Player House Calls (C)")
            c1.plotly_chart(compare_data[3], use_container_width=True)
            c2.subheader("Opponent House Calls (C)")
            c2.plotly_chart(compare_data[4], use_container_width=True)

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
        c1, c2, c3 = st.columns([5, 1, 1])
        c1.subheader("Cards Played")
        if st.session_state.expand_all:
            exp_button_string = "Collapse All"
        else:
            exp_button_string = "Expand All"

        starting_turn_string = c2.selectbox('Starting', options=['Going First', 'Going Second'], label_visibility='collapsed')

        starting_turn = starting_turn_string.split(' ')[-1].lower()

        if starting_turn == 'first':
            num_games = st.session_state.firsts
        else:
            num_games = st.session_state.seconds

        card_played_data = st.session_state.deck_data[pilot]['individual_cards_played_turn'][starting_turn]

        c3.button(exp_button_string, on_click=expand_turns)

        card_image_dict = dok_api.card_image_dict

        for t, cards_played_turn in enumerate(card_played_data):
            relative_frequencies = {key: value['played'] / num_games for key, value in cards_played_turn.items()}
            df = pd.DataFrame(list(relative_frequencies.items()), columns=['Card', 'Relative Frequency'])
            df_sorted = df.sort_values(by='Relative Frequency', ascending=False)

            turn_string = f"Turn {t+1}"
            with st.expander(fr"$\texttt{{\large {turn_string}}}$", expanded=st.session_state.expand_all):
                cols = st.columns(10)

                for i in range(min(10, len(df_sorted))):
                    card_row = df_sorted.iloc[i]
                    card_name = card_row['Card']
                    card_name_image = card_name.split('~~')[0]

                    frequency = round(card_row['Relative Frequency'] * 100)
                    if frequency == 100:
                        frequency_string = f"  {frequency}%"
                    elif frequency < 10:
                        frequency_string = f"    {frequency}%"
                    else:
                        frequency_string = f"   {frequency}%"

                    card_turn_data = cards_played_turn[card_name]
                    card_turn_winrate = round(100 * card_turn_data['wins'] / card_turn_data['played'])
                    if card_turn_winrate == 100:
                        card_turn_winrate_string = f"  {card_turn_winrate}%"
                    elif card_turn_winrate < 10:
                        card_turn_winrate_string = f"    {card_turn_winrate}%"
                    else:
                        card_turn_winrate_string = f"   {card_turn_winrate}%"

                    if card_name_image not in card_image_dict:
                        st.toast(f"Card image not found: {card_name_image}")
                        image_link = None
                    else:
                        image_link = card_image_dict[card_name_image]
                        try:
                            cols[i].image(image_link)
                        except:
                            st.toast(f"Error getting card image: {image_link}")
                    cols[i].markdown(f'<b class="plain-italic-font">{frequency_string}</b>', unsafe_allow_html=True)
                    if card_turn_winrate >= 50:
                        cols[i].markdown(f'<b class="hero-italic-font">{card_turn_winrate_string}</b>', unsafe_allow_html=True)
                    else:
                        cols[i].markdown(f'<b class="villain-italic-font">{card_turn_winrate_string}</b>', unsafe_allow_html=True)

