import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import streamlit_authenticator.utilities.hasher as hasher

import database


def new_user(username, password, email, tco_name):
    if len(username) < 3:
        return "Error", "Username must be at least 3 characters"
    if len(password) < 5:
        return "Error", "Password must be at least 5 characters"

    users = database.get_all_users()
    user_df = database.to_dataframe(users)
    if email in user_df['email'].values:
        return "Error", f"Account already registered for {email}"

    if username in user_df['username'].values:
        return "Error", "Username already exists"

    if tco_name in user_df['tco_name'].values:
        return "Error", "TCO name already exists"

    if 'aliases' in user_df:
        if user_df['aliases'].apply(lambda lst: isinstance(lst, list) and tco_name in lst).any():
            return "Error", "TCO name already exists"

    database.add_user(username, password, email, tco_name)

    return "Success", "Account successfully registered"


def get_authenticator():
    user_db = database.get_all_users()
    user_dict = {'usernames': {}}
    name_conversion_dict = {}
    for user in user_db:
        user_dict['usernames'][user['username']] = {
            'email': user['email'],
            'name': user['tco_name'],
            'password': user['password']
        }

        name_conversion_dict[user['tco_name']] = user['tco_name']
        if 'aliases' in user:
            for alias in user['aliases']:
                name_conversion_dict[alias] = user['tco_name']

    auth = stauth.Authenticate(user_dict, st.secrets['mongo']['username'], st.secrets['mongo']['password'])
    return auth, name_conversion_dict


