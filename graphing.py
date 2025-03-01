import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import random
import ast
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import math

import dok_api

house_colors = {
    "brobnar": (242, 113, 34),
    "dis": (223, 32, 120),
    "ekwidon": (115, 201, 189),
    "logos": (95, 199, 230),
    "mars": (104, 190, 68),
    "sanctum": (5, 116, 179),
    "untamed": (9, 123, 68),
    "unfathomable": (58, 69, 138),
    "shadows": (249, 196, 40),
    "staralliance": (250, 200, 80),
    "saurian": (232, 194, 60),
    "geistoid": (115, 75, 136),
    "skyborn": (241, 235, 210),
    "redemption": (212, 39, 52),
}


house_dict = {
    'Brobnar': {
        'Image': 'https://archonarcana.com/images/thumb/e/e0/Brobnar.png/105px-Brobnar.png',
        'Color': '#000000'
    },
    'Logos': {
        'Image': 'https://archonarcana.com/images/thumb/c/ce/Logos.png/105px-Logos.png',
        'Color': '#000000'
    },
    'Shadows': {
        'Image': 'https://archonarcana.com/images/thumb/e/ee/Shadows.png/105px-Shadows.png',
        'Color': '#000000'
    },
    'Sanctum': {
        'Image': 'https://archonarcana.com/images/thumb/c/c7/Sanctum.png/105px-Sanctum.png',
        'Color': '#000000'
    },
    'Mars': {
        'Image': 'https://archonarcana.com/images/thumb/d/de/Mars.png/105px-Mars.png',
        'Color': '#000000'
    },
    'Dis': {
        'Image': 'https://archonarcana.com/images/thumb/e/e8/Dis.png/105px-Dis.png',
        'Color': '#000000'
    },
    'Untamed': {
        'Image': 'https://archonarcana.com/images/thumb/b/bd/Untamed.png/105px-Untamed.png',
        'Color': '#000000'
    },
    'Saurian': {
        'Image': 'https://archonarcana.com/images/9/9e/Saurian_P.png',
        'Color': '#000000'
    },
    'StarAlliance': {
        'Image': 'https://archonarcana.com/images/thumb/7/7d/Star_Alliance.png/105px-Star_Alliance.png',
        'Color': '#000000'
    },
    'Ekwidon': {
        'Image': 'https://archonarcana.com/images/thumb/3/31/Ekwidon.png/105px-Ekwidon.png',
        'Color': '#000000'
    },
    'Unfathomable': {
        'Image': 'https://archonarcana.com/images/thumb/1/10/Unfathomable.png/105px-Unfathomable.png',
        'Color': '#000000'
    },
    'Geistoid': {
        'Image': 'https://archonarcana.com/images/thumb/4/48/Geistoid.png/105px-Geistoid.png',
        'Color': '#000000'
    },
    'Skyborn': {
        'Image': 'https://archonarcana.com/images/0/06/Skyborn.png',
        'Color': '#000000'
    },
    'Redemption': {
        'Image': 'https://decksofkeyforge.com/static/media/redemption.89858e305d408ad683ca.png',
        'Color': '#000000'
    }
}


set_dict = {
    'CotA': {
        'Image': 'https://decksofkeyforge.com/static/media/cota-dark.07e0e2bc9a12461d3e696422cbf9351d.svg',
        'Color': '#d92b34',
        'Full Name': 'CALL_OF_THE_ARCHONS',
    },
    'AoA': {
        'Image': 'https://decksofkeyforge.com/static/media/aoa-dark.5b9932d1a46bae1af4b72affdc216a60.svg',
        'Color': '#259adb',
        'Full Name': 'AGE_OF_ASCENSION',
    },
    'WC': {
        'Image': 'https://decksofkeyforge.com/static/media/wc-dark.28c626544d41d4ae0a23c408e0ce9341.svg',
        'Color': '#ad39a5',
        'Full Name': 'WORLDS_COLLIDE',
    },
    'MM': {
        'Image': 'https://decksofkeyforge.com/static/media/mm-dark.eb97671dd686e77d4befdb66d8532f5f.svg',
        'Color': '#e94e76',
        'Full Name': 'MASS_MUTATION',
    },
    'DT': {
        'Image': 'https://decksofkeyforge.com/static/media/dt-dark.17fe0a29b6699f9583a09111b6f03402.svg',
        'Color': '#136697',
        'Full Name': 'DARK_TIDINGS',
    },
    'WoE': {
        'Image': 'https://decksofkeyforge.com/static/media/woe-dark.6498ca6ef89a26a1685e068b8969f37d.svg',
        'Color': '#0c9aa8',
        'Full Name': 'WINDS_OF_EXCHANGE',
    },
    'GR': {
        'Image': 'https://decksofkeyforge.com/static/media/gr-dark.d713c39aca369e78957eea6597c6f02f.svg',
        'Color': '#0c4f7f',
        'Full Name': 'GRIM_REMINDERS',
    },
    'AES': {
        'Image': 'https://decksofkeyforge.com/static/media/gr-dark.d713c39aca369e78957eea6597c6f02f.svg',
        'Color': '#f1ebd2',
        'Full Name': 'AEMBER_SKIES',
    },
    'ToC': {
        'Image': 'https://decksofkeyforge.com/static/media/gr-dark.d713c39aca369e78957eea6597c6f02f.svg',
        'Color': '#ea2e46',
        'Full Name': 'TOKENS_OF_CHANGE',
    },
    'MMM': {
        'Image': 'https://decksofkeyforge.com/static/media/mm-dark.eb97671dd686e77d4befdb66d8532f5f.svg',
        'Color': '#e94e76',
        'Full Name': 'MORE_MUTATION',
    },
    'VM23': {
        'Image': 'https://decksofkeyforge.com/static/media/vm23-dark.d797a995bef735704fac3c8c41e1c134.svg',
        'Color': '#838383',
        'Full Name': 'VAULT_MASTERS_2023',
    },
    'VM24': {
        'Image': 'https://decksofkeyforge.com/static/media/vm23-dark.d797a995bef735704fac3c8c41e1c134.svg',
        'Color': '#838383',
        'Full Name': 'VAULT_MASTERS_2024',
    },

}


def hex_to_rgb(hex_color, alpha=1):
    hex_color = hex_color.lstrip('#')
    rgb_tuple = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f'rgba({", ".join(map(str, rgb_tuple))}, {alpha})'


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


