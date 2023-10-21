import tkinter
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk ,Image
import random, copy, sys, pygame
from pygame.locals import *
from pygame import mixer

import time
import os

########################################################################################################################################################
def Connect():
    # import random, copy, sys, pygame
    # from pygame.locals import *



    BOARDWIDTH = 7  # how many spaces wide the board is
    BOARDHEIGHT = 6 # how many spaces tall the board is
    assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

    DIFFICULTY = 2 # how many moves to look ahead. (>2 is usually too much)

    SPACESIZE = 50 # size of the tokens and individual board spaces in pixels

    FPS = 30 # frames per second to update the screen
    WINDOWWIDTH = 1550 # width of the program's window, in pixels
    WINDOWHEIGHT = 800# height in pixels

    XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
    YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

    BRIGHTBLUE = (0, 50, 255)
    WHITE = (255, 255, 255)

    BGCOLOR = BRIGHTBLUE
    TEXTCOLOR = WHITE

    RED = 'red'
    BLACK = 'black'
    EMPTY = None
    HUMAN = 'human'
    COMPUTER = 'computer'


    def main():
        global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
        global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
        global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG

        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Four in a Row')

        REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
        BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
        REDTOKENIMG = pygame.image.load('4row_red.png')
        REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
        BLACKTOKENIMG = pygame.image.load('4row_black.png')
        BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
        BOARDIMG = pygame.image.load('4row_board.png')
        BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))

        HUMANWINNERIMG = pygame.image.load('4row_humanwinner.png')
        COMPUTERWINNERIMG = pygame.image.load('4row_computerwinner.png')
        TIEWINNERIMG = pygame.image.load('4row_tie.png')
        WINNERRECT = HUMANWINNERIMG.get_rect()
        WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

        ARROWIMG = pygame.image.load('4row_arrow.png')
        ARROWRECT = ARROWIMG.get_rect()
        ARROWRECT.left = REDPILERECT.right + 10
        ARROWRECT.centery = REDPILERECT.centery

        isFirstGame = True

        while True:
            runGame(isFirstGame)
            isFirstGame = False


    def runGame(isFirstGame):
        if isFirstGame:
        # Let the computer go first on the first game, so the player
        # can see how the tokens are dragged from the token piles.
            turn = COMPUTER
            showHelp = True
        else:
        # Randomly choose who goes first.
            if random.randint(0, 1) == 0:
                turn = COMPUTER
            else:
                turn = HUMAN
            showHelp = False

        # Set up a blank board data structure.
        mainBoard = getNewBoard()

        while True: # main game loop
            if turn == HUMAN:
            # Human player's turn.
                getHumanMove(mainBoard, showHelp)
                if showHelp:
                # turn off help arrow after the first move
                    showHelp = False
                if isWinner(mainBoard, RED):
                    winnerImg = HUMANWINNERIMG
                    break
                turn = COMPUTER # switch to other player's turn
            else:
            # Computer player's turn.
                column = getComputerMove(mainBoard)
                animateComputerMoving(mainBoard, column)
                makeMove(mainBoard, BLACK, column)
                if isWinner(mainBoard, BLACK):
                    winnerImg = COMPUTERWINNERIMG
                    break
                turn = HUMAN # switch to other player's turn

            if isBoardFull(mainBoard):
            # A completely filled board means it's a tie.
                winnerImg = TIEWINNERIMG
                break

        while True:
        # Keep looping until player clicks the mouse or quits.
            drawBoard(mainBoard)
            DISPLAYSURF.blit(winnerImg, WINNERRECT)
            pygame.display.update()
            FPSCLOCK.tick()
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    # sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    return


    def makeMove(board, player, column):
        lowest = getLowestEmptySpace(board, column)
        if lowest != -1:
            board[column][lowest] = player


    def drawBoard(board, extraToken=None):
        DISPLAYSURF.fill(BGCOLOR)

    # draw tokens
        spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
                if board[x][y] == RED:
                    DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
                elif board[x][y] == BLACK:
                    DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)

    # draw the extra token
        if extraToken != None:
            if extraToken['color'] == RED:
                DISPLAYSURF.blit(REDTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))
            elif extraToken['color'] == BLACK:
                DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))

    # draw board over the tokens
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
                DISPLAYSURF.blit(BOARDIMG, spaceRect)

    # draw the red and black tokens off to the side
        DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT) # red on the left
        DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT) # black on the right


    def getNewBoard():
        board = []
        for x in range(BOARDWIDTH):
            board.append([EMPTY] * BOARDHEIGHT)
        return board


    def getHumanMove(board, isFirstMove):
        draggingToken = False
        tokenx, tokeny = None, None
        while True:
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT:
                    pygame.quit()
                    # sys.exit()
                elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
                # start of dragging on red token pile.
                    draggingToken = True
                    tokenx, tokeny = event.pos
                elif event.type == MOUSEMOTION and draggingToken:
                # update the position of the red token being dragged
                    tokenx, tokeny = event.pos
                elif event.type == MOUSEBUTTONUP and draggingToken:
                # let go of the token being dragged
                    if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
                    # let go at the top of the screen.
                        column = int((tokenx - XMARGIN) / SPACESIZE)
                        if isValidMove(board, column):
                            animateDroppingToken(board, column, RED)
                            board[column][getLowestEmptySpace(board, column)] = RED
                            drawBoard(board)
                            pygame.display.update()
                            return
                    tokenx, tokeny = None, None
                    draggingToken = False
            if tokenx != None and tokeny != None:
                drawBoard(board, {'x':tokenx - int(SPACESIZE / 2), 'y':tokeny - int(SPACESIZE / 2), 'color':RED})
            else:
                drawBoard(board)

            if isFirstMove:
            # Show the help arrow for the player's first move.
                DISPLAYSURF.blit(ARROWIMG, ARROWRECT)

            pygame.display.update()
            FPSCLOCK.tick()


    def animateDroppingToken(board, column, color):
        x = XMARGIN + column * SPACESIZE
        y = YMARGIN - SPACESIZE
        dropSpeed = 1.0

        lowestEmptySpace = getLowestEmptySpace(board, column)

        while True:
            y += int(dropSpeed)
            dropSpeed += 0.5
            if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
                return
            drawBoard(board, {'x':x, 'y':y, 'color':color})
            pygame.display.update()
            FPSCLOCK.tick()


    def animateComputerMoving(board, column):
        x = BLACKPILERECT.left
        y = BLACKPILERECT.top
        speed = 1.0
    # moving the black tile up
        while y > (YMARGIN - SPACESIZE):
            y -= int(speed)
            speed += 0.5
            drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
            pygame.display.update()
            FPSCLOCK.tick()
    # moving the black tile over
        y = YMARGIN - SPACESIZE
        speed = 1.0
        while x > (XMARGIN + column * SPACESIZE):
            x -= int(speed)
            speed += 0.5
            drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
            pygame.display.update()
            FPSCLOCK.tick()
    # dropping the black tile
        animateDroppingToken(board, column, BLACK)


    def getComputerMove(board):
        potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)
    # get the best fitness from the potential moves
        bestMoveFitness = -1
        for i in range(BOARDWIDTH):
            if potentialMoves[i] > bestMoveFitness and isValidMove(board, i):
                bestMoveFitness = potentialMoves[i]
    # find all potential moves that have this best fitness
        bestMoves = []
        for i in range(len(potentialMoves)):
            if potentialMoves[i] == bestMoveFitness and isValidMove(board, i):
                bestMoves.append(i)
        return random.choice(bestMoves)


    def getPotentialMoves(board, tile, lookAhead):
        if lookAhead == 0 or isBoardFull(board):
            return [0] * BOARDWIDTH

        if tile == RED:
            enemyTile = BLACK
        else:
            enemyTile = RED

    # Figure out the best move to make.
        potentialMoves = [0] * BOARDWIDTH
        for firstMove in range(BOARDWIDTH):
            dupeBoard = copy.deepcopy(board)
            if not isValidMove(dupeBoard, firstMove):
                continue
            makeMove(dupeBoard, tile, firstMove)
            if isWinner(dupeBoard, tile):
            # a winning move automatically gets a perfect fitness
                potentialMoves[firstMove] = 1
                break # don't bother calculating other moves
            else:
            # do other player's counter moves and determine best one
                if isBoardFull(dupeBoard):
                    potentialMoves[firstMove] = 0
                else:
                    for counterMove in range(BOARDWIDTH):
                        dupeBoard2 = copy.deepcopy(dupeBoard)
                        if not isValidMove(dupeBoard2, counterMove):
                            continue
                        makeMove(dupeBoard2, enemyTile, counterMove)
                        if isWinner(dupeBoard2, enemyTile):
                        # a losing move automatically gets the worst fitness
                            potentialMoves[firstMove] = -1
                            break
                        else:
                        # do the recursive call to getPotentialMoves()
                            results = getPotentialMoves(dupeBoard2, tile, lookAhead - 1)
                            potentialMoves[firstMove] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
        return potentialMoves


    def getLowestEmptySpace(board, column):
    # Return the row number of the lowest empty row in the given column.
        for y in range(BOARDHEIGHT-1, -1, -1):
            if board[column][y] == EMPTY:
                return y
        return -1


    def isValidMove(board, column):
    # Returns True if there is an empty space in the given column.
    # Otherwise returns False.
        if column < 0 or column >= (BOARDWIDTH) or board[column][0] != EMPTY:
            return False
        return True


    def isBoardFull(board):
    # Returns True if there are no empty spaces anywhere on the board.
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == EMPTY:
                    return False
        return True


    def isWinner(board, tile):
    # check horizontal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
                    return True
    # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
                    return True
    # check / diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(3, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
                    return True
    # check \ diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
                    return True
        return False


    if __name__ == '__main__':
        main()
    


