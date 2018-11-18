def main():
    from board_game.states.chess_state import ChessState
    from .chess_policyvaluenet import ChessPolicyValueNetModel
    from . import policyvaluenet_train

    print('train Chess policyvaluenet model')

    state = ChessState()
    model_path = 'chess_policyvaluenet_model'
    model = ChessPolicyValueNetModel(board_shape = state.board_shape, action_dim = state.get_action_dim(), model_path = model_path)

    config = {
        'model_path' : model_path,
        'replaymemory_file_path' : 'chess_policyvaluenet_replaymemory.pickle',
        'replaymemory_size' : 64 * 1024,
        'sim_num' : 1000,
        'dirichlet_factor' : 0.25,
        'dirichlet_alpha' : 0.03,
        'epoch_num' : 16,
        'batch_size' : 128,
        'learning_rate' : 0.003,
        'episode_num' : 2000000,
    }

    policyvaluenet_train.main(state, model, config)
