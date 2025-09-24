import streamlit as st
import re
from streamlit_authenticator.utilities.validator import Validator
from streamlit_authenticator.utilities.exceptions import RegisterError

import users

try:
    st.set_page_config(
        page_title="KeyTracker",
        page_icon="🔑",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except:
    pass


# Monkey patch to override name validation
def custom_validate_name(self, name_entry: str) -> bool:
    pattern = r"^[A-Za-z0-9_ ]+$"
    return 1 <= len(name_entry) <= 25 and bool(re.match(pattern, name_entry))

Validator.validate_name = custom_validate_name

authenticator, name_conversion_dict = users.get_authenticator()

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    tabs = st.tabs(['Login', 'Register'])
    with tabs[0]:
        if 'login_type' not in st.session_state:
            st.session_state.login_type = 'normal'
        login_results = authenticator.login(location="main")
        if login_results:
            name, auth_status, username = login_results
        if st.session_state.authentication_status is False:
            st.error("Incorrect username/password")
        if st.session_state.login_type == 'special' or st.session_state.authentication_status:
            st.session_state.login_type = 'normal'
            st.session_state.auto_login_check = True
            st.switch_page("Home.py")
    with tabs[1]:
        reg_username, reg_email, reg_name = None, None, None
        if authenticator:
            try:
                reg_email, reg_username, reg_name = authenticator.register_user(fields={'First name': 'TCO Username (Required)', 'Last name': 'Discord Username (Optional)'}, password_hint=False, captcha=False)
            except RegisterError as e:
                st.error(f"{e}")
            try:
                user_dict = authenticator.authentication_controller.authentication_model.credentials['usernames']
            except:
                user_dict = None
            if not reg_username:
                st.error('No username found')
            elif not user_dict:
                st.error('No user info found')
            else:
                name_parts = reg_name.split(' ')
                if len(name_parts) > 2:
                    st.error('Error: Please do not include spaces in your TCO or Discord username. Email logosresearchinstitute@gmail.com for more help')
                else:
                    if len(name_parts) == 1:
                        tco_name = reg_name
                        discord_name = None
                    elif len(name_parts) == 2:
                        tco_name = name_parts[0]
                        discord_name = name_parts[1]

                    register_status, message = users.new_user(reg_username, user_dict[reg_username]['password'], reg_email, tco_name, discord_name)

                    if register_status == "Error":
                        st.error(message)
                    else:
                        st.success(message)
        else:
            st.write("No Authenticator")
else:
    st.switch_page('Home.py')
