from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import QProcess
import sys
from pathlib import Path


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

        backup_group = QGroupBox("Create backup")
        backup_layout = QGridLayout(backup_group)

        self.source_label = QLabel("No source folder selected")
        self.source_label.setWordWrap(True)
        source_button = QPushButton("Choose folder")
        source_button.clicked.connect(self.choose_source_folder)

        self.output_label = QLabel("No output video selected")
        self.output_label.setWordWrap(True)

        self.backup_button = QPushButton("Create video backup")
        self.backup_button.clicked.connect(self.start_backup)

    def start_backup(self):
        if not self.source_folder or not self.backup_video:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Choose a source folder and an output video location first.",
            )
            return

    def choose_source_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Choose source folder")
        if path:
            self.source_folder = path
            self.source_label = path

            if not self.backup_video:
                self.backup_video = str(Path(path).parent / "backup.mkv")
                self.output_label.setText(self.backup_video)

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
