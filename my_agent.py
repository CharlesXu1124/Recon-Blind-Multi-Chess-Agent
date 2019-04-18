#!/usr/bin/env python3

"""
File Name:      my_agent.py
Authors:        TODO: Your names here!
Date:           TODO: The date you finally started working on this.

Description:    Python file for my agent.
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""

import random
import chess
from game import Game
from player import Player


# TODO: Rename this class to what you would like your bot to be named during the game.
class MyAgent(Player):

    def __init__(self):
        self.color = None
        self.board = None
        self.belief_board = None # the board use for search
        self.sensor = None
        self.king_missing = 0
        self.tracking = 0
        self.density = 0.0 # density of chess pieces around sensor
        self.pieces = None
        self.moves = 0
        self.positionCount = 0




    def handle_game_start(self, color, board):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """
        # TODO: implement this method
        self.color = color
        self.board = chess.Board()
        if (color == chess.BLACK):
            self.sensor = 12
        else:
            self.sensor = 52
            
        self.initialize_sensor = 0
        self.pieces = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        
    def handle_opponent_move_result(self, captured_piece, captured_square):
        """
        This function is called at the start of your turn and gives you the chance to update your board.

        :param captured_piece: bool - true if your opponents captured your piece with their last move
        :param captured_square: chess.Square - position where your piece was captured
        """
        # search for nearest opponent chess piece in the "belief board"
        piece = None
        min_dist = 9999  # minimal manhattan distance to the captured piece
        position = 0
        if self.color == chess.WHITE:
            if captured_piece:

                for i in range(0, 8):
                    for j in range(0, 8):
                        p = self.board.piece_at(i * 8 + j)
                        if p == chess.Piece.from_symbol('p') or \
                                p == chess.Piece.from_symbol('r') or \
                                p == chess.Piece.from_symbol('n') or \
                                p == chess.Piece.from_symbol('b') or \
                                p == chess.Piece.from_symbol('k') or \
                                p == chess.Piece.from_symbol('q'):
                            dist = self.manhattan_distance(captured_square, i * 8 + j)
                            if dist < min_dist:
                                position = i * 8 + j
                                min_dist = dist
                                piece = p
        if self.color == chess.BLACK:
            if captured_piece:
                for i in range(0, 8):
                    for j in range(0, 8):
                        p = self.board.piece_at(i * 8 + j)
                        if p == chess.Piece.from_symbol('P') or \
                                p == chess.Piece.from_symbol('R') or \
                                p == chess.Piece.from_symbol('N') or \
                                p == chess.Piece.from_symbol('B') or \
                                p == chess.Piece.from_symbol('K') or \
                                p == chess.Piece.from_symbol('Q'):
                            dist = self.manhattan_distance(captured_square, i * 8 + j)
                            if dist < min_dist:
                                position = i * 8 + j
                                min_dist = dist
                                piece = p
        if captured_piece:
            self.board.remove_piece_at(position)  # place the chess piece at that square to the capture square
            self.board.set_piece_at(captured_square, piece, promoted=False)

    # This method tries to track opponent's king's location
    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """
        # TODO: update this method
        # initialize sensor position: directly above / below the king
        if  not self.initialize_sensor:
            self.initialize_sensor = 1
            if self.color == chess.BLACK:
                self.sensor = 12
            else:
                self.sensor = 52
        
        if self.king_missing == 1: # if the king position is lost
            # print('king is not detected')
            self.sensor = random.choice(possible_sense)
        if self.sensor % 8 == 0 and self.sensor != 0 and self.sensor != 56: # left boundary
            self.sensor += 1
        if self.sensor % 8 == 7 and self.sensor != 7 and self.sensor != 63: # right boundary
            self.sensor -= 1 
        if self.sensor > 0 and self.sensor < 7: # lower boundary
            self.sensor += 8
        if self.sensor > 56 and self.sensor < 63: # upper boundary
            self.sensor -= 8
        if self.sensor == 0: # lower left corner
            self.sensor += 9
        if self.sensor == 7: # lower right corner
            self.sensor += 7
        if self.sensor == 56: # upper left corner
            self.sensor -= 7
        if self.sensor == 63: # upper right corner
            self.sensor -= 9
        return self.sensor
        
    def handle_sense_result(self, sense_result):
        """
        This is a function called after your picked your 3x3 square to sense and gives you the chance to update your
        board.

        :param sense_result: A list of tuples, where each tuple contains a :class:`Square` in the sense, and if there
                             was a piece on the square, then the corresponding :class:`chess.Piece`, otherwise `None`.
        :example:
        [
            (A8, Piece(ROOK, BLACK)), (B8, Piece(KNIGHT, BLACK)), (C8, Piece(BISHOP, BLACK)),
            (A7, Piece(PAWN, BLACK)), (B7, Piece(PAWN, BLACK)), (C7, Piece(PAWN, BLACK)),
            (A6, None), (B6, None), (C8, None)
        ]
        """
        # TODO: implement this method
        # Hint: until this method is implemented, any senses you make will be lost.
        self.moves += 1
        if self.moves == 50: # if the number of turns ever reaches 20, enter tracking mode
            self.tracking = 1 # start tracking mode after 20 steps
        if self.tracking == 1: # if the sensor mode is precision tracking
            
            marker = 0
            for i in range(0,9):
                if self.color == chess.WHITE:
                    if sense_result[i][1] == chess.Piece(chess.KING, chess.BLACK):
                        self.sensor = sense_result[i][0]
                        marker = 1
                        # print("king is detected!")
                else:
                    if sense_result[i][1] == chess.Piece(chess.KING, chess.WHITE):
                        self.sensor = sense_result[i][0]
                        marker = 1
                        # print("king is detected!")
                self.board.set_piece_at(sense_result[i][0], sense_result[i][1], promoted=False)
            if marker == 0:
                self.king_missing = 1 # king position missing, start randome exploration
            else:
                self.king_missing = 0

        else: # if the sensor mode is active recon
            # update the chess board according to what the sensor detects
            for i in range(0,9):
                self.board.set_piece_at(sense_result[i][0], sense_result[i][1], promoted=False)
            if self.color == chess.WHITE:
                self.sensor = random.choice([chess.B7, chess.E7, chess.G7, chess.B5, chess.E5, chess.G5])
            else:
                self.sensor = random.choice([chess.B2, chess.E2, chess.G2, chess.B4, chess.E4, chess.G4])

    def choose_move(self, possible_moves, seconds_left):
        """
        Choose a move to enact from a list of possible moves.

        :param possible_moves: List(chess.Moves) -- list of acceptable moves based only on pieces
        :param seconds_left: float -- seconds left to make a move
        
        :return: chess.Move -- object that includes the square you're moving from to the square you're moving to
        :example: choice = chess.Move(chess.F2, chess.F4)
        
        :condition: If you intend to move a pawn for promotion other than Queen, please specify the promotion parameter
        :example: choice = chess.Move(chess.G7, chess.G8, promotion=chess.KNIGHT) *default is Queen
        """
        # TODO: update this method
        # fast move generation for the first 10 steps
        if self.moves < 10:
            move = random.choice(possible_moves)
            self.board.push(move)
            return move
        # min-max search tree depth
        depth = 2
        move = self.minmaxRoot(depth, possible_moves, True)
        self.board.push(move) # update the board after deciding the move
        return move
    
    def handle_move_result(self, requested_move, taken_move, reason, captured_piece, captured_square):
        """
        This is a function called at the end of your turn/after your move was made and gives you the chance to update
        your board.

        :param requested_move: chess.Move -- the move you intended to make
        :param taken_move: chess.Move -- the move that was actually made
        :param reason: String -- description of the result from trying to make requested_move
        :param captured_piece: bool - true if you captured your opponents piece
        :param captured_square: chess.Square - position where you captured the piece
        """
        # TODO: implement this method
        if requested_move != taken_move: # if the move is unsuccessful, i.e. blocked by opponent piece
            self.board.pop() # relinquish move
        min_dist = 9999  # minimal manhattan distance to the captured piece
        position = 0
        piece = None
        if self.color == chess.WHITE:
            if captured_piece:
                for i in range(0, 8):
                    for j in range(0, 8):
                        p = self.board.piece_at(i * 8 + j)
                        if p == chess.Piece.from_symbol('p') or \
                                p == chess.Piece.from_symbol('r') or \
                                p == chess.Piece.from_symbol('n') or \
                                p == chess.Piece.from_symbol('b') or \
                                p == chess.Piece.from_symbol('k') or \
                                p == chess.Piece.from_symbol('q'):
                            dist = self.manhattan_distance(captured_square, i * 8 + j)
                            if dist < min_dist:
                                position = i * 8 + j
                                min_dist = dist
                                piece = p
            
        if self.color == chess.BLACK:
            if captured_piece:
                for i in range(0, 8):
                    for j in range(0, 8):
                        p = self.board.piece_at(i * 8 + j)
                        if p == chess.Piece.from_symbol('P') or \
                                p == chess.Piece.from_symbol('R') or \
                                p == chess.Piece.from_symbol('N') or \
                                p == chess.Piece.from_symbol('B') or \
                                p == chess.Piece.from_symbol('K') or \
                                p == chess.Piece.from_symbol('Q'):
                            dist = self.manhattan_distance(captured_square, i * 8 + j)
                            if dist < min_dist:
                                position = i * 8 + j
                                min_dist = dist
                                piece = p
        if captured_piece:
            self.board.remove_piece_at(position)
        if not captured_piece:
            self.board.remove_piece_at(position)
            start = requested_move.from_square
            end = requested_move.to_square
            hidden = (int) ((start + end) / 2)
            self.board.set_piece_at(position, piece)


            
        
    def handle_game_end(self, winner_color, win_reason):  # possible GameHistory object...
        """
        This function is called at the end of the game to declare a winner.

        :param winner_color: Chess.BLACK/chess.WHITE -- the winning color
        :param win_reason: String -- the reason for the game ending
        """
        # TODO: implement this method
        pass

    # the function for evaluating individual chess piece

    def minmaxRoot(self, depth, possible_moves, isMaximisingPlayer):
        newGameMoves = possible_moves
        bestMove = -9999;
        bestMoveFound = None;

        for move in possible_moves:
            newGameMove = move
            self.board.push(newGameMove)
            value = self.minmax(depth - 1, self.board.generate_pseudo_legal_moves(), -5000, 5000, not isMaximisingPlayer)
            self.board.pop()
            if (value >= bestMove):
                bestMove = value
                bestMoveFound = newGameMove
        return bestMoveFound

    def minmax(self, depth, possible_moves, alpha, beta, isMaximisingPlayer):
        self.positionCount += 1
        if (depth == 0):
            return -self.evaluateBoard()

        if (isMaximisingPlayer):
            bestMove = -9999
            for move in possible_moves:
                self.board.push(move)
                bestMove = max(bestMove, self.minmax(depth - 1, self.board.generate_pseudo_legal_moves(), alpha, beta, not isMaximisingPlayer))
                self.board.pop()
                alpha = max(alpha, bestMove)
                if (beta <= alpha):
                    return bestMove
            return bestMove
        else:
            bestMove = 9999
            for move in possible_moves:
                self.board.push(move)
                bestMove = min(bestMove, self.minmax(depth - 1, self.board.generate_pseudo_legal_moves(), alpha, beta, not isMaximisingPlayer))
                self.board.pop()
                beta = min(beta, bestMove)
                if (beta <= alpha):
                    return bestMove
            return bestMove

    # evaluate the entire chess board
    def evaluateBoard(self):
        totalEvaluation = 0
        for i in range(0, 8):
            for j in range(0, 8):
                totalEvaluation += self.evaluate(self.board.piece_at(i * 8 + j), i, j)
        return totalEvaluation

    def manhattan_distance(self, captured_square, piece_square):
        row_diff = int(captured_square / 8) - int(piece_square / 8)
        col_diff = captured_square % 8 - piece_square % 8

        return abs(row_diff) + abs(col_diff)


    def evaluate(self, piece, x, y): # input arguments are x and y coordinates of the chess piece (start from 0)
        pawnEvalWhite =[
            [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
            [5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0],
            [1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0],
            [0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5],
            [0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0],
            [0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5],
            [0.5,  1.0, 1.0,  -2.0,  -2.0,  1.0,  1.0,  0.5],
            [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]]

        pawnEvalBlack = [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 1.0, 1.0, -2.0,  -2.0, 1.0, 1.0, 0.5],
            [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
            [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
            [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
            [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
            [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        knightEval = [
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
            [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
            [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
            [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
            [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
            [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
            [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]]

        bishopEvalWhite = [
            [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
            [ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
            [ -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
            [ -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
            [ -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
            [ -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
            [ -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
            [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]]

        bishopEvalBlack = [
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
            [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
            [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
            [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
            [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]]

        rookEvalWhite = [
            [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
            [  0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
            [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
            [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
            [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
            [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
            [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
            [  0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]]

        rookEvalBlack = [
            [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

        evalQueen = [
            [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
            [ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
            [ -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
            [ -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
            [  0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
            [ -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
            [ -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
            [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]]

        kingEvalWhite = [
            [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [ -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
            [ -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
            [  2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0 ],
            [  2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0 ]]

        kingEvalBlack = [
            [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0],
            [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
            [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
            [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0]]

        if piece == None:
            value = 0
        if (piece == chess.Piece.from_symbol('P')):
            value = 30 + pawnEvalWhite[y][x]
        if (piece == chess.Piece.from_symbol('p')):
            value = 30 + pawnEvalBlack[y][x]
        if (piece == chess.Piece.from_symbol('R')):
            value = 80 + rookEvalWhite[y][x]
        if (piece == chess.Piece.from_symbol('r')):
            value = 80 + rookEvalBlack[y][x]
        if (piece == chess.Piece.from_symbol('N') or piece == chess.Piece.from_symbol('n')):
            value = 50 + knightEval[y][x]
        if (piece == chess.Piece.from_symbol('B')):
            value = 90 + bishopEvalWhite[y][x]
        if (piece == chess.Piece.from_symbol('b')):
            value = 90 + bishopEvalBlack[y][x]
        if (piece == chess.Piece.from_symbol('K')):
            value = 900 + kingEvalWhite[y][x]
        if (piece == chess.Piece.from_symbol('k')):
            value = 900 + kingEvalBlack[y][x]
        if (piece == chess.Piece.from_symbol('Q') or piece == chess.Piece.from_symbol('q')):
            value = 100 + evalQueen[y][x]

        return value if self.color else -value




            
