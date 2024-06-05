import sys
from random import shuffle


def readFile(path):
    with open(path, mode='r', encoding='utf-8') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content


def writeFile(data, path):
    with open(path, mode='w', encoding='utf-8') as f:
        for line in data:
            f.write('%s\n'%line)


def shuffle_dataset(label_path):
    data = readFile(label_path)
    shuffle(data)
    writeFile(data, label_path)


if __name__ == "__main__":
    shuffle_dataset(*sys.argv[1:])
