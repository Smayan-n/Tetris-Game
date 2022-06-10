#Tetris with pygame

from copy import deepcopy
import pygame, sys, time, math, random
from constants import *

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

    #getter methods
    def getRows(self):
        return self.rows
    def getCols(self):
        return self.cols
    
#handles individual tetris pieces
class Piece():

    def __init__(self):

        #initial starting row and column of piece (top left block)
        #COL_SPCAE is the starting column here
        self.start_row = -1 #NOTE figure out why pieces are spawning lower
        self.start_col = 3

        #used to determine which rotation map of the piece to load
        self.rotation = 0

        #choosing random piece and color
        self.piece_selection_index = random.randint(0, len(PIECE_TEMPLATES) - 1)
        self.num_rotation_maps = len(PIECE_TEMPLATES[self.piece_selection_index])

        self.piece = PIECE_TEMPLATES[self.piece_selection_index][self.rotation % self.num_rotation_maps]
        self.color = COLORS[self.piece_selection_index]

        #initialize start postion of piece
        self.initPiecePos()

    def initPiecePos(self):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                #only if the block is has coord
                if(self.piece[r][c] != 0):

                    self.piece[r][c] = [self.start_row + r, self.start_col + c]

    
    #function to change coordinates of piece - also checks if piece is out of bounds
    def move(self, row_shift, col_shift):
        print(GAMEBOARD.isInBounds(self.piece))
        # #check for bounds - only updatePos piece if the next position of the piece legal(no other piece in the way)
        # #left
        # for coord in self.getKeyBlocks()[0]:
        #     if coord[1] + col_shift <= GAMEBOARD.getLeftObstructingCol(coord[0], coord[1]):
        #         return
        # #right
        # for coord in self.getKeyBlocks()[1]:
        #     if coord[1] + col_shift >= GAMEBOARD.getRightObstructingCol(coord[0], coord[1]):
        #         return

        #checks if piece makes it to the bottom or sits on top of another piece
        for coord in self.getKeyBlocks()[2]:
            if (coord[0] + row_shift >= GAMEBOARD.getBottomObstructingRow(coord[1], coord[0])):
                #if it does, then the piece is placed on the board
                #adding piece to game board
                GAMEBOARD.addSettledPiece(self.piece)
                #setting current piece to a new piece
                GAMEBOARD.current_piece = Piece()
                break

        test_piece = deepcopy(self.piece)

        #updatePos
        for r in range(len(test_piece)):
            for c in range(len(test_piece[r])):
                if(test_piece[r][c] != 0):
                    test_piece[r][c][0] += row_shift
                    test_piece[r][c][1] += col_shift

        if GAMEBOARD.isInBounds(test_piece):
            self.piece = test_piece
        else:
            return
                
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
        self.rotation += 1

        #get center coordinate and center index of the piece before rotation
        center_coord = self.piece[len(self.piece) // 2][len(self.piece[0]) // 2]
        center_index = [len(self.piece) // 2, len(self.piece[0]) // 2]

        #load the same piece with different rotation map
        self.piece = PIECE_TEMPLATES[self.piece_selection_index][self.rotation % self.num_rotation_maps]

        #using center_coord and center_index to calculate and set coordinates of new rotation map
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if(self.piece[r][c] != 0):
                    #distance from center to next block that is not empty in new map(horizoontal and vertical distance)
                    row_dist = r - center_index[0]
                    col_dist = c - center_index[1]
                    
                    #new coords are the distance + center_coord
                    self.piece[r][c] = [center_coord[0] + row_dist, center_coord[1] + col_dist]
        #render            
        self.draw()

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

#handles game
class GameBoard():
    def __init__(self):

        #board with all cells in game board
        #stores either 0(empty) or a color(filled)
        self.board = [[0 for i in range(GRID.getCols())] for j in range(GRID.getRows())]

        #piece currently falling
        self.current_piece = Piece()

        #timing vars for the falling piece
        self.start_time = time.time()
        self.piece_fall_delay = DEFAULT_PIECE_FALL_DELAY


    def drawPieces(self):
        self.drawSettledPieces() 

        #the Piece.fall() function runs at a slower interval than the main game loop(pieces have to fall slow)
        current_time = time.time()
        if current_time - self.start_time >= self.piece_fall_delay:
            self.current_piece.fall()        

            #start time reset
            self.start_time = time.time()

        #piece draw function running at game loop interval
        self.current_piece.draw()
    
    #draw pieces in self.board (pieces after they are Settled)
    def drawSettledPieces(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != 0:
                    pygame.draw.rect(SCREEN, self.board[r][c], (CELL_SIZE * (c + COL_SPACE), CELL_SIZE * (r), CELL_SIZE, CELL_SIZE))

                    
    #adds piece to game board after it reaches bottom
    def addSettledPiece(self, piece):
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c] != 0:
                    row = piece[r][c][0]
                    col = piece[r][c][1]
                    self.board[row][col] = self.current_piece.color #color of the piece is stored in board

    #returns highest occupied row in the requested column NOTE: change name
    def getBottomObstructingRow(self, col, currentRow):
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

    #checks if piece is in bounds (left, right, and bottom)
    def isInBounds(self, piece):
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c] != 0:
                    if self.board[r][c] != 0 or piece[r][c][1] < 0 or piece[r][c][1] >= GRID.getCols():
                        return False
        return True

    def quickFall(self, flag):
        if flag:
            self.piece_fall_delay = PIECE_QUICK_FALL_DELAY
        else:
            self.piece_fall_delay = DEFAULT_PIECE_FALL_DELAY

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
                    GAMEBOARD.current_piece.updatePos(-1)
                if event.key == pygame.K_RIGHT:
                    GAMEBOARD.current_piece.updatePos(1)
                if event.key == pygame.K_UP:
                    GAMEBOARD.current_piece.rotatePiece()
                if event.key == pygame.K_DOWN:
                    GAMEBOARD.quickFall(True)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    GAMEBOARD.quickFall(False)


        #calling graphics method
        displayGraphics() 

        pygame.display.update()
        CLOCK.tick(60)




#init pygame window
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
CLOCK = pygame.time.Clock()

#creating objects
GRID = Grid()
GAMEBOARD = GameBoard()

if __name__ == '__main__':
   main()