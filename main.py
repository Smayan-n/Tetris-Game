#Tetris with pygame
import pygame, sys, time, math, random

pygame.init()


#grid class - draws grid on screen
class Grid():
    def __init__(self):

        #rows are calculated according to starting height
        self.rows = SCREEN.get_height() // CELL_SIZE
        #columns are fixed
        self.cols = 10

        #set size of display
        pygame.display.set_mode(((self.cols + COL_SPACE*2) * CELL_SIZE, CELL_SIZE * self.rows + 1))
        self.width = SCREEN.get_width()
        self.height = SCREEN.get_height()

    def drawGrid(self):
        for y in range(self.rows + 1):
            pygame.draw.line(SCREEN, BLACK, (COL_SPACE * CELL_SIZE, y * CELL_SIZE), (self.width - (COL_SPACE * CELL_SIZE), y * CELL_SIZE), 1)

        for x in range(COL_SPACE, self.cols + COL_SPACE + 1):
            pygame.draw.line(SCREEN, BLACK, (x * CELL_SIZE, 0 * CELL_SIZE), (x * CELL_SIZE, self.height), 1)

    def getRows(self):
        return self.rows
    def getCols(self):
        return self.cols
    

class Piece():
    #class static variable

    #0's are empty spaces
    #1 and 2 are filled cells
    #2 is the center of the piece
    possible_pieces = [
            [#straight
                [[0, 0], [0, 0], [0, 0], [0, 0]],
            ], 
            [ #square
                [[0, 0], [0, 0]], 
                [[0, 0], [0, 0]]
            ], 
            [#l-shape
                [[0, 0], 0], 
                [[0, 0], 0], 
                [[0, 0], [0, 0]]
            ], 
            [#z-shape
                [[0, 0], 0], 
                [[0, 0], [0, 0]], 
                [0,      [0, 0]]
            ], 
            [#t-shape
                [[0, 0], [0, 0], [0, 0]], 
                [0,      [0, 0],      0]
            ] 
    ]

    def __init__(self):
        #choosing random piece
        # self.piece = random.choice(Piece.possible_pieces)
        self.piece = Piece.possible_pieces[4]
        self.piece_height = len(self.piece)

        #initisal starting row and column of piece (top left block)
        #COL_SPCAE is the starting column here
        self.row = -1
        self.col = 3 + COL_SPACE

        #initialize start postion of piece
        self.initPiecePos()

    def initPiecePos(self):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                #only if the block is has coord
                if(self.piece[r][c] != 0):
                                    #row
                    self.piece[r][c][0] = self.row + r
                                    #col
                    self.piece[r][c][1] = self.col + c
    
    #function to change coordinates of piece - also checks if piece is out of bounds
    def alterPiece(self, row, col):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if(self.piece[r][c] != 0):
                    print(self.piece)
                    self.piece[r][c][0] += row
                    self.piece[r][c][1] += col

                    #checks if piece makes it to the bottom
                    if r == self.piece_height - 1:
                        if self.piece[r][c][0] == GRID.getRows() - 1:
                            #adding piece to game board
                            
                            GAMEBOARD.addSettledPiece(self.piece)
                            GAMEBOARD.pieces.append(Piece())
                            GAMEBOARD.pieces.pop(0)

    
    #draw's piece
    def draw(self):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if(self.piece[r][c] != 0):
                    pygame.draw.rect(SCREEN, RED, (CELL_SIZE * (self.piece[r][c][1]), CELL_SIZE * (self.piece[r][c][0]), CELL_SIZE, CELL_SIZE))
        
    #moves piece down by one row each time           
    def fall(self):
        self.alterPiece(1, 0)

    #when player clicks left or right arrows, piece moves
    def move(self, dir):
        self.alterPiece(0, dir)

        #redners piece on screen (update before graphics function so there is immideiate change)
        SCREEN.fill(BG_COLOR)
        GRID.drawGrid()
        self.draw()

    #rotates picece by 90 degrees every click
    def rotatePiece(self):

        pass

class GameBoard():
    def __init__(self):

        #board with all cells in game board
        self.board = [[0 for i in range(GRID.getCols())] for j in range(GRID.getRows())]

        self.pieces = []
        self.pieces.append(Piece())


    def drawPieces(self):
        for piece in self.pieces:
            piece.fall()              
            piece.draw()  
    
    #draw pieces in self.board (pieces after they are Settled)
    def drawSettledPieces(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != 0:
                    pygame.draw.rect(SCREEN, RED, (CELL_SIZE * (c + COL_SPACE), CELL_SIZE * r, CELL_SIZE, CELL_SIZE))

    #adds piece to game board after it reaches bottom
    def addSettledPiece(self, piece):
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c] != 0:
                    row = piece[r][c][0]
                    col = piece[r][c][1] - COL_SPACE
                    self.board[row][col] = piece[r][c]


#NOTE: Display graphics method runs slower than the pygame mainloop
start_time = time.time() #first run
def displayGraphics():
    global start_time

    #if the elapsed time is greater than threshold, then next frame in rendered
    current_time = time.time()
    if current_time - start_time >= 0.2:

        #fill background
        SCREEN.fill(BG_COLOR)

        #draw grid
        GRID.drawGrid()

        GAMEBOARD.drawPieces()
        GAMEBOARD.drawSettledPieces()


        #start time is reset
        start_time = time.time()

def main():
   
    #main gameloop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            #key events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    GAMEBOARD.pieces[0].move(-1)
                if event.key == pygame.K_RIGHT:
                    GAMEBOARD.pieces[0].move(1)
                if event.key == pygame.K_UP:
                    pass
                if event.key == pygame.K_DOWN:
                    pass

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     GAMEBOARD.pieces[0].move(-1)
        # if keys[pygame.K_RIGHT]:
        #     GAMEBOARD.pieces[0].move(1)

        #calling graphics methods
        displayGraphics() 

        pygame.display.update()
        CLOCK.tick(60)


#static varibles meant to be accesed by all classes and funcs


WIDTH = 800
HEIGHT = 640
CELL_SIZE = 40
#col space is the space to the left and right of the grid(in no of cols)
COL_SPACE = 4

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
CLOCK = pygame.time.Clock()

GRID = Grid()
GAMEBOARD = GameBoard()

#initializing fonts
font1 = pygame.font.SysFont('comicsansms', 12, True)
font2 = pygame.font.SysFont('comicsansms', 25, False, True)
font3 = pygame.font.SysFont('comicsansms', 50, False, True)


#colors
yellow = (244, 208, 63)
brown = (100, 31, 22)
purple = (136, 78, 160)
blue = (53, 152, 219)
RED = (204, 67, 54)
green = (28, 125, 70)
orange = (230, 126, 33)
BLACK = (0, 0, 0)

BG_COLOR = (200, 200, 200)



#bounce_sound = pygame.mixer.Sound('assets/bounce_sound.wav')

if __name__ == '__main__':
   main()