import json
import requests
import time
import pandas as pd
import streamlit as st

headers = {
    "Api-Key": "0287d9c7-e0b6-4689-867c-f7223e520077" #st.secrets['dok']['api_key']
}


def pull_deck_data(deck_id):
    time.sleep(2.5)
    response = requests.get("https://decksofkeyforge.com/public-api/v3/decks/" + deck_id, headers=headers)

    data = response.json()

    return data


def pull_card_data():
    time.sleep(2.5)
    response = requests.get("https://decksofkeyforge.com/public-api/v1/cards", headers=headers)

    data = response.json()

    text = json.dumps(data, sort_keys=True, indent=4)

    df = pd.read_json(text)

    df.to_csv('card_log.csv', index=False)
    return df


@st.cache_resource
def load_card_data():
    card_data = pd.read_csv("card_log.csv")
    return card_data

card_df = load_card_data()


def check_card_type(card_name):
    result = card_df.loc[card_df['cardTitle'] == card_name, 'cardType']
    return result.iloc[0] if not result.empty else None

