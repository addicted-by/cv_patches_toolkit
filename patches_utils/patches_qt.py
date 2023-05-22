import argparse
import cv2
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QPolygon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self, image_path, config_path, image_tag):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OpenCV with PyQt")
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)

        self.image_path = image_path
        self.image = None
        self.drawing_mode = "rectangle"
        self.rectangle = QRect()
        self.polylines = []
        self.config_path = config_path
        self.image_tag = image_tag

        self.load_image(self.image_path)

        self.button = QPushButton("Toggle Mode", self)
        self.button.clicked.connect(self.toggle_drawing_mode)
        self.button.setFixedSize(250, 30)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.clicked.connect(self.clear_annotations)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_annotations)

        self.button.move(10, 10)
        self.clear_button.move(300, 10)
        self.save_button.move(600, 10)

        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(["common", "grid", "noise", "pink", "color"])
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        self.mode_combo.move(600, 50)

        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Enter something...")
        self.input_box.setGeometry(10, 50, 200, 30)

    def load_image(self, image_path):
        self.image = cv2.imread(image_path)
        if self.image is not None:
            self.display_image()
        else:
            print(f"Failed to load image: {image_path}")

    def display_image(self):
        rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)

    def toggle_drawing_mode(self):
        if self.drawing_mode == "rectangle":
            self.drawing_mode = "polylines"
            self.button.setText("Toggle Mode (Polylines)")
        else:
            self.drawing_mode = "rectangle"
            self.button.setText("Toggle Mode (Rectangle)")

    def change_mode(self, index):
        mode = self.mode_combo.currentText()
        print(f"Selected mode: {mode}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drawing_mode == "rectangle":
                self.rectangle.setTopLeft(event.pos())
            elif self.drawing_mode == "polylines":
                self.polylines.append(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.drawing_mode == "rectangle":
                self.rectangle.setBottomRight(event.pos())
            elif self.drawing_mode == "polylines":
                self.polylines.append(event.pos())
            self.display_image()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.drawing_mode == "rectangle":
                self.rectangle.setBottomRight(event.pos())
            elif self.drawing_mode == "polylines":
                self.polylines.append(event.pos())
                # Connect the last point with the first point to close the polygon
                self.polylines.append(self.polylines[0])
                self.rectangle = self.calculate_bounding_rect(self.polylines)
            self.display_image()

    def calculate_bounding_rect(self, points):
        if len(points) == 0:
            return QRect()

        min_x = min(points, key=lambda p: p.x()).x()
        min_y = min(points, key=lambda p: p.y()).y()
        max_x = max(points, key=lambda p: p.x()).x()
        max_y = max(points, key=lambda p: p.y()).y()

        return QRect(min_x, min_y, max_x - min_x, max_y - min_y)

    def paintEvent(self, event):
        super(MainWindow, self).paintEvent(event)
        painter = QPainter(self.image_label.pixmap())
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        if self.drawing_mode == "rectangle":
            painter.drawRect(self.rectangle)
        elif self.drawing_mode == "polylines":
            if len(self.polylines) > 1:
                painter.drawPolyline(QPolygon(self.polylines))
            if self.rectangle.isValid():
                painter.drawRect(self.rectangle)

    def clear_annotations(self):
        self.rectangle = QRect()
        self.polylines = []
        self.display_image()

    def save_annotations(self):
        bounds = [self.rectangle.y(), self.rectangle.y() + self.rectangle.height(),
                self.rectangle.x(), self.rectangle.x() + self.rectangle.width()]
        annotations = {
            "bounds": bounds,
            "polylines": [[point.x(), point.y()] for point in self.polylines ] if self.polylines else None,
            "problem": self.mode_combo.currentText()
        }

        print(self.input_box.text())
        print(self.image_tag)

        with open(self.config_path, 'r') as config_file:
            import yaml
            config = yaml.safe_load(config_file)
            if "patches" in config.keys():
                if self.image_tag in config["patches"].keys():
                    config["patches"][self.image_tag][self.input_box.text()] = annotations
                else:
                    config["patches"][self.image_tag] = {
                        self.input_box.text(): annotations
                    }
            else:
                config["patches"] = {
                    self.image_tag: {
                        self.input_box.text(): annotations
                    }
                }

        with open("check.yaml", 'w') as config_file:
            import yaml
            yaml.safe_dump(config, config_file, default_flow_style=False)

        print("Annotations saved successfully.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="OpenCV with PyQt")
    parser.add_argument("--config", help="Path to the configuration YAML file")
    parser.add_argument("--tag", type=str, help="Tag value")
    return parser.parse_args()

import os

if __name__ == '__main__':
    args = parse_arguments()
    image_path = None
    image_tag = args.tag
    # Read the image path from the configuration file
    with open(args.config, 'r') as config_file:
        import yaml
        config = yaml.safe_load(config_file)
        baseline_paths = config.get("baseline_paths")
        assert image_tag in baseline_paths, f"The proposed image tag {image_tag} does not match with tags in config: [{','.join(list(baseline_paths.keys()))}]"
        image_path = baseline_paths[image_tag]
        assert os.path.exists(image_path), f"Such path {image_path} does not exist"

    if image_path is None:
        print("Invalid configuration file or missing 'image_path' key.")
    else:
        app = QApplication([])
        window = MainWindow(image_path, args.config, args.tag)
        window.show()
        app.exec_()
