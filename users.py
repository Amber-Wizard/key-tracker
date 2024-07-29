import pandas as pd
import streamlit_authenticator as stauth
import streamlit_authenticator.utilities.hasher as hasher

import database


def new_user(username, password, email, tco_name):
    if len(username) < 3:
        return "Error", "Username must be at least 3 characters"
    if len(password) < 5:
        return "Error", "Password must be at least 5 characters"

    user_df = database.get_all_users()('Users')
    if email in user_df['Email'].values:
        print("Email exists")
        return "Error", f"Account already registered for {email}"

    if username in user_df['Username'].values:
        print("Username exists")
        return "Error", "Username already exists"

    database.add_user(username, password, email, tco_name)

    return "Success", "Account successfully registered"


def get_authenticator():
    user_db = database.get_all_users()
    user_dict = {'usernames': {}}
    for user in user_db:
        user_dict['usernames'][user['username']] = {
            'email': user['email'],
            'name': user['tco_name'],
            'password': user['password']
        }

    authenticator = stauth.Authenticate(user_dict, 'keyforge_tracker', 'SpdfdgAEO1QTCF7lYXTO265VuBXlSpMm')
    return authenticator


def check_pw(username, password):
    user_data = database.get_user(username)
    correct_pw = user_data['password']
    if hasher.Hasher([password]).check_pw(password, correct_pw):
        return True
    else:
        return False


