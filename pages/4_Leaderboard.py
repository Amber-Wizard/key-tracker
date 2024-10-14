import streamlit as st
import pandas as pd

import database

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
.rank-font {
    font-size: 22px !important;
    color: #424242 !important;
}
.plain-font {
    font-size: 22px !important;
}
.plain-italic-font {
    font-size: 26px !important;
    font-style: italic !important;  /* Make this font italic */
}
.hero-font {
    font-size: 22px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 22px !important;
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


def get_all_elo_scores():
    with st.spinner('Getting ELO data...'):
        user_scores = database.get_all_users()
        user_dict = {d['tco_name']: d for d in user_scores}
        st.session_state.user_dict = user_dict
        st.session_state.user_scores = [i for i in user_dict.values() if 'games' in i and 'wins' in i and i['games'] > 0]
        deck_scores = database.get_all_elo()
        st.session_state.deck_scores = [i for i in deck_scores if 'games' in i and 'wins' in i and i['games'] > 0]


# get_all_elo_scores()


c1, c2, c3, c4 = st.columns([22, 1, 1, 1])

c1.title("Leaderboard")
home = c3.button("🏠")
if home:
    st.switch_page("Home.py")

c1, c2, c3 = st.columns([4, 1, 1])
lb_type = c1.selectbox('', options=['Decks', 'Players'])
sort_by = c2.selectbox('Sort', options=['Score', 'WR%', 'Games'])
sort_order = c3.selectbox('Order', options=['Desc', 'Asc'])

if lb_type == 'Decks':
    if 'deck_scores' not in st.session_state:
        get_all_elo_scores()
    elo_scores = st.session_state.deck_scores
else:
    if 'user_scores' not in st.session_state:
        get_all_elo_scores()
    elo_scores = st.session_state.user_scores


if sort_order == 'Asc':
    reverse = False
else:
    reverse = True

if sort_by == 'Score':
    st.session_state.elo_scores = sorted(elo_scores, key=lambda x: int(x['score']), reverse=reverse)
elif sort_by == 'Games':
    st.session_state.elo_scores = sorted(elo_scores, key=lambda x: int(x['games']), reverse=reverse)
else:
    st.session_state.elo_scores = sorted(elo_scores, key=lambda x: (int(x['wins']) / int(x['games'])), reverse=reverse)

st.divider()

last_rank = 1
if lb_type == 'Players':
    cols = st.columns([0.8, 1, 1, 0.8, 0.1, 7, 0.9])
    cols[1].markdown(f'<b class="plain-font">Score</b>', unsafe_allow_html=True)
    cols[2].markdown(f'<b class="plain-font"> WR%</b>', unsafe_allow_html=True)
    cols[3].markdown(f'<b class="plain-font">Games</b>', unsafe_allow_html=True)
    cols[5].markdown(f'<b class="plain-font">Player</b>', unsafe_allow_html=True)
    for item in st.session_state.elo_scores:
        with st.container(border=True):
            cols = st.columns([0.8, 1, 1, 0.8, 0.1, 7, 0.9])

            cols[0].markdown(f'<b class="rank-font">{last_rank}.</b>', unsafe_allow_html=True)
            cols[1].markdown(f'<b class="plain-font">{item["score"]}</b>', unsafe_allow_html=True)
            try:
                cols[2].markdown(f'<b class="plain-font">{round(100 * item["wins"] / item["games"])}%</b>', unsafe_allow_html=True)
            except:
                cols[2].markdown(f'<b class="plain-font">--%</b>', unsafe_allow_html=True)

            cols[3].markdown(f'<b class="plain-font">{item["games"]}</b>', unsafe_allow_html=True)

            if 'name' in st.session_state and (st.session_state.name == item['tco_name'] or st.session_state.name == 'master'):
                cols[5].markdown(f'<b class="hero-font">{item["tco_name"]}</b>', unsafe_allow_html=True)
            elif 'show_player' in st.session_state.user_dict[item['tco_name']] and st.session_state.user_dict[item['tco_name']]['show_player']:
                cols[5].markdown(f'<b class="villain-font">{item["tco_name"]}</b>', unsafe_allow_html=True)
            else:
                cols[5].markdown(f'<b class="rank-font">-----</b>', unsafe_allow_html=True)

        last_rank += 1


else:
    cols = st.columns([0.8, 1, 1, 0.8, 7, 2])
    cols[1].markdown(f'<b class="plain-font">Score</b>', unsafe_allow_html=True)
    cols[2].markdown(f'<b class="plain-font"> WR%</b>', unsafe_allow_html=True)
    cols[3].markdown(f'<b class="plain-font">Games</b>', unsafe_allow_html=True)
    cols[4].markdown(f'<b class="plain-font">Deck</b>', unsafe_allow_html=True)
    cols[5].markdown(f'<b class="plain-font">Player</b>', unsafe_allow_html=True)
    for item in st.session_state.elo_scores:
        if item['deck'] != '-Error-' and item['deck'] != '---' and type(item['deck']) == str and 'games' in item and item['games'] > 0:
            with st.container(border=True):
                cols = st.columns([0.8, 1, 1, 0.8, 7, 2])

                cols[0].markdown(f'<b class="rank-font">{last_rank}.</b>', unsafe_allow_html=True)
                cols[1].markdown(f'<b class="plain-font">{item["score"]}</b>', unsafe_allow_html=True)
                try:
                    cols[2].markdown(f'<b class="plain-font">{round(100*item["wins"]/item["games"])}%</b>', unsafe_allow_html=True)
                except:
                    cols[2].markdown(f'<b class="plain-font">--%</b>', unsafe_allow_html=True)

                cols[3].markdown(f'<b class="plain-font"> {item["games"]}</b>', unsafe_allow_html=True)

                if 'name' in st.session_state and (st.session_state.name == item['player'] or st.session_state.name == 'master'):
                    cols[4].markdown(f'<b class="plain-font">{item["deck"]}</b>', unsafe_allow_html=True)
                    cols[5].markdown(f'<b class="hero-font">{item["player"]}</b>', unsafe_allow_html=True)
                elif 'show_decks' in st.session_state.user_dict[item['player']] and st.session_state.user_dict[item['player']]['show_decks']:
                    cols[4].markdown(f'<b class="plain-font">{item["deck"]}</b>', unsafe_allow_html=True)
                    cols[5].markdown(f'<b class="villain-font">{item["player"]}</b>', unsafe_allow_html=True)
                else:
                    cols[4].markdown(f'<b class="rank-font">--------------</b>', unsafe_allow_html=True)
                    cols[5].markdown(f'<b class="rank-font">-----</b>', unsafe_allow_html=True)

            last_rank += 1
