from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import re
# import matplotlib.pyplot as plt
import json
import os
import streamlit as st

from game import Game

# USERNAME = ''
# PASSWORD = ''
# if os.path.exists('config.txt'):
#     with open('config.txt', 'r') as f:
#         file_content = f.read()
#     exec(file_content)
# else:
#     default_content = "USERNAME = ''\nPASSWORD = ''\n"
#     with open('config.txt', 'w') as f:
#         f.write(default_content)


@st.cache_resource
def get_driver():
    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        )
    )

driver = get_driver()


def initialize():
    driver = webdriver.Chrome()
    driver.get("https://thecrucible.online/login")
    driver.implicitly_wait(15)

    return driver


def login(driver, username, password):
    username_input = driver.find_element('name', 'username')
    username_input.send_keys(username)

    if password is not None:
        password_input = driver.find_element('name', 'password')
        password_input.send_keys(password)
        login_button = driver.find_element('xpath', '//button[text()="Login"]')
        login_button.click()

        driver.implicitly_wait(10)
        time.sleep(1)
        driver.get("https://thecrucible.online/play")
    driver.implicitly_wait(10)


def fetch_html(driver):
    driver.implicitly_wait(10)
    html_doc = driver.page_source
    with open('file.html', 'w', encoding='utf-8') as file:
        file.write(html_doc)


def check_start():
    with open('file.html', 'rb') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    boards = soup.find_all('div', {'class': 'game-board'})

    if boards:
        return True
    else:
        return False


def check_finish(p1_messages, p2_messages):
    finish = False
    winner = None
    end_game_message = [m for m in p1_messages + p2_messages if ' has won the game ' in m]
    if len(end_game_message) > 0:
        finish = True
        winner = end_game_message[0][0]

    return finish, winner


def get_player_names():
    with open('file.html', 'rb') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')

    try:
        active_player = soup.find('div', {'class': 'pr-1 player-info active-player'}).find('b').text
        print(f"Active Player Detected: {active_player}")
    except:
        print(f"Error getting active player name")
        active_player = ""
    try:
        inactive_player = soup.find('div', {'class': 'pr-1 player-info inactive-player'}).find('b').text
        print(f"Inactive Player Detected: {inactive_player}")
    except:
        print(f"Error getting active player name")
        inactive_player = ""

    return active_player, inactive_player


def get_deck_info(names):
    with open('file.html', 'rb') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    deck_divs = soup.find_all('div', {'class': 'message mb-1'})
    deck_info = {}
    for div in deck_divs:
        name_elems = div.find_all('span', {'class': 'username user-role'})
        deck_elems = div.find_all('a', {'rel': 'noopener noreferrer'})
        name = [elem.text for elem in name_elems]
        deck = [elem.text for elem in deck_elems]
        link = [elem.get('href') for elem in deck_elems]
        dok_link = f"https://decksofkeyforge.com/decks/{link[0].split('/')[-1]}"
        try:
            deck_info[name[0]] = {'deck-name': deck[0], 'deck-link': dok_link}
        except:
            print(name, deck)
            if len(deck) > 0:
                d = deck[0]
            else:
                d = '-Error-'
            if len(name) > 0:
                deck_info[name[0]] = {'deck-name': d, 'deck-link': dok_link}
            else:
                deck_info['-Error-'] = {'deck-name': d, 'deck-link': dok_link}
    if '-Error-' in deck_info:
        dict_keys = list(deck_info.keys())
        for n in names:
            if n not in dict_keys:
                deck_info[n] = deck_info.pop('-Error-')
                print(names, dict_keys)
                print(f"Name Error Avoided")
            else:
                print(names, dict_keys)
                print(f"Name Error not avoided")

    return deck_info


