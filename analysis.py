import pandas as pd
import ast

import database
import graphing


def get_turn_played(player_data, card_name, analysis_type='replay'):
    if analysis_type == 'replay':
        return next((i for i, d in enumerate(player_data['individual_cards_played']) if card_name in d), -1) + 1
    else:
        return player_data['turn_played'][-1].get(card_name, 0)


def analyze_deck(deck_name, pilot, graphs=True):
    deck_games = database.get_deck_games(pilot, deck_name)
    aggregate_data = {pilot: {'turns': [],
                              'cards_played': [],
                              'turn_played': [{}],
                              'individual_cards_played': [],
                              'individual_cards_discarded': [{}],
                              'individual_amber_icons': [{}],
                              'individual_amber_effect': [{}],
                              'individual_amber_reaped': [{}],
                              'individual_steal': [{}],
                              'amber': [],
                              'keys': [],
                              'creatures': [],
                              'house_calls': [],
                              'amber_icons': [],
                              'amber_effect': [],
                              'amber_reaped': [],
                              'steal': []},
                      'opponent': {'turns': [],
                                   'cards_played': [],
                                   'turn_played': [{}],
                                   'individual_cards_played': [],
                                   'individual_cards_discarded': [{}],
                                   'individual_amber_icons': [{}],
                                   'individual_amber_effect': [{}],
                                   'individual_amber_reaped': [{}],
                                   'individual_steal': [{}],
                                   'amber': [],
                                   'keys': [],
                                   'creatures': [],
                                   'house_calls': [],
                                   'amber_icons': [],
                                   'amber_effect': [],
                                   'amber_reaped': [],
                                   'steal': []}}
    for idx, row in deck_games.iterrows():
        game_data = row['Game Log'][0]
        names = list(game_data.keys())
        opponent_name = [name for name in names if name != pilot][0]
        player_data = game_data[pilot]
        opponent_data = game_data[opponent_name]
        for player, p_data in zip([pilot, 'opponent'], [player_data, opponent_data]):
            for j in range(len(p_data['cards_played'])):
                if j >= len(aggregate_data[player]['turns']):
                    aggregate_data[player]['turns'].append(1)
                    aggregate_data[player]['individual_cards_played'].append({})
                    for val in ['cards_played', 'amber', 'keys', 'creatures', 'amber_icons', 'amber_effect', 'amber_reaped', 'steal']:
                        aggregate_data[player][val].append(p_data[val][j])
                else:
                    aggregate_data[player]['turns'][j] += 1
                    for val in ['cards_played', 'amber', 'keys', 'creatures', 'amber_icons', 'amber_effect', 'amber_reaped', 'steal']:
                        aggregate_data[player][val][j] += p_data[val][j]
                for card, played in p_data['individual_cards_played'][j].items():
                    if card in aggregate_data[player]['individual_cards_played'][j]:
                        aggregate_data[player]['individual_cards_played'][j][card] += played
                    else:
                        aggregate_data[player]['individual_cards_played'][j][card] = played

            aggregate_data[player]['house_calls'] += p_data['house_calls']

            if player == 'opponent':
                player_name = row['Opponent']
            else:
                player_name = pilot
            for card, played in p_data['individual_cards_played'][-1].items():

                turn_played_dict = aggregate_data[player]['turn_played'][-1]

                turn_played = get_turn_played(p_data, card, 'replay')
                if card in turn_played_dict:
                    turn_played_dict[card] += turn_played
                else:
                    turn_played_dict[card] = turn_played
            for card, discarded in p_data['individual_cards_discarded'][-1].items():
                cards_discarded_dict = aggregate_data[player]['individual_cards_discarded'][-1]
                if card in cards_discarded_dict:
                    cards_discarded_dict[card] += discarded
                else:
                    cards_discarded_dict[card] = discarded

            for card, amber in p_data['individual_amber_icons'][-1].items():
                amber_icons_dict = aggregate_data[player]['individual_amber_icons'][-1]
                if card in amber_icons_dict:
                    amber_icons_dict[card] += amber
                else:
                    amber_icons_dict[card] = amber

            for card, amber in p_data['individual_amber_effect'][-1].items():
                amber_effect_dict = aggregate_data[player]['individual_amber_effect'][-1]
                if card in amber_effect_dict:
                    amber_effect_dict[card] += amber
                else:
                    amber_effect_dict[card] = amber

            for card, amber in p_data['individual_amber_reaped'][-1].items():
                amber_reaped_dict = aggregate_data[player]['individual_amber_reaped'][-1]
                if card in amber_reaped_dict:
                    amber_reaped_dict[card] += amber
                else:
                    amber_reaped_dict[card] = amber

            for card, amber in p_data['individual_steal'][-1].items():
                steal_dict = aggregate_data[player]['individual_steal'][-1]
                if card in steal_dict:
                    steal_dict[card] += amber
                else:
                    steal_dict[card] = amber

    for p_agg in aggregate_data.values():
        p_agg['turns'].append(1)  # add 1 in case no 1's appear
        first_one_index = p_agg['turns'].index(1)  # find first 1
        p_agg['turns'] = p_agg['turns'][:first_one_index]  # remove up to first 1
        for stat in ['cards_played', 'amber', 'keys', 'creatures', 'amber_icons', 'amber_effect', 'amber_reaped', 'steal']:
            p_agg[stat] = p_agg[stat][:first_one_index]  # trim stat to first 1
            for i, t in enumerate(p_agg['turns']):
                p_agg[stat][i] = round(p_agg[stat][i] / t, 2)  # divide stat by turns
        for stat in ['turn_played', 'individual_cards_discarded', 'individual_amber_icons', 'individual_amber_effect', 'individual_amber_reaped', 'individual_steal']:
            for card in p_agg[stat][-1]:
                p_agg[stat][-1][card] = round(p_agg[stat][-1][card]/len(deck_games), 1)  # divide stat by games
        p_agg['individual_cards_played'] = p_agg['individual_cards_played'][:first_one_index]
        for i, card_dict in enumerate(p_agg['individual_cards_played']):
            for card in card_dict:
                card_dict[card] = round(card_dict[card]/p_agg['turns'][i], 1)

    return aggregate_data


