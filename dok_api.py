import json
import requests
import time
import pandas as pd
import streamlit as st

headers = {
    "Api-Key": st.secrets['dok']['api_key']
}


def pull_deck_data(deck_id):
    time.sleep(2.5)
    response = requests.get("https://decksofkeyforge.com/public-api/v3/decks/" + deck_id, headers=headers)

    try:
        data = response.json()
        return data
    except:
        print(response)


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
    cid = card_data.set_index('cardTitle')['cardTitleUrl'].to_dict()
    return card_data, cid

card_df, card_image_dict = load_card_data()


def check_card_type(card_name):
    result = card_df.loc[card_df['cardTitle'] == card_name, 'cardType']
    return result.iloc[0] if not result.empty else None


@st.cache_resource
def test_api():
    data = pull_deck_data('b14903de-91f1-47c6-acac-460ffbd43242')
    if 'deck' in data and data['deck']:
        print('DoK API is working.')
    else:
        print('DoK API is NOT working.')

test_api()

