import sys

from utils import Board, LibC
from players.player import RandomPlayer
from players.edax_player import EdaxPlayer
import time
from multiprocessing import Process, Array

def playGame(players, wincount):
    libc = LibC()
    board = Board(0,0)
    libc.board_init(board)
    libc.board_print(board)
    moves = libc.get_moves(board.player, board.opponent)
    tmp = []
    for player, name in players:
        tmp.append(globals()[player](name))
    players = tmp

    # main loop
    current_player = 0
    while not libc.board_is_game_over(board):
        # get move from current player, could be a pass
        move = players[current_player].get_move(board)

        # update board, not using OOP bc edax is in C
        if move == -1:
            libc.board_swap_players(board)
        else:
            libc.board_update(board, move, board) # this implicitly swaps the player, might not be wanted

        # update current_player
        current_player = 1 - current_player
        libc.board_print(board, player_color=current_player)

    # These should be put to analyze and become optional
    cnts = [0,0]
    player_cnt = libc.bit_count(board.player)
    opponent_cnt = libc.bit_count(board.opponent)
    cnts[current_player] = player_cnt
    cnts[1-current_player] = opponent_cnt
    winner = 0
    if cnts[winner] == cnts[1-winner]:
        wincount[2] += 1
        print("draw!!")
        return cnts, 2
    if cnts[winner] < cnts[1-winner]:
        winner = 1-winner
    print(players[winner].name + " wins!!")
    wincount[winner] += 1
    return cnts, winner

if __name__ == '__main__':
    start = time.time()
    win_cnt = Array('i', [0,0,0])
    total_games = 15
    # Pass players in tuples ({class_name}, [{initialization_vars}]) so that they can be pickled
    players = [("EdaxPlayer", "edax player fe"), ("EdaxPlayer", "edax player zx")]

    processes = []
    for i in range(total_games):
        p = Process(target=playGame, args=[players, win_cnt])
        processes.append(p)
        p.start()
        # _, winner = playGame(players)
        # win_cnt[winner] += 1
    for p in processes:
        p.join()

    print('{} wins {}/{} games!'.format(players[0][1], win_cnt[0], total_games))
    print('{} wins {}/{} games!'.format(players[1][1], win_cnt[1], total_games))
    print('Draw {}/{} games!'.format(win_cnt[2], total_games))
    end = time.time()
    print(f"Time: {end - start:.6f} seconds")


