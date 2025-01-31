import streamlit as st
from main import ROLES
from st_pages import add_page_title, get_nav_from_toml
from menu import menu
from streamlit_login_auth_ui.widgets import __login__
import courier
from courier import trycourier
st.header("Log in")
st.write(f"You are logged in as {st.session_state.role}.")
__login__obj = __login__(auth_token="dk_prod_R5VXWAD5CHMGMGJMPBVZEN4G9V1H",
                             company_name="Linn.Games",
                             width=200, height=250,
                             logout_button_name="Logout", hide_menu_bool=False,
                             hide_footer_bool=False,
                             lottieurls = ["https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json"])
                               
LOGGED_IN = __login__obj.build_login_ui()
if LOGGED_IN == True:
    st.markown("Your Streamlit Application Begins here!")


# Retrieve the role from Session State to initialize the widget
st.session_state._role = st.session_state.role

def set_role():
    # Callback function to save the role selection to Session State
    st.session_state.role = st.session_state._role


# Selectbox to choose role
st.selectbox(
    "Select your role:",
    [None, "user", "admin", "super-admin"],
    key="_role",
    on_change=set_role,
)
menu() # Render the dynamic menu!

