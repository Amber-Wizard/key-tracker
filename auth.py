from streamlit_authenticator.utilities.validator import Validator

import users


# Monkey patch to override name validation
def custom_validate_name(self, name_entry: str) -> bool:
    pattern = r"^[A-Za-z0-9_ ]+$"
    return 1 <= len(name_entry) <= 100 and bool(re.match(pattern, name_entry))

Validator.validate_name = custom_validate_name

authenticator, name_conversion_dict = users.get_authenticator()


