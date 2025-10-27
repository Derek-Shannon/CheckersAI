import math

''' NOTES!!!!!
uses cords for pieces

already has get_valid_moves, forced to jump
scores go to 12


Ok so idea time
#start at 0 for score (-24 to +24)
#check each pieces valid moves, then checks each valid move for valid move. do this until you reach depth. each piece has possible 4 moves (if kinged)
#picks move that has a biggest number (piece is worth 1 king is worth 2. Nothing is worth 0) (negative values if you lose a piece)
#pruning using alpha-beta (so if left tree > right tree, don't need to check right anymore)


'''
def check_best_move(legal_moves):
    best_val = -math.inf
    best_move = None
    for move in legal_moves:
        if (move[3] > best_val):
            best_move = move
            best_val = move[3]
    return best_move


'''
def minimax(node,depth, maximizing_player):
    if depth == 0:
        return node.value
    
    if maximizing_player: #black
        best_value = -math.inf
        for child in get_children(node):
            value = minimax(child, depth-1, False)
            best_value = max(best_value,value)
        return best_value
    else: #red
        best_value = math.inf
        for child in get_children(node):
            value = minimax(child, depth-1, True)
            best_value = min(best_value,value)
        return best_value
        '''