import json
import requests
import time
import pandas as pd
import streamlit as st
import ast

headers = {
    "Api-Key": st.secrets['dok']['api_key']
}


def pull_alliance_data(deck_id):
    time.sleep(2.5)
    response = requests.get("https://decksofkeyforge.com/public-api/v1/alliance-decks/" + deck_id, headers=headers)

    try:
        data = response.json()
        return data
    except:
        print(response)
        return None


def pull_deck_data(deck_id):
    time.sleep(2.5)
    response = requests.get("https://decksofkeyforge.com/public-api/v3/decks/" + deck_id, headers=headers)

    try:
        data = response.json()
        return data
    except:
        print(response)
        return None


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
    crd = {}
    chd = {}
    for idx, row in card_data.iterrows():
        card_rarities = []
        card_sets = []
        for exp in ast.literal_eval(row['expansions']):
            if exp['rarity'] not in card_rarities and exp['rarity'] not in ['Special', 'Variant', 'FIXED']:
                card_rarities.append(exp['rarity'])
                card_sets.append(exp['expansion'])
                if len(card_rarities) > 1:
                    print(row['cardTitle'], card_rarities, card_sets)
                    break
        if len(card_rarities) == 1:
            crd[row['cardTitle']] = card_rarities[0]
        else:
            crd[row['cardTitle']] = "Special"

        houses = ast.literal_eval(row['houses'])
        for nh in ['Elders', 'IronyxRebels', 'Redemption']:
            if nh in houses:
                houses.remove(nh)
        if len(houses) == 1:
            chd[row['cardTitle']] = houses[0]
        else:
            chd[row['cardTitle']] = "Special"

    cid = card_data.set_index('cardTitle')['cardTitleUrl'].to_dict()
    return card_data, cid, crd, chd

card_df, card_image_dict, card_rarity_dict, card_house_dict = load_card_data()


def fix_card_string(card_name):
    fixed_string = card_name.replace('”', '"').replace('“', '"').replace("’", "'")
    return fixed_string


def get_card_image(card_name):
    fixed_string = fix_card_string(card_name)
    if card_name in card_image_dict:
        return card_image_dict[card_name]
    elif fixed_string in card_image_dict:
        return card_image_dict[fixed_string]
    else:
        return None


def get_card_rarity(card_name):
    fixed_string = fix_card_string(card_name)
    if card_name in card_rarity_dict:
        return card_rarity_dict[card_name]
    elif fixed_string in card_rarity_dict:
        return card_rarity_dict[fixed_string]
    else:
        return None


def get_card_house(card_name):
    fixed_string = fix_card_string(card_name)
    if card_name in card_house_dict:
        return card_house_dict[card_name]
    elif fixed_string in card_house_dict:
        return card_house_dict[fixed_string]
    else:
        return None


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

# https://decksofkeyforge.com/decks/4165762c-f032-4097-b71a-9e6b8e768dcb