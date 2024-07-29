from datetime import datetime as dt
import os
import pandas as pd
import uuid

import database


def generate_game_id():
    return str(uuid.uuid4())


class Game:
    def __init__(self, player_name, p1_name, p2_name, deck_info):

        self.player_name = player_name
        self.p1_name = p1_name
        self.p2_name = p2_name
        try:
            self.p1_deck = deck_info[p1_name]['deck-name']
            self.p2_deck = deck_info[p2_name]['deck-name']
            self.p1_deck_link = deck_info[p1_name]['deck-link']
            self.p2_deck_link = deck_info[p2_name]['deck-link']
        except:
            print(f"Deck Error: {deck_info}")
            self.p1_deck = None
            self.p2_deck = None
            self.p1_deck_link = None
            self.p2_deck_link = None

        self.player_frags = None
        self.opponent_frags = None

        self.turn = 0
        self.active_player = None
        self.game_log = {p: {
            'cards_played': [],
            'individual_cards_played': [],
            'cards_discarded': [],
            'individual_cards_discarded': [],
            'amber_icons': [],
            'individual_amber_icons': [],
            'amber_effect': [],
            'individual_amber_effect': [],
            'amber_reaped': [],
            'individual_amber_reaped': [],
            'steal': [],
            'individual_steal': [],
            'amber': [],
            'keys': [],
            'creatures': [],
            'key_cost': [],
            'house_calls': [],
        } for p in deck_info.keys()}

    def get_turn(self, p1_msgs, p2_msgs):
        old_turn = f"{self.turn}-{self.active_player}"
        turns = [msg for msg in p1_msgs + p2_msgs if any(f.startswith('Turn ') for f in msg)]
        print(turns)
        p1_turns = [int(msg[0][5:-4]) for msg in turns if msg[1] == self.p1_name]
        p2_turns = [int(msg[0][5:-4]) for msg in turns if msg[1] == self.p2_name]
        if not turns:
            pass
        else:
            if max(p1_turns, default=0) > max(p2_turns, default=0):
                self.active_player = self.p1_name
                self.turn = max(p1_turns, default=0)
            else:
                self.active_player = self.p2_name
                self.turn = max(p2_turns, default=0)
        if old_turn != f"{self.turn}-{self.active_player}":
            turn_change = True
        else:
            turn_change = False
        return turn_change

    def get_log_turn(self):
        if self.active_player == self.p1_name:
            log_turn = (self.turn - 1) * 2
        else:
            log_turn = self.turn * 2 - 1
        log_turn += 1
        return log_turn

    def log_info(self, names, board_info, card_info, discard_info, reap_info, bonus_icon_info, effect_amber_info, steal_info, house_call_info):
        log_turn = self.get_log_turn()
        if log_turn > 0:
            for name in names:
                self.game_log[name]['cards_played'].append(card_info[name]['cards_played'])
                self.game_log[name]['individual_cards_played'].append(card_info[name]['individual'])
                self.game_log[name]['cards_discarded'].append(discard_info[name]['cards_discarded'])
                self.game_log[name]['individual_cards_discarded'].append(discard_info[name]['individual'])
                self.game_log[name]['amber_reaped'].append(reap_info[name]['reaps'])
                self.game_log[name]['individual_amber_reaped'].append(reap_info[name]['individual'])
                self.game_log[name]['amber_icons'].append(bonus_icon_info[name]['bonus_icons'])
                self.game_log[name]['individual_amber_icons'].append(bonus_icon_info[name]['individual'])
                self.game_log[name]['amber_effect'].append(effect_amber_info[name]['effect_amber'])
                self.game_log[name]['individual_amber_effect'].append(effect_amber_info[name]['individual'])
                self.game_log[name]['steal'].append(steal_info[name]['steal'])
                self.game_log[name]['individual_steal'].append(steal_info[name]['individual'])
                self.game_log[name]['house_calls'] = house_call_info[name]
            for i, name in enumerate(names):
                player_board_info = board_info[i]
                for k, v in player_board_info.items():
                    data_ref = self.game_log[name][k]
                    data_ref.append(v)

        print(self.game_log)

    def save_game(self, winner):
        formatted_date = dt.today().strftime('%Y-%m-%d %H:%M')

        if self.p1_name == self.player_name:
            opponent = self.p2_name
            op_deck = self.p2_deck
            op_deck_link = self.p2_deck_link
            deck = self.p1_deck
            deck_link = self.p1_deck_link
        else:
            opponent = self.p1_name
            op_deck = self.p1_deck
            op_deck_link = self.p1_deck_link
            deck = self.p2_deck
            deck_link = self.p2_deck_link

        data = {
            'ID': [generate_game_id()],
            'Date': [formatted_date],
            'Player': [self.player_name],
            'Opponent': [opponent],
            'Deck': [deck],
            'Deck Link': [deck_link],
            'Opponent Deck': [op_deck],
            'Opponent Deck Link': [op_deck_link],
            'Starting Player': [self.p1_name],
            'Winner': [winner],
            'Game Log': [self.game_log],
            'Player Frags': [self.player_frags],
            'Opponent Frags': [self.opponent_frags],
        }
        database.log_game(data)