def get_turn_played(player_data, card_name, analysis_type='replay'):
    if analysis_type == 'replay':
        return next((i for i, d in enumerate(player_data['individual_cards_played']) if card_name in d), -1) + 1
    else:
        return player_data['turn_played'][-1].get(card_name, 0)


def calculate_ttw(player_tav, player_data, opponent_amber_defense):
    ttw = []
    amber_deltas = []
    reap_rates = []
    for i in range(len(player_tav)):
        amber_remaining = 18 - player_tav[i]
        keys = player_data['keys'][i]
        avg_creatures = sum(player_data['creatures'][:i]) / (i+1)
        if avg_creatures > 0:
            reap_rate = player_data['amber_reaped'][i] / (((i+1) * avg_creatures) / 2)
        else:
            reap_rate = None
        amber_delta = (player_data['amber_icons'][i] + player_data['amber_effect'][i] + player_data['steal'][i]) / ((i+1) / 2)
        if reap_rate is not None:
            divisor = (player_data['creatures'][i] * reap_rate + amber_delta) * (1 - opponent_amber_defense / 100)
        else:
            divisor = 0
        if divisor > 0:
            turns_remaining = amber_remaining / ((player_data['creatures'][i] * reap_rate + amber_delta) * (1 - opponent_amber_defense / 100))
        else:
            turns_remaining = 25
        ttw.append(max(min(turns_remaining, 25), 3-keys))
        reap_rates.append(reap_rate)
        amber_deltas.append(amber_delta)

    return ttw, amber_deltas, reap_rates


def calculate_reap_rate(player_data, games=1):
    avg_creatures = sum(player_data['creatures']) / len(player_data['creatures'])
    reap_rate = (games * player_data['amber_reaped'][-1] / (len(player_data['house_calls'])) / avg_creatures)
    return reap_rate


def calculate_amber_delta(player_data, games=1):
    total_delta_amber = player_data['amber_icons'][-1] + player_data['amber_effect'][-1] + player_data['steal'][-1]
    amber_delta = games * total_delta_amber / len(player_data['house_calls'])
    return amber_delta


def calculate_ex_amber(player_data, opponent_data, first_player, opponent_name, games=1):
    op_exa = []
    player_exa = []

    player_tav, opponent_tav, p_amber_gained, op_amber_gained, p_amber_defense, op_amber_defense, p_forge_rate, op_forge_rate = calculate_tav(player_data, opponent_data)
    turns = len(opponent_data['amber'])
    player_delta = calculate_amber_delta(player_data, games)
    player_creatures = player_data['creatures']
    player_reap_rate = calculate_reap_rate(player_data, games)
    opponent_delta = calculate_amber_delta(opponent_data, games)
    opponent_creatures = opponent_data['creatures']
    opponent_reap_rate = calculate_reap_rate(opponent_data, games)

    if first_player == opponent_name:
        op_sval = 0
    else:
        op_sval = 1

    for i in range(turns):
        if i % 2 == op_sval:
            if len(op_exa) == 0:
                op_exa.append(0.5)
            else:
                op_exa.append(op_exa[-1] + opponent_delta + opponent_creatures[i - 1] * opponent_reap_rate)
            if len(player_exa) == 0:
                player_exa.append(0)
            else:
                player_exa.append(player_exa[-1])
        else:
            if len(player_exa) == 0:
                player_exa.append(0.5)
            else:
                player_exa.append(player_exa[-1] + player_delta + player_creatures[i - 1] * player_reap_rate)
            if len(op_exa) == 0:
                op_exa.append(0)
            else:
                op_exa.append(op_exa[-1])

    p_def_adj = sum(player_tav) / sum(player_exa)
    op_def_adj = sum(opponent_tav) / sum(op_exa)

    player_exa = [a * p_def_adj for a in player_exa]
    op_exa = [a * op_def_adj for a in op_exa]

    return player_exa, op_exa, 1-op_def_adj, 1-p_def_adj


def analyze_deck(username, log, games, high_contrast=False):
    player_data = log[username]
    opponent_data = log['opponent']

    deck_analysis_data = create_deck_analysis_graphs(player_data, username, opponent_data, 'opponent', games, high_contrast)

    return deck_analysis_data


