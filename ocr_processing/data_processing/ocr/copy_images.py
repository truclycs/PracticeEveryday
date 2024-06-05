import argparse
import shutil
from pathlib import Path
from natsort import natsorted


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='path to txt file.')
    parser.add_argument('--output-dir', default=None)
    parser.add_argument('--starting-file', default=1)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else Path(args.input_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    label_paths = natsorted(Path(args.input_dir).glob('**/*.txt'), key=lambda x: x.stem)

    for idx, txt_path in enumerate(label_paths[int(args.starting_file) - 1:], int(args.starting_file)):
        print('**' * 30)
        print(txt_path)

        image_path = str(txt_path).replace('txt', 'jpg')

        with open(txt_path, 'r') as f:
            label = f.read().lower()

        if "thượng tá" in label or "thiếu tá" in label or "đại tá" in label or "trung tá" in label:
            print('move')
            shutil.copy(txt_path, output_dir)
            shutil.copy(Path(image_path), output_dir)