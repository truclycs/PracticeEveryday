import os
import cv2
import numpy as np
from pathlib import Path


def order_points(points):
    assert len(points) == 4, 'Length of points must be 4'
    left = sorted(points, key=lambda p: p[0])[:2]
    right = sorted(points, key=lambda p: p[0])[2:]
    tl, bl = sorted(left, key=lambda p: p[1])
    tr, br = sorted(right, key=lambda p: p[1])
    return [tl, tr, br, bl]


def get_warped_images(image, pts):
    rect = order_points(pts)
    tl, tr, br, bl = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(widthA, widthB)

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(heightA, heightB)

    dst = np.array([[0, 0],
                    [maxWidth - 1, 0],
                    [maxWidth - 1, maxHeight - 1],
                    [0, maxHeight - 1]], dtype="float32")
    rect = np.array(rect, dtype="float32")
    M = cv2.getPerspectiveTransform(src=rect, dst=dst)
    warped = cv2.warpPerspective(image, M=M, dsize=(int(maxWidth), int(maxHeight)))
    return warped


def get_gt(image_name):
    digit = ''.join(c for c in image_name if c.isdigit())
    digit = int(digit)
    return "gt_" + str(digit) + ".txt", str(digit)


def check_overlap(x1, x2, a1, a2):
    alpha = 4
    if int(a2) - alpha < int(x1) or int(x2) < int(a1) + alpha:
        return False
    return True


patterns = ['*.txt', '*.jpg']
input_label_dir = Path('/home/trucly/Documents/dataset/vietnamese_vin/labels')
input_image_dir = Path('/home/trucly/Documents/dataset/vietnamese_vin/train_images')
output_dir = Path('/home/trucly/Documents/dataset/vietnamese_vin/text/line/train')

label_paths = []
image_paths = []
for pattern in patterns:
    label_paths += list(input_label_dir.glob(f'**/{pattern}'))
for pattern in patterns:
    image_paths += list(input_image_dir.glob(f'**/{pattern}'))


def cut_word():
    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        gt_name, digit = get_gt(image_name)
        image = cv2.imread(str(image_path))

        gt_path = str(input_label_dir.joinpath(gt_name))
        with open(gt_path, 'r') as f:
            boxes = f.read().split('\n')

        print(image_name)
        for i, box in enumerate(boxes):
            if not box:
                continue
            box = box.split(',')
            value = box[8]
            box = [int(x) for x in box[:8]]
            points = [(box[0], box[1]), (box[2], box[3]), (box[4], box[5]), (box[6], box[7])]
            word = get_warped_images(image, points)
            output_image = str(output_dir.joinpath(digit + '_' + str(i) + '.jpg'))
            cv2.imwrite(output_image, word)
            output_label = str(output_dir.joinpath(digit + '_' + str(i) + '.txt'))
            with open(output_label, 'a') as f:
                f.write(value)


def cutline():
    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        gt_name, digit = get_gt(image_name)
        image = cv2.imread(str(image_path))

        gt_path = str(input_label_dir.joinpath(gt_name))
        with open(gt_path, 'r') as f:
            boxes = f.read().split('\n')

        print(image_name)
        values = ""
        points = []
        for i in range(len(boxes) - 1):
            box = boxes[i]
            if not box:
                continue

            box = box.split(',')
            value = box[8]
            box = [int(x) for x in box[:8]]
            point = [(box[0], box[1]), (box[2], box[3]), (box[4], box[5]), (box[6], box[7])]
            point = order_points(point)

            if not values:
                values = value
                points = point
            else:
                values = values + ' ' + value
                # top_left = (min(points[0][0], points[3][0], point[0][0], point[3][0]), points[0][1])
                # bottom_left = (max(points[1][0], points[2][0], point[1][0], point[2][0]), points[1][1])
                # top_right = (min(points[0][0], points[3][0], point[0][0], point[3][0]), points[3][1])
                # bottom_right = (max(points[1][0], points[2][0], point[1][0], point[2][0]), points[2][1])
                # points = (top_left, bottom_left, top_right, bottom_right)
                points = points[:2] + point[2:]
                # top_left = (points[0][0], points[0][1])
                # bottom_left = (points[1][0], points[1][1])
                # top_right = (point[3][0], point[3][1])
                # bottom_right = (point[2][0], point[2][1])
                # points = (top_left, bottom_left, top_right, bottom_right)

            if not check_overlap(min(boxes[i][0], boxes[i][6]), max(boxes[i][2], boxes[i][4]),
                                 min(boxes[i + 1][0], boxes[i + 1][6]), max(boxes[i + 1][2], boxes[i + 1][4])):
                print(points)
                print(values)
                line = get_warped_images(image, points)
                output_image = str(output_dir.joinpath(digit + '_' + str(i) + '.jpg'))
                cv2.imwrite(output_image, line)
                output_label = str(output_dir.joinpath(digit + '_' + str(i) + '.txt'))
                with open(output_label, 'a') as f:
                    f.write(values)
                values = ""

        break


cutline()