def create_deck_analysis_graphs(player_data, username, opponent_data, opponent_name, games, high_contrast=False):
    player_tav, opponent_tav, p_amber_gained, op_amber_gained, p_amber_defense, op_amber_defense, p_forge_rate, op_forge_rate = calculate_tav(player_data, opponent_data)
    player_ttw, player_delta, player_reap_rate = calculate_ttw(player_tav, player_data, op_amber_defense[-1])
    opponent_ttw, opponent_delta, opponent_reap_rate = calculate_ttw(opponent_tav, opponent_data, p_amber_defense[-1])
    p_values = [player_data['total_amber_effect'][-1], player_data['total_steal'][-1], player_data['total_amber_reaped'][-1], player_data['total_amber_icons'][-1]]
    op_values = [opponent_data['total_amber_effect'][-1], opponent_data['total_steal'][-1], opponent_data['total_amber_reaped'][-1], opponent_data['total_amber_icons'][-1]]
    player_amber_sources = amber_sources(p_values, max(p_values + op_values), username, 'replay', contrast=high_contrast)
    opponent_amber_sources = amber_sources(op_values, max(p_values + op_values), opponent_name, 'replay', contrast=high_contrast)
    if games >= 10:
        min_threshold = round(games/12)
    else:
        min_threshold = 1
    player_house_calls = make_house_image_deck(player_data['house_calls'], min_threshold=min_threshold)
    opponent_house_calls = make_house_image_deck(opponent_data['house_calls'], min_threshold=min_threshold, player_graph=False)
    player_card_data = get_card_information(player_data, analysis_type='Deck')
    opponent_card_data = get_card_information(opponent_data, analysis_type='Deck')
    player_survival_rate = calculate_deck_survival_rate(player_data)
    opponent_survival_rate = calculate_deck_survival_rate(opponent_data)
    normalized_turns = normalize_turns(player_data['turns'])
    # Precompute Reap Advantage
    # reap_advantage = [
    #     min(25, max(1,
    #                 (18 - (opponent_amber or 0)) /
    #                 (1 - (player_defense or 0) / 100) *
    #                 ((opponent_creatures or 0) * (opponent_reap_rate or 0) + (opponent_delta or 0))
    #                 )) -
    #     min(25, max(1,
    #                 (18 - ((player_amber or 0) + 1)) /
    #                 (1 - (opponent_defense or 0) / 100) *
    #                 ((player_creatures or 0) * (player_reap_rate or 0) + (player_delta or 0))
    #                 ))
    #     for opponent_amber, player_defense, opponent_creatures, opponent_reap_rate, opponent_delta,
    #         player_amber, opponent_defense, player_creatures, player_reap_rate, player_delta
    #     in zip(opponent_tav, p_amber_defense, opponent_data['creatures'], opponent_reap_rate, opponent_delta,
    #            player_tav, op_amber_defense, player_data['creatures'], player_reap_rate, player_delta)
    # ]
    #
    # # Precompute Kill Advantage
    # kill_advantage = [
    #     min(25, max(1,
    #                 (18 - (opponent_amber or 0)) /
    #                 (1 - (player_defense or 0) / 100) *
    #                 (max(0, (opponent_creatures or 0) - 1) * (opponent_reap_rate or 0) + (opponent_delta or 0))
    #                 )) -
    #     min(25, max(1,
    #                 (18 - (player_amber or 0)) /
    #                 (1 - (opponent_defense or 0) / 100) *
    #                 (player_creatures or 0 * (player_reap_rate or 0) + (player_delta or 0))
    #                 ))
    #     for opponent_amber, player_defense, opponent_creatures, opponent_reap_rate, opponent_delta,
    #         player_amber, opponent_defense, player_creatures, player_reap_rate, player_delta
    #     in zip(opponent_tav, p_amber_defense, opponent_data['creatures'], opponent_reap_rate, opponent_delta,
    #            player_tav, op_amber_defense, player_data['creatures'], player_reap_rate, player_delta)
    # ]
    #
    # # Precompute Trade Advantage
    # trade_advantage = [
    #     min(25, max(1,
    #                 (18 - (opponent_amber or 0)) /
    #                 (1 - (player_defense or 0) / 100) *
    #                 (max(0, (opponent_creatures or 0) - 1) * (opponent_reap_rate or 0) + (opponent_delta or 0))
    #                 )) -
    #     min(25, max(1,
    #                 (18 - (player_amber or 0)) /
    #                 (1 - (opponent_defense or 0) / 100) *
    #                 (max(0, (player_creatures or 0) - 1) * (player_reap_rate or 0) + (player_delta or 0))
    #                 ))
    #     for opponent_amber, player_defense, opponent_creatures, opponent_reap_rate, opponent_delta,
    #         player_amber, opponent_defense, player_creatures, player_reap_rate, player_delta
    #     in zip(opponent_tav, p_amber_defense, opponent_data['creatures'], opponent_reap_rate, opponent_delta,
    #            player_tav, op_amber_defense, player_data['creatures'], player_reap_rate, player_delta)
    # ]
    #
    # # Precompute Reap/Kill Advantage and Reap/Trade Advantage
    # reap_kill_advantage = [reap - kill for reap, kill in zip(reap_advantage, kill_advantage)]
    # reap_trade_advantage = [reap - trade for reap, trade in zip(reap_advantage, trade_advantage)]

    # Create the DataFrame
    game_dataframe = pd.DataFrame({
        'Player Amber': player_tav,
        'Opponent Amber': opponent_tav,
        'Player Amber Defense': p_amber_defense,
        'Opponent Amber Defense': op_amber_defense,
        'Player Forge Rate': p_forge_rate,
        'Opponent Forge Rate': op_forge_rate,
        'Player Cards': player_data['cards_played'],
        'Opponent Cards': opponent_data['cards_played'],
        'Player Creatures': player_data['creatures'],
        'Opponent Creatures': opponent_data['creatures'],
        'Player Survival Rate': player_survival_rate,
        'Opponent Survival Rate': opponent_survival_rate,
        'Player Prediction': player_ttw,
        'Opponent Prediction': opponent_ttw,
        'Player Delta': player_delta,
        'Opponent Delta': opponent_delta,
        'Player Reap Rate': player_reap_rate,
        'Opponent Reap Rate': opponent_reap_rate,
        # 'Reap Advantage': reap_advantage,
        # 'Kill Advantage': kill_advantage,
        # 'Trade Advantage': trade_advantage,
        # 'Reap/Kill Advantage': reap_kill_advantage,
        # 'Reap/Trade Advantage': reap_trade_advantage
    })
    # game_dataframe = pd.DataFrame({'Player Amber': player_tav, 'Opponent Amber': opponent_tav, 'Player Amber Defense': p_amber_defense, 'Opponent Amber Defense': op_amber_defense, 'Player Cards': player_data['cards_played'], 'Opponent Cards': opponent_data['cards_played'], 'Player Creatures': player_data['creatures'], 'Opponent Creatures': opponent_data['creatures'], 'Player Survival Rate': player_survival_rate, 'Opponent Survival Rate': opponent_survival_rate, 'Player Prediction': player_ttw, 'Opponent Prediction': opponent_ttw, 'Player Delta': player_delta, 'Opponent Delta': opponent_delta, 'Player Reap Rate': player_reap_rate, 'Opponent Reap Rate': opponent_reap_rate})
    # game_dataframe['Reap Advantage'] = min(25, max(1, (18 - game_dataframe['Opponent Amber']) / (1-game_dataframe['Player Amber Defense']/100)*(game_dataframe['Opponent Creatures'] * game_dataframe['Opponent Reap Rate'] + game_dataframe['Opponent Delta']))) - min(25, max(1, (18 - (game_dataframe['Player Amber'] + 1)) / (1-game_dataframe['Opponent Amber Defense']/100)*(game_dataframe['Player Creatures'] * game_dataframe['Player Reap Rate'] + game_dataframe['Player Delta'])))
    # game_dataframe['Kill Advantage'] = min(25, max(1, (18 - game_dataframe['Opponent Amber']) / (1-game_dataframe['Player Amber Defense']/100)*(max(0, game_dataframe['Opponent Creatures'] - 1) * game_dataframe['Opponent Reap Rate'] + game_dataframe['Opponent Delta']))) - min(25, max(1, (18 - game_dataframe['Player Amber']) / (1-game_dataframe['Opponent Amber Defense']/100)*(game_dataframe['Player Creatures'] * game_dataframe['Player Reap Rate'] + game_dataframe['Player Delta'])))
    # game_dataframe['Trade Advantage'] = min(25, max(1, (18 - game_dataframe['Opponent Amber']) / (1-game_dataframe['Player Amber Defense']/100)*(max(0, game_dataframe['Opponent Creatures'] - 1) * game_dataframe['Opponent Reap Rate'] + game_dataframe['Opponent Delta']))) - min(25, max(1, (18 - game_dataframe['Player Amber']) / (1-game_dataframe['Opponent Amber Defense']/100)*(max(0, game_dataframe['Player Creatures'] - 1) * game_dataframe['Player Reap Rate'] + game_dataframe['Player Delta'])))
    # game_dataframe['Reap/Kill Advantage'] = game_dataframe['Reap Advantage'] - game_dataframe['Kill Advantage']
    # game_dataframe['Reap/Trade Advantage'] = game_dataframe['Reap Advantage'] - game_dataframe['Trade Advantage']
    idx = next((i for i, v in enumerate(normalized_turns) if v <= 10), None)
    game_dataframe = game_dataframe[:idx]

    advantage_graphs = []
    advantage_stats = ['Amber', 'Cards', 'Prediction', 'Creatures', 'Delta', 'Reap Rate', 'Amber Defense', 'Survival Rate']
    advantage_reverse = [False] * len(advantage_stats)
    advantage_reverse[2] = True

    for stat, reverse in zip(advantage_stats, advantage_reverse):
        if reverse:
            game_dataframe[f'{stat} Advantage'] = game_dataframe[f'Opponent {stat}'] - game_dataframe[f'Player {stat}']
        else:
            game_dataframe[f'{stat} Advantage'] = game_dataframe[f'Player {stat}'] - game_dataframe[f'Opponent {stat}']

        advantage_graphs.append(advantage_chart(game_dataframe[f'{stat} Advantage']))

    return game_dataframe, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, advantage_graphs, player_card_data, opponent_card_data, normalized_turns


