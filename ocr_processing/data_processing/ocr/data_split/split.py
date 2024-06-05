import os
import json
import cv2
import argparse
from tqdm import tqdm
from pathlib import Path
from random import shuffle

from config import CARD_TYPE

TRAIN_DIR = Path(f'/home/trucly/Documents/DATASET/PROJECTS/DEGREE/{CARD_TYPE}/train')
TEST_DIR = Path(f'/home/trucly/Documents/DATASET/PROJECTS/DEGREE/{CARD_TYPE}/test')
VALID_DIR = Path(f'/home/trucly/Documents/DATASET/PROJECTS/DEGREE/{CARD_TYPE}/valid')
if not TRAIN_DIR.exists():
    TRAIN_DIR.mkdir(parents=True)
if not TEST_DIR.exists():
    TEST_DIR.mkdir(parents=True)
if not VALID_DIR.exists():
    VALID_DIR.mkdir(parents=True)


def get_exts(json_path):
    img_exts = ['.jpg', '.png', '.PNG', '.JPG', '.jpeg', '.JPEG']
    for ext in img_exts:
        if os.path.exists(str(json_path.with_suffix(ext))):
            return ext


def move(string, json_paths, input_dir):
    for json_path in tqdm(json_paths):
        image = cv2.imread(str(json_path.with_suffix(get_exts(json_path))))
        image_name = json_path.stem + get_exts(json_path)
        with open(str(json_path)) as fp:
            info = json.load(fp)
        cv2.imwrite(os.path.join(input_dir, image_name), image)
        with open(os.path.join(input_dir, json_path.name), 'w') as fp:
            json.dump(obj=info, fp=fp, indent=4)


def split(input_dir, _list=False):
    if _list is False:
        json_paths = list(Path(input_dir).glob('**/*.json'))
    else:
        json_paths = input_dir
    print(f'data size {len(json_paths)}')
    num_train = int(len(json_paths) * 0.6)
    num_test = int(len(json_paths) * 0.8)
    print(f'train: {num_train}, test: {len(json_paths) - num_test}, val: {num_test - num_train}')
    shuffle(json_paths)
    move('------------------------------> TRAIN <--------------------------', json_paths[:num_train], str(TRAIN_DIR))
    move('------------------------------> VALID <--------------------------', json_paths[num_train:num_test], str(VALID_DIR))
    move('------------------------------> TEST <---------------------------', json_paths[num_test:], str(TEST_DIR))


def field_split(input_dir, field_require):
    '''
    Path must has .json extention
    '''
    no_fields = []
    have_fields = []
    json_paths = Path(input_dir).glob('**/*.json')
    for json_path in json_paths:
        with open(str(json_path)) as fp:
            info = json.load(fp)
        temp = 0
        for field in info['shapes']:
            if field_require == field['label']:
                have_fields.append(json_path)
                temp = 1
                break
        if temp == 0:
            no_fields.append(json_path)

    # for json_path in no_fields[:50]:
    #     image = cv2.imread(str(json_path.with_suffix('.jpg')))
    #     with open(str(json_path)) as fp:
    #         info = json.load(fp)
    #     cv2.imwrite(os.path.join('BACK_2014', info['imagePath']), image)
    #     with open(os.path.join('BACK_2014', json_path.name), 'w') as fp:
    #         json.dump(obj=info, fp=fp, indent=4)

    split(no_fields, True)
    split(have_fields, True)
    print("No_fields have {} files.".format(len(no_fields)))
    print("Have_fields have {} files.".format(len(have_fields)))


def mean_split(input_dir, field_require):
    '''
    Paths must have .json extention
    '''
    json_paths = Path(input_dir).glob('**/*.json')

    def get_mean_std():
        import numpy as np
        values = []
        for path in json_paths:
            with open(str(path)) as fp:
                info = json.load(fp)
            for field in info['shapes']:
                if field['label'] == field_require:
                    values.append(len(field['value'])) if 'value' in field else values.append(np.nan)
        return np.nanmean(values), np.nanstd(values)

    low = []
    high = []
    medium = []
    no_fields = []

    mean, std = get_mean_std()
    print(f'Mean: {mean}, std: {std}')
    json_paths = Path(input_dir).glob('**/*.json')
    for path in json_paths:
        with open(str(path)) as fp:
            info = json.load(fp)
        check = 0
        for field in info['shapes']:
            if field['label'] == field_require:
                if 'value' not in field or len(field['value']) < mean - 2 * std / 3:
                    low.append(path)
                elif len(field['value']) > mean + 2 * std / 3:
                    high.append(path)
                else:
                    medium.append(path)
                check = 1
                break
        if check == 0:
            no_fields.append(path)

    split(low, True)
    split(high, True)
    split(medium, True)
    split(no_fields, True)
    print('Low have {} images.'.format(len(low)))
    print('High have {} images.'.format(len(high)))
    print('Medium have {} images.'.format(len(medium)))
    print('No_fields have {} images'.format(len(no_fields)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('--type-split', default='1', help='1: random split, 2:field split, 3: mean split')
    parser.add_argument('--field-require', help='field require if chosen split type is 2 or 3')
    args = parser.parse_args()
    if args.type_split == '1':
        split(args.data_dir, False)
    elif args.type_split == '2':
        field_split(args.data_dir, args.field_require)
    else:
        mean_split(args.data_dir, args.field_require)
