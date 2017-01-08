import random

###############################################################################

def _get_player_discs(board, color):
    """
        Find all the discs belonging to the next player.

        Arguments:
        - board: the content of the board
        - color: the next player's color

        Return value:
        - discs_pos: list of all discs position stored as [row, col]
    """
    discs_pos = []

    for row in range(0, 8):
        line = board[row].lower() # remove kings
        col = -1
        while line.find(color, col + 1) != -1:
            col = line.find(color, col + 1)
            discs_pos.append([row, col])

    return discs_pos

###############################################################################

def _next_non_capt(board, disc_pos):
    """
        Find all possible next non capturing positions.

        Arguments:
        - board:    the content of the board
        - disc_pos: the position of the player disc

        Return value:
        - positions: a list of valid non capturing moves.
    """
    # Get the disc attributes
    row, col = disc_pos
    color = board[row].lower()[col]
    king = False if board[row][col] == color else True

    if king:
        # Define the four diagonal positions
        bot_left  = [[row + 1, col - 1]] if col > 0 and row < 7 else []
        bot_right = [[row + 1, col + 1]] if col < 7 and row < 7 else []
        top_left  = [[row - 1, col - 1]] if col > 0 and row > 0 else []
        top_right = [[row - 1, col + 1]] if col < 7 and row > 0 else []
        positions = top_left + top_right + bot_left + bot_right
    else:
        # Define the forward direction
        fwd = 1 if color == "b" else -1

        # Define the two left and right position
        f_row = row + fwd
        left  = [[f_row, col - 1]] if col > 0 and f_row in range(0, 8) else []
        right = [[f_row, col + 1]] if col < 7 and f_row in range(0, 8) else []
        positions = left + right

    # Check that the moves are indeed possible
    positions = [p for p in positions if board[p[0]][p[1]] == "_"]

    return positions

###############################################################################

def _next_capt(board, disc_pos):
    """
        Find all possible next capturing positions.

        Arguments:
        - board:    the content of the board
        - disc_pos: the position of the player disc

        Return value:
        - positions: a list of valid capturing moves.
    """
    # Get the disc attributes
    row, col = disc_pos
    color = board[row].lower()[col]
    king = False if board[row][col] == color else True

    if king:
        # Define the four diagonal positions
        bot_left  = [[row + 2, col - 2]] if col > 1 and row < 6 else []
        bot_right = [[row + 2, col + 2]] if col < 6 and row < 6 else []
        top_left  = [[row - 2, col - 2]] if col > 1 and row > 1 else []
        top_right = [[row - 2, col + 2]] if col < 6 and row > 1 else []
        positions = top_left + top_right + bot_left + bot_right
    else:
        # Define the forward direction
        fwd = 1 if color == "b" else -1

        # Define the two left and right position
        f_row = row + 2 * fwd
        left  = [[f_row, col - 2]] if col > 1 and f_row in range(0, 8) else []
        right = [[f_row, col + 2]] if col < 6 and f_row in range(0, 8) else []
        positions = left + right

    # Check that the landing positions is empty
    positions = [p for p in positions if board[p[0]][p[1]] == "_"]

    # Check that the inbetween position is of the different color
    positions = [p for p in positions \
        if board[(row + p[0]) / 2][(col + p[1]) / 2].lower() \
        not in ["_", color]]

    return positions

###############################################################################

def _update_board_pos(board, prev_pos, next_pos):
    """
        Update the board with a single move.

        Arguments:
        - board:    the content of the board
        - prev_pos: position of the disc before the move
        - next_pos: position of the disc after the move

        Return value:
        - new_board: the updated board.
    """
    # Use new variables for clarity
    prev_row, prev_col = prev_pos
    next_row, next_col = next_pos
    new_board = board
    old_disc = board[prev_row][prev_col]
    color = old_disc.lower()

    # Update next position with previous position and look out for kings
    if old_disc == "b":
        new_disc = "B" if next_row == 7 else "b"
    elif old_disc == "w":
        new_disc = "W" if next_row == 0 else "w"
    else:
        new_disc = old_disc
    s = list(new_board[next_row])
    s[next_col] = new_disc
    new_board[next_row] = "".join(s)

    # Empty previous position
    s = list(new_board[prev_row])
    s[prev_col] = "_"
    new_board[prev_row] = "".join(s)

    # Empty intermediary position if it's a capturing move
    if abs(next_row - prev_row) == 2:
        s = list(new_board[(next_row + prev_row) / 2])
        s[(next_col + prev_col) / 2] = "_"
        new_board[(next_row + prev_row) / 2] = "".join(s)

    return new_board