def normalize_turns(turns):
    max_turns = turns[0]
    normalized_turns = [round(100*t/max_turns) for t in turns]
    return normalized_turns


def calculate_tide(player_data):
    if 'tide_value' in player_data:
        return player_data['tide_value']
    else:
        return None


def calculate_deck_survival_rate(player_data):
    survival_rate = []
    for i in range(len(player_data['survives'])):
        s = sum(player_data['survives'][:i+1])
        d = sum(player_data['deaths'][:i+1])
        if s + d > 0:
            survival_rate.append(round(100 * s / (s + d)))
            survival_rate.append(round(100 * s / (s + d)))
        else:
            survival_rate.append(0)
            survival_rate.append(0)

    if len(player_data['creatures']) > len(survival_rate):
        for _ in range(len(player_data['creatures']) - len(survival_rate)):
            survival_rate.append(survival_rate[-1])
    elif len(survival_rate) > len(player_data['creatures']):
        survival_rate = survival_rate[:len(player_data['creatures'])]

    return survival_rate


def calculate_survival_rate(player_data, player_second=True):
    survives = []
    deaths = []
    survival_rates = []
    individual_survives = {}
    individual_deaths = {}
    individual_survival_rates = {}
    for i in range(player_second, len(player_data['creatures']), 2):
        creatures_turn = player_data['creatures'][i]
        board_turn = player_data['board'][i]
        if len(player_data['creatures']) > i+1:
            next_creatures_turn = player_data['creatures'][i+1]
            next_board_turn = player_data['board'][i+1]

            deaths_turn = max(creatures_turn - next_creatures_turn, 0)

            board_frequency_dict = dict(Counter(board_turn))

            for c, num in board_frequency_dict.items():
                card_survives = min(next_board_turn.count(c), num)
                card_deaths = max(num - next_board_turn.count(c), 0)

                if c not in individual_survives:
                    individual_survives[c] = []
                    individual_deaths[c] = []
                    individual_survival_rates[c] = []

                individual_survives[c].append(card_survives)
                individual_deaths[c].append(card_deaths)
                total_survives = sum(individual_survives[c])
                total_deaths = sum(individual_deaths[c])

                if total_survives + total_deaths > 0:
                    individual_survival_rate = max(0, min(100, round(100 * total_survives / (total_survives + total_deaths))))
                else:
                    individual_survival_rate = None

                individual_survival_rates[c].append(individual_survival_rate)
                individual_survival_rates[c].append(individual_survival_rate)

            survives.append(min(next_creatures_turn, creatures_turn))
            deaths.append(deaths_turn)

            total_survives = sum(survives)
            total_deaths = sum(deaths)
            if total_survives + total_deaths > 0:
                survival_rate = max(0, min(100, round(100 * total_survives / (total_survives + total_deaths))))
            else:
                survival_rate = None

            survival_rates.append(survival_rate)
            survival_rates.append(survival_rate)

    if len(survival_rates) > 0:
        for _ in range(len(player_data['creatures']) - len(survival_rates)):
            survival_rates.append(survival_rates[-1])
    else:
        for _ in range(len(player_data['creatures'])):
            survival_rates.append(None)

    return survival_rates, survives, deaths, individual_survival_rates, individual_survives, individual_deaths


# def calculate_survival_rate(player_data):
#     creatures_played = []
#     individual_cards_played = player_data['individual_cards_played']
#     for i, card_list in enumerate(individual_cards_played):
#         creatures_played_turn = 0
#
#         if i == 0:
#             card_list_turn = card_list
#         else:
#             card_list_turn = subtract_dicts(individual_cards_played[i-1], card_list)
#
#         if len(card_list_turn) > 0:
#             for card, copies in card_list_turn.items():
#                 card_type = dok_api.check_card_type(card)
#                 if card_type == 'Creature':
#                     creatures_played_turn += copies
#
#         creatures_played.append(creatures_played_turn)
#
#     survives = []
#     deaths = []
#     survival_rates = []
#     for i in range(len(player_data['creatures'])):
#         creatures_turn = player_data['creatures'][i]
#         new_creatures_turn = creatures_played[i]
#         survives_turn = creatures_turn - new_creatures_turn
#         if i > 0:
#             deaths_turn = new_creatures_turn + player_data['creatures'][i-1] - creatures_turn
#         else:
#             deaths_turn = 0
#         survives.append(survives_turn)
#         deaths.append(deaths_turn)
#
#         total_survives = sum(survives)
#         total_deaths = sum(deaths)
#         if total_survives + total_deaths > 0:
#             survival_rate = min(100, round(100 * total_survives / (total_survives + total_deaths)))
#             survival_rate = max(0, survival_rate)
#         else:
#             survival_rate = None
#
#         survival_rates.append(survival_rate)
#
#     return survival_rates


