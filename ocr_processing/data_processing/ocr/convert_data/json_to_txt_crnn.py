filename = 'labels.json'


with open(filename, 'r') as fr:
    pre_ = fr.read()
    lines = pre_.split('\n')
    for i in range(1, len(lines) - 1):
        name, content = lines[i].split('.png": "')
        name = name[5:]
        content = content[:-2]
        new_filename = name + ".txt" 
        with open(new_filename, "a") as fw:
            fw.write(content)      