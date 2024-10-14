import streamlit as st
import pandas as pd

import database
from graphing import house_dict, set_dict
from Home import default_settings


achievement_master_dict = {
    'Amberologist': {
        'levels': [25, 50, 100, 150, 200],
        'description': 'Gain ~ Amber in a single game',
        'image_links': ['https://i.postimg.cc/sXw2ghXf/amberologist-L1.png', 'https://i.postimg.cc/6qP5dxnD/amberologist-L2.png', 'https://i.postimg.cc/pVcTNz4q/amberologist-L3.png', 'https://i.postimg.cc/gkw0GrPd/amberologist-L4.png', 'https://i.postimg.cc/BQdnbsqF/amberologist-L5.png'],
    },
    'Reap or Sow': {
        'levels': [20, 35, 50, 75, 100],
        'description': 'Reap ~ times in a single game',
        'image_links': ['https://i.postimg.cc/nrq9cL63/reap-or-sow-L1.png', 'https://i.postimg.cc/1RD8FfjH/reap-or-sow-L2.png', 'https://i.postimg.cc/bN8s9qXj/reap-or-sow-L3.png', 'https://i.postimg.cc/02frthxK/reap-or-sow-L4.png', 'https://i.postimg.cc/Gmmt6zh7/reap-or-sow-L5.png'],
    },
    'A Gift of Amber': {
        'levels': [20, 35, 50, 75, 100],
        'description': 'Gain ~ Amber from Icons in a single game',
        'image_links': ['https://i.postimg.cc/GhF8YHHR/a-gift-of-amber-L1.png', 'https://i.postimg.cc/kgw21zQh/a-gift-of-amber-L2.png', 'https://i.postimg.cc/0NBbxSHY/a-gift-of-amber-L3.png', 'https://i.postimg.cc/nLzC62TV/a-gift-of-amber-L4.png', 'https://i.postimg.cc/NjQyxBHH/a-gift-of-amber-L5.png'],
    },
    'Too Much to Protect': {
        'levels': [20, 35, 50, 75, 100],
        'description': 'Steal ~ Amber in a single game',
        'image_links': ['https://i.postimg.cc/8zkRzhw9/too-much-too-protect-L1.png', 'https://i.postimg.cc/Vk7jrdV6/too-much-too-protect-L2.png', 'https://i.postimg.cc/vmc5WbJv/too-much-too-protect-L3.png', 'https://i.postimg.cc/mrJCjKRW/too-much-too-protect-L4.png', 'https://i.postimg.cc/KzTLHQvk/too-much-too-protect-L5.png'],
    },
    'Library Card': {
        'levels': [50, 75, 100, 150, 200],
        'description': 'Play ~ cards in a single game',
        'image_links': ['https://i.postimg.cc/Zq3ZCDb5/library-card-L1.png', 'https://i.postimg.cc/1tQS6cXc/library-card-L2.png', 'https://i.postimg.cc/D0C3t9gB/library-card-L3.png', 'https://i.postimg.cc/gc4pXhW8/library-card-L4.png', 'https://i.postimg.cc/hv4qZD9X/library-card-L5.png'],
    },
    'Junk Restoration': {
        'levels': [25, 50, 100, 150, 200],
        'description': 'Discard ~ cards in a single game',
        'image_links': ['https://i.postimg.cc/NMdgc2G6/junk-restoration-L1.png', 'https://i.postimg.cc/0j3P6gwr/junk-restoration-L2.png', 'https://i.postimg.cc/PrpdgqgD/junk-restoration-L3.png', 'https://i.postimg.cc/jdpRtbTF/junk-restoration-L4.png', 'https://i.postimg.cc/FFn9CSBm/junk-restoration-L5.png'],
    },
    '': {
        'levels': [20, 35, 50, 75, 100],
        'description': 'Play ~ cards in a single game',
        'image_links': [],
    },
}

achievement_sections = {
    'Game': ['Library Card', 'Junk Restoration', 'Amberologist', 'A Gift of Amber', 'Too Much to Protect', 'Reap or Sow']
}