def analyze_game(username, game_data, high_contrast=False):

    log = game_data['Game Log'][0]
    player_data = log[username]
    first_player = game_data['Starting Player'][0]

    opponent_name = [n for n in log.keys() if n != username and n != 'player_hand'][0]
    opponent_data = log[opponent_name]
    game_analysis_data = create_game_analysis_graphs(player_data, username, opponent_data, opponent_name, first_player, high_contrast)

    return game_analysis_data


def create_game_analysis_graphs(player_data, username, opponent_data, opponent_name, first_player, high_contrast=False):
    player_tav, opponent_tav, p_amber_gained, op_amber_gained, p_amber_defense, op_amber_defense, p_forge_rate, op_forge_rate = calculate_tav(player_data, opponent_data)
    player_ttw, player_delta, player_reap_rate = calculate_ttw(player_tav, player_data, op_amber_defense[-1])
    opponent_ttw, opponent_delta, opponent_reap_rate = calculate_ttw(opponent_tav, opponent_data, p_amber_defense[-1])
    p_values = [player_data['amber_effect'][-1], player_data['steal'][-1], player_data['amber_reaped'][-1], player_data['amber_icons'][-1]]
    op_values = [opponent_data['amber_effect'][-1], opponent_data['steal'][-1], opponent_data['amber_reaped'][-1], opponent_data['amber_icons'][-1]]
    player_amber_sources = amber_sources(p_values, max(p_values + op_values), username, 'replay', high_contrast)
    opponent_amber_sources = amber_sources(op_values, max(p_values + op_values), opponent_name, 'replay', high_contrast)
    player_house_calls = make_house_image(player_data['house_calls'])
    opponent_house_calls = make_house_image(opponent_data['house_calls'], player_graph=False)

    if first_player == username:
        op_second = True
        p_second = False
    else:
        op_second = False
        p_second = True
    player_survival_rate, s, d, player_individual_survival_rates, ind_s, ind_d = calculate_survival_rate(player_data, p_second)
    opponent_survival_rate, s, d, opponent_individual_survival_rates, ind_s, ind_d = calculate_survival_rate(opponent_data, op_second)
    player_card_data = get_card_information(player_data, player_individual_survival_rates)
    opponent_card_data = get_card_information(opponent_data, opponent_individual_survival_rates)
    tide = calculate_tide(player_data)
    game_dataframe = pd.DataFrame({'Player Amber': player_tav, 'Opponent Amber': opponent_tav, 'Player Amber Gained': p_amber_gained, 'Opponent Amber Gained': op_amber_gained, 'Player Amber Defense': p_amber_defense, 'Opponent Amber Defense': op_amber_defense, 'Player Forge Rate': p_forge_rate, 'Opponent Forge Rate': op_forge_rate, 'Player Cards': player_data['cards_played'], 'Opponent Cards': opponent_data['cards_played'], 'Player Creatures': player_data['creatures'], 'Opponent Creatures': opponent_data['creatures'], 'Player Survival Rate': player_survival_rate, 'Opponent Survival Rate': opponent_survival_rate, 'Player Prediction': player_ttw, 'Opponent Prediction': opponent_ttw, 'Player Delta': player_delta, 'Opponent Delta': opponent_delta, 'Player Reap Rate': player_reap_rate, 'Opponent Reap Rate': opponent_reap_rate})
    if tide:
        game_dataframe['Tide'] = tide
    if 'tokens_created' in player_data:
        if len(player_data['tokens_created']) == len(game_dataframe):
            game_dataframe['Player Tokens'] = player_data['tokens_created']
    if 'tokens_created' in opponent_data:
        if len(opponent_data['tokens_created']) == len(game_dataframe):
            game_dataframe['Opponent Tokens'] = opponent_data['tokens_created']

    advantage_graphs = []
    advantage_stats = ['Amber', 'Cards', 'Prediction', 'Creatures', 'Delta', 'Reap Rate', 'Amber Defense', 'Survival Rate']
    advantage_reverse = [False] * len(advantage_stats)
    advantage_reverse[2] = True

    for stat, reverse in zip(advantage_stats, advantage_reverse):
        if reverse:
            game_dataframe[f'{stat} Advantage'] = game_dataframe[f'Opponent {stat}'] - game_dataframe[f'Player {stat}']
        else:
            game_dataframe[f'{stat} Advantage'] = game_dataframe[f'Player {stat}'] - game_dataframe[f'Opponent {stat}']

        advantage_graphs.append(advantage_chart(game_dataframe[f'{stat} Advantage']))

    return game_dataframe, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, advantage_graphs, player_card_data, opponent_card_data


def calculate_tav(player_data, opponent_data):
    player_tav = [k * 6 + a for k, a in zip(player_data['keys'], player_data['amber'])]
    opponent_tav = [k * 6 + a for k, a in zip(opponent_data['keys'], opponent_data['amber'])]
    p_amber_gained = [player_data['amber_icons'][i] + player_data['amber_reaped'][i] + player_data['amber_effect'][i] + player_data['steal'][i] for i in range(len(player_data['amber_icons']))]
    op_amber_gained = [opponent_data['amber_icons'][i] + opponent_data['amber_reaped'][i] + opponent_data['amber_effect'][i] + opponent_data['steal'][i] for i in range(len(opponent_data['amber_icons']))]
    p_amber_defense = [round(100*(1 - opponent_tav[i] / op_amber_gained[i])) if op_amber_gained[i] > 0 else 0 for i in range(len(opponent_tav))]
    op_amber_defense = [round(100*(1 - player_tav[i] / p_amber_gained[i])) if p_amber_gained[i] > 0 else 0 for i in range(len(player_tav))]
    if 'checks' in player_data:
        if 'checked_keys' in player_data:
            # player_data['checked_keys'].pop(0)
            # opponent_data['checked_keys'].pop(0)
            print(len(player_data['checked_keys']), len(player_data['checks']))
            print(player_data['checks'])
            print(player_data['checked_keys'])
            p_forge_rate = [round(100 * k / c) if c != 0 and k != 0 else None for k, c in zip(player_data['checked_keys'], player_data['checks'])]
            op_forge_rate = [round(100 * k / c) if c != 0 and k != 0 else None for k, c in zip(opponent_data['checked_keys'], opponent_data['checks'])]
        else:
            p_forge_rate = [round(100 * k / c) if c != 0 and k != 0 else None for k, c in zip(player_data['keys'], player_data['checks'])]
            op_forge_rate = [round(100 * k / c) if c != 0 and k != 0 else None for k, c in zip(opponent_data['keys'], opponent_data['checks'])]
    else:
        p_forge_rate = [0 for _ in range(len(player_data['keys']))]
        op_forge_rate = [0 for _ in range(len(opponent_data['keys']))]

    p_forge_rate += [None for _ in range(len(player_tav) - len(p_forge_rate))]
    op_forge_rate += [None for _ in range(len(opponent_tav) - len(op_forge_rate))]

    return player_tav, opponent_tav, p_amber_gained, op_amber_gained, p_amber_defense, op_amber_defense, p_forge_rate, op_forge_rate


