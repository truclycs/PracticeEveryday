PATH = '/home/trucly/Documents/DATASET/PROJECTS/DEGREE/degree_testing.txt'
OUT_PATH = '/home/trucly/Documents/DATASET/PROJECTS/DEGREE/txt/'
with open(PATH, 'r') as f:
    lines = f.readlines()

filenames = []
for line in lines:
    filename, value = line.split('\t')
    filenames.append(filename)
    with open(OUT_PATH + filename.replace('jpg', 'txt'), 'w') as f:
        f.write(value)
    print(filename, value.strip())

with open(OUT_PATH + 'test.txt', 'w') as f:
    for filename in filenames:
        f.write(filename + '\n')
