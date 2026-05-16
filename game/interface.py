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

def select_difficulty():
    diff_map = {
        '1': 'dataset_facil.csv',
        '2': 'dataset_medio.csv',
        '3': 'dataset_dificil.csv',
        '4': 'dataset_complexo.csv'
    }
    print("\nSelect ID3 Difficulty:")
    print("(1) Easy")
    print("(2) Medium")
    print("(3) Hard")
    print("(4) Complex")
    while True:
        choice = input("Choice (1-4): ").strip()
        if choice in diff_map:
            return diff_map[choice]
        print("Invalid choice. Select 1-4.")

def painel_torneio():
    while True:
        print("\n" + "="*35)
        print("   MODO TORNEIO / ARENA")
        print("="*35)
        print("  (1) MCTS vs Random")
        print("  (2) MCTS vs ID3")
        print("  (3) ID3 vs Random")
        print("  (4) MCTS vs MCTS")
        print("  (5) ID3 vs ID3")
        print("  (0) Voltar ao Menu Principal")
        print("="*35)
        
        escolha = input("\nEscolhe o confronto (0-5): ").strip()
        if escolha == '0': break
        if escolha not in ['1', '2', '3', '4', '5']:
            print("Opcao invalida.")
            continue

        try:
            games = int(input("Numero de jogos: ").strip() or "20")
        except ValueError: games = 20

        p1_type, p2_type = '', ''
        p1_data, p2_data = None, None

        if escolha == '1':
            p1_type, p2_type = 'mcts', 'random'
            p1_data = float(input("Enter 'c' for MCTS (default 1.41): ").strip() or "1.41")
        
        elif escolha == '2':
            p1_type, p2_type = 'mcts', 'id3'
            p1_data = float(input("Enter 'c' for MCTS (default 1.41): ").strip() or "1.41")
            dataset = select_difficulty()
            p2_data = train_tree(max_depth=12, min_samples=5, filepath=dataset)
            
        elif escolha == '3':
            p1_type, p2_type = 'id3', 'random'
            dataset = select_difficulty()
            p1_data = train_tree(max_depth=12, min_samples=5, filepath=dataset)
            
        elif escolha == '4':
            p1_type, p2_type = 'mcts', 'mcts'
            p1_data = float(input("Enter 'c' for MCTS 1 (X): ").strip() or "1.41")
            p2_data = float(input("Enter 'c' for MCTS 2 (O): ").strip() or "1.41")
            
        elif escolha == '5':
            p1_type, p2_type = 'id3', 'id3'
            print("\n--- Setup Player 1 (X) ---")
            ds1 = select_difficulty()
            p1_data = train_tree(max_depth=12, min_samples=5, filepath=ds1)
            print("\n--- Setup Player 2 (O) ---")
            ds2 = select_difficulty()
            p2_data = train_tree(max_depth=12, min_samples=5, filepath=ds2)

        print(f"\nA iniciar {games} jogos: {p1_type.upper()} vs {p2_type.upper()}\n")
        results = {p1_type: 0, p2_type: 0, 'draw': 0}
        if p1_type == p2_type: results = {'p1': 0, 'p2': 0, 'draw': 0}

        start_time = time.time()
        for i in range(games):
            if i % 2 == 0:
                winner = play_silent_game(p1_type, p2_type, p1_data, p2_data)
                if p1_type == p2_type:
                    if winner == 1: results['p1'] += 1
                    elif winner == 2: results['p2'] += 1
                    else: results['draw'] += 1
                else:
                    if winner == 1: results[p1_type] += 1
                    elif winner == 2: results[p2_type] += 1
                    else: results['draw'] += 1
            else:
                # swap data for swapped starting positions
                winner = play_silent_game(p2_type, p1_type, p2_data, p1_data)
                if p1_type == p2_type:
                    if winner == 2: results['p1'] += 1
                    elif winner == 1: results['p2'] += 1
                    else: results['draw'] += 1
                else:
                    if winner == 2: results[p1_type] += 1
                    elif winner == 1: results[p2_type] += 1
                    else: results['draw'] += 1
            print(f"\rProgresso: Jogo {i+1}/{games}", end="", flush=True)

        elapsed = time.time() - start_time
        print(f"\n\nTempo Total: {elapsed:.1f}s")
        if p1_type == p2_type:
            print(f"Vitorias P1: {results['p1']} | Vitorias P2: {results['p2']} | Empates: {results['draw']}")
        else:
            print(f"Vitorias {p1_type.upper()}: {results[p1_type]} | Vitorias {p2_type.upper()}: {results[p2_type]} | Empates: {results['draw']}")
        input("\nPressiona ENTER para voltar...")

