import os
import time
from game import PopOutState
from mcts import mcts_search
from id3_popout import train_tree, get_id3_move
from arena import play_silent_game

def print_board(state):
    print("\n      0   1   2   3   4   5   6")
    print("   " + "─" * 29)
    for row in state.board[::-1]:
        line = " │ ".join(["X" if x == 1 else "O" if x == 2 else "-" for x in row])
        print("   │ " + line + " │")
    print("   " + "─" * 29)
    if not state.is_terminal(): print(f"   It is now {'X' if state.player == 1 else 'O'}'s turn.\n")

def painel_torneio():
    while True:
        print("\n" + "="*35)
        print("   MODO TORNEIO / ARENA")
        print("="*35)
        print("  (1) MCTS vs Random")
        print("  (2) MCTS vs ID3")
        print("  (3) ID3 vs Random")
        print("  (0) Voltar ao Menu Principal")
        print("="*35)
        
        escolha = input("\nEscolhe o confronto (0/1/2/3): ").strip()
        
        if escolha == '0':
            break
            
        if escolha not in ['1', '2', '3']:
            print("Opcao invalida.")
            continue

        try:
            games = int(input("Numero de jogos (default:20): ").strip() or "20")
        except ValueError:
            print("Numero invalido, a assumir 20.")
            games = 20

        tree, features = None, None
        if escolha in ['2', '3']:
            print("\nA carregar dataset e treinar ID3...")
            tree, features = train_tree(max_depth=12, min_samples=5)
            if not tree:
                print("Erro: dataset.csv nao encontrado!")
                continue

        if escolha == '1': p1, p2 = 'mcts', 'random'
        elif escolha == '2': p1, p2 = 'mcts', 'id3'
        else: p1, p2 = 'id3', 'random'

        print(f"\nA iniciar {games} jogos: {p1.upper()} vs {p2.upper()}\n")
        
        results = {p1: 0, p2: 0, 'draw': 0}
        start_time = time.time()
        
        for i in range(games):
            if i % 2 == 0:
                winner = play_silent_game(p1, p2, tree, features)
                if winner == 1: results[p1] += 1
                elif winner == 2: results[p2] += 1
                else: results['draw'] += 1
            else:
                winner = play_silent_game(p2, p1, tree, features)
                if winner == 2: results[p1] += 1
                elif winner == 1: results[p2] += 1
                else: results['draw'] += 1
                
            print(f"\rProgresso: Jogo {i+1}/{games}", end="", flush=True)
            
        elapsed = time.time() - start_time
        
        print("\n\n" + "="*35)
        print("   RELATORIO DO TORNEIO")
        print("="*35)
        print(f"  Vitorias {p1.upper()}: {results[p1]}")
        print(f"  Vitorias {p2.upper()}: {results[p2]}")
        print(f"  Empates:     {results['draw']}")
        print(f"  Win Rate {p1.upper()}: {(results[p1]/games)*100:.1f}%")
        print(f"  Tempo Total: {elapsed:.1f}s")
        print("="*35)
        input("\nPressiona ENTER para voltar...")

