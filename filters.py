import pandas as pd


def filter_first_player(df: pd.DataFrame, username: str, aliases: list, *args, **kwargs):
    names = [username] + aliases
    if 'Going First' in args:
        df = df.loc[df['Starting Player'].isin(names)]
    elif 'Going Second' in args:
        df = df.loc[~df['Starting Player'].isin(names)]

    return df


def filter_outcome(df: pd.DataFrame, username: str, aliases: list, *args, **kwargs):
    names = [username] + aliases
    if 'Victory' in args:
        df = df.loc[df['Winner'].isin(names)]
    elif 'Defeat' in args:
        df = df.loc[~df['Winner'].isin(names)]

    return df


def filter_card(df: pd.DataFrame, username: str, aliases: list, *args, **kwargs):
    names = [username] + aliases
    if 'I Played' in args:
        df = df.loc[df['Game Log'][username]]

    return df

filter_dict = {
    'First Player': filter_first_player,
    'Outcome': filter_outcome,
}


# SAMPLE IMPLEMENTATION CODE

def _():
    with st.expander('Filter Games'):
        if 'filter_count' not in st.session_state:
            st.session_state.filter_count = 1

        c1, c2, c3, _ = st.columns([1, 1, 2, 18])

        if c1.button('➕'):
            st.session_state.filter_count += 1

        if c2.button('➖'):
            st.session_state.filter_count = max(0, st.session_state.get('filter_count', 1) - 1)

        if c3.button('Apply'):
            pass

        house_list = graphing.house_dict.keys()
        expansion_list = [ex[0] for ex in database.set_conversion_dict.values()]
        card_list = list(dok_api.card_rarity_dict.keys())

        sub_select_options = {
            'First Player': {
                'multi_select': False,
                'sub_options': [
                    'Going First',
                    'Going Second'
                ],
            },
            'Outcome': {
                'multi_select': False,
                'sub_options': [
                    'Victory',
                    'Defeat'
                ],
            },
            'Set': {
                'multi_select': False,
                'sub_options': {
                    'Include ONLY these sets': {
                        'multi_select': True,
                        'sub_options': expansion_list
                    },
                    'Include NONE of these sets': {
                        'multi_select': True,
                        'sub_options': expansion_list
                    },
                }
            },
            'House': {
                'multi_select': False,
                'sub_options': {c: {'multi_select': True, 'sub_options': house_list} for c in ['Include ONLY', 'Include NONE of', 'Include AT LEAST 1 of']}
            },
            'Card': {
                'multi_select': False,
                'sub_options': {c: {'multi_select': False, 'sub_options': {c: {'multi_select': True, 'sub_options': card_list} for c in ['ALL of', 'NONE of', 'AT LEAST 1 of']}} for c in ['I played', 'Opponent played', 'Anyone played']}
            },

        }

        filter_selections = collections.defaultdict(dict)

        filters = []

        for f_idx in range(st.session_state.filter_count):
            filter_cols = st.columns([0.15, 0.5, 1, 1, 1], vertical_alignment='top')
            if filter_cols[0].button('❌', key=f"remove_filter_{f_idx}"):
                pass
            filter_type = filter_cols[1].selectbox(label=f"filter_1_{f_idx}", options=sub_select_options.keys(), label_visibility='collapsed')
            filter_selections[f_idx][1] = filter_type
            current_level_idx = 2
            level_info = sub_select_options[filter_type]
            while current_level_idx <= len(filter_cols) - 1:
                if level_info['multi_select']:
                    f_selection = filter_cols[current_level_idx].multiselect(label=f"filter_{current_level_idx}_{f_idx}", options=level_info['sub_options'], label_visibility='collapsed')
                else:
                    f_selection = filter_cols[current_level_idx].selectbox(label=f"filter_{current_level_idx}_{f_idx}", options=level_info['sub_options'], label_visibility='collapsed')

                filter_selections[f_idx][current_level_idx] = f_selection

                if not isinstance(level_info['sub_options'], dict):
                    break
                else:
                    current_level_idx += 1
                    level_info = level_info['sub_options'][f_selection]

            # level_2 = sub_select_options[filter_type]
            # if level_2['multi_select']:
            #     level_2_selection = c2.multiselect(label=f"filter_2_{f_idx}", options=level_2['sub_options'], label_visibility='collapsed')
            # else:
            #     level_2_selection = c2.selectbox(label=f"filter_2_{f_idx}", options=level_2['sub_options'], label_visibility='collapsed')
            #
            # if isinstance(level_2['sub_options'], list):
            #     pass
            # else:
            #     level_3 = level_2['sub_options'][level_2_selection]
            #
            #     if level_3['multi_select']:
            #         level_3_selection = c3.multiselect(label=f"filter_3_{f_idx}", options=level_3['sub_options'], label_visibility='collapsed')
            #     else:
            #         level_3_selection = c3.selectbox(label=f"filter_3_{f_idx}", options=level_3['sub_options'], label_visibility='collapsed')


