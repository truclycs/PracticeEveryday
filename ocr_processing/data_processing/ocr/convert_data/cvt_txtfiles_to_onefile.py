input_dir = ''
output = ''
text_file = ''


with open(text_file, 'r') as f:
    files = f.read().split('\n')


labels = []
for file in files:
    if file:
        filename = ".".join(file.split('.')[:-1]) + '.txt'
        with open(input_dir + filename, 'r') as f:
            label = f.read()
        labels.append(file + '\t' + label + '\n')


with open(output, 'w') as f:
    for label in labels:
        f.write(label)
