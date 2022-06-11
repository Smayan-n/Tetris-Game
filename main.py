#Tetris with pygame

from copy import deepcopy
import pygame, sys, time, json, random
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
        #COL_SPACE is the starting column here
        self.start_row = -2 
        self.start_col = 3

        #used to determine which rotation map of the piece to load
        self.rotation = 0

        #choosing random piece and according color
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

               
    #draw's piece
    def drawPiece(self):
        for r in range(len(self.piece)):
            for c in range(len(self.piece[r])):
                if(self.piece[r][c] != 0):
                    # pygame.draw.rect(SCREEN, self.color, (CELL_SIZE * (self.piece[r][c][1] + COL_SPACE), CELL_SIZE * (self.piece[r][c][0]), CELL_SIZE, CELL_SIZE))
                    SCREEN.blit(BLOCK_ASSETS[self.piece_selection_index], (CELL_SIZE * (self.piece[r][c][1] + COL_SPACE), CELL_SIZE * (self.piece[r][c][0])))
        
    #moves piece down by one row each time           
    def fall(self):
        #increasing score in quick fall
        if GAMECONTROL.piece_fall_delay == PIECE_QUICK_FALL_DELAY:
            GAMECONTROL.increaseScore(1)

        #creating a test piece to check bounds
        test_piece = deepcopy(self.piece)

        #updatePos
        for r in range(len(test_piece)):
            for c in range(len(test_piece[r])):
                if(test_piece[r][c] != 0):
                    test_piece[r][c][0] += 1

        #if, after moving, test piece is not in bounds
        if not GAMECONTROL.pieceInBounds(test_piece):
            #if it does, then the piece is placed on the board
            #adding piece to game board
            GAMECONTROL.addSettledPiece(self.piece)
            #setting current piece to the next piece
            GAMECONTROL.current_piece = GAMECONTROL.next_piece
            #creating a new Next piece
            GAMECONTROL.next_piece = GAMECONTROL.next_next_piece
            GAMECONTROL.next_next_piece = Piece()
            return

        #if in bounds - set test_piece to real piece
        self.piece = test_piece 

    #updatePos piece pos (move left or right)
    def updatePos(self, shift):
        #creating a test piece to check bounds
        test_piece = deepcopy(self.piece)

        #updatePos
        for r in range(len(test_piece)):
            for c in range(len(test_piece[r])):
                if(test_piece[r][c] != 0):
                    test_piece[r][c][1] += shift

        #if, after moving, test piece is not in bounds
        if not GAMECONTROL.pieceInBounds(test_piece):
            return

        #if in bounds - set test_piece to real piece
        self.piece = test_piece
        #redners piece on screen (updatePos before graphics function so there is immideiate change)
        self.drawPiece()


    #rotatePieces picece by 90 degrees every click
    def rotatePiece(self):
        self.rotation += 1

        #get center coordinate and center index of the piece before rotation
        center_coord = self.piece[len(self.piece) // 2][len(self.piece[0]) // 2]
        center_index = [len(self.piece) // 2, len(self.piece[0]) // 2]

        #load the same piece with different rotation map - in a test_piece to check bounds
        test_piece = PIECE_TEMPLATES[self.piece_selection_index][self.rotation % self.num_rotation_maps]

        #using center_coord and center_index to calculate and set coordinates of new rotation map
        for r in range(len(test_piece)):
            for c in range(len(test_piece[r])):
                if(test_piece[r][c] != 0):
                    #distance from center to next block that is not empty in new map(horizoontal and vertical distance)
                    row_dist = r - center_index[0]
                    col_dist = c - center_index[1]
                    
                    #new coords are the distance + center_coord
                    test_piece[r][c] = [center_coord[0] + row_dist, center_coord[1] + col_dist]
        
        #if, after moving, test piece is not in bounds
        if not GAMECONTROL.pieceInBounds(test_piece):
            return
        
        #if in bounds - set test_piece to real piece
        self.piece = test_piece
        #render            
        self.drawPiece()                  
    
#handles game
class GameControl():
    def __init__(self):

        #board with all cells in game board
        #stores either 0(empty) or a color(filled)
        self.board = [[0 for i in range(GRID.getCols())] for j in range(GRID.getRows())]

        #piece currently falling
        self.current_piece = Piece()
        #next pieces
        self.next_piece = Piece()
        self.next_next_piece = Piece()

        #timing vars for the falling piece
        self.start_time = time.time()
        self.piece_fall_delay = PIECE_DEFAULT_FALL_DELAY

        #score and lines cleared
        self.lines_cleared = 0
        self.score = 0
        self.high_score = 0
        #load high score from file
        self.loadHighScore()
    
    def loadHighScore(self):
        with open("high_score.json", "r") as f:
            data = json.load(f)
        
        self.high_score = data["high_score"]


    def drawPieces(self):

        #the Piece.fall() function runs at a slower interval than the main game loop(pieces have to fall slow)
        current_time = time.time()
        if current_time - self.start_time >= self.piece_fall_delay:
            self.current_piece.fall() 
            self.checkRowComplete()

            #start time reset
            self.start_time = time.time()

        #piece draw function running at game loop interval
        self.current_piece.drawPiece()
        self.drawBoard() 
    
    #draw pieces in self.board (pieces after they are Settled)
    def drawBoard(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != 0:
                    SCREEN.blit(BLOCK_ASSETS[self.board[r][c] - 1], (CELL_SIZE * (c + COL_SPACE), CELL_SIZE * (r)))

                    
    #adds piece to game board after it reaches bottom
    def addSettledPiece(self, piece):

        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c] != 0:
                    row = piece[r][c][0]
                    col = piece[r][c][1]
                    self.board[row][col] = self.current_piece.piece_selection_index + 1 #selection index of the piece is stored in board

        #checking if game is lost
        self.isGameLost()

    #checks if piece is in bounds (left, right, and bottom)
    def pieceInBounds(self, piece):
        for r in range(len(piece)):
            for c in range(len(piece[r])):
                if piece[r][c] != 0:
                    row = piece[r][c][0]
                    col = piece[r][c][1]                                        #if this is not 0, there is a block in that position
                    if  row >= GRID.getRows() or col < 0 or col >= GRID.getCols() or self.board[row][col] != 0:
                        return False
        return True
    
    #checks if game is lost (pieces build up to the top)
    def isGameLost(self):
        #if top row has setteled piece, you loose
        for c in range(len(self.board[0])):
            if self.board[0][c] != 0:            
                #reset game
                self.reset()

    #checks if any rows are completely filled
    def checkRowComplete(self):
        for r in range(len(self.board)):
            complete = True
            for c in range(len(self.board[r])):
                if self.board[r][c] == 0:
                    complete = False

            #if any row is complete, it is cleared
            if complete:
                self.clearRow(r)
    
    #clears given row and brings all other rows on top down
    def clearRow(self, row):
        #clear
        self.board[row] = list(map(lambda x: 0, self.board[row]))

        #bring rows above down to fill the gap created
        for r in range(row, 0, -1):
            for c in range(len(self.board[r])):
                self.board[r][c] = self.board[r - 1][c]

        #increase score and lines cleared
        self.lines_cleared += 1
        self.increaseScore(50)

    #changes piece_fall_delay so piece fall faster when doen arrow in clicked
    def quickFall(self, flag):
        if flag:
            self.piece_fall_delay = PIECE_QUICK_FALL_DELAY
        else:
            self.piece_fall_delay = PIECE_DEFAULT_FALL_DELAY
    
    def increaseScore(self, amount):
        self.score += amount
        if self.score > self.high_score:
            self.high_score = self.score
    
    def reset(self):
        #display game over
        game_over_lbl = FONT2.render("Game Over", True, RED)
        SCREEN.blit(game_over_lbl, (SCREEN.get_width()//2 - game_over_lbl.get_width()//2, SCREEN.get_height()//2 - game_over_lbl.get_height()//2)) 
        pygame.display.update()
        pygame.time.delay(1000)

        #reset board
        self.board = [[0 for i in range(GRID.getCols())] for j in range(GRID.getRows())]

        self.score = 0
        self.lines_cleared = 0

    #draw's next pieces that are going to come
    def drawNextPiece(self, piece, y):
        for r in range(len(piece.piece)):
            for c in range(len(piece.piece[r])):
                if piece.piece[r][c] != 0:
                    SCREEN.blit(BLOCK_ASSETS[piece.piece_selection_index], (CELL_SIZE * (c + GRID.getCols() + COL_SPACE), CELL_SIZE * (r + 1) + y))

# Display graphics method 
def displayGraphics():

    #fill background
    SCREEN.fill(BG_COLOR)


    #draw grid
    GRID.drawGrid()

    #draw all game board features
    GAMECONTROL.drawPieces()

    #display UI - scores, next piece info, etc
    
    #labels
    score_lbl = FONT3.render("Score", True, RED)
    score = FONT3.render(str(GAMECONTROL.score), True, RED)
    SCREEN.blit(score_lbl, ((COL_SPACE * CELL_SIZE)//2 - score_lbl.get_width()//2, 0)) 
    SCREEN.blit(score, ((COL_SPACE * CELL_SIZE)//2 - score.get_width()//2, 50)) 

    high_score_lbl = FONT1.render("High Score", True, RED)
    high_score = FONT1.render(str(GAMECONTROL.high_score), True, RED)
    SCREEN.blit(high_score_lbl, ((COL_SPACE * CELL_SIZE)//2 - high_score_lbl.get_width()//2, 150)) 
    SCREEN.blit(high_score, ((COL_SPACE * CELL_SIZE)//2 - high_score.get_width()//2, 200)) 

    lines_cleared_lbl = FONT3.render("Lines", True, RED)
    lines_cleared = FONT3.render(str(GAMECONTROL.lines_cleared), True, RED)
    SCREEN.blit(lines_cleared_lbl, ((COL_SPACE * CELL_SIZE)//2 - lines_cleared_lbl.get_width()//2, SCREEN.get_height() - 150)) 
    SCREEN.blit(lines_cleared, ((COL_SPACE * CELL_SIZE)//2 - lines_cleared.get_width()//2, SCREEN.get_height() - 100)) 

    next_piece_lbl = FONT3.render("Next", True, RED)
    SCREEN.blit(next_piece_lbl, ((GRID.getCols() + COL_SPACE)*(CELL_SIZE) + (COL_SPACE * CELL_SIZE)//2 - next_piece_lbl.get_width()//2, 0))

    #draw next pieces
    GAMECONTROL.drawNextPiece(GAMECONTROL.next_piece, 0)
    GAMECONTROL.drawNextPiece(GAMECONTROL.next_next_piece, 150)


def main():
   
    #main gameloop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                #save high score in file
                json_data = {"high_score": GAMECONTROL.high_score}
                with open("high_score.json", "w") as f:
                    json.dump(json_data, f, indent=4)

                pygame.quit()
                sys.exit()
            
            #key events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    GAMECONTROL.current_piece.updatePos(-1)
                if event.key == pygame.K_RIGHT:
                    GAMECONTROL.current_piece.updatePos(1)
                if event.key == pygame.K_UP:
                    GAMECONTROL.current_piece.rotatePiece()
                if event.key == pygame.K_DOWN:
                    GAMECONTROL.quickFall(True)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    GAMECONTROL.quickFall(False)


        #calling graphics method
        displayGraphics() 

        pygame.display.update()
        CLOCK.tick(60)

#pygame screen initialized in constants.py

#creating objects
GRID = Grid()
GAMECONTROL = GameControl()

if __name__ == '__main__':
   main()