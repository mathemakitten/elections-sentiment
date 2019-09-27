import os
import pickle
import logging
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from datetime import datetime as dt
from time import time

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels


def get_logger(name):

    logger_path = 'logs'
    if not os.path.exists(logger_path):
        os.makedirs(logger_path)

    # add logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # https://stackoverflow.com/questions/6729268/log-messages-appearing-twice-with-python-logging
    if not logger.handlers:
        # create a file handler
        current_time = dt.now().strftime('%m-%d')
        file_handler = logging.FileHandler(os.path.join(logger_path, '{}.log'.format(current_time)))
        file_handler.setLevel(logging.INFO)
        # create a logging format
        formats = '[%(asctime)s - %(name)s-%(lineno)d - %(funcName)s - %(levelname)s] %(message)s'
        file_formatter = logging.Formatter(formats, '%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        # add the handlers to the logger
        logger.addHandler(file_handler)

        # console handler
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        c_formatter = logging.Formatter(formats, '%m-%d %H:%M:%S')
        c_handler.setFormatter(c_formatter)
        logger.addHandler(c_handler)
    return logger


logger = get_logger('utils')


def get_paths(create_dir=True):
    from pathlib import Path
    from types import SimpleNamespace

    cwd = Path(os.getcwd())
    print('Current working directory: {}'.format(repr(cwd)))
    file_paths = ['cleaned_tweets', 'raw_tweets', 'pics', 'models']
    file_paths = {fp: cwd/fp for fp in file_paths}

    if create_dir:
        for fp in file_paths.values():
            os.makedirs(str(fp), exist_ok=True)

    file_paths = SimpleNamespace(**file_paths)
    return file_paths


paths = get_paths()


def load_csv(file_name, list_type_colname=None, **kwargs):
    df = pd.read_csv(file_name, **kwargs)
    if list_type_colname is not None:
        from ast import literal_eval
        df[list_type_colname] = df[list_type_colname].apply(literal_eval)
    return df


def plot_confusion_matrix(y_true, y_pred, classes, title, save_path, normalize=False, cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = 'Normalized confusion matrix'
        else:
            title = 'Confusion matrix, without normalization'

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           # ... and label them with the respective list entries
           xticklabels=classes, yticklabels=classes,
           title=title,
           ylabel='True label',
           xlabel='Predicted label')

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    plt.savefig(save_path / '{}.png'.format(title))


def plot_class_counts_over_time(data, save_file_name):
    data['formatted_date'] = pd.to_datetime(data['formatted_date']).dt.date
    data.groupby(['formatted_date', 'label']).size().unstack().plot.area(rot=90, alpha=0.6)
    plt.tight_layout()
    plt.savefig('{}.png'.format(save_file_name))


class Timer(object):
    def __init__(self, description):
        self.description = description

    def __enter__(self):
        self.start = time()

    def __exit__(self, type, value, traceback):
        self.end = time()
        print("{}, time took: {} mins".format(self.description, (self.end - self.start)/60))


def check_gpu():
    import tensorflow as tf
    gpu_available = tf.test.is_gpu_available(cuda_only=True, min_cuda_compute_capability=None)
    if gpu_available:
        print('GPU is available')
    else:
        print('GPU is not available, using CPU')
    return gpu_available


def set_gpu_environ():
    if not check_gpu():
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def save_model(model, model_name):
    save_model_file_path = paths.models/'{}.pkl'.format(model_name)

    with open(save_model_file_path, 'wb') as fout:
        pickle.dump(model, fout)


def load_model(model_name):
    load_model_file_path = paths.models/'{}.pkl'.format(model_name)

    with open(load_model_file_path, 'rb') as fin:
        model = pickle.load(fin)

    return model