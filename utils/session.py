import streamlit as st


def initialize_session():

    defaults = {
        
        "mode": "Practice",

        "practice_date": None,

        "drill": "",

        "opponent": "",

        "match_set": 1,

        "rotation": "R1",

        "left_setter": None,

        "right_setter": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value