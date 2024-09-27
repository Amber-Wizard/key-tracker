import streamlit as st
import pandas as pd
import urllib.error
import pymongo
from bson.objectid import ObjectId
import time

import dok_api

set_conversion_dict = {
    'CALL_OF_THE_ARCHONS': ['CotA'],
    'AGE_OF_ASCENSION': ['AoA'],
    'WORLDS_COLLIDE': ['WC'],
    'MASS_MUTATION': ['MM'],
    'DARK_TIDINGS': ['DT'],
    'WINDS_OF_EXCHANGE': ['WoE'],
    'GRIM_REMINDERS': ['GR'],
    'VAULT_MASTERS_2023': ['VM23'],
    'VAULT_MASTERS_2024': ['VM24'],
}


@st.cache_resource
def get_client():
    username = st.secrets['mongo']['username']
    password = st.secrets['mongo']['password']
    mongo_string = f'mongodb+srv://{username}:{password}@keytracker.ztswoqe.mongodb.net/?retryWrites=true&w=majority&appName=KeyTracker'
    c = pymongo.MongoClient(mongo_string, serverSelectionTimeoutMS=5000)
    return c

client = get_client()


def to_dataframe(data):
    documents = list(data)
    df = pd.DataFrame(documents)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df


def get_database(db_name):
    return client['KeyTracker'][db_name]


def add_user(username, password, email, tco_name):
    db = get_database('Users')
    return db.insert_one({"username": username, "password": password, "email": email, "tco_name": tco_name}).acknowledged


def delete_user(username):
    db = get_database('Users')
    return db.delete_many({'username': username}).acknowledged


def get_user(username):
    db = get_database('Users')
    return db.find_one({'username': username})


def get_all_users():
    db = get_database('Users')
    return db.find()


def log_game(data):
    db = get_database('Games')
    return db.insert_one(data).acknowledged


def delete_game(gid):
    db = get_database('Games')
    return db.delete_one({'ID': gid}).acknowledged


def get_game(gid):
    db = get_database('Games')
    return db.find_one({'ID': gid})


def update_game_decks(gid, deck, deck_link, player=True):
    db = get_database('Games')
    query = {'ID': gid}
    if player:
        new_values = {"$set": {"Deck": [deck], "Deck Link": [deck_link]}}
    else:
        new_values = {"$set": {"Opponent Deck": [deck], "Opponent Deck Link": [deck_link]}}

    result = db.update_one(query, new_values)

    if result.modified_count > 0:
        print(f"Updated Deck Info [{gid}] - {deck} ({deck_link})")
        return True
    else:
        print(f"Failed to update deck info [{gid}]: {deck} ({deck_link})")
        return False


def get_user_games(username):
    db = get_database('Games')
    data = db.find({'Player': username})
    df = to_dataframe(data)
    if len(df) > 0:
        sorted_df = df.sort_values(by='Date', ascending=False)
        sorted_df['Format'] = sorted_df['Format'].apply(lambda x: x if isinstance(x, list) else ['Archon'])
        return sorted_df
    else:
        return None


