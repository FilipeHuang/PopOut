import random
from game import PopOutState
from mcts import mcts_search
from id3_popout import get_id3_move
#tournament among Random, MCTS and ID3 agents

def random_move(state): return random.choice(state.get_legal_moves())
#play the games without the need to print board states
def play_silent_game(p1_type, p2_type, p1_data=None, p2_data=None):
    state = PopOutState()
    while not state.is_terminal():
        moves = state.get_legal_moves()
        current_type = p1_type if state.player == 1 else p2_type
        current_data = p1_data if state.player == 1 else p2_data
        if current_type == 'mcts':
            c_val = current_data if current_data is not None else 1.41
            move = mcts_search(state, iterations=1000, c=c_val)
        elif current_type == 'id3':
            if current_data:
                tree, features = current_data
                move = get_id3_move(state, tree, features)
            else: move = random.choice(moves)
            if not move or move not in moves: move = random.choice(moves)
        else: move = random_move(state)
        state = state.make_move(move)
    return state.get_winner()
