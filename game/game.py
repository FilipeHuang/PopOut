class PopOutState:
    
    def __init__(self):
        self.board = [[0]*7 for _ in range(6)]  #inicialise 6x7 board
        self.player = 1 #current player starting with 1, X=1 and O=2
        self.history = {}   #count the number of time each board state appeared
        self.last_move_pop = False  #inicialise the pop state as false
        self.update_history()   #update to the dictionary to count the starting position
    
    def copy(self):
        new = PopOutState() #create a new empty state
        new.board = [row[:] for row in self.board]  #copy the list
        new.player = self.player    #copy cur player value
        new.history = dict(self.history)    #copy the dict
        new.last_move_pop = self.last_move_pop  #copy the state of pop
        return new  #return the identical cur state
    #tranforming the board state into a key for dict
    def state_hash(self): return tuple(tuple(row) for row in self.board)
    
    def update_history(self):
        '''for mcts'''
        h = self.state_hash()   #get cur key
        self.history[h] = self.history.get(h,0)+1   #increment the nº of the cur state being found
    
    def get_legal_moves(self):
        '''see all possible moves'''
        moves = []
        for c in range(7):
            #can put if col not full
            if any(self.board[r][c]==0 for r in range(6)): moves.append((c, 'put'))
            #if bottom piece belongs to player can pop
            if self.board[0][c] == self.player: moves.append((c, 'pop'))
        return moves
    
    def make_move(self, col: int, is_pop: bool):
        new_state = self.copy()
        new_state.last_move_pop = is_pop
        new_state.player = self.player
        if is_pop:
            #if pop true, all pieces in that col fall one down
            for r in range(5): new_state.board[r][col] = new_state.board[r+1][col]
            new_state.board[5][col] = 0 #empty the top
        else:
            #normal move
            for r in range(6):
                if new_state.board[r][col] == 0:
                    new_state.board[r][col] = new_state.player
                    break
        new_state.player = 3 - self.player  #switch player: 3-1=2 3-2=1
        new_state.update_history()  #record the state
        return new_state
    
    def has_four_in_row(self, player: int):
        board = self.board
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        for r in range(6):
            for c in range(7):
                if board[r][c] != player: continue
                for dr, dc in directions:
                    if 0 <= r+3*dr < 6 and 0 <= c+3*dc < 7:
                        if (board[r][c]==player and
                            board[r+dr][c+dc]==player and
                            board[r+2*dr][c+2*dc]==player and
                            board[r+3*dr][c+3*dc]==player):
                            return True
        return False
    #check if all cells different from 0. it is full
    def is_full(self): return all(all(cell!=0 for cell in row) for row in self.board)

    def get_winner(self):
        #rule: check if the board appeared 3 or more
        if any(count>=3 for count in self.history.values()): return "draw"
        p1 = self.has_four_in_row(1)
        p2 = self.has_four_in_row(2)
        #rule: if both got 4 in a row
        if p1 and p2:
            if self.last_move_pop: return 3-self.player #last played wins
        if p1: return 1
        if p2: return 2
        #rule: full board
        if self.is_full():
            #if can still can pop -> game not ended yet
            if any(m[1]=='pop' for m in self.get_legal_moves()): return None
            return 'draw'
        return None
    def is_terminal(self): return self.get_winner() is not None
    