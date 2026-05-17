import csv
from game import PopOutState
from mcts import mcts_search

#generate more strategical features than just raw 42-cell-feature

def count_consecutive(board, player, length):
    #counting the number of sequences of exactly consecutive length
    count = 0
    rows, cols = 6, 7
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(rows):
        for c in range(cols):
            for dr, dc in directions:
                seq = 0
                #check length positions in the current direction
                for k in range(length):
                    nr, nc = r + k * dr, c + k * dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player: seq += 1
                    else: break
                if seq == length: count += 1
    return count
#returns the current fill height of a given column
def col_height(board, col): return sum(1 for r in range(6) if board[r][col] != 0)
#count pieces occupied by each player in central columns(2, 3 and 4)
def center_control(board, player): return sum(board[r][c] == player for r in range(6) for c in [2, 3, 4])
def threats(board, player, length=3):
    #counts open threats
    #sequences of exactly length pieces of player that have at least one empty cell adjacent
    count = 0
    rows, cols = 6, 7
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(rows):
        for c in range(cols):
            for dr, dc in directions:
                seq = 0
                empties = 0
                for k in range(length + 1):
                    nr, nc = r + k * dr, c + k * dc
                    if not (0 <= nr < rows and 0 <= nc < cols): break
                    if board[nr][nc] == player: seq += 1
                    elif board[nr][nc] == 0: empties += 1
                    else: break
                if seq == length and empties >= 1: count += 1
    return count
#see if any col can pop
def poppable_pieces(board, player): return sum(1 for c in range(7) if board[0][c] == player)

def state_to_features(state):
    #transforming the values at a certain state to features
    board = state.board
    p = state.player
    opp = 3 - p

    feats = {}

    cc_me = center_control(board, p)
    cc_opp = center_control(board, opp)
    feats["center_adv"] = _bin3(cc_me - cc_opp, -9, 9)

    feats["threats_me_3"]  = min(count_consecutive(board, p, 3), 4)
    feats["threats_opp_3"] = min(count_consecutive(board, opp, 3), 4)

    feats["open_threats_me"]  = min(threats(board, p), 4)
    feats["open_threats_opp"] = min(threats(board, opp), 4)

    feats["pairs_me"]  = min(count_consecutive(board, p, 2), 6)
    feats["pairs_opp"] = min(count_consecutive(board, opp, 2), 6)

    feats["pop_me"]  = poppable_pieces(board, p)
    feats["pop_opp"] = poppable_pieces(board, opp)

    for c in range(7):
        h = col_height(board, c)
        feats[f"col_h_{c}"] = _bin3(h, 0, 6)
    for c in range(7):
        my_pieces = sum(1 for r in range(6) if board[r][c] == p)
        feats[f"my_col_{c}"] = min(my_pieces, 4)
    for c in range(7):
        opp_pieces = sum(1 for r in range(6) if board[r][c] == opp)
        feats[f"opp_col_{c}"] = min(opp_pieces, 4)
    total_pieces = sum(board[r][c] != 0 for r in range(6) for c in range(7))
    
    if total_pieces <= 8: feats["phase"] = "early"
    elif total_pieces <= 24: feats["phase"] = "mid"
    else: feats["phase"] = "late"

    left  = sum(board[r][c] == p for r in range(6) for c in range(3))
    right = sum(board[r][c] == p for r in range(6) for c in range(4, 7))
    feats["lr_balance"] = _bin3(left - right, -6, 6)

    return feats

def _bin3(value, lo, hi):
    #discretises a continuous numeric value into three categories: "low", "mid", "high"
    third = (hi - lo) / 3
    if value < lo + third: return "low"
    elif value < lo + 2 * third: return "mid"
    else: return "high"

def generate_dataset(num_games=1000, iterations=2000, output_file="dataset.csv"):
    sample = state_to_features(PopOutState())
    header = list(sample.keys()) + ["move"]

    total = 0
    seen_states = set()

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for game_num in range(num_games):
            state = PopOutState()
            print(f"Game {game_num + 1}/{num_games} | Exemplos guardados: {total}")

            while not state.is_terminal() :
                best_move = mcts_search(state, iterations=iterations, c=1.41)
                total_pieces = sum(cell != 0 for row in state.board for cell in row)
                if total_pieces >= 2:
                    feats = state_to_features(state)
                    state_key = tuple(sorted(feats.items()))
                    if state_key not in seen_states:
                        seen_states.add(state_key)
                        col, action = best_move
                        label = f"{col}_{action}"
                        row = {**feats, "move": label}
                        writer.writerow(row)
                        f.flush()
                        total += 1
                state = state.make_move(best_move)
    print(f"\nDataset gerado com {total} exemplos únicos.")
    print(f"Ficheiro guardado em: '{output_file}'")

if __name__ == "__main__": generate_dataset(num_games=100, iterations=1000, output_file="dataset.csv")
