import json
import argparse
from pathlib import Path

from vietnamese_normalization import vietnamese_normalize


def norm(paths, output_dir):
    for path in paths:
        filename = str(path)
        print(filename)
        with open(filename, 'r') as f:
            obj = json.load(f)

        shapes = obj['shapes']

        for i, x in enumerate(shapes):
            if len(x.get('value', '')) > 0:
                value = x['value']
                obj['shapes'][i]['value'] = "".join(vietnamese_normalize(value))

        with open(output_dir + filename.split('/')[-1], 'w') as f:
            json.dump(obj, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='path to file')
    parser.add_argument('--output-dir', default=None)
    parser.add_argument('--pattern', default='*.json')
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    pattern = args.pattern
    input_dir = Path(args.input_dir)
    paths = list(input_dir.glob(f'**/{pattern}'))

    norm(paths, args.output_dir)
