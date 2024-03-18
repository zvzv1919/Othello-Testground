import argparse
import os
from agents import config as cfg
import pandas as pd


# To allow True/False argparse input.
# See answer by Maxim in https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def _parse_args():
    parser = argparse.ArgumentParser(description='Command Line Interface',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--train_mode", default='random', choices=['random', 'self-play'], type=str, metavar='',
                        help="RL training mode. Valid options are 'random', 'self-play'")
    # for evaluation run
    parser.add_argument("--eval_model_dir", default='.', type=str, metavar='',
                        help="Eval models directory")

    return parser.parse_args()


class ParserOutput:
    """
        To store output values in an object instead of returning individual values
        The default datadir and outputdir are set to /workspace for ease of using Docker container.
    """

    def __init__(self):

        self.parser_func()

    def parser_func(self):
        """
        The function acts as a placeholder to update cfg with values from argparse.

        NOTE:
            proceed: continue with subsequent code in main.py
            model: the selected model is either ctgan, tablegan or tvae.
            datadir: where the training data is located.
            outputdir: where the trained model should be stored.
            data_fn: file name of training data.
            discrete_fn: file that contains the names of discrete variables.
        """

        args = _parse_args()

        # Custom
        self.train_mode = args.train_mode
        self.eval_model_dir = args.eval_model_dir
