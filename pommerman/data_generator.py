import numpy as np
import multiprocessing as mp

from . import utility
from . import constants
from .agents import SparringAgent

class DataGenerator:
    def __init__(self, num_workers=constants.NUM_WORKERS):
        self.num_workers = num_workers


    def agent_simulation(self, worker_id, num_games, sparrer_type):
        # NOTE: may need more imports for network agents
        np.random.seed()

        raw_training_examples = []
        for _ in range(num_games):
            agent = SparringAgent(sparrer_type=sparrer_type, agent_id = worker_id % constants.MAX_PLAYERS)
            raw_training_examples += agent.simulate()

        print('Worker {} Generated {} examples'.format(worker_id, len(raw_training_examples)))
        return raw_training_examples


    def generate_agent_data(self, num_games, sparrer_type):
        process_pool = mp.Pool(processes=self.num_workers)
        workers_results = []

        for i in range(self.num_workers):
            data_async = process_pool.apply_async(self.agent_simulation, args=(i, num_games, sparrer_type))
            workers_results.append(data_async)

        try:
            training_data_X = []
            training_data_y = []
            for res in workers_results:
                worker_data = res.get()
                for X, y, agent_id in worker_data:
                    X = utility.convert_to_model_input(agent_id, X)
                    training_data_X.append(X)
                    training_data_y.append(y)

            process_pool.close()
            process_pool.join()

            # training_data_X = np.array(training_data_X)
            # training_data_y = np.array(training_data_y)

            # # Augment training data
            # X_augment = []
            # y_augment = []
            # for i in range(len(training_data_X)):
            #     X, y = utility.augment_data(training_data_X[i], training_data_y[i])
            #     X_augment.append(X)
            #     y_augment.append(y)

            # X_augment = np.concatenate(X_augment)
            # y_augment = np.concatenate(y_augment)

            return training_data_X, training_data_y

        except KeyboardInterrupt:
            print('SIGINT caught, exiting')
            process_pool.terminate()
            process_pool.join()
            exit()


    def generate_simple_agent_data(self, num_games):
        return self.generate_agent_data(num_games, sparrer_type=constants.SIMPLE_SPARRER)


if __name__ == '__main__':
    generator = DataGenerator(num_workers=constants.NUM_WORKERS)
    training_data_X, training_data_y = generator.generate_simple_agent_data(1)

