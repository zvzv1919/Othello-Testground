import ctypes
from ctypes import cdll
import numpy as np

# Global Variables
C_LIB = cdll.LoadLibrary('./edax_so/edax.so')

# Use Clib class if loading library becomes a performance issue
# class Clib()
#     def __init__(self):
#         self.clib = cdll.LoadLibrary('./edax_so/edax')



class Board(ctypes.Structure):
    _fields_=[("player", ctypes.c_uint64), ("opponent", ctypes.c_uint64)]

def board_init(Board):
    pass

"""
:return: 1d array of positions on game board, this is the same as initial observations of the environment
"""
def print_board(board: Board):
    """
    For test purpose, print the bit-board in a crude way
    :param board: the board to print
    """
    rows = [[0 for i in range(8)] for j in range(8)]
    for i in range(64):
        row = (64-i-1)//8
        col = 64 - i - 1 - row * 8
        if (board.player >> i) % 2 == 1:
            rows[row][col] = 1
        if (board.opponent >> i) % 2 == 1:
            rows[row][col] = -1
    for row in rows:
        print(row)



if __name__ == '__main__':

    # Call function
    # C_LIB.board_init.argtypes=[ctypes.POINTER(Board)]
    C_LIB.get_moves.argtypes=[ctypes.c_ulonglong, ctypes.c_ulonglong]
    C_LIB.get_moves.restype=ctypes.c_ulonglong
    C_LIB.get_stderr.restype=ctypes.c_int64
    C_LIB.board_print.argtypes=[ctypes.POINTER(Board), ctypes.c_int16, ctypes.c_int64]
    # C_LIB.board_print.argtypes=[]

    testboard = Board(0,0)
    C_LIB.board_init(ctypes.byref(testboard))

    # testboard.opponent = testboard.opponent | (3 << 34) | (3 << 19)
    # testboard.player = testboard.player ^ (1 << 35)
    print_board(testboard)

    print(format(testboard.player, "x"))
    print(format(testboard.opponent, "x"))
    legal_moves=C_LIB.get_moves(testboard.player,
                                testboard.opponent)


    # legal_moves = C_LIB.get_moves(ctypes.c_ulonglong(testboard.player), ctypes.c_ulonglong(testboard.opponent))

    print("below are legal moves")
    print(format(legal_moves, "x"))
    print_board(Board(legal_moves, 0))
    C_STDERR = C_LIB.get_stderr()

    # test edax AI
    # C_LIB.search_global_init()



    C_LIB.board_print(ctypes.byref(testboard), 0, C_STDERR)
    pass

    # Board board[1];
    # board->player = P;
    # board->opponent = O;

    # printf("board print from get_moves:\n");
    # board_print(board, BLACK, stderr);