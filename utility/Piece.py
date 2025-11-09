# checkers/game/piece.py

class Piece:
    """Represents a single checkers piece."""
    
    def __init__(self, row, col, color):
        # Color should be 'Red' or 'Black'
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        
        # Keep outline_color for king/selection indicator if needed by Board/Scene
        # The color value itself is not essential for logic, but kept for consistency
        self.outline_color = (255, 100, 100) if color == 'Red' else (100, 100, 100)

    def make_king(self):
        """Promotes the piece to a King."""
        self.king = True
        self.outline_color = (255, 255, 0) # King pieces have a yellow/gold outline

    def __repr__(self):
        return f'{self.color[0]}{"K" if self.king else ""}({self.row},{self.col})'