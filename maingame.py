import sys

from utils import Board, LibC
from players.player import RandomPlayer, EdaxPlayer

def playGame(players):
    libc = LibC()
    board = Board(0,0)
    libc.board_init(board)
    libc.board_print(board)
    moves = libc.get_moves(board.player, board.opponent)
    print('{0:x}'.format(moves))


    # main loop
    current_player = 0
    while not libc.board_is_game_over(board):
        # get move from current player, could be a pass
        move = players[current_player].get_move(board)

        # update board, not using OOP bc edax is in C
        if move == -1:
            libc.board_swap_players(board)
            print("pass", file=sys.stderr)
        else:
            libc.board_update(board, move, board) # this implicitly swaps the player, might not be wanted

        # update current_player
        current_player = 1 - current_player
        libc.board_print(board, player_color=current_player)
        print(current_player, file=sys.stderr)

        # libc.board_swap_players(board)
        # time.sleep(1)

    # These should be put to analyze and become optional
    cnts = [0,0]
    player_cnt = libc.bit_count(board.player)
    opponent_cnt = libc.bit_count(board.opponent)
    cnts[current_player] = player_cnt
    cnts[1-current_player] = opponent_cnt
    winner = 0
    if cnts[winner] == cnts[1-winner]:
        print("draw!!")
        return cnts
    if cnts[winner] < cnts[1-winner]:
        winner = 1-winner
    print(players[winner].name + " wins!!")
    return cnts, winner

if __name__ == '__main__':
    players = [EdaxPlayer("edax player zx"), RandomPlayer("rand player fe")]
    win_cnt = 0
    total_games = 10
    for i in range(total_games):
        players = [EdaxPlayer("edax player zx"), RandomPlayer("rand player fe")]
        _, winner = playGame(players)
        if winner == 0:
            win_cnt += 1
    print('{} wins {}/{} games!'.format(players[0].name, win_cnt, total_games))

