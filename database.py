import streamlit as st
import pandas as pd
import urllib.error
import pymongo


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
    res = db.find()
    return res


def log_game(data):
    db = get_database('Games')
    return db.insert_one(data).acknowledged


def delete_game(gid):
    db = get_database('Games')
    return db.delete_one({'ID': gid}).acknowledged


def get_game(gid):
    db = get_database('Games')
    return db.find_one({'ID': gid})


def get_user_games(username):
    db = get_database('Games')
    data = db.find({'Player': username})
    df = to_dataframe(data)
    return df


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


def get_featured_game_log():
    featured_games = get_featured_games()
    for index, row in featured_games.iterrows():
        game_id = row['ID'][0]  # Extract the ID from the list
        game_data = get_game(game_id)

        if game_data:
            for attribute in ['Date', 'Player', 'Opponent', 'Winner', 'Deck', 'Opponent Deck']:
                featured_games.at[index, attribute] = game_data.get(attribute, [''])[0]
    if 'Date' in featured_games.columns:
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
