import tkinter as tk
from tkinter import filedialog
import os
from othello import Othello

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # # Call function
    # C_LIB.board_init.argtypes=[ctypes.POINTER(Board)]
    # testboard = Board(0,0)
    #
    # C_LIB.board_init(ctypes.byref(testboard))
    #
    # print(format(testboard.player, "b"))
    # print(format(testboard.opponent, "b"))
    # # ctypes.
    # pass

    root = tk.Tk()
    game = Othello(root)
    # set window callback
    root.protocol('WM_DELETE_WINDOW', game.exit_program)
    # choose game mode
    select_game_mode = False
    while not select_game_mode:
        game.message_popup("Game Play Mode", "Do you want to play with a Human or Agent?", "human_agent")
        if game.game_mode == "agent":
            model_dir = filedialog.askdirectory(parent=root,
                                                initialdir=os.getcwd(),
                                                title="Please select folder with model:")
            if game.load_rl_agent(model_dir):
                select_game_mode = True


        elif game.game_mode == "human":
            select_game_mode = True

    # play game
    game.play(mode=game.game_mode)

    # # calculate final score
    # final_score_white, final_score_black = game.calculate_score(game.game_board)
    # # display winner
    # msg = ""
    # if final_score_white > final_score_black:
    #     msg += "White Player is the Winner with " + str(final_score_white) + " points"
    # elif final_score_white < final_score_black:
    #     msg += "Black Player is the Winner with " + str(final_score_black) + " points"
    # elif final_score_white == final_score_black:
    #     msg += "Game is a draw with " + \
    #            "Black player: " + str(final_score_black) + " and White player:" + str(final_score_white) + " points"
    #
    # game.alert_popup(root, "Game Completed", msg)