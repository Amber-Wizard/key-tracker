import pandas as pd
import ast

import database
import graphing


def get_turn_played(player_data, card_name, analysis_type='replay'):
    if analysis_type == 'replay':
        return next((i for i, d in enumerate(player_data['individual_cards_played']) if card_name in d), -1) + 1
    else:
        return player_data['turn_played'][-1].get(card_name, 0)


# def analyze_cards(deck_games, pilot):

def analyze_deck(deck_name, pilot, aliases=None, graphs=True, cards=True):
    deck_games = database.get_deck_games(pilot, deck_name, aliases=aliases)
    aggregate_data = {pilot: {'turns': [],
                              'cards_played': [],
                              'turn_played': [{}],
                              'individual_cards_played': [],
                              'individual_cards_played_total': [{}],
                              'individual_cards_played_turn': {'first': [], 'second': []},
                              'individual_cards_drawn': {},
                              'individual_cards_discarded': [{}],
                              'individual_amber_icons': [{}],
                              'individual_amber_effect': [{}],
                              'individual_amber_reaped': [{}],
                              'individual_steal': [{}],
                              'total_amber_icons': [0],
                              'total_amber_effect': [0],
                              'total_amber_reaped': [0],
                              'total_steal': [0],
                              'card_wins': {},
                              'card_losses': {},
                              'amber': [],
                              'keys': [],
                              'checks': [],
                              'checked_keys': [],
                              'creatures': [],
                              'house_calls': [],
                              'amber_icons': [],
                              'amber_effect': [],
                              'amber_reaped': [],
                              'steal': [],
                              'survives': [],
                              'deaths': [],
                              'survival_rate': []},
                      'opponent': {'turns': [],
                                   'cards_played': [],
                                   'turn_played': [{}],
                                   'individual_cards_played': [],
                                   'individual_cards_played_total': [{}],
                                   'individual_cards_discarded': [{}],
                                   'individual_amber_icons': [{}],
                                   'individual_amber_effect': [{}],
                                   'individual_amber_reaped': [{}],
                                   'individual_steal': [{}],
                                   'total_amber_icons': [0],
                                   'total_amber_effect': [0],
                                   'total_amber_reaped': [0],
                                   'total_steal': [0],
                                   'card_wins': {},
                                   'card_losses': {},
                                   'amber': [],
                                   'keys': [],
                                   'checks': [],
                                   'checked_keys': [],
                                   'creatures': [],
                                   'house_calls': [],
                                   'amber_icons': [],
                                   'amber_effect': [],
                                   'amber_reaped': [],
                                   'steal': [],
                                   'survives': [],
                                   'deaths': [],
                                   'survival_rate': []}}

    basic_stat_list = ['cards_played', 'amber', 'keys', 'checks', 'creatures', 'amber_icons', 'amber_effect', 'amber_reaped', 'steal']
    basic_stat_dict = {k: 0 for k in basic_stat_list}
    stat_turn_vals = []

    for idx, row in deck_games.iterrows():
        game_data = row['Game Log'][0]
        names = list(game_data.keys())
        player_name_list = aliases + [pilot]
        player_name = row['Player'][0]
        opponent_name = row['Opponent'][0]
        winner = row['Winner'][0]
        if winner == player_name:
            won = 1
        else:
            won = 0
        first_player = row['Starting Player'][0]

        if first_player == player_name:
            sp_list = [False, True]
            turn_list = aggregate_data[pilot]['individual_cards_played_turn']['first']
        else:
            sp_list = [True, False]
            turn_list = aggregate_data[pilot]['individual_cards_played_turn']['second']

        player_data = game_data[player_name]
        opponent_data = game_data[opponent_name]
        player_hand = game_data['player_hand']

        unique_cards = list(set(value for sublist in player_hand for value in sublist))
        for item in unique_cards:
            if item in aggregate_data[pilot]['individual_cards_drawn']:
                # Increment values if key exists
                aggregate_data[pilot]['individual_cards_drawn'][item]['drawn'] += 1
                aggregate_data[pilot]['individual_cards_drawn'][item]['wins'] += won
            else:
                # Add new key-value pair if key does not exist
                aggregate_data[pilot]['individual_cards_drawn'][item] = {'drawn': 1, 'wins': won}

        for turn_idx, cards_played in enumerate(player_data['individual_cards_played']):
            if turn_idx != 0:
                previous_cards_played = player_data['individual_cards_played'][turn_idx - 1]
            else:
                previous_cards_played = None

            if turn_idx >= len(turn_list):
                turn_list.append({})

            for card, played in cards_played.items():
                if previous_cards_played and card in previous_cards_played:
                    played = played - previous_cards_played[card]

                for x in range(played):
                    if x == 0:
                        card_key = card
                    else:
                        card_key = f"{card}~~{x+1}"
                    if card_key not in turn_list[turn_idx]:
                        turn_list[turn_idx][card_key] = {'played': 0, 'wins': 0}

                    turn_list[turn_idx][card_key]['played'] += 1

                    if winner == player_name:
                        turn_list[turn_idx][card_key]['wins'] += 1

        for player, p_data, sp in zip([pilot, 'opponent'], [player_data, opponent_data], sp_list):
            for j in range(len(p_data['cards_played'])):
                if j >= len(aggregate_data[player]['turns']):
                    aggregate_data[player]['turns'].append(1)
                    aggregate_data[player]['individual_cards_played'].append({})
                    stat_turn_vals.append(dict(basic_stat_dict))

                    for val in basic_stat_list:
                        if val in p_data:
                            aggregate_data[player][val].append(p_data[val][j])
                            stat_turn_vals[j][val] += 1

                            if val == 'checks':
                                aggregate_data[player]['checked_keys'].append(p_data['keys'][j])
                        else:
                            aggregate_data[player][val].append(0)

                else:
                    aggregate_data[player]['turns'][j] += 1
                    for val in basic_stat_list:
                        if val in p_data:
                            aggregate_data[player][val][j] += p_data[val][j]
                            stat_turn_vals[j][val] += 1

                            if val == 'checks':
                                aggregate_data[player]['checked_keys'][j] += p_data['keys'][j]

                for card, played in p_data['individual_cards_played'][j].items():
                    if j != 0:
                        if card in p_data['individual_cards_played'][j-1]:
                            played = played - p_data['individual_cards_played'][j-1][card]

                    if card in aggregate_data[player]['individual_cards_played'][j]:
                        aggregate_data[player]['individual_cards_played'][j][card] += played
                    else:
                        aggregate_data[player]['individual_cards_played'][j][card] = played

            for j, h in enumerate(p_data['house_calls']):
                house_call_list = aggregate_data[player]['house_calls']
                if j >= len(house_call_list):
                    house_call_list.append({})

                house_choice = h.replace(' ', '')
                if house_choice not in house_call_list[j]:
                    house_call_list[j][house_choice] = 1
                else:
                    house_call_list[j][house_choice] += 1

            # aggregate_data[player]['house_calls'] += p_data['house_calls']
            aggregate_data[player]['total_amber_icons'][-1] += p_data['amber_icons'][-1]
            aggregate_data[player]['total_amber_effect'][-1] += p_data['amber_effect'][-1]
            aggregate_data[player]['total_amber_reaped'][-1] += p_data['amber_reaped'][-1]
            aggregate_data[player]['total_steal'][-1] += p_data['steal'][-1]

            for card, played in p_data['individual_cards_played'][-1].items():
                if winner == player_name:
                    card_win_dict = aggregate_data[player]['card_wins']
                else:
                    card_win_dict = aggregate_data[player]['card_losses']
                if card in card_win_dict:
                    card_win_dict[card] += 1
                else:
                    card_win_dict[card] = 1

                cards_played_dict = aggregate_data[player]['individual_cards_played_total'][-1]
                if card in cards_played_dict:
                    cards_played_dict[card] += played
                else:
                    cards_played_dict[card] = played

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

            survival_rate, survive, death, individual_survival_rate, individual_survive, individual_death = graphing.calculate_survival_rate(p_data, sp)

            agg_survives = aggregate_data[player]['survives']
            agg_deaths = aggregate_data[player]['deaths']

            for i, s in enumerate(survive):
                if i >= len(agg_survives):
                    agg_survives.append(s)
                else:
                    agg_survives[i] += s

            for i, d in enumerate(death):
                if i >= len(agg_deaths):
                    agg_deaths.append(d)
                else:
                    agg_deaths[i] += d

    for start in ['first', 'second']:
        aggregate_data[pilot]['individual_cards_played_turn'][start] = [d for d in aggregate_data[pilot]['individual_cards_played_turn'][start] if d]

    for p_agg in aggregate_data.values():
        p_agg['turns'].append(1)  # add 1 in case no 1's appear
        first_one_index = p_agg['turns'].index(1)  # find first 1
        p_agg['turns'] = p_agg['turns'][:first_one_index]  # remove up to first 1
        for stat in ['cards_played', 'amber', 'keys', 'checks', 'creatures', 'amber_icons', 'amber_effect', 'amber_reaped', 'steal']:
            p_agg[stat] = p_agg[stat][:first_one_index]  # trim stat to first 1
            for i, turn_stats in enumerate(stat_turn_vals):
                if i < len(p_agg[stat]):
                    p_agg[stat][i] = round(p_agg[stat][i] / turn_stats[stat], 2) if turn_stats[stat] != 0 else 0  # divide stat by turns

        for i, turn_stats in enumerate(stat_turn_vals):
            if i < len(p_agg['checked_keys']):
                p_agg['checked_keys'][i] = round(p_agg['checked_keys'][i] / turn_stats['checks'], 2) if turn_stats['checks'] > 0 else 0  # divide stat by turns
        for stat in ['turn_played', 'individual_cards_played_total', 'individual_cards_discarded', 'individual_amber_icons', 'individual_amber_effect', 'individual_amber_reaped', 'individual_steal']:
            for card in p_agg[stat][-1]:
                p_agg[stat][-1][card] = round(p_agg[stat][-1][card]/len(deck_games), 1)  # divide stat by games
        for stat in ['total_amber_icons', 'total_amber_effect', 'total_amber_reaped', 'total_steal']:
            p_agg[stat][-1] = round(p_agg[stat][-1] / len(deck_games), 1)
        p_agg['individual_cards_played'] = p_agg['individual_cards_played'][:first_one_index]
        # for i, card_dict in enumerate(p_agg['individual_cards_played']):
        #     for card in card_dict:
        #         card_dict[card] = round(card_dict[card]/p_agg['turns'][i], 2)

    return aggregate_data