def get_all_games(trim_lists=True):
    db = get_database('Games')
    data = db.find()
    df = to_dataframe(data)
    if len(df) > 0:
        sorted_df = df.sort_values(by='Date', ascending=False)
        if trim_lists:
            sorted_df = sorted_df.applymap(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

        return sorted_df
    else:
        return None


def get_deck_games(username, deck, trim_lists=False):
    db = get_database('Games')
    data = db.find({'Player': username, 'Deck': deck})
    df = to_dataframe(data)
    if len(df) > 0:
        sorted_df = df.sort_values(by='Date', ascending=False)
        if trim_lists:
            sorted_df = sorted_df.applymap(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

        return sorted_df
    else:
        return None


def get_dok_cache():
    db = get_database('Dok Data')
    return db.find()


def get_dok_cache_deck_id(deck_id):
    db = get_database('Dok Data')
    dok_data = db.find_one({'ID': deck_id})
    if not dok_data:
        dok_data = update_dok_data(deck_id)
    return dok_data


def get_dok_cache_deck_name(deck_name):
    db = get_database('Dok Data')
    dok_data = db.find_one({'Name': deck_name})
    if not dok_data:
        dok_data = None
    return dok_data


def update_all_dok_data():
    db = get_database('Dok Data')
    games = get_all_games()
    deck_links = pd.concat([games['Deck Link'], games['Opponent Deck Link']]).unique().tolist()
    deck_ids = [l.split('/')[-1] for l in deck_links]
    for deck_id in deck_ids:
        if get_dok_cache_deck_id(deck_id) is None:
            raw_dok_data = dok_api.pull_deck_data(deck_id)
            try:
                deck_name = raw_dok_data['deck']['name']
                db.insert_one({'Deck': deck_name, 'ID': deck_id, 'Data': raw_dok_data})
                print(f"Data updated for {deck_name}")
            except:
                print(f"Error updating DoK Data: {raw_dok_data}")


def update_dok_data(deck_id):
    db = get_database('Dok Data')
    raw_dok_data = dok_api.pull_deck_data(deck_id)
    try:
        deck_name = raw_dok_data['deck']['name']
        inserted_result = db.insert_one({'Deck': deck_name, 'ID': deck_id, 'Data': raw_dok_data})
        inserted_document = {
            '_id': inserted_result.inserted_id,  # This is the unique ID generated by MongoDB
            'Deck': deck_name,
            'ID': deck_id,
            'Data': raw_dok_data
        }

        print(f"Data updated for {deck_name}")
    except:
        print(f"Error updating DoK Data: {raw_dok_data}")
        inserted_document = None
    return inserted_document


def get_user_decks(username):
    user_games = get_user_games(username)
    if user_games is not None and len(user_games) > 1:
        games_counts = pd.Series([item[0] for item in user_games['Deck']]).value_counts()
        user_decks = games_counts.reset_index()
        user_decks.columns = ['Deck', 'Games']
        deck_link_mapping = {row['Deck'][0]: row['Deck Link'][0] for _, row in user_games.iterrows()}
        user_decks['Deck Link'] = user_decks['Deck'].map(deck_link_mapping)
        # user_decks['Deck'] = None
        # user_decks['SAS'] = None
        # user_decks['Set'] = None
        # for idx, row in user_decks.iterrows():
            # deck_id = row['Deck Link'].split('/')[-1]
            # dok_data = get_dok_cache_deck_id(deck_id)
            # user_decks.at[idx, 'Deck'] = dok_data['Deck']
            # user_decks.at[idx, 'SAS'] = dok_data['Data']['deck']['sasRating']
            # user_decks.at[idx, 'Set'] = set_conversion_dict[dok_data['Data']['deck']['expansion']]
            # elo_data = get_elo(username, dok_data['Deck'])

        wins = []
        losses = []
        wl = []
        winrates = []
        for idx, row in user_decks.iterrows():
            deck_games = user_games[(user_games['Deck'].apply(lambda x: x[0]) == row['Deck']) & (user_games['Player'].apply(lambda x: x[0]) == username)]
            deck_wins = len(deck_games[deck_games['Winner'].apply(lambda x: x[0]) == username])
            deck_losses = len(deck_games) - deck_wins
            winrate = round(100 * deck_wins / len(deck_games))
            wins.append(deck_wins)
            losses.append(deck_losses)
            wl.append(f"{deck_wins}-{deck_losses}")
            winrates.append(winrate)
        user_decks['Wins'] = wins
        user_decks['Losses'] = losses
        user_decks['Win-Loss'] = wl
        user_decks['Winrate'] = winrates
        # user_decks['Deck Link'] = user_decks['Deck'].apply(lambda deck: user_games.loc[user_games['Deck'].apply(lambda x: x[0]) == deck, 'Deck Link'].apply(lambda x: x[0]).values[0])
        user_decks['Deck'] = user_decks['Deck'].apply(lambda x: [x])
        return user_decks
    else:
        return None


def update_elo(player, deck, score):
    db = get_database('ELO')
    query = {'player': player, 'deck': deck}
    update_data = {'$set': {'player': player, 'deck': deck, 'score': score}}
    inserted_result = db.update_one(query, update_data, upsert=True)

    return inserted_result


def get_elo(player, deck):
    db = get_database('ELO')
    query = {'player': player, 'deck': deck}
    data = db.find_one(query)
    if not data:
        insert = update_elo(player, deck, 1500)
        data = {
            '_id': insert.inserted_id,
            'player': player,
            'deck': deck,
            'score': 1500
        }
    return data


def get_elo_by_id(share_id):
    db = get_database('ELO')
    query = {'_id': ObjectId(share_id)}
    data = db.find_one(query)

    if data:
        return data
    else:
        return None


def calculate_elo(starting_value, k_value):
    games = get_all_games()
    games = games.sort_values(by='Date', ascending=True)
    players = games['Player'].unique()
    opponents = games['Opponent'].unique()
    player_elo_dict = {}
    opponent_elo_dict = {}
    for p in players:
        player_elo_dict[p] = {'score': starting_value, 'decks': {}}
        decks = games.loc[games['Player'] == p, 'Deck'].unique()
        player_elo_dict[p]['decks'] = {d: starting_value for d in decks}
    for o in opponents:
        opponent_elo_dict[o] = {'score': starting_value, 'decks': {}}
        decks = games.loc[games['Opponent'] == o, 'Opponent Deck'].unique()
        opponent_elo_dict[o]['decks'] = {d: starting_value for d in decks}

    for idx, game in games.iterrows():
        player = game['Player']
        opponent = game['Opponent']
        p_deck = game['Deck']
        op_deck = game['Opponent Deck']

        p1_expected = 1 / (1 + 10**((opponent_elo_dict[opponent]['score'] - player_elo_dict[player]['score'])/400))
        p2_expected = 1 - p1_expected

        p1_deck_expected = 1 / (1 + 10**((opponent_elo_dict[opponent]['decks'][op_deck] - player_elo_dict[player]['decks'][p_deck])/400))
        p2_deck_expected = 1 - p1_deck_expected

        if game['Winner'] == player:
            player_adjustment = round(k_value * p2_expected)
            deck_adjustment = round(k_value * p2_deck_expected)
            player_elo_dict[player]['score'] += player_adjustment
            opponent_elo_dict[opponent]['score'] -= player_adjustment
            player_elo_dict[player]['decks'][p_deck] += deck_adjustment
            opponent_elo_dict[opponent]['decks'][op_deck] -= deck_adjustment
        else:
            player_adjustment = round(k_value * p1_expected)
            deck_adjustment = round(k_value * p1_deck_expected)
            player_elo_dict[player]['score'] -= player_adjustment
            opponent_elo_dict[opponent]['score'] += player_adjustment
            player_elo_dict[player]['decks'][p_deck] -= deck_adjustment
            opponent_elo_dict[opponent]['decks'][op_deck] += deck_adjustment

        print(f"Game {idx} calculated")

    for p in player_elo_dict.keys():
        print(f"{p}: {round(player_elo_dict[p]['score'])}")
        for d in player_elo_dict[p]['decks'].keys():
            print(f"    {d}: {round(player_elo_dict[p]['decks'][d])}")
            update_elo(p, d, round(player_elo_dict[p]['decks'][d]))
        print('')


def feature_game(gid):
    db = get_database('Featured Games')

    existing_game = db.find_one({'ID': gid})

    if existing_game:
        return False

    featured_game_dict = {'ID': gid, 'Likes': 0, 'Likers': []}
    return db.insert_one(featured_game_dict)


def get_featured_games():
    db = get_database('Featured Games')
    featured_games = db.find()
    df = to_dataframe(featured_games)
    return df


def check_featured(gid):
    db = get_database('Featured Games')
    featured_games = db.find()
    df = to_dataframe(featured_games)
    if df['ID'].apply(lambda x: gid in x).any():
        return True
    else:
        return False


def get_featured_game_log():
    featured_games = get_featured_games()
    for idx, row in featured_games.iterrows():
        game_id = row['ID'][0]  # Extract the ID from the list
        game_data = get_game(game_id)

        if game_data:
            for attribute in ['Date', 'Player', 'Opponent', 'Winner', 'Deck', 'Opponent Deck']:
                featured_games.at[idx, attribute] = game_data.get(attribute, [''])[0]
            deck_id = game_data.get('Deck Link', [''])[0].split('/')[-1]
            dok_data = get_dok_cache_deck_id(deck_id)
            featured_games.at[idx, 'SAS'] = dok_data['Data']['deck']['sasRating']
            featured_games.at[idx, 'Set'] = set_conversion_dict[dok_data['Data']['deck']['expansion']][0]

            op_deck_id = game_data.get('Opponent Deck Link', [''])[0].split('/')[-1]
            op_dok_data = get_dok_cache_deck_id(op_deck_id)
            featured_games.at[idx, 'Op. SAS'] = op_dok_data['Data']['deck']['sasRating']
            featured_games.at[idx, 'Op. Set'] = set_conversion_dict[op_dok_data['Data']['deck']['expansion']][0]

    if 'Date' in featured_games.columns:
        featured_games = featured_games.dropna(subset=['Date'])
        sorted_games = featured_games.sort_values(by=['Likes', 'Date'], ascending=[False, False])
        return sorted_games
    else:
        return []


def like_game(gid, user):
    db = get_database('Featured Games')

    game = db.find_one({'ID': gid})

    if not game:
        return False, f"Game {gid} not found."

    if user in game['Likers']:
        return False, "Already liked"

    db.update_one(
        {'ID': gid},
        {'$inc': {'Likes': 1}, '$push': {'Likers': user}}
    )

    return True, "Liked game"
