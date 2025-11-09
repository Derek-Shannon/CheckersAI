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
        self.isCalculating = False

        self._score = None
        self._move = None

    # --- Utility/Evaluation Methods ---
    
    def eval_score(self, board):
        """
        Evaluates the score of a given board state from the AI's perspective (Black).
        Positive score favors Black, Negative score favors Red.
        """
        # Base Piece Values
        REGULAR_PIECE_VAL = 50.0
        KING_VAL = 100.0  # Must be significantly higher than regular
        
        # Positional/Safety Weights
        ADVANCEMENT_BONUS = 2.0  # Reward for moving pieces closer to the king row
        CENTER_CONTROL_BONUS = 5.0 # Reward for occupying central squares
        THREAT_PENALTY = 20.0     # Large penalty for pieces that can be captured next turn
        KING_ROW_BONUS = 15.0     # Bonus for regular pieces reaching the King Row's back row

        score = 0
        
        # Helper function to check if a piece is on a central square (rows 3, 4, 5 and cols 2, 3, 4, 5)
        def is_central(r, c):
            return 2 <= r <= 5 and 2 <= c <= 5

        for r in range(8):
            for c in range(8):
                piece = board.get_piece_at(r, c)
                
                if piece:
                    # Determine the base value
                    val = KING_VAL if piece.king else REGULAR_PIECE_VAL
                    
                    # --- Positional Heuristics ---
                    
                    # 1. Advancement Bonus (Moving closer to king row)
                    if not piece.king:
                        if piece.color == self.color: # Black (moves downwards, wants row 7)
                            # Black row 0 to 7. We want row 7. Max bonus at r=7.
                            val += r * ADVANCEMENT_BONUS
                            
                        else: # Red (moves upwards, wants row 0)
                            # Red row 7 to 0. We want row 0. Max bonus at r=0.
                            val += (7 - r) * ADVANCEMENT_BONUS
                    
                    # 2. Center Control Bonus
                    if is_central(r, c):
                        val += CENTER_CONTROL_BONUS

                    # 3. King Row Home Defense Bonus (Important to prevent opponent kinging)
                    # Pieces on the far back row (for Black, row 7; for Red, row 0)
                    if not piece.king:
                        if piece.color == self.color and r == 7:
                            val += KING_ROW_BONUS
                        elif piece.color == self.opponent_color and r == 0:
                            val += KING_ROW_BONUS

                    # --- Accumulate Score ---
                    if piece.color == self.color: # Black (Maximizing)
                        score += val
                    else: # Red (Minimizing)
                        score -= val
        
        # Check all Red pieces for possible jumps on Black pieces
        for red_piece in board._get_player_pieces(self.opponent_color):
            threats = board._check_jump_moves(red_piece)
            
            # If the Red piece can jump, it's a huge problem for Black
            if threats:
                # Iterate over all targets to see which Black piece is threatened
                for target_rc, captured_piece in threats.items():
                    if captured_piece and captured_piece.color == self.color:
                        # Black piece is threatened, apply severe penalty
                        # Note: The 'val' for the piece is already counted, so this is a penalty.
                        score -= THREAT_PENALTY
                        # We break after the first threat found to keep the calculation simpler, 
                        # but in a more complex eval, you'd want to penalize each unique threatened piece.
        
        # 5. Piece Safety Bonus (Opponent piece is threatened)
        # Check if the AI (Black) has a mandatory jump against the OPPONENT (Red)
        for black_piece in board._get_player_pieces(self.color):
            opportunities = board._check_jump_moves(black_piece)
            
            if opportunities:
                # Reward for a jump opportunity (which should be mandatory)
                score += 0.5 * THREAT_PENALTY # Reward is half the penalty value
                        
        return score

    def runAI(self, current_board):
        """Public method to start the Minimax search."""
        self._score, self._move = self._minmax(current_board, self.max_depth, True)
    
    def get_best_move(self):
        """Public method to start the Minimax search."""
        
        return self._score, self._move

    # ... (MinMaxAgent __init__, eval_score, runAI, get_best_move methods remain the same) ...

    def _minmax(self, board, depth, is_maximizing_player, alpha=-math.inf, beta=math.inf):
        """
        The recursive Minimax function with Alpha-Beta Pruning.
        
        :param board: The current Board object (a copy)
        :param depth: Current search depth
        :param is_maximizing_player: True if current turn is AI (Black), False if opponent (Red)
        :param alpha: The best value found so far for the maximizing player (Black)
        :param beta: The best value found so far for the minimizing player (Red)
        :returns: (score, best_move)
        """
        # Base case 1: Reached max depth
        if depth == 0:
            return self.eval_score(board), None
        
        # Base case 2: Game over (Terminal state)
        _, is_over = board.get_game_state()
        if is_over:
            # Assign terminal scores based on who lost the ability to move
            if board.current_turn != self.color: # Opponent can't move (AI wins)
                return math.inf, None 
            else: # AI can't move (AI loses)
                return -math.inf, None

        color = self.color if is_maximizing_player else self.opponent_color
        valid_moves = board.get_all_legal_moves(color)
        
        if not valid_moves:
            # If no legal moves, the current player loses. Score depends on the winner.
            if is_maximizing_player: # Black can't move, Red wins
                return -math.inf, None 
            else: # Red can't move, Black wins
                return math.inf, None 
        
        best_move = valid_moves[0] # Initialize with a fallback move

        if is_maximizing_player: # Maximizing Player (Black)
            max_val = -math.inf 
            
            for move in valid_moves:
                
                # --- Simulation ---
                new_board = board.deep_copy() 
                piece_rc, target_rc, captured_piece = move
                
                # Retrieve the pieces on the *new_board* for simulation
                piece_on_new_board = new_board.get_piece_at(piece_rc[0], piece_rc[1])
                captured_piece_on_new_board = None
                if captured_piece:
                    cap_r, cap_c = captured_piece.row, captured_piece.col
                    captured_piece_on_new_board = new_board.get_piece_at(cap_r, cap_c)
                
                must_multijump, _ = new_board.move_piece(
                    piece_rc, target_rc, captured_piece_on_new_board
                )
                
                # --- Recursion and Pruning ---
                if must_multijump:
                    # Same player, same depth, pass current alpha/beta
                    current_val, _ = self._minmax(new_board, depth, True, alpha, beta)
                else:
                    # Switch player, decrease depth, pass current alpha/beta
                    current_val, _ = self._minmax(new_board, depth - 1, False, alpha, beta) 

                if current_val > max_val:
                    max_val = current_val
                    best_move = move
                
                # Alpha-Beta Pruning Condition
                alpha = max(alpha, max_val)
                if beta <= alpha:
                    break # Beta cut-off: The minimizing player (Red) won't choose this path
                          # because they already found a better (lower) option elsewhere.

            return max_val, best_move

        else: # Minimizing Player (Red)
            min_val = math.inf
            
            for move in valid_moves:
                
                # --- Simulation (Same logic as above) ---
                new_board = board.deep_copy()
                piece_rc, target_rc, captured_piece = move
                
                piece_on_new_board = new_board.get_piece_at(piece_rc[0], piece_rc[1])
                captured_piece_on_new_board = None
                if captured_piece:
                    cap_r, cap_c = captured_piece.row, captured_piece.col
                    captured_piece_on_new_board = new_board.get_piece_at(cap_r, cap_c)
                
                must_multijump, _ = new_board.move_piece(
                    piece_rc, target_rc, captured_piece_on_new_board
                )
                
                # --- Recursion and Pruning ---
                if must_multijump:
                    # Same player, same depth, pass current alpha/beta
                    current_val, _ = self._minmax(new_board, depth, False, alpha, beta)
                else:
                    # Switch player, decrease depth, pass current alpha/beta
                    current_val, _ = self._minmax(new_board, depth - 1, True, alpha, beta) # Next turn is Maximizing (Black)

                if current_val < min_val:
                    min_val = current_val
                    best_move = move
                
                # Alpha-Beta Pruning Condition
                beta = min(beta, min_val)
                if beta <= alpha:
                    break # Alpha cut-off: The maximizing player (Black) won't choose this path
                          # because they already found a better (higher) option elsewhere.
                     
            return min_val, best_move