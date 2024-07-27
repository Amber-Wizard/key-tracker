import streamlit as st
# from streamlit_gsheets import GSheetsConnection
import pandas as pd
# from deta import Deta


def connect():
    # Create a connection object.
    # conn = st.connection("gsheets", type=GSheetsConnection)
    return conn


def pull(ws):
    conn = connect()
    df = conn.read(worksheet=ws)
    return df


def post(ws, data=None, df=None):
    conn = connect()
    if df is None:
        df = pull(ws)
    if data is None:
        new_df = df
    else:
        new_df = pd.concat([df, data], axis=0)
    conn.update(
        worksheet=ws,
        data=new_df
    )
    return new_df


def pull_user_games(username):
    games_df = pull('Games')
    player_games = games_df[games_df['Player'] == username]
    return player_games


def pull_game(gid):
    games_df = pull('Games')
    game = games_df.loc[games_df['ID'] == gid].iloc[0]
    return game















