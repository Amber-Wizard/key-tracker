import streamlit as st
import pandas as pd
import urllib.error
import pymongo
from bson.objectid import ObjectId
import time
from datetime import datetime, timedelta

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
    'MORE_MUTATION': ['MMM'],
    'VAULT_MASTERS_2023': ['VM23'],
    'VAULT_MASTERS_2024': ['VM24'],
    'DISCOVERY': ['Disc'],
}


@st.cache_resource
def get_client():
    username = st.secrets['mongo']['username']
    password = st.secrets['mongo']['password']
    mongo_string = f'mongodb+srv://{username}:{password}@keytracker.ztswoqe.mongodb.net/?retryWrites=true&w=majority&appName=KeyTracker'
    c = pymongo.MongoClient(mongo_string, serverSelectionTimeoutMS=5000)
    print('Connected to database.')
    db_list = ['Users', 'Games', 'Dok Data', 'ELO', 'Featured Games', 'Snapshot', 'Alliances']
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


def del_database(db_name):
    db = get_database(db_name)
    result = db.delete_many({})
    return result


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


def get_name_conversion_dict():
    user_db = get_all_users()
    name_conversion_dict = {}

    for user in user_db:
        name_conversion_dict[user['tco_name']] = user['tco_name']
        if 'aliases' in user:
            for alias in user['aliases']:
                name_conversion_dict[alias] = user['tco_name']

    return name_conversion_dict


def get_private_data_users():
    db = get_database('Users')
    return db.find({'game_data_use': False})


def update_user_settings(player, settings):
    db = get_database('Users')
    query = {'tco_name': player}
    update_data = {'$set': settings}
    inserted_result = db.update_one(query, update_data, upsert=False)

    return inserted_result


def remove_user_setting(player, setting):
    db = get_database('Users')
    query = {'tco_name': player}
    update_data = {'$unset': {setting: ""}}
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


def update_game_winner(gid, winner):
    db = get_database('Games')
    query = {'ID': gid}
    new_values = {"$set": {"Winner": [winner]}}
    result = db.update_one(query, new_values)

    if result.modified_count > 0:
        print(f"Updated Winner [{gid}] - {winner}")
        return True
    else:
        print(f"Failed to update Winner [{gid}]: {winner}")
        return False


def update_game_format(gid: str, game_format: str):
    db = get_database('Games')
    query = {'ID': gid}

    if isinstance(game_format, list):
        game_format = game_format[0]

    if isinstance(gid, list):
        gid = gid[0]

    # First, check if the value is already correct
    existing_game = db.find_one(query, {'Format': 1})

    if existing_game and existing_game.get('Format') == [game_format]:
        print(f"Format already set for [{gid}] - {game_format}")
        return True  # No update needed, but not an error

    # Otherwise, update the format
    new_values = {"$set": {"Format": [game_format]}}
    result = db.update_one(query, new_values)

    if result.modified_count > 0:
        print(f"Updated Format [{gid}] - {game_format}")
        return True
    else:
        print(f"Failed to update Format [{gid}]: {game_format}")
        return False


def update_alliance_deck(gid, alliance, alliance_link, player_deck=True):
    if not update_game_format(gid, 'Alliance'):
        return False, 'Error updating game format.'

    if not update_game_decks(gid, deck=alliance, deck_link=alliance_link, player=player_deck):
        return False, 'Error updating game decks.'

    return True, f"Updated deck: {alliance}."


def add_alliance_deck(gid, alliance, player, player_deck=True):
    dok_data = dok_api.pull_alliance_data(alliance['link'].split('/')[-1])
    if not dok_data:
        return False, 'Error retrieving DoK data.'

    db = get_database('Alliances')
    alliance_data = {'player': player, 'alliance': alliance['name'], 'link': alliance['link'], 'data': dok_data}
    if not db.insert_one(alliance_data).acknowledged:
        return False, 'Error storing alliance in database.'

    if not update_game_format(gid, 'Alliance'):
        return False, 'Error updating game format.'

    if not update_game_decks(gid, deck=alliance['name'], deck_link=alliance['link'], player=player_deck):
        return False, 'Error updating game decks.'

    return True, f"Added alliance deck: {alliance['name']}."


def get_alliance(alliance, player):
    db = get_database('Alliances')
    return db.find_one({'alliance': alliance, 'player': player})