###############################################################################

def _update_board_move(board, moves):
    """
        Update the board with a serie of moves.

        Arguments:
        - board: the content of the board
        - move:  list of disc positions starting with the current position.

        Return value:
        - new_board: the updated board.
    """
    # Update the board up to the last position step
    new_board = board[:]
    for i in range(0, len(moves) - 1):
        prev_pos = moves[i]
        next_pos = moves[i + 1]
        new_board = _update_board_pos(new_board, prev_pos, next_pos)

    return new_board

###############################################################################

def allowed_moves(board, color):
    """
        This is the first function you need to implement.

        Arguments:
        - board: The content of the board, represented as a list of strings.
                 The length of strings are the same as the length of the list,
                 which represents a NxN checkers board.
                 Each string is a row, from the top row (the black side) to the
                 bottom row (white side). The string are made of five possible
                 characters:
                 - '_' : an empty square
                 - 'b' : a square with a black disc
                 - 'B' : a square with a black king
                 - 'w' : a square with a white disc
                 - 'W' : a square with a white king
                 At the beginning of the game:
                 - the top left square of a board is always empty
                 - the square on it right always contains a black disc
        - color: the next player's color. It can be either 'b' for black or 'w'
                 for white.

        Return value:
        It must return a list of all the valid moves. Please refer to the
        README for a description of what are valid moves. A move is a list of
        all the squares visited by a disc or a king, from its initial position
        to its final position. The coordinates of the square must be specified
        using (row, column), with both 'row' and 'column' starting from 0 at
        the top left corner of the board (black side).

        Example:
        >> board = [
            '________',
            '__b_____',
            '_w_w____',
            '________',
            '_w______',
            '_____b__',
            '____w___',
            '___w____'
        ]

        The top-most black disc can chain two jumps and eat both left white
        discs or jump only over the right white disc. The other black disc
        cannot move because it does produces any capturing move.

        The output must thus be:
        >> allowed_moves(board, 'b')
        [
            [(1, 2), (3, 0), (5, 2)],
            [(1, 2), (3, 4)]
        ]
    """

    # Retrieve next player discs position
    discs_pos = _get_player_discs(board, color)

    # Compute the possible moves
    moves_non_capt = []
    moves_capt = []
    for disc_pos in discs_pos:
        # Retrieve initial capturing positions
        pos_capt_init = _next_capt(board, disc_pos)
        if pos_capt_init != []:
            # Define a queue to store all possible position sequences
            mv_queue = [[disc_pos, p] for p in pos_capt_init]

            # Pop an element from the queue, if there is no more capturing move
            # then we add it to the final move list otherwise we had the new
            # steps and add it to the queue.
            while mv_queue != []:
                # Get the first element from queue and initialize the board
                pos_steps = mv_queue.pop(0)
                new_board = board[:]

                # Update the board up to the last position step
                new_board = _update_board_move(board, pos_steps)

                # Check remaining capturing moves
                pos_capt = _next_capt(new_board, pos_steps[-1])
                if pos_capt == []:
                    moves_capt += [pos_steps]
                else:
                    mv_queue += [pos_steps + [p] for p in pos_capt]

        # Retrieve non capturing positions
        if moves_capt == []:
            pos_non_capt = _next_non_capt(board, disc_pos)
            moves_non_capt += [[disc_pos, p] for p in pos_non_capt]

    return moves_non_capt if moves_capt == [] else moves_capt

###############################################################################

