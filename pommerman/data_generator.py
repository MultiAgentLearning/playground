import numpy as np
import multiprocessing as mp

from . import utility
from . import constants
from .agents import SparringAgent

class DataGenerator:
    def __init__(self, num_workers):
        self.num_workers = num_workers


    def agent_simulation(self, worker_id, sparrer_type):
        # NOTE: may need more imports for network agents
        np.random.seed()

        agent = SparringAgent(sparrer_type=sparrer_type)
        agent.set_agent_id(worker_id % constants.MAX_PLAYERS)

        raw_training_examples = agent.simulate()
        return raw_training_examples


    def generate_agent_data(self, sparrer_type):
        process_pool = mp.Pool(processes=self.num_workers)
        workers_results = []

        for i in range(self.num_workers):
            data_async = process_pool.apply_async(self.agent_simulation, args=(i, sparrer_type))
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

            process_pool.join()
            return np.array(training_data_X), np.array(training_data_y)

        except KeyboardInterrupt:
            print('SIGINT caught, exiting')
            process_pool.terminate()
            process_pool.join()
            exit()


    def generate_simple_agent_data(self):
        return self.generate_agent_data(sparrer_type=constants.SIMPLE_SPARRER)



