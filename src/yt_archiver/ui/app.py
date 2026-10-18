from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QProcess
import sys
import pathlib


class ArchiverWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vid Archiver")
        self.resize(720, 620)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)

        self.source_folder = ""
        self.backup_video = ""
        self.restore_video = ""
        self.restore_folder = ""

        win = QWidget()
        self.setCentralWidget(win)
        layout = QVBoxLayout(win)
        layout.setSpacing(18)

        heading = QLabel("VD Archiver")
        layout.addWidget(heading)

        subtitle = QLabel(
            "Create a video backup or restore files from an existing backup"
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

    def read_stdout(self):
        pass

    def read_stderr(self):
        pass

    def process_finished(self):
        pass

    def process_error(self):
        pass


def main():
    app = QApplication(sys.argv)
    window = ArchiverWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
