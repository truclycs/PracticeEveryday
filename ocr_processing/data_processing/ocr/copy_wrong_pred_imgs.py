import shutil
from pathlib import Path


file_predict = '/home/trucly/Documents/DATASET/PROJECTS/DEGREE/04_main_text_lines/wrong_case.txt'
s_folder = Path('/home/trucly/Documents/DATASET/PROJECTS/DEGREE/04_main_text_lines/images')
e_folder = Path('/home/trucly/Documents/DATASET/PROJECTS/DEGREE/04_main_text_lines/wrong_pred_images')

text = []
file_names = []
with open(file_predict, 'r') as f:
    lines = f.read()
    lines = lines.split('\n')
    for line in lines:
        file, gt, pre = line.split('\t')
        file = file.split('/')[-1]
        if gt.lower() != pre.lower():
            file_names.append(file)
            text.append(line)
            shutil.copy(s_folder.joinpath(file), e_folder.joinpath(file))
            shutil.copy(s_folder.joinpath(file.replace('jpg', 'txt')), e_folder.joinpath(file.replace('jpg', 'txt')))

text = sorted(text)
text_output = 'text_sorted.txt'
with open(e_folder.joinpath(text_output), 'w') as f:
    for t in text:
        f.write(t + '\n')

text_output = 'wrong_pred_files.txt'
file_names = sorted(file_names)
with open(e_folder.joinpath(text_output), 'w') as f:
    for t in file_names:
        f.write(t + '\n')
