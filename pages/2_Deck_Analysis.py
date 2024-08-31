import streamlit as st
import pandas as pd

import database
import graphing
import analysis


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
.hero-font {
    font-size: 26px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
}
.CotA-font {
    font-size: 28px !important;
    color: #d92b34 !important;
}
.AoA-font {
    font-size: 28px !important;
    color: #259adb !important;
}
.WC-font {
    font-size: 28px !important;
    color: #ad39a5 !important;
}
.MM-font {
    font-size: 28px !important;
    color: #e94e76 !important;
}
.DT-font {
    font-size: 28px !important;
    color: #136697 !important;
}
.WoE-font {
    font-size: 28px !important;
    color: #0c9aa8 !important;
}
.GR-font {
    font-size: 28px !important;
    color: #0c4f7f !important;
}
.VM23-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.VM24-font {
    font-size: 28px !important;
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


if 'shareID' in st.query_params:
    st.session_state.share_id = st.query_params.get_all(key='shareID')[0]
    if 'deck_selection' in st.session_state:
        del st.session_state['deck_selection']
    if 'elo_data' in st.session_state:
        del st.session_state['elo_data']
    if 'deck_games' in st.session_state:
        del st.session_state['deck_games']
    if 'deck_data' in st.session_state:
        del st.session_state['deck_data']

if 'deck_selection' in st.session_state:
    if 'elo_data' not in st.session_state:
        st.session_state.elo_data = database.get_elo(st.session_state.name, st.session_state.deck)
        st.session_state.deck = st.session_state.elo_data['deck']
        st.session_state.pilot = st.session_state.elo_data['player']
        st.session_state.score = st.session_state.elo_data['score']
    share_id = st.session_state.elo_data['_id']
    st.query_params['shareID'] = share_id
    st.session_state.share_id = share_id
    deck_link = st.session_state.deck_selection["Deck Link"].iloc[0]
    wins, losses = st.session_state.deck_selection["Win-Loss"].iat[0].split('-')
    games = st.session_state.deck_selection["Games"].iloc[0]
    winrate = st.session_state.deck_selection["Winrate"].iloc[0]

if 'share_id' in st.session_state and 'elo_data' not in st.session_state:
    st.session_state.elo_data = database.get_elo_by_id(st.session_state.share_id)
    st.session_state.deck = st.session_state.elo_data['deck']
    st.session_state.pilot = st.session_state.elo_data['player']
    st.session_state.score = st.session_state.elo_data['score']

if 'deck_games' not in st.session_state:
    pilot = st.session_state.pilot
    deck = st.session_state.deck
    deck_games = database.get_deck_games(pilot, deck, trim_lists=True)
    st.session_state.deck_games = deck_games
    deck_games['Dok Data'] = None
    deck_games['Opponent Set'] = None
    for idx, row in deck_games.iterrows():
        dok_data = database.get_dok_cache_deck_id(row['Opponent Deck Link'].split('/')[-1])
        deck_games.at[idx, 'Dok Data'] = dok_data
        deck_games.at[idx, 'Opponent Set'] = database.set_conversion_dict[dok_data['Data']['deck']['expansion']][0]
    set_winrate_df = deck_games['Opponent Set'].value_counts().reset_index()

    set_winrate_df.columns = ['Opponent Set', 'Count']
    set_winrate_df['Wins'] = None
    for idx, row in set_winrate_df.iterrows():
        opponent_set = row['Opponent Set']
        count = ((deck_games['Opponent Set'] == opponent_set) & (deck_games['Winner'] == pilot)).sum()
        set_winrate_df.at[idx, 'Wins'] = count

    set_winrate_df['Winrate'] = 100 * set_winrate_df['Wins'] / set_winrate_df['Count']
    set_winrate_df['Winrate'] = pd.to_numeric(set_winrate_df['Winrate'], errors='coerce')
    set_winrate_df['Winrate'] = set_winrate_df['Winrate'].round(0).astype(int)
    st.session_state.set_winrate_df = set_winrate_df


if 'deck_selection' not in st.session_state:
    deck_games = st.session_state.deck_games
    deck_link = st.session_state.deck_games['Deck Link'].iat[0]
    wins = (deck_games['Winner'] == st.session_state.pilot).sum()
    games = len(deck_games)
    losses = games - wins
    winrate = round(100 * wins / games)


def pull_deck_data(d, p):
    st.session_state.deck_data = analysis.analyze_deck(d, p)


if 'deck_data' not in st.session_state:
    print('Pulling deck data', deck, pilot)
    pull_deck_data(deck, pilot)

if 'deck_data' not in st.session_state:
    st.error("No deck selected")
else:
    pilot = st.session_state.pilot
    deck = st.session_state.deck
    score = st.session_state.score
    c1, c2, c3, c4 = st.columns([22, 1, 1, 1])
    if 'name' in st.session_state and st.session_state.name == pilot:
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
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.subheader("Games")
    c2.subheader("Win-Loss")
    c3.subheader("Winrate")
    c4.subheader("ELO")
    c1.markdown(f'<b class="plain-font">{games}</b>', unsafe_allow_html=True)
    c2.markdown(f'<b class="hero-font">{wins}</b><b class="plain-font">-</b><b class="villain-font">{losses}</b>', unsafe_allow_html=True)
    if winrate >= 50:
        c3.markdown(f'<b class="hero-font">{winrate}%</b>', unsafe_allow_html=True)
    elif winrate < 50:
        c3.markdown(f'<b class="villain-font">{winrate}%</b>', unsafe_allow_html=True)
    if score:
        if score >= 1500:
            c4.markdown(f'<b class="hero-font">{score}</b>', unsafe_allow_html=True)
        elif score < 1500:
            c4.markdown(f'<b class="villain-font">{score}</b>', unsafe_allow_html=True)
    st.write(' ')
    st.write(' ')
    sets = ['CotA', 'AoA', 'WC', 'MM', 'DT', 'WoE', 'GR', 'VM23', 'VM24']
    set_winrate_df = st.session_state.set_winrate_df
    cols = st.columns(max(len(set_winrate_df), 4))
    col_num = 0
    for s in sets:
        if s in set_winrate_df['Opponent Set'].values:
            cols[col_num].markdown(f'<b class ="{s}-font">vs {s}</b>', unsafe_allow_html=True)
            set_winrate = set_winrate_df.loc[set_winrate_df['Opponent Set'] == s, 'Winrate'].iat[0]
            set_games = set_winrate_df.loc[set_winrate_df['Opponent Set'] == s, 'Count'].iat[0]
            if set_winrate >= 50:
                cols[col_num].markdown(f'<b class="hero-font">{set_winrate}% ({set_games})</b>', unsafe_allow_html=True)
            elif set_winrate < 50:
                cols[col_num].markdown(f'<b class="villain-font">{set_winrate}% ({set_games})</b>', unsafe_allow_html=True)
            col_num += 1

    st.write(' ')
    st.write(' ')
    st.write(' ')

    deck_df, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, player_card_data, opponent_card_data, turns = graphing.analyze_deck(pilot, st.session_state.deck_data)

    turn_df = pd.DataFrame(turns, columns=['Games'])
    st.subheader("Game Length")
    st.line_chart(
        turn_df,
        x=None,
        y=['Games'],
        y_label='Games',
    )

    c1, c2 = st.columns(2)
    c1.subheader("Total Amber Value")
    c1.line_chart(
        deck_df,
        x=None,
        y=['Player Amber', 'Opponent Amber'],
        x_label='Turn',
        y_label='Amber Value',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Total Cards Played")
    c2.line_chart(
        deck_df,
        x=None,
        y=['Player Cards', 'Opponent Cards'],
        x_label='Turn',
        y_label='Cards Played',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Prediction")

    c1.line_chart(
        deck_df,
        x=None,
        y=['Player Prediction', 'Opponent Prediction'],
        x_label='Turn',
        y_label='Turns to Win',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Creatures")
    c2.line_chart(
        deck_df,
        x=None,
        y=['Player Creatures', 'Opponent Creatures'],
        x_label='Turn',
        y_label='Creatures',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Amber Delta")
    c1.line_chart(
        deck_df,
        x=None,
        y=['Player Delta', 'Opponent Delta'],
        x_label='Turn',
        y_label='Delta',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Reap Rate")
    c2.line_chart(
        deck_df,
        x=None,
        y=['Player Reap Rate', 'Opponent Reap Rate'],
        x_label='Turn',
        y_label='Reap Rate',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c1.subheader("Amber Defense")
    c1.line_chart(
        deck_df,
        x=None,
        y=['Player Amber Defense', 'Opponent Amber Defense'],
        x_label='Turn',
        y_label='Amber Defense (%)',
        color=[(255, 75, 75), (96, 180, 255)]
    )

    c2.subheader("Creature Survival Rate")
    c2.line_chart(
        deck_df,
        x=None,
        y=['Player Survival Rate', 'Opponent Survival Rate'],
        x_label='Turn',
        y_label='Survival Rate (%)',
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