def get_user_alliances(username, aliases=None):
    db = get_database('Alliances')
    data = db.find({'player': username})
    df = to_dataframe(data)

    if aliases:
        for alias in aliases:
            alias_data = db.find({'player': alias})
            alias_df = to_dataframe(alias_data)
            if len(alias_df) > 0:
                df = pd.concat([df, alias_df], ignore_index=True)

    return df


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

    def count_turns(game_log):
        try:
            return len(game_log[0][[k for k in game_log[0].keys() if k != 'player_hand'][0]]['cards_played'])
        except:
            return 0

    if 'Game Log' in df.columns and len(df) > 0:
        df['Turns'] = df['Game Log'].apply(count_turns)

        try:
            sorted_df = df.sort_values(by='Date', ascending=False)
        except:
            update_dates()
            try:
                sorted_df = df.sort_values(by='Date', ascending=False)
            except:
                sorted_df = df

        if 'Format' in sorted_df.columns:
            sorted_df['Format'] = sorted_df['Format'].apply(lambda x: x if isinstance(x, list) else ['Archon'])
        else:
            sorted_df['Format'] = [['Archon']] * len(sorted_df)

        game_log_dict = {
            'archon': sorted_df[sorted_df['Format'].apply(lambda x: x == ['Archon'])],
            'sealed': sorted_df[sorted_df['Format'].apply(lambda x: x == ['Sealed'])],
            'alliance': sorted_df[sorted_df['Format'].apply(lambda x: x == ['Alliance'])],
        }

        if trim_lists:
            for k, v in game_log_dict.items():
                game_log_dict[k] = v.applymap(lambda x: x[0] if isinstance(x, list) and len(x) == 1 else x)

        return game_log_dict
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
    if len(deck_id) == 36:
        db = get_database('Dok Data')
        dok_data = db.find_one({'ID': deck_id})
        if not dok_data:
            db = get_database('Alliances')
            dok_data = db.find_one({'link': "https://decksofkeyforge.com/alliance-decks/" + deck_id})
            if dok_data:
                dok_data['Data'] = dok_data['data']
                del dok_data['data']
        if not dok_data:
            dok_data = update_dok_data(deck_id)
        return dok_data


def get_dok_cache_deck_name(deck_name):
    db = get_database('Dok Data')
    dok_data = db.find_one({'Deck': deck_name})
    if not dok_data:
        db = get_database('Alliances')
        dok_data = db.find_one({'alliance': deck_name})
        if dok_data:
            dok_data['Data'] = dok_data['data']
            del dok_data['data']

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
        print(f"Error updating DoK Data for {deck_id}: {raw_dok_data}")
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
        def process_user_decks(filtered_games):
            if not isinstance(filtered_games, pd.DataFrame):  # Ensure it's a DataFrame
                return pd.DataFrame(columns=['Deck', 'Games', 'Deck Link', 'Wins', 'Losses', 'Win-Loss', 'Winrate'])

            if filtered_games.empty:
                return pd.DataFrame(columns=['Deck', 'Games', 'Deck Link', 'Wins', 'Losses', 'Win-Loss', 'Winrate'])

            games_counts = pd.Series([item[0] for item in filtered_games['Deck']]).value_counts()
            user_decks = games_counts.reset_index()
            user_decks.columns = ['Deck', 'Games']

            deck_link_mapping = {row['Deck'][0]: row['Deck Link'][0] for _, row in filtered_games.iterrows()}
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

            wins, losses, wl, winrates = [], [], [], []
            for idx, row in user_decks.iterrows():
                deck_games = filtered_games[
                    (filtered_games['Deck'].apply(lambda x: x[0]) == row['Deck']) &
                    (filtered_games['Player'].apply(lambda x: x[0] in name_list))
                    ]
                deck_wins = len(deck_games[deck_games['Winner'].apply(lambda x: x[0] in name_list)])
                deck_losses = len(deck_games) - deck_wins

                winrate = round(100 * deck_wins / len(deck_games)) if len(deck_games) > 0 else None
                wins.append(deck_wins)
                losses.append(deck_losses)
                wl.append(f"{deck_wins}-{deck_losses}")
                winrates.append(winrate)

            user_decks['Wins'] = wins
            user_decks['Losses'] = losses
            user_decks['Win-Loss'] = wl
            user_decks['Winrate'] = winrates

            user_decks = user_decks[user_decks['Games'] >= 2]
            user_decks['Deck'] = user_decks['Deck'].apply(lambda x: [x])

            return user_decks

        # Create a dictionary of user decks for each format
        user_decks_dict = {format_name: process_user_decks(df) for format_name, df in user_games.items()}

        return user_decks_dict
    else:
        return None


def update_elo(player, deck, deck_data, game_format):
    db = get_database('ELO')
    query = {'player': player, 'deck': deck}
    update_data = {'$set': {'player': player, 'format': game_format, 'deck': deck, 'score': deck_data['score'], 'games': deck_data['games'], 'wins': deck_data['wins']}}
    inserted_result = db.update_one(query, update_data, upsert=True)

    return inserted_result


