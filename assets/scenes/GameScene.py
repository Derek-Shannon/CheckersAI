import pygame
import sys
import math, random, copy

from .Scene import Scene
from . import SearchAlgorithm
from ..data.Timer import Timer

# --- Piece Class ---
class Piece:
    """Represents a single checkers piece."""
    def __init__(self, row, col, color):
        # Color should be 'Red' or 'Black'
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        
        # Removed visual_color and outline_color since we are using images.
        # We'll still keep the outline_color for king status, using yellow for selection/king indicator.
        self.outline_color = (255, 100, 100) if color == 'Red' else (100, 100, 100)

    def make_king(self):
        """Promotes the piece to a King."""
        self.king = True
        self.outline_color = (255, 255, 0) # King pieces have a yellow/gold outline

    def __repr__(self):
        return f'{self.color[0]}{"K" if self.king else ""}({self.row},{self.col})'

# --- GameScene Class ---
class GameScene(Scene):
    def __init__(self, screen, mode='PvP'):
        super().__init__(screen)
        self.mode = mode
        self.AITimer = Timer(500) #500ms delay for AI
        print(f"Starting GameScene in {self.mode} mode.")
        try:
            self.board_image = pygame.image.load('assets/images/board.jpg').convert_alpha()
            self.board_image = pygame.transform.scale(self.board_image, (560, 560))

            self.red_piece_image = pygame.image.load('assets/images/red.png').convert_alpha()
            self.black_piece_image = pygame.image.load('assets/images/black.png').convert_alpha()

            self.red_king_image = pygame.image.load('assets/images/redKing.png').convert_alpha()
            self.black_king_image = pygame.image.load('assets/images/blackKing.png').convert_alpha()
            
            # Scale pieces to fit the squares
            piece_size = 60
            self.red_piece_image = pygame.transform.scale(self.red_piece_image, (piece_size, piece_size))
            self.black_piece_image = pygame.transform.scale(self.black_piece_image, (piece_size, piece_size))
            self.red_king_image = pygame.transform.scale(self.red_king_image, (piece_size, piece_size))
            self.black_king_image = pygame.transform.scale(self.black_king_image, (piece_size, piece_size))

            self.images_loaded = True
        except pygame.error as e:
            print(f"Error loading images: {e}. Using placeholders.")

        # Pygame Setup Constants
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.BOARD_SIZE = 560
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.OFFSET_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 4
        self.OFFSET_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2+30

        # Board Colors
        self.LIGHT_BROWN = (205, 133, 63) # Tan squares
        self.DARK_BROWN = (139, 69, 19)   # Brown squares (playable)
        self.MOVE_HIGHLIGHT = (0, 255, 0, 100) # Green transparent for valid moves
        self.SELECTION_HIGHLIGHT = (0, 0, 255) # Blue for selected piece

        # Back Button Setup
        self.button_rect = pygame.Rect(10, 10, 120, 40)
        self.font = pygame.font.Font(None, 36)
        self.button_text = self.font.render("<< Back", True, (255, 255, 255))
        self.text_rect = self.button_text.get_rect(center=self.button_rect.center)
        
        # Game State
        self.board = self._init_board()
        self.current_turn = 'Red' # Red starts first
        self.selected_piece = None # Stores the (row, col) of the selected piece
        self.valid_moves = {}      # Maps valid move (row, col) to captured piece (or None)
        self.taken_pieces = {'Red': 0, 'Black': 0}
        
        # Text/UI
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.status_message = ""
        self.game_over = False

    def _init_board(self):
        """Initializes the 8x8 checkers board with pieces."""
        board = [[None] * 8 for _ in range(8)]
        
        # Place Black pieces (top three rows)
        for r in range(3):
            for c in range(8):
                # Pieces only placed on dark squares
                if (r + c) % 2 != 0:
                    board[r][c] = Piece(r, c, 'Black')

        # Place Red pieces (bottom three rows)
        for r in range(5, 8):
            for c in range(8):
                # Pieces only placed on dark squares
                if (r + c) % 2 != 0:
                    board[r][c] = Piece(r, c, 'Red')
        return board

    def _get_board_coords(self, pos):
        """Converts screen pixel coordinates to board (row, col)."""
        x, y = pos
        # Adjust for board offset
        x -= self.OFFSET_X
        y -= self.OFFSET_Y
        
        # Check if the click is within the board area
        if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:
            col = int(x // self.SQUARE_SIZE)
            row = int(y // self.SQUARE_SIZE)
            return row, col
        return None, None

    def _get_pixel_coords(self, row, col):
        """Converts board (row, col) to screen pixel center coordinates."""
        center_x = self.OFFSET_X + (col * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2)
        center_y = self.OFFSET_Y + (row * self.SQUARE_SIZE) + (self.SQUARE_SIZE // 2)
        return center_x, center_y
    
    def _is_on_board(self, r, c):
        """Checks if a position is within the 8x8 board bounds."""
        return 0 <= r < 8 and 0 <= c < 8

    def _get_piece_at(self, r, c, board=None):

        if board is None:
            board=self.board


        """Safely retrieves a piece from the board."""
        if self._is_on_board(r, c):
            return board[r][c]
        return None

    # --- Core Checkers Logic ---
    
    def _check_jump_moves(self, piece, mandatory_only=False, board=None):
        """Calculates all possible jump moves for a given piece."""
        
        if board is None:
            board = self.board
        
        
        moves = {}
        r, c = piece.row, piece.col
        
        # Directions: (row_step, col_step)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Non-king pieces can only move forward
        if not piece.king:
            if piece.color == 'Red':
                directions = [d for d in directions if d[0] == -1] # Red moves up (row index decreases)
            else: # Black
                directions = [d for d in directions if d[0] == 1] # Black moves down (row index increases)

        for dr, dc in directions:
            # Check the cell immediately adjacent (enemy position)
            mid_r, mid_c = r + dr, c + dc
            
            # Check the cell two steps away (landing position)
            target_r, target_c = r + 2 * dr, c + 2 * dc

            if self._is_on_board(target_r, target_c):
                # 1. Landing spot must be empty
                if board[target_r][target_c] is None:
                    captured_piece = self._get_piece_at(mid_r, mid_c, board)
                    
                    # 2. Must jump over an opponent piece
                    if captured_piece and captured_piece.color != piece.color:
                        # Format: {(target_r, target_c): captured_piece}
                        moves[(target_r, target_c)] = captured_piece
                        
        return moves

    def get_valid_moves(self, piece, board = None):
        """Calculates all valid moves (jumps and non-jumps) for a piece."""
        
        if board is None:
            board = self.board



        # 1. Always check for mandatory jump moves first
        jump_moves = self._check_jump_moves(piece)
        if jump_moves:
            return jump_moves
        
        #check if a different piece must jump
        player_pieces = self._get_player_pieces(piece.color)
        for other_piece in player_pieces:
            jumps = self._check_jump_moves(other_piece)
            if jumps != {}:
                return {} # a different piece must jump

        # 2. If no jumps are available, check for simple non-jump moves
        moves = {}
        r, c = piece.row, piece.col
        
        # Directions: (row_step, col_step)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Non-king pieces can only move forward
        if not piece.king:
            if piece.color == 'Red':
                directions = [d for d in directions if d[0] == -1] # Red moves up
            else: # Black
                directions = [d for d in directions if d[0] == 1] # Black moves down

        for dr, dc in directions:
            target_r, target_c = r + dr, c + dc
            
            if self._is_on_board(target_r, target_c):
                # Landing spot must be empty and on a dark square
                if self.board[target_r][target_c] is None:
                    # Non-jump moves don't capture a piece (value is None)
                    moves[(target_r, target_c)] = None

        return moves


    '''#for ai scoring
    def get_valid_movesAI(self, coords):
        """Calculates all valid moves (jumps and non-jumps) for a piece."""
        
        print("coords", coords)
        score = 0
        r, c = coords
        piece = Piece(r,c,'Black')
        
        # 1. Always check for mandatory jump moves first
        jump_moves = self._check_jump_moves(piece)
        if jump_moves:
            score = 1
            return jump_moves, score #sends back score for ai

        # 2. If no jumps are available, check for simple non-jump moves
        moves = {}
        
        
        # Directions: (row_step, col_step)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        # Non-king pieces can only move forward
        if not piece.king:
            if piece.color == 'Red':
                directions = [d for d in directions if d[0] == -1] # Red moves up
            else: # Black
                directions = [d for d in directions if d[0] == 1] # Black moves down

        for dr, dc in directions:
            target_r, target_c = r + dr, c + dc
            
            if self._is_on_board(target_r, target_c):
                # Landing spot must be empty and on a dark square
                
                if self.board[target_r][target_c] is None:
                    # Non-jump moves don't capture a piece (value is None)
                    moves[(target_r, target_c)] = None
                    score = 0
                else:
                    score = -2
        
        return moves,score '''


    def move_piece(self, piece_rc, target_rc, captured_piece=None):
        p_r, p_c = piece_rc
        t_r, t_c = target_rc
        piece = self.board[p_r][p_c]

        if not piece:
            return # Safety check

        # 1. Move the piece on the board
        self.board[t_r][t_c] = piece
        self.board[p_r][p_c] = None
        piece.row, piece.col = t_r, t_c

        # 2. Handle capture if a jump occurred
        if captured_piece:
            cap_r, cap_c = captured_piece.row, captured_piece.col
            self.board[cap_r][cap_c] = None
            
            # Update the taken pieces counter
            opponent_color = 'Black' if piece.color == 'Red' else 'Red'
            self.taken_pieces[opponent_color] += 1
            
            # Check for multi-jump opportunity
            if self._check_jump_moves(piece):
                # The turn does NOT switch yet; select the piece again
                self.selected_piece = (t_r, t_c)
                self.valid_moves = self._check_jump_moves(piece)
                self.status_message = f"{piece.color} must make another jump!"
                return
        
        # 3. Handle Kinging
        if not piece.king:
            if piece.color == 'Red' and t_r == 0: # Red kings at row 0
                piece.make_king()
                self.status_message = "Red Kinged!"
            elif piece.color == 'Black' and t_r == 7: # Black kings at row 7
                piece.make_king()
                self.status_message = "Black Kinged!"

        # 4. End turn and switch player
        self.selected_piece = None
        self.valid_moves = {}
        self.current_turn = 'Black' if self.current_turn == 'Red' else 'Red'
        self.status_message = f"It's {self.current_turn}'s turn."
        self._check_game_over()

    def _get_player_pieces(self, color, board = None):
        """Returns a list of all pieces belonging to a color."""

        if board is None:
            board = self.board


        pieces = []
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    def _check_game_over(self):
        """Checks if a player has won."""
        
        # Check if one side has captured all pieces
        if self.taken_pieces['Red'] == 12:
            self.status_message = "Black Wins!"
            self.game_over = True
            return
        if self.taken_pieces['Black'] == 12:
            self.status_message = "Red Wins!"
            self.game_over = True
            return
        
        # Check if the current player has no valid moves (and is not forced to jump)
        current_player_pieces = self._get_player_pieces(self.current_turn)
        has_valid_move = False
        for piece in current_player_pieces:
            if self.get_valid_moves(piece):
                has_valid_move = True
                break
        
        if not has_valid_move:
            winner = 'Black' if self.current_turn == 'Red' else 'Red'
            self.status_message = f"Game Over! {self.current_turn} has no legal moves.\n{winner} wins!"
            self.game_over = True

    def _get_all_legal_movesAI(self, color, board = None):

        if board is None:
            board = self.board


        """Returns a list of all legal moves (piece, target, captured_piece) for a given color."""
        all_moves = []
        player_pieces = self._get_player_pieces(color, board)
        

        





        # Check for mandatory jumps first (standard checkers rule)
        all_jumps = []
        for piece in player_pieces:
            jumps = self._check_jump_moves(piece, True, board=board)
            for target_rc, captured_piece in jumps.items():
                # Store as: (piece_rc, target_rc, captured_piece)
                if (captured_piece.king):
                    score = 2
                else:
                    score = 1

                all_jumps.append(((piece.row, piece.col), target_rc, captured_piece, score))

        if all_jumps:
            # If jumps are available, only return jumps
            return all_jumps

        # If no jumps, check for simple moves
        for piece in player_pieces:
            simple_moves = self.get_valid_moves(piece,board)
            for target_rc, captured_piece in simple_moves.items():
                # captured_piece will be None for simple moves
                score = 0
                all_moves.append(((piece.row, piece.col), target_rc, captured_piece, score))
                
        return all_moves
    


    def eval_score(self, board=None):

        if board is None:
            board = self.board


        score = 0

        for r in range (8):
            for c in range(8):
                piece = board[r][c]
                if piece:
                    val = 1

                    if piece.king:
                        val = 2
                
                    if piece.color == 'Black':
                        score+= val
                    else:
                        score -= val
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == 'Black':
                    # check if Red can jump it
                    threats = self._check_jump_moves(piece, board)
                    if threats:
                        score -= 2
                
            
        return score

    



    def minmax(self,board,depth,isBlack):
        
        


        if depth == 0:
            return self.eval_score(board), None

        color = 'Black' if isBlack else 'Red'
        
        valid_moves = self._get_all_legal_movesAI(color, board)


        if not valid_moves:
            return (self.eval_score(board),None)
            
        


        best_move = None
        
        if (isBlack):
            max_val = -math.inf

            for move in valid_moves:
                
                new_board = copy.deepcopy(board)
                #new_board.move_piece(move[0],move[1],move[2])


                p_r, p_c = move[0]
                t_r, t_c = move[1]
                captured_piece = move[2]

                # copy board already created above
                piece = new_board[p_r][p_c]
                if not piece:
                    continue

                new_board[p_r][p_c] = None
                new_board[t_r][t_c] = piece
                piece.row, piece.col = t_r, t_c

                if captured_piece:
                    cr, cc = captured_piece.row, captured_piece.col
                    new_board[cr][cc] = None

                piece_copy = new_board[t_r][t_c]
                
                
                val, _ = self.minmax(new_board, depth - 1, False)

                

                if val > max_val:
                    max_val = val
                    best_move = move
                    print("max val"+str(max_val))

            return max_val, best_move
        
        else:
            min_val = math.inf

            for move in valid_moves:
                new_board = copy.deepcopy(board)
                ##new_board.move_piece(move[0],move[1],move[2])

                p_r, p_c = move[0]
                t_r, t_c = move[1]
                captured_piece = move[2]

                # copy board already created above
                piece = new_board[p_r][p_c]
                if not piece:
                    continue

                new_board[p_r][p_c] = None
                new_board[t_r][t_c] = piece
                piece.row, piece.col = t_r, t_c

                


                if captured_piece:
                    cr, cc = captured_piece.row, captured_piece.col
                    new_board[cr][cc] = None



                piece_copy = new_board[t_r][t_c]
                
                val, _ = self.minmax(new_board, depth - 1, True)
                

                if val < min_val:
                    min_val = val
                    best_move = move

                    print("min val"+str(min_val))
            return min_val, best_move


        





    def runAI(self):
        if self.current_turn == "Black" and self.game_over == False:
            


            depth = 5 #dpeth for algoritm <----- bigger takes longer + makes AI better (supoosedley) DON'T SET TO HIGH
            
            
            
            best_val, best_move = self.minmax(self.board, depth, True)

            print("best val="+str(best_val))

            if best_move:
                piece_rc, target_rc, captured_piece, who_the_hell_cares = best_move
                self.move_piece(piece_rc,target_rc, captured_piece)

            else:

                print("uh oh! no valid moves :()")
                self._check_game_over()
            
            
            
            
            
            
            
            
            
            
            
            
            
            '''if legal_moves:
                best_move = None 
                for move in legal_moves:
                
                    score = move[3]
                    val = SearchAlgorithm.minimax(self,move[0],2,True, True)
                    if (val+score > best_val):
                        best_val = val + score
                        best_move = move

                if best_move:   
                    self.move_piece(best_move[0],best_move[1],best_move[2])
                else:
                    legal_moves = self._get_all_legal_movesAI("Black")
                    i = random.choice(legal_moves)
                    self.move_piece(i[0],i[1],i[2])


            else:
                # No legal moves, game over is handled in _check_game_over
                print("print no moves")
                self._check_game_over()
                pass '''

    # --- Event Handling ---
    
    def handle_event(self, event):
        # 1. Handle back button click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return 'main_menu'

        if self.game_over:
            return 'game_over'
        
        # #stops mouse input for the User
        # if self.mode != "PvP" and self.current_turn == "Black":
        #     return None

        # 2. Handle game board click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r, c = self._get_board_coords(event.pos)

            if r is not None:
                clicked_piece = self.board[r][c]
                target_rc = (r, c)
                
                if self.selected_piece:
                    # A piece is already selected, check if click is a valid move
                    if target_rc in self.valid_moves:
                        captured_piece = self.valid_moves[target_rc]
                        p_r, p_c = self.selected_piece
                        self.move_piece(self.selected_piece, target_rc, captured_piece)
                        
                    # Clicked the selected piece again to deselect
                    elif target_rc == self.selected_piece:
                        self.selected_piece = None
                        self.valid_moves = {}
                        self.status_message = ""
                    
                    # Clicked another piece (only allow selection change if no mandatory jump is active)
                    elif clicked_piece and clicked_piece.color == self.current_turn and not self.valid_moves:
                        self.selected_piece = target_rc
                        self.valid_moves = self.get_valid_moves(clicked_piece)
                        
                else:
                    # No piece selected, try to select one
                    if clicked_piece and clicked_piece.color == self.current_turn:
                        self.selected_piece = target_rc
                        self.valid_moves = self.get_valid_moves(clicked_piece)
                        
                        # Check for mandatory jump
                        has_jumps = self._check_jump_moves(clicked_piece)
                        if has_jumps:
                            self.status_message = f"{self.current_turn} must jump!"
                        elif not self.valid_moves:
                             self.status_message = f"{self.current_turn}'s piece at ({r},{c}) has no moves."
            #Check for AI
            #if it's AI turn and AI is enabled then do minMax
    def update(self):
        if self.mode == "PvAI" and self.current_turn == "Black":
            if not self.AITimer.running:
                self.AITimer.start()
            if self.AITimer.is_finished():
                self.AITimer.stop()
                self.runAI()
        
    # --- Drawing Methods ---
    
    def draw_board(self):
        """Draws the checkered pattern of the board."""
        board_rect = pygame.Rect(self.OFFSET_X, self.OFFSET_Y, self.SQUARE_SIZE*9, self.SQUARE_SIZE*9)
        self.screen.blit(self.board_image, board_rect.topleft)

        # for r in range(8):
        #     for c in range(8):
        #         # Use dark brown for playable squares, light brown for non-playable
        #         color = self.DARK_BROWN if (r + c) % 2 != 0 else self.LIGHT_BROWN
                
        #         rect = pygame.Rect(
        #             self.OFFSET_X + c * self.SQUARE_SIZE,
        #             self.OFFSET_Y + r * self.SQUARE_SIZE,
        #             self.SQUARE_SIZE,
        #             self.SQUARE_SIZE
        #         )
        #         pygame.draw.rect(self.screen, color, rect)

    def draw_pieces(self):
        """Draws all pieces currently on the board using images."""
        if not self.images_loaded:
            # Fallback (optional: could re-implement basic color circles if images fail)
            return

        piece_size = self.red_piece_image.get_width() # Use the scaled size
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece:
                    center_x, center_y = self._get_pixel_coords(r, c)
                    # Determine which image to use
                    if piece.color == 'Red':
                        piece_image = self.red_king_image if piece.king else self.red_piece_image
                    else: # Black
                        piece_image = self.black_king_image if piece.king else self.black_piece_image
                        
                    # Calculate the top-left corner for blitting
                    top_left_x = center_x - (piece_size // 2)
                    top_left_y = center_y - (piece_size // 2)

                    # Blit the image onto the screen
                    self.screen.blit(piece_image, (top_left_x, top_left_y))

    def draw_indicators(self):
        """Draws selection highlight and valid move indicators."""
        
        # Draw selected piece highlight
        if self.selected_piece:
            r, c = self.selected_piece
            # Highlight the square
            rect = pygame.Rect(
                self.OFFSET_X + c * self.SQUARE_SIZE,
                self.OFFSET_Y + r * self.SQUARE_SIZE,
                self.SQUARE_SIZE,
                self.SQUARE_SIZE
            )
            pygame.draw.rect(self.screen, self.SELECTION_HIGHLIGHT, rect, 5) # Draw blue border

        # Draw valid move indicators
        if self.valid_moves:
            for r, c in self.valid_moves.keys():
                center_x, center_y = self._get_pixel_coords(r, c)
                # Draw a transparent green dot or circle on the valid square
                pygame.draw.circle(self.screen, self.MOVE_HIGHLIGHT, (center_x, center_y), self.SQUARE_SIZE // 4)

    def draw_ui_elements(self):
        """Draws the status message, turn indicator, and taken pieces counter (now with circles)."""
        
        # --- Back Button ---
        pygame.draw.rect(self.screen, (60, 60, 60), self.button_rect, border_radius=8)
        self.screen.blit(self.button_text, self.text_rect)
        
        # --- Status / Turn Indicator ---
        # Positioned above the board
        status_y = self.OFFSET_Y - 30
        turn_color = (200, 0, 0) if self.current_turn == 'Red' else (50, 50, 50)
        
        # Draw a bold turn message
        turn_message = f"Turn: {self.current_turn}"
        turn_render = self.big_font.render(turn_message, True, turn_color)
        turn_rect = turn_render.get_rect(center=(self.OFFSET_X + (self.BOARD_SIZE//2), status_y))
        self.screen.blit(turn_render, turn_rect)

        # Draw the main game status message (below the turn)
        msg_render = self.small_font.render("Debug Info: "+self.status_message, True, (0, 0, 0))
        msg_rect = msg_render.get_rect(center=(self.OFFSET_X + (self.BOARD_SIZE//2), status_y + 20))
        self.screen.blit(msg_render, msg_rect)

        # --- Taken Pieces Counter (Circles) ---
        counter_x_start = self.OFFSET_X + self.BOARD_SIZE + 10
        counter_y_start = self.OFFSET_Y + self.BOARD_SIZE/2 - 100
        circle_radius = 25
        padding = 70
        
        # Title
        title_render = self.small_font.render("Pieces Taken:", True, (0, 0, 0))
        self.screen.blit(title_render, (counter_x_start, counter_y_start))
        
        # --- Draw Red Taken Circle ---
        red_center = (counter_x_start + circle_radius, counter_y_start + padding)
        # The color of the piece itself (Red)
        pygame.draw.circle(self.screen, (200, 0, 0), red_center, circle_radius) 
        # Draw the count in white text on the red circle
        red_count_text = self.big_font.render(str(self.taken_pieces['Red']), True, (255, 255, 255))
        red_count_rect = red_count_text.get_rect(center=red_center)
        self.screen.blit(red_count_text, red_count_rect)

        # Draw a label next to the circle
        red_label = self.small_font.render("Red", True, (0, 0, 0))
        self.screen.blit(red_label, (red_center[0] + circle_radius + 10, red_center[1] - red_label.get_height() // 2))

        # --- Draw Black Taken Circle ---
        black_center = (counter_x_start + circle_radius, counter_y_start + padding + 2 * circle_radius + 10)
        # The color of the piece itself (Black/Dark Grey)
        pygame.draw.circle(self.screen, (50, 50, 50), black_center, circle_radius)
        # Draw the count in white text on the black circle
        black_count_text = self.big_font.render(str(self.taken_pieces['Black']), True, (255, 255, 255))
        black_count_rect = black_count_text.get_rect(center=black_center)
        self.screen.blit(black_count_text, black_count_rect)
        
        # Draw a label next to the circle
        black_label = self.small_font.render("Black", True, (0, 0, 0))
        self.screen.blit(black_label, (black_center[0] + circle_radius + 10, black_center[1] - black_label.get_height() // 2))

    def draw(self):
        # Background
        self.screen.fill((128, 128, 192))
        
        # Game Elements
        self.draw_board()
        self.draw_pieces()
        self.draw_indicators()
        
        # UI Elements
        self.draw_ui_elements()


# --- Minimal Main Menu (to make the script runnable) ---
class MainMenu(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 40)
        self.title_text = self.font.render("Pygame Checkers", True, (0, 0, 0))
        
        # Play Button Setup
        self.button_rect = pygame.Rect(0, 0, 250, 70)
        self.button_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 50)
        self.button_text = self.small_font.render("Start Game", True, (255, 255, 255))
        self.text_rect = self.button_text.get_rect(center=self.button_rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return 'game'
        return None

    def draw(self):
        self.screen.fill((255, 255, 255)) # White background
        
        # Title
        title_rect = self.title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(self.title_text, title_rect)
        
        # Button
        pygame.draw.rect(self.screen, (0, 100, 200), self.button_rect, border_radius=10)
        self.screen.blit(self.button_text, self.text_rect)

# --- Main Game Loop (for local execution) ---
def main():
    pygame.init()
    # Set window size (optimized for this game)
    screen_width = 800
    screen_height = 650
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Two-Player Checkers")
    clock = pygame.time.Clock()

    # Scene management
    scenes = {
        'main_menu': MainMenu(screen),
        'game': GameScene(screen)
    }
    current_scene = scenes['main_menu']

    # Initial status message for the GameScene
    scenes['game'].status_message = "Red starts first! Select a piece to begin."
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle event and check for scene switch signal
            next_scene_name = current_scene.handle_event(event)
            if next_scene_name and next_scene_name in scenes:
                # If we switch to 'game', reset the board
                if next_scene_name == 'game':
                    scenes['game'] = GameScene(screen) # Reset game state
                    scenes['game'].status_message = "Red starts first! Select a piece to begin."
                current_scene = scenes[next_scene_name]

        current_scene.update()
        current_scene.draw()
        
        pygame.display.flip()
        clock.tick(60) # Limit frame rate to 60 FPS

if __name__ == '__main__':
    # This block ensures the script runs when executed directly
    main()
