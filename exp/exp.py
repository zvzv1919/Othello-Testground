import ctypes
from ctypes import cdll



if __name__ == '__main__':
    C_LIB = cdll.LoadLibrary('./edax_so/hello.so')
    C_LIB.print_input.argtypes=[ctypes.c_ulonglong]
    opponent = ctypes.c_ulonglong(0x1c08180000)
    player = ctypes.c_ulonglong(0x10000000)
    C_LIB.print_input(player, opponent)

    C_LIB_EDAX = cdll.LoadLibrary('./edax_so/edax.so')
    # C_LIB_EDAX.print_input(player, opponent)
    moves = C_LIB_EDAX.get_moves(player, opponent)
    C_LIB_EDAX.print_input(moves)


