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
from PySide6.QtCore import QProcess, Qt
import sys
from pathlib import Path


class ArchiverWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VD Archiver")
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
        layout.setSpacing(14)
        layout.setContentsMargins(28, 24, 28, 20)

        heading = QLabel("VD Archiver")
        heading.setObjectName("heading")
        heading.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(heading)

        subtitle = QLabel(
            "Create a video backup or restore files from an existing backup"
        )
        subtitle.setObjectName("subtitle")
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
        self.backup_button.setObjectName("primaryButton")
        self.backup_button.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.restore_button.setObjectName("primaryButton")
        self.restore_button.setCursor(Qt.CursorShape.PointingHandCursor)

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
        self.log.setObjectName("activityLog")

        layout.addWidget(self.log, 1)

        self.status = QLabel("Ready")
        self.setObjectName("status")
        layout.addWidget(self.status)

    def start_backup(self):
        if not self.source_folder or not self.backup_video:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Choose a source folder and an output video location first.",
            )
            return

        self.run_cli(
            [
                "archive",
                self.source_folder,
                "--dest",
                self.backup_video,
            ]
        )

    def start_restore(self):
        if not self.restore_video or not self.restore_folder:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Choose a backup video and destination folder first.",
            )
            return

        self.run_cli(
            [
                "extract",
                self.restore_video,
                "--dest",
                self.restore_folder,
            ]
        )

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
        data = bytes(self.process.readAllStandardOutput().data())
        if data:
            self.log.appendPlainText(data.decode("utf-8", errors="replace").rstrip())

    def read_stderr(self):
        data = bytes(self.process.readAllStandardError().data())
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
    app.setStyle("fusion")
    # ! Credits to GPT for the UI design im not good at this kinda stuff
    app.setStyleSheet("""/* ===== Main window ===== */
    QMainWindow, QWidget {
        background-color: #0B0F19;
        color: #E2E8F0;
        font-family: "Segoe UI";
        font-size: 10pt;
        selection-background-color: #7C5CFC;
        selection-color: #FFFFFF;
    }

    /* ===== Header ===== */
    QLabel#heading {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 750;
        padding-top: 4px;
        padding-bottom: 2px;
    }

    QLabel#subtitle {
        color: #8B95AA;
        font-size: 10.5pt;
        padding-bottom: 8px;
    }

    QLabel {
        color: #C2CAD8;
        background-color: transparent;
    }

    QLabel#status {
        color: #A78BFA;
        padding: 8px 2px;
        font-weight: 600;
        font-size: 9.5pt;
    }

    /* ===== Section panels ===== */
    QGroupBox {
        background-color: #131A29;
        border: 1px solid #273249;
        border-radius: 12px;
        margin-top: 18px;
        padding: 22px 16px 16px 16px;
        font-size: 11pt;
        font-weight: 650;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        top: 0px;
        padding: 0 8px;
        color: #C4B5FD;
        background-color: #131A29;
    }

    /* ===== Standard buttons ===== */
    QPushButton {
        background-color: #1C2537;
        color: #E2E8F0;
        border: 1px solid #34415A;
        border-radius: 8px;
        padding: 9px 14px;
        font-weight: 600;
    }

    QPushButton:hover {
        background-color: #28344B;
        border-color: #6475A0;
        color: #FFFFFF;
    }

    QPushButton:pressed {
        background-color: #151D2D;
        border-color: #7C5CFC;
    }

    QPushButton:focus {
        border: 2px solid #A78BFA;
    }

    QPushButton:disabled {
        background-color: #151C2A;
        color: #68748A;
        border-color: #252F42;
    }

    /* ===== Primary buttons ===== */
    QPushButton#primaryButton {
        background-color: #7C5CFC;
        color: #FFFFFF;
        border: 1px solid #7C5CFC;
        border-radius: 9px;
        padding: 12px 16px;
        font-size: 10.5pt;
        font-weight: 700;
    }

    QPushButton#primaryButton:hover {
        background-color: #9078FF;
        border-color: #9078FF;
    }

    QPushButton#primaryButton:pressed {
        background-color: #6344DB;
        border-color: #6344DB;
    }

    QPushButton#primaryButton:disabled {
        background-color: #40366F;
        color: #B6ACD9;
        border-color: #40366F;
    }

    /* ===== Activity console ===== */
    QPlainTextEdit#activityLog {
        background-color: #080C14;
        color: #A7F3D0;
        border: 1px solid #263249;
        border-radius: 10px;
        padding: 12px;
        selection-background-color: #6344DB;
        selection-color: #FFFFFF;
        font-family: "Consolas";
        font-size: 9.5pt;
    }

    QPlainTextEdit#activityLog:focus {
        border: 1px solid #7C5CFC;
    }

    /* ===== Scrollbars ===== */
    QScrollBar:vertical {
        background-color: transparent;
        width: 10px;
        margin: 3px 2px;
        border: none;
    }

    QScrollBar::handle:vertical {
        background-color: #34415A;
        border-radius: 4px;
        min-height: 28px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #6475A0;
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
        border: none;
    }

    QScrollBar:horizontal {
        background-color: transparent;
        height: 10px;
        margin: 2px;
        border: none;
    }

    QScrollBar::handle:horizontal {
        background-color: #34415A;
        border-radius: 4px;
        min-width: 28px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #6475A0;
    }

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {
        width: 0px;
        border: none;
    }

    /* ===== Tooltips ===== */
    QToolTip {
        background-color: #1C2537;
        color: #F8FAFC;
        border: 1px solid #475569;
        border-radius: 5px;
        padding: 6px 8px;
    }

    /* ===== Dialogs and file pickers ===== */
    QMessageBox, QFileDialog {
        background-color: #131A29;
        color: #E2E8F0;
    }
""")

    window = ArchiverWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
