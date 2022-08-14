import numpy as np
import random
from copy import deepcopy

class Sequence:

    def __init__(self):
        # Letter suits
        # suits = ['S','H','D','C']  
        self.gameOver = False
        self.BLUE = 1
        self.RED = 2
        self.GREEN = 3
        self.SHARED = 4
        self.isAuto = False
        self.score = [0,0,0]
        self.oldScore = [0,0,0]
        # current team 
        self.nTeams = 2
        self.nPlayers = 2
        self.currentTeam = self.BLUE
        self.currentPlayer = 0
        self.otherPlayer = 1
        self.nextTeam2 = { self.BLUE:self.RED, self.RED:self.BLUE}
        self.nextTeam3 = { self.BLUE:self.RED, self.RED:self.GREEN, self.GREEN:self.BLUE}
        self.legalMove = False
        self.suits = ['♠','♥','♦','♣']
        self.series = ['K','Q','J','A','2','3','4','5','6','7','8','9','10']
        self.oneEyed = ['J♠','J♥']
        self.twoEyed = ['J♦','J♣']
        # dictionary for num of cards to deal wrt no of players
        self.handDict = { 2:7, 3:6, 4:6, 6:5, 8:4, 9:4, 10:3, 12:3 }
        # Generating single deck
        self.deck = [n + s for s in self.suits for n in self.series ]
        # Double deck
        self.deck = self.deck + self.deck

        self.nColumn = 10
        self.nRow = 10
        self.colorDict = {'empty': 0, 'black': 1, 'white': 2, 'green': 3}
        self.hands = []
        self.sequences = []
        self.oldScore = 0
        self.newScore = 0

        # self.moves = []
        # Generate board - Layout from deluxe edition
        self.board = [
                    ['◌','6♦','7♦','8♦','9♦','10♦','Q♦','K♦','A♦','◌'],
                    ['5♦','3♥','2♥','2♠','3♠','4♠','5♠','6♠','7♠','A♣'],
                    ['4♦','4♥','K♦','A♦','A♣','K♣','Q♣','10♣','8♠','K♣'],
                    ['3♦','5♥','Q♦','Q♥','10♥','9♥','8♥','9♣','9♠','Q♣'],
                    ['2♦','6♥','10♦','K♥','3♥','2♥','7♥','8♣','10♠','10♣'],
                    ['A♠','7♥','9♦','A♥','4♥','5♥','6♥','7♣','Q♠','9♣'],
                    ['K♠','8♥','8♦','2♣','3♣','4♣','5♣','6♣','K♠','8♣'],
                    ['Q♠','9♥','7♦','6♦','5♦','4♦','3♦','2♦','A♠','7♣'],
                    ['10♠','10♥','Q♥','K♥','A♥','2♣','3♣','4♣','5♣','6♣'],
                    ['◌','9♠','8♠','7♠','6♠','5♠','4♠','3♠','2♠','◌'],
                ]
        # array for quick access - useful in implementing sequence logic
        self.board = np.array(self.board)


        # internal list of players with cards
        self.players = []

        #init play state
        self.playState = [[ 0  for i in range(0,10) ] for j in range(0,10)]
        self.playState = np.array(self.playState)


        #init shared corners
        self.playState[0,0] = self.SHARED
        self.playState[0,9] = self.SHARED
        self.playState[9,0] = self.SHARED
        self.playState[9,9] = self.SHARED


    def getStateFlat(self):
        return self.playState.flatten()

    def showBoard(self):
        print('\n\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.board]))  
    
    def showGame(self):
        boardstate = []
        print('\n\n\t0\t1\t2\t3\t4\t5\t6\t7\t8\t9\t')
        print('------------------------------------------------------------------------------------\n')

               
        for i in range(10):
            row = []
            
            row.append(str(i) + '   |')
            for j in range(10):
                chip = ''
                if self.playState[i][j] == '1':
                    chip = ' \x1b[1;34m●\033[0m'
                elif self.playState[i][j] == '2':
                    chip = " \x1b[1;31m●\033[0m"
                elif self.playState[i][j] == '3':
                    chip = " \x1b[1;32m●\033[0m"
                elif self.playState[i][j] == 'S':
                    chip = ""
                cell = str(self.board[i][j]) + str(chip)
                row.append(cell)            
            boardstate.append(row)
        print('\n\n'.join(['\t'.join([str(cell) for cell in row]) for row in boardstate])) 
        print('\n') 
        # print('\n\n'.join(['\t'.join([str(cell) for cell in row]) for row in boardstate]))  

    def showBoardState(self):
        boardstate = []
        for i in range(10):
            row = []
            for j in range(10):
                cell = str(self.board[i][j]) + str(self.playState[i][j])
                row.append(cell)
            boardstate.append(row)
        
        print('\n\n'.join(['\t'.join([str(cell) for cell in row]) for row in boardstate]))  
        # print(boardstate)

    def tileIterator(self, board_state):
        
        list = []
        size = len(board_state)
        
        # row
        for i in range(size): # [(i,0), (i,1), ..., (i,n-1)]
            list.append([(i, j) for j in range(size)])
        
        # column
        for j in range(size):
            list.append([(i, j) for i in range(size)])
        
        # diagonal: left triangle
        for k in range(size):
            # lower_line consist items [k][0], [k-1][1],...,[0][k]
            # upper_line consist items [size-1][size-1-k], [size-1-1][size-1-k +1],...,[size-1-k][size-1]
            lower_line = [((k-k1), k1) for k1 in range(k+1)]
            upper_line = [((size-1-k2), (size-k-1+k2)) for k2 in range(k+1)]
            if (k == (size-1)): # one diagnoal, lower_line same as upper_line
                list.append(lower_line)
            else :
                if (len(lower_line)>=5):
                    list.append(lower_line)
                if (len(upper_line)>=5):
                    list.append(upper_line)
        
        # diagonal: right triangle
        for k in range(size):
            # lower_line consist items [0][k], [1][k+1],...,[size-1-k][size-1]
            # upper_line consist items [k][0], [k+1][1],...,[size-1][size-1-k]
            lower_line = [(k1, k + k1) for k1 in range(size-k)]
            upper_line = [(k + k2, k2) for k2 in range(size-k)]
            if (k == 0): # one diagnoal, lower_line same as upper_line
                list.append(lower_line)
            else :
                if (len(lower_line)>=5):
                    list.append(lower_line)
                if (len(upper_line)>=5):
                    list.append(upper_line)
        
        for line in list:
            yield line

    def tileValue(self, board_state, coord_list):
        ''' Fetch Value from 2D list with coord_list
        '''
        val = []
        for (i,j) in coord_list:
            val.append(board_state[i][j])
        return val

    def isSublist(self, list, sublist):
        l1 = len(list)
        l2 = len(sublist)
        sub1 = sublist[:]
        sub2 = sublist[:]
        sub1[0] = self.SHARED
        sub2[4] = self.SHARED
        is_sub = 0
        for i in range(l1):
            curSub = list[i: min(i+l2, l1)]
            if (curSub == sublist or curSub == sub1 or curSub == sub2): # check list equal
                is_sub = True
                break
        return is_sub

    def getCoordinates(self, list,sublist):
        l1 = len(list)
        l2 = len(sublist)
        sub1 = sublist[:]
        sub2 = sublist[:]
        sub1[0] = self.SHARED
        sub2[4] = self.SHARED
        for i in range(l1):
            curSub = list[i: min(i+l2, l1)]
            if (curSub == sublist or curSub == sub1 or curSub == sub2): # check list equal
                return i, min(i+l2, l1)
        
    def getIndex(self, list, sublist):
        ''' Return the starting index of the sublist in the list
        '''
        idx = - 1
        l1 = len(list)
        l2 = len(sublist)
        
        for i in range(l1):
            curSub = list[i: min(i+l2, l1)]
            if (curSub == sublist): # check list equal
                idx = i
                break
        return idx

    def checkChipLimit(self, newSequence, currentSequences):
        #   check if any of the chips in current sequence already exists 2 times in all sequences
        #   add exception for corners i.e. -1
        isValidSequence = True
        useCount = []
        currentAllSequences = []
        if self.sequences:
            for seq in self.sequences[self.currentPlayer]:
                currentAllSequences.append(seq)
        
        if currentSequences:
            for seq in currentSequences:
                currentAllSequences.append(seq)
        
        for newChip in newSequence:
            count = 1     
            for sequence in currentAllSequences:
                for  chip in sequence:
                    if chip == newChip and chip != (0,0) and chip != (0,9) and chip != (9,0) and chip != (9,9):
                        count = count + 1
                       
            useCount.append(count)    
        
        for count in useCount:
            if count > 2:
                isValidSequence = False

        return isValidSequence

    def checkPattern(self, board_state, pattern):
            # Check if pattern exist in the board_state lines,
            #     Return: exist: boolean
            #             line: coordinates that contains the patterns
            # 
            pat1 = pattern[:]
            pat2 = pattern[:]
            pat1[0] = self.SHARED
            pat2[4] = self.SHARED
            exist = False
            pattern_found = [] # there maybe multiple patterns found
            for coord in self.tileIterator(board_state):
                line_value = self.tileValue(board_state, coord)
                # check if double pattern = line or line-1 if so then 2 exist
                # test two expand sequences
                if line_value == pattern + pattern or line_value == pat1 + pat2 :
                    if self.checkChipLimit(coord[0:5],pattern_found):
                        pattern_found.append(coord[0:5])

                    if self.checkChipLimit(coord[5:9],pattern_found):
                        pattern_found.append(coord[5:10])
                    
                    exist = True
                # exact coordinates would be split in half
                # test if double pattern with shared
                elif line_value[0:9] == pattern + pattern[0:4]:
                    if self.checkChipLimit(coord[0:5],pattern_found):
                        pattern_found.append(coord[0:5])
                    if self.checkChipLimit(coord[4:9],pattern_found):
                        pattern_found.append(coord[4:9])
                    exist = True
                elif line_value[1:10] == pattern + pattern[0:4]:
                    if self.checkChipLimit(coord[1:6],pattern_found):
                        pattern_found.append(coord[1:6])
                    if self.checkChipLimit(coord[5:10],pattern_found):
                        pattern_found.append(coord[5:10])
                    exist = True
                elif (self.isSublist(line_value, pattern)):
                    # extract exact coordinates
                    start,end = self.getCoordinates(line_value,pattern)
                    exist = True
                    if self.checkChipLimit(coord[start:end],pattern_found):
                        pattern_found.append(coord[start:end])
            return exist, pattern_found
        
    def checkSequences(self):
        self.sequences = []
        size = len(self.playState)
        bluePattern = [self.BLUE for x in range(5)] # 
        redPattern = [self.RED for x in range(5)] #
        greenPattern = [self.GREEN for x in range(5)] #
        self.oldScore = deepcopy(self.score)
        _, bc = self.checkPattern(self.playState, bluePattern)
        _, rc = self.checkPattern(self.playState, redPattern)
        _, gc = self.checkPattern(self.playState, greenPattern)
        self.score = [len(bc),len(rc),len(gc)]
        self.sequences = [bc,rc,gc]

    def shuffleDeck(self):
        random.shuffle(self.deck)

    def getFromDeck(self,num):
        hand = self.deck[0:num]
        del self.deck[0:num]
        return hand

    def dealCards(self,nplayers):
        self.players = [[ x  for x in self.getFromDeck(self.handDict[nplayers]) ] for n in range(nplayers)]

    def getPositions(self,card):
        positions = []
        if 'J' not in card:
            positions.append('Add')
            for i in range(10):
                for j in range(10):
                    if self.board[i][j] == card and self.playState[i][j] == 0:

                        positions.append([i,j])
            # if self.isWasteCard(positions):

            #     print("Waste Card")
            # positions.insert(0,'Add')
            return positions
        # Add two conditions for the Jacks
        # Two Eyed = Any Free Cell
        elif card in self.twoEyed:
            # All free positions Add
            # print('TwoEyed')
            positions.append('Add')
            for i in range(10):
                for j in range(10):
                    if self.playState[i][j] == 0:
                        positions.append([i,j])
            return positions
        # One Eyed = All Occupied - Own Chips - Any Locked
        elif card in self.oneEyed:
            # print('OneEyed')
            positions.append('Remove')

            for i in range(10):
                for j in range(10):
                    if self.playState[i][j] != str(self.currentTeam) and self.playState[i][j] != 0 and self.playState[i][j] != 4:
                        # check if sequence is locked - [i,j] exist in self.sequences
                        # print((i,j))
                        inSequence = False
                        for colors in self.sequences:
                            for sequence in colors:
                                for coord in sequence:
                                    if coord == (i,j):
                                        inSequence = True
                        if not inSequence:
                            positions.append([i,j])
            return positions

    def getMoves(self):
        self.currentMoves = {}
        hand = deepcopy(self.players[self.currentPlayer])
        # hand = ['4♦', '10♣', '8♣', '8♠', '8♠', '10♥', '5♠']
        for card in hand:
            self.currentMoves[card] = self.getPositions(card)
            #   moves.append(self.getPositions(card))
        # go through all possible moves and get all legal moves 
        wasteCard = True

        while wasteCard and len(self.players[self.currentPlayer]) > 0:
            myMoves = {}
            myMoves = deepcopy(self.currentMoves)
            myHand = self.players[self.currentPlayer]
            card = ''
            for card in myHand:
                myMoves = deepcopy(self.currentMoves)
                allMoves = myMoves[card]
                action = allMoves.pop(0)
                if not allMoves and 'J' not in card:
                    wasteCard = True
                    # del self.currentMoves[card]
                    self.players[self.currentPlayer].remove(card)
                    if len(self.deck) > 0:
                        # hand = self.players[player]
                        newCard = self.deck.pop(0)
                        # self.currentMoves[newCard] = self.getPositions(newCard)
                        self.players[self.currentPlayer].append(newCard)
                        # msg = "No moves for " + str(card) + ". Replacing card with " + str(newCard)
                        # print(msg)
                    else:
                        #  msg = "No moves for " + str(card) + ". Deck Finished"
                         break
                    
                    newHand = deepcopy(self.players[self.currentPlayer])
                    self.currentMoves.clear()
                    for card in newHand:
                        self.currentMoves[card] = self.getPositions(card)
                    break
                wasteCard = False
                
        if len(self.players[self.currentPlayer]) == 0:
            # print("Game Over!")
            self.gameOver = True
            return []
            
        return self.currentMoves

    def updateGame(self,player,color,card,action,position):
        # Implement legal checks here for baselines card action position # if invalid do nothing
        
        # check thru list of valid moves or check 
        # self.legalCard = False
        # self.legalAction = False
        self.legalMove = False
        # if 'J' in card:
        #     print('Joker Played')

        # legal = False
        if card in self.players[player]:
            # if player == 0:
            #     self.legalCard = True
            myMoves = deepcopy(self.currentMoves)
            if myMoves:
                act = myMoves[card].pop(0)
                y,x = position
                # if act == action and player == 0:
                #     self.legalAction = True

                if act == action and [y,x] in myMoves[card]:
                    legal = True
                else:
                    # self.gameOver=True
                    return
            else:
                return
        else:
            # self.gameOver=True
            return
        

        if legal:
            
            self.legalMove = True
            # if 'J' in card:
            #     print('Legal Joker')
            # played = "Player " + str(player) + " played " + str(card) + " . " + str(action) + " at " + str(position)
            # print(played)
            # print(str("Deck size" + str(len(self.deck))))
            # print(str("P1 Cards" + str(self.players[0])))
            # print(str("P2 Cards" + str(self.players[1])))
            # game state
            if len(self.players[player]) == 1:
                ...
                # print("Empty")
                # self.gameOver =True
            y,x = position
            if action == "Add":
                self.playState[y][x] = color 
            elif action == "Remove":
                self.playState[y][x] = 0   
            # update sequences
            self.checkSequences()
            # update hand
            self.players[player].remove(card)
            if len(self.deck) > 0:
                self.players[player].append(self.deck.pop(0))
            # change to next player
            if not any(self.players):
                self.gameOver = True
                # print("Game Over!")
            # else:
            #     self.nextTurn()
           
            
        


    def setup(self,nplayers,nteams,auto=True):
        self.isAuto = auto
        self.shuffleDeck()
        self.dealCards(nplayers)
        self.nTeams = nteams
        self.currentPlayer = 0
        self.currentTeam = self.BLUE
        self.nPlayers = nplayers
        self.checkSequences()

    def nextTurn(self):
        # increment player id
        # self.currentPlayer = self.currentPlayer + 1
        # if self.currentPlayer == self.nPlayers:
        #     self.currentPlayer = 0
        # Next teams
        if self.nTeams == 2:
            self.currentTeam = self.nextTeam2[self.currentTeam]
            if self.currentTeam == self.RED and self.isAuto:
                self.randomPolicy()
        elif self.nTeams == 3:
            self.currentTeam = self.nextTeam3[self.currentTeam]
               
    def randomPolicy(self):
        # print("Random Move Selector")
        # time.sleep(0.5)
        allMoves = self.getMoves()
        if allMoves:
            handCards = self.players[self.currentPlayer]
            card = random.choice(handCards)
            cardMoves = deepcopy(allMoves[card])
            if cardMoves:
                action = cardMoves.pop(0)
                move = random.choice(cardMoves)
                self.updateGame(self.currentPlayer,self.currentTeam,card,action,move)
            else:
                self.gameOver = True
                return

        

