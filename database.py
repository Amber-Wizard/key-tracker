import streamlit as st
import pandas as pd
import urllib.error
import pymongo
from bson.objectid import ObjectId
import time
from datetime import datetime

import dok_api

set_conversion_dict = {
    'CALL_OF_THE_ARCHONS': ['CotA'],
    'AGE_OF_ASCENSION': ['AoA'],
    'WORLDS_COLLIDE': ['WC'],
    'MASS_MUTATION': ['MM'],
    'DARK_TIDINGS': ['DT'],
    'WINDS_OF_EXCHANGE': ['WoE'],
    'GRIM_REMINDERS': ['GR'],
    'AEMBER_SKIES': ['AES'],
    'TOKENS_OF_CHANGE': ['ToC'],
    'VAULT_MASTERS_2023': ['VM23'],
    'VAULT_MASTERS_2024': ['VM24'],
}


@st.cache_resource
def get_client():
    username = st.secrets['mongo']['username']
    password = st.secrets['mongo']['password']
    mongo_string = f'mongodb+srv://{username}:{password}@keytracker.ztswoqe.mongodb.net/?retryWrites=true&w=majority&appName=KeyTracker'
    c = pymongo.MongoClient(mongo_string, serverSelectionTimeoutMS=5000)
    db_list = ['Users', 'Games', 'Dok Data', 'ELO', 'Featured Games']
    db_dict = {db: c['KeyTracker'][db] for db in db_list}
    return c, db_dict

client, database_dict = get_client()


def to_dataframe(data):
    documents = list(data)
    df = pd.DataFrame(documents)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df


def get_database(db_name):
    return database_dict[db_name]


def add_user(username, password, email, tco_name):
    db = get_database('Users')
    return db.insert_one({"username": username, "password": password, "email": email, "tco_name": tco_name}).acknowledged


def delete_user(username):
    db = get_database('Users')
    return db.delete_many({'username': username}).acknowledged


def get_user(tco_name):
    db = get_database('Users')
    user = db.find_one({'tco_name': tco_name})

    if not user:
        user = db.find_one({'aliases': {'$in': [tco_name]}})

    return user


def get_all_users():
    db = get_database('Users')
    return db.find()


def update_user_settings(player, settings):
    db = get_database('Users')
    query = {'tco_name': player}
    update_data = {'$set': settings}
    inserted_result = db.update_one(query, update_data, upsert=False)

    return inserted_result


def check_name(tco_name):
    users = get_all_users()
    user_df = to_dataframe(users)

    if tco_name in user_df['tco_name'].values:
        return False

    if 'aliases' in user_df:
        if user_df['aliases'].apply(lambda lst: isinstance(lst, list) and tco_name in lst).any():
            return False

    return True


def add_alias(player, alias):
    if check_name(alias):
        db = get_database('Users')
        query = {'tco_name': player}
        player_info = db.find_one(query)
        if 'aliases' in player_info:
            new_aliases = player_info['aliases'] + [alias]
        else:
            new_aliases = [alias]

        update_data = {'$set': {'aliases': new_aliases}}
        inserted_result = db.update_one(query, update_data, upsert=False)

        return inserted_result
    else:
        return None


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


