from game import PopOutState
from utils import print_board

def play_game():
    state = PopOutState()
    
    print("\n" + "=" * 35)
    print("           POPOUT GAME")
    print("=" * 35)
    print("Rules: Drop or Pop your pieces.\nFirst to 4 in a row wins!")
    print("Type 'put' or 'pop' when asked.\n")    
    
    print_board(state)

    while not state.is_terminal():
        player_symbol = "X" if state.player == 1 else "O"
        print(f"\n{'=' * 35}")
        print(f"            {player_symbol}'S TURN")
        print(f"{'=' * 35}")
        
        moves = state.get_legal_moves()
        print(f"Legal moves: {moves}")
        
        while True:
            try:
                col = int(input("\nEnter column (0-6): "))
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
                    is_pop = (ask == '-') #return bool
                elif can_put:
                    print(f"Only 'put' is possible in column {col}.")
                    is_pop = False
                else:   #'pop' as the only move
                    print(f"Only 'pop' is possible in column {col}.")
                    is_pop = True
                
                move = (col, 'pop' if is_pop else 'put')
                if move in moves:
                    state = state.make_move(col, is_pop)
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