import streamlit as st

from menu import menu_with_redirect

menu_with_redirect()

st.title("This page is available to all users")
st.markdown(f"You are currently logged with the role of {st.session_state.role}.")

def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("frontend/login.py", label="Switch accounts")
    st.sidebar.page_link("frontend/user.py", label="Your profile")
    if st.session_state.role in ["admin", "super-admin"]:
        st.sidebar.page_link("admin/admin.py", label="Manage users")
        st.sidebar.page_link(
            "admin/admin2.py",
            label="Manage admin access",
            disabled=st.session_state.role != "super-admin",
        )


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("frontend/login.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("frontend/login.py")
    menu()
