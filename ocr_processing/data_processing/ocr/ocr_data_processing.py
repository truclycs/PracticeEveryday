import json
import cv2
import shutil
import argparse
import numpy as np
from pathlib import Path
from vietnamese_normalization import vietnamese_normalize

# START_KEYS = ['ORGAN_NAME', 'DEG_NAME', 'V_NAME', 'V_GENDER', 'V_MAJOR',
#               'V_RANKING', 'V_MODE', 'ISSUE_DATE', 'V_SIGN_NAME', 'V_SERIAL_NO',
#               'V_REF_NO', 'V_GRAD_YEAR', 'V_DOB', 'DATE']

# START_KEYS = ['header_1', 'header_2', 'v_nat', 'v_name_1', 'v_name_2', 'v_eth',
#               'v_bd', 'v_sex', 'v_de', 'v_pn', 'v_id', 'v_bp', 'mrz1', 'mrz2']


class OCRDataProcessing():
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

    def _order_points(self, points):
        assert len(points) == 4, 'Length of points must be 4'
        left = sorted(points, key=lambda p: p[0])[:2]
        right = sorted(points, key=lambda p: p[0])[2:]
        tl, bl = sorted(left, key=lambda p: p[1])
        tr, br = sorted(right, key=lambda p: p[1])
        return [tl, tr, br, bl]

    def _get_warped_images(self, image, pts):
        rect = self._order_points(pts)
        tl, tr, br, bl = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(widthA, widthB)

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(heightA, heightB)

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        rect = np.array(rect, dtype="float32")
        M = cv2.getPerspectiveTransform(src=rect, dst=dst)
        warped = cv2.warpPerspective(image, M=M, dsize=(int(maxWidth), int(maxHeight)))

        return warped

    def _is_label(self, label):
        return any([label.startswith(key.upper()) for key in START_KEYS])

    def copy_image(self):
        # label_paths = natsorted(Path(args.input_dir).glob('**/*.txt'), key=lambda x: x.stem)

        # for idx, txt_path in enumerate(label_paths[int(args.starting_file) - 1:], int(args.starting_file)):
        #     print('**' * 30)
        #     print(txt_path)

        #     image_path = str(txt_path).replace('txt', 'jpg')

        #     with open(txt_path, 'r') as f:
        #         label = f.read().lower()

        #     if "thượng tá" in label or "thiếu tá" in label or "đại tá" in label or "trung tá" in label:
        #         print('move')
        #         shutil.copy(txt_path, output_dir)
        #         shutil.copy(Path(image_path), output_dir)

        file_label = 'annotation/vtp/val.txt'
        s_folder = Path('current_textline')
        e_folder = Path('vtp_split/val')

        with open(file_label, 'r') as f:
            lines = f.read().split('\n')

        file_names = {}
        for line in lines:
            image_file, gt = line.split('\t')
            file_name = image_file.split('.')[0]
            gt_file = file_name + '.txt'
            if file_name in file_names:
                print(file_name)
            else:
                file_names[file_name] = 1

            shutil.copy(s_folder.joinpath(image_file), e_folder.joinpath(image_file))
            shutil.copy(s_folder.joinpath(gt_file), e_folder.joinpath(gt_file))

    def cut_textline(self, paths):
        filenames = []
        filename_label = []
        values = []
        for path in paths:
            count = 0
            filename = str(path)
            with open(filename.replace(filename.split('.')[-1], 'json'), 'r') as f:
                obj = json.load(f)

            image_name = obj['imagePath']
            image = cv2.imread(str(self.input_dir.joinpath(image_name)))

            shapes = obj['shapes']
            # import pdb; pdb.set_trace()
            for x in shapes:
                point = x['points']
                label = x['label']
                # if self._is_label(label) and len(x.get('value', '')) > 0:
                if len(x.get('value', '')) > 0:
                    value = x['value']
                    if len(point) == 4:
                        line = self._get_warped_images(image, self._order_points(point))
                    elif len(point) == 2:
                        if (point[0][0] > point[1][0]):
                            point[0], point[1] = point[1], point[0]
                        line = image[int(point[0][1]):int(point[1][1]), int(point[0][0]):int(point[1][0])]
                    else:
                        continue

                    if len(line) != 0:
                        filename = path.stem + '_' + label + '_' + str(count)
                        value = "".join(vietnamese_normalize(value))
                        value = value.replace('–', '-')
                        folder_path = self.output_dir.joinpath(label)
                        if not folder_path.exists():
                            folder_path.mkdir(parents=True)
                        image_path = folder_path.joinpath(filename + '.jpg')
                        cv2.imwrite(str(image_path), line)
                        text_path = folder_path.joinpath(filename + '.txt')
                        with open(str(text_path), 'wt') as f:
                            f.write(value)

                        count += 1
                        filenames.append(filename + '.jpg')
                        filename_label.append(label + '/' + filename + '.jpg')
                        values.append(value)

        label_path = self.output_dir.joinpath('label.txt')
        with open(str(label_path), 'a') as f:
            for filename, value in zip(filenames, values):
                f.write(filename + '\t' + value + '\n')

        filename_path = self.output_dir.joinpath('filename.txt')
        with open(str(filename_path), 'a') as f:
            for filename in filenames:
                f.write(filename + '\n')

        filename_label_path = self.output_dir.joinpath('filename_label.txt')
        with open(str(filename_label_path), 'a') as f:
            for filename in filename_label:
                f.write(filename + '\n')

    def convert_text_line_2_one_file(self, text_file):
        with open(text_file, 'r') as f:
            files = f.read().split('\n')

        labels = []
        for file in files:
            if file:
                filename = ".".join(file.split('.')[:-1]) + '.txt'
                with open(self.input_dir + filename, 'r') as f:
                    label = f.read()
                labels.append(file + '\t' + label + '\n')

        with open(self.output_dir, 'w') as f:
            for label in labels:
                f.write(label)

    def _other_process(self):
        val = 'dataset/vnondb/word/val.txt'
        with open(val, 'r') as f:
            data = f.read().split('\n')
            for line in data:
                if 'ƒ' in line:
                    print(line)

    def get_dict(self):
        data_file = '/home/trucly/Documents/DATASET/PROJECTS/NATCOM/PASSPORT/textlines/label.txt'
        with open(data_file, "r") as f:
            data = f.read().split('\n')
        dict_ = {}
        for line in data:
            filename, value = line.split('\t')
            for c in value:
                dict_[c] = 1

        return "".join(sorted(list(dict_.keys())))

    def get_dict_from_json_label(self, paths):
        dict = {}
        for path in paths:
            print(path)
            path = str(path)
            with open(str(path), 'r') as f:
                label = f.read()
                for c in label:
                    dict[c] = 1

        return "".join(sorted(list(dict.keys())))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='path to file')
    parser.add_argument('--output-dir', default=None)
    parser.add_argument('--patterns', nargs="+", default=['*.jpg', '*.png', '*.jpeg', '*.JPG', '*.PNG', '*.JPEG'])
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    # if not output_dir.exists():
        # output_dir.mkdir(parents=True)

    patterns = args.patterns
    input_dir = Path(args.input_dir)
    paths = []
    for pattern in patterns:
        paths += list(input_dir.glob(f'**/{pattern}'))

    process = OCRDataProcessing(input_dir, output_dir)
    process.cut_textline(paths)
    # print(process.get_dict())
    # print(process.get_dict_from_json_label(paths))


