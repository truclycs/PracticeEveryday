from Vocab import Vocab
from utils import load_yaml

if __name__ == '__main__':
    cfg_path = "config.yaml"
    config = load_yaml(yaml_path=cfg_path)
    runner = Vocab(**config)
    runner.get_vocab()