def play_game():
    while True:
        state = PopOutState()
        
        print("\n" + "=" * 35)
        print("          POPOUT GAME")
        print("=" * 35)
        print("Rules: Drop or Pop your pieces.\nFirst to 4 in a row wins!")
        print("Type 'put' or 'pop' when asked.\n")

        player_types = {1: 'human', 2: 'human'}
        mcts_c = {1: 1.41, 2: 1.41}
        id3_models = {1: (None, None), 2: (None, None)}

        while True:
            print("\nMain Menu:")
            print("(1) Human vs Human")
            print("(2) Human vs AI")
            print("(3) AI vs AI")
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
                print("(1) MCTS\n(2) ID3")
                ai_choice = input("Choice (1/2): ").strip()
                if ai_choice in ['1', '2']:
                    break
                print("Please enter 1 or 2.")

            while True:
                symbol = input("Do you want to play as 'X' (first) or 'O' (second)? (X/O): ").strip().upper()
                if symbol in ['X', 'O']:
                    break
                print("Please enter X or O.")
                
            ai_p = 2 if symbol == 'X' else 1
            player_types[ai_p] = 'mcts' if ai_choice == '1' else 'id3'
            
            if player_types[ai_p] == 'mcts':
                while True:
                    try:
                        c_input = input("Enter exploration parameter 'c' for MCTS (default 1.41): ").strip()
                        mcts_c[ai_p] = float(c_input) if c_input else 1.41
                        break
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                dataset_file = select_difficulty()
                print(f"\nLoading {dataset_file} and training ID3 Tree... Please wait.")
                tree, features = train_tree(max_depth=5, min_samples=20, filepath=dataset_file)
                if not tree:
                    print(f"Warning: {dataset_file} not found. ID3 will play randomly.")
                id3_models[ai_p] = (tree, features)

        elif mode == '3':
            while True:
                print("\nChoose Player 1 (X):")
                p1_choice = input("(1) MCTS (2) ID3: ").strip()
                if p1_choice in ['1', '2']: break
                print("Please enter 1 or 2.")
                
            while True:
                print("Choose Player 2 (O):")
                p2_choice = input("(1) MCTS (2) ID3: ").strip()
                if p2_choice in ['1', '2']: break
                print("Please enter 1 or 2.")
                
            player_types[1] = 'mcts' if p1_choice == '1' else 'id3'
            player_types[2] = 'mcts' if p2_choice == '1' else 'id3'
            
            for p in [1, 2]:
                p_str = "Player 1 (X)" if p == 1 else "Player 2 (O)"
                print(f"\n--- Configuring {p_str} ({player_types[p].upper()}) ---")
                
                if player_types[p] == 'mcts':
                    while True:
                        try:
                            c_input = input(f"Enter parameter 'c' for MCTS (default 1.41): ").strip()
                            mcts_c[p] = float(c_input) if c_input else 1.41
                            break
                        except ValueError:
                            print("Please enter a valid number.")
                else:
                    dataset_file = select_difficulty()
                    print(f"\nLoading {dataset_file} and training ID3 Tree... Please wait.")
                    tree, features = train_tree(max_depth=5, min_samples=20, filepath=dataset_file)
                    if not tree:
                        print(f"Warning: {dataset_file} not found. ID3 will play randomly.")
                    id3_models[p] = (tree, features)

        print_board(state)

        while not state.is_terminal():
            player_symbol = "X" if state.player == 1 else "O"
            print(f"\n{'=' * 35}")
            print(f"            {player_symbol}'S TURN")
            print(f"{'=' * 35}")

            moves = state.get_legal_moves()
            current_type = player_types[state.player]

            if current_type == 'mcts':
                print("MCTS AI is thinking...")
                c_val = mcts_c[state.player]
                move = mcts_search(state, iterations=1000, c=c_val)
                print(f"MCTS played: column {move[0]}, {move[1]}")
                state = state.make_move(move)
                print_board(state)
                continue

            if current_type == 'id3':
                print("ID3 AI is thinking...")
                tree, features = id3_models[state.player]
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