#############################################################################################################################################

def xoo ():
    # import tkinter
    # from tkinter import *
    # from tkinter import messagebox
    # from PIL import ImageTk ,Image
    # import pygame
    
    global click
    
    gamewindow = Toplevel()
    gamewindow.title("tic tac toe")
    gamewindow.geometry("1550x800+-12+0")
    gamewindow.configure(background="#054")
    
    img0 = ImageTk.PhotoImage(Image.open("back2.jpg"))  
    l=Label(gamewindow, image=img0, height=800, width=1550)
    l.place(y=0,x=0)
    
    lab=Label(gamewindow,text="Aya Mohammed" ,font= 15,fg='black', bg="#212223")
    lab.place(y=764,x=1395)
    
    topfram = Frame(gamewindow, height=380, bg="yellow", bd=5, width=790)
    topfram.place(x=300, y=15 )
    
    
    downframe= Frame(gamewindow, bg="#212223", width=500, height=150 )
    downframe.place(y=2, x=1100)

    buttomframe= Frame(gamewindow, bg="yellow", bd=10, width=500, height=130)
    buttomframe.place(x=15, y=600)

    playerx= IntVar()
    playero= IntVar()

    playerx.set(0)
    playero.set(0)

    buttons= StringVar()
    click = True
    pygame.init()   
    X=pygame.mixer.Sound('x.mp3')
    O=pygame.mixer.Sound('o.mp3')
    def checker(buttons):
        global click
        if buttons["text"] == " " and click == True:
            buttons["text"] = "x"
            click = False
            scorekeeper()

        elif buttons["text"] == " " and click == False:
            buttons["text"] = "o"
            click = True
            scorekeeper()


    def colorreturn():
        button1.configure(fg="black")
        button2.configure(fg="black")
        button3.configure(fg="black")
        button4.configure(fg="black")
        button5.configure(fg="black")
        button6.configure(fg="black")
        button7.configure(fg="black")
        button8.configure(fg="black")
        button9.configure(fg="black")
    
        
    def scorekeeper():
        if(button1["text"]=="x" and button2["text"]=="x" and button3["text"]=="x"):
            button1.configure(fg="green")
            button2.configure(fg="green")
            button3.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()

        elif(button4["text"]=="x" and button5["text"]=="x" and button6["text"]=="x"):
            button4.configure(fg="green")
            button5.configure(fg="green")
            button6.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()
            
        elif (button7["text"]=="x" and button8["text"]=="x" and button9["text"]=="x"):
            button7.configure(fg="green")
            button8.configure(fg="green")
            button9.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()
        elif (button1["text"] == "x" and button4["text"] == "x" and button7["text"] == "x"):
            button1.configure(fg="green")
            button4.configure(fg="green")
            button7.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()
        elif (button2["text"]=="x" and button5["text"]=="x" and button8["text"]=="x"):
            button2.configure(fg="green")
            button5.configure(fg="green")
            button8.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()
        elif (button3["text"]=="x" and button6["text"]=="x" and button9["text"]=="x"):
            button3.configure(fg="green")
            button6.configure(fg="green")
            button9.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)


            playerx.set(score)
            X.play()
        elif (button1["text"]=="x" and button5["text"]=="x" and button9["text"]=="x"):
            button1.configure(fg="green")
            button5.configure(fg="green")
            button9.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()
        elif (button3["text"] == "x" and button5["text"] == "x" and button7["text"] == "x"):
            button3.configure(fg="green")
            button5.configure(fg="green")
            button7.configure(fg="green")
            n = int(playerx.get())
            score = (n + 1)
            playerx.set(score)
            X.play()
        elif (button1["text"] == "o" and button2["text"] == "o" and button3["text"] == "o"):
            button1.configure(fg="green")
            button2.configure(fg="green")
            button3.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()

        elif (button4["text"] == "o" and button5["text"] == "o" and button6["text"] == "o"):
            button4.configure(fg="green")
            button5.configure(fg="green")
            button6.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()
        elif (button7["text"] == "o" and button8["text"] == "o" and button9["text"] == "o"):
            button7.configure(fg="green")
            button8.configure(fg="green")
            button9.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()
        elif (button1["text"] == "o" and button4["text"] == "o" and button7["text"] == "o"):
            button1.configure(fg="green")
            button4.configure(fg="green")
            button7.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()
        elif (button2["text"] == "o" and button5["text"] == "o" and button8["text"] == "o"):
            button2.configure(fg="green")
            button5.configure(fg="green")
            button8.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()
        elif (button3["text"] == "o" and button6["text"] == "o" and button9["text"] == "o"):
            button3.configure(fg="green")
            button6.configure(fg="green")
            button9.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            tkinter.messagebox.showinfo("player O has won", "player O is the winner")
        elif (button1["text"] == "o" and button5["text"] == "o" and button9["text"] == "o"):
            button1.configure(fg="green")
            button5.configure(fg="green")
            button9.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()
        elif (button3["text"] == "o" and button5["text"] == "o" and button7["text"] == "o"):
            button3.configure(fg="green")
            button5.configure(fg="green")
            button7.configure(fg="green")
            n = int(playero.get())
            score = (n + 1)
            playero.set(score)
            O.play()

    def reset():
        colorreturn()
        button1["text"] = " "
        button2["text"] = " "
        button3["text"] = " "
        button4["text"] = " "
        button5["text"] = " "
        button6["text"] = " "
        button7["text"] = " "
        button8["text"] = " "
        button9["text"] = " "



    def newgame():
        reset()
        playerx.set(0)
        playero.set(0)


    button1 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button1))
    button1.grid(row=1, column=0)
    button2 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button2))
    button2.grid(row=1, column=1)

    button3 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button3))
    button3.grid(row=1, column=2)

    button4 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button4))
    button4.grid(row=2, column=0)

    button5 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button5))
    button5.grid(row=2, column=1)

    button6 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button6))
    button6.grid(row=2, column=2) 

    button7 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button7))
    button7.grid(row=3, column=0, sticky= S+N+E+W)

    button8 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button8))
    button8.grid(row=3, column=1)

    button9 = Button(topfram, text = " ", font=("Times 24 bold"), height= 3, width= 6, bg="white", command=lambda :checker(button9))
    button9.grid(row=3, column=2)

    space = Label(downframe, font=("arial", 36, "bold"), text="", pady=1, padx=2 , bg="#212223")
    space.grid(row=0, column=0)

    playerxresult = Label(downframe, font=("arial", 38, "bold"), text="score of player X", pady=5, padx=2 , bg="#212223",fg="yellow")
    playerxresult.grid(row=1, column=0, sticky=W)
    resultx = Entry(downframe, font=("arial", 36, "bold"),fg="green", bd=2, width=10, justify=CENTER, textvariable=playerx)
    resultx.grid(row=2, column=0)

    space = Label(downframe, font=("arial", 36, "bold"), text="",  pady=5, padx=2 , bg="#212223")
    space.grid(row=3, column=0, sticky=W)

    playeroresult = Label(downframe, font=("arial", 38, "bold"), text="score of player O", pady=5, padx=2, bg="#212223",fg="yellow")
    playeroresult.grid(row=4, column=0)
    resulto = Entry(downframe, font=("arial", 36, "bold"), fg="green", bd=2, width=10, justify=CENTER, textvariable=playero)
    resulto.grid(row=5, column=0)
    space = Label(downframe, font=("arial", 36, "bold"),text="",  pady=5, padx=2 , bg="#212223")
    space.grid(row=6, column=0)

    resetbutton = Button(buttomframe, text="Restart game", command=reset, width=17, height=3, fg="black", bg="silver", font=
    ("Times 24 bold"),activebackground='#054')

    resetbutton.grid(row=0, column=0)

    newgamebutton = Button(buttomframe, text="Start new game", command=newgame, width=17, fg="green", height=3, bg="silver"
    , font=("Times 24 bold"),activebackground='#054')


    newgamebutton.grid(row=0, column=1) 

    quitbutton = Button(buttomframe, text="back", command=main and gamewindow.destroy,width=17, height=3, fg="red", bg="silver"
                        , font=("Times 24 bold"),activebackground='#054')

    quitbutton.grid(row=0, column=2)

    gamewindow.mainloop()
