from pathlib import Path
from natsort import natsorted
import pandas as pd


if __name__=="__main__":
    image_paths = list(Path("BHXH_splitted").glob(f'**/*.*g'))
    # import pdb; pdb.set_trace();
    # image_paths = natsorted(image_paths, key=lambda x: x.name)
    image_paths = natsorted(image_paths, key=lambda x: x.parent.name)
    print(len(image_paths))

    # image_names = [image_path.name for image_path in image_paths]
    image_names = [image_path.parent.name + "/" + image_path.name for image_path in image_paths]

    data = {
        "filename": image_paths
    }

    df = pd.DataFrame(data)

    # saving the dataframe
    df.to_csv('BHXH_splitted/bhxh.csv', index=False)
