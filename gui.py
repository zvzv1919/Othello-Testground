"""
Everything UI
"""
class GUI:
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