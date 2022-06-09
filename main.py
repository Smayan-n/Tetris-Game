#Tetris with pygame
from cgitb import reset
from telnetlib import GA
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
    
#handles individual tetris pieces
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
                [0,      [0, 0],      0],

            ] 
    ]

    def __init__(self):
        #choosing random piece
        self.piece = random.choice(Piece.possible_pieces)
        # self.piece = Piece.possible_pieces[1]

        #initial starting row and column of piece (top left block)
        #COL_SPCAE is the starting column here
        self.start_row = 0
        self.start_col = 4

        #color
        self.color = random.choice(COLORS)

        #initialize start postion of piece
        self.initPiecePos()

    def initPiecePos(self):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                #only if the block is has coord
                if(self.piece[r][c] != 0):
                                    #row
                    self.piece[r][c][0] = self.start_row + r
                                    #col
                    self.piece[r][c][1] = self.start_col + c
    
    #function to change coordinates of piece - also checks if piece is out of bounds
    def move(self, row_shift, col_shift):
        #check for left and right bounds - only updatePos piece if the updatePos legal(no other piece in the way)
        for coord in self.getKeyBlocks()[0]:
            if coord[1] + col_shift <= GAMEBOARD.getLeftObstructingCol(coord[0], coord[1]):
                return

        for coord in self.getKeyBlocks()[1]:
            if coord[1] + col_shift >= GAMEBOARD.getRightObstructingCol(coord[0], coord[1]):
                return

        #updatePos
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if(self.piece[r][c] != 0):
                    self.piece[r][c][0] += row_shift
                    self.piece[r][c][1] += col_shift
    
        #checks if piece makes it to the bottom or sits on top of another piece- after piece has been moved completely
        for coord in self.getKeyBlocks()[2]:
            if (coord[0] + row_shift >= GAMEBOARD.getRowMaxHeight(coord[1], coord[0])):
                #if it does, then the piece is placed on the board
                #adding piece to game board
                GAMEBOARD.addSettledPiece(self.piece)
                #setting current piece to a new piece
                GAMEBOARD.current_piece = Piece()
                break

    
    #draw's piece
    def draw(self):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if(self.piece[r][c] != 0):
                    pygame.draw.rect(SCREEN, self.color, (CELL_SIZE * (self.piece[r][c][1] + COL_SPACE), CELL_SIZE * (self.piece[r][c][0]), CELL_SIZE, CELL_SIZE))
        
    #moves piece down by one row each time           
    def fall(self):
        self.move(1, 0)

    #updatePos piece pos (move left or right)
    def updatePos(self, dir):
        self.move(0, dir)

        #redners piece on screen (updatePos before graphics function so there is immideiate change)
        self.draw()

    #rotates picece by 90 degrees every click
    def rotatePiece(self):

        pass

    #returns all leftmost, rightmost, and bottom most coords of blocks of the piece
    def getKeyBlocks(self):
        left = []
        right = []
        bottom = []

        #left and right
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if self.piece[r][c] != 0:
                    #for left 
                    if c > 0 and self.piece[r][c - 1] == 0:
                        left.append(self.piece[r][c])
                    elif c == 0:
                        left.append(self.piece[r][c])

                    #for right
                    if c < len(self.piece[r]) - 1 and self.piece[r][c + 1] == 0:
                        right.append(self.piece[r][c])
                    elif c == len(self.piece[r]) - 1:
                        right.append(self.piece[r][c])

        #bottom
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if self.piece[r][c] != 0:
                    #for bottom
                    if r < len(self.piece) - 1 and self.piece[r+1][c] == 0:
                        bottom.append(self.piece[r][c])
                    elif r == len(self.piece) - 1:
                        bottom.append(self.piece[r][c])
        

        return [left, right, bottom]