def get_user_games(username, aliases=None, trim_lists=False):
    db = get_database('Games')
    data = db.find({'Player': username})
    df = to_dataframe(data)

    if aliases:
        for alias in aliases:
            alias_data = db.find({'Player': alias})
            alias_df = to_dataframe(alias_data)
            if len(alias_df) > 0:
                df = pd.concat([df, alias_df], ignore_index=True)

    df['Turns'] = df['Game Log'].apply(lambda x: len(x[0][[k for k in x[0].keys() if k != 'player_hand'][0]]['cards_played']))

    if len(df) > 0:
        sorted_df = df.sort_values(by='Date', ascending=False)
        if 'Format' in sorted_df.columns:
            sorted_df['Format'] = sorted_df['Format'].apply(lambda x: x if isinstance(x, list) else ['Archon'])
        else:
            sorted_df['Format'] = [['Archon']] * len(sorted_df)
        if trim_lists:
            sorted_df = sorted_df.applymap(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

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


def get_deck_games(username, deck, aliases=None, trim_lists=False):
    print(f"Getting Deck Games: {username}, {deck}, {aliases}")
    db = get_database('Games')
    data = db.find({'Player': username, 'Deck': deck})
    df = to_dataframe(data)

    if aliases:
        for name in aliases:
            data = db.find({'Player': name, 'Deck': deck})
            new_df = to_dataframe(data)
            if len(new_df) > 0:
                if len(df) > 0:
                    df = pd.concat([df, new_df], ignore_index=True)
                else:
                    df = new_df

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
    dok_data = db.find_one({'Deck': deck_name})
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


def get_user_decks(username, aliases=None, game_data=None):
    if aliases:
        name_list = [username] + aliases
    else:
        name_list = [username]

    if game_data is not None:
        user_games = game_data
    else:
        user_games = get_user_games(username, aliases=aliases)
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
            deck_games = user_games[(user_games['Deck'].apply(lambda x: x[0]) == row['Deck']) & (user_games['Player'].apply(lambda x: x[0] in name_list))]

            deck_wins = len(deck_games[deck_games['Winner'].apply(lambda x: x[0] in name_list)])

            deck_losses = len(deck_games) - deck_wins
            if len(deck_games) > 0:
                winrate = round(100 * deck_wins / len(deck_games))
            else:
                winrate = None
            wins.append(deck_wins)
            losses.append(deck_losses)
            wl.append(f"{deck_wins}-{deck_losses}")
            winrates.append(winrate)
        user_decks['Wins'] = wins
        user_decks['Losses'] = losses
        user_decks['Win-Loss'] = wl
        user_decks['Winrate'] = winrates
        # user_decks['Deck Link'] = user_decks['Deck'].apply(lambda deck: user_games.loc[user_games['Deck'].apply(lambda x: x[0]) == deck, 'Deck Link'].apply(lambda x: x[0]).values[0])
        user_decks = user_decks[user_decks['Games'] >= 2]
        user_decks['Deck'] = user_decks['Deck'].apply(lambda x: [x])
        return user_decks
    else:
        return None


def update_elo(player, deck, deck_data):
    db = get_database('ELO')
    query = {'player': player, 'deck': deck}
    update_data = {'$set': {'player': player, 'deck': deck, 'score': deck_data['score'], 'games': deck_data['games'], 'wins': deck_data['wins']}}
    inserted_result = db.update_one(query, update_data, upsert=True)

    return inserted_result


def update_player_elo(player, elo_data):
    db = get_database('Users')
    query = {'tco_name': player}
    update_data = {'$set': {'score': elo_data['score'], 'games': elo_data['games'], 'wins': elo_data['wins']}}
    inserted_result = db.update_one(query, update_data, upsert=False)

    return inserted_result


def get_all_elo():
    db = get_database('ELO')
    return db.find()


def get_decks_elo(player):
    db = get_database('ELO')
    data = db.find({'player': player})
    print(data)
    return data


def get_elo(player, deck):
    db = get_database('ELO')
    query = {'player': player, 'deck': deck}
    data = db.find_one(query)

    if not data:
        update_result = update_elo(player, deck, {'score': 1500, 'games': 0, 'wins': 0})

        data = {
            '_id': update_result.upserted_id,  # This will contain the ID of the newly created document
            'player': player,
            'deck': deck,
            'score': 1500
        }

        if data['_id'] is None:
            data = db.find_one(query)

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
        player_elo_dict[p] = {'score': starting_value, 'games': 0, 'wins': 0, 'decks': {}}
        decks = games.loc[games['Player'] == p, 'Deck'].unique()
        player_elo_dict[p]['decks'] = {d: {'score': starting_value, 'games': 0, 'wins': 0} for d in decks}
    for o in opponents:
        opponent_elo_dict[o] = {'score': starting_value, 'decks': {}}
        decks = games.loc[games['Opponent'] == o, 'Opponent Deck'].unique()
        opponent_elo_dict[o]['decks'] = {d: {'score': starting_value} for d in decks}

    for idx, game in games.iterrows():
        player = game['Player']
        opponent = game['Opponent']
        p_deck = game['Deck']
        op_deck = game['Opponent Deck']

        p1_expected = 1 / (1 + 10**((opponent_elo_dict[opponent]['score'] - player_elo_dict[player]['score'])/400))
        p2_expected = 1 - p1_expected

        p1_deck_expected = 1 / (1 + 10**((opponent_elo_dict[opponent]['decks'][op_deck]['score'] - player_elo_dict[player]['decks'][p_deck]['score'])/400))
        p2_deck_expected = 1 - p1_deck_expected

        player_elo_dict[player]['games'] += 1
        player_elo_dict[player]['decks'][p_deck]['games'] += 1

        if game['Winner'] == player:
            player_adjustment = round(k_value * p2_expected)
            deck_adjustment = round(k_value * p2_deck_expected)
            player_elo_dict[player]['score'] += player_adjustment
            opponent_elo_dict[opponent]['score'] -= player_adjustment
            player_elo_dict[player]['decks'][p_deck]['score'] += deck_adjustment
            opponent_elo_dict[opponent]['decks'][op_deck]['score'] -= deck_adjustment
            player_elo_dict[player]['wins'] += 1
            player_elo_dict[player]['decks'][p_deck]['wins'] += 1
        else:
            player_adjustment = round(k_value * p1_expected)
            deck_adjustment = round(k_value * p1_deck_expected)
            player_elo_dict[player]['score'] -= player_adjustment
            opponent_elo_dict[opponent]['score'] += player_adjustment
            player_elo_dict[player]['decks'][p_deck]['score'] -= deck_adjustment
            opponent_elo_dict[opponent]['decks'][op_deck]['score'] += deck_adjustment

        print(f"Game {idx} calculated")

    for p in player_elo_dict.keys():
        print(f"{p}: {player_elo_dict[p]['score']}")
        update_player_elo(p, player_elo_dict[p])
        for d in player_elo_dict[p]['decks'].keys():
            print(f"    {d}: {player_elo_dict[p]['decks'][d]}")
            update_elo(p, d, player_elo_dict[p]['decks'][d])
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
            for attribute in ['Player', 'Opponent', 'Winner', 'Deck', 'Opponent Deck']:
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


def update_dates():
    collection = get_database('Games')

    # Iterate through all documents and update the Date field
    for doc in collection.find({"Date": {"$type": "array"}}):  # Only process documents with Date as an array
        try:
            # Extract the date string
            date_string = doc["Date"][0]  # Assuming Date array always has one element
            # Convert to a datetime object
            date_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
            # Update the document in the database
            collection.update_one(
                {"_id": doc["_id"]},  # Match the specific document
                {"$set": {"Date": date_object}}  # Set the new datetime object
            )
            print(f"Updated document with _id: {doc['_id']}")
        except Exception as e:
            print(f"Failed to update document with _id: {doc['_id']}. Error: {e}")

