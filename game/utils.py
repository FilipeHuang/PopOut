def print_board(state):
    print("\n     0   1   2   3   4   5   6")
    print("   " + "─" * 29)
    for row in state.board[::-1]:        # Top row first
        line = " │ ".join(["X" if x == 1 else "O" if x == 2 else "-" for x in row])
        print("   │ " + line + " │")
    print("   " + "─" * 29)
    print(f"   It is now {'X' if state.player == 1 else 'O'}’s turn.\n")