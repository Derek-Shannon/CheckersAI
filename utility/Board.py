# checkers/game/board.py
import copy
from .Piece import Piece # Assumes Piece is available in the same directory

class Board:
    """Manages the 8x8 checkers board state and game rules."""
    
    def __init__(self):
        self.board = self._init_board()
        self.current_turn = 'Red' # Red starts first
        self.taken_pieces = {'Red': 0, 'Black': 0}

    def __repr__(self):
        """A simple representation of the board for debugging."""
        return f"Board(Turn: {self.current_turn}, Red Taken: {self.taken_pieces['Red']}, Black Taken: {self.taken_pieces['Black']})"

    def _init_board(self):
        """Initializes the 8x8 checkers board with pieces."""
        board = [[None] * 8 for _ in range(8)]
        # Place Black pieces (top three rows)
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 != 0:
                    # Piece objects need to be instantiated
                    board[r][c] = Piece(r, c, 'Black')
        # Place Red pieces (bottom three rows)
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 != 0:
                    # Piece objects need to be instantiated
                    board[r][c] = Piece(r, c, 'Red')
        return board
    
    # --- Deep Copy Method for AI Simulation ---
    def deep_copy(self):
        """
        Returns a completely independent copy of the current Board state,
        including all Piece objects, for MinMax simulation.
        """
        # Create a new Board instance
        new_board_state = Board() 
        
        # Deep copy the piece data structure (list of lists)
        new_board_state.board = copy.deepcopy(self.board)
        
        # Copy scalar attributes
        new_board_state.current_turn = self.current_turn
        new_board_state.taken_pieces = self.taken_pieces.copy()
        
        # It is crucial to update the row/col references in the new pieces
        # to point to the correct Piece objects in the new board state, 
        # though deepcopy of the 2D list of mutable objects handles this correctly.
        # However, because Piece objects store their own (r, c), a standard
        # deepcopy will create new Piece objects with correct internal (r, c)
        # and the board array will reference the new ones.
        return new_board_state


    # --- Utility Methods ---
    def _is_on_board(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece_at(self, r, c): # Renamed to public for scene use
        """Safely retrieves a piece from the board."""
        if self._is_on_board(r, c):
            return self.board[r][c]
        return None

    def _get_player_pieces(self, color):
        """Returns a list of all pieces belonging to a color."""
        pieces = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    # --- Movement/Rule Methods ---

    def _check_jump_moves(self, piece):
        """Calculates all possible jump moves for a given piece."""
        moves = {}
        r, c = piece.row, piece.col
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Non-king pieces can only move forward
        if not piece.king:
            if piece.color == 'Red':
                directions = [d for d in directions if d[0] == -1]
            else: # Black
                directions = [d for d in directions if d[0] == 1]

        for dr, dc in directions:
            mid_r, mid_c = r + dr, c + dc
            target_r, target_c = r + 2 * dr, c + 2 * dc

            if self._is_on_board(target_r, target_c) and self.board[target_r][target_c] is None:
                # Use the local get_piece_at
                captured_piece = self.get_piece_at(mid_r, mid_c)
                if captured_piece and captured_piece.color != piece.color:
                    moves[(target_r, target_c)] = captured_piece
        return moves

    def get_valid_moves(self, piece):
        """
        Calculates all valid moves for a piece, respecting mandatory jump rules.
        Returns a dictionary {(r, c): captured_piece_object or None}.
        """
        
        # 1. Check for mandatory jump moves for THIS piece
        jump_moves = self._check_jump_moves(piece)
        if jump_moves:
            return jump_moves
        
        # 2. Check if a *different* piece must jump (mandatory jump rule)
        player_pieces = self._get_player_pieces(piece.color)
        for other_piece in player_pieces:
            # We must check ALL pieces for jumps
            if self._check_jump_moves(other_piece):
                return {} # A different piece has a mandatory jump, so this piece cannot move non-jump

        # 3. If no jumps are available anywhere, check for simple non-jump moves
        moves = {}
        r, c = piece.row, piece.col
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        if not piece.king:
            if piece.color == 'Red':
                directions = [d for d in directions if d[0] == -1]
            else: # Black
                directions = [d for d in directions if d[0] == 1]

        for dr, dc in directions:
            target_r, target_c = r + dr, c + dc
            if self._is_on_board(target_r, target_c) and self.board[target_r][target_c] is None:
                moves[(target_r, target_c)] = None # None means no piece captured
        return moves

    def move_piece(self, piece_rc, target_rc, captured_piece=None):
        """
        Executes a move.
        Returns: (must_multijump: bool, status_message: str)
        """
        p_r, p_c = piece_rc
        t_r, t_c = target_rc
        piece = self.board[p_r][p_c]
        
        if not piece:
            return False, "" 
            
        # 1. Move the piece on the board
        self.board[t_r][t_c] = piece
        self.board[p_r][p_c] = None
        piece.row, piece.col = t_r, t_c # IMPORTANT: Update piece's internal coordinates
        
        status_message = ""

        # 2. Handle capture if a jump occurred
        if captured_piece:
            cap_r, cap_c = captured_piece.row, captured_piece.col
            # The captured_piece object passed in must correspond to the one on the board
            # For simplicity, we just check the square we jumped over.
            mid_r = (p_r + t_r) // 2
            mid_c = (p_c + t_c) // 2
            self.board[mid_r][mid_c] = None # Remove the captured piece
            
            opponent_color = 'Black' if piece.color == 'Red' else 'Red'
            self.taken_pieces[opponent_color] += 1
            
            # Check for multi-jump opportunity
            if self._check_jump_moves(piece):
                status_message = f"{piece.color} must make another jump!"
                return True, status_message # Multi-jump: turn does NOT switch
        
        # 3. Handle Kinging
        if not piece.king:
            # Red kings at row 0, Black kings at row 7
            if (piece.color == 'Red' and t_r == 0) or (piece.color == 'Black' and t_r == 7):
                piece.make_king()
                status_message = f"{piece.color} Kinged!"
        
        # 4. End turn and switch player
        self.current_turn = 'Black' if self.current_turn == 'Red' else 'Red'
        if not status_message:
             status_message = f"It's {self.current_turn}'s turn."
             
        return False, status_message # No multi-jump, turn switched

    def get_game_state(self):
        """
        Checks for game over conditions.
        Returns: (message: str, is_over: bool)
        """
        
        # Check if one side has captured all pieces
        if self.taken_pieces['Red'] == 12:
            return 'Black Wins!', True
        if self.taken_pieces['Black'] == 12:
            return 'Red Wins!', True

        # Check if the current player has no legal moves
        current_player_pieces = self._get_player_pieces(self.current_turn)
        # Check if ANY piece for the current player has ANY valid move
        has_valid_move = any(self.get_valid_moves(piece) for piece in current_player_pieces)
        
        if not has_valid_move:
            winner = 'Black' if self.current_turn == 'Red' else 'Red'
            return f"Game Over! {self.current_turn} has no legal moves. {winner} wins!", True

        return "", False # Game is not over
    
    # --- Methods for AI/MinMax ---
    
    def get_all_legal_moves(self, color):
        """
        Returns a list of all legal moves for a given color, formatted for MinMax.
        (piece_rc, target_rc, captured_piece)
        """
        all_moves = []
        player_pieces = self._get_player_pieces(color)

        # 1. Check for mandatory jumps first (standard checkers rule)
        all_jumps = []
        for piece in player_pieces:
            jumps = self._check_jump_moves(piece) 
            for target_rc, captured_piece in jumps.items():
                all_jumps.append(((piece.row, piece.col), target_rc, captured_piece))

        if all_jumps:
            # If jumps are available, only return jumps
            return all_jumps
        
        # 2. If no jumps are available, check for simple non-jump moves
        for piece in player_pieces:
            # Note: We can reuse the logic from get_valid_moves, 
            # but since we already confirmed no *jumps* exist anywhere, 
            # we only need to check for simple moves.
            
            r, c = piece.row, piece.col
            directions = []
            if piece.king:
                directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            elif piece.color == 'Red':
                directions = [(-1, 1), (-1, -1)] # Red moves up
            else: # Black
                directions = [(1, 1), (1, -1)] # Black moves down
            
            for dr, dc in directions:
                target_r, target_c = r + dr, c + dc
                
                if self._is_on_board(target_r, target_c) and self.board[target_r][target_c] is None:
                    # Append the simple move (captured_piece is None)
                    all_moves.append(((r, c), (target_r, target_c), None))
        return all_moves