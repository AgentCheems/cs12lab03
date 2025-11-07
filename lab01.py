import sys

class Grids:
    def __init__(self, n:int)->None:
        self.grid = [[0 for _ in range(n)] for _ in range(n)]
        self.grid[n-1][n-1] = 1
        self.n = n

    def gridprint(self):
        a = self.grid
        n = self.n
        for r in range(n):
            for c in range(n):
                v = a[r][c]
                print(f'{r},{c}: {v}')
            if r != n-1:
                print('---')
        print('====')

    #====helper columns====

    def get_col(self,c:int):
        return [self.grid[r][c] for r in range(len(self.grid))]

    def set_col(self,c:int,col:list[int]):
        for r in range(len(self.grid)):
            self.grid[r][c] = col[r]

    #====movement set====

    def north_move(self):
        n = self.n
        for c in range(n):
            col = self.get_col(c) #transpose function per row
            new_col: list[int] = self.duel_merge(col)
            self.set_col(c, new_col) #transpose back
        self.spawner() #adds 1

    def south_move(self):
        n = self.n
        for c in (range(n)):
            col = self.get_col(c)   
            new_col: list[int] = self.duel_merge(col[::-1])
            self.set_col(c, (new_col[::-1]))
        self.spawner()

    def west_move(self):
        n = self.n
        grid = self.grid
        for r in range(n):
            new_row: list[int] = self.duel_merge(grid[r])
            self.grid[r] = new_row[:]
        self.spawner()

    def east_move(self):
        n = self.n
        grid = self.grid
        for r in range(n):
            new_row: list[int] = self.duel_merge(grid[r][::-1])
            self.grid[r] = list(reversed(new_row))
        self.spawner()

    #====algorithms====

    def duel_merge(self, gridline:list[int])-> list[int]:
        n = len(gridline)
        grid_nonzero = [x for x in gridline if x!=0] #removes zero from list[int]
        res: list[int] = [] #
        i = 0
        while i<len(grid_nonzero):
            if len(grid_nonzero)>i+1 and grid_nonzero[i] == grid_nonzero[i+1]:
                res.append(grid_nonzero[i] + 1) #adds adjacent element and stores to res
                i += 2 #skip next index since previous index resting
            else:
                res.append(grid_nonzero[i]) #if not equal, append element and go next index
                i += 1
        add_zero = [0]*(n-len(res)) #adds zero at end of res
        new_col = res + add_zero
        return new_col

    def spawner(self): #spawn 1 bottom rightmost
        n = self.n
        grid = self.grid
        for r in reversed(range(n)): 
            for c in reversed(range(n)):
                if grid[r][c]==0:
                    grid[r][c]=1
                    return None

    def end_grid(self)-> bool: 
        n = self.n
        grid = self.grid
        for r in range(n):
            for c in range(n):
                if grid[r][c] == 0: #contrapositive check all element for 0
                    return False
                if c<n-1 and grid[r][c]==grid[r][c+1]: #contrapositive check all row element are equal
                    return False
                if r<n-1 and grid[r][c]==grid[r+1][c]: #contrapositive check all col element are equal
                    return False
        return True

def start_grid()-> int: #get n, return int
    if len(sys.argv)>1: #sys.argv is a list = ['lab01.py', 'number', 'textfile']
        return int(sys.argv[1])
    else:
        return 0

def pprint(grid: list[list[int]]): #for debugging
    for row in grid:
        print(row)
    print('===')

def main():
    n = start_grid()
    if n == 0:
        print('Input a Number')
        exit()
    # n:int = int(sys.argv[1]) if len(sys.argv)>2 else print('Done')
    g = Grids(n)
    g.gridprint()
    while True:
        try: #exhausts the iterable key
            key = input().lower()
            if  key =='n': #after every move, print the existing grid
                g.north_move()
                g.gridprint()
                #pprint(g.grid)
            elif  key =='s':
                g.south_move()
                g.gridprint()
                #pprint(g.grid)
            elif  key =='w':
                g.west_move()
                g.gridprint()
                #pprint(g.grid)
            elif  key =='e':
                g.east_move()
                g.gridprint()
                #pprint(g.grid)
            else:
                pass #if not 'nswe' move to other condition in the while loop

        except EOFError:
            print("Done") #when no more input is available, exit
            exit()

        if g.end_grid() == True:
            print('Game over') #when no more moves, exit
            exit()


    g.gridprint()
    print(g.grid)

if __name__ == "__main__":
    main()
