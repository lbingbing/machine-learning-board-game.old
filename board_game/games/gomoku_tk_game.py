import tkinter as tk

from .blackwhite_tk_game import BlackWhiteApp
from board_game.states.gomoku_state import GomokuState
from board_game.players import player

class GomokuApp(BlackWhiteApp):

    def init_state(self):
        board_shape = (9, 9)
        target = 5
        self.state = GomokuState(board_shape = board_shape, target = target)

    def create_player(self, state, player_type, player_id):
        from board_game.players.gomoku_player import create_player
        return create_player(state, player_type, player_id)

def main():
    player_types = player.parse_cmd_player_types()
    app = GomokuApp(player_types)
    app.mainloop()