def update_player_elo(player, elo_data):
    db = get_database('Users')
    query = {'tco_name': player}
    update_data = {'$set': {'games_played': {f: {'score': elo_data[f]['score'], 'games': elo_data[f]['games'], 'wins': elo_data[f]['wins']} for f in ['Archon', 'Alliance', 'Sealed']}}}
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


def get_elo(player, deck, game_format):
    db = get_database('ELO')
    query = {'player': player, 'deck': deck}
    data = db.find_one(query)

    if not data:
        update_result = update_elo(player, deck, {'score': 1500, 'games': 0, 'wins': 0}, game_format)

        data = {
            '_id': update_result.upserted_id,  # This will contain the ID of the newly created document
            'player': player,
            'deck': deck,
            'format': game_format,
            'score': 1500,
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


def calculate_elo(starting_value=1500, k_value=30):
    del_database('ELO')
    games = get_all_games()
    games = games.sort_values(by='Date', ascending=True)
    name_conversion_dict = get_name_conversion_dict()
    print(name_conversion_dict)
    unique_players = games['Player'].unique()
    for p in unique_players:
        if p not in name_conversion_dict:
            name_conversion_dict[p] = p
    print(name_conversion_dict)
    games['Player'] = games['Player'].map(name_conversion_dict)
    players = games['Player'].unique()
    opponents = games['Opponent'].unique()
    player_elo_dict = {}
    opponent_elo_dict = {}

    for p in players:
        decks = games.loc[games['Player'] == p, 'Deck'].unique()

        # Create a deck -> set of formats mapping
        deck_format_map = (games.loc[games['Player'] == p, ['Deck', 'Format']]
                           .drop_duplicates()
                           .groupby('Deck')['Format']
                           .apply(set)  # Store formats as a set
                           .to_dict())

        # Construct player_elo_dict with decks appearing in multiple formats
        player_elo_dict[p] = {
            f: {
                'score': starting_value,
                'games': 0,
                'wins': 0,
                'decks': {
                    d: {'format': f, 'score': starting_value, 'games': 0, 'wins': 0}
                    for d in decks if f in deck_format_map.get(d, set())  # Check set membership
                }
            }
            for f in ['Archon', 'Alliance', 'Sealed']
        }

    for o in opponents:
        # Get all unique opponent decks
        decks = games.loc[games['Opponent'] == o, 'Opponent Deck'].unique()

        # Create a deck -> set of formats mapping
        deck_format_map = (games.loc[games['Opponent'] == o, ['Opponent Deck', 'Format']]
                           .drop_duplicates()
                           .groupby('Opponent Deck')['Format']
                           .apply(set)  # Store formats as a set
                           .to_dict())

        # Construct opponent_elo_dict with decks appearing in multiple formats
        opponent_elo_dict[o] = {
            f: {
                'score': starting_value,
                'games': 0,
                'wins': 0,
                'decks': {
                    d: {'format': f, 'score': starting_value}
                    for d in decks if f in deck_format_map.get(d, set())  # Check set membership
                }
            }
            for f in ['Archon', 'Alliance', 'Sealed']
        }

    for idx, game in games.iterrows():
        player = game['Player']
        opponent = game['Opponent']
        p_deck = game['Deck']
        op_deck = game['Opponent Deck']
        game_format = game['Format']

        p1_expected = 1 / (1 + 10**((opponent_elo_dict[opponent][game_format]['score'] - player_elo_dict[player][game_format]['score'])/400))
        p2_expected = 1 - p1_expected

        try:
            player_deck_score = player_elo_dict[player][game_format]['decks'][p_deck]['score']
        except:
            print(f'Error getting deck score for player {player} ({p_deck})')
            print('Player Decks:')
            for d in player_elo_dict[player][game_format]['decks'].keys():
                print(d)
            print('')
            print('Game Info:')
            for k, v in game.items():
                print(f'{k}: {v}')
            print('')
            raise Exception("Error - Deck Score Not Found")

        try:
            opponent_deck_score = opponent_elo_dict[opponent][game_format]['decks'][op_deck]['score']
        except:
            print(f'Error getting deck score for player {player} ({p_deck})')
            print('Player Decks:')
            for d in opponent_elo_dict[opponent][game_format]['decks'].keys():
                print(d)
            print('')
            print('Game Info:')
            for k, v in game.items():
                print(f'{k}: {v}')
            print('')
            raise Exception("Error - Deck Score Not Found")

        p1_deck_expected = 1 / (1 + 10**((opponent_deck_score - player_deck_score)/400))
        p2_deck_expected = 1 - p1_deck_expected

        player_elo_dict[player][game_format]['games'] += 1
        player_elo_dict[player][game_format]['decks'][p_deck]['games'] += 1

        if game['Winner'] == player:
            player_adjustment = round(k_value * p2_expected)
            deck_adjustment = round(k_value * p2_deck_expected)
            player_elo_dict[player][game_format]['score'] += player_adjustment
            opponent_elo_dict[opponent][game_format]['score'] -= player_adjustment
            player_elo_dict[player][game_format]['decks'][p_deck]['score'] += deck_adjustment
            opponent_elo_dict[opponent][game_format]['decks'][op_deck]['score'] -= deck_adjustment
            player_elo_dict[player][game_format]['wins'] += 1
            player_elo_dict[player][game_format]['decks'][p_deck]['wins'] += 1
        else:
            player_adjustment = round(k_value * p1_expected)
            deck_adjustment = round(k_value * p1_deck_expected)
            player_elo_dict[player][game_format]['score'] -= player_adjustment
            opponent_elo_dict[opponent][game_format]['score'] += player_adjustment
            player_elo_dict[player][game_format]['decks'][p_deck]['score'] -= deck_adjustment
            opponent_elo_dict[opponent][game_format]['decks'][op_deck]['score'] += deck_adjustment

        print(f"Game {idx} calculated")

    for p in player_elo_dict.keys():
        update_player_elo(p, player_elo_dict[p])
        for game_format in ['Archon', 'Alliance', 'Sealed']:
            print(game_format)
            print(f"{p}: {player_elo_dict[p][game_format]['score']} ({player_elo_dict[p][game_format]['games']} games)")
            for d in player_elo_dict[p][game_format]['decks'].keys():
                print(f"    {d}: {player_elo_dict[p][game_format]['decks'][d]}")
                update_elo(p, d, player_elo_dict[p][game_format]['decks'][d], game_format)
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
            featured_games.at[idx, 'Date'] = game_data.get('Date', None)
            for attribute in ['Player', 'Opponent', 'Winner', 'Deck', 'Opponent Deck']:
                featured_games.at[idx, attribute] = game_data.get(attribute, [''])
            # deck_id = game_data.get('Deck Link', [''])[0].split('/')[-1]
            # dok_data = get_dok_cache_deck_id(deck_id)
            # featured_games.at[idx, 'SAS'] = dok_data['Data']['deck']['sasRating']
            # featured_games.at[idx, 'Set'] = set_conversion_dict[dok_data['Data']['deck']['expansion']][0]

            # op_deck_id = game_data.get('Opponent Deck Link', [''])[0].split('/')[-1]
            # op_dok_data = get_dok_cache_deck_id(op_deck_id)
            # featured_games.at[idx, 'Op. SAS'] = op_dok_data['Data']['deck']['sasRating']
            # featured_games.at[idx, 'Op. Set'] = set_conversion_dict[op_dok_data['Data']['deck']['expansion']][0]

    if 'Date' in featured_games.columns:
        featured_games = featured_games.dropna(subset=['Date'])
        sorted_games = featured_games.sort_values(by=['Date', 'Likes'], ascending=[False, False])
        return sorted_games
    else:
        print('No Date Column Present')
        return featured_games


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


def get_all_recent_games(days=30, data_share=True):
    collection = get_database('Games')

    start_date = datetime.now() - timedelta(days=days)

    recent_games = collection.find({"Date": {"$gte": start_date}})

    recent_games_df = to_dataframe(recent_games)
    # recent_games_df = recent_games_df.loc[recent_games_df['Format'].str[0] == 'Archon']
    if data_share:
        private_data_users = list(get_private_data_users())
        private_data_username_list = [p['tco_name'] for p in private_data_users]
        for u in private_data_users:
            if 'aliases' in u:
                private_data_username_list += u['aliases']
        private_data_username_list = [[p] for p in private_data_username_list]

        recent_games_df = recent_games_df[~recent_games_df['Player'].isin(private_data_username_list)]

    return recent_games_df


def log_meta_sets(set_data):
    db = get_database('Snapshot')
    query = {'type': 'set data'}
    update_data = {'$set': {'Data': set_data}}
    inserted_result = db.update_one(query, update_data, upsert=True)

    return inserted_result


def get_meta_sets():
    db = get_database('Snapshot')
    query = {'type': 'set data'}
    data = db.find_one(query)

    return data


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

# calculate_elo(1500, 30)


# Database Processing

def update_nf_games():
    db = get_database('Games')
    games = db.find({'Format': {'$ne': ['Sealed']}, 'Deck': ['---']})

    for game in games:
        update_game_format(game['ID'], 'Sealed')
        print(f'Format updated for game: {"ID"}')

