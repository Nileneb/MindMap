from streamlit import session_state as st





def logout():
    st.header("Request 2")
    st.write(f"You are logged in as {st.session_state.role}.")
    st.session_state.role = None
    st.rerun()
    role = "Responder"  # Define the role variable
    default = (role == "Responder")