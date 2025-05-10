import json

from PySide6.QtCore import QPropertyAnimation, QPoint, QEasingCurve, Qt, QRect
from PySide6.QtGui import QPainterPath, QRegion, QColor, QPainter, QBrush
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout, QLabel, QPushButton, QDialog, QCheckBox, QLineEdit, QGroupBox
import random

from res.paths import SETTINGS_PATH, POS_PATH


class CustomWindow(QWidget):
    def __init__(self, title="Custom Window", wid=-1, geometry=(0, 0, 0, 0), add_close_btn=False, config_path=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setGeometry(*geometry)
        self.geo = self.geometry()
        self.geo_old = self.geometry()
        self.first_run = True
        self.wid = wid

        self.l1 = QVBoxLayout(self)
        self.l1.setContentsMargins(0, 0, 0, 0)
        self.l1.setSpacing(0)

        self.title_bar = CustomTitleBar(title, self, add_close_btn, config_path)
        self.l1.addWidget(self.title_bar)

        self.w1 = QWidget()
        self.w1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.w1.setObjectName("content")
        self.l1.addWidget(self.w1)

        self.layout = QVBoxLayout(self.w1)
        self.layout.setAlignment(Qt.AlignTop)

        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
            self.toggle_direction = settings.get('toggle_direction', 'random')

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 6
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())

    def generatePosition(self):
        screen_geometry = self.screen().geometry()
        x = y = 0

        if self.toggle_direction == 'up':
            x = (screen_geometry.width() - self.geo.width()) // 2
            y = -self.geo.height()
        elif self.toggle_direction == 'down':
            x = (screen_geometry.width() - self.geo.width()) // 2
            y = screen_geometry.height()
        elif self.toggle_direction == 'left':
            x = -self.geo.width()
            y = (screen_geometry.height() - self.geo.height()) // 2
        elif self.toggle_direction == 'right':
            x = screen_geometry.width()
            y = (screen_geometry.height() - self.geo.height()) // 2
        else:
            side = random.randint(0, 1)
            if side:
                x = random.randint(0, screen_geometry.width() - self.geo.width())
                y = random.choice([-self.geo.height(), screen_geometry.height()])
            else:
                x = random.choice([-self.geo.width(), screen_geometry.width()])
                y = random.randint(0, screen_geometry.height() - self.geo.height())

        return QPoint(x, y)

    def toggle_windows(self, is_hidden, is_instant=False):
        if is_instant:
            if is_hidden:
                self.hide()
            elif self.wid != -1:
                self.show()
            return

        self.geometry_bugfix()
        self.animation = QPropertyAnimation(self, b"pos")
        start_pos = self.pos()

        end_pos = QPoint(self.geo.x(), self.geo.y()) if is_hidden else self.generatePosition()

        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def hideContent(self):
        title_bar_height = self.title_bar.sizeHint().height()
        self.w1.hide()
        self.setFixedHeight(title_bar_height)

    def showContent(self):
        self.w1.show()
        self.setFixedHeight(self.geo_old.height())

    def geometry_bugfix(self):
        if self.first_run:
            self.geo = self.geometry()
            self.geo_old = self.geometry()
            self.first_run = False


class CustomDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("content")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMask(self.generateRoundedMask())

    def generateRoundedMask(self):
        rect = self.rect()
        path = QPainterPath()
        radius = 6
        path.addRoundedRect(rect, radius, radius)
        return QRegion(path.toFillPolygon().toPolygon())


