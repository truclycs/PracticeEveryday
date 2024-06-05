import os
import argparse
import json
from pathlib import Path
import shutil


BOOK_FIELDS = {
    "BOX_1": [
        "K_INSUR_NUM",
        "K_NAME",
        "K_DOB",
        "K_SEX",
        "K_NAT",
        "K_ID"
    ],
    "BOX_2": [
        "V_INSUR_NUM",
        "V_NAME",
        "V_DOB",
        "V_SEX",
        "V_NAT",
        "V_ID",
        "TEXTLINE"     
    ],
    "BOX_3": [
        "INSUR_PLACE",
        "INSUR_DATE",
        "K_SIGN",
        "STAMP",
        "V_SIGN",
        "V_SIGN_NAME"
    ]
}


PROGRESS_FIELDS = {
    "PROGRESS_1": [
        "K_NAME",
        "V_NAME",
        "K_DOB",
        "V_DOB",
        "K_INSUR_NUM",
        "V_INSUR_NUM",
        "PAGE_NUM",
    ],
    "PROGRESS_2": [
        "K_BEGIN_DAY",
        "HEADER",
        "V_BEGIN_DAY",
        "K_BASE",
        "K_END_DAY",
        "K_RATIO",
    ],
    "PROGRESS_3": [
        "K_POW",
        "K_HT_TT",
        "K_OD_TS",
        "K_TNLD_BNN",
        "K_BHTN",
    ],
    "PROGRESS_4": [
        "V_END_DAY",
        "V_HT_TT_BASE",
        "V_OD_TS_BASE",
        "V_TNLD_BNN_BASE",
        "V_BHTN_BASE",
        "V_SALARY_LEVEL_BASE",
    ],
}


TYPES = ["BOX_1", "BOX_2", "BOX_3",
         "PROGRESS_1", "PROGRESS_2", "PROGRESS_3", "PROGRESS_4"]


def isInsurBook(shape):
    return any(info["label"] == "INSUR_BOOK" for info in shape if "label" in info)


def isInsurProgress(shape):
    return any(info["label"] == "INSUR_PROGRESS" for info in shape if "label" in info)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='Path to original files')
    parser.add_argument('--patterns', nargs="+", default=['*.jpg', '*.png', '*.jpeg', '*.JPG', '*.PNG', '*.JPEG'])
    args = parser.parse_args()
    
    image_paths = []
    patterns = args.patterns
    for pattern in patterns:
        image_paths += list(Path(args.input_dir).glob(f'**/{pattern}'))

    for type in TYPES:
        for image_path in image_paths:
            json_path = image_path.with_suffix(".json")
            with open(str(json_path), "r") as f:
                data = json.load(f)
            f.close()

            shapes = data["shapes"]
            KEEP_LABELS = []
            if isInsurBook(shapes) and type in ["BOX_1", "BOX_2", "BOX_3"]:
                KEEP_LABELS = BOOK_FIELDS
            elif isInsurProgress(shapes) and type in ["PROGRESS_1", "PROGRESS_2", "PROGRESS_3", "PROGRESS_4"]:
                KEEP_LABELS = PROGRESS_FIELDS
            else:
                continue

            new_shapes = []
            for info in shapes:
                if info["label"] in KEEP_LABELS[type]:
                    info["value"] = ""
                    new_shapes.append(info)
                    data["shapes"] = new_shapes

                    print(json_path, len(data))

                    sub_path = os.path.dirname(json_path)
                    new_folder = type + "_" + sub_path
                    if not Path(new_folder).exists():
                        Path(new_folder).mkdir(parents=True)

                    new_image_path = Path(new_folder + "/" + image_path.name)
                    new_json_path = new_image_path.with_suffix('.json')

                    data['imagePath'] = new_image_path.name
                    
                    with new_json_path.open(mode="w", encoding="utf8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                    shutil.copy(str(image_path), str(new_image_path))

