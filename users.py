import pandas as pd
import database
import streamlit_authenticator as stauth
import streamlit_authenticator.utilities.hasher as hasher


def new_user(username, password, email, tco_name):
    if len(username) < 3:
        return "Error", "Username must be at least 3 characters"
    if len(password) < 5:
        return "Error", "Password must be at least 5 characters"

    user_df = database.pull('Users')
    if email in user_df['Email'].values:
        print("Email exists")
        return "Error", f"Account already registered for {email}"

    if username in user_df['Username'].values:
        print("Username exists")
        return "Error", "Username already exists"

    new_user_data = pd.DataFrame(columns=['Username', 'Password', 'Email', 'TCO Name', 'TCO Pass'])
    new_user_data.loc[len(new_user_data)] = [username, password, email, tco_name, '']
    database.post('Users', new_user_data, user_df)

    return "Success", "Account successfully registered"


def delete_user(username):
    user_db = database.pull('Users')
    if username not in user_db['Username'].values:
        return "Error", "Account not found"
    else:
        user_db = user_db[user_db['Username'] != username]
        database.post('Users', df=user_db)
        return "Success", f"Account deleted for {username}"


def get_authenticator():
    user_db = database.pull('Users')
    user_dict = {'usernames': {}}
    for i, row in user_db.iterrows():
        user_dict['usernames'][row['Username']] = {
            'email': row['Email'],
            'name': row['TCO Name'],
            'password': row['Password']
        }

    authenticator = stauth.Authenticate(user_dict, 'keyforge_tracker', 'SpdfdgAEO1QTCF7lYXTO265VuBXlSpMm')
    return authenticator


def check_pw(username, password):
    user_data = database.pull('Users')
    correct_pw = user_data.loc[user_data['Username'] == username, 'Password'].iat[0]
    if hasher.Hasher([password]).check_pw(password, correct_pw):
        return True
    else:
        return False


