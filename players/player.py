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

'''
    coord - eg. 'd3', 'a8'
'''
def coordToMove(coord):
    coord = coord.lower()
    return (ord(coord[0]) - ord('a')) + 8*(int(coord[1])-1)

'''
    Test case:
    print('{}'.format(coordToMove('a1')))
    print(moveToCoord(0)) <- replace the int with result from above
'''
def moveToCoord(move):
    res = str(chr(ord('a')+(move%8)) + str(1 + (move//8)))
    return res
class EdaxPlayer:
    def __init__(self, name):
        self.libc = utils.LibC()
        self.name = name
        self.process = subprocess.Popen(['./bin/mEdax', '-mode', '1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                                       stderr=subprocess.STDOUT)
        self.first_move = True
        self.board = None
        self.last_edax_move = None

    def get_move(self, board):
        edax_move = -1
        if self.first_move:
            self.board = copy.deepcopy(board)
            line = self.process.stdout.readline()
            cnt = 0
            edax_played = False
            print("haha")
            while line:
                cnt += 1
                line_string = line.decode('utf-8')
                if "Edax plays" in line_string:
                    # parse line_string to get edax move
                    edax_move_coords = line_string.split(" ")[2][:-1]
                    edax_move = coordToMove(edax_move_coords)
                    self.last_edax_move = edax_move
                    print("edax_move: ", edax_move, file=sys.stderr)
                    cnt = 0
                    edax_played = True
                print(cnt, '\t', line.decode('utf-8'), end='')
                if cnt == 12 and edax_played:
                    break
                line = self.process.stdout.readline()
            self.first_move = False
        else:
            # compute the other player move and send it to edax
            opponent_move = -1
            # self.libc.board_print(board)
            # self.libc.board_print(self.board)
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
            if opponent_move == -1:
                opponent_move_coords = "ps"
            else:
                opponent_move_coords = moveToCoord(opponent_move)
            print("opponent move coords:", opponent_move_coords)
            self.process.stdin.write(opponent_move_coords.encode('utf-8') + b'\n')
            self.process.stdin.flush()

            # get edax move
            line = self.process.stdout.readline()
            cnt = 0
            edax_played = False
            while line:
                cnt += 1
                line_string = line.decode('utf-8')
                if "Edax plays" in line_string:
                    # parse line_string to get edax move
                    edax_move_coords = line_string.split(" ")[2][:-1]
                    edax_move = coordToMove(edax_move_coords)
                    self.last_edax_move = edax_move
                    print("edax_move: ", edax_move, file=sys.stderr)
                    cnt = 0
                    edax_played = True
                print(cnt, '\t', line.decode('utf-8'), end='')
                if cnt == 12 and edax_played:
                    break
                line = self.process.stdout.readline()
        self.board = copy.deepcopy(board)
        return edax_move

if __name__ == '__main_':
    edax_process = subprocess.Popen(['../bin/mEdax', '-mode', '1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    while True:
        line = edax_process.stdout.readline()
        cnt = 0
        edax_played = False
        while line:
            cnt += 1
            line_string = line.decode('utf-8')
            if "Edax plays" in line_string:
                # parse line_string to get edax move
                edax_move_coords = line_string.split(" ")[2][:-1]
                edax_move = coordToMove(edax_move_coords)

                cnt = 0
                edax_played = True
            print(cnt, '\t', line.decode('utf-8'), end='')
            if cnt == 12 and edax_played:
                break
            line = edax_process.stdout.readline()

        # Read a line of input from the main process's stdin
        print("end output")
        input_line = input()
        print("haha" + input_line)
        # Send this input line to Edax's stdin
        edax_process.stdin.write(input_line.encode('utf-8') + b'\n')
        edax_process.stdin.flush()

    # subprocess.Popen(['../bin/mEdax', '-mode', '0'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

# random_player = Player("random player", )

if __name__ == '__main__':
    print('{}'.format(coordToMove('a1')))
    print(moveToCoord(0))