def get_board_info():
    board_info = [{}, {}]

    with open('file.html', 'rb') as f:
        html_doc = f.read()

    soup = BeautifulSoup(html_doc, 'html.parser')
    panels = soup.find_all('div', {'class': 'panel player-stats'})
    names = []
    for i, panel in enumerate(panels):
        # Get players
        try:
            name_div = panel.find('div', {'class': 'pr-1 player-info active-player'})
            name = name_div.find('b').text
        except:
            name_div = panel.find('div', {'class': 'pr-1 player-info inactive-player'})
            name = name_div.find('b').text

        # Get creature count
        if i == 0:
            board = soup.select_one('div[class^="player-board"]')
        else:
            board = soup.select_one('div[class^="player-board our-side player"]')

        creatures = board.find('div', {'class': 'card-row creatures'}).find_all('div', {'class': 'card-wrapper'})
        creatures_count = len(creatures)

        # Extract amber
        amber_div = panel.find('div', {'class': 'state', 'title': 'Amber'})
        amber_value = int(amber_div.find('div', {'class': 'stat-value'}).text)

        # Extract current key cost
        key_cost_div = panel.find('div', {'class': 'state', 'title': 'Current Key Cost'})
        key_cost_value = int(key_cost_div.find('div', {'class': 'stat-value'}).text)

        # Extract keys forged
        div = panel.find('div', {'class': 'state'})
        keys = 0
        for img in div.find_all('img'):
            try:
                if img['class'][0] == 'forged-key':
                    keys += 1
            except:
                print(f"Key Error: {img}")

        board_info[i]['creatures'] = creatures_count
        board_info[i]['amber'] = amber_value
        board_info[i]['keys'] = keys
        board_info[i]['key_cost'] = key_cost_value
        names.append(name)

    return board_info, names


