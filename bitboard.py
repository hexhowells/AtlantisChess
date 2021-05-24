import numpy as np


piece_value = {'.':0, 'p':-1, 'r':-1, 'n':-1, 'b':-1, 'q':-1, 'k':-1,
                'P':1, 'R':1, 'N':1, 'B':1, 'Q':1, 'K':1}
piece_to_channel = {'.':0, 'p':0, 'r':1, 'n':2, 'b':3, 'q':4, 'k':5,
                'P':0, 'R':1, 'N':2, 'B':3, 'Q':4, 'K':5}

board_tensor = np.zeros((6,64))


class BitBoard:
    def serialise(board):
        board_tensor = np.zeros((6,64))
        board = str(board).replace('\n', ' ')
        
        for i, piece in enumerate(board.split(' ')):
            ch = piece_to_channel[piece]
            board_tensor[ch][i] = piece_value[piece]

        return np.reshape(np.copy(board_tensor), (6,8,8))

