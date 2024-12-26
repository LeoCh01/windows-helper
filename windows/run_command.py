import subprocess
import json
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QGroupBox, QLabel, QDialogButtonBox, \
    QPlainTextEdit, QCheckBox, QDialog
from components.custom_window import CustomWindow, CustomDialog


class RunCmd(CustomWindow):
    def __init__(self, geometry):
        super().__init__("Run Command", geometry)

        self.commands_groupbox = QGroupBox("Commands")
        self.commands_layout = QVBoxLayout()
        self.commands_groupbox.setLayout(self.commands_layout)
        self.layout.addWidget(self.commands_groupbox)

        self.add_button = QPushButton("Add Command")
        self.add_button.clicked.connect(self.open_add_command_dialog)
        self.layout.addWidget(self.add_button)

        self.commands = []
        self.load_commands()

    def open_add_command_dialog(self):
        dialog = AddCommandDialog(self)
        v = dialog.exec()
        if v:
            cmd_name, cmd, show_output = dialog.get_command()
            if cmd and cmd_name:
                self.commands.append((cmd_name, cmd, show_output))
                self.add_command_to_layout(cmd_name, cmd, show_output)
                self.save_commands()

    def add_command_to_layout(self, cmd_name, cmd, show_output):
        cmd_layout = QHBoxLayout()
        cmd_button = QPushButton(cmd_name)
        cmd_button.clicked.connect(lambda _, c=cmd, s=show_output: self.run_cmd(c, s))
        cmd_layout.addWidget(cmd_button)

        delete_button = QPushButton("\u274C")
        delete_button.setFixedWidth(25)
        delete_button.clicked.connect(lambda _, c=cmd, l=cmd_layout: self.delete_command(c, l))
        cmd_layout.addWidget(delete_button)

        self.commands_layout.addLayout(cmd_layout)

    def delete_command(self, cmd, layout):
        self.commands = [c for c in self.commands if c[1] != cmd]
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.save_commands()

    def run_cmd(self, cmd, show_output):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if show_output:
                self.show_command_output(result.stdout)
        except Exception as e:
            print(f"An error occurred: {e}")

    def show_command_output(self, res):
        output_dialog = QDialog(self)
        output_dialog.setWindowTitle("Command Output")
        output_dialog.setGeometry(100, 100, 600, 400)

        output_text = QPlainTextEdit(output_dialog)
        output_text.setPlainText(res)
        output_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(output_text)

        output_dialog.setLayout(layout)
        output_dialog.exec()

    def save_commands(self):
        with open('res/commands.json', 'w') as f:
            json.dump(self.commands, f)

    def load_commands(self):
        try:
            with open('res/commands.json', 'r') as f:
                self.commands = json.load(f)
        except Exception as e:
            print("error :: ", e)
            self.commands = []

        for cmd_name, cmd, show_output in self.commands:
            self.add_command_to_layout(cmd_name, cmd, show_output)


class AddCommandDialog(CustomDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Command")
        screen_geometry = self.screen().geometry()

        self.setGeometry(
            screen_geometry.width() // 2 - 300,
            screen_geometry.height() // 2 - 200,
            600,
            400
        )

        self.command_name_input = QLineEdit(self)
        self.command_name_input.setPlaceholderText("name")

        self.command_input = QPlainTextEdit(self)
        self.command_input.setPlaceholderText("command")

        self.show_output_checkbox = QCheckBox("Show Output", self)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Command Name:"))
        layout.addWidget(self.command_name_input)
        layout.addWidget(QLabel("Command:"))
        layout.addWidget(self.command_input)
        layout.addWidget(self.show_output_checkbox)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def get_command(self):
        return self.command_name_input.text(), self.command_input.toPlainText(), self.show_output_checkbox.isChecked()
