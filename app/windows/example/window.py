import os

from PySide6.QtWidgets import QLabel

from windows.custom_widgets import CustomWindow

RES_PATH = os.path.join(os.path.dirname(__file__), 'res/')
IMG_PATH = os.path.join(os.path.dirname(__file__), 'res/img/')


class MainWindow(CustomWindow):
    """
    MainWindow class that inherits from CustomWindow.

    This class represents a window with two QLabel widgets.
    """

    def __init__(self, wid, geometry=(0, 0, 100, 1)):
        """
        Initialize a window at the top left of the screen.

        Args:
            wid (int): The window ID.
            geometry (tuple): A tuple containing the geometry of the window (x, y, width, height).
        """
        super().__init__('Temp', wid, geometry)

        self.layout.addWidget(QLabel('Hello'))