def total_amber_value(player_tav, opponent_tav, player_data, opponent_data, opponent_name, first_player, save, games=1):
    x = list(range(max(len(player_tav), len(opponent_tav))))

    player_exa, op_exa, *d_scores = calculate_ex_amber(player_data, opponent_data, first_player, opponent_name, games)

    layout = go.Layout(
        margin=dict(pad=10),
        paper_bgcolor='rgb(5,15,15)',  # set chart background color
        plot_bgcolor='rgb(15,25,25)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}},  # set legend font color
        xaxis={'title': 'Turn', 'titlefont': {'color': 'rgb(225,235,235)'}, 'tickfont': {'color': 'rgb(225,235,235)'}},  # set x axis title
        yaxis={'title': 'Total Amber Value', 'titlefont': {'color': 'rgb(225,235,235)'}, 'tickfont': {'color': 'rgb(225,235,235)'}},  # set y axis title
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(x=x, y=player_tav, name=USERNAME, mode='lines', line=dict(color='rgb(75, 165, 220)', width=3)))  # add ttm dividends
    fig.add_trace(go.Scatter(x=x, y=opponent_tav, name=opponent_name, mode='lines', line=dict(color='rgb(220, 60, 115)', width=3)))  # add ttm dividends
    fig.add_trace(go.Scatter(x=x, y=player_exa, name=USERNAME, mode='lines', opacity=0.5, line=dict(color='rgb(75, 165, 220)', width=3, dash='dash')))  # add ttm dividends
    fig.add_trace(go.Scatter(x=x, y=op_exa, name=opponent_name, mode='lines', opacity=0.5, line=dict(color='rgb(220, 60, 115)', width=3, dash='dash')))  # add ttm dividends
    fig.update_layout(title={'text': f'Total Amber Value - {USERNAME} vs {opponent_name}'})  # set chart title
    fig.write_image(f"images/total_amber_value_{save}.png", scale=10)  # save to .png file


def advantage_chart(y):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # Chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # Title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # Legend font color
    )

    max_y = max(max(y), abs(min(y)))
    x = list(range(len(y)))

    # Create the figure
    fig = go.Figure(layout=layout)

    # Add trace for the white line
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        line=dict(color='white', width=2),  # White line
        name='Advantage'
    ))

    # Add trace for positive fill area
    fig.add_trace(go.Scatter(
        x=x + x[::-1],  # x values for positive fill
        y=list(np.maximum(y, 0)) + [0] * len(x),  # Match positive area exactly
        fill='toself',  # Close the fill area
        fillcolor='rgba(96, 180, 255, 0.4)',  # Blue with 40% opacity
        line=dict(color='rgba(0,0,0,0)'),  # No border line
        name='Positive Area'
    ))

    # Add trace for negative fill area
    fig.add_trace(go.Scatter(
        x=x + x[::-1],  # x values for negative fill
        y=list(np.minimum(y, 0)) + [0] * len(x),  # Match negative area exactly
        fill='toself',  # Close the fill area
        fillcolor='rgba(255, 75, 75, 0.4)',  # Red with 40% opacity
        line=dict(color='rgba(0,0,0,0)'),  # No border line
        name='Negative Area'
    ))

    fig.update_layout(
        title={'text': ''},
        width=700,
        height=360,
        showlegend=False,  # Hide legend
    )
    fig.update_yaxes(range=[-max_y, max_y])

    return fig


def creatures(player_creatures, opponent_creatures, opponent_name, save):
    x = list(range(max(len(player_creatures), len(opponent_creatures))))
    layout = go.Layout(
        margin=dict(pad=10),
        paper_bgcolor='rgb(5,15,15)',  # set chart background color
        plot_bgcolor='rgb(15,25,25)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}},  # set legend font color
        xaxis={'title': 'Turn', 'titlefont': {'color': 'rgb(225,235,235)'}, 'tickfont': {'color': 'rgb(225,235,235)'}},  # set x axis title
        yaxis={'title': 'Creatures', 'titlefont': {'color': 'rgb(225,235,235)'}, 'tickfont': {'color': 'rgb(225,235,235)'}},  # set y axis title
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(x=x, y=player_creatures, name=USERNAME, mode='lines', line=dict(color='rgb(75, 165, 220)', width=3)))  # add ttm dividends
    fig.add_trace(go.Scatter(x=x, y=opponent_creatures, name=opponent_name, mode='lines', line=dict(color='rgb(220, 60, 115)', width=3)))  # add ttm dividends
    fig.update_layout(title={'text': f'Creatures - {USERNAME} vs {opponent_name}'})  # set chart title
    fig.write_image(f"images/creatures_{save}.png", scale=10)  # save to .png file


def cards_played(player_cards, opponent_cards, opponent_name, save):
    x = list(range(max(len(player_cards), len(opponent_cards))))
    layout = go.Layout(
        margin=dict(pad=10),
        paper_bgcolor='rgb(5,15,15)',  # set chart background color
        plot_bgcolor='rgb(15,25,25)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}},  # set legend font color
        xaxis={'title': 'Turn', 'titlefont': {'color': 'rgb(225,235,235)'}, 'tickfont': {'color': 'rgb(225,235,235)'}},  # set x axis title
        yaxis={'title': 'Cards Played', 'titlefont': {'color': 'rgb(225,235,235)'}, 'tickfont': {'color': 'rgb(225,235,235)'}},  # set y axis title
    )
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(x=x, y=player_cards, name=USERNAME, mode='lines', line=dict(color='rgb(75, 165, 220)', width=3)))  # add ttm dividends
    fig.add_trace(go.Scatter(x=x, y=opponent_cards, name=opponent_name, mode='lines', line=dict(color='rgb(220, 60, 115)', width=3)))  # add ttm dividends
    fig.update_layout(title={'text': f'Cards Played - {USERNAME} vs {opponent_name}'})  # set chart title
    fig.write_image(f"images/cards_played_{save}.png", scale=10)  # save to .png file


