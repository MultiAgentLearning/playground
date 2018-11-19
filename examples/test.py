import pommerman
from pommerman import agents
from pommerman import constants
from pommerman import MCTS
from pommerman import data_generator
import copy
import time
import h5py

if __name__ == '__main__':
    generator = data_generator.DataGenerator(num_workers=constants.NUM_WORKERS)
    training_data_X, training_data_y = generator.generate_simple_agent_data(num_games=1)
    # (n, 11, 11, 15) (n, 6)

    
    with h5py.File('data.h5', 'w') as file:
        file.create_dataset('X', data=training_data_X)
        file.create_dataset('y', data=training_data_y)
    

    # now = time.time()
    # for i in range(10):
    #     agent = agents.SparringAgent(sparrer_type=constants.SIMPLE_SPARRER, agent_id=0)
    #     raw_training_examples = agent.simulate()
    # print(len(raw_training_examples))
    # print(time.time() - now)
    # env = pommerman.make('PommeTeamCompetition-v0', agent_list=[agents.RandomAgent() for _ in range(4)])

    # for i_episode in range(1):
    #     state = env.reset()
    #     done = False
    #     count = 0
    #     while not done:
    #         env = copy.deepcopy(env)
    #         now = time.time()
    #         actions = env.act(state)
    #         print(time.time() - now)
    #         state, reward, done, info = env.step(actions)
    #         count += 1
    #     print('Episode {} finished'.format(i_episode))
    # env.close()
