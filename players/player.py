import copy
import random
import subprocess
import utils
import sys

'''
    board - struct of two uint64, player and opponent
    player - uint64 rep of a gameboard where '1' represents a piece for the current player
    opponent - uint64 rep of a gameboard where '1' represents a piece for the next player
    moves - uint64 rep of a gameboard where each '1' represents a valid spot for next move for the current player. 
            Least significant bit is A1, then B1, ... to H8
    move - 0 indexed integer representing the square to pick the move. Maingame added pass implementation as -1.
'''
# class Player:
#     # Given a board(player, opponent), return a move
#     def __init__(self, name, get_move):
#
#         self.name = name
#         # func(board) -> move(bitmask)
#         self.get_move = get_move #decor this by pass checker

# implement a random player
class RandomPlayer:
    def __init__(self, name):
        self.libc = utils.LibC()
        self.name = name
        # func(board) -> move(bitmask)
    def get_move(self, board):
        moves = self.libc.get_moves(board.player, board.opponent)
        moves_list = []
        for i in range(64):
            if (moves >> i) % 2 == 1:
                moves_list.append(i)
        move_cnt = len(moves_list)
        if move_cnt == 0:
            return -1
        move_choice = moves_list[random.randint(0, move_cnt-1)]
        # print the move just before board update to debug
        # print("move: {}".format(move_choice), file=sys.stderr)
        return move_choice




