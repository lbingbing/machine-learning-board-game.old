def main():
    from board_game.states.othello_state import OthelloState
    from .othello_policynet import OthelloPolicyNetModel
    from .othello_evaluationnet import OthelloEvaluationNetModel
    from . import policynet_train

    print('train Othello policynet model')

    board_shape = (8, 8)
    print('board_shape:', board_shape)

    state = OthelloState(board_shape = board_shape)
    pmodel_path = 'othello_policynet_model_{0}_{1}'.format(board_shape[0], board_shape[1])
    pmodel = OthelloPolicyNetModel(board_shape = state.board_shape, action_dim = state.get_action_dim(), model_path = pmodel_path)
    emodel_path = 'othello_evaluationnet_model_{0}_{1}'.format(board_shape[0], board_shape[1])
    emodel = OthelloEvaluationNetModel(board_shape = state.board_shape, action_dim = state.get_action_dim(), model_path = emodel_path)

    config = {
        'pmodel_path' : pmodel_path,
        'emodel_path' : emodel_path,
        'discount' : 0.95,
        'batch_size' : 4,
        'learning_rate' : 0.0003,
        'episode_num' : 2000000,
    }

    policynet_train.main(state, pmodel, emodel, config)