class CustomTitleBar(QWidget):
    def __init__(self, title="Custom Title Bar", parent=None, add_close_btn=False, config_path=None):
        super().__init__(parent)
        self.parent = parent

        self.setObjectName("title-bar")
        self.bar_color_default = QColor("#222")
        self.bar_color = self.bar_color_default

        self.l1 = QHBoxLayout(self)

        self.title_label = QLabel(title)
        self.l1.addWidget(self.title_label, stretch=10)

        if config_path:
            self.config_window = ConfigWindow(config_path)
            self.config_btn = QPushButton("⚙")
            self.config_btn.clicked.connect(self.config_window.show)
            self.l1.addWidget(self.config_btn, stretch=1)
        if add_close_btn:
            self.close_btn = QPushButton("✕")
            self.close_btn.clicked.connect(self.parent.close)
            self.l1.addWidget(self.close_btn, stretch=1)
        # else:
            # self.collapse_btn = QPushButton("▼")
            # self.collapse_btn.clicked.connect(self.toggleCollapse)
            # self.l1.addWidget(self.collapse_btn, stretch=1)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.bar_color))
        painter.drawRect(self.rect())

    # def toggleCollapse(self):
    #     self.parent.geometry_bugfix()
    #     if self.collapse_btn.text() == "▼":
    #         self.collapse_btn.setText("▲")
    #         self.parent.hideContent()
    #     else:
    #         self.collapse_btn.setText("▼")
    #         self.parent.showContent()
    #     self.parent.geo = self.parent.geometry()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.window().pos()
            self.bar_color = self.bar_color.darker(150)
            self.parent.setWindowOpacity(0.5)
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.bar_color = self.bar_color_default
        self.parent.setWindowOpacity(1)
        self.parent.geo = QRect(
            round(self.parent.geometry().x() / 10) * 10,
            round(self.parent.geometry().y() / 10) * 10,
            self.parent.geometry().width(),
            self.parent.geometry().height()
        )

        self.parent.setGeometry(self.parent.geo)
        self.update()

        if self.parent.wid != -1:
            with open(POS_PATH, 'r') as f:
                settings = json.load(f)
                w = settings.get('windows')[self.parent.wid]
                settings['pos'][w] = [self.parent.geo.x(), self.parent.geo.y(), self.parent.geo.width(), self.parent.geo.height()]

            with open(POS_PATH, 'w') as f:
                json.dump(settings, f, indent=2)


class ConfigWindow(CustomWindow):
    def __init__(self, config_path=''):
        super().__init__(add_close_btn=True)
        self.setGeometry(300, 300, 400, 100)

        self.config_layout = QVBoxLayout()
        self.layout.addLayout(self.config_layout)
        self.config_path = config_path
        self.generate_settings()

        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.hide)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)
        self.layout.addLayout(self.button_layout)

    def generate_settings(self):
        def add_to_layout(layout, item):
            if isinstance(item, QGroupBox):
                layout.addWidget(item)
            else:
                layout.addLayout(item)

        def create_item(key, value):
            if isinstance(value, bool):
                checkbox = QCheckBox(self)
                checkbox.setChecked(value)
                layout = QHBoxLayout()
                layout.addWidget(QLabel(key))
                layout.addWidget(checkbox)
                return layout
            elif isinstance(value, dict):
                group_box = QGroupBox(key, self)
                group_layout = QVBoxLayout(group_box)
                for k, v in value.items():
                    add_to_layout(group_layout, create_item(k, v))
                return group_box
            else:
                input_field = QLineEdit(self)
                input_field.setText(str(value))
                layout = QHBoxLayout()
                layout.addWidget(QLabel(key))
                layout.addWidget(input_field)
                return layout

        with open(self.config_path, 'r') as f:
            settings = json.load(f)

        for k, v in settings.items():
            add_to_layout(self.config_layout, create_item(k, v))

    def save(self):
        def extract_from_layout(layout):
            result = {}
            for i in range(layout.count()):
                item = layout.itemAt(i)
                widget = item.widget()
                sub_layout = item.layout()

                if isinstance(widget, QGroupBox):
                    group_layout = widget.layout()
                    result[widget.title()] = extract_from_layout(group_layout)
                elif isinstance(sub_layout, QHBoxLayout):
                    label = sub_layout.itemAt(0).widget()
                    value = sub_layout.itemAt(1).widget()
                    k = label.text()

                    if isinstance(value, QCheckBox):
                        result[k] = value.isChecked()
                    elif isinstance(value, QLineEdit):
                        text = value.text()
                        if text.isdigit():
                            result[k] = int(text)
                        elif text.replace('.', '', 1).isdigit():
                            result[k] = float(text)
                        else:
                            result[k] = text

            return result

        config = extract_from_layout(self.config_layout)
        print(config)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            self.hide()