def amber_sources_pie(values, name, save, contrast=False):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )

    if contrast:
        colors = None
    else:
        colors = [f'rgb({255-30*(3-x)/4},{235-50*(3-x)/4},{135-135*(3-x)/4})' for x in [1, 0, 2, 3]]

    labels = ['Effects', 'Steal', 'Reaps', 'Icons']

    fig = go.Figure(data=go.Pie(labels=labels, values=values, marker=dict(colors=colors, line=dict(color='rgb(15,25,25)', width=5))), layout=layout)  # make chart object
    fig.update_traces(textposition='inside', textinfo='value+percent+label')
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    # if name == USERNAME:
    #     save_name = "hero"
    # else:
    #     save_name = "villain"
    # fig.write_image(f"images/{save_name}_amber_sources_{save}.png", scale=10)  # save to .png file
    return fig


def amber_sources(values, max_y, name, save, contrast=False):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )

    if contrast:
        colors = None
    else:
        colors = [f'rgb({255-30*(3-x)/4},{235-50*(3-x)/4},{135-135*(3-x)/4})' for x in [1, 0, 2, 3]]

    labels = ['Effects', 'Steal', 'Reaps', 'Icons']

    fig = go.Figure(data=go.Bar(x=labels, y=values, marker=dict(color=colors[3], line=dict(color=colors[1], width=3), cornerradius="20%"), opacity=0.8), layout=layout)  # make chart object
    # fig.update_traces(textposition='inside', textinfo='value+percent+label')
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    fig.update_yaxes(range=[0, max_y])
    # if name == USERNAME:
    #     save_name = "hero"
    # else:
    #     save_name = "villain"
    # fig.write_image(f"images/{save_name}_amber_sources_{save}.png", scale=10)  # save to .png file
    return fig


def activity_graph(data):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )

    fig = go.Figure(data=go.Bar(x=data['Date'], y=data['Games'], marker=dict(color='rgba(150, 150, 200, 0.5)', line=dict(color='rgb(200, 200, 255)', width=3), cornerradius="20%")), layout=layout)  # make chart object
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    return fig


def set_meta_graph(data):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )
    x = list(data.keys())
    color_sequence = [hex_to_rgb(set_dict[s]['Color'], 0.65) for s in x]
    fig = go.Figure(data=go.Bar(x=x, y=list(data.values()), marker_color=color_sequence, marker=dict(line=dict(color='rgb(255, 255, 255)', width=3), cornerradius="20%")), layout=layout)  # make chart object
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    return fig


def house_meta_graph(data):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )
    x = list(data.keys())
    color_sequence = [f'rgba({house_colors[h.lower()][0]}, {house_colors[h.lower()][1]}, {house_colors[h.lower()][2]}, 0.65)' for h in x]
    fig = go.Figure(data=go.Bar(x=x, y=list(data.values()), marker_color=color_sequence, marker=dict(line=dict(color='rgb(255, 255, 255)', width=3), cornerradius="20%")), layout=layout)  # make chart object
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    return fig


def house_calls(data, name, games, save):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )
    counts = {}
    for call in data['house_calls']:
        if call in counts:
            counts[call] += 1
        else:
            counts[call] = 1
    for h in counts:
        counts[h] = round(counts[h] / games, 1)
    colors = [f'rgb({house_colors[h.strip()]})' for h in list(counts.keys())]
    labels = [h.strip().capitalize() for h in list(counts.keys())]
    values = list(counts.values())

    fig = go.Figure(data=go.Pie(labels=labels, values=values, marker=dict(colors=colors, line=dict(color='rgb(15,25,25)', width=5))), layout=layout)  # make chart object
    fig.update_traces(textposition='inside', textinfo='value+percent+label')
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    # if name == USERNAME:
    #     save_name = "hero"
    # else:
    #     save_name = "villain"
    # fig.write_image(f"images/{save_name}_house_calls_{save}.png", scale=10)  # save to .png file
    return fig


def get_card_information(player_data, individual_survival_rates=None, analysis_type='Game'):
    # link_base = "https://keyforge-card-images.s3-us-west-2.amazonaws.com/card-imgs/"
    # remove_chars = "æ””“!,.-…’'éĕŏăŭĭ\""
    if analysis_type == 'Game':
        card_played_type = 'individual_cards_played'
    else:
        card_played_type = 'individual_cards_played_total'
    df = pd.DataFrame(columns=["Card", "Turn", "Played", "Discarded", "Discarded %", "Amber", "Amber %", "Reaps", "Icons", "Steal", "Effects", "Survival %"])
    if analysis_type == 'Game':
        amber_gained = player_data['amber_icons'][-1] + player_data['amber_effect'][-1] + player_data['amber_reaped'][-1] + player_data['steal'][-1]
    else:
        amber_gained = player_data['total_amber_icons'][-1] + player_data['total_amber_effect'][-1] + player_data['total_amber_reaped'][-1] + player_data['total_steal'][-1]
    card_names = list(set(player_data[card_played_type][-1].keys()).union(player_data['individual_cards_discarded'][-1].keys()).union(player_data['individual_amber_icons'][-1].keys()).union(player_data['individual_amber_effect'][-1].keys()).union(player_data['individual_amber_reaped'][-1].keys()).union(player_data['individual_steal'][-1].keys()))
    sorted_card_names = sorted(card_names, key=lambda x: get_turn_played(player_data, x), reverse=False)
    sorted_card_names = sorted(sorted_card_names, key=lambda x: player_data[card_played_type][-1].get(x, 0), reverse=True)
    for card in sorted_card_names:
        played = player_data[card_played_type][-1].get(card, 0)
        discarded = player_data['individual_cards_discarded'][-1].get(card, 0)
        if discarded + played > 0:
            discarded_pct = round(100 * discarded / (discarded + played))
        else:
            discarded_pct = 0

        if analysis_type == 'Game':
            turn = get_turn_played(player_data, card)
        else:
            turn = player_data['turn_played'][-1].get(card, 0)

        amber_icons = player_data['individual_amber_icons'][-1].get(card, 0)
        amber_reaped = player_data['individual_amber_reaped'][-1].get(card, 0)
        amber_effect = player_data['individual_amber_effect'][-1].get(card, 0)
        amber_steal = player_data['individual_steal'][-1].get(card, 0)
        total_amber = round(amber_icons + amber_reaped + amber_effect + amber_steal, 1)
        if amber_gained > 0:
            amber_pct = round(100 * total_amber / amber_gained)
        else:
            amber_pct = 0

        if individual_survival_rates and card in individual_survival_rates:
            survival_rate = individual_survival_rates[card][-1]
        else:
            survival_rate = '--'

        new_row = [card, turn, played, discarded, discarded_pct, total_amber, amber_pct, amber_reaped, amber_icons, amber_steal, amber_effect, survival_rate]
        df.loc[len(df)] = new_row
    return df


