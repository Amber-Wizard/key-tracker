import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw
import random
import requests
from io import BytesIO
import ast

import database
from graphing import house_dict, set_dict
from Home import default_settings
from dok_api import card_df


try:
    st.set_page_config(
        page_title="Card Trainer - KeyTracker",
        page_icon="🔑",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
except:
    pass

st.markdown("""
<style>
.deck-font {
    font-size: 32px !important;
}
.pilot-font {
    font-size: 28px !important;
    color: #6d3fc0 !important;
}
.game-data-font {
    font-size: 28px !important;
    color: #424242 !important;
}
.plain-font {
    font-size: 26px !important;
}
.hero-font {
    font-size: 26px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
}
.hero-italic-font {
    font-size: 26px !important;
    color: #60b4ff !important;
    font-style: italic !important;  /* Make this font italic */

}
.villain-italic-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
    font-style: italic !important;  /* Make this font italic */

}
</style>
""", unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def create_card_image(url, c_type):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    if c_type == 'Artifact' or c_type == 'Upgrade':
        x, y = 50, 10
    elif c_type == 'TokenCreature':
        x, y = 50, 250
    else:
        x, y = 50, 220

    width, height = 200, 35
    fill_color = (254, 254, 254)
    outline_color = (0, 0, 0)
    draw = ImageDraw.Draw(img)
    draw.rectangle([x, y, x + width, y + height], fill=fill_color, outline=outline_color, width=3)

    return img


def reset_buttons():
    st.session_state.button_dict = {
        'guess_1': {'disabled': False, 'primary': 'secondary', 'icon': '✔'},
        'guess_2': {'disabled': False, 'primary': 'secondary', 'icon': '✔'},
        'guess_3': {'disabled': False, 'primary': 'secondary', 'icon': '✔'},
        'guess_4': {'disabled': False, 'primary': 'secondary', 'icon': '✔'},
    }


def check_answer(x):
    st.session_state.revealed = True

    st.session_state.button_dict = {
        'guess_1': {'disabled': True, 'primary': 'secondary', 'icon': '❌'},
        'guess_2': {'disabled': True, 'primary': 'secondary', 'icon': '❌'},
        'guess_3': {'disabled': True, 'primary': 'secondary', 'icon': '❌'},
        'guess_4': {'disabled': True, 'primary': 'secondary', 'icon': '❌'},
    }

    st.session_state.button_dict[f'guess_{st.session_state.real_location}'] = {'disabled': False, 'primary': 'primary', 'icon': 'Next ►'}

    if x == st.session_state.real_location:
        st.session_state.streak += 1
        st.session_state.correct += 1
        st.toast('You got it correct!')
    else:
        st.session_state.streak = 0
        st.toast("Oops! That's incorrect.")


def submit_guess(x):
    if st.session_state.revealed:
        if 'fake_idxs' in st.session_state:
            del st.session_state.fake_idxs
        assign_card()
        reset_buttons()
    else:
        check_answer(x)


def assign_card():
    st.toast('Assigning Card')
    # Pick a card
    filtered_df = st.session_state.filtered_df

    if st.session_state.current_index >= len(st.session_state.filtered_df):
        st.session_state.current_index = 0  # Restart from the beginning if all cards have been shown
        st.session_state.revealed = False
        st.session_state.streak = 0
        st.session_state.correct = 0
        st.toast("You've gone through all the cards! Restarting...")
        st.session_state.filtered_df = st.session_state.filtered_df.sample(frac=1).reset_index(drop=True)  # Reshuffle

    # Pick the card at the current index
    print(st.session_state.current_index)
    card_row = st.session_state.filtered_df.iloc[st.session_state.current_index]
    st.session_state.current_index += 1  # Move to the next card for the next round

    image_link = card_row['cardTitleUrl']
    card_name = card_row['cardTitle']
    card_type = card_row['cardType']
    card_houses = ast.literal_eval(card_row['houses'])

    # Remove the card itself
    filtered_df = filtered_df[filtered_df['cardTitle'] != card_name]

    # Filter to only cards of the same type (if possible)
    type_df = filtered_df[filtered_df['cardType'] == card_type]

    if len(type_df) < 4:
        type_df = filtered_df

    # Filter to only cards of the same house (if possible)
    h_pattern = '|'.join(card_houses)

    match_df = type_df[type_df['houses'].str.contains(h_pattern, case=False, na=False)]

    if len(match_df) < 4:
        match_df = type_df

    # Assign fake cards
    if 'fake_idxs' not in st.session_state:
        fake_idxs = random.sample(range(len(match_df)), 3)
        fake_images = []

        for f_idx in fake_idxs:
            fake_card_row = match_df.iloc[f_idx]
            fake_card_type = fake_card_row['cardType']
            fake_image = create_card_image(fake_card_row['cardTitleUrl'], fake_card_type)
            fake_images.append(fake_image)

        card_image = create_card_image(image_link, card_type)
        real_location = random.randint(1, 4)
        fake_images.insert(real_location - 1, card_image)

        st.session_state.card_name = card_name
        st.session_state.fake_images = fake_images
        st.session_state.real_location = real_location
        st.session_state.fake_idxs = fake_idxs
        st.session_state.revealed = False
        st.session_state.card_row = card_row

with st.expander('Settings'):
    set_list = ['All'] + list(set_dict.keys())
    set_selections = st.multiselect('Sets', set_list, default='All')
    converted_sets = [set_dict[s]['Full Name'] for s in set_selections if s != 'All']
    if 'All' in set_selections:
        converted_sets += ['All']

    house_list = ['All'] + list(house_dict.keys())
    house_selections = st.multiselect('Houses', house_list, default='All')

    card_type_list = ['All', 'Creature', 'Action', 'Upgrade', 'Artifact']
    card_type_selections = st.multiselect('Card Types', card_type_list, default='All')

if st.button('Start'):
    filtered_card_df = card_df.loc[~card_df['cardTitle'].str.contains('Evil Twin', case=False, na=False)]
    filtered_card_df = filtered_card_df[filtered_card_df['houses'].str.len() <= 50]

    if converted_sets and 'All' not in converted_sets:
        pattern = "|".join(converted_sets)
        filtered_card_df = filtered_card_df[filtered_card_df['expansions'].str.contains(pattern)]

    if house_selections and 'All' not in house_selections:
        pattern = "|".join(house_selections)
        filtered_card_df = filtered_card_df[filtered_card_df['expansions'].str.contains(pattern)]

    if card_type_selections and 'All' not in card_type_selections:
        filtered_card_df = filtered_card_df.loc[filtered_card_df['cardType'].isin(card_type_selections)]

    filtered_card_df = filtered_card_df.sample(frac=1).reset_index(drop=True)
    filtered_card_df = filtered_card_df.drop_duplicates().reset_index(drop=True)

    st.session_state.filtered_df = filtered_card_df

    if 'fake_idxs' in st.session_state:
        del st.session_state.fake_idxs

    assign_card()
    st.session_state.revealed = False
    reset_buttons()
    st.session_state.streak = 0
    st.session_state.correct = 0
    st.session_state.current_index = 0

st.divider()

mode = 'title'

if 'filtered_df' not in st.session_state:
    filtered_card_df = card_df.loc[~card_df['cardTitle'].str.contains('Evil Twin', case=False, na=False)]
    filtered_card_df = filtered_card_df[filtered_card_df['houses'].str.len() <= 50]
    st.session_state.filtered_df = filtered_card_df

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

if len(st.session_state.filtered_df) > 500:
    st.error("Too many cards. Please add additional filters.")
else:

    if 'card_row' not in st.session_state:
        assign_card()

    if 'revealed' not in st.session_state:
        st.session_state.revealed = False

    if 'button_dict' not in st.session_state:
        reset_buttons()

    if 'streak' not in st.session_state:
        st.session_state.streak = 0

    if 'correct' not in st.session_state:
        st.session_state.correct = 0

    if mode == 'title':
        c_name = st.session_state.card_name

        cols = st.columns([1.75, 0.25], vertical_alignment='center')
        cols[0].progress(st.session_state.current_index / len(st.session_state.filtered_df))
        if st.session_state.current_index > 0:
            current_guess_rate = min(100, round(100 * st.session_state.correct / st.session_state.current_index))
            if current_guess_rate == 100:
                cols[1].markdown(f'<b class="hero-italic-font">{current_guess_rate}%</b>', unsafe_allow_html=True)
            elif current_guess_rate >= 75:
                cols[1].markdown(f'<p class="hero-font">{current_guess_rate}%</p>', unsafe_allow_html=True)
            elif current_guess_rate >= 50:
                cols[1].markdown(f'<p class="plain-font">{current_guess_rate}%</p>', unsafe_allow_html=True)
            elif current_guess_rate >= 25:
                cols[1].markdown(f'<p class="villain-font">{current_guess_rate}%</p>', unsafe_allow_html=True)
            else:
                cols[1].markdown(f'<b class="villain-italic-font">{current_guess_rate}%</b>', unsafe_allow_html=True)

        cols = st.columns([0.5, 1, 0.2, 0.15, 0.15], vertical_alignment='center')
        with cols[1].container(border=True, height=60):
            st.markdown(f'<div style="text-align: center;">{c_name}</div>', unsafe_allow_html=True)

        if 'streak' in st.session_state and st.session_state.streak > 2:
            cols[3].markdown(f'<b class="plain-font">{st.session_state.streak}</b>', unsafe_allow_html=True)
            cols[4].image('https://community.wacom.com/en-de/wp-content/uploads/sites/20/2023/10/Flame_GIF_1.gif')


        card_images = st.session_state.fake_images

        _, c1, _, c2, _ = st.columns([0.4, 1, 0.3, 1, 0.4])

        button_dict = st.session_state.button_dict

        c1.image(card_images[0])
        c2.image(card_images[1])

        c1.button(button_dict['guess_1']['icon'], use_container_width=True, key='guess_1', disabled=button_dict['guess_1']['disabled'], type=button_dict['guess_1']['primary'], on_click=submit_guess, args=[1])

        c2.button(button_dict['guess_2']['icon'], use_container_width=True, key='guess_2', disabled=button_dict['guess_2']['disabled'], type=button_dict['guess_2']['primary'], on_click=submit_guess, args=[2])

        c1.image(card_images[2])
        c2.image(card_images[3])

        c1.button(button_dict['guess_3']['icon'], use_container_width=True, key='guess_3', disabled=button_dict['guess_3']['disabled'], type=button_dict['guess_3']['primary'], on_click=submit_guess, args=[3])
        c2.button(button_dict['guess_4']['icon'], use_container_width=True, key='guess_4', disabled=button_dict['guess_4']['disabled'], type=button_dict['guess_4']['primary'], on_click=submit_guess, args=[4])