###########################################################################################################################################################
def flappybird():
    # import random  # For generating random numbers
    # import sys  # We will use sys.exit to exit the program
    # import pygame
    # from pygame.locals import *  # Basic pygame imports

    # Global Variables for the game
    FPS = 32               #speed of one step of the bird (constant)
    scr_width = 400
    scr_height = 560
    display_screen_window = pygame.display.set_mode((scr_width, scr_height))
    play_ground = scr_height * 0.8
    game_image = {}
    game_audio_sound = {}
    player = 'images/bird.png'
    bcg_image = 'images/background.png'
    pipe_image = 'images/pipe.png'


    def welcome_main_screen():
        """
        Shows welcome images on the screen
        """

        p_x = int(scr_width / 5)
        p_y = int((scr_height - game_image['player'].get_height()) / 2)
        msgx = int((scr_width - game_image['message'].get_width()) / 2)
        msgy = int(scr_height * 0.13)
        b_x = 0
        while True:
            for event in pygame.event.get():
                # if user clicks on cross button, close the game
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    # sys.exit()

                # If the user presses space or up key, start the game for them
                elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    return
                else:
                    display_screen_window.blit(game_image['background'], (0, 0))
                    display_screen_window.blit(game_image['player'], (p_x, p_y))
                    display_screen_window.blit(game_image['message'], (msgx, msgy))
                    display_screen_window.blit(game_image['base'], (b_x, play_ground))
                    pygame.display.update()
                    time_clock.tick(FPS)


    def main_gameplay():
        score = 0
        p_x = int(scr_width / 5)
        p_y = int(scr_width / 2)
        b_x = 0     #base (play ground)


        n_pip1 = get_Random_Pipes()
        n_pip2 = get_Random_Pipes()


        up_pips = [
            {'x': scr_width + 200, 'y': n_pip1[0]['y']},
            {'x': scr_width + 200 + (scr_width / 2), 'y': n_pip2[0]['y']},
        ]

        low_pips = [
            {'x': scr_width + 200, 'y': n_pip1[1]['y']},
            {'x': scr_width + 200 + (scr_width / 2), 'y': n_pip2[1]['y']},
        ]

        pip_Vx = -4

        p_vx = -9
        p_mvx = 10
        p_mvy = -8
        p_accuracy = 1

        p_flap_accuracy = -8
        p_flap = False

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    # sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if p_y > 0:
                        p_vx = p_flap_accuracy
                        p_flap = True
                        game_audio_sound['wing'].play()

            cr_tst = is_Colliding(p_x, p_y, up_pips,
                                  low_pips)
            if cr_tst:
                return 


            p_middle_positions = p_x + game_image['player'].get_width() / 2
            for pipe in up_pips:
                pip_middle_positions = pipe['x'] + game_image['pipe'][0].get_width() / 2
                if pip_middle_positions <= p_middle_positions < pip_middle_positions + 4:
                    score += 1

                    game_audio_sound['point'].play()

            if p_vx < p_mvx and not p_flap:
                p_vx += p_accuracy

            if p_flap:
                p_flap = False
            p_height = game_image['player'].get_height()
            p_y = p_y + min(p_vx, play_ground - p_y - p_height)


            for pip_upper, pip_lower in zip(up_pips, low_pips):
                pip_upper['x'] += pip_Vx
                pip_lower['x'] += pip_Vx


            if 0 < up_pips[0]['x'] < 5:
                new_pip = get_Random_Pipes()
                up_pips.append(new_pip[0])
                low_pips.append(new_pip[1])


            if up_pips[0]['x'] < -game_image['pipe'][0].get_width():
                up_pips.pop(0)
                low_pips.pop(0)


            display_screen_window.blit(game_image['background'], (0, 0))
            for pip_upper, pip_lower in zip(up_pips, low_pips):
                display_screen_window.blit(game_image['pipe'][0], (pip_upper['x'], pip_upper['y']))
                display_screen_window.blit(game_image['pipe'][1], (pip_lower['x'], pip_lower['y']))

            display_screen_window.blit(game_image['base'], (b_x, play_ground))
            display_screen_window.blit(game_image['player'], (p_x, p_y))
            d = [int(x) for x in list(str(score))]
            w = 0
            for digit in d:
                w += game_image['numbers'][digit].get_width()
            Xoffset = (scr_width - w) / 2

            for digit in d:
                display_screen_window.blit(game_image['numbers'][digit], (Xoffset, scr_height * 0.12))
                Xoffset += game_image['numbers'][digit].get_width()
            pygame.display.update()
            time_clock.tick(FPS)


    def is_Colliding(p_x, p_y, up_pipes, low_pipes):
        if p_y > play_ground - 25 or p_y < 0:
            game_audio_sound['hit'].play()
            return True

        for pipe in up_pipes:
            pip_h = game_image['pipe'][0].get_height()
            if (p_y < pip_h + pipe['y'] and abs(p_x - pipe['x']) < game_image['pipe'][0].get_width()):
                game_audio_sound['hit'].play()
                return True

        for pipe in low_pipes:
            if (p_y + game_image['player'].get_height() > pipe['y']) and abs(p_x - pipe['x']) < \
                    game_image['pipe'][0].get_width():
                game_audio_sound['hit'].play()
                return True

        return False


    def get_Random_Pipes():
        """
        Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
        """
        pip_h = game_image['pipe'][0].get_height()
        off_s = scr_height / 3
        yes2 = off_s + random.randrange(0, int(scr_height - game_image['base'].get_height() - 1.2 * off_s))
        pipeX = scr_width + 10
        y1 = pip_h - yes2 + off_s
        pipe = [
            {'x': pipeX, 'y': -y1},  # upper Pipe
            {'x': pipeX, 'y': yes2}  # lower Pipe
        ]
        return pipe


    if __name__ == "__main__":

        pygame.init()
        time_clock = pygame.time.Clock()
        pygame.display.set_caption('Flappy Bird Game')
        game_image['numbers'] = (
            pygame.image.load('0.png').convert_alpha(),
            pygame.image.load('1.png').convert_alpha(),
            pygame.image.load('2.png').convert_alpha(),
            pygame.image.load('3.png').convert_alpha(),
            pygame.image.load('4.png').convert_alpha(),
            pygame.image.load('5.png').convert_alpha(),
            pygame.image.load('6.png').convert_alpha(),
            pygame.image.load('7.png').convert_alpha(),
            pygame.image.load('8.png').convert_alpha(),
            pygame.image.load('9.png').convert_alpha(),
        )
        game_image['message'] = pygame.image.load('message.png').convert_alpha()
        game_image['base'] = pygame.image.load('base1.png').convert_alpha()
        game_image['pipe'] = (pygame.transform.rotate(pygame.image.load('pipe.png').convert_alpha(), 180),
                              pygame.image.load('pipe.png').convert_alpha()
                              )

        # Game sounds
        game_audio_sound['die'] = pygame.mixer.Sound('die.wav')
        game_audio_sound['hit'] = pygame.mixer.Sound('hit.wav')
        game_audio_sound['point'] = pygame.mixer.Sound('point.wav')
        game_audio_sound['swoosh'] = pygame.mixer.Sound('swoosh.wav')
        game_audio_sound['wing'] = pygame.mixer.Sound('wing.wav') 

        game_image['background'] = pygame.image.load('background1.png').convert()
        game_image['player'] = pygame.image.load('bird.png').convert_alpha()

        while True:
            welcome_main_screen()  # Shows welcome screen to the user until he presses a button
            main_gameplay()  # This is the main game function

