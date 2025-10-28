import math
from . import GameScene
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
def check_best_move(game_scene,legal_moves):
    best_val = -math.inf
    best_move = None
    for move in legal_moves:
        if (move[3] > best_val):
            best_move = move
            best_val = minimax(game_scene,move,3,True,True)
    return best_move, best_val


def minimax(game_scene,move, depth, maximizing_player, first_loop):
    if depth == 0:
        return 0
    if maximizing_player:
        max_val = -math.inf
        
        print("move 0",move[0])
        '''if first_loop:
            legal_moves,score = game_scene.get_valid_movesAI(move[0])
        else: '''
        legal_moves,score = game_scene.get_valid_movesAI(move)
        for child_move in legal_moves:
            print("yes", child_move)
            val = minimax(game_scene,child_move, depth-1, True, False)
            if (val > max_val):
                max_val = val + score
        return max_val
    '''
    else:
        min_val = math.inf
        legal_moves,score = GameScene.GameScene.get_valid_movesAI(move[1]) 
        for child_move in legal_moves:
            val = minimax(child_move, depth-1, True)
            if (val < min_val):
                min_val = score - val

    return min_val
    '''
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