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

def obf_to_bitboards(s):
    assert re.fullmatch(r"[-OX]{64}\s[OX];", s) is not None
    player = 0
    opponent = 0
    for i in range(64):
        if s[i] == s[65]:
            player += 1 << i
        elif s[i] != "-":
            opponent += 1 << i
    return utils.Board(player, opponent)

def bitboards_to_obf(player, opponent, player_is_black=True):
    assert (player & opponent) == 0
    answer = ""
    for i in range(64):
        if (player & (1 << i)) != 0:
            answer += "X" if player_is_black else "O"
        elif (opponent & (1 << i)) != 0:
            answer += "O" if player_is_black else "X"
        else:
            answer += "-"
    return answer + (" X;" if player_is_black else " O;")

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

def print_obf(obf: str) -> None:
    board = obf_to_bitboards(obf)
    player, opponent = board.player, board.opponent
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

def scorestr2range(s):
    m = re.fullmatch(r"^[><]?[-+][0-9]{2}$", s)
    assert m is not None
    if s[0] == "<":
        return (-64, int(s[1:]))
    if s[0] == ">":
        return (int(s[1:]), 64)
    score = int(s)
    return (score, score)

def compute_one_verbose2_problem(lines):

    lines.reverse()

    for x in lines:
        print(x)
        m = re.search(
            r"([0-9]+)\s+([><]?[-+][0-9]{2})\s+([0-9.:]+)\s+([0-9]+)\s+([0-9]*)\s+(([a-hA-H][1-8]\s?)+)",
            x,
        )
        if m is not None:
            depth = int(m.group(1))
            score_range = scorestr2range(m.group(2))
            nodes = int(m.group(4))
            principal_variation = m.group(6).lower().strip().split(" ")
            return {
                "perfect": True,
                "depth": depth,
                "accuracy": 100,
                "nodes": nodes,
                "score_lowerbound": score_range[0],
                "score_upperbound": score_range[1],
                "principal_variation": principal_variation,
            }

        m = re.search(
            r"([0-9]+)@([0-9]+)%\s+([-+][0-9]{2})\s+([0-9.:]+)\s+([0-9]+)\s+([0-9]*)\s+(([a-hA-H][1-8]\s?)+)",
            x,
        )
        if m is not None:
            depth = int(m.group(1))
            accuracy = int(m.group(2))
            score = int(m.group(3))
            nodes = int(m.group(5))
            principal_variation = m.group(7).lower().strip().split(" ")
            assert accuracy < 100
            return {
                "perfect": False,
                "depth": depth,
                "accuracy": accuracy,
                "nodes": nodes,
                "score_lowerbound": score,
                "score_upperbound": score,
                "principal_variation": principal_variation,
            }

    return None

class EdaxPlayerSolve:

    '''
        Options (see edax doc for ref):
        -l: level
    '''
    def __init__(self, name, *args):
        self.libc = utils.LibC()
        self.name = name
        # self.process = None # Will be initiated during the first call to get_move, depending on the color of this player
        # self.first_move = False
        # self.board = utils.Board(0,0)
        # self.libc.board_init(self.board)
        # self.last_edax_move = None
        self.options = list(args)
        # if name == "edax player fe":
        #     self.options = ['-l', '11', '-game-file', 'gamefile.txt', '-search-log-file', 'searchlog.txt']
        # if name == "edax player zx":
        #     self.options = ['-l', '8']

    def get_move(self, board):
        problem = bitboards_to_obf(board.player, board.opponent)
        with open("tmp_obf_file", "w") as f:
            f.write(problem)
            f.close
        proc = subprocess.Popen(
            ['./bin/mEdax', '-solve', "tmp_obf_file"] + self.options,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        result_stdout = []
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if line:
                result_stdout.append(line.rstrip())

        analyze = compute_one_verbose2_problem(result_stdout)
        print(analyze)
        return coordToMove(analyze["principal_variation"][0])


if __name__ == '__main__':
    # print('{}'.format(coordToMove('a1')))
    # print(moveToCoord(0))
    print_obf("------------O------OOX-----XOX----XXOO----XO-O------------------ X;")
    print(bitboards_to_obf(0x317d453b069dc01d, 0xcc02bac0f9423ee2))
    utils.LibC().board_print(obf_to_bitboards("------------O------OOX-----XOX----XXOO----XO-O------------------ X;"))
    board = obf_to_bitboards("XOXXXOOO-OOOOOXXXOXXX-OXOXXOOOOOXX-XXXOOXOXOOOXOXOXXXXX-X-OOXXOO X;")
    print(board.player, board.opponent)




