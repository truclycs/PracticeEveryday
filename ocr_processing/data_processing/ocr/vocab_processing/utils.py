import yaml
import json
from pathlib import Path
from typing import List, Union


def load_json(path):
    with open(path, mode='r', encoding='utf-8') as f:
        json_dict = json.load(f)
        f.close()
    return json_dict


def load_yaml(yaml_path: str):
    with open(yaml_path, mode='r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data


def read_file(path: Union[Path, str]):
    with open(path, mode='r', encoding='utf-8') as f:
        data = f.read()
        f.close()
    return data


def write_file(content: str, output_path: Path):
    with open(output_path, mode='w', encoding='utf-8') as f:
        f.write(content)
        f.close()
    return True


def write_multi_lines(content: List, output_path: Path):
    with open(output_path, mode='w', encoding='utf-8') as f:
        for line in content:
            line = str(line)
            f.write(f"{line}\n")
        f.close()
    return True


def read_multi_lines(path: Path):
    with open(path, mode='r', encoding='utf-8') as f:
        content = f.readlines()
        f.close()
    content = [x.strip() for x in content]
    return content
