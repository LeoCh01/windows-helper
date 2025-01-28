import sys
import json
import keyboard
from PySide6.QtCore import QSettings, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QPushButton, QLabel, QGridLayout

from src.components.custom_window import CustomWindow

RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"


class Info(CustomWindow):
    def __init__(self, wid, geometry=(10, 10, 180, 1), set_toggle_key=None, key='`'):
        super().__init__('Info', wid, geometry)

        self.grid_layout = QGridLayout()
        self.set_toggle_key = set_toggle_key

        self.ver = QPushButton(f'v{self.get_version()}')
        self.ver.clicked.connect(self.open_url)
        self.grid_layout.addWidget(self.ver, 0, 0, 1, 2)

        self.set_key = QPushButton('Edit Toggle Key')
        self.set_key.setCheckable(True)
        self.set_key.clicked.connect(self.select_key)
        self.grid_layout.addWidget(self.set_key, 1, 0)

        self.key_label = QLabel(' Key = ' + key)
        self.grid_layout.addWidget(self.key_label, 1, 1)

        self.startup = QPushButton('Startup App')
        self.startup.setCheckable(True)
        self.startup.setChecked(self.get_startup())
        self.startup.clicked.connect(self.toggle_startup)
        self.grid_layout.addWidget(self.startup, 3, 0)

        self.q = QPushButton('Quit')
        self.q.setStyleSheet("background-color: #c44; color: white;")
        self.q.clicked.connect(self.quit)
        self.grid_layout.addWidget(self.q, 3, 1)

        self.grid_layout.setColumnStretch(0, 2)
        self.grid_layout.setColumnStretch(1, 1)
        self.layout.addLayout(self.grid_layout)

        # Check current startup status
        self.settings = QSettings(RUN_PATH, QSettings.NativeFormat)
        app_name = self.get_app_name()
        self.startup.setChecked(self.settings.contains(app_name))

    def select_key(self):
        def on_key_press(event):
            key = event.name
            self.set_key.setChecked(False)
            self.key_label.setText(f' Key = {key}')
            self.set_toggle_key(key)
            self.set_key.setText('Edit Toggle Key')
            keyboard.unhook(self.key_hook)

        self.set_key.setChecked(True)
        self.set_key.setText('Press a key')
        self.key_hook = keyboard.on_press(on_key_press)

    @staticmethod
    def get_version():
        with open('res/settings.json', 'r') as file:
            data = json.load(file)
            version = data.get('version', 'xxx')
        return version

    @staticmethod
    def get_startup():
        with open('res/settings.json', 'r') as file:
            data = json.load(file)
            startup = data.get('startup', False)
        return startup

    @staticmethod
    def open_url():
        QDesktopServices.openUrl(QUrl('https://github.com/LeoCh01/windows-helper'))

    @staticmethod
    def quit(self):
        print('Quitting')
        sys.exit()

    def get_app_path(self):
        return sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

    def get_app_name(self):
        return 'WindowsHelper'

    def toggle_startup(self):
        app_name = self.get_app_name()
        app_path = self.get_app_path()

        if self.startup.isChecked():
            self.settings.setValue(app_name, app_path)
            print(f'Added {app_name} to startup with path: {app_path}')
        else:
            self.settings.remove(app_name)
            print(f'Removed {app_name} from startup')

        with open('res/settings.json', 'r') as file:
            data = json.load(file)
            data['startup'] = self.startup.isChecked()
        with open('res/settings.json', 'w') as file:
            json.dump(data, file, indent=2)
