import os
import random
import sys
import gc
from collections import deque

import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K

from scipy.special import softmax

from agents import config as cfg

# for performance profiling
# import cProfile as cprofile
# from memory_profiler import profile
# fp = open("report-agent.log", "w+")  # to capture memory profile logs

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

SEED = 42


class OthelloDQNModel:
    """
    Class for the deep neural network model
    """
    def __init__(self, nb_observations, action_dim, learning_rate):
        self.nb_observations = nb_observations
        self.action_dim = action_dim
        self.learning_rate = learning_rate

    def build_model(self):
        """
        build tensorflow model
        :return: tensorflow model
        """
        def root_mean_squared_log_error(y_true, y_pred):
            msle = tf.keras.losses.MeanSquaredLogarithmicError()
            return K.sqrt(msle(y_true, y_pred))

        def root_mean_squared_error(y_true, y_pred):
            mse = tf.keras.losses.MeanSquaredError()
            return K.sqrt(mse(y_true, y_pred))

        _model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, input_shape=(1, self.nb_observations), activation="relu"),
            tf.keras.layers.Dense(64, activation="relu"),

            tf.keras.layers.Dense(64),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.LeakyReLU(),

            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(128, activation="relu"),

            tf.keras.layers.Dense(64),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.LeakyReLU(),

            tf.keras.layers.Dense(64, activation="relu"),
            # tf.keras.layers.Dense(self.action_dim, activation=tf.keras.activations.softmax)
            tf.keras.layers.Dense(self.action_dim, activation=tf.keras.activations.linear)
        ])

        # Model is the full model w/o custom layers
        # _model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),

        # for tensorflow-macos 2.11 and tensorflow-metal 0.7.0 need to switch to legacy optimiser SGD because Adam
        # optimiser issues and where a new optimizer API has been implemented where a default JIT compilation flag is
        # set https://developer.apple.com/forums/thread/721619
        _model.compile(optimizer=tf.keras.optimizers.legacy.SGD(learning_rate=self.learning_rate,
                                                                momentum=0.1,
                                                                nesterov=True),
                       loss=tf.keras.losses.MeanSquaredError(),
                       # loss=tf.keras.losses.MeanAbsoluteError(),
                       # loss=root_mean_squared_log_error,
                       # loss=root_mean_squared_error,
                       metrics=['accuracy'])

        return _model


