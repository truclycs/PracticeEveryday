filename = 'labels_0916.json'
new_filename = "train_annotation.txt"


with open(filename, 'r') as fr:
    pre_ = fr.read()
    lines = pre_.split('\n')    
    for i in range(1, len(lines) - 1):
        name, content = lines[i].split(': "')
        content = name[5:-1] + '\t' + content[:-2]
        with open(new_filename, "a") as fw:
            fw.write(content + '\n')    