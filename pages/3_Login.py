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
    pattern = r"^[A-Za-z0-9 ]+$"
    return 1 <= len(name_entry) <= 100 and bool(re.match(pattern, name_entry))

Validator.validate_name = custom_validate_name

authenticator = users.get_authenticator()

if 'authentication_status' not in st.session_state or st.session_state.authentication_status is False or st.session_state.authentication_status is None:
    if 'login_type' not in st.session_state:
        st.session_state.login_type = 'normal'
    name, auth_status, username = authenticator.login(location="main")
    if st.session_state.authentication_status is False:
        st.error("Incorrect username/password")
    if st.session_state.login_type == 'special':
        st.session_state.login_type = 'normal'
        st.session_state.auto_login_check = True
        st.switch_page("Home.py")
    reg_username, reg_email, reg_name = None, None, None
    if authenticator:
        try:
            reg_email, reg_username, reg_name, = authenticator.register_user(pre_authorization=False)
        except RegisterError as e:
            st.error(f"{e}")
        try:
            user_dict = authenticator.authentication_controller.authentication_model.credentials['usernames']
        except:
            user_dict = None
        if reg_username:
            if user_dict:
                register_status, message = users.new_user(reg_username, user_dict[reg_username]['password'], reg_email, reg_name)

                if register_status == "Error":
                    st.error(message)
                else:
                    st.success(message)
    else:
        st.write("No Authenticator")
else:
    st.switch_page('Home.py')