def make_house_image(calls, player_graph=True):
    calls = [c.replace(' ', '') for c in calls]

    if len(calls) < 15:
        house_icon_zoom = 0.35
        axis_text_size = 12
    elif len(calls) < 25:
        house_icon_zoom = 0.25
        axis_text_size = 12
    else:
        house_icon_zoom = 0.2
        axis_text_size = 10

    def add_image(ax, image_path, x, y, zoom=house_icon_zoom, alpha=1):
        img = mpimg.imread(image_path)
        imagebox = OffsetImage(img, zoom=zoom, alpha=alpha)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

    bg_color = (14/255, 17/255, 23/255)

    num_calls = len(calls)
    x_positions = [(i+1)/num_calls for i in range(num_calls)]  # Regular intervals

    house_order = [h.lower() for h in house_dict.keys()]

    houses = list(set(calls))

    sorted_strings = sorted(houses, key=lambda z: house_order.index(z))
    if len(houses) == 2:
        minus_factor = 0
    elif len(houses) == 1:
        minus_factor = 0
    else:
        minus_factor = 0
    resulting_dict = {s: minus_factor+idx for idx, s in enumerate(sorted_strings)}

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor(bg_color)

    adjustment_interval = 1/(max(len(houses)+1, 4))

    for h, x in zip(calls, x_positions):
        ax.vlines(x, 0.15, 1-adjustment_interval*(resulting_dict[h]+1), color='gray', linewidth=2, linestyles='dashed')

    y_values = [1 - (i + 1) * adjustment_interval for i in range(max(len(houses), 3))]
    for y in y_values:
        ax.hlines(y, 0.02, 1.05, color='lightgray', linewidth=3)

    call_rate_dict = {}
    for h, h_idx in resulting_dict.items():
        y = y_values[h_idx]
        call_rate = calls.count(h) / num_calls
        call_rate_dict[h] = call_rate
        ax.text(0, y, f'{round(100*call_rate)}%', color='white', fontsize=12, fontweight='bold', ha='right', va='center')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(0, 1)

    for i, x in enumerate(x_positions):
        house = calls[i]
        y = y_values[resulting_dict[house]]
        img = f'./house_images/105px-{house.title()}.png'
        add_image(ax, img, x, y, alpha=0.9)
        ax.text(x, 0.1, i+1, color='white', fontsize=axis_text_size, ha='center')

    if player_graph:
        save_name = 'player_amber_graph.png'
    else:
        save_name = 'opponent_amber_graph.png'
    plt.savefig(save_name, dpi=300, bbox_inches='tight', facecolor=bg_color)

    image = Image.open(save_name)
    return image


def make_house_image_deck(calls, min_threshold=0, player_graph=True):
    house_order = [h.lower() for h in house_dict.keys()]
    houses = list({key for call in calls for key in call.keys()})

    sorted_strings = sorted(houses, key=lambda z: house_order.index(z))

    total_calls = sum([sum(c.values()) for c in calls])

    total_house_values = {}
    for h in sorted_strings:
        total_house_values[h] = sum([c[h] for c in calls if h in c])

    calls = [c for c in calls if sum(c.values()) >= min_threshold]

    if len(calls) < 15:
        house_icon_zoom = 0.35
        axis_text_size = 12
    elif len(calls) < 25:
        house_icon_zoom = 0.25
        axis_text_size = 12
    else:
        house_icon_zoom = 0.2
        axis_text_size = 10

    def add_image(ax, image_path, x, y, zoom=house_icon_zoom, alpha=1):
        img = mpimg.imread(image_path)
        imagebox = OffsetImage(img, zoom=zoom, alpha=alpha)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

    bg_color = (14/255, 17/255, 23/255)

    if len(houses) == 2:
        minus_factor = 1
    elif len(houses) == 1:
        minus_factor = 2
    else:
        minus_factor = 0
    resulting_dict = {s: minus_factor+idx for idx, s in enumerate(sorted_strings)}

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor(bg_color)

    adjustment_interval = 0.25

    num_calls = len(calls)
    x_positions = [(i+1)/num_calls for i in range(num_calls)]  # Regular intervals

    y_values = [1 - (i + 1) * adjustment_interval for i in range(3)]

    for y in y_values:
        ax.hlines(y, 0.02, 1.05, color='lightgray', linewidth=3)

    if player_graph:
        for h, h_idx in resulting_dict.items():
            y = y_values[h_idx]
            call_rate = total_house_values[h] / total_calls
            ax.text(0, y, f'{round(100*call_rate)}%', color='white', fontsize=12, fontweight='bold', ha='right', va='center')

    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(0, 1)

    for i, x in enumerate(x_positions):
        if player_graph:
            top_houses = calls[i].keys()
        else:
            top_houses = sorted(calls[i].items(), key=lambda item: item[1], reverse=True)[:3]
            top_houses = [t[0] for t in top_houses]
        for j, house in enumerate(top_houses):
            img = f'./house_images/105px-{house.title()}.png'
            if player_graph:
                y = y_values[resulting_dict[house]]
            else:
                y = y_values[j]
            true_turn_frequency = calls[i][house] / sum(calls[i].values())
            if player_graph:
                turn_frequency = true_turn_frequency ** (1/2)
            else:
                turn_frequency = true_turn_frequency ** (1/3)
            turn_frequency = min(1, turn_frequency + 0.1)
            add_image(ax, img, x, y, alpha=turn_frequency)
            ax.text(x, y-0.1, f"{round(100*true_turn_frequency)}%", color='white', fontsize=8, ha='center')

        ax.text(x, 0.05, i+1, color='white', fontsize=axis_text_size, ha='center')

    if player_graph:
        save_name = 'player_amber_graph.png'
    else:
        save_name = 'opponent_amber_graph.png'
    plt.savefig(save_name, dpi=300, bbox_inches='tight', facecolor=bg_color)

    image = Image.open(save_name)
    return image
