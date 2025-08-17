import ctypes
from ctypes import cdll
import time
import numpy as np

# Use Clib class if loading library becomes a performance issue
# class Clib()
#     def __init__(self):
#         self.clib = cdll.LoadLibrary('./edax_so/edax')

class Board(ctypes.Structure):
    _fields_=[("player", ctypes.c_uint64), ("opponent", ctypes.c_uint64)]
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent

    def __eq__(self, other):
        return self.opponent == other.opponent and self.player == other.player

class LibC():
    # py-C interface
    def __init__(self):
        # If restype not explicitly set, cdll will truncate a returning int64 to int8
        self.libc = cdll.LoadLibrary('/Users/xuan.zhao/Documents/GitHub-zv/Othello-Testground/edax_so/edax.so')
        self.libc.get_moves.argtypes=[ctypes.c_ulonglong, ctypes.c_ulonglong]
        self.libc.get_moves.restype=ctypes.c_ulonglong
        self.libc.get_stderr.restype=ctypes.c_int64
        #ctypes.POINTER(Board) alias ctypes.c_int64
        self.libc.board_print.argtypes=[ctypes.POINTER(Board), ctypes.c_int16, ctypes.c_int64]
        self.libc.board_init.argtypes=[ctypes.POINTER(Board)]
        self.libc.board_is_game_over.argtypes=[ctypes.POINTER(Board)]
        self.libc.board_is_game_over.restype=ctypes.c_bool
        self.libc.board_swap_players.argtypes=[ctypes.POINTER(Board)]
        self.libc.board_next.argtypes=[ctypes.POINTER(Board), ctypes.c_int16, ctypes.POINTER(Board)]
        self.libc.bit_count.argtypes=[ctypes.c_ulonglong]
        self.libc.bit_count.restype=ctypes.c_int8

    def get_moves(self, player, opponent):
        return self.libc.get_moves(player, opponent)

    def get_stderr(self):
        return self.libc.get_stderr()

    def get_stdout(self):
        return self.libc.get_stdout()

    def stdin(self):
        return self.libc.get_stdin()

    def board_print(self, board, player_color=0, io=None):
        if io is None:
            # Print to stderr since stdout is buffered and can cause segv
            io = self.get_stderr()
        return self.libc.board_print(ctypes.byref(board), player_color, io)

    def board_init(self, board):
        self.libc.board_init(ctypes.byref(board))

    def board_is_game_over(self, board):
        return self.libc.board_is_game_over(ctypes.byref(board))

    def board_swap_players(self, board):
        self.libc.board_swap_players(ctypes.byref(board))

    # not the same name as C func
    def board_update(self, board, move, next):
        self.libc.board_next(ctypes.byref(board), move, ctypes.byref(next))

    def bit_count(self, num):
        return self.libc.bit_count(num)

def board_init(Board):
    pass

def global_init():
    print("hello from global init")

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} Time: {end - start:.6f} seconds")
        if len(args) > 0:
            print(f"args: {args}")
        if len(kwargs) > 0:
            print(f"kwargs: {kwargs}")
        print("====================================================")
        return result
    return wrapper