import os

from keras import regularizers
from keras.optimizers import SGD, Adam
from keras.models import load_model
from keras.models import Model as KerasModel
from keras.layers import Input, Conv2D, Flatten, Dense, BatchNormalization, LeakyReLU, Activation, add

from loss import softmax_cross_entropy_with_logits
from constants import *
import numpy as np


class Model:
    def __init__(self, input_dim, filters, version=0):
        self.input_dim = input_dim
        self.filters = filters
        self.version = version

    def predict(self, input_board):
        logits = self.model.predict(np.expand_dims(input_board, axis=0).astype('float64'))
        p = utils.softmax(logits)           # Apply softmax on the logits after prediction
        return p.squeeze()                  # Remove the extra batch dimension

    def save(self, save_dir, model_prefix, version):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.version = version
        self.model.save('{}/{}{:0>4}.h5'.format(save_dir, model_prefix, version))
        print('\nSaved model "{}{:0>4}.h5" to "{}"\n'.format(model_prefix, version, save_dir))

    def save_weights(self, save_dir, prefix, version):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.model.save_weights('{}/{}{:0>4}-weights.h5'.format(save_dir, prefix, version))
        utils.stress_message('Saved model weights "{}{:0>4}-weights" to "{}"'.format(prefix, version, save_dir), True)

    def load(self, filepath):
        self.model = load_model(
            filepath,
            custom_objects={'softmax_cross_entropy_with_logits': softmax_cross_entropy_with_logits}
        )
        return self.model

    def load_weights(self, filepath):
        self.model.load_weights(filepath)
        return self.model   # Return reference to model just in case



class ResidualCNN(Model):
    def __init__(self, input_dim=INPUT_DIM, filters=NUM_FILTERS):
        Model.__init__(self, input_dim, filters)
        self.model = self.build_model()


    def build_model(self):
        main_input = Input(shape=self.input_dim)
        regularizer = regularizers.l2(REG_CONST)

        x = Conv2D(filters=64, kernel_size=3, kernel_regularizer=regularizer, padding='valid')(main_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)

        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)

        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)
        x = self.residual_block(x, [32, 32, 64], kernel_size=3, regularizer=regularizer)

        policy = self.policy_head(x, regularizer)

        model = KerasModel(inputs=[main_input], outputs=[policy])
        model.compile(loss={'policy_head':softmax_cross_entropy_with_logits}
                    , optimizer=SGD(lr=LEARNING_RATE, momentum=0.9, nesterov=True) # NOTE: keep here for reuse
                    # , optimizer=Adam(lr=LEARNING_RATE)
                    )

        return model


    def policy_head(self, head_input, regularizer):
        x = Conv2D(filters=16, kernel_size=1, kernel_regularizer=regularizer)(head_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Flatten()(x)
        x = Dense(NUM_ACTIONS,
                use_bias=True,
                activation='linear',
                kernel_regularizer=regularizer,
                name='policy_head')(x)
        return x


    def residual_block(self, block_input, filters, kernel_size, regularizer):
        '''
        Residual block setup code referenced from Keras
        https://github.com/keras-team/keras
        '''
        x = Conv2D(filters=filters[0]
                 , kernel_size=1
                 , kernel_regularizer=regularizer)(block_input)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=filters[1]
                 , kernel_size=kernel_size
                 , padding='same'
                 , kernel_regularizer=regularizer)(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=filters[2]
                 , kernel_size=1
                 , kernel_regularizer=regularizer)(x)
        x = BatchNormalization()(x)

        x = add([x, block_input])
        x = Activation('relu')(x)
        return x


if __name__ == '__main__':
    model = ResidualCNN()
    test_X = np.zeros([32,11,11,15])
    test_y = np.zeros([32,6])
    model.model.fit(x = test_X, y = test_y, batch_size = 32, epochs = 1, shuffle=True)