###########################################################################################################################################################
def bingbong():
    
    import os  
    import turtle  
    import sys   
    import button
    import tkinter.font as font
    # from tkinter import *


       
    # First, we will create screen  
    screen = turtle.Screen()  
    screen.title("Ping-Pong Game")  
    screen.bgcolor("black")  
    screen.setup(width = 800, height = 600) 
    screen.bgpic("backgroundpingpong22.png")
    screen.update()
    

    canvas = screen.getcanvas()
    def again():
    
        turtle.reset()
        turtle.clearscreen()
        # First, we will create screen  
        screen = turtle.Screen()  
        screen.title("Ping-Pong Game")  
        screen.bgcolor("black")  
        screen.setup(width = 800, height = 600) 
        screen.bgpic("backgroundpingpong22.png")
        screen.update()
        def openwindow():
            print("Good bye")

        canvas = screen.getcanvas()
        button = Button(canvas.master, text="Restart",fg='white', bg='#FF7F00', height=1 , width=10 ,command= again)
        myFont = font.Font(family='Helvetica')
        button['font'] = myFont
        button.pack()
        button.place(x=355, y=500)  # place the button anywhere on the screen


        # Left paddle  
        left_paddle = turtle.Turtle()  
        left_paddle.speed(8)  
        left_paddle.shape("square")  
        left_paddle.color("blue")  
        left_paddle.shapesize(stretch_wid = 6, stretch_len = 1)  
        left_paddle.penup()  
        left_paddle.goto(-360, 0)  
   
   
        # Right paddle  
        right_paddle = turtle.Turtle()  
        right_paddle.speed(8)  
        right_paddle.shape("square")  
        right_paddle.color("red")  
        right_paddle.shapesize(stretch_wid = 6, stretch_len = 1)  
        right_paddle.penup()  
        right_paddle.goto(360, 0)  
   
   
        # Ball of circle shape  
        ball = turtle.Turtle()  
        ball.speed(0)  
        ball.shape("circle")  
        ball.color("white")  
        ball.penup()  
        ball.goto(5,5)  
        ball.dx = 8 
        ball.dy = -8
   

       #  initialize the score  
        left_player = 0  
        right_player = 0  
   
   
        # Displaying of the score  
        sketch_1 = turtle.Turtle()  
        sketch_1.speed(0)  
        sketch_1.color("white")  
        sketch_1.penup()  
        sketch_1.hideturtle()  
        sketch_1.goto(0, 260)  
        sketch_1.write("Left Player : 0  |  Right Player: 0",  
                     align = "center", font = ("Courier", 24, "normal"))  
   
   
        # Implementing the functions for moving paddle vertically  
        def paddle_L_up():  
            y = left_paddle.ycor()  
            y += 20  
            left_paddle.sety(y)  


        def paddle_L_down():  
            y = left_paddle.ycor()  
            y -= 20  
            left_paddle.sety(y)  


        def paddle_R_up():  
            y = right_paddle.ycor()  
            y += 20  
            right_paddle.sety(y)  


        def paddle_R_down():  
            y = right_paddle.ycor()  
            y -= 20  
            right_paddle.sety(y)  
   
   
        # Then, binding the keys for moving the paddles up and down.   
        screen.listen()  
        screen.onkeypress(paddle_L_up, "5")  
        screen.onkeypress(paddle_L_down, "2")  
        screen.onkeypress(paddle_R_up, "Up")  
        screen.onkeypress(paddle_R_down, "Down")  

        while True: 

            screen.update()  

            ball.setx(ball.xcor() + ball.dx)  
            ball.sety(ball.ycor() + ball.dy)  

            # Check all the borders  
            if ball.ycor() > 290:  
                ball.sety(290)  
                ball.dy *= -1  

            if ball.ycor() < -290:  
                ball.sety(-290)  
                ball.dy *= -1  

            if ball.xcor() > 390 :  
                ball.goto(0, 0)  
                ball.dy *= -1  
                left_player += 1  
                sketch_1.clear()  
                sketch_1.write("Left_player : {}  |  Right_player: {}".format(  
                              left_player, right_player), align = "center",  
                              font = ("Courier", 24, "normal"))  
            if ball.xcor() < -390:  
                ball.goto(0, 0)  
                ball.dy *= -1  
                right_player += 1  
                sketch_1.clear()  
                sketch_1.write("Left_player : {}   |  Right_player: {}".format(  
                                         left_player, right_player), align = "center",  
                                         font = ("Courier", 24, "normal"))  

            # Collision of ball and paddles  
            if (ball.xcor()>340  and ball.xcor()< 350 and (ball.ycor()< right_paddle.ycor()+40 and ball.ycor()> right_paddle.ycor()-40)):
                ball.setx(340)
                ball.dx *=-1
            if (ball.xcor()<-340  and ball.xcor()>-350 and (ball.ycor()<left_paddle.ycor()+40 and ball.ycor()> left_paddle.ycor()-40)):
                ball.setx(-340)
                ball.dx *=-1
            if (left_player> right_player and left_player == 10 ):
                screen.clear()
                sketch_1.color("blue")
                ball.clear()
                turtle.clear()
                turtle.write("Left_player wins" , font =(24,) , align = "center") 
                turtle.bgcolor("blue")
                canvas = screen.getcanvas()

                button = Button(canvas.master, text="Again",fg='white', bg='#FF7F00', height=1 , width=10 ,command= again)
                myFont = font.Font(family='Helvetica')
                button['font'] = myFont
                button.pack()
                button.place(x=355, y=500)  # place the button anywhere on the screen

            
            elif (right_player> left_player and right_player == 10 ):
                screen.clear()
                sketch_1.color("red")
                ball.clear()
                turtle.clear()
                turtle.write("Right_player wins" , font =(24,) , align = "center") 
                turtle.bgcolor("red")
                canvas = screen.getcanvas()

                 
                button = Button(canvas.master, text="Again",fg='white', bg='#FF7F00', height=1 , width=10 ,command= again)
                myFont = font.Font(family='Helvetica')
                button['font'] = myFont
                button.pack()
                button.place(x=355, y=500)  # place the button anywhere on the screen
                
    button = Button(canvas.master, text="Restart",fg='white', bg='#FF7F00', height=1 , width=10 ,command=again)
    myFont = font.Font(family='Helvetica')
    button['font'] = myFont
    button.pack()
    button.place(x=355, y=500)  # place the button anywhere on the screen

   
    # Left paddle  
    left_paddle = turtle.Turtle()  
    left_paddle.speed(0)  
    left_paddle.shape("square")  
    left_paddle.color("blue")  
    left_paddle.shapesize(stretch_wid = 6, stretch_len = 1)  
    left_paddle.penup()  
    left_paddle.goto(-360, 0)  
   
   
    # Right paddle  
    right_paddle = turtle.Turtle()  
    right_paddle.speed(0)  
    right_paddle.shape("square")  
    right_paddle.color("red")  
    right_paddle.shapesize(stretch_wid = 6, stretch_len = 1)  
    right_paddle.penup()  
    right_paddle.goto(360, 0)  
   
   
   # Ball of circle shape  
    ball = turtle.Turtle()  
    ball.speed(0)  
    ball.shape("circle")  
    ball.color("white")  
    ball.penup()  
    ball.goto(5,5)  
    ball.dx = 8
    ball.dy = -8
   
   
    #  initialize the score  
    left_player = 0  
    right_player = 0  
   
   
    # Displaying of the score  
    sketch_1 = turtle.Turtle()  
    sketch_1.speed(0)  
    sketch_1.color("white")  
    sketch_1.penup()  
    sketch_1.hideturtle()  
    sketch_1.goto(0, 260)  
    sketch_1.write("Left Player : 0  |  Right Player: 0",  
                 align = "center", font = ("Courier", 24, "normal"))  
   
   
    # Implementing the functions for moving paddle vertically  
    def paddle_L_up():  
        y = left_paddle.ycor()  
        y += 20  
        left_paddle.sety(y)  
   
   
    def paddle_L_down():  
        y = left_paddle.ycor()  
        y -= 20  
        left_paddle.sety(y)  
   
   
    def paddle_R_up():  
        y = right_paddle.ycor()  
        y += 20  
        right_paddle.sety(y)  
   
   
    def paddle_R_down():  
        y = right_paddle.ycor()  
        y -= 20  
        right_paddle.sety(y)  
   
   
    # Then, binding the keys for moving the paddles up and down.   
    screen.listen()  
    screen.onkeypress(paddle_L_up, "5")  
    screen.onkeypress(paddle_L_down, "2")  
    screen.onkeypress(paddle_R_up, "Up")  
    screen.onkeypress(paddle_R_down, "Down")  

    
    

            



    while True: 
    
        screen.update()  
   
        ball.setx(ball.xcor() + ball.dx)  
        ball.sety(ball.ycor() + ball.dy)  
   
        # Check all the borders  
        if ball.ycor() > 290:  
            ball.sety(290)  
            ball.dy *= -1  
   
        if ball.ycor() < -290:  
            ball.sety(-290)  
            ball.dy *= -1  
   
        if ball.xcor() > 390:  
            ball.goto(0, 0)  
            ball.dy *= -1  
            left_player += 1  
            sketch_1.clear()  
            sketch_1.write("Left_player : {}  |  Right_player: {}".format(  
                          left_player, right_player), align = "center",  
                          font = ("Courier", 24, "normal")) 
         
        if ball.xcor() < -390:  
            ball.goto(0, 0)  
            ball.dy *= -1  
            right_player += 1  
            sketch_1.clear()  
            sketch_1.write("Left_player : {}  | Right_player: {}".format(  
                                     left_player, right_player), align = "center",  
                                     font = ("Courier", 24, "normal")) 
       
   
        # Collision of ball and paddles  
        if (ball.xcor()>340  and ball.xcor()< 350 and (ball.ycor()< right_paddle.ycor()+40 and ball.ycor()> right_paddle.ycor()-40)):
            ball.setx(340)
            ball.dx *=-1
        if (ball.xcor()<-340  and ball.xcor()>-350 and (ball.ycor()<left_paddle.ycor()+40 and ball.ycor()> left_paddle.ycor()-40)):
            ball.setx(-340)
            ball.dx *=-1
           
        if (left_player> right_player and left_player == 10 ):
      
            screen.clear()
            ball.clear()
            turtle.clear()
            sketch_1.color("blue")
            turtle.write("Left_player wins" , font =(24) , align = "center") 
            sketch_1.color("blue")
            turtle.bgcolor("blue")
    
        
            sketch_1.write("    ", align = "center",  
                                     font = ("Courier", 24 , "normal")) 
            sketch_1.color("blue")
            canvas = screen.getcanvas()
            button = Button(canvas.master, text="Again",fg='white', bg='#FF7F00', height=1 , width=10 ,command= again)
            myFont = font.Font(family='Helvetica')
            button['font'] = myFont
            button.pack()
            button.place(x=355, y=500)  # place the button anywhere on the screen

        
            sketch_1.clear()
        elif (right_player> left_player and right_player == 10 ):
        
            screen.clear()
            ball.clear()
            turtle.clear()
            sketch_1.color("red")
            turtle.write("Right_player wins" , font =(24) , align = "center") 
            sketch_1.color("red")
            turtle.bgcolor("red")
    
        
            sketch_1.write("    ", align = "center",  
                                     font = ("Courier", 24 , "normal")) 
            sketch_1.color("red")
            canvas = screen.getcanvas()
            button = Button(canvas.master, text="Again",fg='white', bg='#FF7F00', height=1 , width=10 ,command= again)
            myFont = font.Font(family='Helvetica')
            button['font'] = myFont
            button.pack()
            button.place(x=355, y=500)  # place the button anywhere on the screen

            sketch_1.clear()
    
