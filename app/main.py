import importlib
import json
import keyboard
import logging
import os
import sys

from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from res.paths import SETTINGS_PATH, POS_PATH, RES_PATH, STYLES_PATH, IMG_PATH


class App(QObject):
    toggle = Signal(bool, bool)
    windows = []

    def __init__(self):
        super().__init__()

        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)

        self.toggle_key = str(settings.get('toggle_key', '`'))
        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)
        self.is_hidden = False
        self.is_reset = settings.get('is_default_pos', True)

        self.load_windows(settings)
        self.setup_tray_icon()

    def load_windows(self, settings):
        with open(POS_PATH, 'r') as f:
            pos_settings = json.load(f)
            pos_settings['windows'] = []

        for i, w in enumerate(settings.get('windows')):
            try:
                class_obj = App.load_plugin(w + '/window.py').MainWindow
                print(f'Loading {w}')
            except Exception as e:
                logging.error(f'Error loading {w} :: {e}', exc_info=True)
                continue

            class_obj.set_toggle_key = self.set_toggle_key
            class_obj.toggle_windows_2 = self.toggle_windows_2
            class_obj.toggle_signal = self.toggle

            pos_settings['windows'].append(w + str(i))
            if self.is_reset or not pos_settings['pos'].get(w + str(i)):
                self.windows.append(class_obj(i))
            else:
                self.windows.append(class_obj(i, pos_settings['pos'][w + str(i)]))

        with open(POS_PATH, 'w') as f:
            json.dump(pos_settings, f, indent=2)

        for window in self.windows:
            self.toggle.connect(window.toggle_windows)
            window.show()

    def toggle_windows(self):
        self.toggle.emit(self.is_hidden, False)
        self.is_hidden = not self.is_hidden

    def toggle_windows_2(self, show):
        self.toggle.emit(show, True)

    def set_toggle_key(self, key):
        key = str(key)
        print(f'Changing toggle key from {self.toggle_key} to {key}')
        if self.toggle_key == key:
            return

        keyboard.remove_hotkey(self.toggle_key)
        self.toggle_key = key

        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        settings['toggle_key'] = key
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(IMG_PATH + 'icon.ico'), parent=self)
        self.tray_icon.setToolTip('Windows Helper')
        tray_menu = QMenu()

        reload_action = QAction('Restart', self)
        reload_action.triggered.connect(self.restart)
        tray_menu.addAction(reload_action)

        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(sys.exit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def restart(self):
        for window in App.windows:
            window.close()
        App.windows.clear()

        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)

        self.toggle_key = str(settings.get('toggle_key', '`'))
        keyboard.remove_hotkey(self.toggle_key)
        keyboard.add_hotkey(self.toggle_key, self.toggle_windows, suppress=True)
        self.is_hidden = False
        self.is_reset = settings.get('is_default_pos', True)

        self.load_windows(settings)


    @staticmethod
    def load_plugin(plugin_name):
        plugin_path = os.path.join(os.getcwd() + '\\windows', plugin_name)
        print(plugin_path)

        if os.path.exists(plugin_path):
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            return module
        else:
            logging.error(f'Script {plugin_name} does not exist at {plugin_path}.')
            return None


def initialize_app():
    print('Starting Windows Helper')
    app = QApplication([])

    # Set working directory
    print('Current working directory:', os.getcwd())
    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(base_dir)
    print('Switched working directory:', os.getcwd())

    logging.basicConfig(
        filename=RES_PATH + 'error.log',
        filemode='a',
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    try:
        with open(STYLES_PATH, 'r') as f:
            stylesheet = f.read()
        app.setStyleSheet(stylesheet)

        application = App()
        app.exec()
    except Exception as e:
        print('error :: ', e)
        logging.error(e, exc_info=True)


if __name__ == '__main__':
    initialize_app()
