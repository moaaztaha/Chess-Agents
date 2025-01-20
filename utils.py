from dotenv import load_dotenv
import chess
import chess.svg
from typing_extensions import Annotated
from autogen import ConversableAgent
import streamlit as st
from autogen import register_function

load_dotenv(".secrets")
llm_config = {"model": "gpt-3.5-turbo"}


def init_board():
    return chess.Board()


board = init_board()
made_move = False


def get_legal_moves() -> Annotated[str, "A list of legal moves in UCI Format"]:
    return f"Possible moves are: {','.join([str(move) for move in board.legal_moves])}"


def check_made_move(msg):
    global made_move
    if made_move:
        made_move = False
        return True
    else:
        return False


def make_move(
    move: Annotated[str, "A move in UCI format."]
) -> Annotated[str, "Result of the move."]:
    move = chess.Move.from_uci(move)
    board.push_uci(str(move))
    global made_move
    made_move = True

    # save the board svg.
    svg_output = chess.svg.board(
        board,
        arrows=[(move.from_square, move.to_square)],
        fill={move.from_square: "gray"},
        size=400,
    )

    with open("chessboard.svg", "w") as f:
        f.write(svg_output)
        print("Updated board image")

    # Get the piece name.
    piece = board.piece_at(move.to_square)
    piece_symbol = piece.unicode_symbol()
    piece_name = (
        chess.piece_name(piece.piece_type).capitalize()
        if piece_symbol.isupper()
        else chess.piece_name(piece.piece_type)
    )
    return (
        f"Moved {piece_name} ({piece_symbol}) from "
        f"{chess.SQUARE_NAMES[move.from_square]} to "
        f"{chess.SQUARE_NAMES[move.to_square]}."
    )


def create_players(key: str):
    llm_config["api_key"] = key


    # Player white agent
    player_white = ConversableAgent(
        name="player_white",
        system_message="You are a chess player and you play as white. "
        "First call get_legal_moves(), to get a list of legal moves. "
        "Then call make_move(move) to make a move.",
        llm_config=llm_config,
    )

    # Player black agent
    player_black = ConversableAgent(
        name="player_black",
        system_message="You are a chess player and you play as black. "
        "First call get_legal_moves(), to get a list of legal moves. "
        "Then call make_move(move) to make a move.",
        llm_config=llm_config,
    )

    board_proxy = ConversableAgent(
        name="board_proxy",
        llm_config=False,
        is_termination_msg=check_made_move,
        default_auto_reply="Please make a move.",
        human_input_mode="NEVER",
    )

    for caller in [player_white, player_black]:
        register_function(
            get_legal_moves,
            caller=caller,
            executor=board_proxy,
            name="get_legal_moves",
            description="Get legal moves.",
        )

        register_function(
            make_move,
            caller=caller,
            executor=board_proxy,
            name="make_move",
            description="Call this tool to make a move.",
        )

    player_white.register_nested_chats(
        trigger=player_black,
        chat_queue=[
            {
                "sender": board_proxy,
                "recipient": player_white,
                "summary_method": "last_msg",
                "silent": True,
            }
        ],
    )

    player_black.register_nested_chats(
        trigger=player_white,
        chat_queue=[
            {
                "sender": board_proxy,
                "recipient": player_black,
                "summary_method": "last_msg",
                "silent": True,
            }
        ],
    )
    return player_white, player_black, board_proxy
