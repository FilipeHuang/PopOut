from game import PopOutState
from mcts import mcts_search

def print_board(state):
    print("\n     0   1   2   3   4   5   6")
    print("   " + "─" * 29)
    for row in state.board[::-1]:        # Top row first
        line = " │ ".join(["X" if x == 1 else "O" if x == 2 else "-" for x in row])
        print("   │ " + line + " │")
    print("   " + "─" * 29)
    if not state.is_terminal(): print(f"   It is now {'X' if state.player == 1 else 'O'}'s turn.\n")

def play_game():
    state = PopOutState()
    
    print("\n" + "=" * 35)
    print("           POPOUT GAME")
    print("=" * 35)
    print("Rules: Drop or Pop your pieces.\nFirst to 4 in a row wins!")
    print("Type 'put' or 'pop' when asked.\n")

    # Escolha do modo de jogo
    while True:
        mode = input("Game mode: (1) Human vs Human  (2) Human vs AI: ").strip()
        if mode in ['1', '2']:
            break
        print("Please enter 1 or 2.")
    ai_player = 2 if mode == '2' else None  # IA joga como 'O' (jogador 2)

    print_board(state)

    while not state.is_terminal():
        player_symbol = "X" if state.player == 1 else "O"
        print(f"\n{'=' * 35}")
        print(f"            {player_symbol}'S TURN")
        print(f"{'=' * 35}")

        # Turno da IA
        if ai_player and state.player == ai_player:
            print("AI is thinking...")
            move = mcts_search(state, iterations=1000)
            print(f"AI played: column {move[0]}, {move[1]}")
            state = state.make_move(move)
            print_board(state)
            continue

        moves = state.get_legal_moves()
        print(f"Legal moves: {moves}")

        #rule 2: give option to draw if board is full
        is_draw = any(m[1]=='draw' for m in moves)  #bool

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
                    #ask if both exist
                    ask = input("Enter action ('+' for put or '-' for pop): ").strip().lower()
                    if ask not in ['+', '-']:
                        print("Please type '+' or '-'.")
                        continue
                    action = 'pop' if ask == '-' else 'put'
                elif can_put:
                    print(f"Only 'put' is possible in column {col}.")
                    action = 'put'
                else:   #'pop' as the only move
                    print(f"Only 'pop' is possible in column {col}.")
                    action = 'pop'
                
                move = (col, action)
                if move in moves:
                    state = state.make_move(move)
                    break
                else: print("This move is not legal.")
            except ValueError: print("Please enter a valid number for column.")
        
        print_board(state)

    #Game Over
    print("\n" + "=" * 35)
    winner = state.get_winner()
    if winner == "draw": print("             GAME DRAW!")
    elif winner == 1: print("             'X' WINS!")
    elif winner == 2: print("             'O' WINS!")
    print("=" * 35)