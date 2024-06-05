from pathlib import Path


file_predict = 'dataset/process_data/word_vnondb/test_all_wrong_case.txt'
file_replace = 'dataset/vnondb/word/test.txt'
save_file = 'dataset/process_data/word_vnondb/test_right_label_test/test_edited.txt'


text = {}
remove = []
with open(file_predict, 'r') as f:
    lines = f.read()
    lines = lines.split('\n')
    for line in lines:

        if len(line.split()) == 4:
            print(line)
            file, gt, pre, right = line.split()

            file = file.split('/')[-1]
            print(right)
            if right != 'x':
                text[file] = right
                file_out = Path('dataset/process_data/word_vnondb/test_right_label_test')
                file = file.split('.')[0]
                file_out = file_out.joinpath(file + '.txt')
                with open(file_out, 'w') as ff:
                    ff.write(right)
            else:
                remove.append(file)


new_label = []
with open(file_replace, 'r') as f:
    lines = f.read()
    lines = lines.split('\n')
    for line in lines:
        line = line.split('\t')
        if line[0] in text:
            line[1] = text[line[0]]
        if line[0] in remove:
            continue
        new_label.append(line)


with open(save_file, 'w') as f:
    for label in new_label:
        f.write(label[0] + '\t' + label[1] + '\n')
