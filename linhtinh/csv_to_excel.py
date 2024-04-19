import os
import csv
import argparse
from pathlib import Path
from xlsxwriter.workbook import Workbook


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='path to csv file.')
    parser.add_argument('--output-dir', default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else Path(args.input_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    csv_files = Path(args.input_dir)

    for csvfile in csv_files.glob(os.path.join('.', '*.csv')):
        workbook = Workbook(output_dir.joinpath(str(Path(csvfile).stem) + '.xlsx'))
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()