def play_game():
    while True:
        state = PopOutState()
        
        print("\n" + "=" * 35)
        print("          POPOUT GAME")
        print("=" * 35)
        print("Rules: Drop or Pop your pieces.\nFirst to 4 in a row wins!")
        print("Type 'put' or 'pop' when asked.\n")

        ai_mcts_player = None
        ai_id3_player = None
        c_value = 1.41

        while True:
            print("\nMain Menu:")
            print("(1) Human vs Human")
            print("(2) Human vs AI")
            print("(3) AI (MCTS) vs AI (ID3)")
            print("(4) Arena / Torneio")
            print("(5) Exit")
            mode = input("Choose mode (1/2/3/4/5): ").strip()
            if mode in ['1', '2', '3', '4', '5']:
                break
            print("Please enter 1, 2, 3, 4, or 5.")

        if mode == '5':
            print("Exiting game. Goodbye!")
            break
            
        if mode == '4':
            painel_torneio()
            continue

        if mode == '2':
            while True:
                print("\nChoose AI opponent:")
                print("(1) MCTS")
                print("(2) ID3")
                ai_choice = input("Choice (1/2): ").strip()
                if ai_choice in ['1', '2']:
                    break
                print("Please enter 1 or 2.")

            if ai_choice == '1':
                while True:
                    try:
                        c_input = input("Enter exploration parameter 'c' for MCTS (default 1.41): ").strip()
                        c_value = float(c_input) if c_input else 1.41
                        break
                    except ValueError:
                        print("Please enter a valid number.")

            while True:
                symbol = input("Do you want to play as 'X' (first) or 'O' (second)? (X/O): ").strip().upper()
                if symbol in ['X', 'O']:
                    break
                print("Please enter X or O.")
                
            if symbol == 'X':
                if ai_choice == '1': ai_mcts_player = 2
                else: ai_id3_player = 2
            else:
                if ai_choice == '1': ai_mcts_player = 1
                else: ai_id3_player = 1

        elif mode == '3':
            while True:
                try:
                    c_input = input("Enter exploration parameter 'c' for MCTS (default 1.41): ").strip()
                    c_value = float(c_input) if c_input else 1.41
                    break
                except ValueError:
                    print("Please enter a valid number.")

            while True:
                first = input("Who plays first as 'X'? (1) MCTS or (2) ID3: ").strip()
                if first in ['1', '2']:
                    break
                print("Please enter 1 or 2.")
                
            if first == '1':
                ai_mcts_player = 1
                ai_id3_player = 2
            else:
                ai_id3_player = 1
                ai_mcts_player = 2

        tree, features = None, None
        if ai_id3_player is not None:
            print("\nLoading dataset and training ID3 Tree... Please wait.")
            tree, features = train_tree(max_depth=10)
            if not tree:
                print("Warning: dataset.csv not found. ID3 will play randomly.")

        print_board(state)

        while not state.is_terminal():
            player_symbol = "X" if state.player == 1 else "O"
            print(f"\n{'=' * 35}")
            print(f"            {player_symbol}'S TURN")
            print(f"{'=' * 35}")

            moves = state.get_legal_moves()

            if ai_mcts_player and state.player == ai_mcts_player:
                print("MCTS AI is thinking...")
                move = mcts_search(state, iterations=1000, c=c_value)
                print(f"MCTS played: column {move[0]}, {move[1]}")
                state = state.make_move(move)
                print_board(state)
                continue

            if ai_id3_player and state.player == ai_id3_player:
                print("ID3 AI is thinking...")
                if tree:
                    move = get_id3_move(state, tree, features)
                    if move not in moves:
                        move = moves[0]
                else:
                    import random
                    move = random.choice(moves)
                
                print(f"ID3 played: column {move[0]}, {move[1]}")
                state = state.make_move(move)
                print_board(state)
                continue

            print(f"Legal moves: {moves}")

            is_draw = any(m[1]=='draw' for m in moves)

            if is_draw: text = "\nEnter column (0-6) or 'd' for DRAW: "
            else: text = "\nEnter column (0-6): "

            while True:
                try:
                    choice = input(text)
                    if choice=='d':
                        if is_draw:
                            state = state.make_move((-1, 'draw'))
                            break
                        else: continue
                    col = int(choice)
                    if not 0 <= col <= 6:
                        print("Column must be between 0 and 6!")
                        continue

                    can_put = any(state.board[r][col] == 0 for r in range(6))
                    can_pop = (state.board[0][col] == state.player)

                    if not can_put and not can_pop:
                        print("No moves possible in this column.")
                        continue
                    if can_put and can_pop:
                        ask = input("Enter action ('+' for put or '-' for pop): ").strip().lower()
                        if ask not in ['+', '-']:
                            print("Please type '+' or '-'.")
                            continue
                        action = 'pop' if ask == '-' else 'put'
                    elif can_put:
                        print(f"Only 'put' is possible in column {col}.")
                        action = 'put'
                    else:
                        print(f"Only 'pop' is possible in column {col}.")
                        action = 'pop'
                    
                    move = (col, action)
                    if move in moves:
                        state = state.make_move(move)
                        break
                    else: print("This move is not legal.")
                except ValueError: print("Please enter a valid number for column.")
            
            print_board(state)

        print("\n" + "=" * 35)
        winner = state.get_winner()
        if winner == "draw": print("             GAME DRAW!")
        elif winner == 1: print("             'X' WINS!")
        elif winner == 2: print("             'O' WINS!")
        print("=" * 35)
