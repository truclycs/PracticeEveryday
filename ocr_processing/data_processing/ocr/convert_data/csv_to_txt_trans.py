import csv 


csv_file = "data/convert_data/train_line.csv"
txt_file = "data/convert_data/train_line.txt"


with open(txt_file, "w") as my_output_file:
    with open(csv_file, "r") as my_input_file:
        for index, filename, value in csv.reader(my_input_file, delimiter='\t'):
            print(filename, value, sep='\n')
            my_output_file.write(filename + '.png\t' + value + '\n')
    my_output_file.close()
