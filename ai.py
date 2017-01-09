import random

###############################################################################

def _get_color_discs(board, color):
    """
        Find all the discs of the given color.

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

def allowed_moves(board, color, all_moves=True):
    """
        Compute either all allowed moves or only the capturing moves

        Arguments:
        - board: the content of the board
        - color: the next player's color
        - all_moves: boolean representing whether we should return all possible
                 moves (True, by default) or only the capturing moves (False)

        Return value:
        - moves: list of all the valid moves
    """

    # Retrieve next player discs position
    discs_pos = _get_color_discs(board, color)

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
        if moves_capt == [] and all_moves:
            pos_non_capt = _next_non_capt(board, disc_pos)
            moves_non_capt += [[disc_pos, p] for p in pos_non_capt]

    # Update the final moves
    if all_moves:
        moves = moves_non_capt if moves_capt == [] else moves_capt
    else:
        moves = moves_capt

    return moves

###############################################################################

def _get_unprotected_score(board, color):
    """
        Compute the number of unprotected disks of the given color considering
        that a disk is worth one point if let completely unprotected and a half
        otherwise.

        Arguments:
        - board: the content of the board
        - color: the color of the player

        Retur value:
        - score: score corresponding to the unprotected discs
    """
    # Retrieve discs position
    discs_pos = _get_color_discs(board, color)

    # Define forward direction and back row
    bck_row = 0 if color == "b" else 7
    fwd_dir = 1 if color == "b" else -1

    # Loop through all positions
    score = 0
    for disc_pos in discs_pos:
        row, col = disc_pos

        # Discs in the back row are automatically protected
        if row == bck_row or board[row][col] == color.upper():
            continue

        # Check left then right
        score += 0.5 if col > 0 and board[row - fwd_dir][col - 1] == "_" else 0
        score += 0.5 if col < 7 and board[row - fwd_dir][col + 1] == "_" else 0

    return score


###############################################################################

def _eval_board(board, our_color):
    """
        Heuristic used to evaluate a board. As we don't have access to the
        ennemy AI we will simply use their number of discs are metrics. For our
        AI on the other hand we will use:
            - number of kings and discs
            - king centering
            - disc protection

        Arguments:
        - board: the content of the board
        - our_color: the color of our AI

        Return value:
        - score: the board value, higher is better
    """
    their_color = "b" if our_color == "w" else "w"

    # Values used for positions
    DISC_VAL = 1        # Value of a normal disc
    KING_VAL = 3        # King
    CNTR_VAL = 0.01     # King in the midle
    UNPD_VAL = 0.5      # Unprotected score

    # Initialize variables
    our_kings   = 0;            their_kings = 0
    our_discs   = 0;            their_discs = 0
    middle_king = 0
    unprotected = _get_unprotected_score(board, our_color)

    # Go through all lines from our back to our front
    for row in range(0, 8):
        line = board[row]

        # Number of kings and normal discs
        our_kings += line.count(our_color.upper())
        our_discs += line.count(our_color)
        their_kings += line.count(their_color.upper())
        their_discs += line.count(their_color)

        # Number of kings on the midle
        middle_king += line.count(our_color.upper()) * \
            (3.5 - abs(row - 3.5))

    # Update the scores
    our_score = our_kings * KING_VAL + our_discs * DISC_VAL +\
        middle_king * CNTR_VAL + unprotected * UNPD_VAL
    their_score = their_kings * KING_VAL + their_discs * DISC_VAL

    return our_score - their_score

###############################################################################

def _last_eval_board(board, our_color, player_color):
    """
        Evaluate a board considering it's the last stage of the search tree.
        Only capturing moves are evaluated until there are no more unresolved
        capturing conflicts.

        Arguments:
        - board:        the content of the board
        - our_color:    the color of our AI
        - player_color: the color of the next player

        Return value:
        - best_score:   the score corresponding to the move that maximizes (or
                        minimizes) the score depending on the player color
    """
    # Initialize variables
    their_color = "w" if our_color == "b" else "b"
    next_player_color = "w" if player_color == "b" else "b"

    next_moves = allowed_moves(board, player_color, False)
    if next_moves == []:
        return _eval_board(board, our_color)
    else:
        # Initialize variables
        best_score = None

        # Go through all moves and recursively find the best
        for next_move in next_moves:
            # Update the board
            new_board = _update_board_move(board, next_move)

            # Compute best move and score
            score = _last_eval_board(new_board, our_color, next_player_color)

            # Update the score depending on the player color
            if best_score == None:
                best_score = score
            elif player_color == our_color and score > best_score:
                best_score = score
            elif player_color == their_color and score < best_score:
                best_score = score

    return best_score

###############################################################################

def _find_best_move(board, our_color, depth):
    """
        Recursively find the best move by maxmimzing the score with our move and
        minimizing it with their move.

        Arguments:
        - board:        the content of the board
        - our_color:    the color of our AI
        - depth:        number of moves to see in the futur

        Return value:
        - our_bst_mv:   our move to maximize score
        - our_bst_scr:  corresponding score
    """
    # Initialize variables
    their_color = "b" if our_color == "w" else "w"
    our_bst_mv = []
    our_bst_scr = _eval_board(board, our_color)

    # Go through all possible combination of our move and their move
    our_moves = allowed_moves(board, our_color)
    for our_move in our_moves:
        new_board1 = _update_board_move(board, our_move)
        their_moves = allowed_moves(new_board1, their_color)

        # Initialize variables
        their_bst_mv = []
        their_bst_scr = _eval_board(new_board1, our_color)

        # Go through each independent move
        for their_move in their_moves:
            new_board2 = _update_board_move(new_board1, their_move)

            # Find the best move and record score
            if depth > 0:
                _, score = _find_best_move(new_board2, our_color, depth - 1)
            else:
                score = _last_eval_board(new_board2, our_color, our_color)

            # Check if they can play better which means decreasing the score
            if their_bst_mv == [] or score < their_bst_scr:
                their_bst_scr = score
                their_bst_mv = their_move

        # Check if we can play better which means increasing the score
        if our_bst_mv == [] or their_bst_scr > our_bst_scr:
            our_bst_scr = their_bst_scr
            our_bst_mv = our_move

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
        We look all the possible moves in the future up to a certain depth and
        considering that we play perfectly and so does the other player we chose
        the move that maximize our score defined using _eval_board()
    """
    # Define the depth of the tree
    depth = 1 if _number_disc(board) > 6 else 2

    # Retrieve the best move
    best_move, _ = _find_best_move(board, color, depth)

    return best_move