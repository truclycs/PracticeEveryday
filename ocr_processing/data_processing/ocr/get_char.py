import sys
from tqdm import tqdm
from pathlib import Path


def readFile(path):
    with open(path, mode='r', encoding='utf-8') as f:
        data = f.read()
    return data


def writeFile(content, path='cur_char.txt'):
    with open(path, mode='w', encoding='utf-8') as f:
        f.write(content)


def getCharacters(list_lables=None):
    max_len = 0
    lst_chars = set()
    lst_img_paths = list()
    image_exts = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']

    for label in tqdm(list_lables):
        data = readFile(label)
        lst_chars.update(set(data))
        if len(data) > max_len:
            max_len = len(data)
        cur_img_path = None
        for ext in image_exts:
            if label.with_suffix(f".{ext}").exists():
                cur_img_path = label.with_suffix(f".{ext}")
                cur_img_path = str(cur_img_path).replace('\\', '/')
                break
        if cur_img_path:
            lst_img_paths.append(cur_img_path)
    list_char = ""
    for char in lst_chars:
        list_char += char
    newlist = ''.join(sorted(list_char))
    writeFile(newlist)
    print(max_len)
    return lst_img_paths


def writeFileLabels(data, path):
    with open(path, mode='w', encoding='utf-8') as f:
        for line in data:
            f.write('%s\n' % line)


def scan(data_path):
    list_labels = list(Path(data_path).rglob('*.txt'))
    list_img_paths = getCharacters(list_labels)
    writeFileLabels(list_img_paths, 'full_data.txt')


if __name__ == "__main__":
    scan(*sys.argv[1:])