###########################################################################################################################################################    

def space_shooter():
    # import time
    # import random
    pygame.init()
    pygame.font.init()

    WIDTH, HEIGHT = 900, 750
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter Tutorial")

    # Load images
    RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
    GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
    BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

    # back and exit buttons

    back_button_img = pygame.image.load(os.path.join("assets", "back-button.png"))
    Exit_button_img = pygame.image.load(os.path.join("assets", "Exit-Button.png"))

    # Player
    YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship.png"))

    # weapons
    egg = pygame.image.load(os.path.join("assets", "egg.png"))
    YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

    # Background
    BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.jpeg")), (WIDTH, HEIGHT))
    main_BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "main_background.jpeg")), (WIDTH, HEIGHT))


    class Laser:
        def __init__(self, x, y, img):
            self.x = x
            self.y = y
            self.img = img
            self.mask = pygame.mask.from_surface(self.img)

        def draw(self, window):
            window.blit(self.img, (self.x, self.y))

        def move(self, vel):
            self.y += vel

        def off_screen(self, height):
            return not(self.y <= height and self.y >= 0)

        def collision(self, obj):
            return collide(self, obj)


    class Ship:
        COOLDOWN = 30

        def __init__(self, x, y, health=100):
            self.x = x
            self.y = y
            self.health = health
            self.ship_img = None
            self.laser_img = None
            self.lasers = []
            self.cool_down_counter = 0

        def draw(self, window):
            window.blit(self.ship_img, (self.x, self.y))
            for laser in self.lasers:
                laser.draw(window)

        def move_lasers(self, vel, obj):
            self.cooldown()
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                elif laser.collision(obj):
                    obj.health -= 10
                    self.lasers.remove(laser)

        def cooldown(self):
            if self.cool_down_counter >= self.COOLDOWN:
                self.cool_down_counter = 0
            elif self.cool_down_counter > 0:
                self.cool_down_counter += 1

        def shoot(self):
            if self.cool_down_counter == 0:
                laser = Laser(self.x-15, self.y-50, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1
                laserSound = mixer.Sound('laser.wav')
                laserSound.play()

        def get_width(self):
            return self.ship_img.get_width()

        def get_height(self):
            return self.ship_img.get_height()


    class Player(Ship):
        def __init__(self, x, y, health=100):
            super().__init__(x, y, health)
            self.ship_img = YELLOW_SPACE_SHIP
            self.laser_img = YELLOW_LASER
            self.mask = pygame.mask.from_surface(self.ship_img)
            self.max_health = health

        def move_lasers(self, vel, objs):
            self.cooldown()
            for laser in self.lasers:
                laser.move(vel)
                if laser.off_screen(HEIGHT):
                    self.lasers.remove(laser)
                else:
                    for obj in objs:
                        if laser.collision(obj):
                            objs.remove(obj)
                            if laser in self.lasers:
                                chickenSound = mixer.Sound('Chicken_sound.mp3')
                                chickenSound.play()
                                self.lasers.remove(laser)

        def draw(self, window):
            super().draw(window)
            self.healthbar(window)

        def healthbar(self, window):
            pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
            pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


    class Enemy(Ship):
        COLOR_MAP = {
                    "red": (RED_SPACE_SHIP, egg),
                    "green": (GREEN_SPACE_SHIP, egg),
                    "blue": (BLUE_SPACE_SHIP, egg)
                    }

        def __init__(self, x, y, color, health=100):
            super().__init__(x, y, health)
            self.ship_img, self.laser_img = self.COLOR_MAP[color]
            self.mask = pygame.mask.from_surface(self.ship_img)

        def move(self, vel):
            self.y += vel

        def shoot(self):
            if self.cool_down_counter == 0:
                laser = Laser(self.x+20, self.y+50, self.laser_img)
                self.lasers.append(laser)
                self.cool_down_counter = 1




    def collide(obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


    class button():
        def __init__(self, x, y, image, scale):
            width = image.get_width()
            height = image.get_height()
            self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)
            self.clicked = False
        def draw(self):
            action = False
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    self.clicked = True
                    action = True

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            WIN.blit(self.image, (self.rect.x, self.rect.y))

            return action

    backButton = button(10, 10, back_button_img, 1)


    def main():

        run = True

        FPS = 60
        level = 0
        lives = 5
        main_font = pygame.font.SysFont("comicsans", 50)
        lost_font = pygame.font.SysFont("comicsans", 60)

        enemies = []
        wave_length = 5
        enemy_vel = 1

        player_vel = 5
        laser_vel = 5

        player = Player(400, 630)

        clock = pygame.time.Clock()

        lost = False
        lost_count = 0

        def redraw_window():
            WIN.blit(BG, (0,0))
            # draw text
            lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
            level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

            WIN.blit(lives_label, (360, 10))
            WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

            for enemy in enemies:
                enemy.draw(WIN)

            WIN.blit(back_button_img, (10, 10))


            player.draw(WIN)

            if lost:
                lossSound = mixer.Sound('lostSound.mp3')
                lossSound.play()
                lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
                WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

            pygame.display.update()

        while run:
            clock.tick(FPS)
            redraw_window()

            if backButton.draw():
                run = False

            if lives <= 0 or player.health <= 0:
                lost = True
                lost_count += 1

            if lost:
                if lost_count > FPS * 3:
                    run = False
                else:
                    continue



            if len(enemies) == 0:
                level += 1
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                    enemies.append(enemy)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
                player.x -= player_vel
            if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
                player.x += player_vel
            if keys[pygame.K_UP] and player.y - player_vel > 0: # up
                player.y -= player_vel
            if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
                player.y += player_vel
            if keys[pygame.K_SPACE]:
                player.shoot()

            for enemy in enemies[:]:
                enemy.move(enemy_vel)
                enemy.move_lasers(laser_vel, player)


                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()


                if collide(enemy, player):
                    player.health -= 10
                    chickenSound = mixer.Sound('Chicken_sound.mp3')
                    chickenSound.play()
                    enemies.remove(enemy)
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1

                    enemies.remove(enemy)

            player.move_lasers(-laser_vel, enemies)


    ExitButton = button(10, HEIGHT-74, Exit_button_img, 1)


    def main_menu():
        title_font = pygame.font.SysFont("comicsans", 70)
        run = True
        exit_clicked = False
        main_sound = mixer.Sound('main_sound.wav')
        main_sound.play()
        while run:
            WIN.blit(main_BG, (0, 0))
            title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
            WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 550))
            WIN.blit(Exit_button_img, (10, HEIGHT-74))
            pygame.display.update()

            for event in pygame.event.get():
                if ExitButton.draw():
                    exit_clicked = True
                    run = False
                if event.type == pygame.QUIT:
                    run = False
                if (exit_clicked is False) and (event.type == pygame.MOUSEBUTTONDOWN):
                    main()

        pygame.quit()


    main_menu()