def get_message_info(p1_msgs, p2_msgs, p1_name, p2_name):
    p1_cards_played_dict = {}
    p2_cards_played_dict = {}
    p1_cards_played_msgs = [message for message in p1_msgs + p2_msgs if ' plays  ' in message and message[0] == p1_name]
    p1_cards_played = len(p1_cards_played_msgs)
    for msg in p1_cards_played_msgs:
        card_name = msg[2]
        if card_name in p1_cards_played_dict:
            p1_cards_played_dict[card_name] += 1
        else:
            p1_cards_played_dict[card_name] = 1
    p2_cards_played_msgs = [message for message in p1_msgs + p2_msgs if ' plays  ' in message and message[0] == p2_name]
    p2_cards_played = len(p2_cards_played_msgs)
    for msg in p2_cards_played_msgs:
        card_name = msg[2]
        if card_name in p2_cards_played_dict:
            p2_cards_played_dict[card_name] += 1
        else:
            p2_cards_played_dict[card_name] = 1
    card_info = {p1_name: {
        'cards_played': p1_cards_played,
        'individual': p1_cards_played_dict},
        p2_name: {
            'cards_played': p2_cards_played,
            'individual': p2_cards_played_dict}}

    p1_cards_discarded_dict = {}
    p2_cards_discarded_dict = {}
    p1_cards_discarded_msgs = [message for message in p1_msgs + p2_msgs if
                               ' discards  ' in message and message[0] == p1_name]
    p1_cards_discarded = len(p1_cards_discarded_msgs)
    for msg in p1_cards_discarded_msgs:
        card_name = msg[2]
        if card_name in p1_cards_discarded_dict:
            p1_cards_discarded_dict[card_name] += 1
        else:
            p1_cards_discarded_dict[card_name] = 1
    p2_cards_discarded_msgs = [message for message in p1_msgs + p2_msgs if
                               ' discards  ' in message and message[0] == p2_name]
    p2_cards_discarded = len(p2_cards_discarded_msgs)
    for msg in p2_cards_discarded_msgs:
        card_name = msg[2]
        if card_name in p2_cards_discarded_dict:
            p2_cards_discarded_dict[card_name] += 1
        else:
            p2_cards_discarded_dict[card_name] = 1
    discard_info = {p1_name: {
        'cards_discarded': p1_cards_discarded,
        'individual': p1_cards_discarded_dict},
        p2_name: {
            'cards_discarded': p2_cards_discarded,
            'individual': p2_cards_discarded_dict}}

    p1_reap_msgs = [message for message in p1_msgs + p2_msgs if 'reap with  ' in message and message[0] == p1_name]
    p2_reap_msgs = [message for message in p1_msgs + p2_msgs if 'reap with  ' in message and message[0] == p2_name]
    p1_reaps = len(p1_reap_msgs)
    p2_reaps = len(p2_reap_msgs)
    p1_reap_dict = {}
    p2_reap_dict = {}
    for msg in p1_reap_msgs:
        card_name = msg[-1]
        if card_name in p1_reap_dict:
            p1_reap_dict[card_name] += 1
        else:
            p1_reap_dict[card_name] = 1
    for msg in p2_reap_msgs:
        card_name = msg[-1]
        if card_name in p2_reap_dict:
            p2_reap_dict[card_name] += 1
        else:
            p2_reap_dict[card_name] = 1
    reap_info = {p1_name: {
        'reaps': p1_reaps,
        'individual': p1_reap_dict},
        p2_name: {
            'reaps': p2_reaps,
            'individual': p2_reap_dict}}

    p1_bonus_icon_msgs = [message for message in p1_msgs + p2_msgs if
                          ' gains an  Æmber  due to  ' in message and "'s bonus icon " in message and message[
                              0] == p1_name]
    p2_bonus_icon_msgs = [message for message in p1_msgs + p2_msgs if
                          ' gains an  Æmber  due to  ' in message and "'s bonus icon " in message and message[
                              0] == p2_name]
    p1_bonus_icons = len(p1_bonus_icon_msgs)
    p2_bonus_icons = len(p2_bonus_icon_msgs)
    p1_bonus_icon_dict = {}
    p2_bonus_icon_dict = {}
    for msg in p1_bonus_icon_msgs:
        card_name = msg[-2]
        if card_name in p1_bonus_icon_dict:
            p1_bonus_icon_dict[card_name] += 1
        else:
            p1_bonus_icon_dict[card_name] = 1
    for msg in p2_bonus_icon_msgs:
        card_name = msg[-2]
        if card_name in p2_bonus_icon_dict:
            p2_bonus_icon_dict[card_name] += 1
        else:
            p2_bonus_icon_dict[card_name] = 1
    bonus_icon_info = {p1_name: {
        'bonus_icons': p1_bonus_icons,
        'individual': p1_bonus_icon_dict},
        p2_name: {
            'bonus_icons': p2_bonus_icons,
            'individual': p2_bonus_icon_dict}}
    p1_effect_amber_msgs = [message for message in p1_msgs + p2_msgs if (' uses  ' in message) and (
                (len(message) <= 7 and message[0] == p1_name) or (len(message) > 7 and message[5] == p1_name))]
    p2_effect_amber_msgs = [message for message in p1_msgs + p2_msgs if (' uses  ' in message) and (
                (len(message) <= 7 and message[0] == p2_name) or (len(message) > 7 and message[5] == p2_name))]
    # p1_effect_amber_msgs = [message for message in p1_msgs + p2_msgs if (' uses  ' in message) and (len(message) > 5 and (message[0] == p1_name and message[5] != p2_name) or message[5] == p1_name) or (len(message <= 5 and message[0] == p1_name))]
    # p2_effect_amber_msgs = [message for message in p1_msgs + p2_msgs if (' uses  ' in message) and ((message[0] == p2_name and message[5] != p1_name) or message[5] == p2_name)]
    p1_effect_amber = 0
    p2_effect_amber = 0
    p1_effect_amber_dict = {}
    p2_effect_amber_dict = {}
    p1_steal = 0
    p2_steal = 0
    p1_steal_dict = {}
    p2_steal_dict = {}
    for i, msgs in enumerate([p1_effect_amber_msgs, p2_effect_amber_msgs]):
        for message in msgs:
            eff_number = None
            for fragment in message:
                match = re.search(r'gain\s+(\d+)\s+Æmber', fragment)
                if match:
                    eff_number = int(match.group(1))
            if eff_number is None and 'gain  ' in message:
                msg_index = message.index('gain  ') + 1
                eff_number = int(message[msg_index].strip())
            if eff_number:
                card_name = message[2]
                if len(message) > 7:
                    p_name = message[5]
                else:
                    p_name = message[0]
                if card_name == 'Allusions of Grandeur':
                    if p_name == p1_name:
                        p_name = p2_name
                    elif p_name == p2_name:
                        p_name = p1_name
                    else:
                        print(f"Name Error when switching effect amber: {p_name} not in {[p1_name, p2_name]}")
                if p_name == p1_name:
                    p1_effect_amber += eff_number
                    if card_name in p1_effect_amber_dict:
                        p1_effect_amber_dict[card_name] += eff_number
                    else:
                        p1_effect_amber_dict[card_name] = eff_number
                elif p_name == p2_name:
                    p2_effect_amber += eff_number
                    if card_name in p2_effect_amber_dict:
                        p2_effect_amber_dict[card_name] += eff_number
                    else:
                        p2_effect_amber_dict[card_name] = eff_number
                else:
                    print(f"Unknown Steal Error: {message}")
            for fragment in message:
                match = re.search(r'steal\s+(\d+)\s+Æmber', fragment)
                if match:
                    steal_number = int(match.group(1))
                    card_name = message[2]
                    if i == 0:
                        p1_steal += steal_number
                        if card_name in p1_steal_dict:
                            p1_steal_dict[card_name] += steal_number
                        else:
                            p1_steal_dict[card_name] = steal_number
                    else:
                        p2_steal += steal_number
                        if card_name in p2_steal_dict:
                            p2_steal_dict[card_name] += steal_number
                        else:
                            p2_steal_dict[card_name] = steal_number

    effect_amber_info = {p1_name: {
        'effect_amber': p1_effect_amber,
        'individual': p1_effect_amber_dict},
        p2_name: {
            'effect_amber': p2_effect_amber,
            'individual': p2_effect_amber_dict}}

    steal_info = {p1_name: {
        'steal': p1_steal,
        'individual': p1_steal_dict},
        p2_name: {
            'steal': p2_steal,
            'individual': p2_steal_dict}}

    p1_house_calls = [message[2] for message in p1_msgs + p2_msgs if
                      ' as their active house this turn ' in message and message[0] == p1_name]
    p2_house_calls = [message[2] for message in p1_msgs + p2_msgs if
                      ' as their active house this turn ' in message and message[0] == p2_name]
    house_call_info = {p1_name: p1_house_calls, p2_name: p2_house_calls}

    return card_info, discard_info, reap_info, bonus_icon_info, effect_amber_info, steal_info, house_call_info


