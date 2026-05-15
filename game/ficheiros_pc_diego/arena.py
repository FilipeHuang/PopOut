import random
from game import PopOutState
from mcts import mcts_search
from id3_popout import get_id3_move

def random_move(state):
    # returns a valid random move
    return random.choice(state.get_legal_moves())

def play_silent_game(p1_type, p2_type, tree=None, features=None):
    # plays a complete game without terminal output and returns the winner
    state = PopOutState()
    
    while not state.is_terminal():
        moves = state.get_legal_moves()
        current_type = p1_type if state.player == 1 else p2_type
        
        if current_type == 'mcts':
            # c=1.41 is the standard uct balance for exploration vs exploitation
            move = mcts_search(state, iterations=1000, c=1.41)
        elif current_type == 'id3':
            move = get_id3_move(state, tree, features)
            if not move or move not in moves:
                move = random.choice(moves)
        else:
            move = random_move(state)
            
        state = state.make_move(move)
        
    return state.get_winner()