class OthelloDQN:
    """
    Class for the OthelloDQN object
    """

    def __init__(self, nb_observations, player="white"):

        self.set_global_determinism(seed=SEED)

        self.player = player

        self.action_dim = 64
        self.state_dim = 64

        self.gamma = cfg.agent_setting.GAMMA  # reward decay rate
        self.alpha1 = cfg.agent_setting.ALPHA1  # soft copy weights for self-play, alpha1 updates while (1-alpha1) remains
        self.alpha2 = cfg.agent_setting.ALPHA2  # soft copy weights from eval net to target net, alpha2 updates while (1-alpha2) remains
        self.epsilon_reduce = 0.9999  # 0.995, 0.9995, 0.99975, 0.9999, 0.999975
        self.epsilon = cfg.agent_setting.EPSILON  # epsilon parameter for epsilon greedy selection

        # q network learning parameters
        self.learning_rate = cfg.agent_setting.LEARNING_RATE  # 0.001, 0.0005, 0.0001
        self.batch_size = cfg.agent_setting.BATCH_SIZE  # 128, 256, 512, 768, 1024, 2048
        self.training_epochs = cfg.agent_setting.TRAINING_EPOCHS  # 15, 20, 50, 100

        # total learning step - count how many times the eval net has been updated, used to set a basis for updating
        # the target net
        self.learn_step_counter = 0
        self.replace_target_iter = 75  # 10, 50, 75, 100, 150

        # replay buffer settings
        self.replay_buffer_size = cfg.agent_setting.REPLAY_BUFFER_SIZE  # 20000, 40000, 75000, 150000
        self.replay_buffer = deque(maxlen=self.replay_buffer_size)

        # define the q network
        self.model_full_path = "./models/"

        # only white player learns hence q network will only be created for white player
        if self.player == "white":
            # self.model_eval = self.build_model(nb_observations)  # this is the q network
            self.model_eval = OthelloDQNModel(nb_observations, self.action_dim,
                                              self.learning_rate).build_model()  # this is the q network

        # regardless of training (random or self-play) target network will always be created because this is the network
        # that will be used to predict the action
        # self.model_target = self.build_model(nb_observations)  # this is the target network
        self.model_target = OthelloDQNModel(nb_observations, self.action_dim,
                                            self.learning_rate).build_model()  # this is the target network
        # performance profiling
        # self.cprof = cprofile.Profile()

    @staticmethod
    def set_env_seeds(seed=SEED):
        """
        sets the seed value so that we can reproduce the results constantly
        :param seed:
        :return:
        """
        os.environ['PYTHONHASHSEED'] = str(seed)
        random.seed(seed)
        tf.random.set_seed(seed)
        np.random.seed(seed)

    def set_global_determinism(self, seed=SEED):
        """
        sets tensorflow specific deterministic parameters for reproducibility
        :param seed:
        :return:
        """
        self.set_env_seeds(seed=seed)
        os.environ['TF_DETERMINISTIC_OPS'] = '1'
        os.environ['TF_CUDNN_DETERMINISTIC'] = '1'

    # def build_model(self, nb_observations):
    #     """
    #     build DQN model
    #     :param nb_observations: no. of observations from the game board
    #     :return: DQN model
    #     """
    #     def root_mean_squared_log_error(y_true, y_pred):
    #         msle = tf.keras.losses.MeanSquaredLogarithmicError()
    #         return K.sqrt(msle(y_true, y_pred))
    #
    #     def root_mean_squared_error(y_true, y_pred):
    #         mse = tf.keras.losses.MeanSquaredError()
    #         return K.sqrt(mse(y_true, y_pred))
    #
    #     _model = tf.keras.Sequential([
    #         tf.keras.layers.Dense(64, input_shape=(1, nb_observations), activation="relu"),
    #         tf.keras.layers.Dense(64, activation="relu"),
    #
    #         tf.keras.layers.Dense(64),
    #         tf.keras.layers.BatchNormalization(),
    #         tf.keras.layers.LeakyReLU(),
    #
    #         tf.keras.layers.Dense(128, activation="relu"),
    #         tf.keras.layers.Dense(128, activation="relu"),
    #         tf.keras.layers.Dense(128, activation="relu"),
    #
    #         tf.keras.layers.Dense(64),
    #         tf.keras.layers.BatchNormalization(),
    #         tf.keras.layers.LeakyReLU(),
    #
    #         tf.keras.layers.Dense(64, activation="relu"),
    #         # tf.keras.layers.Dense(self.action_dim, activation=tf.keras.activations.softmax)
    #         tf.keras.layers.Dense(self.action_dim, activation=tf.keras.activations.linear)
    #     ])
    #
    #     # Model is the full model w/o custom layers
    #     # _model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
    #
    #     # for tensorflow-macos 2.11 and tensorflow-metal 0.7.0 need to switch to legacy optimiser SGD because Adam
    #     # optimiser issues and where a new optimizer API has been implemented where a default JIT compilation flag is
    #     # set https://developer.apple.com/forums/thread/721619
    #     _model.compile(optimizer=tf.keras.optimizers.legacy.SGD(learning_rate=self.learning_rate,
    #                                                             momentum=0.1,
    #                                                             nesterov=True),
    #                    loss=tf.keras.losses.MeanSquaredError(),
    #                    # loss=tf.keras.losses.MeanAbsoluteError(),
    #                    # loss=root_mean_squared_log_error,
    #                    # loss=root_mean_squared_error,
    #                    metrics=['accuracy'])
    #
    #     return _model

    # @profile(stream=fp)
    def store_transition(self, observation, action, reward, done, next_observation):
        """
        stores the experience into a deque object. for white player only as we wil be training the white player
        :param next_observation:
        :param done:
        :param reward:
        :param action:
        :param observation:
        :return:
        """
        if self.player == "white":
            self.replay_buffer.append((observation, action, reward, next_observation, done))
        elif self.player == "black":  # black doesn't need to learn so no need to store
            pass

    # @profile(stream=fp)
    def choose_action(self, observation, possible_actions):
        """
        This is an implementation of epsilon_greedy_action_selection to balance between exploitation and exploration
        :param observation: list[list], shape=[8, 8]
        :param possible_actions: a set of tuples (row, col)
        :return: a tuple of (row, col)
        """
        # performance profiling
        # self.cprof.enable()

        # set the mask
        mask = np.array([[True] * 64], dtype=bool)  # shape = (1, 64)
        for row, col in possible_actions:
            mask[0][(row * 8) + col] = False  # do not mask a possible action

        if np.random.random() > self.epsilon:
            observation = np.expand_dims(observation, axis=0)  # (1, 64, )

            with tf.device('/cpu:0'):
                prediction = self.model_target.predict_on_batch(observation)
                # prediction = self.model_eval.predict(observation, verbose=0)  # [0.4 ... 0.6] (64, )
                # prediction = tf.where(mask, -1e9, prediction)  # same as torch.masked_fill
                # prediction = tf.nn.softmax(prediction, axis=None, name=None)  # all masked prob equal to 0 after this step

            # prediction = np.ma.array(prediction, mask=mask).filled(fill_value=-1e9)
            # prediction = softmax(prediction, axis=None)
            prediction = softmax(np.ma.array(prediction, mask=mask).filled(fill_value=-1e9), axis=None)

            # action = tf.argmax(prediction[0], axis=1)
            # action = int(tf.keras.backend.eval(action))
            action = np.argmax(prediction[0], axis=1).item()

            # print("Epsilon:", '%.4f' % self.epsilon, "Agent play:", action)
        else:
            action = random.choice(list(possible_actions))
            action = (action[0] * 8) + action[1]

        # performance profiling
        # self.cprof.disable()
        return action

    # assign weights fromm trained agent into self-play agent
    # @profile(stream=fp)
    def assign_weights(self, other: "OthelloDQN"):
        """
        accept weights from the other (white) player where the weights from the trained agent will be copied and this
        agent will be used for self-play training
        :param other: trained agent from which the weights are to be copied from
        :return:
        """
        if self.player == "other":
            self.model_target.set_weights(other.model_eval.get_weights())
            # print('Update weights from another agent')

    # sync between mode and target_model
    # @profile(stream=fp)
    def __tgt_evl_sync(self):
        """
        copies the weights from model_eval (Q network) to model_target (Target network). partial copy the weights from
        eval net to target net, alpha2 updates while (1-alpha2) remains
        :return:
        """
        if self.player == "white":
            # self.model_target.set_weights(self.model_eval.get_weights())

            self.model_target.set_weights(np.multiply(self.model_eval.get_weights(), self.alpha2, dtype=object) +
                                          np.multiply(self.model_target.get_weights(), (1 - self.alpha2), dtype=object))

            # for t, e in zip(self.model_target.trainable_variables, self.model_eval.trainable_variables):
            #     t.assign(t * (1 - self.alpha2) + e * self.alpha2)

            # for model_layer, target_layer in zip(self.model_eval.layers, self.model_target.layers):
            #     if model_layer.name == "dense":
            #         # same as layer.set_weights([weights_array, bias_array])
            #         target_layer.set_weights([np.multiply(model_layer.get_weights()[0], self.alpha2) +
            #                                   np.multiply(target_layer.get_weights()[0], (1 - self.alpha2)),
            #                                   np.multiply(model_layer.get_weights()[1], self.alpha2) +
            #                                   np.multiply(target_layer.get_weights()[1], (1 - self.alpha2))])

            print('\nUpdate target_model weights')
        elif self.player == "black":
            pass

    # @profile(stream=fp)
    def learn(self):
        """
        trains the DQN model for white player only. model_eval and model_target are synced before training
        :return:
        """
        if self.player == "white":  # only white player learns
            if len(self.replay_buffer) < self.batch_size:
                return

            # sync model_eval and model_targets
            if self.learn_step_counter % self.replace_target_iter == 0:
                self.__tgt_evl_sync()

            # get random sample from reply_buffer
            samples = random.sample(self.replay_buffer, self.batch_size)

            target_batch = []
            zipped_samples = list(zip(*samples))
            states, actions, rewards, new_states, dones = zipped_samples

            # using predict_on_batch resolves the memory leak from predict function
            targets = np.array(self.model_target.predict_on_batch(np.array(states)))
            q_values = np.array(self.model_eval.predict_on_batch(np.array(new_states)))
            # targets = self.model_target.predict(np.array(states), batch_size=self.batch_size , steps=1, verbose=0)
            # q_values = self.model_eval.predict(np.array(new_states), batch_size=self.batch_size , steps=1, verbose=0)

            # populate reward for training
            for i in range(self.batch_size):
                q_value = max(q_values[i][0])
                target = targets[i].copy()
                # target = copy.deepcopy(targets[i])
                # print("before count:", i, "rewards:", rewards[i], "actions:", actions[i], "target:", target[0][actions[i]])
                # input("press to continue")
                if dones[i]:
                    target[0][actions[i]] = rewards[i]
                    # print("1 after count:", i, "rewards:", rewards[i], "actions:", actions[i], "target:", target[0][actions[i]])
                    # input("press to continue")
                else:
                    target[0][actions[i]] = rewards[i] + q_value * self.gamma
                    # print("2 after count:", i, "rewards:", rewards[i], "actions:", actions[i], "target:", target[0][actions[i]])
                    # input("press to continue")
                target_batch.append(target)

            # train network
            # history = self.model_eval.fit(np.array(states), np.array(target_batch),
            #                               epochs=self.training_epochs,
            #                               batch_size=self.batch_size,
            #                               steps_per_epoch=1,
            #                               verbose=0, workers=1)

            history = []
            for i in range(self.training_epochs):
                loss, accuracy = self.model_eval.train_on_batch(np.array(states), np.array(target_batch))
                history.append((loss, accuracy))

            if history is None:
                pass
            else:
                print("\nEpsilon:", round(self.epsilon, 4),
                      "Replay Buffer:", len(self.replay_buffer),
                      "Learn Step:", self.learn_step_counter,
                      # "Avg. Loss:", '%.4f' % np.mean([round(elem, 4) for elem in history.history['loss']]),
                      # "Avg. Accuracy:", '%.4f' % np.mean([round(elem, 4) for elem in history.history['accuracy']]),
                      "Avg. Loss:", '%.4f' % np.mean([item[0] for item in history if item[0] != 0]),
                      "Avg. Accuracy:", '%.4f' % np.mean([item[1] for item in history if item[1] != 0]),
                      "\n")

            # increment the learning step counter
            self.learn_step_counter += 1

            # update the epsilon for epsilon greedy exploration / exploitation
            self.epsilon *= self.epsilon_reduce  # eps * 0.9xxxx

            return

    # @profile(stream=fp)
    def reward_transition_update(self, reward: float):
        """
        if it is the Black that take the last turn, the reward the white player obtained should be updated because the
        winner has been determined
        :param reward: float
        :return:
        """
        def modify_tuple(tup, idx, new_value):
            return tup[:idx] + (new_value,) + tup[idx + 1:]

        if self.player == "white":
            obs = modify_tuple(self.replay_buffer[-1], 2, reward)
            self.replay_buffer.pop()
            self.replay_buffer.append(obs)

    def save_model(self, name="OthelloDQN", save_step='training'):
        """
        saves weights and model
        :return:
        """
        self.model_eval.save_weights("./models/{0}/{1}_{2}.{3}".format(save_step, name, "weights", "h5f"), overwrite=True)
        self.model_eval.save("./models/{0}/{1}_{2}.{3}".format(save_step, name, "model", "h5"))

    def load_model(self, path="", name="OthelloDQN", format_type="model"):
        """
        loads weights and model
        :return:
        """
        if not os.path.exists(path):
            sys.exit("cannot load %s" % name)

        try:
            if format_type == "model":
                print("{0}/{1}_{2}.{3}".format(path, name, "model", "h5"))
                self.model_eval = tf.keras.models.load_model("{0}/{1}_{2}.{3}".format(path, name, "model", "h5"))
                self.model_full_path = "{0}/{1}_{2}.{3}".format(path, name, "model", "h5")
                # print("./models/{0}/{1}_{2}.{3}".format(path, name, "model", "h5"))
                # self.model_eval = tf.keras.models.load_model("./models/{0}/{1}_{2}.{3}".format(path, name, "model", "h5"))
                # self.model_full_path = "./models/{0}/{1}_{2}.{3}".format(path, name, "model", "h5")
            elif format_type == "weights":
                print("{0}/{1}_{2}.{3}".format(path, name, "weights", "h5f"))
                self.model_eval.load_weights("{0}/{1}_{2}.{3}".format(path, name, "weights", "h5f"))
                self.model_full_path = "{0}/{1}_{2}.{3}".format(path, name, "weights", "h5f")
                # print("./models/{0}/{1}_{2}.{3}".format(path, name, "weights", "h5f"))
                # self.model_eval.load_weights("./models/{0}/{1}_{2}.{3}".format(path, name, "weights", "h5f"))
                # self.model_full_path = "./models/{0}/{1}_{2}.{3}".format(path, name, "weights", "h5f")

            return True, "Successfully loaded agent from\n{0}".format(self.model_full_path)
        except ValueError as ve:
            error_str = str(ve)
            print(error_str)
            return False, "Failed to load agent!"

