import re
import numpy as np
import argparse
from pathlib import Path
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import (QFont, QFontMetrics, QImage, QIntValidator, QKeyEvent, QPalette, QPixmap, QKeySequence)
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QScrollArea, QScrollBar, QShortcut, QSizePolicy, QVBoxLayout, QWidget)

WIN_SIZE = (1024, 128)


def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


class SwitchSignal(QWidget):

    next = pyqtSignal()
    prev = pyqtSignal()

    def keyPresseEvent(self, ev: QKeyEvent):
        super().keyPressEvent(ev)
        if ev.key() == Qt.Key_Up:
            print('KEy UP')
            self.prev.emit()
        elif ev.key() == Qt.Key_Down:
            print('KEy Down')
            self.next.emit()


class Dataset():
    def __init__(self, log_file: Path, list_file: Path, image_dir: Path):
        log_lines = [line.strip() for line in open(log_file, 'rt', encoding='utf-8').readlines()]
        image_lines = [line.strip() for line in open(list_file, 'rt', encoding='utf-8').readlines()]
        # false_idx = [i for i, line in enumerate(log_lines) if line.split()[-1] == 'False']
        data_file = Path(list_file)
        self.note_file = Path(list_file).with_name(f"note_{data_file.name}")
        false_idx = []
        for idx, (log_line, image_line) in enumerate(zip(log_lines, image_lines)):
            if log_line.split()[-1] == 'False':
                false_idx.append(idx)
        if len(false_idx) == 0:
            print('Nothing to do! Nice!')
            exit(0)

        self.textlines = []
        for idx in false_idx:
            log_line = log_lines[idx]
            predict = self.extract_predict(log_line)
            image_path = Path(image_lines[idx])

            textline = TextLine(predict, image_path)
            self.textlines.append(textline)

    def extract_predict(self, line: str):
        pattern = r'\=\>.*, gt'
        predict_text = re.findall(pattern, line)[0][3:-4].rstrip()
        return predict_text

    def __getitem__(self, idx):
        return self.textlines[idx]

    def __len__(self):
        return len(self.textlines)


class TextLine():
    def __init__(self, predict_text: str, image_path: Path):
        self.predict_text = predict_text
        self.image_path = image_path
        self.txt_path = self.image_path.with_suffix('.txt')

    def textline(self):
        return open(str(self.txt_path), 'rt', encoding='utf-8').readline().strip()

    def save(self, new_label):
        txt_path = Path(self.image_path).with_suffix('.txt')
        open(txt_path, 'wt', encoding='utf-8').write(new_label)

    def save_image(self, new_image: Image.Image):
        new_image.save(self.image_path)


