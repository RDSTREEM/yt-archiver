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
    QPlainTextEdit,
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

        restore_group = QGroupBox("Restore backup")
        restore_layout = QGridLayout(restore_group)

        self.video_label = QLabel("No backup video selected")
        self.video_label.setWordWrap(True)
        video_button = QPushButton("Choose video")
        video_button.clicked.connect(self.choose_restore_video)

        self.destination_label = QLabel("No destination folder selected")
        self.destination_label.setWordWrap(True)
        destination_button = QPushButton("Choose folder")
        destination_button.clicked.connect(self.choose_restore_folder)

        self.restore_button = QPushButton("Extract files")
        self.restore_button.clicked.connect(self.start_restore)

        restore_layout.addWidget(QLabel("Backup video"), 0, 0)
        restore_layout.addWidget(self.video_label, 0, 1)
        restore_layout.addWidget(video_button, 0, 2)
        restore_layout.addWidget(QLabel("Destination"), 1, 0)
        restore_layout.addWidget(self.destination_label, 1, 1)
        restore_layout.addWidget(destination_button, 1, 2)
        restore_layout.addWidget(self.restore_button, 2, 0, 1, 3)

        layout.addWidget(restore_group)

        layout.addWidget(QLabel("Activity"))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Choose an operation to see its output here.")

        layout.addWidget(self.log, 1)

        self.status = QLabel("Ready")
        layout.addWidget(self.status)

    def start_backup(self):
        if not self.source_folder or not self.backup_video:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Choose a source folder and an output video location first.",
            )
            return

    def start_restore(self):
        if not self.restore_video or not self.restore_folder:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Choose a backup video and destination folder first.",
            )
            return

    def cli_commands(self, arguments: list[str]) -> tuple[str, list[str]]:
        if getattr(sys, "frozen", False):
            executable_name = (
                "yt-archiver.exe" if sys.platform == "win32" else "yt-archiver"
            )

            executable = Path(sys.executable).with_name(executable_name)

            return str(executable), arguments

        return sys.executable, ["-m", "yt_archiver.cli", *arguments]

    def run_cli(self, arguments: list[str]):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return

        program, cli_arguments = self.cli_commands(arguments)

        self.log.clear()
        self.log.appendPlainText(f"Running: {program} {' '.join(cli_arguments)}")

        self.set_busy(True)
        self.status.setText("Working")
        self.process.start(program, cli_arguments)

    def set_busy(self, b):
        pass

    def choose_restore_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose backup video", "", "Matroska video (*mkv)"
        )
        if path:
            self.restore_video = path
            self.video_label.setText(path)

            if not self.restore_folder:
                self.restore_folder = str(Path(path).parent / "restored")
                self.destination_label.setText(self.restore_folder)

    def choose_restore_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Choose restore destination")
        if path:
            self.restore_folder = path
            self.destination_label.setText(path)

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
        data = bytes(self.process.readAllStandardOutput())
        if data:
            self.log.appendPlainText(data.decode("utf-8", errors="replace").rstrip())

    def read_stderr(self):
        data = bytes(self.process.readAllStandardError())
        if data:
            self.log.appendPlainText(
                "ERROR: " + data.decode("utf-8", errors="replace").rstrip()
            )

    def process_finished(self, exit_code, exit_status):
        self.read_stdout()
        self.read_stderr()
        self.set_busy(False)

        if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0:
            self.status.setText("Completed sucessfully.")

        else:
            self.status.setText(f"Failed (exit code {exit_code})")
            QMessageBox.critical(
                self,
                "Operation Failed",
                "The CLI operation failed. Check the activity log.",
            )

    def process_error(self, err):
        if err == QProcess.ProcessError.FailedToStart:
            self.set_busy(False)
            self.status.setText("Could not start the CLI")
            self.log.appendPlainText(
                "\nCould not start the CLI. Check that it is installed or bundled beside the GUI"
            )

    def set_busy(self, busy: bool):
        self.backup_button.setEnabled(not busy)
        self.restore_button.setEnabled(not busy)


def main():
    app = QApplication(sys.argv)
    window = ArchiverWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
