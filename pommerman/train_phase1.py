import numpy as np
import sys
import copy
import random
import keras
import pommerman
import h5py

from pommerman import agents
from model import ResidualCNN
from constants import *

def main(model_path = None, data_path = None):
	model = ResidualCNN()
	if model_path != None:
		model.load(model_path)

	training_data_X = None
	training_data_y = None
	if data_path != None:
		file = h5py.File(data_path, 'r')
		training_data_X = np.copy(file['X'])
		training_data_y = np.copy(file['y'])
	else:
		training_data_X, training_data_y = parallel_data_generate()

	version = 0
	while True:
		model.model.fit(x = training_data_X, y= training_data_y, batch_size = 32, epochs = 1, shuffle=True, validation_split=0.2)
		model.save(SAVE_MODELS_DIR, MODEL_PREFIX, version)
		version += 1


if __name__ == '__main__':
	if len(sys.argv) >= 3:
		main(sys.argv[1], sys.argv[2])
	elif len(sys.argv) >= 2:
		if sys.argv[1].endswith('.h5py'):
			main(model_path = None, data_path = sys.argv[1])
		else:
			main(model_path = sys.argv[1], data_path = None)
	else:
		main()





