import logging

from tqdm import tqdm
from pathlib import Path
from typing import Set, List

from utils import read_file, write_file, write_multi_lines, load_yaml


class Vocab:
    def __init__(self, input_dir: str, output_dir: str, limit_num_char: int = 128, replace_OOV: bool = False, ignore_OOV: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        self.limit_num_char = limit_num_char
        self.exceeded_limit_paths = list()

        self.label_ext = "txt"
        self._image_exts = ['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'PNG']
        self._label_file_name = "train_path.txt"
        self._vocab_file_name = "vocab_char.txt"

        self.list_label_paths = list()

        self.vocab = set()
        self._standard_vocab = set(read_file('standard_vocab'))

        self.replace_OOV = replace_OOV
        self.OOV_Char = load_yaml("OOV_Char.yaml")

        self.ignore_OOV = ignore_OOV
        self.OOV_paths = list()

        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)

        self.setup_logging()

    def setup_logging(self):
        log_filename = self.output_dir.joinpath("error_log.txt")
        self.logger = logging.getLogger()
        handler = logging.FileHandler(str(log_filename), mode='w', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.info("=" * 80)

    def check_valid_vocab(self, set_of_char: Set):
        new_char = set_of_char.difference(self._standard_vocab)
        return new_char

    def replace_special_char(self, set_of_new_char: Set, line_content: str):
        fix_label = False
        for char in set_of_new_char:
            if char in self.OOV_Char.get('special_char', []):
                fix_label = True
                line_content = line_content.replace(char, self.OOV_Char.get('mapping_char', {}).get(char, char))
        return line_content, fix_label

    def get_image_paths(self, list_label_paths: List[Path]):
        list_image_paths = []
        for label_path in list_label_paths:
            for ext in self._image_exts:
                if label_path.with_suffix(f".{ext}").exists():
                    list_image_paths.append(label_path.with_suffix(f".{ext}"))
                    break
        return list_image_paths

    def save_vocab(self):
        str_vocab = "".join(sorted(self.vocab))
        voca_path = self.output_dir.joinpath(self._vocab_file_name)
        write_file(str_vocab, output_path=voca_path)

    def save_image_paths(self, list_label_paths: List[Path], file_name: str):
        list_image_paths = self.get_image_paths(list_label_paths)
        label_file_path = self.output_dir.joinpath(file_name)
        write_multi_lines(list_image_paths, label_file_path)

    def get_vocab(self):

        list_label_paths = list(self.input_dir.rglob(f"*.{self.label_ext}"))
        max_len_text = 0
        new_char_set = set()
        for label_path in tqdm(list_label_paths):
            data = read_file(label_path)
            if len(data) == 0:
                self.logger.error(f"Empty data: {str(label_path)}")
                continue
            max_len_text = max(len(data), max_len_text)
            if len(data) > self.limit_num_char:
                print(label_path, len(data))
                self.exceeded_limit_paths.append(label_path)

            set_of_char = set(data)
            self.vocab.update(set_of_char)
            new_char = self.check_valid_vocab(set_of_char)
            if len(new_char) > 0:
                new_char_set.update(new_char)
                try:
                    self.logger.warning(f"{str(label_path)} - Out of Standard Vocab: {new_char}")
                except Exception as e:
                    print(e)
                if self.replace_OOV:
                    data, fix_label = self.replace_special_char(new_char, data)
                    if fix_label:
                        write_file(data, label_path)

                self.OOV_paths.append(label_path)
            else:
                self.list_label_paths.append(label_path)

        self.save_vocab()
        self.save_image_paths(self.list_label_paths, file_name=self._label_file_name)
        # save OOV paths
        self.save_image_paths(self.OOV_paths, file_name="OOV_path.txt")
        # save exceeded_limit_char paths
        self.save_image_paths(self.exceeded_limit_paths, file_name="exceeded_limit_path.txt")

        self.logger.info(f"The max text length = {max_len_text}")
        write_file("\n".join(new_char_set), self.output_dir.joinpath("OOV.txt"))
