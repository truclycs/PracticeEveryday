import json
import argparse
from pathlib import Path


def check_difference(path1, path2):
    result = {}

    for p1 in path1:
        p1 = str(p1)
        file1 = p1.split('/')[-1]
        for p2 in path2:
            p2 = str(p2)
            file2 = p2.split('/')[-1]

            if file1 == file2:
                with open(p1, "r") as f:
                    info1 = json.load(f)

                with open(p2, "r") as f:
                    info2 = json.load(f)

                shape1 = info1['shapes']
                shape2 = info2['shapes']

                for s1 in shape1:
                    label1 = s1['label']
                    for s2 in shape2:
                        label2 = s2['label']

                        if label1 == label2:
                            if s1['value'] != s2['value']:
                                if p1 in result:
                                    result[p1].append((label1, s1['value'], s2['value']))
                                else:
                                    result[p1] = [(label1, s1['value'], s2['value'])]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir1', help='path to original file')
    parser.add_argument('--input-dir2', help='path to fixed file')
    parser.add_argument('--patterns', nargs="+", default=['*.jpg', '*.png', '*.jpeg', '*.JPG', '*.PNG', '*.JPEG'])

    args = parser.parse_args()

    input_dir1 = Path(args.input_dir1)
    input_dir2 = Path(args.input_dir2)
    patterns = args.patterns

    path1 = []
    path2 = []
    for pattern in patterns:
        path1 += list(input_dir1.glob(f'**/{pattern}'))
    for pattern in patterns:
        path2 += list(input_dir2.glob(f'**/{pattern}'))

    files = check_difference(path1, path2)
    print(len(files))
    for file in files:
        print(file, files[file])
