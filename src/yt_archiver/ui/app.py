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
        output_button = QPushButton("Save this video as")
        output_button.clicked.connect(self.choose_backup_video)

        self.backup_button = QPushButton("Create video backup")
        self.backup_button.clicked.connect(self.start_backup)

        backup_layout.addWidget(QLabel("Source folder"), 0, 0)
        backup_layout.addWidget(self.source_label, 0, 1)
        backup_layout.addWidget(source_button, 0, 2)
        backup_layout.addWidget(QLabel("Output video"), 1, 0)
        backup_layout.addWidget(self.output_label, 1, 1)
        backup_layout.addWidget(output_button, 1, 2)
        backup_layout.addWidget(self.backup_button, 2, 0, 1, 3)

        layout.addWidget(backup_group)

    def start_backup(self):
        if not self.source_folder or not self.backup_video:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Choose a source folder and an output video location first.",
            )
            return

    def choose_backup_video(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save backup video",
            self.backup_video or "backup.mkv",
            "Matroska video (*mkv)",
        )
        if path:
            if not path.lower().endswith("mkv"):
                path += ".mkv"

            self.backup_video = path
            self.output_label.setText(path)

    def choose_source_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Choose source folder")
        if path:
            self.source_folder = path
            self.source_label.setText(path)

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