try:
    st.set_page_config(
        page_title="Player Page - KeyTracker",
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
.big-hero-font {
    font-size: 36px !important;
    color: #60b4ff !important;
}
.big-villain-font {
    font-size: 36px !important;
    color: #ff4b4b !important;
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


if 'name' not in st.session_state:
    st.error("You must be logged in to view this page.")
else:
    with st.spinner('Setting up player page...'):
        if 'player_games' not in st.session_state:
            if 'game_log' in st.session_state:
                st.session_state.player_games = st.session_state.game_log.applymap(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)
            else:
                with st.spinner("Getting player games..."):
                    st.session_state.player_games = database.get_user_games(st.session_state.name, trim_lists=True)

        if 'settings' not in st.session_state:
            st.session_state.settings = default_settings

        if 'user_info' not in st.session_state:
            with st.spinner("Getting user info..."):
                st.session_state.user_info = database.get_user(st.session_state.name)
                for setting in default_settings.keys():
                    if setting in st.session_state.user_info:
                        st.session_state.settings[setting] = st.session_state.user_info[setting]

    # c1, c2, c3, c4 = st.columns([22, 1, 1, 1])
    c1, c2, c3, c4 = st.columns([1.5, 11.5, 0.5, 0.5], vertical_alignment='center')
    c1.image(st.session_state.settings['icon_link'])
    c2.markdown(f'<b class="big-hero-font">{st.session_state.name}</b>', unsafe_allow_html=True)
    # c1.markdown(f'<b class="big-hero-font">{st.session_state.name}</b>', unsafe_allow_html=True)
    home = c3.button("🏠")
    if home:
        st.switch_page("Home.py")
    st.write('')
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.subheader("Games")
    c2.subheader("Win-Loss")
    c3.subheader("Winrate")
    c4.subheader("ELO")
    games = len(st.session_state.player_games)
    wins = (st.session_state.player_games['Winner'] == st.session_state.name).sum()
    losses = games - wins
    if wins + losses > 0:
        winrate = round(100*wins / (wins + losses))
    else:
        winrate = '--'
    if 'score' in st.session_state.user_info:
        score = st.session_state.user_info['score']
    else:
        score = 1500

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

    st.divider()
    st.write('')
    st.write('')
    with st.spinner('Getting favorites...'):
        if 'favorite_deck' not in st.session_state:
            st.session_state.favorite_deck = st.session_state.player_games['Deck'].mode()[0]

        if 'favorite_opponent' not in st.session_state:
            st.session_state.favorite_opponent = st.session_state.player_games['Opponent'].mode()[0]

        if 'favorite_set' not in st.session_state or 'sorted_houses' not in st.session_state:
            deck_data = st.session_state.player_games.groupby('Deck').size().reset_index(name='Count')
            deck_data['Dok Data'] = deck_data['Deck'].apply(database.get_dok_cache_deck_name)
            deck_data = deck_data[deck_data['Dok Data'].notna()]

            deck_data['Set'] = deck_data['Dok Data'].apply(lambda dok_data: database.set_conversion_dict[dok_data['Data']['deck']['expansion']][0])
            set_count_sum = deck_data.groupby('Set')['Count'].sum().reset_index(name='Count')
            st.session_state.favorite_set = set_count_sum.loc[set_count_sum['Count'].idxmax(), 'Set']

            deck_data['Houses'] = deck_data['Dok Data'].apply(lambda dok_data: [hd['house'] for hd in dok_data['Data']['deck']['housesAndCards']])
            expanded_deck_games = deck_data.explode('Houses')
            house_winrate_df = expanded_deck_games.groupby('Houses')['Count'].sum().reset_index(name='Count')
            st.session_state.sorted_houses = house_winrate_df.sort_values(by='Count', ascending=False)

    top_3_houses = st.session_state.sorted_houses.head(3)

    c1, c2, c3 = st.columns([1, 2, 0.5])

    c1.markdown(f'<p class="plain-font">Favorite Deck:</p>', unsafe_allow_html=True)
    c2.markdown(f'<b class="plain-font">{st.session_state.favorite_deck}</b>', unsafe_allow_html=True)
    # c3.button('Deck Info')

    c1.markdown(f'<p class="plain-font">Favorite Set:</p>', unsafe_allow_html=True)
    c2.markdown(f'<b class ="{st.session_state.favorite_set}-font">{st.session_state.favorite_set}</b>', unsafe_allow_html=True)

    cols = st.columns([1, 0.15, 0.15, 0.15, 2.05])
    cols[0].markdown(f'<p class="plain-font">Favorite Houses:</p>', unsafe_allow_html=True)
    for i, h in enumerate(top_3_houses['Houses'].values):
        cols[i+1].image(house_dict[h]['Image'])

    c1, c2, c3 = st.columns([1, 2, 0.5])
    c1.markdown(f'<p class="plain-font">Favorite Opponent:</p>', unsafe_allow_html=True)
    c2.markdown(f'<b class="villain-font">{st.session_state.favorite_opponent}</b>', unsafe_allow_html=True)

    st.divider()

    # Calculate Achievements
    name = st.session_state.name

    def amberologist(game_log):
        final_amber_gained = game_log[name]['amber_icons'][-1] + game_log[name]['amber_effect'][-1] + game_log[name]['amber_reaped'][-1] + game_log[name]['steal'][-1]
        for j in range(5):
            if final_amber_gained >= achievement_master_dict['Amberologist']['levels'][4 - j]:
                return 5 - j, final_amber_gained
        return 0, final_amber_gained


    def reap_or_sow(game_log):
        reaps = game_log[name]['amber_reaped'][-1]
        for j in range(5):
            if reaps >= achievement_master_dict['Reap or Sow']['levels'][4 - j]:
                return 5 - j, reaps
        return 0, reaps


    def a_gift_of_amber(game_log):
        icons = game_log[name]['amber_icons'][-1]
        for j in range(5):
            if icons >= achievement_master_dict['A Gift of Amber']['levels'][4 - j]:
                return 5 - j, icons
        return 0, icons


    def too_much_to_protect(game_log):
        steal = game_log[name]['steal'][-1]
        for j in range(5):
            if steal >= achievement_master_dict['Too Much to Protect']['levels'][4 - j]:
                return 5 - j, steal
        return 0, steal

    def library_card(game_log):
        cards_played = game_log[name]['cards_played'][-1]
        for j in range(5):
            if cards_played >= achievement_master_dict['Library Card']['levels'][4 - j]:
                return 5 - j, cards_played
        return 0, cards_played

    def junk_restoration(game_log):
        cards_discarded = game_log[name]['cards_discarded'][-1]
        for j in range(5):
            if cards_discarded >= achievement_master_dict['Junk Restoration']['levels'][4 - j]:
                return 5 - j, cards_discarded
        return 0, cards_discarded

    achievement_func_dict = {
        'Amberologist': amberologist,
        'Reap or Sow': reap_or_sow,
        'A Gift of Amber': a_gift_of_amber,
        'Too Much to Protect': too_much_to_protect,
        'Library Card': library_card,
        'Junk Restoration': junk_restoration,
    }

    @st.cache_resource
    def calculate_achievements(achievement_list):
        temp_achievements = {}
        notifs = []

        with st.spinner('Calculating temp_achievements...'):
            for idx, row in st.session_state.player_games.iterrows():
                for a in achievement_func_dict.keys():
                    result, stat = achievement_func_dict[a](row['Game Log'])
                    if stat and a not in temp_achievements:
                        temp_achievements[a] = {'level': 0, 'stat': stat}
                    if result and a in temp_achievements and temp_achievements[a]['level'] < result:
                        temp_achievements[a]['level'] = result
                        achievement_string = f"{a}_{result}"
                        if achievement_string in achievement_list:
                            pass
                        else:
                            if result > 1:
                                notifs.append(f'Achievement Earned: **{a} Lv.{result}**')
                                achievement_list.append(achievement_string)
                            else:
                                notifs.append(f'Achievement Earned: **{a}**')
                                achievement_list.append(achievement_string)

                    if stat and stat > temp_achievements[a]['stat']:
                        temp_achievements[a]['stat'] = stat

        return temp_achievements, notifs, achievement_list


    if 'quest_notifications' not in st.session_state:
        with st.spinner('Calculating achievements...'):
            achievements, quest_notifications, achievement_data_list = calculate_achievements(st.session_state.settings['achievements'])
            st.session_state.quest_notifications = quest_notifications
            st.session_state.achievements = achievements
            st.session_state.settings['achievements'] = achievement_data_list
            with st.spinner("Saving achievements..."):
                database.update_user_settings(st.session_state.name, {'achievements': achievement_data_list})

    if len(st.session_state.quest_notifications) > 0:
        if len(st.session_state.quest_notifications) > 5:
            st.toast(f'**{len(st.session_state.quest_notifications)}** Achievements Earned', icon=':material/done_all:')
        else:
            for notif in st.session_state.quest_notifications:
                st.toast(notif, icon=':material/check:')

        st.session_state.quest_notifications = []

    achievements = st.session_state.achievements
    # Settings Section
    st.header('Settings')
    with st.expander('Icon'):
        cols = st.columns(10)
        last_col = 0
        row_num = 0
        for a, v in achievements.items():
            image_links = achievement_master_dict[a]['image_links']
            for j in range(v['level']):
                if len(image_links) > j:
                    cols[last_col].image(image_links[j])
                    if cols[last_col].button(' Set Icon ', key=f'pp_button_{row_num}-{last_col}'):
                        database.update_user_settings(st.session_state.name, {'icon_link': image_links[j]})
                        st.session_state.settings['icon_link'] = image_links[j]
                        st.toast(f'Updated Icon: **{a}**')
                    last_col += 1
                    if last_col > 9:
                        last_col = 0
                        row_num += 1

    with st.expander('Data'):
        with st.container(border=True):
            game_data_use = st.toggle('I consent to my games being used for aggregate data (your individual games/decks are still private)', value=st.session_state.settings['game_data_use'])

        with st.container(border=True):
            show_decks = st.toggle('I want my decks to show up on the leaderboard', value=st.session_state.settings['show_decks'])

        with st.container(border=True):
            show_player = st.toggle('I want my player stats to show up on the leaderboard', value=st.session_state.settings['show_player'])

        # with st.container(border=True):
        #     show_player_page = st.toggle('I want my Player Page to be public', value=st.session_state.settings['show_player_page'])

    with st.expander('Display'):
        with st.container(border=True):
            if st.session_state.settings['board_layout'] == 'tco':
                ctd = False
            else:
                ctd = True
            compact_turn_display = st.toggle('Compact turn display', value=ctd)

        with st.container(border=True):
            contrast_amber_charts = st.toggle('High contrast amber charts', value=st.session_state.settings['high_contrast'])

    st.write('')
    if st.button('Save'):
        setting_dict = {'game_data_use': game_data_use, 'show_decks': show_decks, 'show_player': show_player, 'high_contrast': contrast_amber_charts}
        if compact_turn_display:
            setting_dict['board_layout'] = 'compact'
        else:
            setting_dict['board_layout'] = 'tco'

        database.update_user_settings(st.session_state.name, setting_dict)
        for setting in setting_dict.keys():
            st.session_state.settings[setting] = setting_dict[setting]
        st.success('Settings saved!')

    st.divider()

    # Achievement Section
    st.header('Achievements')

    with st.expander(fr"$\texttt{{\large Game}}$"):
        for a in achievement_sections['Game']:
            image_links = achievement_master_dict[a]['image_links']
            if a in achievements:
                current_level = achievements[a]['level']
            else:
                current_level = 0

            if current_level == 0:
                starting_number = 0
            else:
                starting_number = achievement_master_dict[a]['levels'][current_level-1]
            goal_number = achievement_master_dict[a]['levels'][current_level]
            current_stat = achievements[a]['stat']
            image_link = image_links[current_level]

            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 8, 0.8], vertical_alignment='bottom')
                c1.image(image_link)
                c2.markdown(f'<b class="plain-font">{a}</b>', unsafe_allow_html=True)
                c2.caption(f'**{achievement_master_dict[a]["description"].replace("~", f":orange[{goal_number}]")}**')
                try:
                    c2.progress((current_stat - starting_number) / (goal_number - starting_number), '')
                except:
                    st.toast(f"Stat Error - C: {current_stat} G: {goal_number} S: {starting_number} ({a})")
                c3.write(f':orange[{current_stat}/{goal_number}]')

    # with st.expander(fr"$\texttt{{\large House}}$"):
    #     with st.container(border=True):
    #         c1, c2, c3 = st.columns([1, 8, 0.8], vertical_alignment='bottom')
    #         c1.image('https://i.imgur.com/uLxY9Zy.png')
    #         c2.markdown(f'<b class="plain-font">Brobnar Loyalist</b>', unsafe_allow_html=True)
    #         c2.caption('**Win :orange[1] games while only calling house Brobnar**')
    #         c2.progress(0, '')
    #         c3.write(':orange[0/1]')

    # with st.expander(fr"$\texttt{{\large Secret}}$"):
    #     with st.container(border=True):
    #         c1, c2, c3 = st.columns([1, 8, 0.8], vertical_alignment='bottom')
    #         c1.image('https://i.imgur.com/OGN7Gj5.png')
    #         c2.markdown(f'<b class="plain-font">Assert Dominance</b>', unsafe_allow_html=True)
    #         c2.caption('**Win :orange[3] games with a final Amber Defense Score of 100**')
    #         c2.progress(0.66, '')
    #         c3.write(':orange[2/3]')



