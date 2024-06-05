from pathlib import Path
import json
import shutil


if __name__=="__main__":
    json_paths = list(Path("VOTECARD_TYPE2").glob("*.json"))

    # keep_labels = ["K_ID", "K_NAME", "K_BD", "K_BP",
    #                "K_LOCAL", "K_ISSUE_DATE", "K_OTHER_CODE",
    #                "K_SEX", "K_A", "K_SIGN_S", "K_SIGN_E"]

    keep_labels = ["K_ID", "K_NAME", "K_BD", "K_BP",
                   "K_LOCAL", "K_ISS_DATE", "K_OTHER_CODE", "K_CEDULA",
                   "K_SEX", "K_A", "K_SIGN_S", "K_SIGN_E", "UNKNOWN"]


    for json_path in json_paths:
        with open(str(json_path), "r") as f:
            data = json.load(f)
        f.close()

        new_shapes = []

        for shape in data["shapes"]:
            if shape["label"] in keep_labels:
                shape["value"] = ""
                new_shapes.append(shape)

        print(str(json_path), len(new_shapes))
        data["shapes"] = new_shapes

        save_path = "MOZ_VOTERCARD_KEYS_802/VOTECARD_TYPE2/" + json_path.name
        with Path(save_path).open(mode="w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        image_path = json_path.with_suffix(".jpg")
        save_path = "MOZ_VOTERCARD_KEYS_802/VOTECARD_TYPE2/" + image_path.name

        shutil.copy(str(image_path), str(save_path))
