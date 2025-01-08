from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QGridLayout
from components.custom_window import CustomWindow


class Timer(CustomWindow):
    def __init__(self, geometry, wid):
        super().__init__('Timer', geometry, wid)

        self.grid_layout = QGridLayout()

        self.time_display = QLabel("00:00:00.00", self)
        self.layout.addWidget(self.time_display)
        self.grid_layout.addWidget(self.time_display, 0, 0, 1, 3)

        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_timer)
        self.grid_layout.addWidget(self.start_button, 1, 0)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_timer)
        self.grid_layout.addWidget(self.stop_button, 1, 1)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_timer)
        self.grid_layout.addWidget(self.reset_button, 1, 2)

        self.layout.addLayout(self.grid_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0

    def start_timer(self):
        self.timer.start(10)

    def stop_timer(self):
        self.timer.stop()

    def reset_timer(self):
        self.timer.stop()
        self.elapsed_time = 0
        self.update_timer_display()

    def update_timer(self):
        self.elapsed_time += 10
        self.update_timer_display()

    def update_timer_display(self):
        h, remainder = divmod(self.elapsed_time, 3600000)
        m, remainder = divmod(remainder, 60000)
        s, ms = divmod(remainder, 1000)
        ms //= 10

        self.time_display.setText(f"{h:02}:{m:02}:{s:02}.{ms:02}")
