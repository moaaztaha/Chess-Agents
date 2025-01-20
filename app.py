import streamlit as st
from utils import create_players
from utils import board
from utils import made_move
import os

st.title("Chess AI Agents")

with st.sidebar:
    st.header("Configs")
    key = st.sidebar.text_input("ChatGPT Key")

    st.text("Please config you Agentic Players")
    n_turns = st.number_input("Number of Turns", min_value=1, max_value=5)
    start = st.button("Start the game")

if "board" not in st.session_state:
    st.session_state.board = "chessboard_default.svg"

board_image = st.empty()
board_image.image(st.session_state.board, width=400)


def player_black_move():
    with st.chat_message("user"):
        chat_result = player_white.initiate_chat(
            player_black,
            message="Let's play chess! Your move.",
            max_turns=1,
        )

        for message in chat_result.chat_history[1:]:
            st.markdown(message["content"])


def player_white_move():
    with st.chat_message("assistant"):
        chat_result = player_black.initiate_chat(
            player_white,
            message="Let's play chess! Your move.",
            max_turns=1,
        )

        for message in chat_result.chat_history[1:]:
            st.markdown(message["content"])


if key:
    # Creating players
    player_white, player_black, board_proxy = create_players(key)

    if start:
        for i in range(n_turns):
            player_white_move()
            board_image.image("chessboard.svg", width=400)

            player_black_move()
            board_image.image("chessboard.svg", width=400)
else:
    st.error("Please input a valid ChatGPT API key!!")
