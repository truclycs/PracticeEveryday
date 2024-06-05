import cv2
import argparse
from pathlib import Path


def write_multi_lines(content, output_path):
    with open(output_path, mode='w', encoding='utf-8') as f:
        for line in content:
            f.write(f"{line}\n")
        f.close()
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=str)
    parser.add_argument("--output-dir", type=str, default="rot_out_new/")
    parser.add_argument("--patterns", nargs="+", default=["*.jpg"])
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    image_paths = []
    for pattern in args.patterns:
        image_paths += list(input_dir.glob(pattern))

    idx = 0
    key = None
    images = dict()

    angle = 0
    while idx < len(image_paths) and key != ord("q"):

        image_path = image_paths[idx]
        if str(image_path) in images.keys():
            image = images.get(str(image_path))
        else:
            image = cv2.imread(str(image_path))
        images[str(image_path)] = image

        cv2.imshow(str(image_path), cv2.resize(image, dsize=(0, 0), fx=8.0, fy=8.0))

        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

        if key == ord("r"):
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            images[str(image_path)] = image
        elif key == ord("q"):
            break
        # Left arrow
        elif key == ord("j"):
            idx -= 1
            continue
        # Right arrow
        elif key == ord("l"):
            idx += 1
            continue
        elif key == ord("s"):
            output_path = output_dir.joinpath(image_path.relative_to(input_dir))
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True)
            cv2.imwrite(str(output_path), images[str(image_path)])
            del images[str(image_path)]
            print(f"Saved {image_path}")
            idx += 1
            angle = 0
            continue
