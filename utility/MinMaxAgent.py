# checkers/ai/minmax.py
import math
import copy
# We assume Piece and Board are correctly imported and accessible
from .Piece import Piece
from .Board import Board

class MinMaxAgent:
    """
    Implements the Minimax algorithm to find the best move for the AI player (Black).
    It works by simulating moves on copies of the Board object.
    """
    
    def __init__(self, color, max_depth):
        self.color = color # 'Black'
        self.opponent_color = 'Red'
        self.max_depth = max_depth

    # --- Utility/Evaluation Methods ---
    
    def eval_score(self, board):
        """
        Evaluates the score of a given board state from the AI's perspective (Black).
        Positive score favors Black, Negative score favors Red.
        """
        score = 0
        
        # 1. Piece Count and King Status
        for r in range(8):
            for c in range(8):
                piece = board.get_piece_at(r, c)
                if piece:
                    val = 1
                    if piece.king:
                        val = 2 # Kings are more valuable
                        
                    if piece.color == self.color: # Black (Maximizing)
                        score += val
                    else: # Red (Minimizing)
                        score -= val
        for piece in board._get_player_pieces(self.color):
            r, c = piece.row, piece.col
            pass

        return score

    # --- Minimax Algorithm ---
    
    def get_best_move(self, current_board):
        """Public method to start the Minimax search."""
        
        # Note: The Minimax function is now part of the class and uses the Board methods directly.
        # We start by maximizing for 'Black'.
        score, move = self.minmax(current_board, self.max_depth, True)
        return move

    def minmax(self, board, depth, is_maximizing_player):
        """
        The recursive Minimax function.
        
        :param board: The current Board object (a copy)
        :param depth: Current search depth
        :param is_maximizing_player: True if current turn is AI (Black), False if opponent (Red)
        :returns: (score, best_move)
        """
        # Base case 1: Reached max depth
        if depth == 0:
            return self.eval_score(board), None
        
        # Base case 2: Game over
        _, is_over = board.get_game_state()
        if is_over:
             # Very high score for win, very low for loss
             if board.current_turn != self.color: # If AI's opponent can't move (AI wins)
                 return math.inf, None 
             else: # If AI can't move (AI loses)
                 return -math.inf, None

        color = self.color if is_maximizing_player else self.opponent_color
        
        # Get all *potential first moves* for the current player
        # We use the board's method now
        valid_moves = board.get_all_legal_moves(color)
        
        if not valid_moves:
             # Can't move, assume it's a loss for the current player
             # The game over check above should handle this, but this is a safety.
             return self.eval_score(board), None
        
        best_move = valid_moves[0] # Initialize with the first move as a fallback

        if is_maximizing_player: # Maximizing Player (Black)
            max_val = -math.inf 
            
            for move in valid_moves:
                
                # 1. Simulate the current move on a deep copy
                new_board = board.deep_copy() 
                piece_rc, target_rc, captured_piece = move
                
                # NOTE: The move_piece method on the Board object now handles all logic:
                # moving the piece, kinging, and checking for multi-jumps.
                
                # We need to get the PIECE object on the *new_board* at the start_rc
                piece_on_new_board = new_board.get_piece_at(piece_rc[0], piece_rc[1])
                
                # The captured piece passed in the 'move' tuple is from the original board.
                # We need to find the equivalent captured piece on the new_board copy.
                cap_r, cap_c = None, None
                if captured_piece:
                    cap_r, cap_c = captured_piece.row, captured_piece.col
                    captured_piece_on_new_board = new_board.get_piece_at(cap_r, cap_c)
                else:
                    captured_piece_on_new_board = None

                # Execute the move simulation (uses the Board logic)
                # The move_piece method updates the board in place and returns multi-jump status
                must_multijump, _ = new_board.move_piece(
                    piece_rc, target_rc, captured_piece_on_new_board
                )

                # 2. Recurse based on multi-jump status
                if must_multijump:
                    # Turn is NOT over. Recurse for SAME player, SAME depth.
                    # This handles the mandatory multi-jump sequence.
                    current_val, _ = self.minmax(new_board, depth, is_maximizing_player)
                else:
                    # Turn is over. Switch player, decrease depth.
                    current_val, _ = self.minmax(new_board, depth - 1, False) # Next turn is Minimizing (Red)

                # 3. Update best value
                if current_val > max_val:
                    max_val = current_val
                    best_move = move

            return max_val, best_move

        else: # Minimizing Player (Red)
            min_val = math.inf
            
            for move in valid_moves:
                
                # 1. Simulate the current move on a deep copy
                new_board = board.deep_copy()
                piece_rc, target_rc, captured_piece = move
                
                piece_on_new_board = new_board.get_piece_at(piece_rc[0], piece_rc[1])
                
                cap_r, cap_c = None, None
                if captured_piece:
                    cap_r, cap_c = captured_piece.row, captured_piece.col
                    captured_piece_on_new_board = new_board.get_piece_at(cap_r, cap_c)
                else:
                    captured_piece_on_new_board = None
                
                must_multijump, _ = new_board.move_piece(
                    piece_rc, target_rc, captured_piece_on_new_board
                )
                
                # 2. Recurse based on multi-jump status
                if must_multijump:
                    # Turn is NOT over. Recurse for SAME player, SAME depth.
                    current_val, _ = self.minmax(new_board, depth, is_maximizing_player)
                else:
                    # Turn is over. Switch player, decrease depth.
                    current_val, _ = self.minmax(new_board, depth - 1, True) # Next turn is Maximizing (Black)

                # 3. Update best value
                if current_val < min_val:
                    min_val = current_val
                    best_move = move
                     
            return min_val, best_move