# csv to crnn
# import csv

# csv_file = "data/all_word.csv"


# with open(csv_file, 'r') as my_input_file:
#     for index, filename, value in csv.reader(my_input_file, delimiter='\t'):
#         new_filename = "data/word/" + filename + ".txt"
#         with open(new_filename, "a") as fw:
#             fw.write(value)

# csv to  trans
# import csv

# csv_file = "data/convert_data/train_line.csv"
# txt_file = "data/convert_data/train_line.txt"


# with open(txt_file, "w") as my_output_file:
#     with open(csv_file, "r") as my_input_file:
#         for index, filename, value in csv.reader(my_input_file, delimiter='\t'):
#             print(filename, value, sep='\n')
#             my_output_file.write(filename + '.png\t' + value + '\n')
#     my_output_file.close()


# json to crnn
# filename = 'labels.json'


# with open(filename, 'r') as fr:
#     pre_ = fr.read()
#     lines = pre_.split('\n')
#     for i in range(1, len(lines) - 1):
#         name, content = lines[i].split('.png": "')
#         name = name[5:]
#         content = content[:-2]
#         new_filename = name + ".txt"
#         with open(new_filename, "a") as fw:
#             fw.write(content)

# json_to_txt_trans
# filename = 'labels_0916.json'
# new_filename = "train_annotation.txt"


# with open(filename, 'r') as fr:
#     pre_ = fr.read()
#     lines = pre_.split('\n')
#     for i in range(1, len(lines) - 1):
#         name, content = lines[i].split(': "')
#         content = name[5:-1] + '\t' + content[:-2]
#         with open(new_filename, "a") as fw:
#             fw.write(content + '\n')
