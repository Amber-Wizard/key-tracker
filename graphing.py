import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import ast

import analysis

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
}


def calculate_ttw(player_tav, player_data):
    ttw = []
    amber_deltas = []
    reap_rates = []
    for i in range(len(player_tav)):
        amber_remaining = 18 - player_tav[i]
        avg_creatures = sum(player_data['creatures'][:i+1]) / (i+1)
        if avg_creatures > 0:
            reap_rate = player_data['amber_reaped'][i] / (((i+1) * avg_creatures) / 2)
        else:
            reap_rate = 0
        amber_delta = (player_data['amber_icons'][i] + player_data['amber_effect'][i] + player_data['steal'][i]) / ((i+1) / 2)
        divisor = player_data['creatures'][i] * reap_rate + amber_delta
        if divisor > 0:
            turns_remaining = amber_remaining / (player_data['creatures'][i] * reap_rate + amber_delta)
        else:
            turns_remaining = 25
        ttw.append(min(turns_remaining, 25))
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

    player_tav, opponent_tav = calculate_tav(player_data, opponent_data)
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


def analyze_game(username, game_data):

    log = game_data['Game Log'][0]
    player_data = log[username]
    first_player = game_data['Starting Player'][0]

    if list(log.keys())[0] == username:
        opponent_name = list(log.keys())[1]
        opponent_data = log[opponent_name]
    else:
        opponent_name = list(log.keys())[0]
        opponent_data = log[opponent_name]

    game_analysis_data = create_game_analysis_graphs(player_data, username, opponent_data, opponent_name, first_player)

    return game_analysis_data


def create_game_analysis_graphs(player_data, username, opponent_data, opponent_name, first_player):
    player_tav, opponent_tav = calculate_tav(player_data, opponent_data)
    player_ttw, player_delta, player_reap_rate = calculate_ttw(player_tav, player_data)
    opponent_ttw, opponent_delta, opponent_reap_rate = calculate_ttw(opponent_tav, opponent_data)
    # total_amber_value(player_tav, opponent_tav, player_data, opponent_data, opponent_name, first_player, 'replay')
    values = [player_data['steal'][-1], player_data['amber_reaped'][-1], player_data['amber_icons'][-1], player_data['amber_effect'][-1]]
    player_amber_sources = amber_sources(values, username, 'replay')
    values = [opponent_data['steal'][-1], opponent_data['amber_reaped'][-1], opponent_data['amber_icons'][-1], opponent_data['amber_effect'][-1]]
    opponent_amber_sources = amber_sources(values, opponent_name, 'replay')
    player_house_calls = house_calls(player_data, username, 1, 'replay')
    opponent_house_calls = house_calls(opponent_data, opponent_name, 1, 'replay')
    player_card_data = get_card_information(player_data)
    opponent_card_data = get_card_information(opponent_data)
    game_dataframe = pd.DataFrame({'Player Amber': player_tav, 'Opponent Amber': opponent_tav, 'Player Cards': player_data['cards_played'], 'Opponent Cards': opponent_data['cards_played'], 'Player Creatures': player_data['creatures'], 'Opponent Creatures': opponent_data['creatures'], 'Player Prediction': player_ttw, 'Opponent Prediction': opponent_ttw, 'Player Delta': player_delta, 'Opponent Delta': opponent_delta, 'Player Reap Rate': player_reap_rate, 'Opponent Reap Rate': opponent_reap_rate})
    return game_dataframe, player_amber_sources, opponent_amber_sources, player_house_calls, opponent_house_calls, player_card_data, opponent_card_data


def calculate_tav(player_data, opponent_data):
    player_tav = [k * 6 + a for k, a in zip(player_data['keys'], player_data['amber'])]
    opponent_tav = [k * 6 + a for k, a in zip(opponent_data['keys'], opponent_data['amber'])]
    return player_tav, opponent_tav


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


def amber_sources(values, name, save):
    layout = go.Layout(
        paper_bgcolor='rgb(14, 17, 23)',  # set chart background color
        title={'font': {'color': 'rgb(225,235,235)'}},  # set title font color
        legend={'font': {'color': 'rgb(225,235,235)'}}  # set legend font color
    )

    colors = [f'rgb({255-30*(3-x)/4},{235-50*(3-x)/4},{135-135*(3-x)/4})' for x in range(4)]

    labels = ['Steal', 'Reaps', 'Icons', 'Effects']

    fig = go.Figure(data=go.Pie(labels=labels, values=values, marker=dict(colors=colors, line=dict(color='rgb(15,25,25)', width=5))), layout=layout)  # make chart object
    fig.update_traces(textposition='inside', textinfo='value+percent+label')
    fig.update_layout(title={'text': f''}, width=420, height=480, showlegend=False)  # set chart title
    # if name == USERNAME:
    #     save_name = "hero"
    # else:
    #     save_name = "villain"
    # fig.write_image(f"images/{save_name}_amber_sources_{save}.png", scale=10)  # save to .png file
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
        counts[h] = counts[h] / games
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


def get_card_information(player_data):
    df = pd.DataFrame(columns=["Card", "Turn", "Played", "Discarded", "Discarded %", "Amber", "Amber %", "Icons", "Reaps", "Steal", "Effect"])
    amber_gained = player_data['amber_icons'][-1] + player_data['amber_effect'][-1] + player_data['amber_reaped'][-1] + player_data['steal'][-1]
    card_names = list(set(player_data['individual_cards_played'][-1].keys()).union(player_data['individual_cards_discarded'][-1].keys()))
    sorted_card_names = sorted(card_names, key=lambda x: analysis.get_turn_played(player_data, x), reverse=False)
    sorted_card_names = sorted(sorted_card_names, key=lambda x: player_data['individual_cards_played'][-1].get(x, 0), reverse=True)
    for card in sorted_card_names:
        played = player_data['individual_cards_played'][-1].get(card, 0)
        discarded = player_data['individual_cards_discarded'][-1].get(card, 0)
        discarded_pct = round(100 * discarded / (discarded + played))
        turn = analysis.get_turn_played(player_data, card)

        amber_icons = player_data['individual_amber_icons'][-1].get(card, 0)
        amber_reaped = player_data['individual_amber_reaped'][-1].get(card, 0)
        amber_effect = player_data['individual_amber_effect'][-1].get(card, 0)
        amber_steal = player_data['individual_steal'][-1].get(card, 0)
        total_amber = round(amber_icons + amber_reaped + amber_effect + amber_steal, 1)
        amber_pct = round(100 * total_amber / amber_gained)

        new_row = [card, turn, played, discarded, discarded_pct, total_amber, amber_pct, amber_icons, amber_reaped, amber_steal, amber_effect]
        df.loc[len(df)] = new_row
    return df