#main game handling method
class GameBoard():
    def __init__(self):

        #board with all cells in game board
        self.board = [[0 for i in range(GRID.getCols())] for j in range(GRID.getRows())]

        #piece currently falling
        self.current_piece = Piece()

        #timing vars for the falling piece
        self.start_time = time.time()
        self.piece_fall_delay = 0.15

        self.x = False

    def drawPieces(self):
        self.drawSettledPieces() 

        #the Piece.fall() function runs at a slower interval than the main game loop(pieces have to fall slow)
        current_time = time.time()
        if current_time - self.start_time >= self.piece_fall_delay:
            self.current_piece.fall()    
            if self.x:
                self.current_piece.updatePos(-1)        

            #start time reset
            self.start_time = time.time()

        #piece draw function running at game loop interval
        self.current_piece.draw()
    
    #draw pieces in self.board (pieces after they are Settled)
    def drawSettledPieces(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != 0:
                    pygame.draw.rect(SCREEN, RED, (CELL_SIZE * (self.board[r][c][1] + COL_SPACE), CELL_SIZE * (self.board[r][c][0]), CELL_SIZE, CELL_SIZE))

                    
    #adds piece to game board after it reaches bottom
    def addSettledPiece(self, piece):
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c] != 0:
                    row = piece[r][c][0]
                    col = piece[r][c][1]
                    self.board[row][col] = [row, col] #the piece's final position is stored in board so it can be displayed

    #returns highest occupied row in the requested column
    def getRowMaxHeight(self, col, currentRow):
        for r in range(currentRow, len(self.board), 1):
            if self.board[r][col] != 0:
                return r
        return GRID.getRows()
    
    #returns the closest occupied column to the left in the requested row
    def getLeftObstructingCol(self, row, currentCol):
        for c in range(currentCol, -1, -1):
            if self.board[row][c] != 0:
                return c
        return -1

    #returns the closest occupied column to the right in the requested row
    def getRightObstructingCol(self, row, currentCol):
        for c in range(currentCol, len(self.board[row]), 1):
            if self.board[row][c] != 0:
                return c
        return GRID.getCols()

    def quickFall(self, flag):
        if flag:
            self.piece_fall_delay = 0.06
        else:
            self.piece_fall_delay = 0.3

# Display graphics method 
def displayGraphics():
    global start_time

    #fill background
    SCREEN.fill(BG_COLOR)

    #draw grid
    GRID.drawGrid()

    #draw all game board features
    GAMEBOARD.drawPieces()
    

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
                    GAMEBOARD.x = True
                    # GAMEBOARD.current_piece.updatePos(-1)
                if event.key == pygame.K_RIGHT:
                    GAMEBOARD.current_piece.updatePos(1)
                if event.key == pygame.K_UP:
                    GAMEBOARD.current_piece.rotatePiece()
                if event.key == pygame.K_DOWN:
                    GAMEBOARD.quickFall(True)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    GAMEBOARD.x = False
                if event.key == pygame.K_DOWN:
                    GAMEBOARD.quickFall(False)


        keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT]:
        #     # GAMEBOARD.current_piece.updatePos(-1)
        # if keys[pygame.K_RIGHT]:
            # GAMEBOARD.current_piece.updatePos(1)
        # if keys[pygame.K_DOWN]:
        #     GAMEBOARD.piece_fall_delay = 0.05


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


#initializing fonts
font1 = pygame.font.SysFont('comicsansms', 12, True)
font2 = pygame.font.SysFont('comicsansms', 25, False, True)
font3 = pygame.font.SysFont('comicsansms', 50, False, True)


#colors
BROWN = (100, 31, 22)
PURPLE = (136, 78, 160)
BLUE = (53, 152, 219)
RED = (204, 67, 54)
GREEN = (28, 125, 70)
ORANGE = (230, 126, 33)
BLACK = (0, 0, 0)

BG_COLOR = (200, 200, 200)

COLORS = [BROWN, PURPLE, BLUE, RED, GREEN, ORANGE, BLACK]

#creating objects
GRID = Grid()
GAMEBOARD = GameBoard()


if __name__ == '__main__':
   main()