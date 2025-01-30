import streamlit as st
from agent.llm_rag import ChatLLM

chat_llm = ChatLLM()

def render_chat_window():
    """Erstellt ein schwebendes Chat-Fenster als Popover in der unteren rechten Ecke."""

    # ✅ **Popover für den Chat**
    with st.popover("💬 AI Chat", icon=":material/chat:", help="Chat mit AI öffnen"):
        st.markdown("### 🤖 AI Chat")
        
        # ✅ **Chat-Verlauf anzeigen**
        for speaker, message in st.session_state.conversation:
            if speaker == "You":
                st.markdown(f'<p><strong>You:</strong> {message}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color:green;"><strong>Bot:</strong> {message}</p>', unsafe_allow_html=True)

        # ✅ **Falls ein Diagramm vorhanden ist, rendern**
        if hasattr(chat_llm, "figures") and chat_llm.figures:
            for fig in chat_llm.figures:
                st.pyplot(fig)
            chat_llm.figures.clear()  # Nach der Anzeige leeren, um doppeltes Rendern zu vermeiden
            
        # ✅ **Chat-Eingabe**
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Nachricht eingeben:", key="chat_input")
            submitted = st.form_submit_button("Senden")

            if submitted and user_input:
                response = chat_llm.get_response(user_input)
                st.session_state.conversation.append(("You", user_input))
                st.session_state.conversation.append(("Bot", response))
                st.rerun()

