import streamlit as st
import pandas as pd
import urllib.error
import pymongo


@st.cache_resource
def get_client():
    username = st.secrets['mongo']['username']
    password = st.secrets['mongo']['password']
    mongo_string = f'mongodb+srv://{username}:{password}@keytracker.ztswoqe.mongodb.net/?retryWrites=true&w=majority&appName=KeyTracker'
    c = pymongo.MongoClient(mongo_string)
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
