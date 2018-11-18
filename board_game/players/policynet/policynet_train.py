import itertools
import numpy as np
import os

from board_game.utils.utils import get_entropy

#np.set_printoptions(threshold = np.nan)

def sample(state, pmodel, batch_size):
    samples = []
    results = []

    for sample_id in range(batch_size):
        state_m_time_l = []
        action_index_time_l = []
        r_time_l = []
        n_state_m_time_l = []
        is_end_time_l = []
        state.reset()
        #print(state)

        is_first_action = True
        for player_id in itertools.cycle((1, 2)):
            state_m = state.to_state_m()
            action = pmodel.get_action(state, player_id)
            state.do_action(player_id, action)
            #print('training player:', action)
            #print(state)
            result = state.get_result()
            action_index = state.action_to_action_index(action)
            n_state_m = state.to_state_m()
            r = 1 if result == player_id else 0
            is_end = result>=0

            if not is_first_action:
                if is_end:
                    last_r = -1
                state_m_time_l.append(last_state_m)
                action_index_time_l.append(last_action_index)
                r_time_l.append(last_r)
                n_state_m_time_l.append(last_n_state_m)
                is_end_time_l.append(is_end)
            else:
                is_first_action = False
            if not is_end:
                last_state_m = state_m
                last_action_index = action_index
                last_r = r
                last_n_state_m = n_state_m
            else:
                state_m_time_l.append(state_m)
                action_index_time_l.append(action_index)
                r_time_l.append(r)
                n_state_m_time_l.append(n_state_m)
                is_end_time_l.append(is_end)
                break

        state_m_time_batch = np.concatenate(state_m_time_l, axis = 0)
        action_m_time_batch = np.zeros((len(action_index_time_l), state.get_action_dim()))
        for t, action_index in enumerate(action_index_time_l):
            action_m_time_batch[t, action_index] = 1
        r_m_time_batch = np.array(r_time_l).reshape(-1, 1).astype(dtype = np.float32)
        n_state_m_time_batch = np.concatenate(n_state_m_time_l, axis = 0)
        is_end_m_time_batch = np.array(is_end_time_l).reshape(-1, 1)

        samples.append((state_m_time_batch, action_m_time_batch, r_m_time_batch, n_state_m_time_batch, is_end_m_time_batch))
        results.append(result)

    return samples, results

def train_emodel(emodel, discount, learning_rate, samples):
    for state_m_time_batch, action_m_time_batch, r_m_time_batch, n_state_m_time_batch, is_end_m_time_batch in samples:
        _, n_V_m_time_batch = emodel.get_V(n_state_m_time_batch)
        target_V_m_time_batch = r_m_time_batch + np.where(is_end_m_time_batch, 0, n_V_m_time_batch) * discount
        emodel.train(state_m_time_batch, target_V_m_time_batch, learning_rate)

def train_pmodel(pmodel, emodel, discount, learning_rate, samples):
    for state_m_time_batch, action_m_time_batch, r_m_time_batch, n_state_m_time_batch, is_end_m_time_batch in samples:
        _, V_m_time_batch = emodel.get_V(state_m_time_batch)
        _, n_V_m_time_batch = emodel.get_V(n_state_m_time_batch)
        advantage_m_time_batch = r_m_time_batch
        advantage_m_time_batch -= V_m_time_batch
        advantage_m_time_batch += np.where(is_end_m_time_batch, 0, n_V_m_time_batch) * discount
        pmodel.train(state_m_time_batch, action_m_time_batch, advantage_m_time_batch, learning_rate)

def main(state, pmodel, emodel, config):
    for k, v in config.items():
        print('{0}: {1}'.format(k, v))

    pmodel.init_parameters()
    #pmodel.load()
    emodel.init_parameters()
    #emodel.load()
    scores = [0] * 3
    for episode_id in range(1, config['episode_num']+1):
        samples, results = sample(state, pmodel, config['batch_size'])
        train_emodel(emodel, config['discount'], config['learning_rate'], samples)
        train_pmodel(pmodel, emodel, config['discount'], config['learning_rate'], samples)
        for result in results:
            scores[result] += 1
        if episode_id % 1 == 0:
            state.reset()
            state_m = state.to_state_m()
            _, V1 = emodel.get_V(state_m)
            V1 = np.asscalar(V1)
            _, action_m1 = pmodel.get_P(state_m)
            entropy1 = get_entropy(action_m1.reshape(-1))
            action = pmodel.get_action(state, 1)
            state.do_action(1, action)
            state_m = state.to_state_m()
            _, V2 = emodel.get_V(state_m)
            V2 = np.asscalar(V2)
            _, action_m2 = pmodel.get_P(state_m)
            entropy2 = get_entropy(action_m2.reshape(-1))
            print('episode: {0} P_e1: {1:.6f} V1: {2:.6f} P_e2: {3:.6f} V2: {4:.6f} p1/p2/draw: {5}/{6}/{7}'.format(episode_id, entropy1, V1, entropy2, V2, scores[1], scores[2], scores[0]))
        #pmodel.save()
        #emodel.save()
        if os.path.isfile('policynet_train_stop'):
            print('stopped')
            break
