import copy
import random
import subprocess
import utils
import sys
import re

'''
    board - struct of two uint64, player and opponent
    player - uint64 rep of a gameboard where '1' represents a piece for the current player
    opponent - uint64 rep of a gameboard where '1' represents a piece for the next player
    moves - uint64 rep of a gameboard where each '1' represents a valid spot for next move for the current player. 
            Least significant bit is A1, then B1, ... to H8
    move - 0 indexed integer representing the square to pick the move. Maingame added pass implementation as -1.
'''

'''
    coord - eg. 'd3', 'a8'
'''
def coordToMove(coord):
    coord = coord.lower()
    if coord == "ps":
        return -1
    return (ord(coord[0]) - ord('a')) + 8*(int(coord[1])-1)

'''
    Test case:
    print('{}'.format(coordToMove('a1')))
    print(moveToCoord(0)) <- replace the int with result from above
'''
def moveToCoord(move):
    res = str(chr(ord('a')+(move%8)) + str(1 + (move//8)))
    return res

def get_moves(player, opponent):
    mask = opponent & 0x7E7E7E7E7E7E7E7E
    a1 = get_some_moves(player, mask, 1)
    a2 = get_some_moves(player, opponent, 8)
    a3 = get_some_moves(player, mask, 7)
    a4 = get_some_moves(player, mask, 9)
    empty_bb = (player | opponent) ^ 0xFFFFFFFFFFFFFFFF
    return (a1 | a2 | a3 | a4) & empty_bb

def get_some_moves(bb, mask, direction):
    # 1-stage Parallel Prefix (intermediate between kogge stone & sequential)
    # 6 << + 6 >> + 7 | + 10 &
    direction2 = direction + direction
    flip_l = mask & (bb << direction)
    flip_r = mask & (bb >> direction)
    flip_l |= mask & (flip_l << direction)
    flip_r |= mask & (flip_r >> direction)
    mask_l = mask & (mask << direction)
    mask_r = mask & (mask >> direction)
    flip_l |= mask_l & (flip_l << direction2)
    flip_r |= mask_r & (flip_r >> direction2)
    flip_l |= mask_l & (flip_l << direction2)
    flip_r |= mask_r & (flip_r >> direction2)
    return (flip_l << direction) | (flip_r >> direction)

def obf_to_bitboards(s):
    assert re.fullmatch(r"[-OX]{64}\s[OX];", s) is not None
    player = 0
    opponent = 0
    for i in range(64):
        if s[i] == s[65]:
            player += 1 << i
        elif s[i] != "-":
            opponent += 1 << i
    return (player, opponent)

def print_obf(obf: str) -> None:
    player, opponent = obf_to_bitboards(obf)
    bb_moves = get_moves(player, opponent)
    if bb_moves == 0:
        assert get_moves(opponent, player) == 0
    assert ((player | opponent) & bb_moves) == 0
    print("  A B C D E F G H")
    for i in range(8):
        line = f"{i+1} "
        for j in range(8):
            line += obf[i * 8 + j] if (bb_moves & (1 << (i * 8 + j))) == 0 else "."
            line += " "
        suffix = ""
        if i == 1:
            suffix = f" {obf[65]} to move" if bb_moves > 0 else " game is end."
        elif i == 3:
            suffix = f" O: discs = {str(obf[:64].count('O')).rjust(2)}"
        elif i == 4:
            suffix = f" X: discs = {str(obf[:64].count('X')).rjust(2)}"
        elif i == 5:
            suffix = f"  empties = {str(obf[:64].count('-')).rjust(2)}"
        print(line + str(i + 1) + suffix)
    print("  A B C D E F G H")

class EdaxPlayer:

    '''
        Options (see edax doc for ref):
        -l: level
    '''
    def __init__(self, name, *args):
        self.libc = utils.LibC()
        self.name = name
        self.process = None # Will be initiated during the first call to get_move, depending on the color of this player
        self.first_move = False
        self.board = utils.Board(0,0)
        self.libc.board_init(self.board)
        self.last_edax_move = None
        self.options = list(args)
        if name == "edax player fe":
            self.options = ['-l', '30', '-game-file', 'gamefile.txt', '-search-log-file', 'searchlog.txt']
        if name == "edax player zx":
            self.options = ['-l', '8']

    def read_edax_move(self):
        edax_move = -1
        line = self.process.stdout.readline()
        cnt = 0
        edax_played = False
        while line:
            cnt += 1
            line_string = line.decode('utf-8')
            # print(cnt, '\t', line_string, end='')
            # Edax will hang up waiting for user input after 12 lines of standard output
            if "Edax plays" in line_string:
                edax_move_coords = line_string.split(" ")[2][:-1]
                edax_move = coordToMove(edax_move_coords)
                self.last_edax_move = edax_move
                # print("edax_move: ", edax_move, file=sys.stderr)
                cnt = 0
                edax_played = True
            if cnt == 12 and edax_played:
                break
            line = self.process.stdout.readline()
        return edax_move

    def send_opponent_move(self, opponent_move):
        if opponent_move == -1:
            opponent_move_coords = "ps"
        else:
            opponent_move_coords = moveToCoord(opponent_move)
        # print("opponent move coords:", opponent_move_coords)
        self.process.stdin.write(opponent_move_coords.encode('utf-8') + b'\n')
        self.process.stdin.flush()

    def get_move(self, board):
        if self.process is None:
            if board == self.board:
                self.process = subprocess.Popen(['./bin/mEdax', '-mode', '1'] + self.options, stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT)
                self.first_move = True
            else:
                self.process = subprocess.Popen(['./bin/mEdax', '-mode', '0'] + self.options, stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT)
        if self.first_move:
            edax_move = self.read_edax_move()
            self.first_move = False
        else:
            # compute the other player move and send it to edax
            opponent_move = -1
            combined_moves = (board.opponent|board.player) - (self.board.opponent|self.board.player)
            # print("opponent move: {0:x}".format((board.opponent|board.player) - (
            #         self.board.opponent|self.board.player)))
            moves_list = []
            for i in range(64):
                if (combined_moves >> i) % 2 == 1:
                    moves_list.append(i)
            for move in moves_list:
                if move == self.last_edax_move:
                    continue
                opponent_move = move

            # send the move to edax engine
            self.send_opponent_move(opponent_move)

            # read edax move
            edax_move = self.read_edax_move()
        self.board = copy.deepcopy(board)
        return edax_move

if __name__ == '__main__':
    # print('{}'.format(coordToMove('a1')))
    # print(moveToCoord(0))
    print_obf("------------O------OOX-----XOX----XXOO----XO-O------------------ X;")