def _eval_board_single_color(board, color):
    """
        Evaluate the board score for one color individually.
        The evaluation takes into consideration:
            - the number of normal discs
            - the number of kings
            - the number of discs on sides

        Arguments:
        - board: the content of the board
        - color: the color to be evaluated

        Return value:
        - score: the board value, higher is better
    """
    # Values used for positions
    KING_VAL = 4
    DISC_VAL = 1
    SIDE_VAL = 0.75

    # Bonus point for kings and discs
    kings = 0
    discs = 0
    for line in board:
        kings += line.count(color.upper())
        discs += line.count(color)
    score = KING_VAL * kings + DISC_VAL * discs

    # # Bonus points for side position
    # sides = 0
    # for line in board:
    #     s = list(line)
    #     sides += 1 if s[0] == color else 0
    #     sides += 1 if s[-1] == color else 0
    # score += SIDE_VAL * sides

    return score

###############################################################################

def _eval_board(board, our_color):
    """
        Heuristic used to evaluate a board.

        Arguments:
        - board: the content of the board
        - color: the color of our AI

        Return value:
        - score: the board value, higher is better
    """
    their_color = "b" if our_color == "w" else "w"
    our_score = _eval_board_single_color(board, our_color)
    their_score = _eval_board_single_color(board, their_color)

    return our_score - their_score

###############################################################################

def _find_best_move(board, our_color, depth):
    """
        Recursively find the best move by maxmimzing the score with our move and
        minimizing it with their score.

        Arguments:
        - board:        the content of the board
        - our_color:    the color of our AI
        - depth:        number of moves to see in the futur

        Return value:
        - our_bst_mv:   our move to maximize score
        - our_bst_scr:  correspond score
    """
    # Initialize variables
    their_color = "b" if our_color == "w" else "w"
    our_bst_mv = []
    our_bst_scr = 0

    # Go through all possible combination of our move and their move
    our_moves = allowed_moves(board, our_color)
    for our_move in our_moves:
        new_board1 = _update_board_move(board, our_move)
        their_moves = allowed_moves(new_board1, their_color)

        # Initialize variables
        their_bst_mv = []
        their_bst_scr = 0

        # Go through each independent move
        for their_move in their_moves:
            new_board2 = _update_board_move(new_board1, their_move)

            # Find the best move and record score
            if depth > 0:
                _, score = _find_best_move(new_board2, our_color, depth - 1)
            else:
                score = _eval_board(new_board2, our_color)

            # Initial update if it was never assigned
            if their_bst_mv == []:
                their_bst_scr = score
                their_bst_mv = their_move

            # Check if they can play better which means decreasing the score
            if score < their_bst_scr:
                their_bst_scr = score
                their_bst_mv = their_move

        # Initial update if it was never assigned
        if our_bst_mv == []:
            our_bst_scr = their_bst_scr
            our_bst_mv = our_move

        # Check if we can play better which means increasing the score
        if their_bst_scr > our_bst_scr:
            our_bst_mv = our_move
            our_bst_scr = their_bst_scr

    return our_bst_mv, our_bst_scr

###############################################################################

def _number_disc(board):
    """
        Count the number of discs in the board.

        Arguments:
        - board: the content of the board

        Return value:
        - n: number of discs
    """
    n = 0
    for line in board:
        n += line.lower().count("b")
        n += line.lower().count("w")

    return n

###############################################################################

def play(board, color):
    """
        We look all the possible n moves in the future and considering that we
        play perfectly and so does the other player we chose the move that
        maximize our score using the _eval_board() function.
    """
    n_disc = _number_disc(board)
    depth = 2 if n_disc > 15 else 3

    print("Adaptative depth: %d" % depth)
    best_move, best_score = _find_best_move(board, color, depth)
    print("Score: %d" % best_score)

    return best_move

###############################################################################

def random_play(board, color):
    """
        An example of play function based on allowed_moves.
    """
    moves = allowed_moves(board, color)
    # There will always be an allowed move
    # because otherwise the game is over and
    # 'play' would not be called by main.py
    return random.choice(moves)
