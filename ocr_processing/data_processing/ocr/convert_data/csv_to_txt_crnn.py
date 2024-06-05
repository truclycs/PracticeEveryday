import csv


csv_file = "data/all_word.csv"


with open(csv_file, 'r') as my_input_file:
    for index, filename, value in csv.reader(my_input_file, delimiter='\t'):
        new_filename = "data/word/" + filename + ".txt"
        with open(new_filename, "a") as fw:
            fw.write(value)
