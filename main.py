from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLineEdit, QLabel,QComboBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import openai
from pdf_parser import Paper
from utils import review_by_chatgpt


class ReviewThread(QThread):
    status_update = pyqtSignal(str)

    def __init__(self, api_key, file_paths, research_domain):
        super().__init__()
        self.api_key = api_key
        self.file_paths = file_paths
        self.research_domain = research_domain

    def run(self):
        paper_list = []
        file_names = []
        for file_path in self.file_paths:
            file_name = file_path.split('/')[-1].split('.')[0]
            file_names.append(file_name)
            with open(file_path, "rb") as f:
                paper = Paper(path=file_path)
                paper_list.append(paper)
                self.status_update.emit(f"Finished loading {file_name}.")

        self.status_update.emit("Start reviewing papers.")
        review_by_chatgpt(paper_list, key_word=self.research_domain, api_key=self.api_key, export_path='./review/', file_format='txt', file_names=file_names)
        self.status_update.emit("All files have been reviewed.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paper Reviewer")
        self.setGeometry(100, 100, 500, 300)

        self.api_key_input = QLineEdit(self)
        self.api_key_input.move(20, 20)
        self.api_key_input.resize(360, 30)
        self.api_key_input.setPlaceholderText("Enter your OpenAI API key")

        self.domain_label = QLabel("Research Domain:", self)
        self.domain_label.move(20, 60)
        self.domain_label.setAlignment(Qt.AlignLeft)
        self.domain_label.resize(130, 60)

        self.domain_menu = QComboBox(self)
        self.domain_menu.move(150, 60)
        self.domain_menu.resize(300, 30)
        self.domain_menu.addItems(["Computer Science and Artificial Intelligence", "Biology", "Engineering", "Social Science", "Other"])

        self.select_btn = QPushButton("Select Files", self)
        self.select_btn.move(20, 100)
        self.select_btn.clicked.connect(self.select_files)

        self.selected_files_label = QLabel("", self)
        self.selected_files_label.move(20, 140)
        self.selected_files_label.setAlignment(Qt.AlignLeft)
        self.selected_files_label.resize(360, 30)

        self.review_btn = QPushButton("Review", self)
        self.review_btn.move(20, 180)
        self.review_btn.clicked.connect(self.start_review)

        self.status_label = QLabel("", self)
        self.status_label.move(20, 220)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.resize(360, 30)


    def select_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("PDF files (*.pdf)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.file_paths = file_dialog.selectedFiles()
            num_files_selected = len(self.file_paths)
            self.selected_files_label.setText(f"{num_files_selected} files selected.")
            

    def start_review(self):
        self.api_key = self.api_key_input.text()
        self.research_domain = self.domain_menu.currentText()

        if not self.api_key:
            self.status_label.setText("Please enter your OpenAI API key.")
        elif not self.file_paths:
            self.status_label.setText("Please select at least one PDF file.")
        else:
            self.thread = ReviewThread(self.api_key, self.file_paths, self.research_domain)
            self.thread.status_update.connect(self.update_status)
            self.thread.finished.connect(self.show_notification)
            self.thread.start()

    def update_status(self, status):
        self.status_label.setText(status)

    def show_notification(self):
        self.status_label.setText("All files have been reviewed.")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
