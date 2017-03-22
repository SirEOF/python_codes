import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.split(__file__)[0] + '/data/'

TRAIN_FILE = BASE_DIR + 'training.csv'
TRAIN_SAMPLE_FILE = BASE_DIR + 'trainingsample.csv'
TEST_FILE = BASE_DIR + 'test.csv'
SAVE_PATH = BASE_DIR + 'model'

def input_data(filename, test=False):
    df = pd.read_csv(filename)
    cols = df.columns

    df = df.dropna()
    df['Image'] = df['Image'].apply(lambda img: np.fromstring(img, sep=' ') / 255.0)

    X = np.vstack(df['Image'])
    x = X.reshape((-1, 96, 96, 1))
    if test:
        y = None
    else:
        y = df[cols[:-1]].values / 96.
    return x, y

keypoint_index = {
    'left_eye_center_x':0,
    'left_eye_center_y':1,
    'right_eye_center_x':2,
    'right_eye_center_y':3,
    'left_eye_inner_corner_x':4,
    'left_eye_inner_corner_y':5,
    'left_eye_outer_corner_x':6,
    'left_eye_outer_corner_y':7,
    'right_eye_inner_corner_x':8,
    'right_eye_inner_corner_y':9,
    'right_eye_outer_corner_x':10,
    'right_eye_outer_corner_y':11,
    'left_eyebrow_inner_end_x':12,
    'left_eyebrow_inner_end_y':13,
    'left_eyebrow_outer_end_x':14,
    'left_eyebrow_outer_end_y':15,
    'right_eyebrow_inner_end_x':16,
    'right_eyebrow_inner_end_y':17,
    'right_eyebrow_outer_end_x':18,
    'right_eyebrow_outer_end_y':19,
    'nose_tip_x':20,
    'nose_tip_y':21,
    'mouth_left_corner_x':22,
    'mouth_left_corner_y':23,
    'mouth_right_corner_x':24,
    'mouth_right_corner_y':25,
    'mouth_center_top_lip_x':26,
    'mouth_center_top_lip_y':27,
    'mouth_center_bottom_lip_x':28,
    'mouth_center_bottom_lip_y':29
}