###########################################################################################################################################################

def runner():
    import pygame
    from sys import exit
    from random import randint, choice

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()

            player_walk_1 = pygame.image.load('graphics/player/player_walk_1.png').convert_alpha()
            player_walk_2 = pygame.image.load('graphics/player/player_walk_2.png').convert_alpha()
            self.player_walk = [player_walk_1,player_walk_2]
            self.player_index = 0
            self.player_jump = pygame.image.load('graphics/player/jump.png').convert_alpha()

            self.image = self.player_walk[self.player_index]
            self.rect = self.image.get_rect(midbottom = (80,300))
            self.gravity = 0

            self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
            self.jump_sound.set_volume(0.5)

        def player_input(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
                self.gravity = -20
                self.jump_sound.play()

        def apply_gravity(self):
            self.gravity += 1
            self.rect.y += self.gravity
            if self.rect.bottom >= 300:
                self.rect.bottom = 300

        def animation_state(self):
            if self.rect.bottom < 300: 
                self.image = self.player_jump
            else:
                self.player_index += 0.1
                if self.player_index >= len(self.player_walk):self.player_index = 0
                self.image = self.player_walk[int(self.player_index)]

        def update(self):
            self.player_input()
            self.apply_gravity()
            self.animation_state()

    class Obstacle(pygame.sprite.Sprite):
        def __init__(self,type):
            super().__init__()

            if type == 'fly':
                fly_1 = pygame.image.load('graphics/fly/fly1.png').convert_alpha()
                fly_2 = pygame.image.load('graphics/fly/fly2.png').convert_alpha()
                self.frames = [fly_1,fly_2]
                y_pos = 210
            else:
                snail_1 = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
                snail_2 = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
                self.frames = [snail_1,snail_2]
                y_pos  = 300

            self.animation_index = 0
            self.image = self.frames[self.animation_index]
            self.rect = self.image.get_rect(midbottom = (randint(900,1100),y_pos))

        def animation_state(self):
            self.animation_index += 0.1 
            if self.animation_index >= len(self.frames): self.animation_index = 0
            self.image = self.frames[int(self.animation_index)]

        def update(self):
            self.animation_state()
            self.rect.x -= 6
            self.destroy()

        def destroy(self):
            if self.rect.x <= -100: 
                self.kill()

    def display_score():
        current_time = int(pygame.time.get_ticks() / 1000) - start_time
        score_surf = test_font.render(f'Score: {current_time}',False,(64,64,64))
        score_rect = score_surf.get_rect(center = (400,50))
        screen.blit(score_surf,score_rect)
        return current_time

    def collision_sprite():
        if pygame.sprite.spritecollide(player.sprite,obstacle_group,False):
            obstacle_group.empty()
            return False
        else: return True

    def mainn():
        pygame.init()
        global screen 
        screen = pygame.display.set_mode((800,400))
        pygame.display.set_caption('Runner')
        clock = pygame.time.Clock()
        global test_font
        test_font = pygame.font.Font('font/Pixeltype.ttf', 50)
        global game_active 
        game_active = False
        global start_time 
        start_time = 0
        score = 0
        bg_music = pygame.mixer.Sound('audio/music.wav')
        bg_music.play(loops = -1)

        #Groups
        global player 
        player = pygame.sprite.GroupSingle()
        player.add(Player())
        global obstacle_group
        obstacle_group = pygame.sprite.Group()

        sky_surface = pygame.image.load('graphics/Sky.png').convert()
        ground_surface = pygame.image.load('graphics/ground.png').convert()
        # global text_surface


        # global text_rect

        # Intro screen
        player_stand = pygame.image.load('graphics/player/player_stand.png').convert_alpha()
        player_stand = pygame.transform.rotozoom(player_stand,0,2)
        player_stand_rect = player_stand.get_rect(center = (400,200))
        text_surface=test_font.render('Amal Eltelbany',False,'Black')
        text_rect=text_surface.get_rect(bottomright=(780,380))
        game_name = test_font.render('Pixel Runner',False,(111,196,169))
        game_name_rect = game_name.get_rect(center = (400,80))

        game_message = test_font.render('Press space to run',False,(111,196,169))
        game_message_rect = game_message.get_rect(center = (400,330))

        # Timer 
        obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(obstacle_timer,1500)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    # exit()

                if game_active:
                    if event.type == obstacle_timer:
                        obstacle_group.add(Obstacle(choice(['fly','snail','snail','snail'])))

                else:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        game_active = True
                        start_time = int(pygame.time.get_ticks() / 1000)


            if game_active:

                screen.blit(sky_surface,(0,0))
                screen.blit(ground_surface,(0,300))
                screen.blit(text_surface,text_rect)
                score = display_score()

                player.draw(screen)
                player.update()

                obstacle_group.draw(screen)
                obstacle_group.update()

                game_active = collision_sprite()

            else:
                screen.fill((94,129,162))
                screen.blit(player_stand,player_stand_rect)

                score_message = test_font.render(f'Your score: {score}',False,(111,196,169))
                score_message_rect = score_message.get_rect(center = (400,330))
                screen.blit(game_name,game_name_rect)

                if score == 0: screen.blit(game_message,game_message_rect)
                else: screen.blit(score_message,score_message_rect)

            pygame.display.update()
            clock.tick(60)
    if __name__ == '__main__':
         mainn()  
###########################################################################################################################################################
def main():
    main = Tk()
    main.title("Games")
    main.geometry("1600x900+-10+0")
    main.configure(background="black")

    back = ImageTk.PhotoImage(Image.open("back1.jpg"))  
    l=Label(image=back, height=800, width=1550)
    l.place(y=0,x=0) 

    img1 = ImageTk.PhotoImage(Image.open("xoo.jfif"))  
    xo=Button(main, image=img1, height=300, width=300 ,command=main.destroy and xoo , activebackground='red')
    xo.place(y=40,x=90)

    img2 = ImageTk.PhotoImage(Image.open("connect_4.jfif"))  
    snakee=Button(main, image=img2, height=300, width=300, activebackground='red',command=main.destroy and Connect )
    snakee.place(y=40,x=440)

    img3 = ImageTk.PhotoImage(Image.open("space_shooter.png"))  
    space=Button(main, image=img3, height=300, width=300, activebackground='red',command=main.destroy and space_shooter)
    space.place(y=40,x=790)

    img4 = ImageTk.PhotoImage(Image.open("bing.jpg"))  
    bing=Button(main, image=img4, height=300, width=300, activebackground='red',command=main.destroy and bingbong)
    bing.place(y=40,x=1140)

    img5 = ImageTk.PhotoImage(Image.open("flappybird.jpeg"))  
    flap=Button(main, image=img5, height=300, width=300, activebackground='red',command=main.destroy and flappybird)
    flap.place(y=380,x=440)

    img6 = ImageTk.PhotoImage(Image.open("runner.png"))  
    snakee=Button(main, image=img6, height=300, width=300, activebackground='red',command=main.destroy and runner )
    snakee.place(y=380,x=790)
  
    backk = ImageTk.PhotoImage(Image.open("spongebob.gif"))  
    l=Label(image=backk, height=150, width=150,borderwidth = 0)
    l.place(y=600,x=20) 

    quitbutton = Button(main, text="Exit", command=main.destroy,width=5, height=1, fg="white", bg="green"
                    , font=("Times 24 bold"),activebackground='red', borderwidth = 20)
    quitbutton.place(x=1340, y=650)
    
    main.mainloop()
    
main()