def create_deck_analysis_options():
    # ***************************
    game_log = pd.read_csv("game_log.csv")
    deck_analysis_df = pd.DataFrame(
        columns=['Deck Name', 'Games', 'Winrate', 'CPT', 'APT', 'Spd', 'Def', 'Op. CPT', 'Op. APT', 'Op. Spd',
                 'Op. Def'])
    deck_names = game_log['Deck'].value_counts().sort_values(ascending=False).to_dict()
    for deck, games in deck_names.items():
        if games > 1:
            wins = len(game_log.loc[(game_log['Deck'] == deck) & (game_log['Winner'] == USERNAME)])
            winrate = round(100 * wins / games)
            agg_data = analyze_deck(deck, graphs=False)
            cpt = round(games * max(agg_data[0][USERNAME]['cards_played']) / len(agg_data[0][USERNAME]['house_calls']),
                        1)
            op_cpt = round(
                games * max(agg_data[0]['opponent']['cards_played']) / len(agg_data[0][USERNAME]['house_calls']), 1)
            apt = round(games * (agg_data[0][USERNAME]['amber_icons'][-1] + agg_data[0][USERNAME]['amber_reaped'][-1] +
                                 agg_data[0][USERNAME]['amber_effect'][-1] + agg_data[0][USERNAME]['steal'][-1]) / len(
                agg_data[0][USERNAME]['house_calls']), 1)
            op_apt = round(games * (
                    agg_data[0]['opponent']['amber_icons'][-1] + agg_data[0]['opponent']['amber_reaped'][-1] +
                    agg_data[0]['opponent']['amber_effect'][-1] + agg_data[0]['opponent']['steal'][-1]) / len(
                agg_data[0][USERNAME]['house_calls']), 1)
            p_exa, op_exa, p_defense, op_defense = graphing.calculate_ex_amber(agg_data[0][USERNAME],
                                                                               agg_data[0]['opponent'], USERNAME,
                                                                               'Opponent', games)
            speed = round(18 / (apt * (1 - op_defense)))
            op_speed = round(18 / (op_apt * (1 - p_defense)))
            p_defense = round(p_defense * 100)
            op_defense = round(op_defense * 100)
            deck_analysis_df.loc[len(deck_analysis_df)] = [deck, games, winrate, cpt, apt, speed, p_defense, op_cpt, op_apt, op_speed, op_defense]
    return deck_analysis_df
