import csv
from game import PopOutState
from mcts import mcts_search

def state_to_features(state):
    """
    Converte o estado do jogo numa lista de 43 features:
    - 42 valores do tabuleiro (6x7): 0=vazio, 1=X, 2=O
    - 1 valor para o jogador atual (1 ou 2)
    """
    flat = [cell for row in state.board for cell in row]
    flat.append(state.player)
    return flat

def generate_dataset(num_games=1000, iterations=2000, output_file="dataset.csv"):
    header = [f"cell_{r}_{c}" for r in range(6) for c in range(7)] + ["player", "move"]
    total = 0
    seen_states = set()  # para evitar duplicados

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for game_num in range(num_games):
            state = PopOutState()
            print(f"Game {game_num + 1}/{num_games} | Exemplos guardados: {total}")

            while not state.is_terminal():
                best_move = mcts_search(state, iterations=iterations)

                features = state_to_features(state)
                state_key = tuple(features)

                # Só guarda se este estado ainda não foi visto
                if state_key not in seen_states:
                    seen_states.add(state_key)
                    col, action = best_move
                    label = f"{col}_{action}"
                    writer.writerow(features + [label])
                    f.flush()  # guarda imediatamente no disco
                    total += 1

                state = state.make_move(best_move)

    print(f"\nDataset gerado com sucesso!")
    print(f"Total de exemplos únicos: {total}")
    print(f"Ficheiro guardado em: '{output_file}'")

if __name__ == "__main__":
    generate_dataset(num_games=1000, iterations=2000, output_file="dataset.csv")