def get_messages():
    with open('file.html', 'rb') as f:
        html_doc = f.read()
    soup = BeautifulSoup(html_doc, 'html.parser')
    messages_us = soup.find_all('div', {'class': 'message mb-1 this-player'})
    messages_them = soup.find_all('div', {'class': 'message mb-1 other-player'})
    us_frags = [
        [elem.text for elem in div.find_all('span', class_=['message-fragment', 'username user-role', 'card-link'])] for
        div in messages_us]
    them_frags = [
        [elem.text for elem in div.find_all('span', class_=['message-fragment', 'username user-role', 'card-link'])] for
        div in messages_them]
    keywords = ['Turn', 'turn', 'plays', 'Æmber', 'reap', 'as their active house', 'won ', 'discards', 'archive',
                'steal']
    our_msgs = [frag for frag in us_frags if any(keyword in word for keyword in keywords for word in frag)]
    their_msgs = [frag for frag in them_frags if any(keyword in word for keyword in keywords for word in frag)]

    return our_msgs, their_msgs, us_frags, them_frags


def play(username, password):

    login(driver, username, password)

    game_obj = None
    p1_name = None
    p2_name = None
    while True:
        fetch_html(driver)
        if check_start():
            if game_obj is None:
                p1_name, p2_name = get_player_names()
                deck_info = get_deck_info([p1_name, p2_name])
                game_obj = Game(username, p1_name, p2_name, deck_info)
                print(f"Game Started: {game_obj.p1_deck}[{game_obj.p1_name}] vs {game_obj.p2_deck}[{game_obj.p2_name}]")
            msgs_us, msgs_them, frags_us, frags_them = get_messages()
            game_obj.player_frags = frags_us
            game_obj.opponent_frags = frags_them
            if game_obj.p1_name == username:
                p1_msgs = msgs_us
                p2_msgs = msgs_them
                player_first = True
            else:
                p2_msgs = msgs_us
                p1_msgs = msgs_them
                player_first = False
            turn_change = game_obj.get_turn(p1_msgs, p2_msgs)
            if turn_change:
                print(f"Turn [{game_obj.turn}] - {game_obj.active_player}")
                board_info, names = get_board_info()
                card_info, discard_info, reap_info, bonus_icon_info, effect_amber_info, steal_info, house_call_info = get_message_info(p1_msgs, p2_msgs, p1_name, p2_name)
                game_obj.log_info(names, board_info, card_info, discard_info, reap_info, bonus_icon_info, effect_amber_info, steal_info, house_call_info)
            finish, winner = check_finish(p1_msgs, p2_msgs)
            if finish:
                board_info, names = get_board_info()
                card_info, discard_info, reap_info, bonus_icon_info, effect_amber_info, steal_info, house_call_info = get_message_info(p1_msgs, p2_msgs, p1_name, p2_name)
                game_obj.log_info(names, board_info, card_info, discard_info, reap_info, bonus_icon_info, effect_amber_info, steal_info, house_call_info)
                print(f"Game Finished")
                game_obj.save_game(winner)
                time.sleep(25)
                break
        time.sleep(1)

    return game_obj









