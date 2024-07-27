import pandas as pd
import ast

# import graphing
# from graphing import USERNAME


def get_turn_played(player_data, card_name, analysis_type='replay'):
    if analysis_type == 'replay':
        return next((i for i, d in enumerate(player_data['individual_cards_played']) if card_name in d), -1) + 1
    else:
        return player_data['turn_played'][-1].get(card_name, 0)


def analyze_deck(deck_name, graphs=True):
    #********************************
    log = pd.read_csv("game_log.csv")
    deck_games = log.loc[log['Deck'] == deck_name]
    aggregate_data = {USERNAME: {'turns': [],
                                 'cards_played': [],
                                 'turn_played': [{}],
                                 'individual_cards_played': [{}],
                                 'individual_cards_discarded': [{}],
                                 'individual_amber_icons': [{}],
                                 'individual_amber_effect': [{}],
                                 'individual_amber_reaped': [{}],
                                 'individual_steal': [{}],
                                 'amber': [],
                                 'keys': [],
                                 'creatures': [],
                                 'house_calls': [],
                                 'amber_icons': [0],
                                 'amber_effect': [0],
                                 'amber_reaped': [0],
                                 'steal': [0]},
                      'opponent': {'turns': [],
                                   'cards_played': [],
                                   'turn_played': [{}],
                                   'individual_cards_played': [{}],
                                   'individual_cards_discarded': [{}],
                                   'individual_amber_icons': [{}],
                                   'individual_amber_effect': [{}],
                                   'individual_amber_reaped': [{}],
                                   'individual_steal': [{}],
                                   'amber': [],
                                   'keys': [],
                                   'creatures': [],
                                   'house_calls': [],
                                   'amber_icons': [0],
                                   'amber_effect': [0],
                                   'amber_reaped': [0],
                                   'steal': [0]}}
    for idx, row in deck_games.iterrows():
        game_data = ast.literal_eval(row['Game Log'])
        names = list(game_data.keys())
        opponent_name = [name for name in names if name != USERNAME][0]
        player_data = game_data[USERNAME]
        opponent_data = game_data[opponent_name]
        for player, p_data in zip([USERNAME, 'opponent'], [player_data, opponent_data]):
            for j in range(len(p_data['cards_played'])):
                if j >= len(aggregate_data[player]['turns']):
                    aggregate_data[player]['turns'].append(1)
                    for val in ['cards_played', 'amber', 'keys', 'creatures']:
                        aggregate_data[player][val].append(p_data[val][j])
                else:
                    aggregate_data[player]['turns'][j] += 1
                    for val in ['cards_played', 'amber', 'keys', 'creatures']:
                        aggregate_data[player][val][j] += p_data[val][j]

            aggregate_data[player]['house_calls'] += p_data['house_calls']

            aggregate_data[player]['amber_icons'][0] += p_data['amber_icons'][-1]
            aggregate_data[player]['amber_effect'][0] += p_data['amber_effect'][-1]
            aggregate_data[player]['amber_reaped'][0] += p_data['amber_reaped'][-1]
            aggregate_data[player]['steal'][0] += p_data['steal'][-1]
            if player == 'opponent':
                player_name = row['Opponent']
            else:
                player_name = USERNAME
            for card, played in p_data['individual_cards_played'][-1].items():
                cards_played_dict = aggregate_data[player]['individual_cards_played'][-1]
                if card in cards_played_dict:
                    cards_played_dict[card] += played
                else:
                    cards_played_dict[card] = played

                turn_played_dict = aggregate_data[player]['turn_played'][-1]
                if card in turn_played_dict:
                    turn_played_dict[card] += get_turn_played(game_data, player_name, card, 'replay')
                else:
                    turn_played_dict[card] = get_turn_played(game_data, player_name, card, 'replay')

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
        p_agg['turns'].append(1)
        first_one_index = p_agg['turns'].index(1)
        p_agg['turns'] = p_agg['turns'][:first_one_index]
        for stat in ['cards_played', 'amber', 'keys', 'creatures']:
            p_agg[stat] = p_agg[stat][:first_one_index]
            for i, t in enumerate(p_agg['turns']):
                p_agg[stat][i] = round(p_agg[stat][i] / t, 1)
        for stat in ['amber_icons', 'amber_effect', 'amber_reaped', 'steal']:
            p_agg[stat][0] /= len(deck_games)
        for stat in ['turn_played', 'individual_cards_played', 'individual_cards_discarded', 'individual_amber_icons',
                     'individual_amber_effect', 'individual_amber_reaped', 'individual_steal']:
            for card in p_agg[stat][-1]:
                p_agg[stat][-1][card] /= len(deck_games)

    player_tav, opponent_tav = graphing.calculate_tav(aggregate_data[USERNAME], aggregate_data['opponent'])
    p_values = [aggregate_data[USERNAME]['steal'][0], aggregate_data[USERNAME]['amber_reaped'][0],
                aggregate_data[USERNAME]['amber_icons'][0], aggregate_data[USERNAME]['amber_effect'][0]]
    op_values = [aggregate_data['opponent']['steal'][0], aggregate_data['opponent']['amber_reaped'][0],
                 aggregate_data['opponent']['amber_icons'][0], aggregate_data['opponent']['amber_effect'][0]]
    if graphs:
        graphing.total_amber_value(player_tav, opponent_tav, aggregate_data[USERNAME], aggregate_data['opponent'],
                                   "Opponent", USERNAME, 'analysis', len(deck_games))
        graphing.creatures(aggregate_data[USERNAME]['creatures'], aggregate_data['opponent']['creatures'], "Opponent",
                           'analysis')
        graphing.cards_played(aggregate_data[USERNAME]['cards_played'], aggregate_data['opponent']['cards_played'],
                              "Opponent", 'analysis')
        graphing.amber_sources(p_values, USERNAME, 'analysis')
        graphing.amber_sources(op_values, "Opponent", 'analysis')
        graphing.house_calls(aggregate_data[USERNAME], USERNAME, len(deck_games), 'analysis')
        graphing.house_calls(aggregate_data['opponent'], "Opponent", len(deck_games), 'analysis')
    return aggregate_data, USERNAME, len(deck_games)


def create_deck_analysis_options():
    #***************************
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
            deck_analysis_df.loc[len(deck_analysis_df)] = [deck, games, winrate, cpt, apt, speed, p_defense, op_cpt,
                                                           op_apt, op_speed, op_defense]
    return deck_analysis_df




