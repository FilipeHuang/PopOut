import math
import random

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state          # PopOutState
        self.parent = parent        # nó pai
        self.move = move            # jogada que gerou este nó
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_legal_moves()

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, c=1.41):
        # Fórmula UCB1
        return max(self.children, key=lambda n: 
            n.wins / n.visits + c * math.sqrt(math.log(self.visits) / n.visits)
        )

    def expand(self):
        move = self.untried_moves.pop()
        new_state = self.state.make_move(move)
        child = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child)
        return child

    def rollout(self):
        # Simulação aleatória até ao fim
        state = self.state.copy()
        while not state.is_terminal():
            moves = state.get_legal_moves()
            state = state.make_move(random.choice(moves))
        return state.get_winner()

    def backpropagate(self, result, ai_player):
        self.visits += 1
        if result == ai_player:
            self.wins += 1
        elif result == 'draw':
            self.wins += 0.5
        if self.parent:
            self.parent.backpropagate(result, ai_player)


def mcts_search(state, iterations=1000):
    """
    Recebe um PopOutState e devolve a melhor jogada.
    """
    ai_player = state.player
    root = MCTSNode(state)

    for _ in range(iterations):
        # 1. Selection
        node = root
        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        # 2. Expansion
        if not node.is_fully_expanded():
            node = node.expand()

        # 3. Simulation
        result = node.rollout()

        # 4. Backpropagation
        node.backpropagate(result, ai_player)

    # Devolve a jogada do filho com mais visitas
    best = max(root.children, key=lambda n: n.visits)
    return best.move