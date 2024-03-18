# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# Importing stuff
import sys
import os
import numpy as np

import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog
from tkinter import ttk

import turtle
from turtle import ScrolledCanvas

from agents import othello_agent

# Making the coordinate arrays
grid_pos = [-150, -100, -50, 0, 50, 100, 150]  # 7 lines = 8 grids
black_player = {"id": -1, "colour": "#000000", "label": "Player 1 (Black)", "score": 0}
white_player = {"id": 1, "colour": "#FFFFFF", "label": "Player 2 (White)", "score": 0}
directions = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))  # eight directions

# Given a board, return a move.
def player(game_state):
    return (0,0)


'''
Othello game class
'''
# Should be initialized as Othello(white=None, black=None, gui=None)
class Othello:
    def start(self):
        self.curr_player = 1 #1 for black and 0 for white
        self.play

    def __init__(self, _root):
        """
        Initialises the key game variables

        player_pos_list - list of player positions based on grid size
        game_board - n x n board matrix
        curr_player - current player can be white_player or black_player
        next_player - next player can be white_player or black_player
        token - Turtle graphics object to draw tokens
        instruction - Turtle graphics object for instruction text
        score - Turtle graphics object for score text
        window - Turtle graphics object to display game window and for GUI events
        """


        self.root = _root

        # global instance of turtles
        self.outer = None
        self.inner = None
        self.grid = None
        self.token = None
        self.cross = None
        self.player_instruction = None
        self.game_instruction = None
        self.score = None
        self.close_msg = None
        self.window = None

        self.player_pos_list = None
        self.game_board = None
        self.game_over = False

        # variable for player turn
        self.skip_turn = False
        self.curr_player = None
        self.next_player = None

        # a set of the possible coordinates (x, y) for the next player
        self.next_possible_actions = set()
        # a set of the possible positions for the player in turn
        self.player_valid_pos = set()

        # if True, show a red plus sign in the grid where the player is allowed to put a piece
        self.show_next_possible_actions_hint = True

        # rl agent variables
        self.game_mode = None
        self.rl_agent = othello_agent.OthelloDQN(nb_observations=64, player="white")

        # reset game environment
        self.reset()

    def render(self):
        """
        method override from gym class for rendering the game environment
        :return: _render_frame()
        """
        return self._render_frame()

    def _render_frame(self):
        """
        if render_mode is human, initialise the turtle objects for rendering and draw game board. Regardless of
        modes, always initialise the board
        :return: 1d array of positions on game board, this is the same as initial observations of the environment
        """
        if self.window is None:

            self.root.title("Othello")
            # center the root
            ws = self.root.winfo_screenwidth()
            hs = self.root.winfo_screenheight()
            w = ws * 0.5
            h = hs * 0.75
            x = (ws / 2) - (w / 2)
            y = (hs / 2) - (h / 2)
            self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

            # create canvas, need to put into scrolled canvas so that resizing of the window will not crop the
            # TurtleScreen
            self.canvas_frame = tk.Frame(self.root)
            self.canvas_frame.pack(side=tk.LEFT, padx=0, pady=1, fill=tk.BOTH, expand=tk.YES)
            self.canvas = ScrolledCanvas(self.canvas_frame, width=w, height=h)
            self.canvas.pack(anchor=tk.CENTER, padx=5, pady=1, fill=tk.BOTH, expand=tk.YES)

            # Window Setup - needs to be here so that we can initialise the window, draw and initialise the game board,
            # capture the mouse clicks using window.mainloop()
            # self.window = turtle.Screen()
            self.window = turtle.TurtleScreen(self.canvas)
            self.window.bgcolor("#444444")
            self.window.colormode(255)

            # self.outer = turtle.Turtle()
            self.outer = turtle.RawTurtle(self.window)
            self.outer.speed(0)
            self.outer.ht()

            # self.inner = turtle.Turtle()
            self.inner = turtle.RawTurtle(self.window)
            self.inner.speed(0)
            self.inner.ht()

            # self.grid = turtle.Turtle()
            self.grid = turtle.RawTurtle(self.window)
            self.grid.speed(0)
            self.grid.ht()

            # global instance of token turtle
            # self.token = turtle.Turtle()
            self.token = turtle.RawTurtle(self.window)
            self.token.speed(0)
            self.token.ht()

            # global instance of cross turtle
            # self.cross = turtle.Turtle()
            self.cross = turtle.RawTurtle(self.window)
            self.cross.speed(0)
            self.cross.ht()

            # global instance of instruction turtle
            # self.instruction = turtle.Turtle()
            self.player_instruction = turtle.RawTurtle(self.window)
            self.player_instruction.color("white")
            self.player_instruction.speed(0)
            self.player_instruction.ht()

            # self.game_instruction = turtle.Turtle()
            self.game_instruction = turtle.RawTurtle(self.window)
            self.game_instruction.color("white")
            self.game_instruction.speed(0)
            self.game_instruction.ht()

            # global instance of score turtle
            # self.score = turtle.Turtle()
            self.score = turtle.RawTurtle(self.window)
            self.score.color("white")
            self.score.speed(0)
            self.score.ht()

            # global instance of close_msg turtle
            # self.close_msg = turtle.Turtle()
            self.close_msg = turtle.RawTurtle(self.window)
            self.close_msg.speed(0)
            self.close_msg.ht()

            # draw the game board once only
            self.draw_board(grid_pos, self.outer, self.inner, self.grid)

        else:
            # clear existing turtles
            self.token.clear()
            self.cross.clear()
            self.player_instruction.clear()
            self.score.clear()

        # initialise the board positions
        self.init_board(self.player_pos_list)
        # return the game_board grid
        return self.game_board

    def reset(self, seed=None, options=None):
        """
        Resets the game, along with the default players and initial board positions
        :param seed: set seed including super class
        :param options: not used
        :return: environment observations, environment info
        """
        # initialise datastructure
        self.player_pos_list = generate_player_pos_list(grid_pos)
        self.game_board = np.zeros((len(self.player_pos_list), len(self.player_pos_list)))

        self._render_frame()

        # reinitialise game variables
        self.game_over = False

        # variable for player turn - black always starts first
        self.skip_turn = False
        self.curr_player = black_player
        self.next_player = white_player
        self.next_possible_actions = get_valid_board_pos(self.game_board, self.curr_player)

        print("Game Reset.")

    def load_rl_agent(self, model_dir="./model"):
        if self.game_mode == "agent":
            load_status, msg = self.rl_agent.load_model(path=model_dir, name="OthelloDQN", format_type="model")
            if not load_status:
                self.message_popup("Error loading agent", msg, "ok_message")
            else:
                self.message_popup("Success", msg, "ok_message")
            return load_status
        elif self.game_mode == "human":
            return True

    def play(self, mode="human"):
        """
        initialise the mouse click callbacks and starts the event loop
        :return:
        """
        # each mouse click is to place the token
        if mode == "agent":
            self.window.onscreenclick(self.play_against_agent)
            white_player["label"] = "Reinforcement Learning Agent (White)"
        elif mode == "human":
            self.window.onscreenclick(self.play_against_human)

        self.window.onkeypress(self.close, "Escape")
        self.window.onkeypress(self.end_game, "q")
        # listen for
        self.window.listen()
        self.window.mainloop()

    def message_popup(self, title, message, btn_type="ok_message"):
        """
        Displays a pop-up window for messages
        :param title: title string
        :param message: string to show on popup
        :param btn_type: prompt button type
        :return:
        """

        def set_game_mode(value):
            self.game_mode = value

        btn_height = 1
        btn_width = 10

        pop = Toplevel(self.root)
        pop.transient(self.root)
        pop.grab_set()
        pop.wm_title(title)
        w = 400  # popup window width
        h = 175  # popup window height
        sw = pop.winfo_screenwidth()
        sh = pop.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        pop.geometry('%dx%d+%d+%d' % (w, h, x, y))

        label_frame = Frame(pop)
        label_frame.pack(side=TOP, fill=X)

        label = Label(label_frame, text=message, font=("Verdana", 16), wraplength=375, justify="center")
        label.pack(side="top", fill="x", pady=15)

        button_frame = Frame(pop)
        button_frame.pack(side=BOTTOM, fill=X)

        if btn_type == "ok_message":
            ok_button = Button(button_frame, text="OK", width=btn_width, height=btn_height, command=pop.destroy)
            ok_button.pack(in_=button_frame, side="bottom", pady=20)

        elif btn_type == "done_replay":
            done_button = Button(button_frame, text="Done", width=btn_width, height=btn_height,
                                 command=lambda: [self.exit_program(), pop.destroy()])
            # done_button.pack(in_=bottom, side="left", pady=5)
            done_button.grid(row=0, column=0, sticky=W, padx=10, pady=20)

            replay_button = Button(button_frame, text="Replay", width=btn_width, height=btn_height,
                                   command=lambda: [self.reset(), pop.destroy()])
            # replay_button.pack(in_=bottom, side="right", pady=5)
            replay_button.grid(row=0, column=1, sticky=E, padx=10, pady=20)

            button_frame.grid_rowconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)

        elif btn_type == "human_agent":
            human_button = Button(button_frame, text="Human", width=btn_width, height=btn_height,
                                  command=lambda: [set_game_mode("human"), pop.destroy()])
            human_button.grid(row=0, column=0, sticky=W, padx=10, pady=20)

            agent_button = Button(button_frame, text="Agent", width=btn_width, height=btn_height,
                                  command=lambda: [set_game_mode("agent"), pop.destroy()])
            agent_button.grid(row=0, column=1, sticky=E, padx=10, pady=20)

            button_frame.grid_rowconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)

        self.root.wait_window(pop)

    def draw_board(self, _grid_pos, outer, inner, grid):
        """
        draw the game board using turtles
        :param _grid_pos: array of grid lines
        :param outer: outer box turtle drawing object
        :param inner: outer box turtle drawing object
        :param grid: grid lines turtle drawing object
        :return:
        """
        # def is_checked():
        #     return Label(self.root, text=f'Playing against RL agent, {play_agent.get()}').pack()

        border = 10

        grid_pos_x = max(_grid_pos) + 50 + border
        grid_pos_y = max(_grid_pos) + 50 + border
        grid_length = grid_pos_x + grid_pos_x

        # Making the outer border of the game
        outer.color((255, 255, 255))
        outer.up()
        outer.goto(grid_pos_x, grid_pos_y)
        outer.down()
        outer.begin_fill()
        for z in range(4):
            outer.rt(90)
            outer.fd(grid_length)
        outer.end_fill()

        # Making the inner border of the game
        inner.color((53, 136, 86))
        inner.up()
        inner.goto(grid_pos_x - border, grid_pos_y - border)
        inner.down()
        inner.begin_fill()
        for z in range(4):
            inner.rt(90)
            inner.fd(grid_length - (border * 2))
        inner.end_fill()

        # Making the grid
        grid.color((0, 0, 0))
        for p in range(len(grid_pos)):
            grid.up()
            grid.goto(-grid_pos_x + border, grid_pos[p])
            grid.down()
            grid.fd(grid_length - (border * 2))
            grid.lt(90)
            grid.up()
            grid.goto(grid_pos[p], -grid_pos_y + border)
            grid.down()
            grid.fd(grid_length - (border * 2))
            grid.rt(90)

        # write for next player - first player always black
        self.game_instruction.clear()
        self.game_instruction.penup()
        self.game_instruction.goto(0, -(self.window.window_height() / 2) + 80)
        self.game_instruction.write("Press Q to end current game and ESC to exit game", align="center",
                                    font=("Courier", 24, "bold"))

    # draw token
    def draw_token(self, x_ind, y_ind, colour, _pos_list):
        """
        draw token on the game board
        :param x_ind: x pos index
        :param y_ind: y pos index
        :param colour: token colour (#000000 or #FFFFFF)
        :param _pos_list: list of token positions (x,y) in points for each cell on the game board
        :return:
        """
        self.token.speed(0)
        self.token.up()
        self.token.goto(_pos_list[x_ind], _pos_list[y_ind])
        self.token.dot(40, colour)

    # draw cross
    def draw_cross(self, x_ind, y_ind, colour, width, length, _pos_list):
        """
        draw cross on the game board to mark out valid positions
        :param x_ind: x pos index
        :param y_ind: y pos index
        :param width: width of the cross
        :param length: length of the cross
        :param colour: token colour (#000000 or #FFFFFF)
        :param _pos_list: list of token positions (x,y) in points for each cell on the game board
        :return:
        """
        self.cross.speed(0)
        self.cross.width(width)
        self.cross.color(colour)
        self.cross.penup()
        self.cross.goto(_pos_list[x_ind], _pos_list[y_ind])
        self.cross.pendown()
        self.cross.right(45)
        self.cross.forward(length)
        self.cross.backward(length * 2)
        self.cross.forward(length)
        self.cross.left(90)
        self.cross.forward(length)
        self.cross.backward(length * 2)

    # initialise game_board
    def init_board(self, _pos_list):
        """
        initialise the game board with starting positions
        :param _pos_list: list of token positions (x,y) in points for each cell on the game board
        :return:
        """
        # set the game_board matrix
        self.game_board[3, 3] = black_player['id']
        self.game_board[4, 4] = black_player['id']
        self.game_board[3, 4] = white_player['id']
        self.game_board[4, 3] = white_player['id']

        # turn turtle animation on or off and set a delay for update drawings.
        self.window.delay(0)
        self.window.tracer(0, 0)

        self.draw_token(3, 3, black_player['colour'], _pos_list)
        self.draw_token(4, 4, black_player['colour'], _pos_list)
        self.draw_token(3, 4, white_player['colour'], _pos_list)
        self.draw_token(4, 3, white_player['colour'], _pos_list)

        # write for next player - first player always black
        self.player_instruction.clear()
        self.player_instruction.penup()
        self.player_instruction.goto(0, -(self.window.window_height() / 2) + 120)
        self.player_instruction.write(black_player['label'] + " To Play", align="center", font=("Courier", 24, "bold"))

        # draw valid positions on board
        self.show_valid_board_pos(black_player)

        # Perform a TurtleScreen update. To be used when tracer is turned off.
        self.window.update()

    # get the next player
    def get_next_player(self):
        """
        get the next player based on the current player
        :return: the next player
        """
        if self.curr_player is None:
            self.curr_player = black_player
        else:
            self.curr_player = white_player if self.curr_player == black_player else black_player
        return self.curr_player

    def get_board_index(self, _x_pos, _y_pos):
        """
        get board index from mouse click x, y pos. convert mouse x,y positions into game board positions
        :param _x_pos: x position from mouse click
        :param _y_pos: y position from mouse click
        :return: set of valid (x, y) board positions
        """
        # find the closest index for x, y coordinate
        x_index = 0
        curr_x_diff = 50  # set to 50 because it is the max distance from the mouse pos to the grid
        y_index = 0
        curr_y_diff = 50  # set to 50 because it is the max distance from the mouse pos to the grid
        # find the closest index for x y coordinate
        for i in range(len(self.player_pos_list)):
            if curr_x_diff > abs(self.player_pos_list[i] - _x_pos):
                x_index = i
                curr_x_diff = abs(self.player_pos_list[i] - _x_pos)

            if curr_y_diff > abs(self.player_pos_list[i] - _y_pos):
                y_index = i
                curr_y_diff = abs(self.player_pos_list[i] - _y_pos)

        return x_index, y_index

    def show_valid_board_pos(self, player):
        """
        display all valid player positions as crosses on the game board
        :param player:
        :return:
        """
        # get all valid positions based on the next player
        self.player_valid_pos = get_valid_board_pos(self.game_board, player)
        # draw possible positions on board
        self.cross.clear()
        for pos in self.player_valid_pos:
            self.cross.setheading(0)
            self.draw_cross(pos[0], pos[1], "NavyBlue", 3, 10, self.player_pos_list)

    def add_to_board(self, x_ind, y_ind, player):
        """
        add x_ind, y_ind position to game board and flip tokens (if any)
        :param x_ind: x index position
        :param y_ind: y index position
        :param player: current player
        :return:
        """
        # check that player is a valid player
        assert player in (black_player, white_player), "illegal player input"

        # place the player on the board
        self.game_board[x_ind, y_ind] = player['id']

        # draw the player's token on the screen
        self.draw_token(x_ind, y_ind, player['colour'], self.player_pos_list)

        # validate the play and identify any captured positions
        for direction in range(8):
            flip_seq = []
            flip_tokens = False

            if direction == 0:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind, y_ind + 1, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 1:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind + 1, y_ind + 1, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 2:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind + 1, y_ind, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 3:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind + 1, y_ind - 1, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 4:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind, y_ind - 1, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 5:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind - 1, y_ind - 1, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 6:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind - 1, y_ind, direction, player, flip_seq,
                                                  flip_tokens)

            if direction == 7:
                flip_tokens, flip_seq = eval_cell(self.game_board, x_ind - 1, y_ind + 1, direction, player, flip_seq,
                                                  flip_tokens)

            # if there is a valid capture and the list of captured positions is > 0
            if flip_tokens and len(flip_seq) > 0:
                # print(direction, flip_seq)
                # flip all captured positions
                for i in range(len(flip_seq)):
                    self.game_board[flip_seq[i][0], flip_seq[i][1]] = player['id']
                    self.draw_token(flip_seq[i][0], flip_seq[i][1], player['colour'], self.player_pos_list)
                # print(self.game_board)

    # place the token based on the mouse click position x, y
    # this function will then execute all the logic of the game
    def play_token(self, x_ind, y_ind, player):
        """
        Plays one move of the game.  This is a callback function for click of the mouse
        :param player:
        :param x_ind: x position on game board
        :param y_ind: y position on game board
        :return: True - if play is valid, False - if play is invalid
        """
        # turn turtle animation on or off and set a delay for update drawings.
        self.window.delay(0)
        self.window.tracer(0, 0)

        # set / reset skip_turn variable
        self.skip_turn = False

        # check that this is a valid position
        if not check_board_pos(self.game_board, x_ind, y_ind, player):
            self.message_popup("Error", "You cannot place a token here", "ok_message")
            return False

        # add the token to the board
        self.add_to_board(x_ind, y_ind, player)

        # calculate white and black score
        _score_white, _score_black = calculate_score(self.game_board)
        # assign scores to the player objects
        white_player['score'] = _score_white
        black_player['score'] = _score_black

        self.score.clear()
        self.score.hideturtle()

        self.score.penup()
        self.score.goto(0, -(self.window.window_height() / 2) + 700)
        self.score.write(white_player['label'] + " score:" + str(white_player['score']), align="center",
                         font=("Courier", 24, "bold"))

        self.score.penup()
        self.score.goto(0, -(self.window.window_height() / 2) + 670)
        self.score.write(black_player['label'] + " score:" + str(black_player['score']), align="center",
                         font=("Courier", 24, "bold"))

        # get the next player
        next_player = white_player if player == black_player else black_player

        # get all valid positions based on the next player and draw valid positions on board
        self.show_valid_board_pos(next_player)
        # get the set of next possible actions
        self.next_possible_actions = get_valid_board_pos(self.game_board, next_player)

        # check if there are still positions to play else end the game
        if len(self.next_possible_actions) == 0:
            # back to current player's turn
            curr_possible_actions = get_valid_board_pos(self.game_board, player)
            # if even current player cannot place any position then game ends
            if len(curr_possible_actions) == 0:
                self.next_possible_actions = set()
                self.next_player = None
                self.game_over = True
            else:  # if current player can place position then continue with next player as current player
                self.next_possible_actions = curr_possible_actions
                self.skip_turn = True  # set prev player as player to indicate a skip turn
                self.curr_player = player  # this is so that the get_player() is getting the correct player turn
                # get all valid positions based on the next player and draw valid positions on board
                self.show_valid_board_pos(player)
        else:
            # write instructions for next player
            self.player_instruction.clear()
            self.player_instruction.penup()
            self.player_instruction.goto(0, -(self.window.window_height() / 2) + 120)
            self.player_instruction.write(next_player['label'] + " To Play", align="center",
                                          font=("Courier", 24, "bold"))

        # Perform a TurtleScreen update. To be used when tracer is turned off.
        self.window.update()

        return True

    def play_against_human(self, _x_pos, _y_pos):
        """
        Plays one move of the game with a human.  This is a callback function for click of the mouse
        :param _x_pos: x position from mouse click
        :param _y_pos: y position from mouse click
        :return:
        """
        # get the board index from the mouse position
        x_ind, y_ind = self.get_board_index(_x_pos, _y_pos)
        is_valid_play = self.play_token(x_ind, y_ind, self.curr_player)

        # if it is valid play and it is not a skip turn then it is black player turn
        # this is for the case when the next turn cannot be played so the black player goes again
        if is_valid_play and not self.skip_turn:
            # next player turn else play is still with current player
            # self.curr_player = white_player if self.curr_player == black_player else black_player
            self.curr_player = self.get_next_player()
        else:  # if not valid placement then return and don't proceed to agent turn and exit
            return

        if self.game_over:
            self.end_game()

    def play_against_agent(self, _x_pos, _y_pos):
        """
        Plays one move of the game against the RL agent.  This is a callback function for click of the mouse
        :param _x_pos: x position from mouse click (for human)
        :param _y_pos: y position from mouse click (for human)
        :return:
        """
        # if human turn and there is a valid next action then play human position
        if self.curr_player == black_player and len(self.next_possible_actions) > 0:
            # play human move
            x_ind, y_ind = self.get_board_index(_x_pos, _y_pos)
            # return True if token can be placed in a valid position
            is_valid_play = self.play_token(x_ind, y_ind, self.curr_player)

            # if it is valid play and it is not a skip turn then it is white player (agent) turn
            # this is for the case when the next turn cannot be played so the black player goes again
            if is_valid_play and not self.skip_turn:
                # next player turn else play is still with current player
                # self.curr_player = white_player if self.curr_player == black_player else black_player
                self.curr_player = self.get_next_player()
            else:  # if not valid placement then return and don't proceed to agent turn and exit
                return

            # if after human move there are next possible moves then agent will play else if no other move for agent
            # then end game
            print(self.next_possible_actions)
            if len(self.next_possible_actions) > 0:

                while True:
                    # play agent move
                    action = self.rl_agent.choose_action(self.game_board.flatten().reshape((1, 64)),
                                                         self.next_possible_actions)
                    y_ind = action % 8
                    x_ind = (action // 8) % 8
                    # check that agent can make a valid move
                    assert (x_ind, y_ind) in self.next_possible_actions, "Invalid Next Action"
                    is_valid_play = self.play_token(x_ind, y_ind, self.curr_player)

                    # if it is valid play and it is not a skip turn then it is black player turn
                    # this is for the case when the next turn cannot be played so the white player (agent) goes again
                    if is_valid_play and not self.skip_turn:
                        # next player turn else play is still with current player
                        # self.curr_player = white_player if self.curr_player == black_player else black_player
                        self.curr_player = self.get_next_player()
                        break
                    # else:  # if not valid placement then return and don't proceed to agent turn and exit
                    #     return

            else:
                self.next_possible_actions = set()
                self.next_player = None
                self.game_over = True
        else:
            self.next_possible_actions = set()
            self.next_player = None
            self.game_over = True

        if self.game_over:
            self.end_game()

    def calculate_final_score(self):
        """
        calculates the final score of the game
        :return: message of who is the winner
        """
        # calculate final score
        final_score_white, final_score_black = calculate_score(self.game_board)
        # display winner
        msg = ""
        if final_score_white > final_score_black:
            msg += "White Player is the Winner with " + str(final_score_white) + " points"
        elif final_score_white < final_score_black:
            msg += "Black Player is the Winner with " + str(final_score_black) + " points"
        elif final_score_white == final_score_black:
            msg += "Game is a draw with " + \
                   "Black player: " + str(final_score_black) + " and White player:" + str(final_score_white) + " points"

        return msg

    def end_game(self):
        """
        ends the current game, calculates the current score and prompts player to quit or replay
        :return:
        """
        msg = self.calculate_final_score()
        self.message_popup("Game Completed", msg, "done_replay")

    def close(self):
        """
        This is a callback function for the escape key to clean up and exit
        :return:
        """
        self.score.clear()
        self.player_instruction.clear()
        self.game_instruction.clear()

        msg = self.calculate_final_score()
        self.message_popup("Game Completed", msg, "ok_message")
        self.exit_program()

    def exit_program(self):
        """
        terminates the turtle window and exits the program
        :return:
        """
        self.root.destroy()
        sys.exit()

def check_board_pos(game_board, x_ind, y_ind, player):
    """
    checks the x_ind, y_ind position if it is a valid position on the board
    :param x_ind:
    :param y_ind:
    :return: True if valid, False if invalid position
    """
    # get all the adjacent cells
    adj = get_adjacent(game_board, x_ind, y_ind)
    adj_sum = 0
    for i in range(len(adj)):
        adj_sum += abs(adj[i])

    # position must be either 0 or near an already placed token
    if game_board[x_ind, y_ind] == 0 and adj_sum > 0 and (x_ind, y_ind) in get_valid_board_pos(game_board, player):
        valid_pos = True
    else:
        valid_pos = False

    return valid_pos

def get_valid_board_pos(game_board, player):
    """
    gets a list of all the valid positions that the player can place given the current board positions.
    e.g. a player can only play a position if that position is able to flip token(s)
    :param player:
    :return: set of valid (x, y) positions
    """
    assert player in (black_player, white_player), "illegal player input"
    flip_seq = []
    flip_tokens = False
    valid_positions = []
    for x in range(8):
        for y in range(8):
            if game_board[x, y] in (0, player['id']): continue
            for i in range(len(directions)):
                _x = x + directions[i][0]
                _y = y + directions[i][1]
                if (_x < 0 or _x > 7) or (_y < 0 or _y > 7) or game_board[_x, _y] != 0: continue
                for j in range(len(directions)):
                    flip_tokens, flip_seq = eval_cell(game_board, _x + directions[j][0], _y + directions[j][1], j,
                                                      player,
                                                           flip_seq, flip_tokens)
                    if flip_tokens and len(flip_seq) > 0:
                        valid_positions.append((_x, _y))
    return set(valid_positions)

def eval_cell(game_board, x, y, _direction, _player, _flip_seq, _flip_tokens):
    """
    recursively evaluate all the possible cells to check if the position (x,y) has any tokens that can be flipped
    :param x: x index position
    :param y: y index position
    :param _direction: direction of evaluation
    :param _player: current player
    :param _flip_seq: list of (x,y) positions that can be flipped
    :param _flip_tokens: True = flip, False = do not flip
    :return:
    """
    try:
        cell_value = game_board[x, y]

        # if the cell is a 0 or out of bounds then end the recursion and return the current flip state and token
        # list as what is recorded thus far
        if (cell_value == 0) or (y < 0 or y >= 8) or (x < 0 or x >= 8):
            # return _flip_tokens, _flip_seq
            return False, []

        # if the cell is not the player's cell then mark for flipping
        if _player['id'] != cell_value:
            _flip_seq.append([x, y])
            _flip_tokens = False
        elif _player['id'] == cell_value:  # if the cell is the player's token then end the recursion
            _flip_tokens = True
            return _flip_tokens, _flip_seq

        # recursion if there are still more cells to evaluate. The evaluation and input to x and y depends on the
        # direction
        if _direction == 0 and cell_value != 0 and (y < game_board.shape[1]):
            _flip_tokens, _flip_seq = eval_cell(game_board, x, y + 1, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 1 and cell_value != 0 and (y < game_board.shape[1] and x < game_board.shape[0]):
            _flip_tokens, _flip_seq = eval_cell(game_board, x + 1, y + 1, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 2 and cell_value != 0 and (x < game_board.shape[0]):
            _flip_tokens, _flip_seq = eval_cell(game_board, x + 1, y, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 3 and cell_value != 0 and (y >= 0 and x < game_board.shape[0]):
            _flip_tokens, _flip_seq = eval_cell(game_board, x + 1, y - 1, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 4 and cell_value != 0 and (y >= 0):
            _flip_tokens, _flip_seq = eval_cell(game_board, x, y - 1, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 5 and cell_value != 0 and (y >= 0 and x >= 0):
            _flip_tokens, _flip_seq = eval_cell(game_board, x - 1, y - 1, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 6 and cell_value != 0 and (x >= 0):
            _flip_tokens, _flip_seq = eval_cell(game_board, x - 1, y, _direction, _player, _flip_seq, _flip_tokens)

        if _direction == 7 and cell_value != 0 and (y < game_board.shape[1] and x >= 0):
            _flip_tokens, _flip_seq = eval_cell(game_board, x - 1, y + 1, _direction, _player, _flip_seq, _flip_tokens)

        # return at the end of the recursion
        return _flip_tokens, _flip_seq
    except (IndexError, ValueError):
        return False, []

def get_adjacent(arr, i, j):
    """
    get the values of all adjacent cells of (i,j)
    :param arr: 1d array of token positions
    :param i: x index position
    :param j: y index position
    :return: vector of all values in the adjacent cells of (i,j)
    """

    def is_valid_pos(_i, _j, _n, _m):
        if _i < 0 or _j < 0 or _i > _n - 1 or _j > _m - 1:
            return False
        return True

    # Size of given 2d array
    n = arr.shape[0]
    m = arr.shape[1]

    # Initialising a vector array where adjacent element will be stored
    v = []

    # Checking for all the possible adjacent positions
    # bottom left
    if is_valid_pos(i - 1, j - 1, n, m):
        v.append(arr[i - 1][j - 1])
    # left
    if is_valid_pos(i - 1, j, n, m):
        v.append(arr[i - 1][j])
    # top left
    if is_valid_pos(i - 1, j + 1, n, m):
        v.append(arr[i - 1][j + 1])
    # top
    if is_valid_pos(i, j - 1, n, m):
        v.append(arr[i][j - 1])
    # top right
    if is_valid_pos(i, j + 1, n, m):
        v.append(arr[i][j + 1])
    # right
    if is_valid_pos(i + 1, j - 1, n, m):
        v.append(arr[i + 1][j - 1])
    # bottom right
    if is_valid_pos(i + 1, j, n, m):
        v.append(arr[i + 1][j])
    # bottom
    if is_valid_pos(i + 1, j + 1, n, m):
        v.append(arr[i + 1][j + 1])

    # Returning the vector
    return v

def calculate_score(_game_board):
    """
    calculate the score of black and white players from game board
    :param _game_board:
    :return: white player score, black player score
    """
    # calculate score the score
    score_white = 0
    score_black = 0

    for i in range(len(_game_board)):
        for j in range(len(_game_board)):
            value = _game_board[i, j]
            if value == white_player['id']:
                score_white += 1
            elif value == black_player['id']:
                score_black += 1

    return score_white, score_black

# We will draw a dot based on the turtle's position as the center of the circle. Because of this, we need a new array
# called player_pos_list. The values in this will be 25 away from each value in grid_pos, because our grid boxes are 50x50.
# So, we'll start at -225, then -175, -125, etc.
# Note that because the grid_pos are actually position of the lines, therefore the number of boxes will be 1 + no of
# lines thus the player_pos_list should be = 1+len(grid_pos).  When we populate this array of positions, we need to then
# make sure that the center (i.e. where grid_pos[i] == 0) translates into 2 positions of the player_pos_list[i] and
# player_pos_list[i+1]
def generate_player_pos_list(_grid_pos):
    """
    Generates a list of player positions (x,y) based on the dimensions of the game board to facilitate the drawing
    of the tokens on the board
    :param _grid_pos: array of grid lines
    :return: list of token positions (x,y) in points for each cell on the game board
    """
    lst = [None] * (len(_grid_pos) + 1)
    for i in range(len(_grid_pos)):
        if _grid_pos[i] < 0:
            lst[i] = _grid_pos[i] - 25
        elif _grid_pos[i] == 0:
            lst[i] = _grid_pos[i] - 25
            lst[i + 1] = _grid_pos[i] + 25  # to populate the additional position
        elif grid_pos[i] > 0:
            lst[i + 1] = _grid_pos[i] + 25  # henceforth the indexing on lst would be i+1
    return lst