class App(QMainWindow):
    def __init__(self, log_file: Path, list_file: Path, image_dir: Path):
        super().__init__()

        self.image = QImage()
        self.scaleFactor = 1.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setFixedSize(1024, 64)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(False)

        layout = QVBoxLayout()

        ##################
        # Index
        ##################
        index_widget = QWidget()
        index_layout = QHBoxLayout()
        index_layout.setAlignment(Qt.AlignLeft)

        self.current_line_index = QLineEdit(f'{0:05d}')
        self.current_line_index.setValidator(QIntValidator())
        self.current_line_index.setMaxLength(5)
        self.current_line_index.setFixedWidth(50)
        self.current_line_index.editingFinished.connect(self.jump_to_line_index)
        self.total_line_label = QLabel('/0')
        index_layout.addWidget(self.current_line_index)
        index_layout.addWidget(self.total_line_label)

        self.current_path_label = QLineEdit('path')
        self.current_path_label.setFixedWidth(1000)
        self.current_path_label.setReadOnly(True)
        index_layout.addWidget(self.current_path_label)

        index_widget.setLayout(index_layout)
        layout.addWidget(index_widget)

        label = QLabel('Image:')
        layout.addWidget(label)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setVisible(False)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

        label = QLabel('Label:')
        layout.addWidget(label)

        self.label_text = QLineEdit("label")
        f = self.label_text.font()
        f.setPointSize(27) # sets the size to 27
        f.setStyleHint(QFont.Monospace)
        self.label_text.setFont(f)
        self.label_text.setFocus()
        self.label_text.setReadOnly(False)
        layout.addWidget(self.label_text)

        label = QLabel('OCR Predict:')
        layout.addWidget(label)

        self.pred_text = QLineEdit("pred")
        f = self.pred_text.font()
        f.setPointSize(27) # sets the size to 27
        f.setStyleHint(QFont.Monospace)
        self.pred_text.setFont(f)
        self.pred_text.setFocus()
        self.pred_text.setReadOnly(True)
        layout.addWidget(self.pred_text)

        signal_widget = SwitchSignal()
        signal_widget.next.connect(self.next_image)
        signal_widget.prev.connect(self.prev_image)
        layout.addWidget(signal_widget)

        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

        self.resize(WIN_SIZE[0], WIN_SIZE[1])

        self.current_index = 0

        self.dataset = Dataset(log_file, list_file, image_dir)

        if len(self.dataset) == 0:
            print('Nothing to do! Nice!')
            exit(0)

        self.label_text.installEventFilter(self)

        self.need_save = False
        self.current_textline = self.dataset[0]
        self.total_line_label.setText(f'{len(self.dataset) - 1:05d}')
        self.set_step(0)

        #######################
        # Set shortcut
        shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.save_current_line)

        shortcut_rotate = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_rotate.activated.connect(self.rotate)

        shortcut_note = QShortcut(QKeySequence("Ctrl+D"), self)
        shortcut_note.activated.connect(self.note)
        self.note_file = self.dataset.note_file

        self._is_rotate = False

    def save_current_line(self):
        if self.current_textline.textline() != self.label_text.text():
            print('Save text')
            self.current_textline.save(self.label_text.text())

        if self._is_rotate:
            self._is_rotate = False
            print('Save image')
            self.current_textline.save_image(self.pillow_image.rotate(self.current_angle, expand=True))

    def jump_to_line_index(self):
        step = int(self.current_line_index.text())
        self.set_step(step)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and source is self.label_text):
            if event.key() == Qt.Key_Down:
                self.next_image()
            elif event.key() == Qt.Key_Up:
                self.prev_image()
        return super().eventFilter(source, event)

    def next_image(self):
        self.set_step(self.current_index + 1)

    def prev_image(self):
        self.set_step(self.current_index - 1)

    def is_able_to_next(self, step):
        if step >= len(self.current_textline):
            if self.current_step == len(self.account) - 1:
                return False
        return True

    def is_able_to_back(self, step):
        if step < 0:
            if self.current_step == 0:
                return False
        return True

    def set_step(self, step):
        if step >= len(self.dataset) or step < 0:
            return

        if step != self.current_index:
            # check if next/prev image without save
            if self.current_textline.textline() != self.label_text.text():
                buttonReply = QMessageBox.question(self, 'Text not saved yet?', "Do you like to save?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    self.save_current_line()

        self.current_textline = self.dataset[step]
        self.current_index = step

        image = Image.open(self.current_textline.image_path)
        pred = self.current_textline.predict_text
        label = self.current_textline.textline()

        if image.size[0] * image.size[1] == 0:
            print(f'Width or height is 0. WxH = {image.size[0]}x{image.size[1]}')
            if self.is_able_to_next(step):
                self.next_image()
                return
            elif self.is_able_to_back(step):
                self.prev_image()
                return
            else:
                print('Done!')
                exit(0)
        self.pillow_image: Image.Image = image
        self.current_angle = 0
        self.current_line_index.setText(f'{self.current_index:05d}')
        self.pred_text.setText(pred)
        self.label_text.setText(label)
        self.loadImage(image)

        #### Resize font
        # Use binary search to efficiently find the biggest font that will fit.
        max_size = 27
        min_size = 1
        font = self.label_text.font()
        while 1 < max_size - min_size:
            new_size = (min_size + max_size) // 2
            font.setPointSize(new_size)
            metrics = QFontMetrics(font)

            target_rect = self.label_text.contentsRect()

            # Be careful which overload of boundingRect() you call.
            rect = metrics.boundingRect(target_rect, Qt.AlignLeft, label)
            if (rect.width() > target_rect.width() or
                    rect.height() > target_rect.height()):
                max_size = new_size
            else:
                min_size = new_size

        font.setPointSize(min_size)
        self.label_text.setFont(font)

        pred_font = self.pred_text.font()
        pred_font.setPointSize(min_size)
        self.pred_text.setFont(pred_font)

    def loadImage(self, pillow_image: Image.Image):
        image_w, image_h = pillow_image.size
        target_h = 64
        factor = target_h / image_h
        image_w = factor * image_w
        image_h = factor * image_h
        image_w, image_h = int(image_w), int(image_h)
        pillow_image = pillow_image.resize((image_w, image_h))

        self.scrollArea.setVisible(True)
        self.image = ImageQt(pillow_image)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
        self.imageLabel.setFixedSize(image_w, image_h)

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), 0)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), 1.0)

        self.current_path_label.setText(str(self.current_textline.image_path))
        message = "{}, {}x{}, Depth: {}".format(self.current_textline.image_path, self.image.width(), self.image.height(), self.image.depth())
        self.statusBar().showMessage(message)
        return True

    def rotate(self):
        self.current_angle += 90
        rotated_image = self.pillow_image.rotate(self.current_angle, expand=True)
        self.loadImage(rotated_image)
        self._is_rotate = True

    def note(self):
        current_path = self.current_textline.image_path
        with open(self.note_file, mode="a", encoding="utf-8") as f:
            f.write(f"{current_path}\n")

    def adjustScrollBar(self, scrollBar: QScrollBar, factor: float):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log_path', help='path to log file.')
    parser.add_argument('-p', '--label_path', help='path to label file.')
    parser.add_argument('-r', '--root_dir', help='data dir', default="./")
    args = parser.parse_args()
    app = QApplication([])
    window = App(log_file=args.log_path, list_file=args.label_path, image_dir=args.root_dir)
    window.show()
    app.exec_()
